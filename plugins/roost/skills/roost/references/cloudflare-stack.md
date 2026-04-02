# Cloudflare Stack Reference

Deep reference for Cloudflare Workers ecosystem primitives, React Router 7 integration, Drizzle ORM, and wrangler CLI.

## LLM Documentation

Fetch current docs when needed:

- General: `https://developers.cloudflare.com/llms.txt`
- Per-product: `https://developers.cloudflare.com/{product}/llms.txt`
  - Workers: `https://developers.cloudflare.com/workers/llms.txt`
  - Pages: `https://developers.cloudflare.com/pages/llms.txt`
  - D1: `https://developers.cloudflare.com/d1/llms.txt`
  - KV: `https://developers.cloudflare.com/kv/llms.txt`
  - R2: `https://developers.cloudflare.com/r2/llms.txt`
  - Queues: `https://developers.cloudflare.com/queues/llms.txt`
  - Durable Objects: `https://developers.cloudflare.com/durable-objects/llms.txt`
  - Workers AI: `https://developers.cloudflare.com/workers-ai/llms.txt`
  - Vectorize: `https://developers.cloudflare.com/vectorize/llms.txt`
  - Containers: `https://developers.cloudflare.com/containers/llms.txt`

## Framework Decision: React Router 7 vs Hono

| Scenario                       | Use                                                      | Why                                                          |
| ------------------------------ | -------------------------------------------------------- | ------------------------------------------------------------ |
| Full-stack SaaS with UI        | **React Router 7**                                       | SSR for SEO/AI SEO, file-based routing, single Worker deploy |
| API-only microservice          | **Hono**                                                 | No SSR overhead, lightweight, pure REST/GraphQL              |
| Adding UI to existing Hono API | **React Router 7** (new) + keep Hono via service binding | Incremental migration                                        |

Roost defaults to React Router 7 for all new projects with UI.

## React Router 7 on Cloudflare Workers

React Router 7 in framework mode with SSR runs directly on Workers via `@cloudflare/vite-plugin`.

### Setup

```bash
# Create new project
bunx create-react-router@latest my-app --template cloudflare
```

### Vite Config

```typescript
import { cloudflare } from '@cloudflare/vite-plugin';
import { reactRouter } from '@react-router/dev/vite';
import tsconfigPaths from 'vite-tsconfig-paths';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [cloudflare({ viteEnvironment: { name: 'ssr' } }), reactRouter(), tsconfigPaths()],
});
```

### React Router Config

```typescript
// react-router.config.ts
import type { Config } from '@react-router/dev/config';

export default {
  ssr: true,
  future: { v8_viteEnvironmentApi: true },
} satisfies Config;
```

### Worker Entry

```typescript
// workers/app.ts
import { createRequestHandler } from 'react-router';

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext) {
    const requestHandler = createRequestHandler(
      () => import('virtual:react-router/server-build'),
      import.meta.env.MODE
    );
    return requestHandler(request, { env, ctx });
  },
  async scheduled(controller: ScheduledController, env: Env, ctx: ExecutionContext) {
    // Cron handlers
  },
  async queue(batch: MessageBatch, env: Env, ctx: ExecutionContext) {
    // Queue consumer
  },
} satisfies ExportedHandler<Env>;
```

### Route Patterns

```typescript
// app/routes/api.v1.users.tsx — API resource route
import type { Route } from './+types/api.v1.users';
import { getDb } from '~/src/core/db/db';
import { users } from '~/src/core/db/schema';
import { requireAuth } from '~/app/lib/api-auth';

export async function loader({ request, context }: Route.LoaderArgs) {
  const { env } = context.cloudflare;
  const session = await requireAuth(request, env);
  const db = getDb(env.DB);
  const allUsers = await db.select().from(users);
  return Response.json({ users: allUsers });
}

export async function action({ request, context }: Route.ActionArgs) {
  const { env } = context.cloudflare;
  const session = await requireAuth(request, env);
  // Handle POST/PUT/DELETE
}
```

