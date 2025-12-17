"""Utilities for loading and rendering Jinja2 prompt templates."""

from pathlib import Path
from functools import lru_cache
from typing import Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

# Default templates directory: same folder as this file
TEMPLATES_DIR = Path(__file__).parent.resolve()


@lru_cache(maxsize=8)
def _get_env(templates_dir: str) -> Environment:
    """Return a cached Jinja2 environment for the given templates directory."""
    loader = FileSystemLoader(str(templates_dir))
    return Environment(
        loader=loader,
        autoescape=select_autoescape(enabled_extensions=("j2", "jinja2", "tpl", "txt")),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _normalize_filename(filename: str) -> str:
    """Add .j2 extension if no template extension is present."""
    if not any(filename.endswith(ext) for ext in (".j2", ".jinja2", ".tpl", ".txt")):
        return filename + ".j2"
    return filename


def load_prompt_template(
    filename: str, templates_dir: Optional[str] = None
) -> Template:
    """Load and return a Jinja2 Template for the given prompt filename.

    Args:
        filename: name of the template file (with or without extension).
        templates_dir: optional directory to load templates from (defaults to
            this module's folder).

    Returns:
        Loaded Jinja2 Template object.

    Raises:
        FileNotFoundError: if template not found.
    """
    directory = (
        str(Path(templates_dir).resolve()) if templates_dir else str(TEMPLATES_DIR)
    )
    env = _get_env(directory)
    name = _normalize_filename(filename)
    try:
        return env.get_template(name)
    except Exception as exc:
        raise FileNotFoundError(
            f"Prompt template '{name}' not found in {directory}"
        ) from exc


def render_prompt(
    filename: str,
    context: Optional[Dict[str, Any]] = None,
    templates_dir: Optional[str] = None,
) -> str:
    """Load a prompt template and render it with the provided context dict.

    Returns:
        The rendered string.
    """
    tpl = load_prompt_template(filename, templates_dir)
    return tpl.render(context or {})


__all__ = ["load_prompt_template", "render_prompt"]
