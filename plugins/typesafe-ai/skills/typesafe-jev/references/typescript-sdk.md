# TypeScript & Node/Edge Integration Guide

## Overview

In TypeScript applications (Next.js, Remix, Hono, Express, Cloudflare Workers), TypeSafe AI provides native **Zod** schema inference and parallel decision sampling with sub-20ms latency.

---

## Installation & Setup

```bash
npm install @typesafe-ai/jev zod
```

---

## Example 1: Typed Intent Classifier with Zod

```typescript
import { JevClient } from "@typesafe-ai/jev"
import { z } from "zod"

const client = new JevClient({
  apiKey: process.env.TYPESAFE_API_KEY!,
})

// Define strictly typed output schema
const IntentSchema = z.object({
  action: z.enum(["CHECK_BALANCE", "TRANSFER_FUNDS", "SPEAK_WITH_AGENT", "DISPUTE"]),
  requiresAuth: z.boolean(),
  urgencyScore: z.number().min(0).max(10),
})

export type Intent = z.infer<typeof IntentSchema>

export async function routeUserMessage(userMessage: string): Promise<Intent> {
  const result = await client.decide({
    input: userMessage,
    schema: IntentSchema,
  })

  // Check calibrated probability
  if (result.confidence < 0.85) {
    console.warn(`Ambiguous intent (confidence: ${result.confidence}). Falling back to human agent.`)
    return { action: "SPEAK_WITH_AGENT", requiresAuth: true, urgencyScore: 5 }
  }

  return result.data
}
```

---

## Example 2: Edge Runtime & Cloudflare Workers

Because Jev does not run heavy token generation or streaming, edge functions can return decisions within single-digit milliseconds:

```typescript
import { JevClient } from "@typesafe-ai/jev"
import { z } from "zod"

const ModerationSchema = z.object({
  status: z.enum(["APPROVED", "FLAGGED", "REJECTED"]),
  flagReason: z.string().optional(),
})

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { comment } = await request.json()
    const jev = new JevClient({ apiKey: env.TYPESAFE_API_KEY })

    const decision = await jev.decide({
      input: comment,
      schema: ModerationSchema,
    })

    if (decision.confidence >= 0.90 && decision.data.status === "APPROVED") {
      // Fast path: commit directly to DB without holding request
      return Response.json({ allowed: true })
    }

    return Response.json({ allowed: false, review: true })
  },
}
```
