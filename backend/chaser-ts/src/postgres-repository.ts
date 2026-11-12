import type { Pool, PoolClient, QueryResultRow } from "pg";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { randomUUID } from "node:crypto";
import { HttpError, type ChaseCase, type ChaseRepository, type CreateCaseInput, type DocumentRecord, type RequestBatch } from "./types.js";

interface CaseRow extends QueryResultRow {
  id: string;
  company: string;
  contact: string;
  email: string;
  rm: string;
  chase_rounds: number;
  last_request_at: Date | null;
  draft: string;
}

interface DocumentRow extends QueryResultRow {
  case_id: string;
  name: string;
  requested_at: Date | null;
  received_at: Date | null;
}

interface BatchRow extends QueryResultRow {
  case_id: string;
  sent_at: Date;
  document_names: string[];
  response_at: Date | null;
}

function iso(value: Date | null): string | null {
  return value ? value.toISOString() : null;
}

function assemble(row: CaseRow, docs: DocumentRow[], batches: BatchRow[]): ChaseCase {
  const documents: DocumentRecord[] = docs
    .filter((document) => document.case_id === row.id)
    .map((document) => ({
      name: document.name,
      requestedAt: iso(document.requested_at),
      receivedAt: iso(document.received_at),
    }));
  const requestHistory: RequestBatch[] = batches
    .filter((batch) => batch.case_id === row.id)
    .map((batch) => ({
      sentAt: batch.sent_at.toISOString(),
      documentNames: batch.document_names,
      responseAt: iso(batch.response_at),
    }));
  return {
    id: row.id,
    company: row.company,
    contact: row.contact,
    email: row.email,
    rm: row.rm,
    chaseRounds: row.chase_rounds,
    lastRequestAt: iso(row.last_request_at),
    draft: row.draft,
    documents,
    requestHistory,
  };
}

export class PostgresChaseRepository implements ChaseRepository {
  constructor(private readonly pool: Pool) {}

  async initialize(seedDemoData: boolean): Promise<void> {
    const client = await this.pool.connect();
    try {
      await client.query("BEGIN");
      await client.query("SELECT pg_advisory_xact_lock(672019458)");
      await client.query(`
        CREATE TABLE IF NOT EXISTS chaser_schema_migrations (
          version INTEGER PRIMARY KEY,
          applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
      `);
      const applied = await client.query<{ version: number }>(
        "SELECT version FROM chaser_schema_migrations WHERE version = 1",
      );
      if (!applied.rowCount) {
        const migration = await readFile(join(process.cwd(), "migrations", "001_create_chaser_tables.sql"), "utf8");
        await client.query(migration);
        await client.query("INSERT INTO chaser_schema_migrations (version) VALUES (1)");
      }
      await client.query("COMMIT");
    } catch (error) {
      await client.query("ROLLBACK");
      throw error;
    } finally {
      client.release();
    }
    if (seedDemoData) await this.seedDemoData();
  }

  async createCase(input: CreateCaseInput): Promise<ChaseCase> {
    const id = `KYC-${randomUUID().replace(/-/g, "").slice(0, 12).toUpperCase()}`;
    const requiredDocs = [
      "Certificate of Incorporation",
      "Articles of Association",
      "Ultimate Beneficial Owner Register",
      "Proof of Registered Address",
      "Director Identification",
    ];
    const client = await this.pool.connect();
    try {
      await client.query("BEGIN");
      const result = await client.query<CaseRow>(
        `INSERT INTO chase_cases (id, company, contact, email, rm)
         VALUES ($1, $2, $3, $4, 'Relationship Manager') RETURNING *`,
        [id, input.company, input.contact, input.email],
      );
      for (const name of requiredDocs) {
        await client.query(
          "INSERT INTO chase_documents (case_id, name) VALUES ($1, $2)",
          [id, name],
        );
      }
      const item = await this.assembleCase(result.rows[0]!, client);
      await client.query("COMMIT");
      return item;
    } catch (error) {
      await client.query("ROLLBACK");
      throw error;
    } finally {
      client.release();
    }
  }

