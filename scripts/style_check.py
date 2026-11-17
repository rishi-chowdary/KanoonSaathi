#!/usr/bin/env python3
"""Repository style and hygiene check script."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EMOJI_RE = re.compile(
    "["
    "\U0001f300-\U0001f9ff"
    "\U0001fa00-\U0001faff"
    "\u2600-\u26ff"
    "\u2700-\u27bf"
    "]"
)

BANNED_WORDS = [
    "seamless",
    "seamlessly",
    "robust",
    "leverage",
    "comprehensive",
    "cutting-edge",
    "state-of-the-art",
    "powerful",
    "revolutionize",
    "unlock",
    "empower",
    "supercharge",
    "game-changer",
    "delve",
    "elevate",
    "streamline",
    "effortlessly",
    "exhaustive",
    "in today's fast-paced world",
    "ai-powered",
]
BANNED_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(w) for w in BANNED_WORDS) + r")\b",
    re.IGNORECASE,
)

LEAKED_TERMS = [
    r"\brule\s*[467]\b",
    r"\brule_[467]\b",
    r"\brule[467]\b",
    r"\btri[-\s_]?tier\b",
    r"\blegal advice guard\b",
    r"\bhardened\b",
    r"\bdossier\b",
    r"\bphase\s*m\d*\b",
    r"\bper spec\b",
]
LEAKED_RE = re.compile("|".join(LEAKED_TERMS), re.IGNORECASE)

TODO_RE = re.compile(r"\b(?:TODO|FIXME)\b")
COMMENTED_CODE_RE = re.compile(
    r"^\s*#\s*(?:def |class |if |elif |else:|for |while |return |import |from |try:|except |[a-z_][a-z0-9_]*\s*=\s*)"
)
JINJA_SAFE_RE = re.compile(r"\|\s*safe\b")

EXCLUDED_DOCS: set[str] = set()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_files(dirs: list[str], suffixes: tuple[str, ...]) -> list[Path]:
    found: list[Path] = []
    for entry in dirs:
        target = ROOT / entry
        if not target.exists():
            continue
        if target.is_file():
            if target.suffix in suffixes:
                found.append(target)
        else:
            for p in sorted(target.rglob("*")):
                if (
                    p.is_file()
                    and p.suffix in suffixes
                    and "__pycache__" not in p.parts
                ):
                    found.append(p)
    return found


def check_emojis(errors: list[str]) -> None:
    files = iter_files(
        ["app", "tests", "scripts", "docs", "README.md"],
        (".py", ".html", ".css", ".js", ".md"),
    )
    for path in files:
        r = rel(path)
        if r in EXCLUDED_DOCS or r == "scripts/style_check.py":
            continue
        if "vendor/" in r:
            continue
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
        ):
            if EMOJI_RE.search(line):
                errors.append(f"[emoji] {r}:{lineno}: {line.strip()[:80]}")


def check_banned_words(errors: list[str]) -> None:
    files = iter_files(
        ["app/templates", "docs", "README.md"],
        (".html", ".md"),
    )
    for path in files:
        r = rel(path)
        if r in EXCLUDED_DOCS:
            continue
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
        ):
            match = BANNED_RE.search(line)
            if match:
                errors.append(f"[banned-word] {r}:{lineno}: matched '{match.group(0)}'")


def check_leaked_terms(errors: list[str]) -> None:
    files = iter_files(
        [
            "app",
            "tests",
            "data",
            "docs",
            "README.md",
            "evaluation/evaluate_nlp_stack.py",
            "evaluation/RESULTS.md",
        ],
        (".py", ".html", ".css", ".js", ".yaml", ".yml", ".md"),
    )
    for path in files:
        r = rel(path)
        if r in EXCLUDED_DOCS or "vendor/" in r:
            continue
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
        ):
            match = LEAKED_RE.search(line)
            if match:
                errors.append(f"[leaked-term] {r}:{lineno}: matched '{match.group(0)}'")


def check_python_hygiene(errors: list[str], warnings: list[str]) -> None:
    py_files = iter_files(["app", "tests", "scripts"], (".py",))
    for path in py_files:
        r = rel(path)
        if r == "scripts/style_check.py":
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        code_lines = 0
        comment_lines = 0
        consecutive_commented_code = 0

        for lineno, line in enumerate(lines, 1):
            stripped = line.strip()
            if TODO_RE.search(line):
                errors.append(f"[todo] {r}:{lineno}: {stripped[:80]}")

            if stripped.startswith("#"):
                comment_lines += 1
                if COMMENTED_CODE_RE.match(line):
                    consecutive_commented_code += 1
                    if consecutive_commented_code == 3:
                        errors.append(
                            f"[commented-code] {r}:{lineno - 2}-{lineno}: block of commented-out code"
                        )
                else:
                    consecutive_commented_code = 0
            else:
                consecutive_commented_code = 0
                if stripped:
                    code_lines += 1

        if r.startswith("app/") and (code_lines + comment_lines) > 0:
            ratio = comment_lines / (code_lines + comment_lines)
            if ratio > 0.25:
                errors.append(
                    f"[comment-ratio] {r}: {ratio * 100:.1f}% comments (>25% limit)"
                )

        if r.startswith("app/"):
            tree = ast.parse("\n".join(lines), filename=r)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    end = getattr(node, "end_lineno", node.lineno)
                    length = end - node.lineno + 1
                    if length > 60:
                        warnings.append(
                            f"[long-function] {r}:{node.lineno} {node.name}() is {length} lines"
                        )


def check_css(errors: list[str]) -> None:
    for path in iter_files(["app/static/css"], (".css",)):
        r = rel(path)
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            lower = line.lower()
            if "gradient(" in lower:
                errors.append(f"[css-gradient] {r}:{lineno}: {line.strip()[:80]}")
            if "backdrop-filter" in lower:
                errors.append(f"[css-backdrop] {r}:{lineno}: {line.strip()[:80]}")
            if (
                "box-shadow" in lower
                and "none" not in lower
                and not re.search(r"0\s+0\s+0\s+[123]px", lower)
            ):
                errors.append(f"[css-shadow] {r}:{lineno}: {line.strip()[:80]}")


def check_jinja_safe(errors: list[str]) -> None:
    for path in iter_files(["app/templates"], (".html",)):
        r = rel(path)
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if JINJA_SAFE_RE.search(line):
                errors.append(f"[jinja-safe] {r}:{lineno}: {line.strip()[:80]}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    check_emojis(errors)
    check_banned_words(errors)
    check_leaked_terms(errors)
    check_python_hygiene(errors, warnings)
    check_css(errors)
    check_jinja_safe(errors)

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"FAIL  {e}")

    if errors:
        print(
            f"\nstyle_check failed: {len(errors)} error(s), {len(warnings)} warning(s)"
        )
        return 1

    print(f"style_check passed: 0 errors, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
