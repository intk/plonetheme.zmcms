#!/usr/bin/python
# -*- coding: utf-8 -*-


from zope.component import getMultiAdapter, getUtility
from Products.CMFCore.utils import getToolByName

from docxtpl import DocxTemplate
from docx.shared import Inches
from cgi import escape

def escape_items(context):
    for item in context['items']:
        for attr in item:
            if attr not in ['image']:
                value = item[attr]
                new_value = escape(value)
                item[attr] = new_value

def generate_docx(tpl, items):
    sd = tpl.new_subdoc()
    sd.add_page_break()

    context = { 
        'items' : items,
        'pagebreak': sd
    }

    escape_items(context)

    tpl.render(context)
    return tpl
