# core/renderer.py

from jinja2 import Template
from core.templates import TEMPLATES
from utils.logger import setup_logger

logger = setup_logger("renderer")

"""
Render CLI commands from a Jinja2 template.

Args:
    name (str): Template key from TEMPLATES dict.
    context (dict): Data to pass into the template.

Returns:
    List of CLI commands (strings).
"""

def render_template(name: str, context: dict) -> list[str]:
    template_str = TEMPLATES.get(name)
    if not template_str:
        logger.error(f"Template '{name}' not found.")
        raise ValueError(f"No template named '{name}'.")

    logger.debug(f"Rendering template '{name}' with context: {context}")
    template = Template(template_str)
    rendered = template.render(**context)
    lines = rendered.strip().splitlines()

    logger.info(f"Rendered {len(lines)} lines from template '{name}'")
    for line in lines:
        logger.debug(f"  >> {line}")

    return lines
