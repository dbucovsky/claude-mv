#!/usr/bin/env python3
"""Move a project directory together with its Claude Code context
(sessions, history, file-history, todos, shell-snapshots, debug).

Usage:
    claude-mv.py <old_directory> <new_directory>
        Move <old_directory> to <new_directory> and relocate its Claude context.

    claude-mv.py --anchor
        Record the current folder's absolute path in a .anchor file inside it.
        The .anchor file travels with the folder on an ordinary OS-level move
        (drag-and-drop, `mv`, rename, etc).

    claude-mv.py
        No arguments: assume the current folder is the NEW location and the
        last entry in its .anchor file is the OLD location, then relocate the
        Claude context to match (without moving any files, since the folder
        is already where it needs to be). Appends the new location to .anchor.
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

CONTEXT_SUBDIRS = ["projects", "file-history", "todos", "shell-snapshots", "debug"]
ANCHOR_FILENAME = ".anchor"
TIMESTAMP_FMT = "%Y-%m-%dT%H-%M-%S"  # no colons, so "timestamp:location" splits unambiguously


def encode_path(path: str) -> str:
    """Match Claude Code's project-folder naming: every non-alphanumeric
    character (':', '\\', '/', '.', spaces, ...) becomes '-'."""
    return re.sub(r"[^A-Za-z0-9]", "-", path)


def die(message: str, code: int = 1):
    print(message)
    sys.exit(code)


def merge_dir(src: Path, dst: Path):
    for item in src.iterdir():
        target = dst / item.name
        if target.exists():
            if item.is_dir() and target.is_dir():
                merge_dir(item, target)
                item.rmdir()
            else:
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
                shutil.move(str(item), str(target))
        else:
            shutil.move(str(item), str(target))
    try:
        src.rmdir()
    except OSError:
        shutil.rmtree(src, ignore_errors=True)


def replace_in_file(path: Path, old: str, new: str):
    old_escaped = old.replace("\\", "\\\\")
    new_escaped = new.replace("\\", "\\\\")
    text = path.read_text(encoding="utf-8")
    updated = text.replace(old_escaped, new_escaped).replace(old, new)
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def update_history(claude_dir: Path, old_abs: str, new_abs: str):
    history_file = claude_dir / "history.jsonl"
    if history_file.is_file():
        print("Updating history.jsonl references...")
        backup_file = history_file.with_suffix(history_file.suffix + ".backup")
        shutil.copy2(history_file, backup_file)
        replace_in_file(history_file, old_abs, new_abs)
        print(f"Updated history.jsonl (backup: {backup_file.name})")


def anchor_path_for(directory: Path) -> Path:
    return directory / ANCHOR_FILENAME


def append_anchor_entry(directory: Path, location: str):
    anchor_file = anchor_path_for(directory)
    timestamp = datetime.now().strftime(TIMESTAMP_FMT)
    with anchor_file.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp}:{location}\n")


def read_last_anchor_location(directory: Path) -> str:
    anchor_file = anchor_path_for(directory)
    if not anchor_file.is_file():
        die(
            f"Error: No {ANCHOR_FILENAME} file found in current directory.\n"
            f"Run 'python claude-mv.py --anchor' here first, before moving it."
        )
    lines = [line.strip() for line in anchor_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        die(f"Error: {ANCHOR_FILENAME} file is empty.")
    last_line = lines[-1]
    if ":" not in last_line:
        die(f"Error: Malformed line in {ANCHOR_FILENAME}: {last_line}")
    _, location = last_line.split(":", 1)
    return location


def sync_anchor_if_present(new_dir: Path, new_abs: str):
    if anchor_path_for(new_dir).is_file():
        append_anchor_entry(new_dir, new_abs)
        print(f"Anchor updated: {new_abs}")


def relocate_claude_context(old_abs: str, new_abs_future: str, claude_dir: Path) -> int:
    old_encoded = encode_path(old_abs)
    new_encoded = encode_path(new_abs_future)

    # Check if destination Claude context already exists BEFORE moving anything
    existing_context = []
    for subdir in CONTEXT_SUBDIRS:
        if (claude_dir / subdir / new_encoded).exists():
            existing_context.append(subdir)

    if existing_context:
        print(f"Warning: Claude context already exists for {new_abs_future}:")
        for item in existing_context:
            count_str = ""
            if item == "projects":
                proj_dir = claude_dir / "projects" / new_encoded
                if proj_dir.is_dir():
                    session_count = len(list(proj_dir.glob("*.jsonl")))
                    count_str = f" ({session_count} sessions)"
            print(f"  - {item}{count_str}")
        print()
        print("Options:")
        print("  [c] Clean out existing context and continue")
        print("  [m] Merge old context into existing context")
        print("  [n] Abort (default)")
        print()
        choice = input("Choose [c/m/N]: ").strip().lower()

        if choice == "c":
            print(f"Cleaning out existing context for {new_abs_future}...")
            for item in existing_context:
                target = claude_dir / item / new_encoded
                if target.is_dir():
                    shutil.rmtree(target)
                elif target.exists():
                    target.unlink()
                print(f"  Removed {item}")
            print()
        elif choice == "m":
            print("Will merge contexts...")
        else:
            print("Aborted.")
            sys.exit(1)

    print("Moving Claude context from:")
    print(f"  {old_abs}")
    print(f"  -> {new_abs_future}")
    print()

    moved = 0
    for subdir in CONTEXT_SUBDIRS:
        old_ctx = claude_dir / subdir / old_encoded
        new_ctx = claude_dir / subdir / new_encoded

        if old_ctx.is_dir():
            new_ctx.parent.mkdir(parents=True, exist_ok=True)
            if new_ctx.is_dir():
                print(f"Merging {subdir}/{old_encoded} -> {subdir}/{new_encoded}")
                merge_dir(old_ctx, new_ctx)
            else:
                print(f"Moving {subdir}/{old_encoded} -> {subdir}/{new_encoded}")
                shutil.move(str(old_ctx), str(new_ctx))
            moved += 1
        elif old_ctx.is_file():
            new_ctx.parent.mkdir(parents=True, exist_ok=True)
            print(f"Moving {subdir}/{old_encoded} -> {subdir}/{new_encoded}")
            if new_ctx.exists():
                new_ctx.unlink()
            shutil.move(str(old_ctx), str(new_ctx))
            moved += 1

    if moved == 0:
        print(f"No Claude context found for {old_abs}")
    else:
        print(f"Moved {moved} context location(s)")
    print()

    # Update session file contents to reference the new path
    projects_new = claude_dir / "projects" / new_encoded
    if projects_new.is_dir():
        session_files = list(projects_new.glob("*.jsonl"))
        if session_files:
            print("Updating session file references...")
            for f in session_files:
                replace_in_file(f, old_abs, new_abs_future)
            print("Updated session files")
            print()

    return moved


def run_write_anchor():
    cwd = Path.cwd().resolve()
    new_abs = str(cwd)
    append_anchor_entry(cwd, new_abs)
    print(f"Anchor written to {anchor_path_for(cwd)}")
    print(f"  {new_abs}")


def run_anchor_sync():
    cwd = Path.cwd().resolve()
    new_abs = str(cwd)
    old_abs = read_last_anchor_location(cwd)

    if old_abs == new_abs:
        print("Current location matches the last recorded anchor; nothing to do.")
        return

    claude_dir = Path.home() / ".claude"
    print("Detected move via anchor:")
    print(f"  {old_abs}")
    print(f"  -> {new_abs}")
    print()

    relocate_claude_context(old_abs, new_abs, claude_dir)
    update_history(claude_dir, old_abs, new_abs)

    append_anchor_entry(cwd, new_abs)
    print(f"Anchor updated: {new_abs}")


def run_explicit_move(old_dir_arg: str, new_dir_arg: str):
    old_path = Path(old_dir_arg)
    if not old_path.is_dir():
        die(f"Error: Old directory does not exist: {old_dir_arg}")
    old_abs = str(old_path.resolve())

    new_path = Path(new_dir_arg)
    if new_path.exists():
        die(f"Error: New directory already exists: {new_dir_arg}")

    # Figure out what the new absolute path will be once moved
    if new_path.is_absolute():
        new_abs_future = str(new_path)
    else:
        parent = new_path.parent
        if str(parent) == ".":
            new_abs_future = str(Path.cwd() / new_path.name)
        else:
            if not parent.is_dir():
                die(f"Error: Parent directory does not exist: {parent}")
            new_abs_future = str(parent.resolve() / new_path.name)

    claude_dir = Path.home() / ".claude"

    relocate_claude_context(old_abs, new_abs_future, claude_dir)

    # Move the actual directory AFTER Claude context is moved
    print("Moving directory:")
    print(f"  {old_abs}")
    print(f"  -> {new_dir_arg}")
    try:
        shutil.move(old_abs, str(new_path))
    except OSError as e:
        die(f"Error moving directory: {e}")

    new_abs = str(new_path.resolve())
    print("Directory moved")
    print()

    update_history(claude_dir, old_abs, new_abs)

    # If the moved folder carries a .anchor file, keep its history current
    sync_anchor_if_present(Path(new_abs), new_abs)


def print_usage():
    print("Usage:")
    print("  claude-mv.py <old_directory> <new_directory>   Move a directory and its Claude context")
    print("  claude-mv.py --anchor                          Record this folder's path in .anchor")
    print("  claude-mv.py                                   Sync Claude context after moving the anchored folder")


def main():
    args = sys.argv[1:]

    if len(args) == 0:
        run_anchor_sync()
    elif len(args) == 1 and args[0] in ("--anchor", "anchor"):
        run_write_anchor()
    elif len(args) == 2:
        run_explicit_move(args[0], args[1])
    else:
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