  async listCases(): Promise<ChaseCase[]> {
    const [caseResult, documentResult, batchResult] = await Promise.all([
      this.pool.query<CaseRow>("SELECT * FROM chase_cases ORDER BY id"),
      this.pool.query<DocumentRow>("SELECT * FROM chase_documents ORDER BY case_id, name"),
      this.pool.query<BatchRow>("SELECT * FROM chase_request_batches ORDER BY sent_at, id"),
    ]);
    return caseResult.rows.map((row) => assemble(row, documentResult.rows, batchResult.rows));
  }

  async getCase(id: string): Promise<ChaseCase | null> {
    const row = await this.findCase(id);
    if (!row) return null;
    return this.assembleCase(row);
  }

  async updateDraft(id: string, draft: string): Promise<ChaseCase | null> {
    const result = await this.pool.query<CaseRow>(
      "UPDATE chase_cases SET draft = $2 WHERE id = $1 RETURNING *",
      [id, draft],
    );
    return result.rows[0] ? this.assembleCase(result.rows[0]) : null;
  }

  async recordRequest(id: string): Promise<ChaseCase | null> {
    const client = await this.pool.connect();
    try {
      await client.query("BEGIN");
      const found = await client.query<CaseRow>("SELECT * FROM chase_cases WHERE id = $1 FOR UPDATE", [id]);
      const row = found.rows[0];
      if (!row) {
        await client.query("ROLLBACK");
        return null;
      }
      const outstanding = await client.query<DocumentRow>(
        "SELECT * FROM chase_documents WHERE case_id = $1 AND received_at IS NULL ORDER BY name",
        [id],
      );
      if (!outstanding.rowCount) throw new HttpError(409, "There are no outstanding documents to request");
      const requestedAt = new Date();
      const documentNames = outstanding.rows.map((document) => document.name);
      await client.query(
        "UPDATE chase_documents SET requested_at = COALESCE(requested_at, $2) WHERE case_id = $1 AND received_at IS NULL",
        [id, requestedAt],
      );
      await client.query(
        "INSERT INTO chase_request_batches (case_id, sent_at, document_names) VALUES ($1, $2, $3::jsonb)",
        [id, requestedAt, JSON.stringify(documentNames)],
      );
      const updated = await client.query<CaseRow>(
        "UPDATE chase_cases SET chase_rounds = chase_rounds + 1, last_request_at = $2 WHERE id = $1 RETURNING *",
        [id, requestedAt],
      );
      await client.query("COMMIT");
      return this.assembleCase(updated.rows[0]!, client);
    } catch (error) {
      await client.query("ROLLBACK");
      throw error;
    } finally {
      client.release();
    }
  }

  async recordReceived(id: string, documentName: string): Promise<ChaseCase | null> {
    const client = await this.pool.connect();
    try {
      await client.query("BEGIN");
      const updated = await client.query<DocumentRow>(
        `UPDATE chase_documents
         SET received_at = NOW()
         WHERE case_id = $1 AND name = $2 AND received_at IS NULL AND requested_at IS NOT NULL
         RETURNING *`,
        [id, documentName],
      );
      if (!updated.rowCount) {
        const exists = await client.query(
          "SELECT 1 FROM chase_documents WHERE case_id = $1 AND name = $2",
          [id, documentName],
        );
        if (!exists.rowCount) {
          await client.query("ROLLBACK");
          return null;
        }
        const caseResult = await client.query<CaseRow>("SELECT * FROM chase_cases WHERE id = $1", [id]);
        if (!caseResult.rows[0]) {
          await client.query("ROLLBACK");
          return null;
        }
        await client.query("ROLLBACK");
        throw new HttpError(409, "Record the document request before logging its receipt");
      }
      await client.query(
        `UPDATE chase_request_batches
         SET response_at = NOW()
         WHERE id = (
           SELECT id FROM chase_request_batches
           WHERE case_id = $1 AND document_names @> $2::jsonb AND response_at IS NULL
           ORDER BY sent_at DESC, id DESC LIMIT 1
         )`,
        [id, JSON.stringify([documentName])],
      );
      const caseResult = await client.query<CaseRow>("SELECT * FROM chase_cases WHERE id = $1", [id]);
      const item = caseResult.rows[0] ? await this.assembleCase(caseResult.rows[0], client) : null;
      await client.query("COMMIT");
      return item;
    } catch (error) {
      await client.query("ROLLBACK");
      throw error;
    } finally {
      client.release();
    }
  }

