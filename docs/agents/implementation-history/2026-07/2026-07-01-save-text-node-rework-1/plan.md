# Plan

## Plan Audit Cycles
- Audits: none — Plan Auditor v1.5.0
- Architectural Reviews: none — Plan Architect Reviewer v1.6.0

## Prior Project Context
The initial plan (`2026-07-01-save-text-node`) delivered a production-ready `SaveTextNode` across 4 work packages with 18/18 pipeline stages passing and zero rework. The security audit identified two Medium OWASP A01 path-traversal risks in `subfolder` and `filename` inputs — documented in `README.md` and `api-surface.md` but intentionally deferred. The synthesis recommended remediating these as the primary next step, alongside three lower-priority items. Knowledge base insight #2 (`OWASP A01 path-traversal risk — unmitigated`) confirms the exact remediation pattern. This rework plan addresses all actionable synthesis items, including deferred items promoted to plan steps.

## Summary
Address all actionable items from the `2026-07-01-save-text-node` synthesis: remediate two OWASP A01 path-traversal vulnerabilities in `nodes.py execute()`, add server-side `counter_length` validation, handle the empty-extension edge case, and add `authors` metadata to `pyproject.toml` for registry readiness. Update documentation to reflect the hardened behavior.

## Architectural Context
The project consists of three source files:
- [nodes.py](../../nodes.py) — `SaveTextNode` class with `define_schema()` and `execute()` classmethod
- [__init__.py](../../__init__.py) — Extension registration via `ComfyExtension` + `comfy_entrypoint()`
- [pyproject.toml](../../pyproject.toml) — Package metadata

The `execute()` method in `nodes.py` (lines 35–79) is the sole target for all code changes. It currently:
1. Trims input text and replaces empty text with a placeholder
2. Strips leading dots from the extension
3. Resolves target directory via `folder_paths.get_output_directory()` + optional subfolder
4. Scans for existing files to determine counter value (when counter_length > 0)
5. Writes text to the resolved file path

The path-traversal risk exists at steps 3 and 5: `subfolder` is joined to `output_dir` without boundary validation (line ~47), and `filename` is used without stripping path separators (line ~62).

## Approach / Architecture
All code changes are confined to `nodes.py execute()`. No new files, no new dependencies, no architectural changes.

1. **Path traversal remediation**: Add `os.path.realpath()` boundary checks after resolving the target directory, and apply `os.path.basename()` to strip path separators from `filename`. Raise `ValueError` if the resolved path escapes the output directory boundary.
2. **counter_length validation**: Clamp to non-negative with `max(0, counter_length)` before the counter logic.
3. **Empty-extension fallback**: Default to `"txt"` if `extension.lstrip(".")` yields an empty string.
4. **pyproject.toml authors**: Add the `authors` field.
5. **Documentation updates**: Remove the security caveats from `README.md` and `api-surface.md`; replace with a note that path-boundary enforcement is active.

## Rationale
- The path-traversal remediation is the only non-trivial risk in the codebase. The `os.path.realpath()` + prefix check pattern is the standard OWASP-recommended approach and requires no external dependencies.
- Raising `ValueError` (rather than silently clamping the path) makes malicious input visible — ComfyUI surfaces Python exceptions to the user.
- The `counter_length` and empty-extension fixes are defensive single-line guards with zero risk of regression.
- Adding `authors` to `pyproject.toml` is a metadata-only change with no runtime impact.

## Considered Alternatives

| Decision | Chosen Shape | Alternatives Considered | Trade-Off Summary |
|----------|--------------|-------------------------|-------------------|
| Path boundary enforcement | `os.path.realpath()` prefix check + `ValueError` | Regex-based character filtering; allowlist of path components | `realpath` resolves symlinks and `..` canonically — character filtering is incomplete (misses encoded separators, symlinks). `ValueError` is explicit and debuggable. |
| Filename sanitization | `os.path.basename()` | Regex stripping of `os.sep` and `/` | `basename()` is a single stdlib call that handles all platform-specific separators; regex needs platform-conditional logic. |
| Empty extension handling | Default to `"txt"` | Raise error; leave as trailing dot | Defaulting matches the existing `extension` default value (`"txt"`) and prevents OS-dependent trailing-dot behavior on Windows. Silent and non-breaking. |
| counter_length validation | `max(0, counter_length)` | Raise error for negative | Clamping is consistent with how ComfyUI handles schema violations gracefully. A negative counter_length is a schema bypass edge case, not a user error. |

