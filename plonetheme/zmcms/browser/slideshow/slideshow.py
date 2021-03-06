#!/usr/bin/python
# -*- coding: utf-8 -*-

#Slideshow theme specific

from Products.Five import BrowserView
import json
from zope.component import getMultiAdapter, getUtility
from Products.CMFCore.utils import getToolByName
from collective.leadmedia.interfaces import ICanContainMedia
from zope.schema import getFieldsInOrder
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from zope.i18nmessageid import MessageFactory as msgfactory
from zope.intid.interfaces import IIntIds
from zc.relation.interfaces import ICatalog
from zope.security import checkPermission
from plone import api
from plone.app.uuid.utils import uuidToCatalogBrain, uuidToObject
from plone.app.contenttypes.behaviors.collection import ICollection
from z3c.relationfield.interfaces import IRelationValue
from zope.component import getMultiAdapter, getUtility
from Products.CMFCore.utils import getToolByName


MessageFactory = msgfactory('collective.object')
_book = msgfactory('collective.bibliotheek')

NOT_ALLOWED = [None, '', ' ', 'None']


class get_nav_objects(BrowserView):
    """
    Utils
    """

    def generate_related_exhibitions_objects(self, tab, object_schema, fields, object, field_schema):
        for field, choice in tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                related_objects = self.get_field_from_object(field, object)
                if len(related_objects) > 0:
                    temp_schema = []

                    for rel in related_objects:
                        rel_object = rel.to_object
                        temp_schema.append("<a href='%s'>%s</a>" %(rel_object.absolute_url(), rel_object.title))

                    if len(temp_schema) > 0:
                        title = fieldvalue.title
                        new_schema = {"title": self.context.translate(_book(title)), "value": "<p>".join(temp_schema)}
                        object_schema[field_schema]['fields'].append(new_schema)

    def generate_related_museum_objects(self, tab, object_schema, fields, object, field_schema):
        for field, choice in tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                related_objects = self.get_field_from_object(field, object)
                if len(related_objects) > 0:
                    temp_schema = []

                    for rel in related_objects:
                        rel_object = rel.to_object
                        temp_schema.append("<a href='%s'>%s</a>" %(rel_object.absolute_url(), rel_object.title))

                    if len(temp_schema) > 0:
                        title = fieldvalue.title
                        new_schema = {"title": self.context.translate(_book(title)), "value": "<p>".join(temp_schema)}
                        object_schema[field_schema]['fields'].append(new_schema)
                     

    def generate_regular_tab(self, tab, object_schema, fields, object, field_schema):
        for field, choice in tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice)

                if schema_value != "":
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(_book(title)), "value": schema_value})

    def generate_series_isbn_tab(self, identification_tab, object_schema, fields, object, field_schema):
        for field, choice in identification_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice)

                if schema_value != "":
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(_book(title)), "value": schema_value})

    def generate_title_author_tab(self, identification_tab, object_schema, fields, object, field_schema):
        for field, choice in identification_tab:
            # Title field
            if field in ['title']:
                value = getattr(object, field, "")
                if value != "" and value != None:
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(_book('Title')), "value": value})
            
            # Regular fields
            else:
                fieldvalue = self.get_field_from_schema(field, fields)
                if fieldvalue != None:
                    title = fieldvalue.title
                    value = self.get_field_from_object(field, object)

                    schema_value = self.transform_schema_field(field, value, choice)

                    if schema_value != "":
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(_book(title)), "value": schema_value})

    def get_all_fields_book(self, object):

        object_schema = {}

        object_schema["title_author"] = {
            "fields": [],
            "name": self.context.translate(_book("Title, author, imprint, collation"))
        }

        object_schema["series_notes_isbn"] = {
            "fields": [],
            "name": self.context.translate(_book("Series, notes, ISBN"))
        }

        object_schema["abstract_subject_terms"] = {
            "fields": [],
            "name": self.context.translate(_book("Abstract and subject terms"))
        }

        object_schema["reproductions"] = {
            "fields": [],
            "name": self.context.translate(_book("Reproductions"))
        }

        object_schema["exhibitions_auctions_collections"] = {
            "fields": [],
            "name": self.context.translate(_book("Exhibitions, auctions, collections"))
        }

        object_schema["relations"] = {
            "fields": [],
            "name": self.context.translate(_book("Relations"))
        }

        object_schema["free_fields_numbers"] = {
            "fields": [],
            "name": self.context.translate(_book("Free fields and numbers"))
        }

        object_schema["copies_and_shelf_marks"] = {
            "fields": [],
            "name": self.context.translate(_book("Copies and shelf marks"))
        }


        schema = getUtility(IDexterityFTI, name='Book').lookupSchema()
        fields = getFieldsInOrder(schema)

        title_author_tab = [('title', None), ('titleAuthorImprintCollation_titleAuthor_author', 'author'), 
                            ('titleAuthorImprintCollation_titleAuthor_illustrator', 'illustrator'),
                            ('titleAuthorImprintCollation_titleAuthor_statementOfRespsib', None),
                            ('titleAuthorImprintCollation_titleAuthor_corpAuthor', None),
                            ('titleAuthorImprintCollation_edition_edition', None),
                            ('titleAuthorImprintCollation_imprint_place', None),
                            ('titleAuthorImprintCollation_imprint_publisher', None),
                            ('titleAuthorImprintCollation_imprint_year', None),
                            ('titleAuthorImprintCollation_imprint_placePrinted', None)
                            ]

        series_notes_isbn_tab = [('seriesNotesISBN_series_series', 'series'),
                                ('seriesNotesISBN_series_subseries', 'subseries'),
                                ('seriesNotesISBN_notes_bibliographicalNotes', None),
                                ('seriesNotesISBN_ISBN_ISBN', 'ISBN'),
                                ('seriesNotesISBN_ISBN_ISSN', None)]

        abstract_subject_terms_tab = [('abstractAndSubjectTerms_materialType', None),
                                     ('abstractAndSubjectTerms_classNumber', None),
                                     ('abstractAndSubjectTerms_subjectTerm', 'subjectType'),
                                     ('abstractAndSubjectTerms_personKeywordType', 'name'),
                                     ('abstractAndSubjectTerms_geographicalKeyword', None),
                                     ('abstractAndSubjectTerms_period', None),
                                     ('abstractAndSubjectTerms_startDate', None),
                                     ('abstractAndSubjectTerms_endDate', None),
                                     ('abstractAndSubjectTerms_digitalReferences_reference', None),
                                     ('abstractAndSubjectTerms_abstract_abstract', None)]

        reproductions_tab = [('reproductions_reproduction', 'reference', None)]

        exhibitions_tab = []

        free_fields_tab = []

        copies_tab = [('copiesAndShelfMarks_copyDetails', None)]

        museum_objects_tab = [('relations_relatedMuseumObjects', None)]

        related_exhibitions = [('exhibitionsAuctionsCollections_relatedExhibitions', None)]

        ## Identification tab
        self.generate_title_author_tab(title_author_tab, object_schema, fields, object, "title_author")

        ## Series
        self.generate_series_isbn_tab(series_notes_isbn_tab, object_schema, fields, object, "series_notes_isbn")

        ## Abstract
        self.generate_regular_tab(abstract_subject_terms_tab, object_schema, fields, object, "abstract_subject_terms")

        ## Reproductions
        self.generate_reproductions_tab(reproductions_tab, object_schema, fields, object, "reproductions")

        ## Related exhibitions
        self.generate_related_exhibitions_objects(related_exhibitions, object_schema, fields, object, "exhibitions_auctions_collections")

        ## Exhibition
        self.generate_regular_tab(exhibitions_tab, object_schema, fields, object, "exhibitions_auctions_collections")

        ## Free fields
        self.generate_regular_tab(free_fields_tab, object_schema, fields, object, "free_fields_numbers")

        ## Copies and shelf marks
        self.generate_regular_tab(copies_tab, object_schema, fields, object, "copies_and_shelf_marks")
        
        ## Museum objects
        self.generate_related_museum_objects(museum_objects_tab, object_schema, fields, object, "relations")

        new_object_schema = []
        new_object_schema.append(object_schema['title_author'])
        new_object_schema.append(object_schema['series_notes_isbn'])
        new_object_schema.append(object_schema['abstract_subject_terms'])
        new_object_schema.append(object_schema['reproductions'])
        new_object_schema.append(object_schema['exhibitions_auctions_collections'])
        new_object_schema.append(object_schema['relations'])
        new_object_schema.append(object_schema['free_fields_numbers'])
        new_object_schema.append(object_schema['copies_and_shelf_marks'])

        return new_object_schema

    def get_slideshow_items(self):
        item = self.context
        order = self.request.get('sort_on')
        catalog = getToolByName(self.context, 'portal_catalog')

        scale = "/@@images/image/large"

        items = []

        if item.portal_type == "Object":
            if hasattr(item, 'slideshow'):
                slideshow = item['slideshow']
                path = '/'.join(slideshow.getPhysicalPath())

                if order == None:
                    order = 'getObjPositionInParent'

                results = catalog.searchResults(path={'query': path, 'depth': 1}, sort_on=order)
                for brain in results:
                    url = brain.getObject().absolute_url()
                    slideshow_url = "%s%s" %(url, scale)
                    items.append({'url':slideshow_url})

        return json.dumps(items)


    def get_object_idx(self, results, object_id, is_folder):
        if is_folder:
            for idx, res in enumerate(results):
                if res.getId == object_id:
                    return idx
        else:
            for idx, res in enumerate(results):
                if res.getId() == object_id:
                    return idx

    def get_all_batch(self, collection_object, is_folder):
        catalog = getToolByName(self.context, 'portal_catalog')

        if is_folder:
            collection_obj = collection_object
        else:
            collection_obj = collection_object.getObject()

        if is_folder:
            folder_path = '/'.join(collection_obj.getPhysicalPath())
            results = catalog(path={'query': folder_path, 'depth': 1})
        else:
            sort_on = ICollection(collection_obj).sort_on
            results = collection_obj.queryCatalog(batch=False, sort_on=sort_on)

        #print results
        return results

    def get_batch(self, collection_object, start, pagesize=33):
        collection_obj = collection_object.getObject()

        results = collection_obj.queryCatalog(batch=True, b_start=int(start), b_size=pagesize)

        return results

    """
    Get prev obj
    """
    def get_prev_obj(self, start, collection_id):
        pagesize = 33
        
        if "/" not in start:
            object_id = self.context.getId()
            collection_object = uuidToCatalogBrain(collection_id)

            if collection_object:
                if collection_object.portal_type == "Collection":
                    ## Get Batch of collection
                    results = self.get_batch(collection_object, start, pagesize)
                    
                    ## Get prev item
                    object_idx = self.get_object_idx(results, object_id)                    
                    if object_idx > 0:
                        return results[object_idx-1]
                    else:
                        if results.has_previous:
                            page = results.previouspage
                            start = int(start)
                            start = (page * pagesize) - pagesize
                            b_results = self.get_batch(collection_object, start, pagesize)
                            last_element = b_results[b_results.items_on_page-1]
                            return last_element
                        else:
                            lastpage = results.lastpage
                            start = int(start)
                            start = (lastpage * pagesize) - pagesize
                            b_results = self.get_batch(collection_object, start, pagesize)
                            last_element = b_results[b_results.items_on_page-1]
                            return last_element
    """
    Get next obj
    """
    def get_next_obj(self, start, collection_id):
        pagesize = 33

        if "/" not in start:
            object_id = self.context.getId()
            collection_object = uuidToCatalogBrain(collection_id)

            if collection_object:
                if collection_object.portal_type == "Collection":
                    results = self.get_batch(collection_object, start, pagesize)
                    object_idx = self.get_object_idx(results, object_id)
                    if object_idx < results.items_on_page-1:
                        return results[object_idx+1]
                    else:
                        if results.has_next:
                            page = results.nextpage
                            page -= 1
                            start = int(start)
                            start = (page * pagesize)
                            b_results = self.get_batch(collection_object, start, pagesize)
                            first_element = b_results[0]
                            return first_element
                        else:
                            start = 0
                            b_results = self.get_batch(collection_object, start, pagesize)
                            first_element = b_results[0]
                            return first_element

    def get_collection_from_catalog(self, collection_id):
        uuid = collection_id
        collection_object = uuidToCatalogBrain(collection_id)
        if collection_object:
            if collection_object.portal_type == "Collection":
                return collection_object

        return None

    def get_all_items_from_collection(self, collection_object):
        items = {
            "list":[],
            "object_idx":0,
            'total':False
        }

        results = self.get_all_batch(collection_object, False)
        object_idx = self.get_object_idx(results, self.context.getId())
        items['object_idx'] = object_idx

        for obj in results:
            if obj != None:
                obj_media = ICanContainMedia(obj.getObject()).getLeadMedia()
                if obj_media != None:
                    items['list'].append({'url':obj.getURL(),'image_url': obj_media.absolute_url()+'/@@images/image/large', 'object_id': obj.getId(), 'title':obj.Title(), 'description': obj.Description(), 'body': ""})

        return items

    """
    AJAX to get all items inside collection
    """
    def get_all_collection(self):
        collection_id = self.request.get('collection_id')
        items = []
        
        if collection_id != None:
            collection_object = self.get_collection_from_catalog(collection_id)
            if collection_object != None:
                ## Get Batch of collection
                items = self.get_all_items_from_collection(collection_object)

        return json.dumps(items)

    def get_multiple_images(self, _object, view_type):
        images = []
        
        if view_type == 'double_view':
            limit = 2
            curr = 0
            if hasattr(_object, 'slideshow'):
                slideshow = _object['slideshow']
                if slideshow.portal_type == "Folder":
                    for img in slideshow:
                        curr += 1 
                        if slideshow[img].portal_type == 'Image':
                            images.append(slideshow[img].absolute_url()+'/@@images/image/large')
                        if curr >= limit:
                            break

        elif view_type == 'multiple_view':
            if hasattr(_object, 'slideshow'):
                slideshow = _object['slideshow']
                if slideshow.portal_type == "Folder":
                    for img in slideshow:
                        if slideshow[img].portal_type == 'Image':
                            images.append(slideshow[img].absolute_url()+'/@@images/image/large')

        res = sorted(images)
        return res

    def trim_white_spaces(self, text):
        if text != "" and text != None:
            if len(text) > 0:
                if text[0] == " ":
                    text = text[1:]
                if len(text) > 0:
                    if text[-1] == " ":
                        text = text[:-1]
                return text
            else:
                return ""
        else:
            return ""

    def create_author_name(self, value):
        comma_split = value.split(",")

        for i in range(len(comma_split)):       
            name_split = comma_split[i].split('(')
            
            raw_name = name_split[0]
            name_split[0] = self.trim_white_spaces(raw_name)
            name_artist = name_split[0]
            
            name_artist_link = '<a href="/'+self.context.language+'/search?SearchableText=%s">%s</a>' % (name_artist, name_artist)
            name_split[0] = name_artist_link

            if len(name_split) > 1:
                if len(name_split[1]) > 0:
                    name_split[0] = name_artist_link + " "
        
            comma_split[i] = '('.join(name_split)

        _value = ", ".join(comma_split)

        return _value

    def create_materials(self, value):
        materials = value.split(',')
        _value = ""
        for i, mat in enumerate(materials):
            if i == (len(materials)-1):
                _value += '<a href="/'+self.context.language+'/search?SearchableText=%s">%s</a>' % (mat, mat)
            else:
                _value += '<a href="/'+self.context.language+'/search?SearchableText=%s">%s</a>, ' % (mat, mat)

        return _value


    ## NEW FIELDS

    def get_field_from_object(self, field, object):
        
        empty_field = ""
        
        value = getattr(object, field, "")
        if value != "" and value != None:
            return value
        
        return empty_field

    def get_field_from_schema(self, fieldname, schema):
        for name, field in schema:
            if name == fieldname:
                return field

        return None

    def transform_schema_field(self, name, field_value, choice=None, restriction=None, not_show=[]):
        try:
            if type(field_value) is list:
                new_val = []
                if choice == None:
                    for val in field_value:
                        if type(val) is unicode:
                            new_val.append(val)
                        elif type(val) is str:
                            new_val.append(val)
                        else:
                            for key, value in val.iteritems():
                                if key not in not_show:
                                    if value != "" and value != None and value != " ":
                                        if restriction != None:
                                            if value != restriction:
                                                if key in "name" and name not in ['exhibitions_exhibition','identification_objectName_objectname']:
                                                    value = self.create_maker(value)
                                                if type(value) is list: 
                                                    new_val.append(value[0])
                                                else:
                                                    new_val.append(value)
                                        else:
                                            if key == "name" and name not in ['exhibitions_exhibition','identification_objectName_objectname']:
                                                value = self.create_maker(value)
                                            if type(value) is list: 
                                                new_val.append(value[0])
                                            else:
                                                new_val.append(value)
                else:
                    for val in field_value:
                        if val[choice] != "" and val[choice] != None and val[choice] != " ":
                            if restriction != None:
                                if val[choice] != restriction:
                                    if choice == "name" and name not in ['exhibitions_exhibition','identification_objectName_objectname']:
                                        new_val.append(self.create_maker(val[choice]))
                                    else:
                                        
                                        if type(val[choice]) is list: 
                                            if val[choice]:
                                                new_val.append(val[choice][0])
                                        else:
                                            new_val.append(val[choice])
                            else:
                                if choice in ["name", "author"] and name not in ['exhibitions_exhibition','identification_objectName_objectname']:
                                    new_val.append(self.create_maker(val[choice]))
                                else:
                                    if type(val[choice]) is list: 
                                        if val[choice]:
                                            new_val.append(val[choice][0])
                                    else:
                                        new_val.append(val[choice])

                if len(new_val) > 0:
                    if name in ["exhibitions_exhibition", "productionDating_production", "labels", "seriesNotesISBN_notes_bibliographicalNotes",
                                "abstractAndSubjectTerms_notes", "abstractAndSubjectTerms_abstract_abstract",
                                "exhibitionsAuctionsCollections_exhibition", "exhibitionsAuctionsCollections_auction",
                                "exhibitionsAuctionsCollections_collection"]:
                        return '<p>'.join(new_val)
                    else:
                        for index, single_value in enumerate(new_val):
                            single_value = "<a href='/%s/search?SearchableText=%s'>%s</a>" %(self.context.language, single_value, single_value)
                            new_val[index] = single_value
                        return ', '.join(new_val)
                else:
                    return ""
            else:
                return field_value
        except:
            return ""


    def generate_identification_tab(self, identification_tab, object_schema, fields, object, field_schema):
        for field, choice in identification_tab:
            # Title field
            if field in ['title']:
                value = getattr(object, field, "")
                if value != "" and value != None and value != " ":
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Title')), "value": value})

            elif field in ['text']:
                val = getattr(object, field, "")
                if val:
                    value = val.output
                else:
                    value = ""
                if value != "" and value != None and value != " ":
                    object_schema[field_schema]['fields'].append({"title": "body", "value": value})
            
            # Regular fields
            elif field not in ['identification_taxonomy']:
                fieldvalue = self.get_field_from_schema(field, fields)
                if fieldvalue != None:
                    title = fieldvalue.title
                    value = self.get_field_from_object(field, object)

                    schema_value = self.transform_schema_field(field, value, choice)

                    if schema_value != "" and schema_value != " ":
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})

            # Taxonomy special case
            else:
                taxonomy = self.get_field_from_object(field, object)
                if len(taxonomy) > 0:
                    taxonomy_elem = taxonomy[0]

                    scientific_name = taxonomy_elem['scientific_name']
                    #common_name = taxonomy_elem['common_name']

                    #if scientific_name != "" and scientific_name != " ":
                    #    object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Scient. name')), "value": scientific_name})
                    #if common_name != "" and common_name != " ":
                    #    object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Common name')), "value": common_name})


    def create_maker(self, name, url=False):
        maker = []
        name_split = name.split(",")

        if len(name_split) > 0:
            if len(name_split) > 1:
                maker.append(name_split[-1])
                maker.append(name_split[0])
            else:
                maker.append(name_split[0])

        new_maker = ' '.join(maker)
        if url:
            #language = self.context.language
            #new_maker = "<a href='%s'>%s</a>" %(url, new_maker)
            new_maker = new_maker
            #new_maker = "<a href='/%s/search?SearchableText=%s'>%s</a>" %(language, new_maker, new_maker)

        return new_maker

    def create_production_field(self, field, url=False):
        production = ""

        maker = field['maker']
        qualifier = field['qualifier']
        role = field['role']
        place = field['place']

        production = self.create_maker(maker, url)

        if qualifier not in NOT_ALLOWED:
            if production:
                production = "%s, %s" %(qualifier, production)
            else:
                production = "%s" %(qualifier)

        if role not in NOT_ALLOWED:
            if production:
                production = "(%s) %s" %(role, production)
            else:
                production = "(%s)" %(role)

        if place not in NOT_ALLOWED:
            if production:
                production = "%s, %s" %(production, place)
            else:
                production = "%s" %(place)

        return production

    def create_period_field(self, field):
        period = field['period']
        start_date = field['date_early']
        start_date_precision = field['date_early_precision']
        end_date = field['date_late']
        end_date_precision = field['date_late_precision']

        result = ""

        if period != "" and period != None and period != " ":
            result = "%s" %(period)

        if start_date != "" and start_date != " ":
            if result:
                if start_date_precision != "" and start_date_precision != " ":
                    result = "%s, %s %s" %(result, start_date_precision, start_date)
                else:
                    result = "%s, %s" %(result, start_date)
            else:
                if start_date_precision != "" and start_date_precision != " ":
                    result = "%s %s" %(start_date_precision, start_date)
                else:
                    result = "%s" %(start_date)
    

        if end_date != "" and end_date != " ":
            if result:
                if end_date_precision != "" and end_date_precision != " ":
                    result = "%s - %s %s" %(result, end_date_precision, start_date)
                else:
                    result = "%s - %s" %(result, end_date)
            else:
                if end_date_precision != "" and end_date_precision != " ":
                    result = "%s %s" %(end_date_precision, start_date)
                else:
                    result = "%s" %(end_date)

        return result

    def get_url_by_uid(self, uid):
        brains = uuidToCatalogBrain(uid)
        if brains:
            return brains.getURL()
        return ""

    def generate_production_dating(self, production_dating_tab, object_schema, fields, object, field_schema):
        production_field = self.get_field_from_object('productionDating_productionDating', object)

        production_result = []
        # Generate production
        url = ""
        for field in production_field:
            production = {}
            if field['makers']:
                production['maker'] = field["makers"][0].title
                url = self.get_url_by_uid(field["makers"][0].UID())
            else:
                production['maker'] = ""

            production['qualifier'] = field['qualifier']

            if field['role']:
                production['role'] = field['role'][0]
            else:
                production['role'] = ""

            if field['place']:
                production['place'] = field['place'][0]
            else:
                production['place'] = ""

            result = self.create_production_field(production, url)
            if result not in NOT_ALLOWED:
                production_result.append(result)

        if len(production_result) > 0:
            production_value = '<p>'.join(production_result)
            object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Maker')), "value": production_value})


        ## Generate Period
        period_field = self.get_field_from_object('productionDating_dating_period', object)

        period = []
        for field in period_field:
            result = self.create_period_field(field)
            if result not in NOT_ALLOWED:
                period.append(result)

        if len(period) > 0:
            period_value = ', '.join(period)
            object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Period')), "value": period_value})

    def generate_production_dating_tab(self, production_dating_tab, object_schema, fields, object, field_schema):

        ## Generate Author
        production_field = self.get_field_from_object('productionDating_production', object)
        production = []
        for field in production_field:
            result = self.create_production_field(field)
            if result not in NOT_ALLOWED:
                production.append(result)

        if len(production) > 0:
            production_value = '<p>'.join(production)
            object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Maker')), "value": production_value})

        ## Generate Period
        period_field = self.get_field_from_object('productionDating_dating_period', object)

        period = []
        for field in period_field:
            result = self.create_period_field(field)
            if result not in NOT_ALLOWED:
                period.append(result)

        if len(period) > 0:
            period_value = ', '.join(period)
            object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Period')), "value": period_value})

    def create_dimension_field(self, field):
        new_dimension_val = []
        dimension_result = ""

        for val in field:
            dimension = ""
            if val['value'] != "":
                dimension = "%s" %(val['value'])
            if val['units'] != "":
                dimension = "%s %s" %(dimension, val['units'])
            if val['dimension'] != "" and val['dimension'] != []:
                dimension = "%s: %s" %(val['dimension'][0], dimension)

            new_dimension_val.append(dimension)

        dimension_result = '<p>'.join(new_dimension_val)
        
        return dimension_result

    def generate_physical_characteristics_tab(self, physical_characteristics_tab, object_schema, fields, object, field_schema):
        
        for field, choice, restriction in physical_characteristics_tab:
            if field == 'physicalCharacteristics_dimension':
                dimension_field = getattr(object, 'physicalCharacteristics_dimension', None)
                if dimension_field != None:
                    dimension = self.create_dimension_field(dimension_field)
                    ## add to schema
                    if dimension != "" and dimension != None:
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Dimensions')), "value": dimension})
            else:
                fieldvalue = self.get_field_from_schema(field, fields)
                if fieldvalue != None:
                    title = fieldvalue.title
                    value = self.get_field_from_object(field, object)

                    schema_value = self.transform_schema_field(field, value, choice)

                    if schema_value != "":
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})


    def generate_associations_tab(self, associations_tab, object_schema, fields, object, field_schema):
        for field, choice, restriction in associations_tab:
            if field == "associations_associatedPersonInstitutions":
                fieldvalue = self.get_field_from_schema(field, fields)
                if fieldvalue:
                    title = fieldvalue.title
                    associations_field = self.get_field_from_object('associations_associatedPersonInstitutions', object)

                    result = []
                    for line in associations_field:
                        names = line["names"]
                        if names:
                            name = names[0].title
                            url = self.get_url_by_uid(names[0].UID())
                            new_name = self.create_maker(name, url)
                            result.append(new_name)

                    final_result = "<p>".join(result)
                    if final_result != "":
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": final_result})

            else:
                fieldvalue = self.get_field_from_schema(field, fields)
                if fieldvalue != None:
                    title = fieldvalue.title
                    value = self.get_field_from_object(field, object)

                    schema_value = self.transform_schema_field(field, value, choice)

                    if schema_value != "":
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})
    
    def generate_reproductions_tab(self, reproductions_tab, object_schema, fields, object, field_schema):
        for field, choice, restriction in reproductions_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice)

                if schema_value != "":
                    if field == "reproductions_reproduction":
                        title = "Reference"
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})    

    def generate_recommendations_tab(self, recommendations_tab, object_schema, fields, object, field_schema):
        for field, choice, restriction in recommendations_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice)

                if schema_value != "":
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})     

    def generate_location_tab(self, location_tab, object_schema, fields, object, field_schema):
        for field, choice, restriction in location_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice)

                if schema_value != "":
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})


    def generate_fieldcollection_tab(self, fieldcollection_tab, object_schema, fields, object, field_schema):
        for field, choice, restriction in fieldcollection_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice)

                if schema_value != "":
                    if field == 'fieldCollection_habitatStratigraphy_stratigraphy':
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Geologisch tijdvak')), "value": schema_value})
                    else:
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})


    def generate_exhibitions_tab_temp(self, exhibitions_tab, object_schema, fields, object, field_schema):
        for field, choice, restriction, not_show in exhibitions_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice, restriction, not_show)

                if schema_value != "":
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})

    def generate_exhibition_tab(self, exhibitions_tab, object_schema, fields, object, field_schema):

        relations = []
        related_exhibitions = []

        def get_url_by_uid(context, uid):
            brain = uuidToCatalogBrain(uid)
            if brain:
                return brain.getURL()

            return ""

        for field, choice, restriction, not_show in exhibitions_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)
                if value:
                    for val in value:
                        exhibition = val['exhibitionName']
                        if exhibition:
                            rel = exhibition[0]
                            rel_obj = None
                            if IRelationValue.providedBy(rel):
                                rel_obj = rel.to_object
                            else:
                                rel_obj = rel

                            if rel_obj:
                                rel_url = get_url_by_uid(self.context, rel_obj.UID())
                                rel_title = rel_obj.title
                                related_exhibitions.append("<a href='%s'>%s</a>"%(rel_url, rel_title))

                                rel_date_start = ""
                                rel_date_end = ""
                                if hasattr(rel_obj, 'start_date'):
                                    rel_date_start = rel_obj.start_date

                                if hasattr(rel_obj, 'end_date'):
                                    rel_date_end = rel_obj.end_date

                                if rel_date_start != "":
                                    try:
                                        date_start = rel_date_start.strftime('%Y-%m-%d')
                                    except:
                                        rel_date_start = ""

                                if rel_date_end != "":
                                    try:
                                        date_end = rel_date_end.strftime('%Y-%m-%d')
                                    except:
                                        rel_date_end = ""


                                final_date = ""
                                if rel_date_start != "" and rel_date_end != "":
                                    final_date = "%s t/m %s" %(date_start, date_end)

                                if final_date != "":
                                    related_exhibitions.append(final_date)

                                # organisator
                                orgs = []
                                locations = []
                                places = []
                                """organisators = rel_obj.exhibitionsDetails_organizingInstitutions

                                if organisators:
                                    for organiser in organisators:
                                        try:
                                            name = organiser['name']
                                            if name:
                                                if name != 'Zeeuws Museum':
                                                    orgs.append(name)
                                        except:
                                            pass

                                        try:
                                            l = organiser['address']
                                            if l:
                                                if l != 'Zeeuws Museum':
                                                    locations.append(l)

                                            p = organiser['place']
                                            if p:
                                                if p != 'Zeeuws Museum':
                                                    places.append(p)
                                        except:
                                            pass

                                    final_orgs = ', '.join(orgs)
                                    if final_orgs:
                                        related_exhibitions.append(final_orgs)
                                    
                                    final_locations = ', '.join(locations)
                                    if final_locations:
                                        related_exhibitions.append(final_locations)

                                    final_places = ', '.join(places)
                                    if final_places:
                                        related_exhibitions.append(final_places)"""

        if len(related_exhibitions) > 0:
            related_exhibitions_value = '<p>'.join(related_exhibitions)
            object_schema[field_schema]['fields'].append({'title': self.context.translate(MessageFactory('Exhibition name')), 'value': related_exhibitions_value})


    def generate_exhibitions_tab(self, exhibitions_tab, object_schema, fields, object, field_schema):
        intids = getUtility(IIntIds)
        catalog = getUtility(ICatalog)

        relations = sorted(catalog.findRelations({'to_id': intids.getId(object), 'from_attribute':'linkedObjects_relatedItems'}))

        related_exhibitions = []
        for rel in relations:
            rel_obj = rel.from_object
            rel_url = rel_obj.absolute_url()
            rel_title = rel_obj.title
            related_exhibitions.append("<a href='%s'>%s</a>"%(rel_url, rel_title))

            rel_date_start = ""
            rel_date_end = ""
            if hasattr(rel_obj, 'start_date'):
                rel_date_start = rel_obj.start_date

            if hasattr(rel_obj, 'end_date'):
                rel_date_end = rel_obj.end_date

            if rel_date_start != "":
                date_start = rel_date_start.strftime('%Y-%m-%d')

            if rel_date_end != "":
                date_end = rel_date_start.strftime('%Y-%m-%d')

            final_date = ""
            if rel_date_start != "" and rel_date_end != "":
                final_date = "%s t/m %s" %(date_start, date_end)

            if final_date != "":
                related_exhibitions.append(final_date)

        if len(related_exhibitions) > 0:
            related_exhibitions_value = '<p>'.join(related_exhibitions)
            object_schema[field_schema]['fields'].append({'title': self.context.translate(MessageFactory('Exhibitions')), 'value': related_exhibitions_value})

    def generate_labels_tab(self, labels_tab, object_schema, fields, object, field_schema):
        for field, choice, restriction in labels_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice, restriction)

                if schema_value != "":
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})

    def generate_related_books_tab(self, object_schema, fields, object, field_schema):
        if checkPermission('cmf.ManagePortal', self.context):
            intids = getUtility(IIntIds)
            catalog = getUtility(ICatalog)

            relations = sorted(catalog.findRelations({'to_id': intids.getId(object), 'from_attribute':'relations_relatedMuseumObjects'}))
            related_exhibitions = []
            for rel in relations:
                rel_obj = rel.from_object
                rel_url = rel_obj.absolute_url()
                rel_title = rel_obj.title
                related_exhibitions.append("<a href='%s'>%s</a>"%(rel_url, rel_title))
            
            if len(related_exhibitions) > 0:
                related_exhibitions_value = '<p>'.join(related_exhibitions)
                object_schema[field_schema]['fields'].append({'title': self.context.translate(MessageFactory('Books')), 'value': related_exhibitions_value})


    def generate_documentation_tab(self, object_schema, fields, object, field_schema):
        if hasattr(object, 'documentation_documentation'):
            documentation = object.documentation_documentation
            docs = []

            if documentation:
                for doc in documentation:
                    try:
                        if doc['title'] != "":
                            new_doc = "%s" %(doc['title'])

                            if doc['pageMark'] != "":
                                new_doc = "%s, %s" %(new_doc, doc['pageMark'])

                            if doc['notes'] != "":
                                new_doc = "%s, %s" %(new_doc, doc['notes'])

                            docs.append(new_doc)
                    except:
                        pass

            if len(docs) > 0:
                schema_value = '<p>'.join(docs)
                object_schema[field_schema]['fields'].append({'title': self.context.translate(MessageFactory('Documentation')), 'value': schema_value})


    def get_all_fields_object(self, object):

        object_schema = {}

        object_schema["identification"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Identification"))
        }

        object_schema["production_dating"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Production & Dating"))
        }

        object_schema["physical_characteristics"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Physical Characteristics"))
        }

        object_schema["associations"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Associations"))
        }

        object_schema["reproductions"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Reproductions"))
        }

        object_schema["recommendations_requirements"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Recommendations/requirements"))
        }

        object_schema["location"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Location"))
        }

        object_schema["field_collection"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Field Collection"))
        }

        object_schema["exhibitions"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Exhibitions"))
        }

        object_schema["labels"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Labels"))
        }

        object_schema["books"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Books"))
        }

        object_schema["documentation"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Documentation"))
        }


        schema = getUtility(IDexterityFTI, name='Object').lookupSchema()
        fields = getFieldsInOrder(schema)

        identification_tab = [('identification_identification_collections', None), ('identification_identification_objectNumber', None),
                                ('identification_objectName_category', None), ('identification_objectName_objectname', 'name'),
                                ('title', None), ('identification_taxonomy', 'scientific_name'), ('text', None)]

        production_dating_tab = ['productionDating_production', 'productionDating_dating_period']

        physical_characteristics_tab = [('physicalCharacteristics_technique', 'technique', None), ('physicalCharacteristics_material', 'material', None),
                                        ('physicalCharacteristics_dimension', None, None)]

        associations_tab = [('associations_associatedPersonInstitutions', 'names', None), ('associations_associatedSubjects', 'subject', None)]

        reproductions_tab = [('reproductions_reproduction', 'reference', None)]

        recommendations_tab = [('recommendationsRequirements_creditLine_creditLine', None, None)]

        location_tab = [('location_current_location', 'location_type', None)]

        fieldcollection_tab = [('fieldCollection_fieldCollection_places', None, None), ('fieldCollection_habitatStratigraphy_stratigrafie', 'unit', None)]

        exhibitions_tab = [('exhibitions_exhibition', None, 'Zeeuws Museum', ['catObject'])]

        labels_tab = [('labels', 'text', None)]


        ## Identification tab
        try:
            self.generate_identification_tab(identification_tab, object_schema, fields, object, "identification")
        except:
            pass
            
        ## Vervaardiging & Datering tab
        #self.generate_production_dating_tab(production_dating_tab, object_schema, fields, object, "production_dating")
        try:
            self.generate_production_dating(production_dating_tab, object_schema, fields, object, "production_dating")
        except:
            pass
            
        ## Physical Characteristics
        try:
            self.generate_physical_characteristics_tab(physical_characteristics_tab, object_schema, fields, object, "physical_characteristics")
        except:
            pass

        ## Associations
        try:
            self.generate_associations_tab(associations_tab, object_schema, fields, object, "associations")
        except:
            pass
        ## Reproductions
        try:
            self.generate_reproductions_tab(reproductions_tab, object_schema, fields, object, "reproductions")
        except:
            pass
        ## Recommendations
        try:
            self.generate_recommendations_tab(recommendations_tab, object_schema, fields, object, "recommendations_requirements")
        except:
            pass
        ## Location
        try:
            self.generate_location_tab(location_tab, object_schema, fields, object, "location")
        except:
            pass
        ## Field collection
        try:
            self.generate_fieldcollection_tab(fieldcollection_tab, object_schema, fields, object, "field_collection")
        except:
            pass
        ## Exhibtions
        #self.generate_exhibitions_tab(exhibitions_tab, object_schema, fields, object, "exhibitions")
        try:
            self.generate_exhibition_tab(exhibitions_tab, object_schema, fields, object, "exhibitions")
        except:
            pass

        ## Labels
        try:
            self.generate_labels_tab(labels_tab, object_schema, fields, object, "labels")
        except:
            pass

        ## Books
        try:
            self.generate_related_books_tab(object_schema, fields, object, "books")
        except:
            pass

        ## Documentation
        try:
            self.generate_documentation_tab(object_schema, fields, object, "documentation")
        except:
            pass

        new_object_schema = []
        new_object_schema.append(object_schema['identification'])
        new_object_schema.append(object_schema['production_dating'])
        new_object_schema.append(object_schema['physical_characteristics'])
        new_object_schema.append(object_schema['associations'])
        new_object_schema.append(object_schema['reproductions'])
        new_object_schema.append(object_schema['recommendations_requirements'])
        new_object_schema.append(object_schema['location'])
        new_object_schema.append(object_schema['field_collection'])
        new_object_schema.append(object_schema['exhibitions'])
        new_object_schema.append(object_schema['labels'])
        new_object_schema.append(object_schema['books'])
        new_object_schema.append(object_schema['documentation'])
        return new_object_schema



    def build_json_with_list(self, list_items, object_idx, total, is_folder, total_items):
        items = {
            'list':[],
            'object_idx':object_idx,
            'total': total,
            'has_list_images':False,
            'view_type': 'regular',
            'total_items': 0
        }

        state = getMultiAdapter(
                (self.context, self.request),
                name=u'plone_context_state')

        # Check view type
        view_type = state.view_template_id()

        if view_type == "double_view" or view_type == "multiple_view":
            items["has_list_images"] = True
            items["view_type"] = view_type

        items['total_items'] = total_items

        if is_folder:
            for obj in list_items:
                obj_media = ICanContainMedia(obj.getObject()).getLeadMedia()
                if obj_media != None:
                    if obj.portal_type == "Book":
                        schema = self.get_all_fields_book(obj.getObject())
                    else:
                        schema = self.get_all_fields_object(obj.getObject())
                        
                    if not items['has_list_images']:
                        items['list'].append({'schema':schema, 'url':obj.getURL(),'image_url': obj_media.absolute_url()+'/@@images/image/large', 'object_id': obj.getId, 'title':obj.Title, 'description': obj.Description, 'body': self.get_object_body(obj.getObject())})
                    else:
                        items['list'].append({'schema':schema, 'images':self.get_multiple_images(obj.getObject(), view_type), 'url':obj.getURL(),'image_url': obj_media.absolute_url()+'/@@images/image/large', 'object_id': obj.getId, 'title':obj.Title, 'description': obj.Description, 'body': self.get_object_body(obj.getObject())})    
                else:
                    if obj.portal_type == "Book":
                        schema = self.get_all_fields_book(obj.getObject())
                    else:
                        schema = self.get_all_fields_object(obj.getObject())
                    items['list'].append({'schema':schema, 'url':obj.getURL(),'image_url': '', 'object_id': obj.getId, 'title':obj.Title, 'description': obj.Description, 'body': self.get_object_body(obj.getObject())})

        else:
            for obj in list_items:
                obj_media = ICanContainMedia(obj.getObject()).getLeadMedia()
                
                if obj_media != None:
                    if obj.portal_type == "Book":
                        schema = self.get_all_fields_book(obj.getObject())
                    else:
                        schema = self.get_all_fields_object(obj.getObject())
                    if not items['has_list_images']:
                        items['list'].append({'schema':schema, 'url':obj.getURL(),'image_url': obj_media.absolute_url()+'/@@images/image/large', 'object_id': obj.getId(), 'title':obj.Title(), 'description': obj.Description(), 'body': self.get_object_body(obj)})
                    else:
                        items['list'].append({'schema':schema, 'images':self.get_multiple_images(obj.getObject(), view_type), 'url':obj.getURL(),'image_url': obj_media.absolute_url()+'/@@images/image/large', 'object_id': obj.getId(), 'title':obj.Title(), 'description': obj.Description(), 'body': self.get_object_body(obj)})        

                else:
                    if obj.portal_type == "Book":
                        schema = self.get_all_fields_book(obj.getObject())
                    else:
                        schema = self.get_all_fields_object(obj.getObject())
                    items['list'].append({'schema':schema, 'url':obj.getURL(),'image_url': '', 'object_id': obj.getId(), 'title':obj.Title(), 'description': obj.Description(), 'body': self.get_object_body(obj)})
                         
        return items

    """
    Get bulk of prev items
    """
    def get_prev_objects(self):
        bulk = 10
        b_start = self.request.get('b_start')
        collection_id = self.request.get('collection_id')
        object_id = self.request.get('object_id')

        if b_start != None and collection_id != None and object_id != None:
            collection_object = self.get_collection_from_catalog(collection_id)
            results = self.get_all_batch(collection_object, False)
            object_idx = self.get_object_idx(results, object_id)

            if object_idx-bulk >= 0:
                list_of_items = list(results)
                bulk_of_items = list_of_items[(object_idx-bulk):object_idx]
                items = self.build_json_with_list(bulk_of_items, 0, False, False, len(list_of_items))
                items['list'] = list(reversed(items['list']))
                return json.dumps(items)

        return json.dumps({'list':[], 'object_idx':0})




    def get_next_objects(self):
        bulk = 10
        b_start = self.request.get('b_start')
        collection_id = self.request.get('collection_id')
        object_id = self.request.get('object_id')
        req_bulk = self.request.get('bulk')

        if req_bulk != None:
            buffer_size = int(req_bulk)

        is_collection = False
        is_folder = False
        if b_start != None and collection_id != None:
            is_collection = True
        else:
            if self.context.getParentNode() != None:
                parent = self.context.getParentNode();
                if parent.portal_type == 'Folder':
                    is_folder = True

        if not (is_folder == False and is_collection == False) and object_id != None:
            if is_collection:
                collection_object = self.get_collection_from_catalog(collection_id)
            else:
                collection_object = parent

            results = self.get_all_batch(collection_object, is_folder)
            object_idx = self.get_object_idx(results, object_id, is_folder)

            if object_idx+bulk < len(results):
                list_of_items = list(results)
                bulk_of_items = list_of_items[(object_idx+1):(object_idx+bulk+1)]
                items = self.build_json_with_list(bulk_of_items, 0, False, is_folder, len(list_of_items))
                return json.dumps(items)
            
            elif object_idx+bulk >= len(results):
                list_of_items = list(results)
                offset = (object_idx+bulk) - len(results)
                bulk_of_items = list_of_items[(object_idx+1):] + list_of_items[0:(offset+1)]
                items = self.build_json_with_list(bulk_of_items, 0, True, is_folder, len(list_of_items))
                return json.dumps(items)

        return json.dumps({'list':[], 'object_idx':0, 'total':False})

    def get_object_body(self, object):
        if hasattr(object, 'text') and object.text != None:
            return object.text.output
        else:
            return ""

    """
    Get bulk of next items
    """

    def _get_next_objects(self):
        buffer_size = 10
        b_start = self.request.get('b_start')
        collection_id = self.request.get('collection_id')
        object_id = self.request.get('object_id')
        req_bulk = self.request.get('bulk')

        dangerous_entries = int(object_id)

        collection_object = uuidToObject(collection_id)

        if collection_object.portal_type == "Collection":
            new_start = dangerous_entries

            if int(b_start) > buffer_size:
                new_start = int(b_start) + 5
            
            sort_on = ICollection(collection_object).sort_on
            next_batch = collection_object.queryCatalog(batch=True, b_size=buffer_size, b_start=new_start, sort_on=sort_on)
            next_items = next_batch._sequence

            collection_total_size = next_items.actual_result_count
            items = self.build_json_with_list(next_items, 0, False, False, collection_total_size)
            return json.dumps(items)

        return json.dumps({'list':[], 'object_idx':0, 'total':False})

    def _getJSON(self):
        
        buffer_size = 10

        object_id = self.context.getId()

        b_start = self.request.get('b_start')
        b_start = int(b_start)
        collection_id = self.request.get('collection_id')
        req_buffer = self.request.get('bulk')
        #if req_buffer:
        #    buffer_size = int(req_buffer)

        collection_object = uuidToObject(collection_id)

        if collection_object.portal_type == "Collection":
            b_size = ICollection(collection_object).item_count
            sort_on = ICollection(collection_object).sort_on
            real_object_index = b_start

            if real_object_index - buffer_size < 0:
                new_size = buffer_size - abs(real_object_index-buffer_size)
                if new_size:
                    prev_batch = collection_object.queryCatalog(batch=True, b_size=new_size, b_start=0, sort_on=sort_on)
                    prev_items = prev_batch._sequence
                else:
                    prev_items = []

            elif real_object_index - buffer_size >= 0:
                new_start = real_object_index - buffer_size
                if buffer_size:
                    prev_batch = collection_object.queryCatalog(batch=True, b_size=buffer_size, b_start=new_start, sort_on=sort_on)
                    prev_items = prev_batch._sequence
                else:
                    prev_items = []

            next_batch = collection_object.queryCatalog(batch=True, b_size=buffer_size, b_start=real_object_index, sort_on=sort_on)
            next_items = next_batch._sequence

            collection_total_size = next_items.actual_result_count
            final_items = list(next_items) + list(prev_items)
            items = self.build_json_with_list(final_items, 0, False, False, collection_total_size)
            items['index_obj'] = real_object_index+1

            return json.dumps(items)

        return json.dumps({'list':[], 'object_idx':0, 'total':False})
        

    def getJSON(self):
        pagesize = 33
        
        buffer_size = 10
        b_start = self.request.get('b_start')
        collection_id = self.request.get('collection_id')
        req_bulk = self.request.get('bulk')

        if req_bulk != None:
            buffer_size = int(req_bulk)

        items = {}

        is_folder = False
        is_collection = False

        if b_start != None and collection_id != None:
            is_collection = True
        else:
            if self.context.getParentNode() != None:
                parent = self.context.getParentNode();
                if parent.portal_type == 'Folder':
                    is_folder = True

        if not (is_folder == False and is_collection == False): 
            if is_collection:
                collection_object = self.get_collection_from_catalog(collection_id)
            else:
                collection_object = parent

            current_id = self.context.getId()

            results = self.get_all_batch(collection_object, is_folder)
            object_idx = self.get_object_idx(results, current_id, is_folder)

            if object_idx-buffer_size >= 0 and object_idx+buffer_size < len(results):
                list_of_items = list(results)
                
                prev_items = list_of_items[(object_idx-buffer_size):object_idx]
                next_items = list_of_items[object_idx:(object_idx+buffer_size+1)]

                bulk_of_items = next_items + prev_items
                
                items = self.build_json_with_list(bulk_of_items, 0, False, is_folder, len(list_of_items))
                items['index_obj'] = object_idx+1
                return json.dumps(items)
            
            elif object_idx-buffer_size < 0 and object_idx+buffer_size < len(results):
                #fetch from last page
                offset = object_idx-buffer_size
                
                list_of_items = list(results)
                prev_items = list_of_items[offset:] + list_of_items[0:object_idx]
                next_items = list_of_items[object_idx:(object_idx+buffer_size+1)]

                bulk_of_items = next_items + prev_items
                
                items = self.build_json_with_list(bulk_of_items, 0, False, is_folder, len(list_of_items))
                items['index_obj'] = object_idx+1
                return json.dumps(items)

            elif object_idx+buffer_size >= len(results) and object_idx-buffer_size > 0:
                list_of_items = list(results)

                offset = (object_idx+buffer_size) - len(results)

                prev_items = list_of_items[(object_idx-buffer_size):object_idx]
                next_items = list_of_items[object_idx:] + list_of_items[0:(offset+1)]

                bulk_of_items = next_items + prev_items
                items = self.build_json_with_list(bulk_of_items, 0, False, is_folder, len(list_of_items))
                items['index_obj'] = object_idx+1
                return json.dumps(items)

            elif object_idx+buffer_size >= len(results) and object_idx-buffer_size < 0:
                list_of_items = list(results)

                prev_items = list_of_items[0:object_idx]
                next_items = list_of_items[object_idx:]

                bulk_of_items = next_items + prev_items
                items = self.build_json_with_list(bulk_of_items, 0, True, is_folder, len(list_of_items))
                items['index_obj'] = object_idx+1
                return json.dumps(items)
        else:
            return json.dumps(items);


