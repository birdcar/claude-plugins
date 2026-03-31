# Cloudflare Stack Reference

Deep reference for Cloudflare Workers ecosystem primitives, deployment patterns, and wrangler CLI.

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

## Workers Runtime

Cloudflare Workers run V8 isolates at the edge. No cold starts for standard Workers.

### Key Characteristics

- Request/response model via `fetch` handler
- 128 MB memory limit per invocation
- CPU time limits: 10ms (free), 30s (paid), 15min (Cron Triggers)
- No filesystem, no Node.js built-ins by default (use `nodejs_compat` flag)
- Environment bindings for all CF services (D1, KV, R2, Queues, DO)

### Hono on Workers

Hono is the preferred API framework for Workers:

```typescript
import { Hono } from 'hono';
const app = new Hono<{ Bindings: Env }>();

app.get('/api/health', (c) => c.json({ ok: true }));
export default app;
```

Hono middleware pattern for auth, CORS, logging:

```typescript
app.use('/api/*', cors());
app.use('/api/*', authMiddleware());
```

### Environment Bindings Type

```typescript
interface Env {
  DB: D1Database;
  KV: KVNamespace;
  BUCKET: R2Bucket;
  QUEUE: Queue;
  WORKOS_API_KEY: string;
  WORKOS_CLIENT_ID: string;
  STRIPE_SECRET_KEY: string;
  STRIPE_WEBHOOK_SECRET: string;
  RESEND_API_KEY: string;
}
```

## D1 — SQL Database

SQLite-based, globally distributed with read replicas. Ideal for structured data: users, orgs, subscriptions, orders, listings.

### Characteristics

- SQLite dialect — no JOINs across databases, but full SQL within one DB
- Read replicas for global low-latency reads
- Write operations routed to primary
- 10 GB per database (paid plan)
- Batch queries for transactional operations

### Usage Pattern

```typescript
const result = await c.env.DB.prepare('SELECT * FROM users WHERE org_id = ?').bind(orgId).all();

// Batch for transactions
await c.env.DB.batch([
  c.env.DB.prepare('INSERT INTO users (id, name) VALUES (?, ?)').bind(id, name),
  c.env.DB.prepare('INSERT INTO org_members (user_id, org_id) VALUES (?, ?)').bind(id, orgId),
]);
```

### Migration Pattern

Place migration files in `migrations/` directory:

```sql
-- migrations/0001_create_users.sql
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name TEXT,
  workos_user_id TEXT UNIQUE,
  stripe_customer_id TEXT UNIQUE,
  created_at TEXT DEFAULT (datetime('now'))
);
```

Apply with: `wrangler d1 migrations apply <DB_NAME>`

## KV — Key-Value Store

Eventually consistent, high read throughput. Best for sessions, config, feature flags, caching.

### Characteristics

- Key: up to 512 bytes, Value: up to 25 MB
- Eventually consistent (reads may lag writes by ~60s)
- Global distribution with edge caching
- Metadata per key (up to 1 KB)
- Expiration and expiration TTL support

### Usage Pattern

```typescript
await c.env.KV.put('session:abc', JSON.stringify(sessionData), {
  expirationTtl: 3600, // 1 hour
});
const session = await c.env.KV.get('session:abc', 'json');
```

### When to Use KV vs D1

| Need                                    | Use |
| --------------------------------------- | --- |
| Structured queries, joins, transactions | D1  |
| High-frequency reads, simple key lookup | KV  |
| Session storage, feature flags          | KV  |
| User profiles, orders, billing records  | D1  |

## R2 — Object Storage

S3-compatible with zero egress fees. For user uploads, assets, exports.

### Characteristics

- S3 API compatible
- Zero egress fees (major cost advantage)
- Multipart upload support for large files
- Presigned URLs for direct client uploads

### Usage Pattern

```typescript
// Upload
await c.env.BUCKET.put(`uploads/${userId}/${filename}`, file, {
  httpMetadata: { contentType: 'image/png' },
});

// Download
const object = await c.env.BUCKET.get(`uploads/${userId}/${filename}`);
if (object) {
  return new Response(object.body, {
    headers: { 'Content-Type': object.httpMetadata?.contentType || 'application/octet-stream' },
  });
}

// Presigned URL (via S3 API)
// Requires R2 API token with appropriate permissions
```

## Queues — Async Messaging