  private async findCase(id: string, client: Pool | PoolClient = this.pool): Promise<CaseRow | null> {
    const result = await client.query<CaseRow>("SELECT * FROM chase_cases WHERE id = $1", [id]);
    return result.rows[0] ?? null;
  }

  private async assembleCase(row: CaseRow, client: Pool | PoolClient = this.pool): Promise<ChaseCase> {
    const [documents, batches] = await Promise.all([
      client.query<DocumentRow>("SELECT * FROM chase_documents WHERE case_id = $1 ORDER BY name", [row.id]),
      client.query<BatchRow>("SELECT * FROM chase_request_batches WHERE case_id = $1 ORDER BY sent_at, id", [row.id]),
    ]);
    return assemble(row, documents.rows, batches.rows);
  }

  private async seedDemoData(): Promise<void> {
    const requiredDocs = [
      "Certificate of Incorporation",
      "Articles of Association",
      "Ultimate Beneficial Owner Register",
      "Proof of Registered Address",
      "Director Identification",
    ];
    const samples = [
      { id: "KYC-48291", company: "Meridian Infrastructure Group", contact: "James Whitaker", email: "james.whitaker@example.com", received: [0, 3], requestedDaysAgo: 4, rounds: 1 },
      { id: "KYC-48276", company: "Northstar Renewables Ltd", contact: "Amara Okafor", email: "amara.okafor@example.com", received: [0, 1, 4], requestedDaysAgo: 2, rounds: 2 },
      { id: "KYC-48253", company: "Alderbrook Capital Partners", contact: "Sophie Laurent", email: "sophie.laurent@example.com", received: [0, 1, 2, 3], requestedDaysAgo: 1, rounds: 1 },
      { id: "KYC-48198", company: "Riverstone Logistics PLC", contact: "David Chen", email: "david.chen@example.com", received: [0, 1, 2, 3, 4], requestedDaysAgo: null, rounds: 1 },
    ];
    for (const sample of samples) {
      const requestAgeDays = sample.requestedDaysAgo ?? 7;
      const requestedAt = new Date(Date.now() - requestAgeDays * 86_400_000);
      const responseAgeDays = Math.max(0, requestAgeDays - 2);
      const responseAt = new Date(Date.now() - responseAgeDays * 86_400_000);
      await this.pool.query(
        `INSERT INTO chase_cases (id, company, contact, email, rm, chase_rounds, last_request_at)
         VALUES ($1, $2, $3, $4, 'Elena Vance', $5, $6) ON CONFLICT (id) DO NOTHING`,
        [sample.id, sample.company, sample.contact, sample.email, sample.rounds, sample.requestedDaysAgo === null ? null : requestedAt],
      );
      for (let index = 0; index < requiredDocs.length; index += 1) {
        const received = sample.received.includes(index);
        await this.pool.query(
          `INSERT INTO chase_documents (case_id, name, requested_at, received_at)
           VALUES ($1, $2, $3, $4) ON CONFLICT (case_id, name) DO NOTHING`,
          [sample.id, requiredDocs[index], requestedAt, received ? responseAt : null],
        );
      }
      await this.pool.query(
        `INSERT INTO chase_request_batches (case_id, sent_at, document_names, response_at)
         SELECT $1, $2, $3::jsonb, $4 WHERE NOT EXISTS (
           SELECT 1 FROM chase_request_batches WHERE case_id = $1
         )`,
        [sample.id, requestedAt, JSON.stringify(requiredDocs), sample.received.length ? responseAt : null],
      );
    }
  }
}