class get_slideshow_options(BrowserView):
    """
    AJAX call to get slideshow options
    """
    def getJSON(self):
        callback = hasattr(self.request, 'callback') and 'json' + self.request['callback'] or None
        only_documented = not hasattr(self.request, 'only_documented') 
        
        state = getMultiAdapter(
                (self.context, self.request),
                name=u'plone_context_state')

        # Check view type
        view_type = state.view_template_id()

        if view_type == "double_view":
            options = {
                'changes': True,
                'slidesToShow': 2,
                'arrows':False,
                'height':'480px',
                'type': 'double'
            }
        elif view_type == "multiple_view":
            options = {
                'changes': True,
                'autoplay': True,
                'autoplaySpeed': 500,
                'type': 'multiple',
                'arrows': False
            }
        else:
            options = {
                'changes': False
            }

        json_str = json.dumps(options)

        if callback is not None:
            return callback +'(' + json_str + ')'
        else:
            return json_str


class get_fields(BrowserView):
    """
    Utils
    """

    def get_object_body(self, object):
        if hasattr(object, 'text') and object.text != None:
            return object.text.output
        else:
            return ""

    def trim_white_spaces(self, text):
        if text != "" and text != None:
            if len(text) > 0:
                if text[0] == " ":
                    text = text[1:]
                if len(text) > 0:
                    if text[-1] == " ":
                        text = text[:-1]
                return text
            else:
                return ""
        else:
            return ""

    def create_author_name(self, value):
        comma_split = value.split(",")

        for i in range(len(comma_split)):       
            name_split = comma_split[i].split('(')
            
            raw_name = name_split[0]
            name_split[0] = self.trim_white_spaces(raw_name)
            name_artist = name_split[0]
            
            name_artist_link = '<a href="/'+self.context.language+'/search?SearchableText=%s">%s</a>' % (name_artist, name_artist)
            name_split[0] = name_artist_link

            if len(name_split) > 1:
                if len(name_split[1]) > 0:
                    name_split[0] = name_artist_link + " "
        
            comma_split[i] = '('.join(name_split)

        _value = ", ".join(comma_split)

        return _value

    def create_materials(self, value):
        materials = value.split(',')
        _value = ""
        for i, mat in enumerate(materials):
            if i == (len(materials)-1):
                _value += '<a href="/'+self.context.language+'/search?SearchableText=%s">%s</a>' % (mat, mat)
            else:
                _value += '<a href="/'+self.context.language+'/search?SearchableText=%s">%s</a>, ' % (mat, mat)

        return _value

    
    def getJSON(self):
        schema = []
        if self.context.portal_type == "Object":
            obj = self.context
            schema = self.get_all_fields_object(obj)
        elif self.context.portal_type == "Book":
            obj = self.context
            schema = self.get_all_fields_book(obj)

        return json.dumps({'schema':schema})


    ## NEW FIELDS

    def get_field_from_object(self, field, object):
        
        empty_field = ""
        
        value = getattr(object, field, "")
        if value != "" and value != None:
            return value
        
        return empty_field

    def get_field_from_schema(self, fieldname, schema):
        for name, field in schema:
            if name == fieldname:
                return field

        return None

    def transform_schema_field(self, name, field_value, choice=None, restriction=None, not_show=[]):
        try:
            if type(field_value) is list:
                new_val = []
                if choice == None:
                    for val in field_value:
                        if type(val) is unicode:
                            new_val.append(val)
                        elif type(val) is str:
                            new_val.append(val)
                        else:
                            for key, value in val.iteritems():
                                if key not in not_show:
                                    if value != "" and value != None and value != " ":
                                        if restriction != None:
                                            if value != restriction:
                                                if key in "name" and name not in ['exhibitions_exhibition','identification_objectName_objectname']:
                                                    value = self.create_maker(value)
                                                if type(value) is list: 
                                                    new_val.append(value[0])
                                                else:
                                                    new_val.append(value)
                                        else:
                                            if key == "name" and name not in ['exhibitions_exhibition','identification_objectName_objectname']:
                                                value = self.create_maker(value)
                                            if type(value) is list: 
                                                new_val.append(value[0])
                                            else:
                                                new_val.append(value)
                else:
                    for val in field_value:
                        if val[choice] != "" and val[choice] != None and val[choice] != " ":
                            if restriction != None:
                                if val[choice] != restriction:
                                    if choice == "name" and name not in ['exhibitions_exhibition','identification_objectName_objectname']:
                                        new_val.append(self.create_maker(val[choice]))
                                    else:
                                        
                                        if type(val[choice]) is list: 
                                            if val[choice]:
                                                new_val.append(val[choice][0])
                                        else:
                                            new_val.append(val[choice])
                            else:
                                if choice in ["name", "author"] and name not in ['exhibitions_exhibition','identification_objectName_objectname']:
                                    new_val.append(self.create_maker(val[choice]))
                                else:
                                    if type(val[choice]) is list: 
                                        if val[choice]:
                                            new_val.append(val[choice][0])
                                    else:
                                        new_val.append(val[choice])

                if len(new_val) > 0:
                    if name in ["exhibitions_exhibition", "productionDating_production", "labels", "seriesNotesISBN_notes_bibliographicalNotes",
                                "abstractAndSubjectTerms_notes", "abstractAndSubjectTerms_abstract_abstract",
                                "exhibitionsAuctionsCollections_exhibition", "exhibitionsAuctionsCollections_auction",
                                "exhibitionsAuctionsCollections_collection"]:
                        return '<p>'.join(new_val)
                    else:
                        for index, single_value in enumerate(new_val):
                            single_value = "<a href='/%s/search?SearchableText=%s'>%s</a>" %(self.context.language, single_value, single_value)
                            new_val[index] = single_value
                        return ', '.join(new_val)
                else:
                    return ""
            else:
                return field_value
        except:
            return ""


    def generate_identification_tab(self, identification_tab, object_schema, fields, object, field_schema):
        for field, choice in identification_tab:
            # Title field
            if field in ['title']:
                value = getattr(object, field, "")
                if value != "" and value != None and value != " ":
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Title')), "value": value})

            elif field in ['text']:
                val = getattr(object, field, "")
                if val:
                    value = val.output
                else:
                    value = ""
                if value != "" and value != None and value != " ":
                    object_schema[field_schema]['fields'].append({"title": "body", "value": value})
            
            # Regular fields
            elif field not in ['identification_taxonomy']:
                fieldvalue = self.get_field_from_schema(field, fields)
                if fieldvalue != None:
                    title = fieldvalue.title
                    value = self.get_field_from_object(field, object)

                    schema_value = self.transform_schema_field(field, value, choice)

                    if schema_value != "" and schema_value != " ":
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})

            # Taxonomy special case
            else:
                taxonomy = self.get_field_from_object(field, object)
                if len(taxonomy) > 0:
                    scientific_names = []
                    common_names_list = []

                    for taxonomy_elem in taxonomy:
                        scientific_name = taxonomy_elem['scientific_name']
                        if scientific_name:
                            tax = scientific_name[0]
                            tax_obj = None
                            if IRelationValue.providedBy(tax):
                                tax_obj = tax.to_object
                            else:
                                tax_obj = tax

                            if tax_obj:
                                tax_title = getattr(tax_obj, 'title', '')
                                if tax_title:
                                    scientific_names.append(tax_title)

                                common_name = getattr(tax_obj, 'taxonomicTermDetails_commonName', '')
                                if common_name:
                                    common_names = []
                                    for line in common_name:
                                        if line['commonName'] not in [None, '', ' ']:
                                            common_names.append(line['commonName'])

                                    common_names_list.extend(common_names)
                    
                    if scientific_names:     
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Scient. name')), "value": ', '.join(scientific_names)})
                    
                    if common_names_list:
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Common name')), "value": ', '.join(common_names_list)})


    def create_maker(self, name, url=False):
        maker = []
        name_split = name.split(",")

        if len(name_split) > 0:
            if len(name_split) > 1:
                maker.append(name_split[-1])
                maker.append(name_split[0])
            else:
                maker.append(name_split[0])

        new_maker = ' '.join(maker)
        if url:
            #language = self.context.language
            #new_maker = "<a href='%s'>%s</a>" %(url, new_maker)
            new_maker = new_maker
            #new_maker = "<a href='/%s/search?SearchableText=%s'>%s</a>" %(language, new_maker, new_maker)

        return new_maker

    def create_production_field(self, field, url=False):
        production = ""

        maker = field['maker']
        qualifier = field['qualifier']
        role = field['role']
        place = field['place']

        production = self.create_maker(maker, url)

        if qualifier not in NOT_ALLOWED:
            if production:
                production = "%s, %s" %(qualifier, production)
            else:
                production = "%s" %(qualifier)

        if role not in NOT_ALLOWED:
            if production:
                production = "(%s) %s" %(role, production)
            else:
                production = "(%s)" %(role)

        if place not in NOT_ALLOWED:
            if production:
                production = "%s, %s" %(production, place)
            else:
                production = "%s" %(place)

        return production

    def create_period_field(self, field):
        period = field['period']
        start_date = field['date_early']
        start_date_precision = field['date_early_precision']
        end_date = field['date_late']
        end_date_precision = field['date_late_precision']

        result = ""

        if period != "" and period != None and period != " ":
            result = "%s" %(period)

        if start_date != "" and start_date != " ":
            if result:
                if start_date_precision != "" and start_date_precision != " ":
                    result = "%s, %s %s" %(result, start_date_precision, start_date)
                else:
                    result = "%s, %s" %(result, start_date)
            else:
                if start_date_precision != "" and start_date_precision != " ":
                    result = "%s %s" %(start_date_precision, start_date)
                else:
                    result = "%s" %(start_date)
    

        if end_date != "" and end_date != " ":
            if result:
                if end_date_precision != "" and end_date_precision != " ":
                    result = "%s - %s %s" %(result, end_date_precision, start_date)
                else:
                    result = "%s - %s" %(result, end_date)
            else:
                if end_date_precision != "" and end_date_precision != " ":
                    result = "%s %s" %(end_date_precision, start_date)
                else:
                    result = "%s" %(end_date)

        return result

    def get_url_by_uid(self, uid):
        brains = uuidToCatalogBrain(uid)
        if brains:
            return brains.getURL()

        return ""


    def generate_production_dating(self, production_dating_tab, object_schema, fields, object, field_schema):
        production_field = self.get_field_from_object('productionDating_productionDating', object)

        production_result = []
        # Generate production
        url = ""
        for field in production_field:
            production = {}
            if field['makers']:
                production['maker'] = field["makers"][0].title
                url = self.get_url_by_uid(field["makers"][0].UID())
            else:
                production['maker'] = ""

            production['qualifier'] = field['qualifier']

            if field['role']:
                production['role'] = field['role'][0]
            else:
                production['role'] = ""

            if field['place']:
                production['place'] = field['place'][0]
            else:
                production['place'] = ""

            result = self.create_production_field(production, url)
            if result not in NOT_ALLOWED:
                production_result.append(result)

        if len(production_result) > 0:
            production_value = '<p>'.join(production_result)
            object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Maker')), "value": production_value})

        ## Generate Period
        period_field = self.get_field_from_object('productionDating_dating_period', object)

        period = []
        for field in period_field:
            result = self.create_period_field(field)
            if result not in NOT_ALLOWED:
                period.append(result)

        if len(period) > 0:
            period_value = ', '.join(period)
            object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Period')), "value": period_value})

    def generate_production_dating_tab(self, production_dating_tab, object_schema, fields, object, field_schema):

        ## Generate Author
        production_field = self.get_field_from_object('productionDating_production', object)
        production = []
        for field in production_field:
            result = self.create_production_field(field)
            if result not in NOT_ALLOWED:
                production.append(result)

        if len(production) > 0:
            production_value = '<p>'.join(production)
            object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Maker')), "value": production_value})

        ## Generate Period
        period_field = self.get_field_from_object('productionDating_dating_period', object)

        period = []
        for field in period_field:
            result = self.create_period_field(field)
            if result not in NOT_ALLOWED:
                period.append(result)

        if len(period) > 0:
            period_value = ', '.join(period)
            object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Period')), "value": period_value})

    def create_dimension_field(self, field):
        new_dimension_val = []
        dimension_result = ""

        for val in field:
            dimension = ""
            if val['value'] != "":
                dimension = "%s" %(val['value'])
            if val['units'] != "":
                dimension = "%s %s" %(dimension, val['units'])
            if val['dimension'] != "" and val['dimension'] != []:
                dimension = "%s: %s" %(val['dimension'][0], dimension)

            new_dimension_val.append(dimension)

        dimension_result = '<p>'.join(new_dimension_val)
        
        return dimension_result

    def generate_physical_characteristics_tab(self, physical_characteristics_tab, object_schema, fields, object, field_schema):
        
        for field, choice, restriction in physical_characteristics_tab:
            if field == 'physicalCharacteristics_dimension':
                dimension_field = getattr(object, 'physicalCharacteristics_dimension', None)
                if dimension_field != None:
                    dimension = self.create_dimension_field(dimension_field)
                    ## add to schema
                    if dimension != "" and dimension != None:
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Dimensions')), "value": dimension})
            else:
                fieldvalue = self.get_field_from_schema(field, fields)
                if fieldvalue != None:
                    title = fieldvalue.title
                    value = self.get_field_from_object(field, object)

                    schema_value = self.transform_schema_field(field, value, choice)

                    if schema_value != "":
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})


    def generate_associations_tab(self, associations_tab, object_schema, fields, object, field_schema):
        for field, choice, restriction in associations_tab:
            if field == "associations_associatedPersonInstitutions":
                fieldvalue = self.get_field_from_schema(field, fields)
                if fieldvalue:
                    title = fieldvalue.title
                    associations_field = self.get_field_from_object('associations_associatedPersonInstitutions', object)

                    result = []
                    for line in associations_field:
                        names = line["names"]
                        if names:
                            name = names[0].title
                            url = self.get_url_by_uid(names[0].UID())
                            new_name = self.create_maker(name, url)
                            result.append(new_name)

                    final_result = "<p>".join(result)
                    if final_result != "":
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": final_result})

            else:
                fieldvalue = self.get_field_from_schema(field, fields)
                if fieldvalue != None:
                    title = fieldvalue.title
                    value = self.get_field_from_object(field, object)

                    schema_value = self.transform_schema_field(field, value, choice)

                    if schema_value != "":
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})
    
    def generate_reproductions_tab(self, reproductions_tab, object_schema, fields, object, field_schema):
        for field, choice, restriction in reproductions_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice)

                if schema_value != "":
                    if field == "reproductions_reproduction":
                        title = "Reference"
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})    

    def generate_recommendations_tab(self, recommendations_tab, object_schema, fields, object, field_schema):
        for field, choice, restriction in recommendations_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice)

                if schema_value != "":
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})     

    def generate_location_tab(self, location_tab, object_schema, fields, object, field_schema):
        for field, choice, restriction in location_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice)

                if schema_value != "":
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})


    def generate_fieldcollection_tab(self, fieldcollection_tab, object_schema, fields, object, field_schema):
        for field, choice, restriction in fieldcollection_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice)

                if schema_value != "":
                    if field == 'fieldCollection_habitatStratigraphy_stratigraphy':
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory('Geologisch tijdvak')), "value": schema_value})
                    else:
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})


    def generate_exhibitions_tab_temp(self, exhibitions_tab, object_schema, fields, object, field_schema):
        for field, choice, restriction, not_show in exhibitions_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice, restriction, not_show)

                if schema_value != "":
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})

    def generate_exhibition_tab(self, exhibitions_tab, object_schema, fields, object, field_schema):

        relations = []
        related_exhibitions = []

        def get_url_by_uid(context, uid):
            brain = uuidToCatalogBrain(uid)
            if brain:
                return brain.getURL()

            return ""

        for field, choice, restriction, not_show in exhibitions_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)
                if value:
                    for val in value:
                        exhibition = val['exhibitionName']
                        if exhibition:
                            rel = exhibition[0]
                            rel_obj = None
                            if IRelationValue.providedBy(rel):
                                rel_obj = rel.to_object
                            else:
                                rel_obj = rel

                            if rel_obj:
                                rel_url = get_url_by_uid(self.context, rel_obj.UID())
                                rel_title = rel_obj.title
                                related_exhibitions.append("<a href='%s'>%s</a>"%(rel_url, rel_title))

                                rel_date_start = ""
                                rel_date_end = ""
                                if hasattr(rel_obj, 'start_date'):
                                    rel_date_start = rel_obj.start_date

                                if hasattr(rel_obj, 'end_date'):
                                    rel_date_end = rel_obj.end_date

                                if rel_date_start != "":
                                    try:
                                        date_start = rel_date_start.strftime('%Y-%m-%d')
                                    except:
                                        rel_date_start = ""

                                if rel_date_end != "":
                                    try:
                                        date_end = rel_date_end.strftime('%Y-%m-%d')
                                    except:
                                        rel_date_end = ""


                                final_date = ""
                                if rel_date_start != "" and rel_date_end != "":
                                    final_date = "%s t/m %s" %(date_start, date_end)

                                if final_date != "":
                                    related_exhibitions.append(final_date)

                                # organisator
                                orgs = []
                                locations = []
                                places = []
                                """organisators = rel_obj.exhibitionsDetails_organizingInstitutions

                                if organisators:
                                    for organiser in organisators:
                                        try:
                                            name = organiser['name']
                                            if name:
                                                if name != 'Zeeuws Museum':
                                                    orgs.append(name)
                                        except:
                                            pass

                                        try:
                                            l = organiser['address']
                                            if l:
                                                if l != 'Zeeuws Museum':
                                                    locations.append(l)

                                            p = organiser['place']
                                            if p:
                                                if p != 'Zeeuws Museum':
                                                    places.append(p)
                                        except:
                                            pass

                                    final_orgs = ', '.join(orgs)
                                    if final_orgs:
                                        related_exhibitions.append(final_orgs)
                                    
                                    final_locations = ', '.join(locations)
                                    if final_locations:
                                        related_exhibitions.append(final_locations)

                                    final_places = ', '.join(places)
                                    if final_places:
                                        related_exhibitions.append(final_places)"""

        if len(related_exhibitions) > 0:
            related_exhibitions_value = '<p>'.join(related_exhibitions)
            object_schema[field_schema]['fields'].append({'title': self.context.translate(MessageFactory('Exhibition name')), 'value': related_exhibitions_value})


    def generate_exhibitions_tab(self, exhibitions_tab, object_schema, fields, object, field_schema):
        relations = getattr(object, 'exhibitions_exhibition', None)

        if relations:
            related_exhibitions = []
            for rel in relations:
                rel_obj = None
                if IRelationValue.providedBy(rel):
                    rel_obj = rel.to_object
                else:
                    rel_obj = rel

                rel_url = rel_obj.absolute_url()
                rel_title = rel_obj.title
                related_exhibitions.append("<a href='%s'>%s</a>"%(rel_url, rel_title))

                rel_date_start = ""
                rel_date_end = ""
                if hasattr(rel_obj, 'start_date'):
                    rel_date_start = rel_obj.start_date

                if hasattr(rel_obj, 'end_date'):
                    rel_date_end = rel_obj.end_date

                if rel_date_start != "":
                    date_start = rel_date_start.strftime('%Y-%m-%d')

                if rel_date_end != "":
                    date_end = rel_date_start.strftime('%Y-%m-%d')

                final_date = ""
                if rel_date_start != "" and rel_date_end != "":
                    final_date = "%s t/m %s" %(date_start, date_end)

                if final_date != "":
                    related_exhibitions.append(final_date)

        if len(related_exhibitions) > 0:
            related_exhibitions_value = '<p>'.join(related_exhibitions)
            object_schema[field_schema]['fields'].append({'title': self.context.translate(MessageFactory('Exhibitions')), 'value': related_exhibitions_value})

    def generate_labels_tab(self, labels_tab, object_schema, fields, object, field_schema):
        for field, choice, restriction in labels_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice, restriction)

                if schema_value != "":
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(MessageFactory(title)), "value": schema_value})

    def generate_related_books_tab(self, object_schema, fields, object, field_schema):
        if checkPermission('cmf.ManagePortal', self.context):
            intids = getUtility(IIntIds)
            catalog = getUtility(ICatalog)

            relations = sorted(catalog.findRelations({'to_id': intids.getId(object), 'from_attribute':'relations_relatedMuseumObjects'}))
            related_exhibitions = []
            for rel in relations:
                rel_obj = rel.from_object
                rel_url = rel_obj.absolute_url()
                rel_title = rel_obj.title
                related_exhibitions.append("<a href='%s'>%s</a>"%(rel_url, rel_title))
            
            if len(related_exhibitions) > 0:
                related_exhibitions_value = '<p>'.join(related_exhibitions)
                object_schema[field_schema]['fields'].append({'title': self.context.translate(MessageFactory('Books')), 'value': related_exhibitions_value})


    def generate_documentation_tab(self, object_schema, fields, object, field_schema):
        if hasattr(object, 'documentation_documentation'):
            documentation = object.documentation_documentation
            docs = []

            if documentation:
                for doc in documentation:
                    try:
                        if doc['title'] != "":
                            new_doc = "%s" %(doc['title'])

                            if doc['pageMark'] != "":
                                new_doc = "%s, %s" %(new_doc, doc['pageMark'])

                            if doc['notes'] != "":
                                new_doc = "%s, %s" %(new_doc, doc['notes'])

                            docs.append(new_doc)
                    except:
                        pass

            if len(docs) > 0:
                schema_value = '<p>'.join(docs)
                object_schema[field_schema]['fields'].append({'title': self.context.translate(MessageFactory('Documentation')), 'value': schema_value})


    def get_all_fields_object(self, object):

        object_schema = {}

        object_schema["identification"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Identification"))
        }

        object_schema["production_dating"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Production & Dating"))
        }

        object_schema["physical_characteristics"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Physical Characteristics"))
        }

        object_schema["associations"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Associations"))
        }

        object_schema["reproductions"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Reproductions"))
        }

        object_schema["recommendations_requirements"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Recommendations/requirements"))
        }

        object_schema["location"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Location"))
        }

        object_schema["field_collection"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Field Collection"))
        }

        object_schema["exhibitions"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Exhibitions"))
        }

        object_schema["labels"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Labels"))
        }

        object_schema["books"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Books"))
        }

        object_schema["documentation"] = {
            "fields": [],
            "name": self.context.translate(MessageFactory("Documentation"))
        }


        schema = getUtility(IDexterityFTI, name='Object').lookupSchema()
        fields = getFieldsInOrder(schema)

        identification_tab = [('identification_identification_collections', None), ('identification_identification_objectNumber', None),
                                ('identification_objectName_category', None), ('identification_objectName_objectname', 'name'),
                                ('title', None), ('identification_taxonomy', 'scientific_name'), ('text', None)]

        production_dating_tab = ['productionDating_production', 'productionDating_dating_period']

        physical_characteristics_tab = [('physicalCharacteristics_technique', 'technique', None), ('physicalCharacteristics_material', 'material', None),
                                        ('physicalCharacteristics_dimension', None, None)]

        associations_tab = [('associations_associatedPersonInstitutions', 'names', None), ('associations_associatedSubjects', 'subject', None)]

        reproductions_tab = [('reproductions_reproduction', 'reference', None)]

        recommendations_tab = [('recommendationsRequirements_creditLine_creditLine', None, None)]

        location_tab = [('location_current_location', 'location_type', None)]

        fieldcollection_tab = [('fieldCollection_fieldCollection_places', None, None), ('fieldCollection_habitatStratigraphy_stratigrafie', 'unit', None)]

        exhibitions_tab = [('exhibitions_exhibition', None, 'Zeeuws Museum', ['catObject'])]

        labels_tab = [('labels', 'text', None)]


        ## Identification tab
        try:
            self.generate_identification_tab(identification_tab, object_schema, fields, object, "identification")
        except:
            pass
            
        ## Vervaardiging & Datering tab
        #self.generate_production_dating_tab(production_dating_tab, object_schema, fields, object, "production_dating")
        try:
            self.generate_production_dating(production_dating_tab, object_schema, fields, object, "production_dating")
        except:
            pass
            
        ## Physical Characteristics
        try:
            self.generate_physical_characteristics_tab(physical_characteristics_tab, object_schema, fields, object, "physical_characteristics")
        except:
            pass

        ## Associations
        try:
            self.generate_associations_tab(associations_tab, object_schema, fields, object, "associations")
        except:
            pass
        ## Reproductions
        try:
            self.generate_reproductions_tab(reproductions_tab, object_schema, fields, object, "reproductions")
        except:
            pass
        ## Recommendations
        try:
            self.generate_recommendations_tab(recommendations_tab, object_schema, fields, object, "recommendations_requirements")
        except:
            pass
        ## Location
        try:
            self.generate_location_tab(location_tab, object_schema, fields, object, "location")
        except:
            pass
        ## Field collection
        try:
            self.generate_fieldcollection_tab(fieldcollection_tab, object_schema, fields, object, "field_collection")
        except:
            pass
        ## Exhibtions
        #self.generate_exhibitions_tab(exhibitions_tab, object_schema, fields, object, "exhibitions")
        try:
            self.generate_exhibition_tab(exhibitions_tab, object_schema, fields, object, "exhibitions")
        except:
            pass

        ## Labels
        try:
            self.generate_labels_tab(labels_tab, object_schema, fields, object, "labels")
        except:
            pass

        ## Books
        try:
            self.generate_related_books_tab(object_schema, fields, object, "books")
        except:
            pass

        ## Documentation
        try:
            self.generate_documentation_tab(object_schema, fields, object, "documentation")
        except:
            pass

        new_object_schema = []
        new_object_schema.append(object_schema['identification'])
        new_object_schema.append(object_schema['production_dating'])
        new_object_schema.append(object_schema['physical_characteristics'])
        new_object_schema.append(object_schema['associations'])
        new_object_schema.append(object_schema['reproductions'])
        new_object_schema.append(object_schema['recommendations_requirements'])
        new_object_schema.append(object_schema['location'])
        new_object_schema.append(object_schema['field_collection'])
        new_object_schema.append(object_schema['exhibitions'])
        new_object_schema.append(object_schema['labels'])
        new_object_schema.append(object_schema['books'])
        new_object_schema.append(object_schema['documentation'])

        return new_object_schema

    # Get related exhibtions objects
    def generate_related_exhibitions_objects(self, tab, object_schema, fields, object, field_schema):
        for field, choice in tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                related_objects = self.get_field_from_object(field, object)
                if len(related_objects) > 0:
                    temp_schema = []

                    for rel in related_objects:
                        rel_object = rel.to_object
                        temp_schema.append("<a href='%s'>%s</a>" %(rel_object.absolute_url(), rel_object.title))

                    if len(temp_schema) > 0:
                        title = fieldvalue.title
                        new_schema = {"title": self.context.translate(_book(title)), "value": "<p>".join(temp_schema)}
                        object_schema[field_schema]['fields'].append(new_schema)

    def generate_related_museum_objects(self, tab, object_schema, fields, object, field_schema):
        for field, choice in tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                related_objects = self.get_field_from_object(field, object)
                if len(related_objects) > 0:
                    temp_schema = []

                    for rel in related_objects:
                        rel_object = rel.to_object
                        temp_schema.append("<a href='%s'>%s</a>" %(rel_object.absolute_url(), rel_object.title))

                    if len(temp_schema) > 0:
                        title = fieldvalue.title
                        new_schema = {"title": self.context.translate(_book(title)), "value": "<p>".join(temp_schema)}
                        object_schema[field_schema]['fields'].append(new_schema)
                     

    def generate_regular_tab(self, tab, object_schema, fields, object, field_schema):
        for field, choice in tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice)

                if schema_value != "":
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(_book(title)), "value": schema_value})

    def generate_series_isbn_tab(self, identification_tab, object_schema, fields, object, field_schema):
        for field, choice in identification_tab:
            fieldvalue = self.get_field_from_schema(field, fields)
            if fieldvalue != None:
                title = fieldvalue.title
                value = self.get_field_from_object(field, object)

                schema_value = self.transform_schema_field(field, value, choice)

                if schema_value != "":
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(_book(title)), "value": schema_value})

    def generate_title_author_tab(self, identification_tab, object_schema, fields, object, field_schema):
        for field, choice in identification_tab:
            # Title field
            if field in ['title']:
                value = getattr(object, field, "")
                if value != "" and value != None:
                    object_schema[field_schema]['fields'].append({"title": self.context.translate(_book('Title')), "value": value})
            
            # Regular fields
            else:
                fieldvalue = self.get_field_from_schema(field, fields)
                if fieldvalue != None:
                    title = fieldvalue.title
                    value = self.get_field_from_object(field, object)

                    schema_value = self.transform_schema_field(field, value, choice)

                    if schema_value != "":
                        object_schema[field_schema]['fields'].append({"title": self.context.translate(_book(title)), "value": schema_value})

    def get_all_fields_book(self, object):

        object_schema = {}

        object_schema["title_author"] = {
            "fields": [],
            "name": self.context.translate(_book("Title, author, imprint, collation"))
        }

        object_schema["series_notes_isbn"] = {
            "fields": [],
            "name": self.context.translate(_book("Series, notes, ISBN"))
        }

        object_schema["abstract_subject_terms"] = {
            "fields": [],
            "name": self.context.translate(_book("Abstract and subject terms"))
        }

        object_schema["reproductions"] = {
            "fields": [],
            "name": self.context.translate(_book("Reproductions"))
        }

        object_schema["exhibitions_auctions_collections"] = {
            "fields": [],
            "name": self.context.translate(_book("Exhibitions, auctions, collections"))
        }

        object_schema["relations"] = {
            "fields": [],
            "name": self.context.translate(_book("Relations"))
        }

        object_schema["free_fields_numbers"] = {
            "fields": [],
            "name": self.context.translate(_book("Free fields and numbers"))
        }

        object_schema["copies_and_shelf_marks"] = {
            "fields": [],
            "name": self.context.translate(_book("Copies and shelf marks"))
        }


        schema = getUtility(IDexterityFTI, name='Book').lookupSchema()
        fields = getFieldsInOrder(schema)

        title_author_tab = [('title', None), ('titleAuthorImprintCollation_titleAuthor_author', 'author'), 
                            ('titleAuthorImprintCollation_titleAuthor_illustrator', 'illustrator'),
                            ('titleAuthorImprintCollation_titleAuthor_statementOfRespsib', None),
                            ('titleAuthorImprintCollation_titleAuthor_corpAuthor', None),
                            ('titleAuthorImprintCollation_edition_edition', None),
                            ('titleAuthorImprintCollation_imprint_place', None),
                            ('titleAuthorImprintCollation_imprint_publisher', None),
                            ('titleAuthorImprintCollation_imprint_year', None),
                            ('titleAuthorImprintCollation_imprint_placePrinted', None)
                            ]

        series_notes_isbn_tab = [('seriesNotesISBN_series_series', 'series'),
                                ('seriesNotesISBN_series_subseries', 'subseries'),
                                ('seriesNotesISBN_notes_bibliographicalNotes', None),
                                ('seriesNotesISBN_ISBN_ISBN', 'ISBN'),
                                ('seriesNotesISBN_ISBN_ISSN', None)]

        abstract_subject_terms_tab = [('abstractAndSubjectTerms_materialType', None),
                                     ('abstractAndSubjectTerms_classNumber', None),
                                     ('abstractAndSubjectTerms_subjectTerm', 'subjectType'),
                                     ('abstractAndSubjectTerms_personKeywordType', 'name'),
                                     ('abstractAndSubjectTerms_geographicalKeyword', None),
                                     ('abstractAndSubjectTerms_period', None),
                                     ('abstractAndSubjectTerms_startDate', None),
                                     ('abstractAndSubjectTerms_endDate', None),
                                     ('abstractAndSubjectTerms_digitalReferences_reference', None),
                                     ('abstractAndSubjectTerms_abstract_abstract', None)]

        reproductions_tab = [('reproductions_reproduction', 'reference', None)]

        exhibitions_tab = []

        free_fields_tab = []

        copies_tab = [('copiesAndShelfMarks_copyDetails', None)]

        museum_objects_tab = [('relations_relatedMuseumObjects', None)]

        related_exhibitions = [('exhibitionsAuctionsCollections_relatedExhibitions', None)]

        ## Identification tab
        self.generate_title_author_tab(title_author_tab, object_schema, fields, object, "title_author")

        ## Series
        self.generate_series_isbn_tab(series_notes_isbn_tab, object_schema, fields, object, "series_notes_isbn")

        ## Abstract
        self.generate_regular_tab(abstract_subject_terms_tab, object_schema, fields, object, "abstract_subject_terms")

        ## Reproductions
        self.generate_reproductions_tab(reproductions_tab, object_schema, fields, object, "reproductions")

        ## !Related exhibitions
        self.generate_related_exhibitions_objects(related_exhibitions, object_schema, fields, object, "exhibitions_auctions_collections")
        
        ## Exhibition
        #self.generate_regular_tab(exhibitions_tab, object_schema, fields, object, "exhibitions_auctions_collections")

        ## Free fields
        self.generate_regular_tab(free_fields_tab, object_schema, fields, object, "free_fields_numbers")

        ## Copies and shelf marks
        self.generate_regular_tab(copies_tab, object_schema, fields, object, "copies_and_shelf_marks")
        
        ## Museum objects
        self.generate_related_museum_objects(museum_objects_tab, object_schema, fields, object, "relations")


        new_object_schema = []
        new_object_schema.append(object_schema['title_author'])
        new_object_schema.append(object_schema['series_notes_isbn'])
        new_object_schema.append(object_schema['abstract_subject_terms'])
        new_object_schema.append(object_schema['reproductions'])
        new_object_schema.append(object_schema['exhibitions_auctions_collections'])
        new_object_schema.append(object_schema['relations'])
        new_object_schema.append(object_schema['free_fields_numbers'])
        new_object_schema.append(object_schema['copies_and_shelf_marks'])

        return new_object_schema


