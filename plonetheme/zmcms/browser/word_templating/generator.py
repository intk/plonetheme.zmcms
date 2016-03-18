#!/usr/bin/python
# -*- coding: utf-8 -*-


from zope.component import getMultiAdapter, getUtility
from Products.CMFCore.utils import getToolByName

from docxtpl import DocxTemplate
from docx.shared import Inches


def generate_docx(tpl, items):
    sd = tpl.new_subdoc()
    sd.add_page_break()

    context = { 
        'items' : items,
        'pagebreak': sd
    }

    print context['items']

    tpl.render(context)
    return tpl
