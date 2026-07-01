# Constraints & Conventions

## Non-Negotiable Design Decisions

These are documented in the [plan](../plans/2026-07-01-save-text-node/plan.md) and require explicit user approval to change.

- **V3 API only** — no V1 compatibility layer.
- **Single node** — no multi-node expansion.
- **No external dependencies** — stdlib and ComfyUI builtins only.
- **UTF-8 encoding only** — no encoding selection.
- **Output directory only** — no arbitrary file path support.

## Node Behavior Rules

- **`not_idempotent=True`** — the node must re-execute every run, never cache. This is required because the node writes to disk.
- **`is_output_node=True`** — marks the node as having side effects (file I/O).
- **Empty text handling** — when the trimmed input is empty, save `(empty string specified)` instead. Do not raise an error or skip the save.
- **String trimming** — input text is always trimmed (`strip()`) before saving.
- **Extension dot stripping** — leading dots are stripped from the extension input (`lstrip(".")`), so both `txt` and `.txt` are accepted.
- **Counter disabled at 0** — when `counter_length` is `0`, the file is written as `{filename}.{extension}` and overwrites on repeated runs.

## Counter Convention

The counter follows ComfyUI's `ImageSaveHelper` pattern:

- Scan the target directory for files matching `{filename}_{counter}.{extension}`.
- Next counter = `max(existing) + 1`, or `1` if no matches.
- Counter is zero-padded to `counter_length` digits.
- Separator character is `_`.

## File I/O

- All writes go through Python's `open(path, "w", encoding="utf-8")`.
- Subfolders are created with `os.makedirs(exist_ok=True)`.
- The output base directory is resolved via `folder_paths.get_output_directory()`.

## Project Conventions

- **Two-file layout**: `__init__.py` (registration) + `nodes.py` (node logic). No further module splitting.
- **Reference patterns**: Follow `skill_test_nodes/` in the companion workspace for V3 API usage.
- **Manual testing only**: No automated test suite. Node is tested manually in ComfyUI.