### Accessing Cloudflare Bindings in Routes

```typescript
// In any RR7 loader or action:
export async function loader({ context }: Route.LoaderArgs) {
  const { env, ctx } = context.cloudflare;
  const db = getDb(env.DB); // D1 via Drizzle
  const value = await env.KV.get(key); // KV
  const obj = await env.STORAGE.get(key); // R2
  await env.QUEUE.send(message); // Queue
  const result = await env.AI.run(model, input); // Workers AI
}
```

## Workers Runtime

Cloudflare Workers run V8 isolates at the edge. No cold starts for standard Workers.

### Key Characteristics

- Request/response model via `fetch` handler
- 128 MB memory limit per invocation
- CPU time limits: 10ms (free), 30s (paid), 15min (Cron Triggers)
- No Node.js built-ins by default (use `nodejs_compat` flag)
- Environment bindings for all CF services

### Hono on Workers (API-only projects)

For API-only services without UI:

```typescript
import { Hono } from 'hono';
const app = new Hono<{ Bindings: Env }>();

app.get('/api/health', (c) => c.json({ ok: true }));
export default app;
```

### Environment Bindings Type

```typescript
// src/core/types.ts
interface Env {
  // Databases
  DB: D1Database;
  KV: KVNamespace;
  STORAGE: R2Bucket;
  QUEUE: Queue;

  // AI
  AI: Ai;
  VECTORIZE: VectorizeIndex;

  // Durable Objects
  USER_CONNECTION_DO: DurableObjectNamespace;

  // Service Bindings
  RSSHUB: Fetcher; // Cloudflare Container

  // Static Assets (RR7)
  ASSETS: { fetch: typeof fetch };

  // Secrets
  WORKOS_API_KEY: string;
  WORKOS_CLIENT_ID: string;
  WORKOS_COOKIE_PASSWORD: string;
  STRIPE_SECRET_KEY: string;
  STRIPE_WEBHOOK_SECRET: string;
  RESEND_API_KEY: string;
  TWILIO_AUTH_TOKEN: string;
  POSTHOG_API_KEY: string;

  // Vars
  ENVIRONMENT: string;
  APP_URL: string;
  APP_NAME: string;
  EMAIL_DOMAIN: string;
  TWILIO_ACCOUNT_SID: string;
  TWILIO_FROM_NUMBER: string;
  POSTHOG_HOST: string;
}
```

## D1 — SQL Database (via Drizzle ORM)

SQLite-based, globally distributed. All access via Drizzle — never raw SQL in application code.

### Drizzle Setup

```typescript
// src/core/db/db.ts
import { drizzle } from 'drizzle-orm/d1';
import * as schema from './schema';

export function getDb(d1: D1Database) {
  return drizzle(d1, { schema });
}
```

### Query Patterns

```typescript
import { eq, and } from 'drizzle-orm';
import { getDb } from '~/src/core/db/db';
import { users, orgMembers } from '~/src/core/db/schema';

// Select
const user = await db.select().from(users).where(eq(users.email, email)).get();

// Insert
await db.insert(users).values({ id: generateId(), email, name }).run();

// Update
await db.update(users).set({ name: newName }).where(eq(users.id, userId)).run();

// Join
const members = await db
  .select({ user: users, membership: orgMembers })
  .from(orgMembers)
  .innerJoin(users, eq(orgMembers.userId, users.id))
  .where(eq(orgMembers.orgId, orgId))
  .all();

// Transaction (D1 batch)
await db.batch([
  db.insert(users).values({ id, email, name }),
  db.insert(orgMembers).values({ id: memberId, userId: id, orgId }),
]);
```

### Migration Workflow

```bash
# 1. Edit src/core/db/schema.ts
# 2. Generate migration SQL
bunx drizzle-kit generate

# 3. Apply locally
wrangler d1 migrations apply <DB_NAME> --local

# 4. Apply to production
wrangler d1 migrations apply <DB_NAME> --remote
```

