# ComfyUI Save Text Node

A minimal, single-purpose ComfyUI V3 custom node that saves a string to a text file in ComfyUI's output directory. One node, one job — designed to keep working as ComfyUI evolves.

## Features

- Saves any string (multiline or single-line) to a text file in the output directory.
- Auto-increments a numeric counter in the filename to avoid overwrites — configurable digit length, or disable entirely for fixed filenames that overwrite on each run.
- Optional subfolder under the output directory — created automatically if it does not exist.
- Accepts `.txt` and `txt` notation interchangeably for the extension.
- Empty or whitespace-only input is written as `(empty string specified)` rather than producing an empty file.
- Always writes fresh output — never uses cached results from previous runs.
- Passes the saved text through as an output and displays it in a preview area on the node.

## Requirements

- ComfyUI with V3 API support (`comfy_api.latest`)
- Python 3.10+

## Quick Start

Clone the repository into ComfyUI's `custom_nodes` directory:

```bash
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/Mistralys/comfyui-save-text-node.git
```

Restart ComfyUI. The node appears under the **utils** category as **Save Text**.

Connect any string-producing node's output to the `text` input. Configure the inputs below, then run the workflow. The file is written to ComfyUI's output directory on each run — for example `output/output_00001.txt` — with the counter incrementing automatically. The saved text is also passed through as an output and shown in a preview area on the canvas.

| Input | Default | Description |
|-------|---------|-------------|
| `text` | `""` | The string to save. Trimmed before use. |
| `filename` | `"output"` | Base filename without extension. |
| `extension` | `"txt"` | File extension. Leading dots are stripped (`.txt` and `txt` both work). |
| `counter_length` | `5` | Zero-padded counter digit length. Set to `0` to disable — file is overwritten on each run. |
| `subfolder` | `""` | Optional subdirectory under ComfyUI's output folder. Created automatically if absent. |

## Security

The `subfolder` and `filename` inputs are actively validated against path-traversal attacks. `os.path.realpath()` ensures the resolved path stays within ComfyUI's output directory, and `os.path.basename()` strips directory separators from the filename unconditionally. Any path that escapes the output directory raises a `ValueError`.

If you expose ComfyUI to a network, additional hardening at the ComfyUI or reverse-proxy level is recommended. See the [ComfyUI documentation](https://docs.comfy.org/) for guidance.

## Learn More

| Resource | Description |
|----------|-------------|
| [API Surface](docs/agents/project-manifest/api-surface.md) | Full node schema and method signatures |
| [Constraints & Conventions](docs/agents/project-manifest/constraints.md) | Design rules, counter behavior, and security invariants |
| [Changelog](changelog.md) | Version history |
| [License](LICENSE) | MIT license |
