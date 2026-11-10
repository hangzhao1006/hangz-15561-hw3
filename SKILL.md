---
name: python-docstrings
description: Write concise PEP 8 / PEP 257 compliant docstrings for Python code in a single pass. Every function and method docstring gets one line per input parameter and a line for the output. After writing, show the user each docstring and list any ambiguities that were resolved by assumption, so the user can accept the result or ask for fixes. Use when the user asks to document Python code, add or fix docstrings, or make docstrings PEP 8 / PEP 257 compliant.
---

# Python Docstrings

Write docstrings for the Python code the user points to in **one pass, without asking questions first**. Then report what was written and what was assumed. The user decides whether the result is good enough or whether to continue the conversation to fix it.

## Workflow

### 1. Determine Scope

Document what the user named: a file, a function, a selection, or a directory. If nothing is named but Python code is in the conversation, document that.

- Default to **all functions, methods, and classes** in scope, plus the module docstring if the user gave a whole file.
- Skip functions that already have a docstring meeting every rule below. Rewrite ones that don't, and say so in the report.
- Only ask before starting if the scope itself can't be determined (e.g., "document my code" with no file and no code in the conversation).

### 2. Read Before Writing

Read each function's full body, not just its name and signature. Also read:
- Functions it calls and functions that call it, when needed to understand what an argument means or what the return value is used for
- Project config (`pyproject.toml`, `setup.cfg`, `.ruff.toml`) for a `pydocstyle` convention or line-length setting
- A few existing docstrings in the project to detect the style in use

### 3. Write the Docstrings

Edit the file in place, touching **only docstrings**. Never change code, names, signatures, or formatting. If you notice a bug, note it in the report and leave the code alone.

Follow the **Docstring Rules** below. Aim for the shortest docstring that is accurate and complete.

### 4. Resolve Ambiguity by Principled Choice

When the meaning of a parameter or return value isn't certain from the code, **don't stop to ask**. Pick the most defensible reading and record it. In order of preference, base the choice on:

1. What the code actually does (always wins over the name)
2. How callers in the codebase use it
3. Names, type hints, and default values
4. Domain conventions (e.g., `fps` is frames per second, `lr` is learning rate)

Describe behavior the code actually has, even if it looks unintended. For example, if a function mutates its input and also returns it, document both. Don't write vague wording to hide uncertainty ("some value", "the data"). Commit to a specific description and flag it.

### 5. Report

After editing, reply with the following and nothing more:

**Docstrings written**: for each function, method, or class, its location and the docstring as written:

````markdown
#### `resample_frames` — [video.py:42](video.py:42)
```python
"""Resample video frames to a new frame rate.

Args:
    frames (list[numpy.ndarray]): RGB frames in display order.
    target_fps (float): Output frame rate in frames per second.

Returns:
    list[numpy.ndarray]: Resampled frames, same shape and dtype.
"""
```
````

**Assumptions to check**: a numbered list of every ambiguity resolved by choice. Each item names the function and parameter, states what was assumed, and gives the evidence for it in one sentence:

```markdown
1. `resample_frames` / `target_fps`: assumed frames per second, not
   a ratio. It is divided into `len(frames) / duration` on line 51.
2. `load_labels` returns `None` when the file is missing, because the
   `FileNotFoundError` is caught on line 88. Documented as a return case.
```

If there were none, write "None. Every docstring is based directly on the code."

**Also noticed** (only if applicable): suspected bugs, misleading names, or stale comments. One line each. Don't fix them.

End with one line telling the user they can reply with numbered corrections (e.g., "1: it's a ratio") or ask for any docstring to be rewritten.

Don't add extra commentary, restate the rules, or describe the process.

### Follow-up Turns

If the user replies with corrections, apply them, then show only the docstrings that changed. If a correction affects other docstrings (e.g., a shared parameter like `df` that appears across functions), update those too and say which ones.

## Docstring Rules

### Conciseness

