# CLAUDE.md template — Next.js 15 + SQLite SaaS

An opinionated `CLAUDE.md` to drop at the root of a greenfield Next.js 15 (App
Router) + SQLite (`better-sqlite3` / Turso) SaaS project.

## Use

```bash
cp CLAUDE.md /path/to/your-new-project/CLAUDE.md
```

Then edit the **Stack & versions** table if your choices differ — everything else
is written to be used as-is.

## What it covers

- **Stack & versions** — one table, every row with the reason it was chosen
- **Folder structure** — `app/` orchestrates, `features/` decides, `db/` persists
- **SQL & migration conventions** — append-only numbered migrations, reversible
  pairs, parameterised queries only, multi-step writes in a transaction
- **Naming conventions** — files, components, tables, columns, hooks
- **Component patterns** — server components by default, client boundaries explicit
- **What we don't do (and why)** — the anti-pattern list, each with its reasoning

## Design rule

Every rule carries a reason. If a rule can't justify itself in one line, it
doesn't belong in the file — otherwise Claude follows it blindly and you can't
tell a real convention from a leftover preference.
