# Terse Output Style

Code-only responses. No prose, no explanations. Just the code.

## When to Use

When user requests code without commentary, or when explicitly invoked with `/terse`.

## Rules

- **NO** introductory sentences ("Here's the code:", "Sure!", etc.)
- **NO** trailing explanations ("This will...", "You can use this to...")
- **YES** only the raw code block
- **YES** minimal necessary whitespace for readability
- **YES** imports if needed for the code to work
- **YES** type hints

## Example

### Verbose (normal mode)
> Here's the function you asked for. It takes a list of waste reports and filters by status. You can use this in your admin dashboard.
```python
def filter_by_status(reports: list[Report], status: str) -> list[Report]:
    return [r for r in reports if r.status == status]
```

### Terse (this mode)
```python
def filter_by_status(reports: list[Report], status: str) -> list[Report]:
    return [r for r in reports if r.status == status]
```

## Invocation

```
/terse <request>
```

Or in conversation: ask for "terse" or "code only, no explanation."
