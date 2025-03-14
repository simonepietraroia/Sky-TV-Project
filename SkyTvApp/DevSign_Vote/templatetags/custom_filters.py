import base64
from django import template

register = template.Library()

@register.filter(name="decode_image")
def decode_image(image_binary):
    """Convert binary image data to a Base64-encoded string."""
    if image_binary:
        return base64.b64encode(image_binary).decode("utf-8")
    return ""