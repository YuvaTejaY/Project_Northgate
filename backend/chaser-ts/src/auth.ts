import type { NextFunction, Request, Response } from "express";
import jwt, { type JwtPayload } from "jsonwebtoken";

const permittedRoles = new Set(["admin", "analyst", "reviewer"]);
const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export interface AuthenticatedRequest extends Request {
  userId?: string;
}

export function requireUser(secret: string, isActiveUser: (id: string) => Promise<boolean>) {
  return async (request: AuthenticatedRequest, response: Response, next: NextFunction): Promise<void> => {
    const authorization = request.header("authorization");
    const token = authorization?.match(/^Bearer\s+(.+)$/i)?.[1];
    if (!token) {
      response.status(401).json({ detail: "Bearer access token required" });
      return;
    }

    let payload: JwtPayload | string;
    try {
      payload = jwt.verify(token, secret, { algorithms: ["HS256"] });
    } catch {
      response.status(401).json({ detail: "Invalid or expired access token" });
      return;
    }

    if (
      typeof payload === "string"
      || !payload.sub
      || !uuidPattern.test(payload.sub)
      || payload.type !== "access"
      || typeof payload.role !== "string"
      || !permittedRoles.has(payload.role.toLowerCase())
    ) {
      response.status(403).json({ detail: "An active RM, analyst, or admin access token is required" });
      return;
    }

    const userId = payload.sub;
    try {
      if (!await isActiveUser(userId)) {
        response.status(401).json({ detail: "User account is inactive or no longer exists" });
        return;
      }
    } catch (error) {
      next(error);
      return;
    }
    request.userId = userId;
    next();
  };
}
