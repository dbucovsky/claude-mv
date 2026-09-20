# claude-mv

Move a project folder together with its Claude Code context (chat sessions, history, file-history, todos, shell snapshots, and debug logs) so nothing gets orphaned under the old path.

Claude Code keys all of this per-project state to the project's absolute folder path. If you rename or relocate a folder with a plain `mv` / drag-and-drop / rename in Explorer, Claude Code treats the new location as a brand-new, contextless project. `claude-mv` keeps the two in sync.

Two implementations are included:

- **`claude-mv.py`** — a Python port that runs natively on Windows (or anywhere Python 3 is installed), with Windows-correct path encoding and no dependency on BSD `sed`.
- **[`ref/claude-mv`](ref/claude-mv)** — the original Bash script, kept for reference (macOS/Linux; also runs under Git Bash/WSL on Windows).

Full usage details, including the `.anchor` location-tracking workflow, are in [doc/wiki/Usage.md](doc/wiki/Usage.md).

## Credits

`ref/claude-mv` is the original Bash/macOS script, written by Chase:
[Rescuing your Claude conversations when you rename projects](https://curiouslychase.com/posts/rescuing-your-claude-conversations-when-you-rename-projects/).
`claude-mv.py` is a Windows-compatible Python port of it, with the `.anchor` tracking feature added on top.

## Quick start

Move a folder and its Claude context in one step:

```
python claude-mv.py "C:\old\path\my-project" "C:\new\path\my-project"
```

If you'd rather move the folder yourself (Explorer, a sync tool, etc.) and just want Claude's context to catch up afterwards, drop an anchor first:

```
cd "C:\old\path\my-project"
python claude-mv.py --anchor
```

...move the folder however you like, then from its new location:

```
cd "C:\new\path\my-project"
python claude-mv.py
```

See [doc/wiki/Usage.md](doc/wiki/Usage.md) for the full command reference.
