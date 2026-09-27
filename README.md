# claude-code-kit

> Guardrails, automation and templates for **Claude Code** — three small tools, no
> SDK, no dependencies, nothing to install beyond Python 3.

[![ci](https://github.com/15818681903-netizen/claude-code-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/15818681903-netizen/claude-code-kit/actions/workflows/ci.yml)

| Tool | What it is | Verified by |
|------|-----------|-------------|
| [`hooks/bash-guard`](hooks/bash-guard) | A `PreToolUse` hook that blocks `rm -rf`, `DROP TABLE`, `TRUNCATE`, `DELETE` without `WHERE` and `git push --force` — before Claude Code runs them — and logs every block | **23/23** assertions |
| [`n8n/weekly-github-summary`](n8n/weekly-github-summary) | An importable n8n workflow: every Friday 5pm it reads a repo's commits/PRs/issues, asks Claude for a narrative summary, delivers to Discord/Slack or email | 12-node structural validation + JS/expression checks |
| [`templates/nextjs-sqlite`](templates/nextjs-sqlite) | An opinionated `CLAUDE.md` for a Next.js 15 + SQLite SaaS — every rule carries its reason | covers all 5 required sections |

---

## 1. `bash-guard` — stop the destructive command before it runs

```bash
mkdir -p ~/.claude/hooks && curl -fsSL https://raw.githubusercontent.com/15818681903-netizen/claude-code-kit/main/hooks/bash-guard/bash-guard.py -o ~/.claude/hooks/bash-guard.py && chmod +x ~/.claude/hooks/bash-guard.py
```

Then register it in `~/.claude/settings.json` (the full 2-command snippet is in
[the README](hooks/bash-guard)). It emits the canonical
`{"permissionDecision":"deny"}` payload, exits `2`, and appends a JSONL line to
`~/.claude/hooks/blocked.log` with timestamp, command, project path and matched rule.

What it deliberately does **not** block: `rm -f file`, `rm -r dir`,
`git push origin main`, `git push --follow-tags`, `DELETE FROM t WHERE id=3;`,
and quoted text like `echo 'rm -rf is dangerous'` — 10 of the 21 command cases are
false-positive traps.

## 2. `weekly-github-summary` — the Friday summary you never write

Import the JSON into n8n, attach a GitHub credential and an Anthropic header-auth
credential, set the repo/channel/language in the `Config` node, activate. Five steps,
documented in [the README](n8n/weekly-github-summary).

Validate without n8n:

```bash
python3 n8n/weekly-github-summary/validate_workflow.py
```

## 3. `templates/nextjs-sqlite` — a CLAUDE.md that has opinions

```bash
cp templates/nextjs-sqlite/CLAUDE.md /path/to/your-project/CLAUDE.md
```

Covers stack & versions, folder structure, SQL/migration conventions, naming,
component patterns, and an explicit "what we don't do (and why)" list. The rule
for the file itself: if a rule can't justify itself in one line, it is not a
convention — it is a preference, and it does not belong here.

---

## Run the checks

```bash
python3 hooks/bash-guard/test_bash_guard.py
python3 n8n/weekly-github-summary/validate_workflow.py
```

Both run from any directory and need no third-party packages. CI runs them on
every push.

## Honest limits

- **`weekly-github-summary` has not been executed on a live n8n instance.** Its
  structure, JavaScript and `{{ }}` expressions are validated offline; importing it
  and hitting *Execute Workflow* once is the remaining step.
- **`templates/nextjs-sqlite` has not been validated in a live Claude Code session.**
  It is derived from a real Next.js + SQLite layout, not from a recorded session.
- **`bash-guard` matches command text, not a shell AST.** Obfuscation
  (`r''m -rf`) can slip past. It is a guardrail against the common accidental
  destructive command, not a sandbox.

## 中文

给 Claude Code 用的三件小工具：**危险命令拦截 hook**（`rm -rf` / `DROP TABLE` /
`TRUNCATE` / 无 `WHERE` 的 `DELETE` / `git push --force`，带 JSONL 审计日志）、
**n8n 周报工作流**（每周五 17:00 拉 GitHub 活动 → Claude 写叙述式总结 → Discord/Slack/邮件）、
**Next.js + SQLite 的 `CLAUDE.md` 模板**（每条规则都写了理由）。

三者都无第三方依赖，`python3` 直接可跑；CI 会在每次 push 时执行全部检查。
上面的「Honest limits」一节如实列出了尚未完成的两项实机验证。

## License

MIT — see [LICENSE](LICENSE).
