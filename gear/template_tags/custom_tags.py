from django.template.defaulttags import register

@register.filter
def get_item(object, attribute_name):
    if object is not None:
        return getattr(object, attribute_name)

@register.filter
def multiplyBy(object, value):
    return object * value
