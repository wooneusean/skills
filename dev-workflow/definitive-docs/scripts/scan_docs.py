#!/usr/bin/env python3
"""Find candidate non-definitive prose in docs and comments.

This is a heuristic candidate finder. It cannot distinguish durable rationale
("batch size is 500 because the API caps payloads at 1MB") from change
narration ("batch size should be 500 instead of 200"). Every hit requires
human or model judgment. Do not bulk-apply substitutions to its output.

Usage:
    python scan_docs.py docs/ CLAUDE.md
    python scan_docs.py . --category hedging,temporal_rot
    python scan_docs.py . --include-source --format json
"""

import argparse
import fnmatch
import json
import os
import re
import sys

DOC_EXTS = {".md", ".mdx", ".markdown", ".rst", ".txt", ".adoc"}

# Line-comment markers, by source extension. Used only when --include-source
# is set, to avoid flagging string literals and identifiers in code.
COMMENT_MARKERS = {
    ".py": ("#",), ".rb": ("#",), ".sh": ("#",), ".bash": ("#",), ".zsh": ("#",),
    ".yml": ("#",), ".yaml": ("#",), ".toml": ("#",), ".tf": ("#",), ".pl": ("#",),
    ".js": ("//", "*", "/*"), ".jsx": ("//", "*", "/*"), ".ts": ("//", "*", "/*"),
    ".tsx": ("//", "*", "/*"), ".go": ("//", "*", "/*"), ".java": ("//", "*", "/*"),
    ".c": ("//", "*", "/*"), ".h": ("//", "*", "/*"), ".cc": ("//", "*", "/*"),
    ".cpp": ("//", "*", "/*"), ".hpp": ("//", "*", "/*"), ".cs": ("//", "*", "/*"),
    ".rs": ("//", "*", "/*"), ".swift": ("//", "*", "/*"), ".kt": ("//", "*", "/*"),
    ".php": ("//", "#", "*", "/*"), ".scala": ("//", "*", "/*"), ".sql": ("--",),
    ".lua": ("--",), ".hs": ("--",), ".ex": ("#",), ".exs": ("#",),
}

# Files that exist to record history. Definitizing these destroys their point.
EXEMPT_NAME_PATTERNS = [
    "CHANGELOG*", "CHANGES*", "HISTORY*", "NEWS*", "RELEASE_NOTES*", "RELEASES*",
    "UPGRADING*", "UPGRADE*", "MIGRATION*", "MIGRATING*", "POSTMORTEM*",
    "RETROSPECTIVE*", "*postmortem*", "*retrospective*", "*.patch", "*.diff",
]
EXEMPT_DIR_PATTERNS = [
    ".git", "node_modules", "vendor", "dist", "build", "target", ".venv", "venv",
    "__pycache__", ".next", ".tox", "site-packages", ".mypy_cache", ".pytest_cache",
    "adr", "adrs", "decisions", "rfcs", "rfc", "migrations", "migration",
    "changelog", "changelogs", "postmortems", "retrospectives",
]

