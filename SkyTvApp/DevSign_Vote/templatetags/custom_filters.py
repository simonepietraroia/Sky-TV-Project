import base64
from django import template

register = template.Library()

@register.filter
def decode_image(image_data):
    if image_data:
        return base64.b64encode(image_data).decode('utf-8')
    return None
