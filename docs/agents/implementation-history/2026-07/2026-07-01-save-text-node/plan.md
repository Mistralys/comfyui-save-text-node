# Plan

## Plan Audit Cycles
- Audits: 1 — Plan Auditor v1.5.0
- Architectural Reviews: none — Plan Architect Reviewer v1.6.0

## Summary

Implement a single ComfyUI V3 custom node ("Save Text") that saves a string to a text file in ComfyUI's output directory. The node accepts a multiline string, filename, file extension, counter length, and optional subfolder. It writes the (trimmed) string to disk, passes it through as an output, and displays a preview of the saved content. The project is intentionally minimal — one node, no external dependencies — to maximize long-term stability against ComfyUI API evolution.

## Architectural Context

The `comfyui-save-text-node` repository is a fresh project containing only a LICENSE (MIT), README stub, and the project specification. There is no existing source code.

The companion workspace `comfyui-custom-node-skills` provides comprehensive V3 API documentation and reference implementations in `skill_test_nodes/`. Key reference patterns:

- **V3 node structure**: `io.ComfyNode` + `define_schema()` + `execute()` classmethod pattern ([nodes_basics.py](../../../comfyui-custom-node-skills/skill_test_nodes/nodes_basics.py))
- **V3 registration**: `ComfyExtension` + `comfy_entrypoint()` ([__init__.py](../../../comfyui-custom-node-skills/skill_test_nodes/__init__.py))
- **Data + UI output**: `io.NodeOutput(data, ui=ui.PreviewText(...))` pattern ([nodes_outputs.py](../../../comfyui-custom-node-skills/skill_test_nodes/nodes_outputs.py), `SkillTest_DataPlusUI`)
- **PreviewText**: `ui.PreviewText(value)` for on-node text display ([nodes_outputs.py](../../../comfyui-custom-node-skills/skill_test_nodes/nodes_outputs.py), `SkillTest_PreviewText`)
- **File I/O**: `folder_paths.get_output_directory()` for the output directory, standard Python `open()` for writing
- **Project layout**: `pyproject.toml` + `__init__.py` entry point ([skill_test_nodes/pyproject.toml](../../../comfyui-custom-node-skills/skill_test_nodes/pyproject.toml))

## Approach / Architecture

A single-node project with the standard ComfyUI V3 custom node layout:

```
comfyui-save-text-node/
  __init__.py           # NEW — Extension registration + comfy_entrypoint()
  nodes.py              # NEW — SaveTextNode class
  pyproject.toml        # NEW — Package metadata
  README.md             # EXISTS — Update with usage docs
  LICENSE               # EXISTS — No change
  docs/                 # EXISTS — No change
```

The node class (`SaveTextNode`) will:
1. Accept inputs: text (multiline), filename, extension, counter_length, subfolder (optional).
2. Trim the input text; replace empty strings with a placeholder.
3. Strip leading dots from the extension input.
4. Build the target directory (`output_dir / subfolder`), creating it if needed.
5. Scan the target directory for existing files matching the filename prefix to determine the next counter value (when counter is enabled).
6. Write the text content to the resolved file path.
7. Return the original (trimmed) input text as a passthrough output and display it via `PreviewText`.

The node sets `is_output_node=True` (it has a side effect: writing to disk) and `not_idempotent=True` (must re-execute every run, never cache).

## Rationale

- **V3 API only**: The V1 API is legacy. Using V3 exclusively aligns with the project's goal of longevity.
- **Single file for node logic**: With only one node, splitting into multiple modules adds no value.
- **Folder-scan counter**: Matches `ImageSaveHelper`'s approach — reliable across restarts, no state to persist.
- **`not_idempotent=True`**: The node writes to disk on every execution. Caching would silently skip file writes when inputs haven't changed, which is incorrect for a save node.
- **No external dependencies**: Only uses `folder_paths` (bundled with ComfyUI) and Python stdlib. No `requirements.txt` needed.

## Considered Alternatives

| Decision | Chosen Shape | Alternatives Considered | Trade-Off Summary |
|----------|--------------|-------------------------|-------------------|
| Counter strategy | Folder-scan for highest existing counter | In-memory counter; timestamp suffix | Folder scan survives restarts and matches ComfyUI's built-in image save pattern; in-memory counter would reset and cause overwrites |
| Empty text handling | Replace with `(empty string specified)` | Raise error; skip save; save empty file | Placeholder makes the "empty" state visible in both the file and the preview without blocking the workflow |
| API version | V3 only | V1 only; dual V1+V3 | V3 is the current recommended API; maintaining V1 compat adds complexity for no benefit given the project's longevity goal |
| File layout | `__init__.py` + `nodes.py` | Single-file node | Two files cleanly separates registration boilerplate from node logic; follows the skill_test_nodes reference pattern |

