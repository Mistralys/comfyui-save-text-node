"""Contains SaveTextNode, a ComfyUI V3 custom node that saves a string to a text file
in the output directory."""

import os
import re
import folder_paths
from comfy_api.latest import io, ui


class SaveTextNode(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="SaveText",
            display_name="Save Text",
            category="utils",
            description="Saves a string to a text file in the output directory.",
            is_output_node=True,
            not_idempotent=True,
            inputs=[
                io.String.Input("text", multiline=True, default="",
                    tooltip="The text content to save. Trimmed of leading and trailing whitespace. An empty or whitespace-only value is written as '(empty string specified)'."),
                io.String.Input("filename", default="output",
                    tooltip="Base name of the output file, without the extension. Directory separators are stripped automatically to prevent path traversal."),
                io.String.Input("extension", default="txt",
                    tooltip="File extension for the saved file (e.g. txt, md, csv). Leading dots are stripped, so both 'txt' and '.txt' are accepted."),
                io.Int.Input("counter_length", default=5, min=0, max=10, step=1,
                    tooltip="Number of digits in the auto-incrementing counter appended to the filename (e.g. output_00001.txt). Set to 0 to disable — the file is overwritten on each run."),
                io.String.Input("subfolder", default="", optional=True,
                    tooltip="Optional subdirectory inside ComfyUI's output directory. Created automatically if absent. Must resolve inside the output directory. Leave empty to save to the root output folder."),
            ],
            outputs=[
                io.String.Output("TEXT",
                    tooltip="Passthrough of the saved text, trimmed of leading and trailing whitespace. Identical to the value written to disk."),
            ],
        )

    @classmethod
    def execute(cls, text, filename, extension, counter_length, subfolder=""):
        # Normalize text
        text = text.strip()
        if not text:
            text = "(empty string specified)"

        # Normalize extension
        extension = extension.lstrip(".")
        if not extension:
            extension = "txt"

        # Sanitize filename to prevent path traversal
        filename = os.path.basename(filename)

        # Resolve target directory
        output_dir = folder_paths.get_output_directory()
        subfolder = subfolder.strip()
        if subfolder:
            target_dir = os.path.join(output_dir, subfolder)
            real_output = os.path.realpath(output_dir)
            real_target = os.path.realpath(target_dir)
            if not (real_target == real_output or real_target.startswith(real_output + os.sep)):
                raise ValueError(
                    f"Subfolder '{subfolder}' resolves outside the output directory."
                )
            os.makedirs(target_dir, exist_ok=True)
        else:
            target_dir = output_dir

        # Build filename with optional counter
        counter_length = max(0, counter_length)
        if counter_length > 0:
            # Scan directory for existing files to determine the next counter value
            pattern = re.compile(
                r"^" + re.escape(filename) + r"_(\d+)\." + re.escape(extension) + r"$"
            )
            counters = []
            try:
                for entry in os.scandir(target_dir):
                    m = pattern.match(entry.name)
                    if m:
                        counters.append(int(m.group(1)))
            except OSError:
                pass
            next_counter = max(counters) + 1 if counters else 1
            full_filename = f"{filename}_{next_counter:0{counter_length}d}.{extension}"
        else:
            # counter_length=0: no counter — same filename written on every run (overwrite behavior)
            full_filename = f"{filename}.{extension}"

        filepath = os.path.join(target_dir, full_filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)

        return io.NodeOutput(text, ui=ui.PreviewText(text))
