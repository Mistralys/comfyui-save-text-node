# Public API Surface

> **Status:** Implemented — `nodes.py` at project root.

## `nodes.py` — SaveTextNode

ComfyUI V3 node class (`io.ComfyNode` subclass).

### Schema (`define_schema`)

| Property | Value |
|---|---|
| `node_id` | `"SaveText"` |
| `display_name` | `"Save Text"` |
| `description` | `"Saves a string to a text file in the output directory."` |
| `category` | `"utils"` |
| `is_output_node` | `True` |
| `not_idempotent` | `True` |

#### Inputs

| Name | Type | Default | Notes | Tooltip |
|---|---|---|---|---|
| `text` | `io.String` | `""` | `multiline=True` | "The text content to save. Trimmed of leading and trailing whitespace. An empty or whitespace-only value is written as '(empty string specified)'." |
| `filename` | `io.String` | `"output"` | Base filename, no extension | "Base name of the output file, without the extension. Directory separators are stripped automatically to prevent path traversal." |
| `extension` | `io.String` | `"txt"` | Leading dots stripped automatically | "File extension for the saved file (e.g. txt, md, csv). Leading dots are stripped, so both 'txt' and '.txt' are accepted." |
| `counter_length` | `io.Int` | `5` | `min=0, max=10`; `0` disables counter | "Number of digits in the auto-incrementing counter appended to the filename (e.g. output_00001.txt). Set to 0 to disable — the file is overwritten on each run." |
| `subfolder` | `io.String` | `""` | `optional=True`; subdirectory under output | "Optional subdirectory inside ComfyUI's output directory. Created automatically if absent. Must resolve inside the output directory. Leave empty to save to the root output folder." |

> `subfolder` and `filename` are validated with `os.path.realpath()` boundary check and `os.path.basename()` sanitization respectively. Paths resolving outside the output directory raise `ValueError`.

#### Outputs

| Name | Type | Notes | Tooltip |
|---|---|---|---|
| `TEXT` | `io.String` | Passthrough of trimmed input text | "Passthrough of the saved text, trimmed of leading and trailing whitespace. Identical to the value written to disk." |

#### UI

`ui.PreviewText(text)` — displays saved content on the node.

### Methods

```
@classmethod
define_schema(cls) -> io.Schema

@classmethod
execute(cls, text, filename, extension, counter_length, subfolder) -> io.NodeOutput
```

## `__init__.py` — Extension Registration

### Classes

```
class SaveTextExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]
```

### Module-level Functions

```
async def comfy_entrypoint() -> SaveTextExtension
```
