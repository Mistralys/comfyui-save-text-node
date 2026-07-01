# Public API Surface

> **Status:** Planned — source code not yet implemented.
> Signatures below are derived from the [implementation plan](../plans/2026-07-01-save-text-node/plan.md).

## `nodes.py` — SaveTextNode

ComfyUI V3 node class (`io.ComfyNode` subclass).

### Schema (`define_schema`)

| Property | Value |
|---|---|
| `node_id` | `"SaveText"` |
| `display_name` | `"Save Text"` |
| `category` | `"utils"` |
| `is_output_node` | `True` |
| `not_idempotent` | `True` |

#### Inputs

| Name | Type | Default | Notes |
|---|---|---|---|
| `text` | `io.String` | `""` | `multiline=True` |
| `filename` | `io.String` | `"output"` | Base filename, no extension |
| `extension` | `io.String` | `"txt"` | Leading dots stripped automatically |
| `counter_length` | `io.Int` | `5` | `min=0, max=10`; `0` disables counter |
| `subfolder` | `io.String` | `""` | `optional=True`; subdirectory under output |

#### Outputs

| Name | Type | Notes |
|---|---|---|
| `TEXT` | `io.String` | Passthrough of trimmed input text |

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
    get_node_list(cls) -> list[type[io.ComfyNode]]
```

### Module-level Functions

```
comfy_entrypoint() -> ComfyExtension
```
