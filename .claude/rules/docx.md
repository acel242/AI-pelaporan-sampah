# DOCX Rules — Word Document Generation

Loads when working in `docs/**` or when creating/editing `.docx` files.

## Skill Reference

Use the `docx` skill for:
- Creating new `.docx` files with `docx-js`
- Editing existing documents (unpack → edit XML → repack)
- Adding tracked changes, comments, tables of contents
- Validating documents

Location: `~/.agents/skills/docx/SKILL.md`

---

## Project Documents

This project generates proposals and reports in Word format:
- `PROPOSAL.md`, `PROPOSAL_V2.md`, `PROPOSAL_V3.md` — proposal drafts (markdown)
- `PROPOSAL_ECOLAPOR_MANADO.docx` — final Word document for funder submission

## Quick Workflow: Markdown → DOCX

```bash
# Convert markdown proposal to DOCX
pandoc PROPOSAL_V3.md -o PROPOSAL_FINAL.docx
```

## Full DOCX Creation (for polished documents)

```bash
# Install docx
npm install -g docx

# Create document (see docx skill for full patterns)
node scripts/create_proposal.js

# Validate
python scripts/office/validate.py PROPOSAL_FINAL.docx
```

## Key Rules

- **Use `docx-js` for new documents** — programmatic generation with tables, images, TOC
- **Use `pandoc` for quick conversions** — one-command markdown → docx
- **Page size**: always set explicitly (A4 for Indonesian government proposals)
- **Never use `\n`** in docx-js — use separate `Paragraph` elements
- **Never use unicode bullets** — use `LevelFormat.BULLET` with numbering config
- **Tables**: set both `width` and `columnWidths` in DXA units
- **Validate after creation** — `python scripts/office/validate.py`
