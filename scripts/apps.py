# /// script
# dependencies = ["pyyaml"]
# ///
"""Validate apps.yml and keep the README "Published Apps" table in sync.

apps.yml is the single source of truth for published apps (it also feeds the
"Made with Flet" showcase on flet.dev). The README table is generated from it,
so the two can never drift.

Usage:
    python scripts/apps.py sync     # validate apps.yml, then rewrite the README table
    python scripts/apps.py check    # validate + verify the table is up to date (used by CI)
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required. Install it with: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
APPS_YML = ROOT / "apps.yml"
README = ROOT / "README.md"
START = "<!-- APPS:START -->"
END = "<!-- APPS:END -->"

PLATFORMS = {
    "android": "Android",
    "ios": "iOS",
    "web": "Web",
    "windows": "Windows",
    "macos": "macOS",
    "linux": "Linux",
}
# Store key -> (display label); also defines the column order within "Install".
STORES = {
    "google_play": "Google Play",
    "app_store": "App Store",
    "microsoft_store": "Microsoft Store",
    "snap_store": "Snap Store",
    "other": "Store",
}


def load_apps() -> list[dict]:
    data = yaml.safe_load(APPS_YML.read_text(encoding="utf-8")) or {}
    return data.get("apps") or []


def validate(apps: list[dict]) -> list[str]:
    """Return a list of human-readable problems (empty means valid)."""
    errors: list[str] = []
    seen: set[str] = set()
    for i, app in enumerate(apps):
        where = app.get("name") or f"entry #{i + 1}"
        for field in ("name", "tagline"):
            if not app.get(field):
                errors.append(f"{where}: missing required field '{field}'")

        platforms = app.get("platforms") or []
        if not platforms:
            errors.append(f"{where}: needs at least one platform")
        for p in platforms:
            if p not in PLATFORMS:
                errors.append(
                    f"{where}: unknown platform '{p}' (allowed: {', '.join(PLATFORMS)})"
                )

        stores = app.get("stores") or {}
        if not stores:
            errors.append(f"{where}: needs at least one store link")
        for key, url in stores.items():
            if key not in STORES:
                errors.append(
                    f"{where}: unknown store '{key}' (allowed: {', '.join(STORES)})"
                )
            if not str(url).startswith("https://"):
                errors.append(f"{where}: store '{key}' URL must start with https://")

        for field in ("source", "website"):
            url = app.get(field)
            if url and not str(url).startswith("https://"):
                errors.append(f"{where}: '{field}' URL must start with https://")

        name_key = (app.get("name") or "").casefold()
        if name_key and name_key in seen:
            errors.append(f"{where}: duplicate app name")
        seen.add(name_key)
    return errors


def _source_link(url: str) -> str:
    host = (
        "GitHub"
        if "github.com" in url
        else "GitLab"
        if "gitlab" in url
        else "Codeberg"
        if "codeberg" in url
        else "Source"
    )
    return f"[{host}]({url})"


def render_table(apps: list[dict]) -> str:
    rows = [["App", "Description", "Platforms", "Install", "Source"]]
    for app in sorted(apps, key=lambda a: (a.get("name") or "").casefold()):
        platforms = " · ".join(
            PLATFORMS.get(p, p) for p in (app.get("platforms") or [])
        )
        stores = app.get("stores") or {}
        install = " · ".join(
            f"[{STORES[key]}]({stores[key]})" for key in STORES if key in stores
        )
        source = _source_link(app["source"]) if app.get("source") else "-"
        rows.append(
            [app.get("name", ""), app.get("tagline", ""), platforms, install, source]
        )

    widths = [max(len(row[c]) for row in rows) for c in range(len(rows[0]))]

    def fmt(row: list[str]) -> str:
        return (
            "| "
            + " | ".join(cell.ljust(widths[c]) for c, cell in enumerate(row))
            + " |"
        )

    lines = [fmt(rows[0]), "|" + "|".join("-" * (w + 2) for w in widths) + "|"]
    lines += [fmt(row) for row in rows[1:]]
    return "\n".join(lines)


def apply_table(table: str, *, write: bool) -> bool:
    """Splice the table between the markers. Returns True if README is already in sync."""
    text = README.read_text(encoding="utf-8")
    lines = text.split("\n")
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == START)
        end = next(i for i, line in enumerate(lines) if line.strip() == END)
    except StopIteration:
        sys.exit(f"README is missing the {START} / {END} markers.")
    if end <= start:
        sys.exit(
            f"README markers are in the wrong order: {END} appears before {START}."
        )

    new_lines = lines[: start + 1] + ["", table, ""] + lines[end:]
    new_text = "\n".join(new_lines)
    if write and new_text != text:
        README.write_text(new_text, encoding="utf-8")
    return new_text == text


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("command", choices=["sync", "check"])
    args = parser.parse_args()

    apps = load_apps()
    errors = validate(apps)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        print(f"\napps.yml is invalid ({len(errors)} problem(s)).", file=sys.stderr)
        return 1

    table = render_table(apps)

    if args.command == "sync":
        in_sync = apply_table(table, write=True)
        status = "already up to date" if in_sync else "updated"
        print(f"apps.yml valid ({len(apps)} apps); README table {status}.")
        return 0

    # check
    in_sync = apply_table(table, write=False)
    if not in_sync:
        print(
            "error: the README Published Apps table is out of sync with apps.yml.\n"
            "       run 'python scripts/apps.py sync' and commit the result.",
            file=sys.stderr,
        )
        return 1
    print(f"apps.yml valid ({len(apps)} apps); README table up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