class CollectionSlideshow(BrowserView):
    def getImageObject(self, item):
        if item.portal_type == "Image":
            return item.getObject()

        if item.leadMedia != None:
            uuid = item.leadMedia
            media_object = uuidToObject(uuid)
            if media_object:
                return "%s%s" %(media_object.absolute_url(), "/@@images/image/large")

        return ""

    def get_collection_items(self):
        collection_items = []
        if self.context.portal_type == "Collection":
            collection_obj = self.context
            brains = collection_obj.queryCatalog(batch=False)
            results = list(brains)
            
            for item in results[1:]:
                if item.portal_type == "Link" and item.leadMedia != None:
                    image = self.getImageObject(item)
                    obj_id = obj.getId()
                    obj = item.getObject()
                    data_description = obj.Description()
                    data_title = obj.Title()
                    data_url = obj.absolute_url()

                    collection_items.append({
                        "_id": obj_id,
                        "is_video": True,
                        "remote_url": obj.remoteUrl,
                        "has_overlay": True,
                        "data_description": data_description,
                        "data_title": data_title,
                        "data_url": data_url,
                        "image_path": image
                    });

                elif item.portal_type == "Link" and not item.leadMedia != None:
                    obj = item.getObject()
                    obj_id = obj.getId()
                    data_description = obj.Description()
                    data_title = obj.Title()
                    data_url = obj.absolute_url()
                    collection_items.append({
                        "_id": obj_id,
                        "is_video": True,
                        "remote_url": obj.remoteUrl,
                        "has_overlay": False,
                        "data_description": data_description,
                        "data_title": data_title,
                        "data_url": data_url,
                        "image_path": ""
                    });

                elif item.portal_type == "Object" or item.portal_type == "Event":
                    obj = item.getObject()
                    obj_id = obj.getId()
                    data_description = obj.Description()
                    data_title = obj.Title()
                    data_url = obj.absolute_url()
                    image = self.getImageObject(item)

                    collection_items.append({
                        "_id": obj_id,
                        "is_video": False,
                        "remote_url": "",
                        "has_overlay": False,
                        "data_description": data_description,
                        "data_title": data_title,
                        "data_url": data_url,
                        "image_path": image
                    });

        return json.dumps(collection_items)


