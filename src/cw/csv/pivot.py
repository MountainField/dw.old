# -*- coding: utf-8 -*-

# =================================================================
# Licensed Materials - Property of IBM
#
# (c) Copyright IBM Corp. 2019, 2019 All Rights Reserved
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
# =================================================================

from __future__ import unicode_literals, print_function, absolute_import

from collections import OrderedDict
import logging
import re

import cw
from . import ToTypedCsvCli, gather_values_from_csv_texts

LOGGER = logging.getLogger("cw")


class RowsIteratorGenerator(object):
    
    def __init__(self, rows, f):
        self._rows = rows
        self._f = f
    
    def __iter__(self):
        return iter((row[self._f] for row in self._rows))


################################################################################
# Main
def pivot(input_file="-", output_file="-",
        input_text_encoding=cw.DEFAULT_TEXT_ENCODING, input_text_errors=cw.DEFAULT_TEXT_ERRORS,
        output_text_encoding=cw.DEFAULT_TEXT_ENCODING, output_text_errors=cw.DEFAULT_TEXT_ERRORS,
        input_csv_delimiter=cw.DEFAULT_CSV_DELIMITER, input_csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR,
        output_csv_delimiter=cw.DEFAULT_CSV_DELIMITER, output_csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR, output_csv_quoting=cw.DEFAULT_CSV_QUOTING,
        metadata_file=None,
        key_fieldnames=None, asssignment_formulas=[], before_all_statement=[]):
    
    if not key_fieldnames:
        LOGGER.info("Exit pivot because of no key field name")
        return
    
    key_fieldnames = gather_values_from_csv_texts(key_fieldnames, delimiter=input_csv_delimiter, quotechar=input_csv_quotechar)
    
    fieldname2formula = OrderedDict()
    
    for asssignment_formula in asssignment_formulas:
        m = re.match(r"\s*([^=]+)\s*=\s*(.*)\s*", asssignment_formula)
        if m:
            fieldname = m.group(1)
            value_formula = m.group(2)
            fieldname2formula[fieldname] = value_formula
        else:
            LOGGER.error("Found illeagl asssignment_formula==%s", asssignment_formula)
            raise ValueError("Found illeagl asssignment_formula==%s" % asssignment_formula)
    
    variables = {}
    if before_all_statement:
        exec(before_all_statement, variables)
    
    keys2list = {}
    
    metadata = cw.csv.load_metadata(metadata_file)
    fieldname2deserializer, fieldname2serializer = cw.csv.get_field_types(metadata)

    with cw.csv.open_csv_typed_dict_reader(input_file,
                                text_encoding=input_text_encoding, text_errors=input_text_errors,
                                csv_delimiter=input_csv_delimiter, csv_quotechar=input_csv_quotechar,
                                fieldname2deserializer=fieldname2deserializer) as csv_dict_reader:
        
        for row in csv_dict_reader:
            
            keys = tuple([row.get(k, None) for k in key_fieldnames])  # => (1, 2)
            
            if keys not in keys2list:
                keys2list[keys] = []  # find the first key combination! initialize with empty bin
            keys2list[keys].append(row)
            
        output_fieldnames = list(key_fieldnames)  # make a copy
        output_fieldnames.extend(fieldname2formula.keys())
        LOGGER.debug("Found output_fieldnames==%s", output_fieldnames)
    
    output_rows = []
    for keys, rows in keys2list.items():
        output_row = {}
        
        for key_idx, key_fieldname in enumerate(key_fieldnames) :
            key_value = keys[key_idx]
            output_row[key_fieldname] = key_value
        
        variables["rows"] = rows
        
        for input_fieldname in csv_dict_reader.fieldnames:
            # variables["_" + input_fieldname] = (row[input_fieldname] for row in rows)  # Set generator of iterator
            variables["_" + input_fieldname] = RowsIteratorGenerator(rows, input_fieldname)  # to solve issues #4 and #5
        
        for fieldname, formula in fieldname2formula.items():
            output_row[fieldname] = eval(formula, variables, variables)
        
        output_rows.append(output_row)
    
    with cw.csv.open_csv_typed_dict_writer(output_file, fieldnames=output_fieldnames,
                                text_encoding=output_text_encoding, text_errors=output_text_errors,
                                csv_delimiter=output_csv_delimiter, csv_quotechar=output_csv_quotechar, output_csv_quoting=output_csv_quoting,
                                fieldname2serializer=fieldname2serializer) as csv_dict_writer:
        
        csv_dict_writer.writeheader()
        
        for output_row in output_rows:
            csv_dict_writer.writerow(output_row)


class PivotCli(ToTypedCsvCli):
    
    def __init__(self, name="cw-csv-formula", description="cw-csv-formula", *args, **kwargs):
        
        super(PivotCli, self).__init__(name=name, description=description, *args, **kwargs)

        self.arg_parser.add_argument("--field", metavar="FIELDNAME", nargs="*",
                                dest="key_fieldnames", default=None,
                                help="key field names of pivot table")

        self.arg_parser.add_argument("--formula", metavar="FIELDNAME=PY_FORMULA", nargs="*",
                                dest="asssignment_formulas", default=None,
                                help="formulas to add new fields")

        self.arg_parser.add_argument("--before-all", metavar="PY_STATEMENT", nargs=None,
                                dest="before_all_statement", default=None,
                                help="statements to execute before iterating rows")

    def main(self, input_file="-", output_file="-",
                   input_text_encoding=cw.DEFAULT_TEXT_ENCODING, input_text_errors=cw.DEFAULT_TEXT_ERRORS,
                   output_text_encoding=cw.DEFAULT_TEXT_ENCODING, output_text_errors=cw.DEFAULT_TEXT_ERRORS,
                   input_csv_delimiter=cw.DEFAULT_CSV_DELIMITER, input_csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR,
                   output_csv_delimiter=cw.DEFAULT_CSV_DELIMITER, output_csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR, output_csv_quoting=cw.DEFAULT_CSV_QUOTING,
                   metadata_file=None,
                   key_fieldnames=None, asssignment_formulas=[], before_all_statement=[],
                   log_level=cw.DEFAULT_LOG_LEVEL):
        self.set_log_config(log_level=log_level)
        pivot(input_file=input_file, output_file=output_file,
            input_text_encoding=input_text_encoding, input_text_errors=input_text_errors,
            output_text_encoding=output_text_encoding, output_text_errors=output_text_errors,
            input_csv_delimiter=input_csv_delimiter, input_csv_quotechar=input_csv_quotechar,
            output_csv_delimiter=output_csv_delimiter, output_csv_quotechar=output_csv_quotechar, output_csv_quoting=output_csv_quoting,
            metadata_file=metadata_file,
            key_fieldnames=key_fieldnames, asssignment_formulas=asssignment_formulas, before_all_statement=before_all_statement)
        return 0
