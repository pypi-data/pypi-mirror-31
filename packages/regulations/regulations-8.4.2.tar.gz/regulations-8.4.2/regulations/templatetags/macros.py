"""Macros used to make a few common tasks in templates easier"""
from django import template
from django.utils.html import escape

register = template.Library()


@register.inclusion_tag('regulations/macros/external_link.html')
def external_link(url, text, classes="", title=""):
    return {"url": escape(url), "text": escape(text),
            "classes": escape(classes), "title": escape(title)}


@register.inclusion_tag('regulations/macros/search_for.html')
def search_for(terms, reg, version, text=None):
    if text is None:
        text = terms
    return {"terms": terms, "reg": reg, "version": version,
            "text": escape(text)}