## Pattern Alignment
- **`os.path.realpath()` boundary check**: Standard OWASP A01 remediation pattern. No existing codebase pattern to follow — this is a new security layer.
- **`os.path.basename()`**: Standard Python path sanitization. No departure from conventions.
- **Defensive clamping** (`max(0, ...)`, fallback defaults): Consistent with the existing empty-text placeholder pattern in `execute()` (line ~38).

## Detailed Steps

### 1. Add path-traversal boundary check for `subfolder` in `nodes.py`

In `execute()`, after resolving `target_dir` (currently line ~47–51), add a realpath boundary check:

```python
# After: target_dir = os.path.join(output_dir, subfolder)
real_output = os.path.realpath(output_dir)
real_target = os.path.realpath(target_dir)
if not (real_target == real_output or real_target.startswith(real_output + os.sep)):
    raise ValueError(
        f"Subfolder '{subfolder}' resolves outside the output directory."
    )
```

Place this check **before** `os.makedirs()` to prevent directory creation outside the boundary.

### 2. Sanitize `filename` to prevent path traversal in `nodes.py`

Before the filename is used in the counter logic or final path construction, strip any path components:

```python
filename = os.path.basename(filename)
```

Add this immediately after the existing `extension = extension.lstrip(".")` line (~line 41). This ensures `filename` cannot contain directory separators regardless of platform.

### 3. Add empty-extension fallback in `nodes.py`

After `extension = extension.lstrip(".")`, add:

```python
if not extension:
    extension = "txt"
```

This handles the edge case where the user provides an extension consisting entirely of dots (e.g., `"..."` → `""` after lstrip → default to `"txt"`).

### 4. Add `counter_length` server-side validation in `nodes.py`

At the start of the counter logic block, before the `if counter_length > 0:` branch, add:

```python
counter_length = max(0, counter_length)
```

This ensures a negative `counter_length` (possible only via schema bypass) is treated as `0` (no counter).

### 5. Add `authors` field to `pyproject.toml`

Add an `authors` entry to the `[project]` table:

```toml
authors = [
    { name = "Mistralys" },
]
```

This improves discoverability when the package is submitted to the ComfyUI registry. The name matches the existing `PublisherId` in `[tool.comfy]`.

### 6. Update `README.md` security note

Replace the current "Security Note" section with an updated version that reflects the active path-boundary enforcement:

