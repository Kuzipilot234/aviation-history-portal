import markdown as markdown_lib
import nh3
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def markdownify(text):
    """Render AI-written Markdown as HTML, keeping only safe tags."""
    rendered = markdown_lib.markdown(text or "", extensions=["tables", "sane_lists"])
    return mark_safe(nh3.clean(rendered))
