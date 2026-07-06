---
name: mem0-memory-flow
description: Suggest, review, approve, upload, and manually recall Mem0 long-term memories with a user-approval workflow. Use when the user mentions Mem0, memory hooks, memory candidates, important memories, manual recall, approving/rejecting memories, or sharing a reusable memory workflow with other agents.
---

# Mem0 Memory Flow

Use this skill to manage durable Mem0 memories without silent uploads.

## Rules

- Never upload a suggested memory without explicit user approval.
- When candidates exist, briefly report each candidate in Chinese: `id`, category, content, and reason.
- Store only durable facts: stable preferences, project rules, explicit decisions, repeated workflows, and lessons that prevent future mistakes.
- Do not store raw chat logs, temporary todos, one-off facts, passwords, API keys, tokens, cookies, private URLs, or unapproved third-party personal data.
- Keep recall manual unless the user explicitly changes that policy.
- Keep credentials in `.env.local` or environment variables. Never write keys into skill files, plugin manifests, prompts, public docs, or chat output.

## Setup

The scripts are bundled in `scripts/`. Run them from the target workspace root, or set `MEM0_WORKSPACE` to the workspace that should hold `.env.local` and `memory/`.

Required workspace files:

```text
.env.local        # contains MEM0_API_KEY=...
memory/           # local audit queue and suggestion queue
```

Recommended `.gitignore` entries:

```text
.env.local
memory/mem0_important_outbox.jsonl
memory/mem0_memory_suggestions.jsonl
memory/mem0_hook.log
```

Use the workspace's preferred Python. On this user's Windows workspace, use:

```powershell
C:\Users\jefeer\an\python.exe
```

## Manual Recall

Recall remains manual. Search before tasks where prior preferences or project rules may matter:

```powershell
python .agents\skills\mem0-memory-flow\scripts\mem0_memory.py search --query "当前任务要点" --top-k 8
```

## Suggest Candidates

Create a local candidate without uploading:

```powershell
python .agents\skills\mem0-memory-flow\scripts\mem0_suggest.py --category preference --content "用户偏好使用中文回答。" --reason "用户表达了稳定语言偏好。"
```

Then list candidates and report them to the user:

```powershell
python .agents\skills\mem0-memory-flow\scripts\mem0_review.py list
```

The user must decide whether to approve or reject.

## Approve Or Reject

Upload only after the user explicitly approves specific candidates:

```powershell
python .agents\skills\mem0-memory-flow\scripts\mem0_review.py approve <id>
```

Reject candidates the user does not want stored:

```powershell
python .agents\skills\mem0-memory-flow\scripts\mem0_review.py reject <id>
```

If the user directly approves a memory in the same turn, it is acceptable to upload it with:

```powershell
python .agents\skills\mem0-memory-flow\scripts\mem0_memory.py add --approved --category decision --source mem0-user-approved --content "..."
```

## Hook Mode

`scripts/mem0_suggest_hook.py` is a Stop-hook style helper. It reads the host payload from stdin, extracts the latest user/assistant turn, and appends local candidates to `memory/mem0_memory_suggestions.jsonl`. It never calls Mem0.

Use hook mode only for suggestions. After the hook creates candidates, the agent must summarize them to the user before any approval command is run.

## Categories

- `preference`: stable user preference, style, language, or workflow preference.
- `project`: durable project configuration, architecture, environment rule, or agent role.
- `decision`: user-approved decision likely to matter later.
- `lesson`: mistake, correction, or operational lesson that should prevent recurrence.
- `identity`: stable identity or communication rule.

## Verification

For local validation without uploading, use a temporary workspace:

```powershell
$env:MEM0_WORKSPACE = "C:\tmp\mem0-skill-test"
python .agents\skills\mem0-memory-flow\scripts\mem0_suggest.py --category decision --content "测试候选：上传必须人工批准。" --reason "验证候选队列。"
python .agents\skills\mem0-memory-flow\scripts\mem0_review.py list
```

Unset `MEM0_WORKSPACE` after testing.

