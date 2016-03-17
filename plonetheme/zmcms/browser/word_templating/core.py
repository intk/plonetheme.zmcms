#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from z3c.relationfield.interfaces import IRelationList, IRelationValue

NOT_ALLOWED = ['', ' ', None]

CORE = {
    "IN":"identification_identification_objectNumber",
    "OB":'identification_objectName_objectname-name',
    "TI":"title",
    "BE":"identification_titleDescription_description",
    "VV":"productionDating_productionDating-makers",
    "VP":"productionDating_productionDating-place",
    "TN":"exhibitions_exhibition-exhibitionName",
    "CL":"identification_identification_collections",
    "DS":"productionDating_dating_period",
    #"DE":"productionDating_dating_period-date_late",
    "MA":"physicalCharacteristics_material-material",
    "ST":"location_currentLocation-location"
}

SEPARATORS = {
    "physicalCharacteristics_material": "; "
}

EXPORT_PATH = {
    "prod":"/var/www/zm-templates/exports/%s",
    "dev":"/Users/AG/Projects/collectie-zm/TEMPLATES/%s"
}

TEMPLATE_PATH = {
    "prod":{
        "a":"/var/www/zm-templates/a-template-shortnames.docx",
        "b":"/var/www/zm-templates/b-template-shortnames.docx"
    },
    "dev": {
        "a":"/Users/AG/Projects/DOCXTemplate/test_files/a-template-shortnames.docx",
        "b":"/Users/AG/Projects/DOCXTemplate/test_files/b-template-shortnames.docx"
    }
}

LOG_PATH = {
    "prod":"/var/www/zm-templates/logs/export-templates-log.csv",
    "dev":"/Users/AG/Projects/collectie-zm/TEMPLATES/logs/word_template.csv"
}

