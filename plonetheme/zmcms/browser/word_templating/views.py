#!/usr/bin/python
# -*- coding: utf-8 -*-

# Plone dependencies
from Products.Five import BrowserView
from zope.component import getMultiAdapter, getUtility
from Products.CMFCore.utils import getToolByName
from plone import api
from cStringIO import StringIO
import datetime
import csv

# DOCX dependencies
from docxtpl import DocxTemplate
from docx.shared import Inches

# CORE utils
from .core import CORE, EXPORT_PATH, TEMPLATE_PATH, LOG_PATH, NOT_ALLOWED, WordGeneratorCore
from .generator import generate_docx

DEFAULT_LIST_NUMBERS = 'M62-099,M62-100,M62-101,M62-126'
IMAGE_SIZE = {
	"a": 1.7,
	"b": 6.0
}
ENV = "dev"

class WordDocumentGenerator(BrowserView):
	"""
	Backend that generates a .docx file based on a word template.
	Input: List of object numbers, template to be used
	Returns: .docx file
	"""

	def __call__(self):
		# define file name
		resp = self.request.response
		self.catalog = getToolByName(self.context, 'portal_catalog')

		self.template = self.request.get('template')
		self.objects = self.request.get('objects')

		self.export_path = EXPORT_PATH[ENV]
		self.log_file = open(LOG_PATH[ENV], "a")
		self.log_wr = csv.writer(self.log_file, quoting=csv.QUOTE_ALL)
		# INIT core
		self.core = WordGeneratorCore(self.log_wr, ENV)

		return self.get_word_document()

	def get_template_path(self):
		if not self.template:
			return None
		else:
			if self.template.lower() in TEMPLATE_PATH[ENV]:
				path = TEMPLATE_PATH[ENV][self.template.lower()]
				return path
			else:
				return None
		return None

	def get_object(self, number):
		object_number = number.lower().strip()
		results = self.catalog(identification_identification_objectNumber=object_number, portal_type='Object')
		if results:
			brain = results[0]
			return brain

		return None

	def get_image_file(self, brain):
		DEFAULT_VALUE = ''

		if brain.leadMedia != None:
			results = self.catalog(UID=brain.leadMedia)
			if results:
				image_brain = results[0]
				image = image_brain.getObject()
				rawimage = StringIO(image.image.data)
				subdoc = self.tpl.new_subdoc()
				subdoc.add_picture(rawimage, width=Inches(IMAGE_SIZE[self.template]))
				return subdoc
			else:
				return DEFAULT_VALUE

		return DEFAULT_VALUE

	def get_fields(self, brain):
		obj = brain.getObject()

		item = {}
		for key, value in CORE.iteritems():
			repeatable = self.core.is_repeatable(value)
			if repeatable:
				fieldname, subfieldname = self.core.get_fields_names(value)
				field_value = self.core.get_subfield(obj, fieldname, subfieldname, 0)
				item[key] = field_value
			else:
				field_value = self.core.get_field(obj, value)
				item[key] = field_value

		media = self.get_image_file(brain)
		item['image'] = media

		return item

	def build_response(self, tpl):
		timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
		filename = "export-%s-%s.docx" %(self.template, timestamp)

		f = StringIO()
		tpl.save(f)
		tpl.save(self.export_path %(filename))

		ret = f.getvalue()
		f.close()

		self.request.response.setHeader('content-type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
		self.request.response.setHeader(
            'content-disposition', 'attachment;filename={}'.format(filename))

		return ret

	def get_word_document(self):

		self.template_path = self.get_template_path()
		if self.template_path:
			self.tpl = DocxTemplate(self.template_path)

			items = []
			if not self.objects:
				self.objects = DEFAULT_LIST_NUMBERS

			object_numbers = self.objects.split(',')
			for number in object_numbers:
				brain = self.get_object(number)
				if brain:
					self.core.write_log("Found: %s" %(brain.getURL()))
					new_item = self.get_fields(brain)
					items.append(new_item)
				else:
					self.core.write_log("Object not found: %s" %(number))

			final_docx = generate_docx(self.tpl, items)

			return self.build_response(final_docx)
		else:
			text = "Template ID: '%s' is not valid." %(self.template)
			self.core.write_log(text)
			return text




