#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

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
    "DS":"productionDating_dating_period-date_early",
    "DE":"productionDating_dating_period-date_late",
    "MA":"physicalCharacteristics_material-material",
    "ST":"location_currentLocation-location"
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

    #
    # Transforms object types: PersonOrInstitution
    # TODO: Transform all other content type
    #
    def transform_object(self, obj, values):
        portal_type = getattr(obj, 'portal_type', None)

        if portal_type:
            if portal_type == "PersonOrInstitution":
                value = getattr(obj, 'title', None)
                if value not in NOT_ALLOWED:
                    values.append(value)
                else:
                    pass
            elif portal_type == "Exhibition":
                value = getattr(obj, 'title', None)
                if value not in NOT_ALLOWED:
                    values.append(value)
                else:
                    pass
            else:
                #TODO: Needs to know how to get values from Exhibitions, loans etc
                self.write_log("Something went wrong. Don't know how to transform type %s" %(portal_type))
                pass
        else:
            pass

    def transform_list(self, fieldvalue):
        DEFAULT_VALUE = ''

        values = []
        for elem in fieldvalue:
            if elem not in NOT_ALLOWED:
                if getattr(elem, 'portal_type', None) != None:
                    self.transform_object(elem, values)
                elif IRelationValue.providedBy(elem):
                    to_object = elem.to_object
                    self.transform_object(to_object, values)
                else:
                    values.append(elem)
        
        finalvalue = ', '.join(values)
        
        if finalvalue not in NOT_ALLOWED:
            return finalvalue
        else:
            #Not valid
            return DEFAULT_VALUE

        return DEFAULT_VALUE

    def transform_string(self, fieldvalue):
        DEFAULT_VALUE = ''
        if fieldvalue not in NOT_ALLOWED:
            return fieldvalue
        else:
            return DEFAULT_VALUE

    def transform_value(self, fieldvalue, fieldname):
        DEFAULT_VALUE = ''

        try:
            if fieldvalue:
                if type(fieldvalue) in [str, unicode]:
                    return self.transform_string(fieldvalue)
                elif type(fieldvalue) is list:
                    return self.transform_list(fieldvalue)
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
        return self.transform_value(fieldvalue, fieldname)

    def get_subfield_from_list(self, field, fieldname, subfieldname):
        values = []
        for subfield in field:
            if subfieldname in subfield:
                field_value = subfield[subfieldname]
                final_value = self.transform_value(field_value, "%s-%s"%(fieldname, subfieldname))
                if final_value:
                    values.append(final_value)
            else:
                self.write_log("[%s-%s] Something went wrong. Subfield is not available. Please check CORE dictionary." %(fieldname, subfieldname))

        finalvalue = ', '.join(values)
        return finalvalue

    def get_subfield(self, obj, fieldname, subfieldname, index):
        DEFAULT_VALUE = ''

        field = getattr(obj, fieldname, None)
        if field:
            return self.get_subfield_from_list(field, fieldname, subfieldname)
        else:
            # Something went wrong
            #TODO: log proper explanation
            return DEFAULT_VALUE

        return DEFAULT_VALUE

