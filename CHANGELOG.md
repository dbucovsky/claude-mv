# Changelog

All notable changes to the `claude-mv` scripts are documented here.

## V1.0.0 — 2026-09-20 11:30
### Changes
- Ported `claude-mv` from a Bash/macOS script to a cross-platform Python script (`claude-mv.py`) that runs natively on Windows.
- Fixed path encoding to match Claude Code's actual Windows project-folder naming (every non-alphanumeric character becomes `-`, not just `/` and `.` as the original Bash script assumed).
- Replaced the BSD-only `sed -i ''` calls (which silently fail under GNU sed on Git Bash/WSL) with direct Python text substitution, handling both raw and JSON-escaped path forms in session `.jsonl` files.
