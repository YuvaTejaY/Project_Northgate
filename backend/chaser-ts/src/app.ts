import cors from "cors";
import express, { type ErrorRequestHandler } from "express";
import { z } from "zod";
import { requireUser } from "./auth.js";
import { HttpError, type ChaseRepository } from "./types.js";

const createCaseSchema = z.object({
  company: z.string().trim().min(1).max(255),
  contact: z.string().trim().min(1).max(255),
  email: z.string().trim().email().max(255),
}).strict();
const draftSchema = z.object({ draft: z.string().max(20_000) }).strict();
const requestSchema = z.object({ manualSendConfirmed: z.literal(true) }).strict();
const receivedSchema = z.object({}).strict();

export function createApp(repository: ChaseRepository, options: {
  jwtSecret: string;
  allowedOrigins: string[];
  isActiveUser: (id: string) => Promise<boolean>;
}) {
  const app = express();
  app.use(cors({ origin: options.allowedOrigins }));
  app.use(express.json({ limit: "64kb" }));
  app.get("/health", (_request, response) => response.json({ status: "healthy", service: "document-chaser-api" }));
  app.use("/api", requireUser(options.jwtSecret, options.isActiveUser));

  app.post("/api/cases", async (request, response, next) => {
    try {
      const parsed = createCaseSchema.safeParse(request.body);
      if (!parsed.success) throw new HttpError(422, "Provide a company, client contact, and valid client email");
      response.status(201).json(await repository.createCase(parsed.data));
    } catch (error) {
      next(error);
    }
  });

  app.get("/api/cases", async (_request, response, next) => {
    try {
      response.json(await repository.listCases());
    } catch (error) {
      next(error);
    }
  });

  app.get("/api/cases/:caseId", async (request, response, next) => {
    try {
      const item = await repository.getCase(request.params.caseId);
      if (!item) throw new HttpError(404, "Onboarding case not found");
      response.json(item);
    } catch (error) {
      next(error);
    }
  });

  app.put("/api/cases/:caseId/draft", async (request, response, next) => {
    try {
      const parsed = draftSchema.safeParse(request.body);
      if (!parsed.success) throw new HttpError(422, "Draft must be a JSON object with a string draft (maximum 20,000 characters)");
      const item = await repository.updateDraft(request.params.caseId, parsed.data.draft);
      if (!item) throw new HttpError(404, "Onboarding case not found");
      response.json(item);
    } catch (error) {
      next(error);
    }
  });

  app.post("/api/cases/:caseId/requests", async (request, response, next) => {
    try {
      const parsed = requestSchema.safeParse(request.body);
      if (!parsed.success) throw new HttpError(422, "Manual send confirmation is required before recording a request");
      const item = await repository.recordRequest(request.params.caseId);
      if (!item) throw new HttpError(404, "Onboarding case not found");
      response.json(item);
    } catch (error) {
      next(error);
    }
  });

  app.post("/api/cases/:caseId/documents/:documentName/received", async (request, response, next) => {
    try {
      const parsed = receivedSchema.safeParse(request.body);
      if (!parsed.success) throw new HttpError(422, "Request body must be an empty JSON object");
      const item = await repository.recordReceived(request.params.caseId, request.params.documentName);
      if (!item) throw new HttpError(404, "Case or document not found");
      response.json(item);
    } catch (error) {
      next(error);
    }
  });

  const handleError: ErrorRequestHandler = (error: unknown, _request, response, _next) => {
    if (error instanceof HttpError) {
      response.status(error.status).json({ detail: error.message });
      return;
    }
    console.error("Document-chaser request failed", error);
    response.status(500).json({ detail: "Internal server error" });
  };
  app.use(handleError);
  return app;
}
