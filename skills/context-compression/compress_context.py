import os
import asyncio
from math import ceil

# Optional: use tiktoken for accurate token count if available
try:
    import tiktoken
    ENCODER = tiktoken.get_encoding('cl100k_base')
except Exception:
    ENCODER = None

# Configuration via env vars
TOKEN_LIMIT = int(os.getenv('CTX_COMPRESS_LIMIT', '100000'))  # approx tokens
SUMMARY_PATH = os.getenv('CTX_SUMMARY_PATH', 'memory/context-summary.md')
MODEL = os.getenv('CTX_SUMMARY_MODEL', 'openrouter/auto')

# Simple prompt for summarization
SUMMARY_PROMPT = (
    "You are summarizing a long conversation. Produce a concise summary (200‑300 words) "
    "that captures key decisions, facts, and actions. Keep the tone neutral."
)

async def _count_tokens(text: str) -> int:
    if ENCODER:
        return len(ENCODER.encode(text))
    # Rough approximation: 1 token ≈ 4 characters
    return ceil(len(text) / 4)

async def _summarize(chunk: str) -> str:
    # Minimal stub – replace with actual LLM call.
    # Here we just prepend a marker for demonstration.
    return f"[SUMMARY]\n{chunk[:min(500, len(chunk))]}...\n"

async def maybe_compress(context: list[dict]) -> None:
    """Check the accumulated context and compress if it exceeds the token limit.

    `context` is expected to be a list of message dicts as used by the OpenClaw
    agent (e.g., `{'role': 'user', 'content': '...'}').
    """
    # Join all messages into a single string for token estimation
    full_text = "\n".join(msg.get('content', '') for msg in context)
    token_count = await _count_tokens(full_text)
    if token_count < TOKEN_LIMIT:
        return  # No need to compress

    # Determine how much to truncate – we keep the newest half
    half = len(context) // 2
    old_chunk = "\n".join(context[i].get('content', '') for i in range(half))

    # Generate summary (replace with real LLM call in production)
    summary = await _summarize(old_chunk)

    # Append summary to the summary file (create if missing)
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "a", encoding="utf-8") as f:
        f.write("\n--- Context Summary ---\n")
        f.write(summary)
        f.write("\n--- End Summary ---\n")

    # Trim the old part from the in‑memory context
    del context[:half]

    # Also optionally append a reference to MEMORY.md for long‑term storage
    mem_path = os.path.join(os.path.dirname(SUMMARY_PATH), "../MEMORY.md")
    if os.path.exists(mem_path):
        with open(mem_path, "a", encoding="utf-8") as mem:
            mem.write("\n## Context Snapshot\n")
            mem.write(summary)
            mem.write("\n")

# For manual testing
if __name__ == "__main__":
    example = [{"role": "user", "content": "a" * 20000}] * 10
    asyncio.run(maybe_compress(example))
    print("Done")
