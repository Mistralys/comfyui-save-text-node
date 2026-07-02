"""Extension registration for ComfyUI Save Text Node."""

from comfy_api.latest import ComfyExtension

from .nodes import SaveTextNode


class SaveTextExtension(ComfyExtension):
    async def get_node_list(self):
        return [SaveTextNode]


async def comfy_entrypoint() -> SaveTextExtension:
    return SaveTextExtension()
