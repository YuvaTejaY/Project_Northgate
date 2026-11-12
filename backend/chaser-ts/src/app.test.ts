import assert from "node:assert/strict";
import { createServer } from "node:http";
import { once } from "node:events";
import { test } from "node:test";
import jwt from "jsonwebtoken";
import { createApp } from "./app.js";
import type { ChaseCase, ChaseRepository } from "./types.js";

const secret = "test-secret-that-is-long-enough";
const demoCase: ChaseCase = {
  id: "KYC-1",
  company: "Example Corp",
  contact: "Alex Client",
  email: "alex@example.com",
  rm: "Elena Vance",
  chaseRounds: 0,
  lastRequestAt: null,
  draft: "",
  documents: [{ name: "Certificate of Incorporation", requestedAt: null, receivedAt: null }],
  requestHistory: [],
};

function makeRepository(): ChaseRepository {
  const item = structuredClone(demoCase);
  return {
    async createCase(input) {
      const created = { ...structuredClone(demoCase), id: "KYC-2", ...input };
      return created;
    },
    async listCases() { return [item]; },
    async getCase(id) { return id === item.id ? item : null; },
    async updateDraft(id, draft) {
      if (id !== item.id) return null;
      item.draft = draft;
      return item;
    },
    async recordRequest(id) {
      if (id !== item.id) return null;
      item.chaseRounds += 1;
      item.lastRequestAt = new Date().toISOString();
      item.documents[0]!.requestedAt = item.lastRequestAt;
      item.requestHistory.push({
        sentAt: item.lastRequestAt,
        documentNames: [item.documents[0]!.name],
        responseAt: null,
      });
      return item;
    },
    async recordReceived(id, name) {
      if (id !== item.id || name !== item.documents[0]!.name) return null;
      if (!item.documents[0]!.requestedAt) return null;
      item.documents[0]!.receivedAt = new Date().toISOString();
      item.requestHistory[0]!.responseAt = item.documents[0]!.receivedAt;
      return item;
    },
  };
}

async function withServer(run: (baseUrl: string) => Promise<void>): Promise<void> {
  const server = createServer(createApp(makeRepository(), {
    jwtSecret: secret,
    allowedOrigins: ["http://localhost:8000"],
    isActiveUser: async (id) => id === userId,
  }));
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  const address = server.address();
  assert(address && typeof address === "object");
  try {
    await run(`http://127.0.0.1:${address.port}`);
  } finally {
    server.close();
    await once(server, "close");
  }
}

const userId = "00000000-0000-4000-8000-000000000001";
const accessToken = jwt.sign({ sub: userId, role: "Reviewer", type: "access" }, secret, { algorithm: "HS256", expiresIn: "5m" });
const authHeaders = { Authorization: `Bearer ${accessToken}` };

test("health endpoint is public and the chase API requires a valid access token", async () => {
  await withServer(async (baseUrl) => {
    const health = await fetch(`${baseUrl}/health`);
    assert.equal(health.status, 200);
    const unauthenticated = await fetch(`${baseUrl}/api/cases`);
    assert.equal(unauthenticated.status, 401);
    const cases = await fetch(`${baseUrl}/api/cases`, { headers: authHeaders });
    assert.equal(cases.status, 200);
    assert.equal((await cases.json() as ChaseCase[])[0]?.id, "KYC-1");

    const inactiveToken = jwt.sign({ sub: "00000000-0000-4000-8000-000000000002", role: "Reviewer", type: "access" }, secret, { algorithm: "HS256" });
    const inactive = await fetch(`${baseUrl}/api/cases`, { headers: { Authorization: `Bearer ${inactiveToken}` } });
    assert.equal(inactive.status, 401);
  });
});

test("drafts and request recording require validated input and manual-send confirmation", async () => {
  await withServer(async (baseUrl) => {
    const invalidDraft = await fetch(`${baseUrl}/api/cases/KYC-1/draft`, {
      method: "PUT",
      headers: { ...authHeaders, "Content-Type": "application/json" },
      body: JSON.stringify({ draft: "Draft", unexpected: true }),
    });
    assert.equal(invalidDraft.status, 422);

    const unconfirmed = await fetch(`${baseUrl}/api/cases/KYC-1/requests`, {
      method: "POST",
      headers: { ...authHeaders, "Content-Type": "application/json" },
      body: JSON.stringify({ manualSendConfirmed: false }),
    });
    assert.equal(unconfirmed.status, 422);

    const recorded = await fetch(`${baseUrl}/api/cases/KYC-1/requests`, {
      method: "POST",
      headers: { ...authHeaders, "Content-Type": "application/json" },
      body: JSON.stringify({ manualSendConfirmed: true }),
    });
    assert.equal(recorded.status, 200);
    const body = await recorded.json() as ChaseCase;
    assert.equal(body.chaseRounds, 1);
    assert.equal(body.documents[0]?.requestedAt !== null, true);

    const savedDraft = await fetch(`${baseUrl}/api/cases/KYC-1/draft`, {
      method: "PUT",
      headers: { ...authHeaders, "Content-Type": "application/json" },
      body: JSON.stringify({ draft: "Reviewed client request" }),
    });
    assert.equal(savedDraft.status, 200);

    const receipt = await fetch(`${baseUrl}/api/cases/KYC-1/documents/Certificate%20of%20Incorporation/received`, {
      method: "POST",
      headers: { ...authHeaders, "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    assert.equal(receipt.status, 200);
    const completed = await receipt.json() as ChaseCase;
    assert.equal(completed.documents[0]?.receivedAt !== null, true);
    assert.equal(completed.requestHistory[0]?.responseAt !== null, true);
  });
});

test("authenticated users can create a case with validated client details", async () => {
  await withServer(async (baseUrl) => {
    const invalid = await fetch(`${baseUrl}/api/cases`, {
      method: "POST",
      headers: { ...authHeaders, "Content-Type": "application/json" },
      body: JSON.stringify({ company: "", contact: "Client", email: "not-an-email" }),
    });
    assert.equal(invalid.status, 422);

    const created = await fetch(`${baseUrl}/api/cases`, {
      method: "POST",
      headers: { ...authHeaders, "Content-Type": "application/json" },
      body: JSON.stringify({ company: "New Corp", contact: "Alex Client", email: "alex@example.com" }),
    });
    assert.equal(created.status, 201);
    const item = await created.json() as ChaseCase;
    assert.equal(item.company, "New Corp");
    assert.equal(item.documents.length, 1);
  });
});