- The summary line says what the function does in as few words as possible. No "This function...", "Helper to...", or "Used to...".
- Add an extended description only when the summary and the argument and return lines can't convey something the caller needs: a side effect, a non-obvious algorithm, a precondition, or a performance caveat. Most functions need none.
- Each parameter line is one short phrase saying what the value **is**, plus a unit, range, shape, or `None` meaning only when it matters. Wrap to a second line only when necessary.
- Don't restate the type in prose ("an integer that is...") or the obvious ("the path to the file" for `path`, unless saying what file).
- Omit `Examples` sections unless the user asks for them.

### The Input/Output Rule (mandatory)

Every function and method docstring is multi-line and contains:

1. **One line per input parameter**, in signature order, with name, type, and what it represents. Include `*args`, `**kwargs`, and keyword-only parameters. Exclude only `self` and `cls`. Mention a default only when its effect isn't obvious.
2. **An output line, always**:
   - `Returns:` with type and meaning.
   - For no return value: `Returns:` / `None.`, optionally with what the function does instead ("None. Writes the CSV to ``out_path``.").
   - For generators: `Yields:` with the type and meaning of each item.
   - For tuples: describe each element.
3. **`Raises:`** only for exceptions the function raises on purpose and that callers should handle.

If the function takes no parameters, write `Args:` / `None.`

Type hints don't remove the need for any of these lines. If the signature has hints, the docstring type may be left out only if the project's existing docstrings do so.

### PEP 8 / PEP 257 Format

- Triple double quotes `"""`. Use `r"""` if the docstring contains backslashes.
- Summary line: one line, imperative mood ("Return...", not "Returns..."), ends with a period, doesn't restate the signature.
- One blank line between the summary and the rest.
- The closing `"""` goes on its own line for multi-line docstrings.
- No blank line before or after a function docstring. One blank line after a class docstring.
- Body indented to match the opening quotes.
- Lines at most 72 characters, unless project config says otherwise.
- Module docstrings go at the very top of the file, before imports. One or two lines describing what the module provides.
- Class docstrings: summary, constructor `Args:`, and public `Attributes:`. Put constructor args in the class docstring or in `__init__`, matching the project, never both.

### Style

Use the project's existing style (Google, NumPy, or reST). If there is none, use **Google style**. Never mix styles in one project.

**Google (default):**

```python
def save_labels(labels, out_path):
    """Write frame labels to a CSV file.

    Args:
        labels (dict[int, str]): Label for each frame index.
        out_path (pathlib.Path): Destination CSV; overwritten if present.

    Returns:
        None.
    """
```

```python
def iter_batches(items, size):
    """Split items into consecutive batches.

    Args:
        items (Sequence[Any]): Items to split.
        size (int): Maximum batch length.

    Yields:
        list[Any]: Next batch; the last may be shorter than ``size``.
    """
```

```python
class FrameCache:
    """In-memory cache of decoded frames with oldest-first eviction.

    Args:
        max_frames (int): Maximum number of frames held.

    Attributes:
        hits (int): Lookups served from the cache.
    """

    def get(self, index):
        """Return a cached frame.

        Args:
            index (int): Zero-based frame index.

        Returns:
            numpy.ndarray | None: The frame, or None if not cached.
        """
```

**NumPy:**

```python
def scale(x, factor):
    """Multiply an array by a scalar.

    Parameters
    ----------
    x : numpy.ndarray
        Values to scale.
    factor : float
        Multiplier.

    Returns
    -------
    numpy.ndarray
        New array ``x * factor``; ``x`` is unchanged.
    """
```

**reST / Sphinx:**

```python
def scale(x, factor):
    """Multiply an array by a scalar.

    :param x: Values to scale.
    :type x: numpy.ndarray
    :param factor: Multiplier.
    :type factor: float
    :returns: New array ``x * factor``; ``x`` is unchanged.
    :rtype: numpy.ndarray
    """
```

## Self-Check Before Reporting

Before writing the report, verify each docstring against its signature:
- Each parameter except `self`/`cls` appears exactly once, in order, with the exact name
- A `Returns:` or `Yields:` section is present, including for `None`
- Documented defaults and raised exceptions match the code
- No line exceeds the length limit

If a shell is available and the project already uses `ruff` or `pydocstyle`, run it on the edited files and fix what it reports. Don't install tools or add config unless asked.
