# Contributing to Awesome Flet

Thanks for helping improve this list! It's **curated**, so we favor quality over quantity — every entry should be useful to someone building with [Flet](https://flet.dev).

## Quick rules

- **One project per pull request.**
- The project must be genuinely **related to or built with Flet**.
- Put it in the **most specific section**, and keep each list **alphabetically sorted**.
- Write **one short, factual sentence** — capitalized, ending with a period, no marketing language.
- The **link text is the project's name**, and the link is its **GitHub repo** (fall back to the PyPI page only if there is no repo).
- **No duplicates** — check it isn't already listed.

## Entry format

Most sections (Libraries, Apps and Projects, Tools, Learning Resources, Community):

```markdown
- [project-name](https://github.com/owner/repo) - Short description of what it does.
```

**Extensions** — list under *Official* (maintained by the Flet team) or *Community*. If it wraps a Flutter or native package, name that package and link its pub.dev page:

```markdown
- [flet-thing](https://github.com/owner/flet-thing) - What it does. Wraps [`flutter_package`](https://pub.dev/packages/flutter_package).
```

## Published apps

Apps shipped to a public app store live in [`apps.yml`](apps.yml) — the single source of truth that also powers the "Made with Flet" showcase on [flet.dev](https://flet.dev). **Add your entry there**, not directly to the README table.

```yaml
  - name: My App
    tagline: One-line description of what the app does.
    platforms: [android, ios]          # any of: android, ios, web, windows, macos, linux
    stores:
      google_play: https://play.google.com/store/apps/details?id=...
      app_store: https://apps.apple.com/app/...
    source: https://github.com/owner/repo   # optional — only if the app itself is open source
    website: https://example.com            # optional
    tags: [example, tag]                     # optional
```

Then regenerate the README table and commit both files:

```bash
uv run scripts/apps.py sync   # validates apps.yml and rewrites the README table
# (or: pip install pyyaml && python scripts/apps.py sync)
```

Can't run it? No problem — a reviewer will run it on your PR before merging.

Include a **working store link**. Add `source` only if the **app's own code** is public (not just the framework it uses).

## Review

Every pull request is reviewed before merging. For published apps, a reviewer **confirms the app is built with Flet** first. We may ask for a source link or other evidence, and may decline submissions that are unmaintained, broken, duplicated, or out of scope.
