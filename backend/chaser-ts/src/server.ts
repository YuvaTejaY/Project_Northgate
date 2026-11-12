import "dotenv/config";
import { Pool } from "pg";
import { createApp } from "./app.js";
import { PostgresChaseRepository } from "./postgres-repository.js";

const port = Number(process.env.PORT ?? 8001);
const databaseUrl = process.env.DATABASE_URL;
const jwtSecret = process.env.SECRET_KEY;
const seedDemoData = process.env.SEED_DEMO_DATA === "true";
if (!databaseUrl) throw new Error("DATABASE_URL must be configured");
if (!jwtSecret || jwtSecret.length < 32 || jwtSecret.includes("replace-me")) {
  throw new Error("Set a strong SECRET_KEY of at least 32 characters, shared with the FastAPI authentication service");
}

const allowedOrigins = (process.env.ALLOWED_ORIGINS ?? "http://localhost:8000,http://127.0.0.1:8000")
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);
const pool = new Pool({ connectionString: databaseUrl });
const repository = new PostgresChaseRepository(pool);
const app = createApp(repository, {
  jwtSecret,
  allowedOrigins,
  isActiveUser: async (id) => {
    const result = await pool.query(
      "SELECT 1 FROM users WHERE id = $1 AND is_active = TRUE AND LOWER(role::text) = ANY($2::text[])",
      [id, ["admin", "analyst", "reviewer"]],
    );
    return result.rowCount === 1;
  },
});

async function start(): Promise<void> {
  await repository.initialize(seedDemoData);
  const server = app.listen(port, "0.0.0.0", () => {
    console.log(`Document Chaser API listening on port ${port}`);
  });
  const shutdown = () => {
    server.close(() => {
      void pool.end().then(() => process.exit(0));
    });
  };
  process.once("SIGINT", shutdown);
  process.once("SIGTERM", shutdown);
}

void start().catch(async (error: unknown) => {
  console.error("Unable to start Document Chaser API", error);
  await pool.end();
  process.exitCode = 1;
});
