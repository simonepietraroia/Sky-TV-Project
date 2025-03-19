import base64
from django import template

register = template.Library()

@register.filter
def decode_image(image_field):
    if not image_field:  
        return None

    try:
        with image_field.open("rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None 