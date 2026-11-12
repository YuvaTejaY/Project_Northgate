export interface DocumentRecord {
  name: string;
  requestedAt: string | null;
  receivedAt: string | null;
}

export interface RequestBatch {
  sentAt: string;
  documentNames: string[];
  responseAt: string | null;
}

export interface ChaseCase {
  id: string;
  company: string;
  contact: string;
  email: string;
  rm: string;
  chaseRounds: number;
  lastRequestAt: string | null;
  draft: string;
  documents: DocumentRecord[];
  requestHistory: RequestBatch[];
}

export interface CreateCaseInput {
  company: string;
  contact: string;
  email: string;
}

export interface ChaseRepository {
  createCase(input: CreateCaseInput): Promise<ChaseCase>;
  listCases(): Promise<ChaseCase[]>;
  getCase(id: string): Promise<ChaseCase | null>;
  updateDraft(id: string, draft: string): Promise<ChaseCase | null>;
  recordRequest(id: string): Promise<ChaseCase | null>;
  recordReceived(id: string, documentName: string): Promise<ChaseCase | null>;
}

export class HttpError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "HttpError";
  }
}