CATEGORIES = {
    "change_narration": (
        "Describes a delta from a state the reader cannot see",
        r"\b(should (?:now )?be|should instead|instead of|rather than before|"
        r"changed (?:from|to)|change[ds] this|updated to|has been updated|"
        r"renamed to|was renamed|switched to|swapped (?:to|for)|"
        r"now (?:uses?|returns?|accepts?|requires?|supports?|defaults?|points?)|"
        r"no longer|used to (?:be|use|return)|previously|formerly|"
        r"has been (?:changed|moved|removed|replaced|renamed)|"
        r"we (?:changed|moved|removed|added|switched|replaced|renamed)|"
        r"replaced (?:with|by)|as opposed to before|"
        r"the (?:old|former|previous) (?:value|behavior|version|implementation))\b"
    ),
    "research_narration": (
        "Reports how the fact was established instead of the fact",
        r"\b(based on (?:a |the |my )?(?:search|grep|review|reading|inspection|"
        r"analysis|look)|after (?:checking|searching|reviewing|reading|inspecting|"
        r"looking)|upon (?:checking|review|inspection)|per (?:the |your )?"
        r"(?:user|request|clarification|instruction)|as requested|as (?:you |we )?"
        r"(?:asked|requested|discussed|mentioned|agreed)|according to my|"
        r"from what I (?:can tell|found|see)|I (?:found|checked|searched|verified|"
        r"confirmed|noticed)|having (?:checked|reviewed|read)|"
        r"(?:my|the) investigation)\b"
    ),
    "hedging": (
        "Transfers the writer's uncertainty to every future reader",
        r"\b(should probably|probably|might be|may be|seems? to|appears? to|"
        r"I (?:think|believe|assume|suspect|expect)|presumably|it looks like|"
        r"looks like it|not (?:entirely )?sure|unclear (?:whether|if|why|how)|"
        r"possibly|perhaps|apparently|in theory|I'm guessing|"
        r"(?:most )?likely (?:because|due|the))\b"
    ),
    "temporal_rot": (
        "True only at the instant of writing",
        r"\b(currently|at present|right now|for (?:the )?(?:now|time being|moment)|"
        r"at the moment|as of (?:now|today|this writing|the time)|recently|"
        r"newly (?:added|introduced|created)|just added|the new\b|"
        r"new (?:implementation|approach|version|system|way)|latest version|"
        r"nowadays|these days|going forward|from now on|temporar(?:y|ily)|"
        r"soon|shortly|in the (?:near )?future|upcoming|not yet implemented|"
        r"still (?:being|under) (?:worked|development|discussion))\b"
    ),
    "conversational": (
        "Addresses a reader who is not there",
        r"\b(note that you|you asked|you mentioned|you wanted|let me know|"
        r"as we discussed|feel free to|hope(?:fully)? this helps|"
        r"remember (?:that )?we|last time|in our (?:chat|conversation|discussion)|"
        r"to answer your|your question|as you can see|"
        r"(?:I|we)'ve (?:gone ahead and|now))\b"
    ),
    "self_reference": (
        "Document narrating its own maintenance",
        r"\b(this (?:section|document|doc|file|comment|note|paragraph) "
        r"(?:was|has been|is being) (?:added|updated|written|revised|expanded|"
        r"rewritten|corrected|clarified)|fixed a bug where|this fix(?:es)?|"
        r"corrected (?:the|this|an)|the (?:earlier|previous|old) version "
        r"(?:of )?(?:this )?(?:doc|file|section|said)|added for clarity|"
        r"expanded per|per (?:review|feedback)|clarif(?:ied|ying) that)\b"
    ),
    "deferred_uncertainty": (
        "Announces the doc may be lying, assigns it to nobody",
        r"(\bTODO\b(?!\s*\(\s*@)|\bFIXME\b|\bXXX\b|\bTBD\b|"
        r"\bverify (?:this|that|whether)|\bneeds? (?:verification|confirmation|"
        r"checking)|\bdouble[- ]?check|\bconfirm (?:this|that|whether)|"
        r"\bnot sure if this is (?:still )?(?:true|accurate|correct))"
    ),
}


def is_exempt(path):
    parts = [p.lower() for p in os.path.normpath(path).split(os.sep)]
    for part in parts[:-1]:
        for pat in EXEMPT_DIR_PATTERNS:
            if part == pat.lower():
                return True
    name = os.path.basename(path)
    for pat in EXEMPT_NAME_PATTERNS:
        if fnmatch.fnmatch(name.upper(), pat.upper()):
            return True
    return False


def collect_files(targets, include_source):
    seen, out = set(), []
    for target in targets:
        if os.path.isfile(target):
            candidates = [target]
        else:
            candidates = []
            for root, dirs, files in os.walk(target):
                dirs[:] = [
                    d for d in dirs
                    if not d.startswith(".")
                    and d.lower() not in {p.lower() for p in EXEMPT_DIR_PATTERNS}
                ]
                candidates.extend(os.path.join(root, f) for f in files)
        for path in candidates:
            ext = os.path.splitext(path)[1].lower()
            wanted = ext in DOC_EXTS or (include_source and ext in COMMENT_MARKERS)
            if not wanted or is_exempt(path):
                continue
            real = os.path.realpath(path)
            if real not in seen:
                seen.add(real)
                out.append(path)
    return sorted(out)


