#!/usr/bin/env python3
"""Test suite for bash-guard.py — runnable from any working directory."""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

HOOK = str(pathlib.Path(__file__).resolve().with_name("bash-guard.py"))

CASES = [
    # (command, should_block)
    ("rm -rf /tmp/foo", True),
    ("rm -rf node_modules", True),
    ("sudo rm -rf /", True),
    ("rm -f file.txt", False),
    ("rm file.txt", False),
    ("rm -r olddir", False),
    ('psql -c "DROP TABLE users;"', True),
    ('mysql -e "drop database prod"', True),
    ('psql -c "DELETE FROM users;"', True),
    ('psql -c "DELETE FROM users WHERE id=3;"', False),
    ('psql -c "TRUNCATE TABLE logs;"', True),
    ("git push --force origin main", True),
    ("git push -f", True),
    ("git push --force-with-lease", True),
    ("git push origin main", False),
    ("git push --follow-tags", False),
    ("ls -la", False),
    ("echo 'rm -rf is dangerous' > note.txt", False),  # quoted text, not execution
    ("npm run build", False),
    ("docker compose up -d", False),
    ("git commit -m 'fix rm -rf handling'", False),  # commit message text only
]


def run_hook(cmd, log_path):
    payload = json.dumps({"tool_input": {"command": cmd}, "cwd": "/tmp/proj"})
    env = dict(os.environ, BASH_GUARD_LOG=str(log_path))
    return subprocess.run(
        [sys.executable, HOOK], input=payload, capture_output=True, text=True, env=env
    )


def main() -> int:
    fails = 0
    tmp = tempfile.NamedTemporaryFile(prefix="bash-guard-", suffix=".log", delete=False)
    tmp.close()
    log_path = pathlib.Path(tmp.name)

    for cmd, expect in CASES:
        r = run_hook(cmd, log_path)
        blocked = r.returncode == 2
        ok = blocked == expect
        if not ok:
            fails += 1
        print(f"{'OK ' if ok else 'XX '} block={blocked!s:5} expect={expect!s:5} | {cmd}")

    # The hook must emit the canonical Claude Code PreToolUse deny decision.
    decision_fail = 0
    r = run_hook("rm -rf /tmp/foo", log_path)
    try:
        out = json.loads(r.stdout)
        ok = out["hookSpecificOutput"]["permissionDecision"] == "deny"
    except Exception:
        ok = False
    if not ok:
        decision_fail += 1
    print(f"{'OK ' if ok else 'XX '} PreToolUse JSON deny decision on stdout")

    # Every blocked attempt must be logged with timestamp / command / project path.
    lines = [json.loads(x) for x in log_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    blocked_count = sum(1 for _, expect in CASES if expect) + 1
    log_ok = (
        len(lines) == blocked_count
        and all({"timestamp", "command", "project_path", "rules"} <= set(e) for e in lines)
        and all(e["project_path"] == "/tmp/proj" for e in lines)
    )
    if not log_ok:
        fails += 1
    print(
        f"{'OK ' if log_ok else 'XX '} blocked.log entries={len(lines)} "
        f"(expected {blocked_count}), all carry timestamp/command/project_path/rules"
    )

    log_path.unlink(missing_ok=True)
    total = len(CASES) + 2
    passed = total - fails
    print(f"\n{passed}/{total} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
