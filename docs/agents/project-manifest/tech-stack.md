# Tech Stack & Patterns

## Runtime

| Property | Value |
|---|---|
| Language | Python 3.10+ |
| Host Platform | ComfyUI (custom node) |
| API | ComfyUI V3 (`comfy_api.latest`) — no V1 fallback |

## Dependencies

| Dependency | Source | Purpose |
|---|---|---|
| `comfy_api.latest` | ComfyUI built-in | V3 node API (`io`, `ui`, `ComfyNode`, `ComfyExtension`) |
| `folder_paths` | ComfyUI built-in | Resolve output directory path |
| `os` | Python stdlib | Path manipulation, directory creation |
| `re` | Python stdlib | Filename pattern matching for counter scan |

No external (pip) dependencies.

## Architecture

Single custom node registered as a ComfyUI V3 extension.

| Pattern | Description |
|---|---|
| V3 Node class | `io.ComfyNode` subclass with `define_schema()` + `execute()` classmethods |
| V3 Registration | `ComfyExtension` subclass + module-level `comfy_entrypoint()` |
| Data + UI output | `io.NodeOutput(data, ui=ui.PreviewText(...))` for passthrough + on-node preview |
| Folder-scan counter | Scan target directory for existing files to determine next counter value |

## Build & Packaging

| Property | Value |
|---|---|
| Package manager | pip (installed via ComfyUI `custom_nodes/`) |
| Build tool | None (pure Python) |
| Package metadata | `pyproject.toml` |
| Test framework | Manual testing in ComfyUI |