class WordGeneratorCore:

    def __init__(self, log_file, env):
        self.log_file = log_file
        self.env = env

        self.special_fields = {
            "DS": self.transform_dating
        }

    ##
    ## Transforms for different portal_types
    ##
    def transform_exhibition(self, obj, values):
        value = getattr(obj, 'title', None)
        if value not in NOT_ALLOWED:
            values.append(value)
        else:
            # Value not valid
            pass

    def transform_person(self, obj, original_obj, index, values):
        value = getattr(obj, 'title', None)
        if value not in NOT_ALLOWED:
            creators = getattr(original_obj, 'productionDating_productionDating', None)
            if creators:
                creator = creators[index]
                qualifier = creator['qualifier']
                if qualifier not in NOT_ALLOWED:
                    value = "%s (%s)" %(value, qualifier)
                else:
                    # Value not valid
                    pass
            else:
                # No value
                pass

            values.append(value)
        else:
            #Value not valid
            pass

    ##
    ## Utils
    ##
    def write_log(self, text):
        timestamp = datetime.datetime.now()

        log_final_text = "[%s]__%s" %(timestamp, text)
        log_final_list = log_final_text.split('__')

        if self.env == 'dev':
            print "[%s] %s" %(timestamp, text)

        self.log_file.writerow(log_final_list)

    def is_repeatable(self, fieldname):
        if len(fieldname.split('-')) > 1:
            return True
        return False

    def get_fields_names(self, fieldname):
        field_name = ''
        subfield_name = ''

        field_parts = fieldname.split('-')
        field_name = field_parts[0]
        subfield_name = field_parts[1]

        return field_name, subfield_name
    
    def create_period_field(self, field):
        period = field['period']
        start_date = field['date_early']
        start_date_precision = field['date_early_precision']
        end_date = field['date_late']
        end_date_precision = field['date_late_precision']

        result = ""

        if period not in  NOT_ALLOWED:
            result = "%s" %(period)

        if start_date not in NOT_ALLOWED:
            if result:
                if start_date_precision not in NOT_ALLOWED:
                    result = "%s, %s %s" %(result, start_date_precision, start_date)
                else:
                    result = "%s, %s" %(result, start_date)
            else:
                if start_date_precision not in NOT_ALLOWED:
                    result = "%s %s" %(start_date_precision, start_date)
                else:
                    result = "%s" %(start_date)
    

        if end_date not in NOT_ALLOWED:
            if result:
                if end_date_precision not in NOT_ALLOWED:
                    result = "%s - %s %s" %(result, end_date_precision, start_date)
                else:
                    result = "%s - %s" %(result, end_date)
            else:
                if end_date_precision not in NOT_ALLOWED:
                    result = "%s %s" %(end_date_precision, start_date)
                else:
                    result = "%s" %(end_date)

        return result

    #
    # Transforms object types: PersonOrInstitution
    # TODO: Transform all other content type
    #

    def transform_dating(self, key, value, obj):
        DEFAULT_VALUE = ''
        
        dating_field = getattr(obj, value, None)
        if dating_field:
            items = []
            for elem in dating_field:
                elem_value = self.create_period_field(elem)
                if elem_value not in NOT_ALLOWED:
                    items.append(elem_value)

            final_value = ', '.join(items)
            return final_value
        else:
            return DEFAULT_VALUE
        return DEFAULT_VALUE

    def transform_object(self, obj, values, original_obj, index):
        portal_type = getattr(obj, 'portal_type', None)

        if portal_type:
            if portal_type == "PersonOrInstitution":
                self.transform_person(obj, original_obj, index, values)

            elif portal_type == "Exhibition":
                self.transform_exhibition(obj, values)
            else:
                #TODO: Needs to know how to get values from Exhibitions, loans etc
                self.write_log("Something went wrong. Don't know how to transform type %s" %(portal_type))
                pass
        else:
            #TODO log proper explanation
            pass

    def transform_list(self, fieldvalue, fieldname, original_obj):
        DEFAULT_VALUE = ''

        values = []
        for index, elem in enumerate(fieldvalue):
            if elem not in NOT_ALLOWED:
                if getattr(elem, 'portal_type', None) != None:
                    self.transform_object(elem, values, original_obj, index)
                elif IRelationValue.providedBy(elem):
                    to_object = elem.to_object
                    self.transform_object(to_object, values, original_obj, index)
                else:
                    values.append(elem)
        
        if fieldname in SEPARATORS:
            finalvalue = SEPARATORS[fieldname].join(values)
        else:
            finalvalue = ', '.join(values)
        
        if finalvalue not in NOT_ALLOWED:
            return finalvalue
        else:
            #Not valid
            return DEFAULT_VALUE

        return DEFAULT_VALUE

    def transform_string(self, fieldvalue, original_obj):
        DEFAULT_VALUE = ''
        if fieldvalue not in NOT_ALLOWED:
            return fieldvalue
        else:
            return DEFAULT_VALUE

    def transform_value(self, fieldvalue, fieldname, original_obj):
        DEFAULT_VALUE = ''

        try:
            if fieldvalue:
                if type(fieldvalue) in [str, unicode]:
                    return self.transform_string(fieldvalue, original_obj)
                elif type(fieldvalue) is list:
                    return self.transform_list(fieldvalue, fieldname, original_obj)
                else:
                    self.write_log("[%s] Something went wrong while getting field value to export. Don't know how to transform field %s." %(fieldname, type(fieldvalue)))
                    return DEFAULT_VALUE
            else:
                return DEFAULT_VALUE
        except:
            self.write_log("[%s] Something went wrong while getting field value to export. Please check CORE dictionary for mistakes." %(fieldname))
            raise
            return DEFAULT_VALUE

    def get_field(self, obj, fieldname):
        fieldvalue = getattr(obj, fieldname, None)
        return self.transform_value(fieldvalue, fieldname, obj)

    def get_subfield_from_list(self, field, fieldname, subfieldname, original_obj):
        values = []
        for subfield in field:
            if subfieldname in subfield:
                field_value = subfield[subfieldname]
                final_value = self.transform_value(field_value, "%s-%s"%(fieldname, subfieldname), original_obj)
                if final_value:
                    values.append(final_value)
            else:
                self.write_log("[%s-%s] Something went wrong. Subfield is not available. Please check CORE dictionary." %(fieldname, subfieldname))

        if fieldname in SEPARATORS:
            finalvalue = SEPARATORS[fieldname].join(values)
        else:
            finalvalue = ', '.join(values)

        return finalvalue

    def get_subfield(self, obj, fieldname, subfieldname, index):
        DEFAULT_VALUE = ''

        field = getattr(obj, fieldname, None)
        if field:
            return self.get_subfield_from_list(field, fieldname, subfieldname, obj)
        else:
            # Something went wrong
            #TODO: log proper explanation
            return DEFAULT_VALUE

        return DEFAULT_VALUE

    def transform_field(self, key, value, item, obj):
        if key in self.special_fields:
            value = self.special_fields[key](key, value, obj)
            item[key] = value
        else:
            repeatable = self.is_repeatable(value)
            if repeatable:
                fieldname, subfieldname = self.get_fields_names(value)
                field_value = self.get_subfield(obj, fieldname, subfieldname, 0)
                item[key] = field_value
            else:
                field_value = self.get_field(obj, value)
                item[key] = field_value