### Drizzle Config

```typescript
// drizzle.config.ts
import { defineConfig } from 'drizzle-kit';

export default defineConfig({
  schema: './src/core/db/schema.ts',
  out: './src/core/db/migrations',
  dialect: 'sqlite',
});
```

## KV — Key-Value Store

Eventually consistent, high read throughput. Best for sessions, config, feature flags, caching.

```typescript
await env.KV.put('session:abc', JSON.stringify(data), { expirationTtl: 3600 });
const session = await env.KV.get('session:abc', 'json');
```

### When to Use KV vs D1

| Need                                    | Use          |
| --------------------------------------- | ------------ |
| Structured queries, joins, transactions | D1 (Drizzle) |
| High-frequency reads, simple key lookup | KV           |
| Session storage, feature flags, cursors | KV           |
| User profiles, orders, billing records  | D1 (Drizzle) |

## R2 — Object Storage

S3-compatible with zero egress fees. For user uploads, assets, exports.

```typescript
// Upload
await env.STORAGE.put(`uploads/${userId}/${filename}`, file, {
  httpMetadata: { contentType: 'image/png' },
});

// Download
const object = await env.STORAGE.get(`uploads/${userId}/${filename}`);
```

## Queues — Async Messaging

Durable message delivery for background jobs: email sends, webhook delivery, data processing.

```typescript
// Producer (in RR7 action/loader)
await env.QUEUE.send({ type: 'send-email', to: email, template: 'welcome', data: { name } });

// Consumer (in workers/app.ts queue handler)
export default {
  async queue(batch: MessageBatch<EmailJob>, env: Env) {
    for (const message of batch.messages) {
      try {
        await processJob(message.body, env);
        message.ack();
      } catch (err) {
        message.retry();
      }
    }
  },
};
```

## Durable Objects — Strongly Consistent State

Per-object strong consistency with transactional storage and WebSocket hibernation.

### Use Cases

- Real-time collaboration (shared documents, cursors)
- WebSocket rooms (chat, presence, live updates)
- Rate limiting with exact counts
- Distributed locks

### Pattern: WebSocket Hub

```typescript
// src/core/durable-objects/UserConnectionDO.ts
import { DurableObject } from 'cloudflare:workers';

export class UserConnectionDO extends DurableObject {
  async fetch(request: Request): Promise<Response> {
    if (request.headers.get('Upgrade') === 'websocket') {
      const pair = new WebSocketPair();
      this.ctx.acceptWebSocket(pair[1]);
      return new Response(null, { status: 101, webSocket: pair[0] });
    }
    return new Response('Expected WebSocket', { status: 400 });
  }

  async webSocketMessage(ws: WebSocket, message: string) {
    // Broadcast to all connected clients
    for (const client of this.ctx.getWebSockets()) {
      if (client !== ws) client.send(message);
    }
  }

  async webSocketClose(ws: WebSocket) {
    ws.close();
  }
}
```

### wrangler.toml Config

```toml
[[durable_objects.bindings]]
name = "USER_CONNECTION_DO"
class_name = "UserConnectionDO"

[[migrations]]
tag = "v1"
new_classes = ["UserConnectionDO"]
```

## Workers AI — Serverless GPU Inference

Run AI models directly on Cloudflare's edge network.

### Available Model Types

- Text generation: `@cf/meta/llama-3.1-8b-instruct`
- Text embeddings: `@cf/baai/bge-base-en-v1.5` (768-dim)
- Image generation: `@cf/stabilityai/stable-diffusion-xl-base-1.0`
- Speech-to-text: `@cf/openai/whisper`
- Translation, classification, summarization

### Usage Pattern

```typescript
// Text generation
const result = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
  messages: [{ role: 'user', content: prompt }],
});

// Embeddings
const embeddings = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
  text: ['document to embed'],
});
```

