# Context Compression Skill

## Overview
This skill monitors the length of the conversation context for any agent. When the token count approaches a configurable threshold (default **100,000 tokens**), it automatically:

1. **Summarizes** the oldest portions of the context using the configured LLM.
2. **Appends** the summary to the long‑term memory file `MEMORY.md` (or a dedicated `context-summary.md`).
3. **Resets** the in‑memory context to start from the recent interaction, keeping the summary as a concise reference.

The process is effectively a **Retrieval‑Augmented Generation (RAG)** pattern: older context is compressed into a persistent store and later fetched when needed.

## How it works
- **Trigger**: `should_compress(context, limit=100_000)` checks the token count (approximate characters / 4).
- **Summarize**: `compress(context, model='openrouter/auto')` sends the oldest chunk to the LLM with a prompt:
  > "Summarize the following conversation excerpt in 200‑300 words, preserving key decisions, facts, and actions."
- **Persist**: The summary is written to `memory/context-summary.md` and also appended to `MEMORY.md` under a *## Context Snapshots* section.
- **Reset**: The original context is cleared (or trimmed) so the agent starts fresh while still having access to the summary via the memory file.

## Integration steps for any agent
1. **Import the helper**:
   ```python
   from skills.context_compression.compress_context import maybe_compress
   ```
2. **Call after each response** (e.g., in `SmartAgent.process` or the main loop):
   ```python
   await maybe_compress(self.conversation_history)
   ```
3. **Configure** (optional) by setting environment variables:
   - `CTX_COMPRESS_LIMIT` – token threshold.
   - `CTX_SUMMARY_PATH` – where to store the summary (default `memory/context-summary.md`).

## Dependencies
- `openai` or any OpenRouter‑compatible client for summarization.
- `tiktoken` (optional) for precise token counting.

## Example usage in an agent
```python
from skills.context_compression.compress_context import maybe_compress

class SmartAgent:
    async def process(self, message, user_id, username):
        # ... existing logic ...
        reply = await self.generate_reply(message)
        # After sending reply, ensure context stays manageable
        await maybe_compress(self.history)
        return reply
```

## Notes
- The skill is **idempotent** – calling `maybe_compress` when below the limit does nothing.
- Summaries are version‑controlled via Git, so you can review the compression history.
- Adjust `model` and prompt to suit your domain (e.g., technical vs casual).

---
*Created by Claw – your personal OpenClaw assistant.*