def scannable_lines(path, ext):
    """Yield (lineno, text) for lines worth scanning.

    Markdown fenced code blocks are skipped: sample output and config snippets
    produce noise. For source files, only comment lines are scanned.
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError as exc:
        print(f"  ! could not read {path}: {exc}", file=sys.stderr)
        return

    is_doc = ext in DOC_EXTS
    markers = COMMENT_MARKERS.get(ext, ())
    in_fence = False
    fence_re = re.compile(r"^\s*(```|~~~)")

    for i, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        if is_doc:
            if fence_re.match(line):
                in_fence = not in_fence
                continue
            if in_fence or line.startswith("    ") or line.startswith("\t"):
                continue  # indented code block
            yield i, line
        else:
            stripped = line.strip()
            if any(stripped.startswith(m) for m in markers):
                yield i, stripped
            else:
                for m in markers:
                    if m in ("*",):
                        continue
                    idx = line.find(m)
                    if idx > 0:
                        yield i, line[idx:]
                        break


def scan(paths, categories, include_source):
    patterns = {
        name: re.compile(spec[1], re.IGNORECASE)
        for name, spec in CATEGORIES.items()
        if name in categories
    }
    results = {}
    for path in collect_files(paths, include_source):
        ext = os.path.splitext(path)[1].lower()
        hits = []
        for lineno, text in scannable_lines(path, ext):
            for name, rx in patterns.items():
                m = rx.search(text)
                if m:
                    hits.append({
                        "line": lineno,
                        "category": name,
                        "match": m.group(0),
                        "text": text.strip()[:160],
                    })
        if hits:
            results[path] = hits
    return results


def main():
    ap = argparse.ArgumentParser(
        description="Find candidate non-definitive prose in docs and comments.",
        epilog="Heuristic only. Every hit needs judgment; never bulk-substitute.",
    )
    ap.add_argument("paths", nargs="*", default=["."],
                    help="files or directories to scan (default: .)")
    ap.add_argument("--category", default="all",
                    help="comma-separated subset: " + ",".join(CATEGORIES))
    ap.add_argument("--include-source", action="store_true",
                    help="also scan comments in source files")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--list-categories", action="store_true")
    args = ap.parse_args()

    if args.list_categories:
        for name, (desc, _) in CATEGORIES.items():
            print(f"{name:22} {desc}")
        return 0

    if args.category == "all":
        cats = set(CATEGORIES)
    else:
        cats = {c.strip() for c in args.category.split(",") if c.strip()}
        unknown = cats - set(CATEGORIES)
        if unknown:
            ap.error(f"unknown categor{'y' if len(unknown) == 1 else 'ies'}: "
                     f"{', '.join(sorted(unknown))}")

    results = scan(args.paths or ["."], cats, args.include_source)

    if args.format == "json":
        print(json.dumps(results, indent=2))
        return 1 if results else 0

    if not results:
        print("No candidates found.")
        return 0

    total = 0
    by_cat = {}
    for path, hits in results.items():
        print(f"\n{path}")
        for h in sorted(hits, key=lambda x: x["line"]):
            print(f"  {h['line']:>5}  [{h['category']}] \"{h['match']}\"")
            print(f"         {h['text']}")
            total += 1
            by_cat[h["category"]] = by_cat.get(h["category"], 0) + 1

    print(f"\n{'-' * 60}")
    print(f"{total} candidate(s) across {len(results)} file(s)")
    for name, count in sorted(by_cat.items(), key=lambda kv: -kv[1]):
        print(f"  {count:>4}  {name} — {CATEGORIES[name][0]}")
    print("\nCandidates, not verdicts. Apply the fresh-reader and twelve-month")
    print("tests to each; durable rationale and history files stay as they are.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
