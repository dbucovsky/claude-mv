# Changelog

All notable changes to the `claude-mv` scripts are documented here.

## V1.1.2 — 2026-09-20 12:40
### Changes
- Set GitHub's default branch to `main` (was `win-ver`); `main` is pushed with its single empty initial commit, `win-ver` remains the active branch to be merged back into `main`.
- Added `.github/workflows/wiki-sync.yml`, which auto-syncs `doc/wiki/` to the repo's GitHub Wiki on every push to `main` touching `doc/wiki/**` (plus manual `workflow_dispatch`).

## V1.1.1 — 2026-09-20 12:05
### Changes
- Moved the original Bash script to `ref/claude-mv` and credited its author, Chase — [Rescuing your Claude conversations when you rename projects](https://curiouslychase.com/posts/rescuing-your-claude-conversations-when-you-rename-projects/) — in `README.md`, `doc/wiki/Usage.md`, and both scripts' headers.

## V1.1.0 — 2026-09-20 11:52
### Changes
- Added `.anchor` file tracking: `claude-mv.py --anchor` records the current folder's absolute path with a timestamp.
- Added no-argument mode: running `claude-mv.py` with no parameters reads the last recorded location from `.anchor` in the current folder as the old path, treats the current folder as the new path, and re-syncs the Claude Code context without physically moving anything.
- Explicit two-argument moves now also append to `.anchor` after a successful move, if the folder already has one, so location history stays current regardless of which mode is used.

### Known bugs (not yet fixed)
- None currently identified.

### Planned (not yet implemented)
- None currently planned.

## V1.0.0 — 2026-09-20 11:30
### Changes
- Ported `claude-mv` from a Bash/macOS script to a cross-platform Python script (`claude-mv.py`) that runs natively on Windows.
- Fixed path encoding to match Claude Code's actual Windows project-folder naming (every non-alphanumeric character becomes `-`, not just `/` and `.` as the original Bash script assumed).
- Replaced the BSD-only `sed -i ''` calls (which silently fail under GNU sed on Git Bash/WSL) with direct Python text substitution, handling both raw and JSON-escaped path forms in session `.jsonl` files.