## Pattern Alignment

- **V3 node class structure** (`io.ComfyNode`, `define_schema`, `execute` classmethod): follows `skill_test_nodes/nodes_basics.py` exactly.
- **V3 registration** (`ComfyExtension` + `comfy_entrypoint()`): follows `skill_test_nodes/__init__.py` exactly.
- **Data + UI return** (`io.NodeOutput(data, ui=...)`): follows the `SkillTest_DataPlusUI` pattern in `skill_test_nodes/nodes_outputs.py`.
- **Output directory access** (`folder_paths.get_output_directory()`): follows the manual save pattern in `skill_test_nodes/nodes_outputs.py`.
- **`pyproject.toml` metadata**: follows `skill_test_nodes/pyproject.toml` structure.

No departures from existing patterns.

## Detailed Steps

### 1. Create `pyproject.toml`

Create the package metadata file at the project root with:
- `name`: `comfyui-save-text-node`
- `version`: `1.0.0`
- `license`: `MIT`
- `requires-python`: `>=3.10`
- Repository URL pointing to the GitHub repo

### 2. Create `nodes.py` — SaveTextNode class

Create the node class implementing:

**Schema** (`define_schema`):
- `node_id`: `"SaveText"` (globally unique identifier)
- `display_name`: `"Save Text"`
- `category`: `"utils"`
- `description`: `"Saves a string to a text file in the output directory."`
- `is_output_node`: `True`
- `not_idempotent`: `True`
- Inputs:
  - `io.String.Input("text", multiline=True, default="")` — the text to save
  - `io.String.Input("filename", default="output")` — base filename (no extension)
  - `io.String.Input("extension", default="txt")` — file extension
  - `io.Int.Input("counter_length", default=5, min=0, max=10, step=1)` — zero-padded counter digit count; `0` disables
  - `io.String.Input("subfolder", default="", optional=True)` — optional subdirectory under output
- Outputs:
  - `io.String.Output("TEXT")` — passthrough of the (trimmed) input text

**Execute** (`execute`):
1. Trim the input text (`text.strip()`).
2. If trimmed text is empty, replace with `"(empty string specified)"`.
3. Strip leading dots from the extension (`extension.lstrip(".")`).
4. Get the output directory via `folder_paths.get_output_directory()`.
5. If subfolder is provided and non-empty (after stripping), join it to the output directory and create it with `os.makedirs(exist_ok=True)`.
6. **Counter logic** (when `counter_length > 0`):
   - Scan the target directory for files matching the pattern `{filename}_{counter}.{extension}`.
   - Parse the counter values from matching filenames.
   - Set the next counter to `max(existing) + 1`, or `1` if no matches.
   - Format the full filename: `{filename}_{counter:0{counter_length}d}.{extension}`.
7. **No counter** (when `counter_length == 0`):
   - Format the full filename: `{filename}.{extension}`.
8. Write the text content to the resolved path using `open(filepath, "w", encoding="utf-8")`.
9. Return `io.NodeOutput(text, ui=ui.PreviewText(text))` — passing through the trimmed text (or placeholder) and displaying it as a preview.

### 3. Create `__init__.py` — Extension registration

Create the entry point file:
- Import `SaveTextNode` from `.nodes`.
- Define `SaveTextExtension(ComfyExtension)` with `async def get_node_list(self)` returning `[SaveTextNode]`.
- Define `async def comfy_entrypoint()` returning a new `SaveTextExtension()` instance.

### 4. Update `README.md`

Expand the README stub with:
- Project description (from the problem statement).
- Installation instructions (clone into `custom_nodes/`).
- Node inputs/outputs reference table.
- Usage example (brief workflow description).
- License reference.

## Dependencies

- No external Python dependencies. Only uses:
  - `folder_paths` (bundled with ComfyUI)
  - `os`, `re` (Python stdlib)
  - `comfy_api.latest` (ComfyUI V3 API)

## Required Components

- `pyproject.toml` — **NEW** — package metadata
- `nodes.py` — **NEW** — `SaveTextNode` class
- `__init__.py` — **NEW** — extension registration and entry point
- `README.md` — **EXISTS** — update with documentation

## Assumptions

- ComfyUI is running a version that supports the V3 API (`comfy_api.latest`, `io.ComfyNode`, `ComfyExtension`, `comfy_entrypoint()`).
- `folder_paths.get_output_directory()` is available and returns a writable path.
- `ui.PreviewText` is available in `comfy_api.latest`.
- The node will be installed by cloning into `ComfyUI/custom_nodes/`.

