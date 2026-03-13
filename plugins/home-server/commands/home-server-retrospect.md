---
name: home-server-retrospect
description: >-
  Review the current session for new server knowledge, configuration changes,
  or gotchas, then update the home-server skill references, memory files,
  and credentials store.
user_invocable: true
---

## Instructions

Run the `home-server:retrospect` agent with this prompt:

> Review this conversation for any new information about the nest home server that should be persisted. Look for:
>
> 1. New services deployed or removed
> 2. Configuration changes (ports, volumes, env vars, API keys)
> 3. New gotchas or workarounds discovered
> 4. Network/DNS/cert changes
> 5. Credential changes or new API keys
>
> Read the current state of all reference files and memory before proposing changes.
> Present a summary of what you'd update before making changes.
> Only update files that actually need changes — don't touch files where nothing is new.

Use the Agent tool with `subagent_type: "home-server:retrospect"`.
