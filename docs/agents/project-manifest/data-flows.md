# Key Data Flows

> **Status:** Implemented — `nodes.py` at project root.

## Save Text Execution Flow

The node has a single execution path triggered by ComfyUI's workflow engine.

```
ComfyUI Engine
  → SaveTextNode.execute(text, filename, extension, counter_length, subfolder)
    → text.strip()
    → if empty: replace with "(empty string specified)"
    → extension.lstrip(".")
    → if extension is now empty: default to "txt"
    → filename = os.path.basename(filename)  # strip any directory separators
    → subfolder = subfolder.strip()
    → folder_paths.get_output_directory() → base output path
    → if subfolder: validate boundary, then os.makedirs(output_dir / subfolder, exist_ok=True)
    → if counter_length > 0:
        scan target dir for {filename}_{counter}.{extension} pattern
        → next counter = max(existing) + 1 (or 1 if none)
        → full filename = {filename}_{counter:0Nd}.{extension}
    → else:
        → full filename = {filename}.{extension}
    → open(filepath, "w", encoding="utf-8").write(text)
    → return io.NodeOutput(text, ui=ui.PreviewText(text))
      → text passes through to downstream nodes
      → PreviewText renders saved content on the node in the UI
```

There are no other data flows. The node has no state, no background processes, and no inter-node communication beyond the standard output passthrough.