## Constraints

- Single node only — no multi-node expansion.
- No external dependencies — stdlib and ComfyUI builtins only.
- V3 API only — no V1 fallback.
- Files are always written to the ComfyUI output directory (no arbitrary path support).
- UTF-8 encoding only.

## Out of Scope

- Appending to existing files (always creates new files or overwrites when counter is disabled).
- Reading files back from disk.
- Binary file output.
- Custom encoding selection (hardcoded UTF-8).
- Integration with ComfyUI's metadata/workflow embedding system.
- Frontend JavaScript extensions.
- Internationalization / locales.

## Acceptance Criteria

- The node appears in ComfyUI's node menu under the `utils` category as "Save Text".
- Connecting a multiline string and running the workflow writes a text file to the output directory.
- The filename, extension, counter, and subfolder inputs correctly control the output path.
- When counter_length > 0, successive executions produce incrementing filenames (e.g., `output_00001.txt`, `output_00002.txt`).
- When counter_length is 0, the file is written as `{filename}.{extension}` (overwriting if it exists).
- Empty input text produces a file containing `(empty string specified)`.
- The input text is trimmed (leading/trailing whitespace removed).
- The extension input accepts both `txt` and `.txt` notation.
- The output string passes through the (trimmed) input text to downstream nodes.
- A text preview is displayed on the node in the UI.
- The node re-executes every run (no caching).
- The subfolder is created automatically if it doesn't exist.

## Testing Strategy

Testing is manual in the ComfyUI environment since the node interacts with ComfyUI's runtime (`folder_paths`, `comfy_api.latest`). The test plan below describes the manual verification steps to cover all acceptance criteria.

## Test Plan

- **Manual: Basic save** — Connect a multiline string, run workflow, verify file appears in output directory with correct content. Covers: basic file writing, multiline support.
- **Manual: Filename and extension** — Set filename to `"myfile"` and extension to `"md"`, verify output is `myfile_00001.md`. Covers: filename/extension inputs.
- **Manual: Counter increment** — Run the workflow 3 times, verify files are `output_00001.txt`, `output_00002.txt`, `output_00003.txt`. Covers: counter scan and increment.
- **Manual: Counter disabled** — Set counter_length to `0`, run twice, verify file is `output.txt` and is overwritten. Covers: counter disable, overwrite behavior.
- **Manual: Subfolder** — Set subfolder to `"test_sub"`, run workflow, verify file is created under `output/test_sub/` and the directory was created. Covers: subfolder creation.
- **Manual: Empty text** — Leave text input empty, run workflow, verify file contains `(empty string specified)`. Covers: empty text handling.
- **Manual: Trimming** — Input text with leading/trailing whitespace, verify file content is trimmed. Covers: string trimming.
- **Manual: Extension dot stripping** — Set extension to `".txt"`, verify output file has `.txt` extension (not `..txt`). Covers: dot-stripping logic.
- **Manual: Passthrough output** — Connect the output string to another node (e.g., a second Save Text), verify the text passes through correctly. Covers: output passthrough.
- **Manual: Preview display** — Run workflow, verify the node displays the saved text content in the UI. Covers: PreviewText UI.
- **Manual: No caching** — Run the same workflow twice without changing inputs, verify both runs create files (counter increments). Covers: not_idempotent behavior.

## Documentation Updates

- `README.md` — Expand with project description, installation instructions, node reference table, usage example, and license section.
- `docs/agents/project-manifest/file-tree.md` — Remove `<!-- TODO: create -->` markers from `__init__.py`, `nodes.py`, and `pyproject.toml`.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| **`ui.PreviewText` API changes or is removed** | `PreviewText` is a simple UI helper; if removed, the node can fall back to returning `io.NodeOutput(text)` without the preview — core save functionality is unaffected. |
| **`folder_paths` API changes** | `folder_paths.get_output_directory()` is a foundational ComfyUI utility used by all save nodes; unlikely to be removed without a migration path. |
| **Filename collision in counter-disabled mode** | Documented behavior: counter_length=0 overwrites. This is intentional and expected. |
| **Filesystem permission errors** | ComfyUI's output directory is already writable (required for image saves). If permissions are wrong, the error will surface naturally via Python's `OSError`. |
| **Concurrent execution race condition on counter scan** | Low risk in typical ComfyUI usage (single-user, sequential execution). The folder-scan approach matches the built-in `ImageSaveHelper` pattern, which has the same characteristic. |
