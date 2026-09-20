# Usage

`claude-mv.py` supports three modes: an explicit two-argument move, an `--anchor` write, and a no-argument anchor sync, plus `--version` and `--help`. `ref/claude-mv` (the original Bash script, kept for reference) supports only the two-argument move, and requires Git Bash or WSL on Windows.

## 1. Explicit move: `claude-mv.py <old_directory> <new_directory>`

Moves `<old_directory>` to `<new_directory>` on disk and relocates all matching Claude Code context:

```
python claude-mv.py "C:\old\path\my-project" "C:\new\path\my-project"
```

What it does, in order:

1. Resolves `<old_directory>` to an absolute path; errors if it doesn't exist.
2. Errors if `<new_directory>` already exists.
3. Computes the Windows-encoded project-folder name for both paths (every non-alphanumeric character — `:`, `\`, spaces, `.` — becomes `-`, matching Claude Code's own naming scheme).
4. If Claude context already exists at the destination, prompts:
   - `[c]` clean out the existing destination context and continue
   - `[m]` merge the old context into the existing destination context
   - `[n]` abort (default)
5. Moves/merges each of `projects`, `file-history`, `todos`, `shell-snapshots`, and `debug` under `~/.claude/` from the old encoded name to the new one.
6. Rewrites the moved session `.jsonl` files so any embedded old-path references point at the new path (handles both raw and JSON-escaped path forms).
7. Moves the actual directory on disk.
8. Updates `~/.claude/history.jsonl` to reference the new path, keeping a `.backup` copy first.
9. If the moved folder contains a `.anchor` file (see below), appends the new location to it.

## 2. Recording an anchor: `claude-mv.py --anchor`

Writes the current folder's absolute path into a `.anchor` file inside it:

```
cd "C:\old\path\my-project"
python claude-mv.py --anchor
```

Use this before moving a folder by any means *other* than `claude-mv.py` itself — Explorer drag-and-drop, a sync tool, `mv`, a rename, etc. Because `.anchor` lives inside the folder, it travels along with it.

## 3. Syncing after an anchored move: `claude-mv.py` (no arguments)

Run this from the folder's *new* location after moving it:

```
cd "C:\new\path\my-project"
python claude-mv.py
```

It reads the last recorded location from `.anchor` as the old path and treats the current working directory as the new path, then runs the same context-relocation steps as the explicit move (steps 3–6 and 8 above) — but does **not** move any files, since the folder is already where it needs to be. On success it appends the new location to `.anchor`.

If `.anchor` doesn't exist in the current folder, this errors and tells you to run `--anchor` first. If the current folder already matches the last recorded anchor entry (nothing moved), it prints a message and exits without changes.

## The `.anchor` file format

Plain text, one entry per line, appended (never overwritten) so it doubles as a location history:

```
2026-09-20T11-50-22:C:\Users\damia\projects\my-project
2026-09-20T14-05-41:D:\Projects\my-project
```

- Each line is `<timestamp>:<absolute path>`.
- The timestamp uses `-` instead of `:` in the time portion (`HH-MM-SS`) specifically so the line can be split on the *first* colon to separate the timestamp from a Windows path — otherwise the path's own drive-letter colon (`C:`) would be ambiguous.
- The **last line** is always the current/most recent known location.

## 4. Version and help

```
python claude-mv.py --version   # prints e.g. "claude-mv.py 1.1.2"
python claude-mv.py --help      # prints the usage summary
```

## Notes

- `claude-mv.py` requires no third-party packages — just Python 3.
- The original `ref/claude-mv` Bash script only replaces `/` and `.` when encoding paths, which is correct for macOS/Linux but not for Windows paths (which also need `:`, `\`, and spaces encoded). Use `claude-mv.py` on Windows.

## Credits

`ref/claude-mv` is the original script, written for macOS/Linux by Chase:
[Rescuing your Claude conversations when you rename projects](https://curiouslychase.com/posts/rescuing-your-claude-conversations-when-you-rename-projects/).
`claude-mv.py` is a Windows-compatible Python port, with the `.anchor` tracking feature (this wiki's [[Home]] page) added on top.