Durable message delivery for background jobs: email sends, webhook delivery, data processing.

### Characteristics

- At-least-once delivery guarantee
- Configurable batch size and retry
- Dead letter queues for failed messages
- Producer: any Worker; Consumer: dedicated Worker

### Usage Pattern

```typescript
// Producer
await c.env.QUEUE.send({
  type: 'send-email',
  to: 'user@example.com',
  template: 'welcome',
  data: { name: 'Alice' },
});

// Consumer (separate Worker or same with queue handler)
export default {
  async queue(batch: MessageBatch<EmailJob>, env: Env) {
    for (const message of batch.messages) {
      try {
        await processEmail(message.body, env);
        message.ack();
      } catch (err) {
        message.retry();
      }
    }
  },
};
```

## Durable Objects — Strongly Consistent State

Per-object strong consistency. For real-time collaboration, rate limiting, WebSocket coordination.

### Characteristics

- Single instance per ID globally
- Strongly consistent within one object
- Transactional storage API
- WebSocket hibernation for long-lived connections
- Alarm API for scheduled work

### When to Use

- Real-time collaboration (shared documents, cursors)
- Rate limiting with exact counts
- WebSocket rooms (chat, presence)
- Distributed locks

## Pages — Frontend Deployment

For React/Vite frontends. Integrates with Workers for full-stack apps.

### Build Configuration

```toml
# In wrangler.toml for Pages
[site]
bucket = "./dist"

# Or use pages_build_output_dir
pages_build_output_dir = "packages/web/dist"
```

### Vite Config for Pages

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
```

## Additional Primitives

### Workers AI

Serverless GPU inference with ~50 open-source models. Access via `AI` binding:

```typescript
const result = await c.env.AI.run('@cf/meta/llama-3-8b-instruct', {
  messages: [{ role: 'user', content: prompt }],
});
```

### Vectorize

Vector database for semantic search. Pairs with Workers AI for embeddings.

### Hyperdrive

Connection pooler for existing Postgres/MySQL databases. Reduces latency for external DB connections.

### Workflows

Durable multi-step orchestration with automatic retry and state persistence.

### Containers

Docker-compatible workloads on Cloudflare. For tasks that need full OS, long-running processes.

### Pipelines

High-volume streaming data ingestion.

## Wrangler CLI

### Essential Commands

| Command                               | Purpose                  |
| ------------------------------------- | ------------------------ |
| `wrangler dev`                        | Local development server |
| `wrangler deploy`                     | Deploy to production     |
| `wrangler d1 create <name>`           | Create D1 database       |
| `wrangler d1 migrations apply <db>`   | Apply D1 migrations      |
| `wrangler kv namespace create <name>` | Create KV namespace      |
| `wrangler r2 bucket create <name>`    | Create R2 bucket         |
| `wrangler queues create <name>`       | Create queue             |
| `wrangler secret put <name>`          | Set secret (interactive) |
| `wrangler tail`                       | Live log streaming       |
| `wrangler pages deploy <dir>`         | Deploy Pages project     |

### wrangler.toml Structure

```toml
name = "my-app-api"
main = "src/index.ts"
compatibility_date = "2024-01-01"
compatibility_flags = ["nodejs_compat"]

[[d1_databases]]
binding = "DB"
database_name = "my-app-db"
database_id = "xxx"

[[kv_namespaces]]
binding = "KV"
id = "xxx"

[[r2_buckets]]
binding = "BUCKET"
bucket_name = "my-app-uploads"

[[queues.producers]]
binding = "QUEUE"
queue = "my-app-jobs"

[[queues.consumers]]
queue = "my-app-jobs"
max_batch_size = 10
max_retries = 3

[vars]
ENVIRONMENT = "production"
```

## Project Structure Convention

Roost generates a monorepo with separate API and web packages:

```
my-app/
  packages/
    api/                  # Hono on Workers
      src/
        index.ts          # Entry point
        routes/           # Route handlers
        middleware/        # Auth, CORS, billing
        lib/              # Shared utilities
        db/
          schema.ts       # D1 schema types
          migrations/     # SQL migrations
      wrangler.toml
    web/                  # React + Vite on Pages
      src/
        main.tsx
        routes/           # File-based or React Router
        components/
        lib/
      vite.config.ts
    shared/               # Shared types, constants
      src/
        types.ts
  package.json            # Workspace root
```
