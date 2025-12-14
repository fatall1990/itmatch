from django import template

register = template.Library()

@register.filter
def intersect(list1, list2):
    """Возвращает пересечение двух списков"""
    return list(set(list1) & set(list2))