> **Security Note**
>
> The `subfolder` and `filename` inputs are validated against path-traversal attacks. The node resolves the final path using `os.path.realpath()` and rejects any path that escapes ComfyUI's output directory. The `filename` input is sanitized with `os.path.basename()` to strip directory separators.
>
> If you expose ComfyUI to a network, additional hardening at the ComfyUI / reverse-proxy level is still recommended. See [ComfyUI security hardening](https://docs.comfy.org/tutorials/basic/comfyui-on-a-server) for guidance.

### 7. Update `api-surface.md` security note

Remove the OWASP A01 security caveat from the Inputs table notes and replace with:

> `subfolder` and `filename` are validated with `os.path.realpath()` boundary check and `os.path.basename()` sanitization respectively. Paths resolving outside the output directory raise `ValueError`.

### 8. Update `docs/agents/project-manifest/constraints.md`

Add a constraint entry documenting the path-boundary enforcement as a project invariant.

## Dependencies

- No new dependencies. All changes use Python stdlib (`os.path.realpath`, `os.path.basename`, `max`).

## Required Components

- [nodes.py](../../nodes.py) — **EXISTS** — modify `execute()` method (steps 1–4)
- [pyproject.toml](../../pyproject.toml) — **EXISTS** — add `authors` field (step 5)
- [README.md](../../README.md) — **EXISTS** — update security note (step 6)
- [docs/agents/project-manifest/api-surface.md](../project-manifest/api-surface.md) — **EXISTS** — update security note (step 7)
- [docs/agents/project-manifest/constraints.md](../project-manifest/constraints.md) — **EXISTS** — add constraint entry (step 8)

## Assumptions

- `os.path.realpath()` correctly canonicalizes paths on the deployment OS (Windows, Linux, macOS). This is a Python stdlib guarantee.
- ComfyUI surfaces `ValueError` exceptions to the user as workflow errors (standard Python exception handling).
- The `PublisherId` in `pyproject.toml` (`Mistralys`) is the correct author/maintainer name.

## Constraints

- No new files — all changes are to existing files.
- No new dependencies — stdlib only.
- No behavioral changes for valid inputs — only invalid (path-traversal) inputs are rejected.
- The boundary check must use `os.path.realpath()` (not `os.path.abspath()`) to resolve symlinks.

## Out of Scope

- Automated test infrastructure (pytest fixtures, CI/CD). The project remains manually tested.
- Registry submission process (this plan adds the `authors` field; actual submission is a separate activity).
- Additional input sanitization beyond path traversal (e.g., filename character restrictions, length limits).
- `__init__.py` changes — no modifications needed.

## Acceptance Criteria

- A `subfolder` value containing `..` that would escape the output directory raises `ValueError` instead of creating files outside the boundary.
- A `filename` value containing path separators (e.g., `../../etc/passwd`) is sanitized to its basename (e.g., `passwd`) before use.
- An extension consisting entirely of dots (e.g., `"..."`) defaults to `"txt"` instead of producing a trailing-dot filename.
- A negative `counter_length` value (schema bypass) is treated as `0` (no counter, overwrite mode).
- The `authors` field is present in `pyproject.toml`.
- The `README.md` security note reflects active path-boundary enforcement (no longer a caveat).
- The `api-surface.md` security note reflects active validation (no longer a warning).
- All existing behavior for valid inputs is unchanged — the node continues to function identically for non-malicious usage.

## Testing Strategy

Testing remains manual in the ComfyUI environment. The new test obligations focus on the boundary conditions introduced by the security remediation.

## Test Plan

- **Manual: Subfolder traversal blocked** — Set subfolder to `../../etc`, run workflow, verify `ValueError` is raised and no directory is created outside the output folder. Covers: path-traversal remediation for subfolder.
- **Manual: Nested subfolder traversal blocked** — Set subfolder to `valid/../../../escape`, verify `ValueError`. Covers: realpath resolution of mixed valid/traversal paths.
- **Manual: Valid subfolder still works** — Set subfolder to `metadata/session1`, verify subdirectories are created and file is saved correctly. Covers: no regression for valid subfolder paths.
- **Manual: Filename with path separators sanitized** — Set filename to `../../evil`, verify the output file is named `evil_00001.txt` (basename extracted). Covers: filename sanitization.
- **Manual: Filename with backslash separators** — Set filename to `..\\..\\evil`, verify basename extraction works on Windows. Covers: platform-specific separator handling.
- **Manual: All-dots extension defaults to txt** — Set extension to `...`, verify output file has `.txt` extension. Covers: empty-extension fallback.
- **Manual: Normal extension unchanged** — Set extension to `md`, verify output file has `.md` extension. Covers: no regression for valid extensions.
- **Manual: counter_length clamping** — (If schema bypass is possible) Provide counter_length=-1, verify behavior matches counter_length=0 (overwrite mode). Covers: server-side counter_length validation.
- **Manual: Basic save unchanged** — Standard workflow with default inputs, verify file is written correctly. Covers: no regression for standard usage.
- **Manual: Counter increment unchanged** — Run 3 times with defaults, verify `output_00001.txt`, `output_00002.txt`, `output_00003.txt`. Covers: no regression for counter logic.

## Documentation Updates

Per `AGENTS.md` documentation maintenance rules:

- [README.md](../../README.md) — Replace the "Security Note" section to reflect active path-boundary enforcement instead of a caveat.
- [docs/agents/project-manifest/api-surface.md](../project-manifest/api-surface.md) — Update the security note in the Inputs section to reflect active validation.
- [docs/agents/project-manifest/constraints.md](../project-manifest/constraints.md) — Add path-boundary enforcement as a project constraint/invariant.
- [docs/agents/projects/node-project.md](../projects/node-project.md) — No changes needed (spec does not reference security behavior).
- [docs/agents/project-manifest/file-tree.md](../project-manifest/file-tree.md) — No changes needed (no new files).

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| **`os.path.realpath()` behaves differently across platforms** | `realpath` is a Python stdlib function with consistent cross-platform behavior. The prefix check uses `os.sep` which adapts to the platform. |
| **Symlinked output directory causes false-positive rejection** | The check compares `realpath(target)` against `realpath(output_dir)`, so both sides resolve symlinks — a symlinked output directory works correctly. |
| **`ValueError` disrupts workflow for users with valid but unusual subfolder names** | The check only rejects paths that resolve outside the output directory. Valid subfolders with special characters (spaces, unicode) pass through because `realpath` only normalizes path structure, not content. |
| **`os.path.basename()` strips intentional directory components in filename** | This is the intended behavior. The `filename` input is documented as a base filename; directory components are not supported by design. |
| **Authors field uses incorrect name** | The name `Mistralys` matches the existing `PublisherId` in `[tool.comfy]`. If the registry requires a different format, it can be updated at submission time. |
