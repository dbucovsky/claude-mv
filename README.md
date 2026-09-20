# claude-mv

Move a project folder together with its Claude Code context (chat sessions, history, file-history, todos, shell snapshots, and debug logs) so nothing gets orphaned under the old path.

Claude Code keys all of this per-project state to the project's absolute folder path. If you rename or relocate a folder with a plain `mv` / drag-and-drop / rename in Explorer, Claude Code treats the new location as a brand-new, contextless project. `claude-mv` keeps the two in sync.

Two implementations are included:

- **`claude-mv`** — the original Bash script, for macOS/Linux (also runs under Git Bash/WSL on Windows).
- **`claude-mv.py`** — a Python port that runs natively on Windows (or anywhere Python 3 is installed), with Windows-correct path encoding and no dependency on BSD `sed`.

See [doc/wiki/Usage.md](doc/wiki/Usage.md) for full usage, including the `.anchor` location-tracking feature.

## Quick start

Move a folder and its Claude context in one step:

```
python claude-mv.py "C:\old\path\my-project" "C:\new\path\my-project"
```

If you'd rather move the folder yourself (Explorer, `mv`, a sync tool, etc.) and just want Claude's context to catch up afterwards, use an anchor instead — see the usage doc.