### AI Gateway (optional)

Route AI calls through Cloudflare AI Gateway for caching, rate limiting, and observability:

```typescript
// Via env vars
const result = await env.AI.run(model, input, {
  gateway: { id: env.AI_GATEWAY_ID },
});
```

## Vectorize — Vector Database

Semantic search and similarity matching. Pairs with Workers AI embeddings.

```typescript
// Insert vectors
await env.VECTORIZE.upsert([
  {
    id: entryId,
    values: embedding, // 768-dim float array
    metadata: { title, userId },
  },
]);

// Query
const results = await env.VECTORIZE.query(queryEmbedding, {
  topK: 10,
  filter: { userId },
  returnMetadata: 'all',
});
```

### wrangler.toml Config

```toml
[[vectorize]]
binding = "VECTORIZE"
index_name = "my-app-entries"
```

## Containers — Docker Workloads

Run Docker containers on Cloudflare for workloads that need a full runtime (long-running processes, specific system libraries, sidecar services).

### Use Cases

- RSS feed processor (RSSHub)
- Headless browser for screenshots
- Background data pipelines
- Custom ML model serving

### Service Binding Pattern

```toml
# wrangler.toml
[[services]]
binding = "RSSHUB"
service = "rsshub-container"
```

```typescript
// Access via service binding
const response = await env.RSSHUB.fetch('http://rsshub/twitter/user/example');
```

### Local Development

Use Docker Compose locally, Cloudflare Containers in production:

```yaml
# docker-compose.yml
services:
  rsshub:
    image: diygod/rsshub:latest
    ports:
      - '1200:1200'
```

## Wrangler CLI

### Essential Commands

| Command                                                             | Purpose                                    |
| ------------------------------------------------------------------- | ------------------------------------------ |
| `wrangler dev`                                                      | Local development server                   |
| `wrangler deploy`                                                   | Deploy to production                       |
| `wrangler d1 create <name>`                                         | Create D1 database                         |
| `wrangler d1 migrations apply <db>`                                 | Apply D1 migrations                        |
| `wrangler kv namespace create <name>`                               | Create KV namespace                        |
| `wrangler r2 bucket create <name>`                                  | Create R2 bucket                           |
| `wrangler queues create <name>`                                     | Create queue                               |
| `wrangler vectorize create <name> --dimensions=768 --metric=cosine` | Create vector index                        |
| `wrangler secret put <name>`                                        | Set secret (interactive)                   |
| `wrangler tail`                                                     | Live log streaming                         |
| `wrangler types`                                                    | Generate typed bindings from wrangler.toml |

### wrangler.toml Structure

```toml
name = "my-app"
main = "workers/app.ts"
compatibility_date = "2025-01-01"
compatibility_flags = ["nodejs_compat"]
assets = { binding = "ASSETS", directory = "./build/client" }

[observability]
enabled = true

[[d1_databases]]
binding = "DB"
database_name = "my-app-db"
database_id = "xxx"
migrations_dir = "src/core/db/migrations"

[[kv_namespaces]]
binding = "KV"
id = "xxx"

[[r2_buckets]]
binding = "STORAGE"
bucket_name = "my-app-storage"

[[queues.producers]]
binding = "QUEUE"
queue = "my-app-jobs"

[[queues.consumers]]
queue = "my-app-jobs"
max_batch_size = 10
max_retries = 3

[ai]
binding = "AI"

[[vectorize]]
binding = "VECTORIZE"
index_name = "my-app-entries"

[[durable_objects.bindings]]
name = "USER_CONNECTION_DO"
class_name = "UserConnectionDO"

[[migrations]]
tag = "v1"
new_classes = ["UserConnectionDO"]

[triggers]
crons = ["*/15 * * * *"]

[vars]
ENVIRONMENT = "production"
APP_URL = "https://app.example.com"
APP_NAME = "My SaaS"
```
