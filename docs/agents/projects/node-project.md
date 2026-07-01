# Project: Save Text Node for ComfyUI

## The Problem

There are a great many nodes for ComfyUI available online, but non-official nodes are notoriously unstable with some exceptions. The general philosophy in creating nodes is often to add as much flexibility as possible. However, the more complex they are, the higher the likelihood that the maintainers burn out and stop maintaining them.

In my search for a simple node to save a String to a file, after trying many different nodes and combining multiple nodes, I eventually decided that I would create a node myself. One that requires only a very minimal API surface and fills a single role to maximize its longevity facing the rapid ComfyUI API evolution.

## The Idea

I have a set of string nodes that are concatenated to collect metadata throughout my workflow. This ends as a long string that I would like to be able to save alongside the image, so I need a node with the simple task to save a string (multiline or not) to a file.

## Node Properties

The node needs these properties:

- `string` - An input string (multiline-capable).
- `string` - The filename.
- `string` - The file extension (defaults to `txt`, allows `.txt` notation by stripping the dot).
- `int` - Counter length (defaults to `5`, set to `0` to disable, separator char is `_`)
- `string` - Optional: The name of a subfolder to save the file in.
- `string` - An output string (passthrough of the 
input string).
- A preview text area to display the saved content.

## Node Action

The node builds the relative output path using the filename, optional counter, extension and optional folder name. It then saves the file to ComfyUI's output folder with the provided input string as content. 

> Note: The subfolder is created automatically if it does not exist yet.

### Counter Collision Logic

The counter is incremented for each duplicate file, which is determined by scanning the target folder (like the ImageSaveHelper does) for maximum reliability.

### String Trimming

The string must be trimmed on front and end.

### If Input Text Is Empty

Use the text `(empty string specified)` instead to make the fact visible.

### Node Caching

No caching: It must be re-executed each time.

## ComfyUI API Documentation

In the workspace, the project `comfyui-custom-node-skills` is available, which contains a set of Claude skills that you can use to extract the necessary knowledge to build custom nodes from.
