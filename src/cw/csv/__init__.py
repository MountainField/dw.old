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

from abc import ABCMeta
import argparse
import csv as builtincsv
import datetime
import errno
import io
import json
import logging
import os
import sys
import textwrap

builtincsv.field_size_limit(sys.maxsize)

import cw

LOGGER = logging.getLogger("cw")


class Closeable(object):

    def __init__(self, f, close_io_obj=True):
        self._f = f
        self.close_io_obj = close_io_obj
        if close_io_obj:
            if self._f:
                if self._f is sys.stdin or self._f is sys.stdout:
                # or self._f is sys.stdin.buffer or self._f is sys.stdout.buffer:
                    LOGGER.debug("Overwrite from close_io_obj=True to False because io_obj is stdio")
                    self.close_io_obj = False                

    def close(self):
        if self.close_io_obj:
            LOGGER.debug("Closing %s", self._f)
            self._f.close()

    # with statement
    def __enter__(self, *args, **kwargs):
        return self
 
    def __exit__(self, *args, **kwargs):
        if hasattr(self._f, 'flush'):
            return self._f.flush()
        return self.close()


if sys.version_info[0] >= 3:

    class CloseableCsvReader(Closeable):
    
        def __init__(self, f, close_io_obj=True, *args, **kwargs):
            LOGGER.debug("Initializing CloseableCsvReader with f=%s, close_io_obj=%s, *args=%s, **kwargs=%s", f, close_io_obj, args, kwargs)
            
            self.csv_reader = builtincsv.reader(f, *args, **kwargs)
            Closeable.__init__(self, f, close_io_obj)
        
        def __next__(self):
            return next(self.csv_reader)

        next = __next__
        
        def __iter__(self):
            return self

    class CloseableCsvDictReader(builtincsv.DictReader, Closeable):
    
        def __init__(self, f, close_io_obj=True, *args, **kwargs):
            LOGGER.debug("Initializing CloseableCsvDictReader with f=%s, close_io_obj=%s, *args=%s, **kwargs=%s", f, close_io_obj, args, kwargs)
            super(CloseableCsvDictReader, self).__init__(f, *args, **kwargs)
            Closeable.__init__(self, f, close_io_obj)

    class CloseableCsvWriter(Closeable):
    
        def __init__(self, f, close_io_obj=True, *args, **kwargs):
            LOGGER.debug("Initializing CloseableCsvWriter with f=%s, close_io_obj=%s, *args=%s, **kwargs=%s", f, close_io_obj, args, kwargs)
            self.csv_writer = builtincsv.writer(f, *args, **kwargs)
            Closeable.__init__(self, f, close_io_obj)
        
        def writerow(self, row):
            self.csv_writer.writerow(row)
        
        def writerows(self, rows):
            for row in rows:
                self.writerow(row)
    
    class CloseableCsvDictWriter(builtincsv.DictWriter, Closeable):
    
        def __init__(self, f, fieldnames, close_io_obj=True, *args, **kwargs):
            LOGGER.debug("Initializing CloseableCsvDictWriter with f=%s, fieldnames=%s, close_io_obj=%s, *args=%s, **kwargs=%s", f, fieldnames, close_io_obj, args, kwargs)
            super(CloseableCsvDictWriter, self).__init__(f, fieldnames, *args, **kwargs)
            Closeable.__init__(self, f, close_io_obj)
    
    def opencsv_reader(input_file,
                        text_encoding=cw.DEFAULT_TEXT_ENCODING, text_errors=cw.DEFAULT_TEXT_ERRORS,
                        csv_delimiter=cw.DEFAULT_CSV_DELIMITER, csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR):
        text_reader = cw.text.open_text_reader(input_file, text_encoding=text_encoding, text_errors=text_errors)  # TODO: new line はちゃんと考える
        csv_reader = CloseableCsvReader(text_reader, delimiter=csv_delimiter, quotechar=csv_quotechar)
        return csv_reader

    def opencsv_dict_reader(input_file,
                             text_encoding=cw.DEFAULT_TEXT_ENCODING, text_errors=cw.DEFAULT_TEXT_ERRORS,
                             csv_delimiter=cw.DEFAULT_CSV_DELIMITER, csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR):
        text_reader = cw.text.open_text_reader(input_file, text_encoding=text_encoding, text_errors=text_errors)  # TODO: new line はちゃんと考える
        csv_dict_reader = CloseableCsvDictReader(text_reader, delimiter=csv_delimiter, quotechar=csv_quotechar)
        return csv_dict_reader
    
    def opencsv_writer(output_file,
                        text_encoding=cw.DEFAULT_TEXT_ENCODING, text_errors=cw.DEFAULT_TEXT_ERRORS,
                        csv_delimiter=cw.DEFAULT_CSV_DELIMITER, csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR, output_csv_quoting=cw.DEFAULT_CSV_QUOTING):
        text_writer = cw.text.open_text_writer(output_file, text_encoding=text_encoding, text_errors=text_errors)  # TODO: new line はちゃんと考える
        quoting = getattr(builtincsv, "QUOTE_" + output_csv_quoting.upper(), builtincsv.QUOTE_MINIMAL)
        csv_writer = CloseableCsvWriter(text_writer,
                                        delimiter=csv_delimiter, quotechar=csv_quotechar, quoting=quoting)
        return csv_writer

    def opencsv_dict_writer(output_file,
                             fieldnames,
                             text_encoding=cw.DEFAULT_TEXT_ENCODING, text_errors=cw.DEFAULT_TEXT_ERRORS,
                             csv_delimiter=cw.DEFAULT_CSV_DELIMITER, csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR, output_csv_quoting=cw.DEFAULT_CSV_QUOTING):
        text_writer = cw.text.open_text_writer(output_file, text_encoding=text_encoding, text_errors=text_errors)  # TODO: new line はちゃんと考える
        quoting = getattr(builtincsv, "QUOTE_" + output_csv_quoting.upper(), builtincsv.QUOTE_MINIMAL)
        csv_dict_writer = CloseableCsvDictWriter(text_writer, fieldnames, delimiter=csv_delimiter, quotechar=csv_quotechar, quoting=quoting)
        return csv_dict_writer


def gather_values_from_csv_texts(csv_texts, delimiter=cw.DEFAULT_CSV_DELIMITER, quotechar=cw.DEFAULT_CSV_QUOTECHAR):
    values = []
    for csv_text in csv_texts:
        csv_reader = CloseableCsvReader(io.StringIO(csv_text), delimiter=delimiter, quotechar=quotechar)
        for row in csv_reader:
            values.extend(row)
    return values

####################################################
# see https://libguides.library.kent.edu/SPSS/DefineVariables


def load_metadata(metadata_file):
    metadata = {}
    if metadata_file:
        if os.path.exists(metadata_file):
            with io.open(metadata_file, "rt", encoding=cw.DEFAULT_TEXT_ENCODING, errors=cw.DEFAULT_TEXT_ERRORS) as f:
                metadata = json.load(f)
    return metadata


def get_field_types(metadata={}):
    fieldname2deserializer = {}
    fieldname2serializer = {}

    if "fields" in metadata:
        fieldname2info = metadata["fields"]
        for fieldname, info in fieldname2info.items():
            storage_type = info.get("type")
            if storage_type is None or storage_type == "str" or storage_type == "string":
                pass
            elif storage_type == "int" or storage_type == "integer":
                # set default serializer deserializer
                fieldname2serializer[fieldname] = lambda v: str(v)
                fieldname2deserializer[fieldname] = lambda v: int(v, base=0)  # => automatic type detection is enabled.
                
                if "format" in info:
                    integer_format = info["format"]
                    if integer_format == "hex":
                        fieldname2serializer[fieldname] = lambda v: hex(v)  # => 17 -> "0x11"
                        fieldname2deserializer[fieldname] = lambda v: int(v, base=16)  # => "0x11" -> 17
                    elif integer_format == "oct":
                        fieldname2serializer[fieldname] = lambda v: oct(v)  # => 9 -> "0o11"
                        fieldname2deserializer[fieldname] = lambda v: int(v, base=8)  # => "0o11" -> 9
                    elif integer_format == "bin":
                        fieldname2serializer[fieldname] = lambda v: bin(v)  # => 3 -> "0o11"
                        fieldname2deserializer[fieldname] = lambda v: int(v, base=2)  # => "0o11" -> 3
                    else:
                        raise ValueError("Unknown format==%s for type==integer" % integer_format)
            elif storage_type == "number" or storage_type == "float":
                fieldname2deserializer[fieldname] = float  # set function pointer of int(str)
            elif storage_type == "datetime":
                if "format" in info:
                    datetime_format = info["format"]
                    fieldname2deserializer[fieldname] = lambda v: datetime.datetime.strptime(v, datetime_format)
                    fieldname2serializer[fieldname] = lambda v: datetime.datetime.strftime(v, datetime_format)
                else:
                    raise ValueError("format is required to storage_type datetime")
            else:
                raise ValueError("unknown storage_type==%s" % storage_type)

    return fieldname2deserializer, fieldname2serializer


class CloseableCsvTypedDictReader(Closeable):

    def __init__(self, closeable_csv_dict_reader, fieldname2deserializer={}, close_io_obj=True):
        if closeable_csv_dict_reader is None:
            raise ValueError("closeable_csv_dict_reader is None")
        LOGGER.debug("Initializing CloseableCsvTypedDictReader with closeable_csv_dict_reader=%s, close_io_obj=%s", closeable_csv_dict_reader, close_io_obj)
        self.closeable_csv_dict_reader = closeable_csv_dict_reader
        self.fieldname2deserializer = fieldname2deserializer
        Closeable.__init__(self, closeable_csv_dict_reader, close_io_obj)
    
    @property
    def fieldnames(self):
        return self.closeable_csv_dict_reader.fieldnames
    
    def __next__(self):
        row = next(self.closeable_csv_dict_reader)
        if self.fieldname2deserializer:  # not empty
            for fieldname in self.fieldname2deserializer.keys():
                if fieldname in row and row[fieldname]:  # not empty
                    deserializer = self.fieldname2deserializer[fieldname]
                    row[fieldname] = deserializer(row[fieldname])
        return row
    
    next = __next__
    
    def __iter__(self):
        return self

    
class CloseableCsvTypedDictWriter(Closeable):

    def __init__(self, closeable_csv_dict_writer, fieldname2serializer={}, close_io_obj=True):
        if closeable_csv_dict_writer is None:
            raise ValueError("closeable_csv_dict_reader is None")
        LOGGER.debug("Initializing CloseableCsvTypedDictReader with closeable_csv_dict_writer=%s, fieldname2serializer=%s, close_io_obj=%s", closeable_csv_dict_writer, fieldname2serializer, close_io_obj)
        self.closeable_csv_dict_writer = closeable_csv_dict_writer
        self.fieldname2serializer = fieldname2serializer
        Closeable.__init__(self, closeable_csv_dict_writer, close_io_obj)
    
    def writeheader(self):
        self.closeable_csv_dict_writer.writeheader()
    
    def writerow(self, row):
        if self.fieldname2serializer:  # not empty
            for fieldname in self.fieldname2serializer.keys():
                if fieldname in row:
                    serializer = self.fieldname2serializer[fieldname]
                    row[fieldname] = serializer(row[fieldname])
        self.closeable_csv_dict_writer.writerow(row)
    
    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def open_csv_typed_dict_reader(input_file,
                               text_encoding=cw.DEFAULT_TEXT_ENCODING, text_errors=cw.DEFAULT_TEXT_ERRORS,
                               csv_delimiter=cw.DEFAULT_CSV_DELIMITER, csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR,
                               fieldname2deserializer={}):
    text_reader = cw.text.open_text_reader(input_file, text_encoding=text_encoding, text_errors=text_errors)  # TODO: new line はちゃんと考える
    csv_dict_reader = CloseableCsvDictReader(text_reader, delimiter=csv_delimiter, quotechar=csv_quotechar)
    csv_typed_dict_reader = CloseableCsvTypedDictReader(csv_dict_reader, fieldname2deserializer)
    return csv_typed_dict_reader


def open_csv_typed_dict_writer(output_file,
                              fieldnames,
                              text_encoding=cw.DEFAULT_TEXT_ENCODING, text_errors=cw.DEFAULT_TEXT_ERRORS,
                              csv_delimiter=cw.DEFAULT_CSV_DELIMITER, csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR, output_csv_quoting=cw.DEFAULT_CSV_QUOTING,
                              fieldname2serializer={}):
    text_writer = cw.text.open_text_writer(output_file, text_encoding=text_encoding, text_errors=text_errors)  # TODO: new line はちゃんと考える
    quoting = getattr(builtincsv, "QUOTE_" + output_csv_quoting.upper(), builtincsv.QUOTE_MINIMAL)
    csv_dict_writer = CloseableCsvDictWriter(text_writer, fieldnames, delimiter=csv_delimiter, quotechar=csv_quotechar, quoting=quoting)
    csv_typed_dict_writer = CloseableCsvTypedDictWriter(csv_dict_writer, fieldname2serializer=fieldname2serializer)
    return csv_typed_dict_writer

################################################################################
# Mix-In for Cli


class HasInputCsvDelimiterArgs(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.arg_parser.add_argument("--input-delimiter", "--delimiter", "-d", metavar="CHAR", nargs=None,
                                dest="input_csv_delimiter", default=cw.DEFAULT_CSV_DELIMITER,
                                help="delimiter char for input csv [default: '{0}']".format(cw.DEFAULT_CSV_DELIMITER))


class HasOutputCsvDelimiterArgs(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.arg_parser.add_argument("--output-delimiter", "--Delimiter", "-D", metavar="CHAR", nargs=None,
                                dest="output_csv_delimiter", default=cw.DEFAULT_CSV_DELIMITER,
                                help="delimiter char for output csv [default: '{0}']".format(cw.DEFAULT_CSV_DELIMITER))


class HasInputCsvQuoteCharArgs(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.arg_parser.add_argument("--input-quotechar", "--quotechar", "-q", metavar="CHAR", nargs=None,
                                dest="input_csv_quotechar", default=cw.DEFAULT_CSV_QUOTECHAR,
                                help="qute char for input csv [default: '{0}']".format(cw.DEFAULT_CSV_QUOTECHAR))


class HasOutputCsvQuoteCharArgs(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.arg_parser.add_argument("--output-quotechar", "--Quotechar", "-Q", metavar="CHAR", nargs=None,
                                dest="output_csv_quotechar", default=cw.DEFAULT_CSV_QUOTECHAR,
                                help="qute char for output csv [default: '{0}']".format(cw.DEFAULT_CSV_QUOTECHAR))

        self.arg_parser.add_argument("--output-quoting", "--Quoting", metavar="QUOTING", nargs=None,
                                dest="output_csv_quoting", default=cw.DEFAULT_CSV_QUOTING,
                                help="quoting style for output csv (ALL, MINIMAL, NONNUMERIC, NONE) [default: MINIMAL]")
        
        self.arg_parser.epilog += textwrap.dedent("""
            Csv output quoting:
                The style of quoting of output csv field.
                
                - ALL: quote all fields
                - MINIMAL: only quote those fields which contain special characters such as delimiter, quotechar or any of the characters in lineterminator
                - NONNUMERIC: quote all non-numeric fields
                - NONE: never quote fields.

                see https://docs.python.org/ja/3/library/csv.html#csv.QUOTE_ALL
            """)
        
################################################################################
# print


def tocsv(input_file="-", output_file="-",
           input_text_encoding=cw.DEFAULT_TEXT_ENCODING, input_text_errors=cw.DEFAULT_TEXT_ERRORS,
           output_text_encoding=cw.DEFAULT_TEXT_ENCODING, output_text_errors=cw.DEFAULT_TEXT_ERRORS,
           input_csv_delimiter=cw.DEFAULT_CSV_DELIMITER, input_csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR,
           output_csv_delimiter=cw.DEFAULT_CSV_DELIMITER, output_csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR, output_csv_quoting=cw.DEFAULT_CSV_QUOTING):
    
    with cw.csv.opencsv_reader(input_file,
                                text_encoding=input_text_encoding, text_errors=input_text_errors,
                                csv_delimiter=input_csv_delimiter, csv_quotechar=input_csv_quotechar) as csv_reader:
        with cw.csv.opencsv_writer(output_file,
                                    text_encoding=output_text_encoding, text_errors=output_text_errors,
                                    csv_delimiter=output_csv_delimiter, csv_quotechar=output_csv_quotechar, output_csv_quoting=output_csv_quoting) as csv_writer:
            for values in csv_reader:
                csv_writer.writerow(values)


class ToCsvCli(cw.text.ToTextCli, HasInputCsvDelimiterArgs, HasInputCsvQuoteCharArgs, HasOutputCsvDelimiterArgs, HasOutputCsvQuoteCharArgs):
    
    def __init__(self, name="cw-csv-to-csv", description="cw-csv-to-csv", *args, **kwargs):
        
        super(ToCsvCli, self).__init__(name=name, description=description, *args, **kwargs)
        HasInputCsvDelimiterArgs.__init__(self)
        HasOutputCsvDelimiterArgs.__init__(self)
        HasInputCsvQuoteCharArgs.__init__(self)
        HasOutputCsvQuoteCharArgs.__init__(self)
            
    def main(self, input_file="-", output_file="-",
                   input_text_encoding=cw.DEFAULT_TEXT_ENCODING, input_text_errors=cw.DEFAULT_TEXT_ERRORS,
                   output_text_encoding=cw.DEFAULT_TEXT_ENCODING, output_text_errors=cw.DEFAULT_TEXT_ERRORS,
                   input_csv_delimiter=cw.DEFAULT_CSV_DELIMITER, input_csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR,
                   output_csv_delimiter=cw.DEFAULT_CSV_DELIMITER, output_csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR, output_csv_quoting=cw.DEFAULT_CSV_QUOTING,
                   log_level=cw.DEFAULT_LOG_LEVEL):
        self.set_log_config(log_level=log_level)
        tocsv(input_file=input_file, output_file=output_file,
               input_text_encoding=input_text_encoding, input_text_errors=input_text_errors,
               output_text_encoding=output_text_encoding, output_text_errors=output_text_errors,
               input_csv_delimiter=input_csv_delimiter, input_csv_quotechar=input_csv_quotechar,
               output_csv_delimiter=output_csv_delimiter, output_csv_quotechar=output_csv_quotechar, output_csv_quoting=output_csv_quoting)
        return 0

def to_typed_csv(input_file="-", output_file="-",
           input_text_encoding=cw.DEFAULT_TEXT_ENCODING, input_text_errors=cw.DEFAULT_TEXT_ERRORS,
           output_text_encoding=cw.DEFAULT_TEXT_ENCODING, output_text_errors=cw.DEFAULT_TEXT_ERRORS,
           input_csv_delimiter=cw.DEFAULT_CSV_DELIMITER, input_csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR,
           output_csv_delimiter=cw.DEFAULT_CSV_DELIMITER, output_csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR, output_csv_quoting=cw.DEFAULT_CSV_QUOTING,
           metadata_file=None):
    
    metadata = load_metadata(metadata_file)
    fieldname2deserializer, fieldname2serializer = get_field_types(metadata)
    
    with cw.csv.open_csv_typed_dict_reader(input_file,
                                text_encoding=input_text_encoding, text_errors=input_text_errors,
                                csv_delimiter=input_csv_delimiter, csv_quotechar=input_csv_quotechar,
                                fieldname2deserializer=fieldname2deserializer) as csv_dict_reader:
        
        LOGGER.info("Found input fieldnames==%s", csv_dict_reader.fieldnames)
        
        with cw.csv.open_csv_typed_dict_writer(output_file, fieldnames=csv_dict_reader.fieldnames,
                                    text_encoding=output_text_encoding, text_errors=output_text_errors,
                                    csv_delimiter=output_csv_delimiter, csv_quotechar=output_csv_quotechar, output_csv_quoting=output_csv_quoting,
                                    fieldname2serializer=fieldname2serializer) as csv_dict_writer:
            
            csv_dict_writer.writeheader()
            for row in csv_dict_reader:
                csv_dict_writer.writerow(row)


class ToTypedCsvCli(ToCsvCli):
    
    def __init__(self, name="cw-csv-to-typedcsv", description="cw-csv-to-typedcsv", *args, **kwargs):
        
        super(ToTypedCsvCli, self).__init__(name=name, description=description, *args, **kwargs)
        
        self.arg_parser.add_argument("--metadata", metavar="FILE", nargs=None,
                                dest="metadata_file", default=None,
                                help="metadata file of csv data [default: '{0}']".format(None))

    def main(self, input_file="-", output_file="-",
                   input_text_encoding=cw.DEFAULT_TEXT_ENCODING, input_text_errors=cw.DEFAULT_TEXT_ERRORS,
                   output_text_encoding=cw.DEFAULT_TEXT_ENCODING, output_text_errors=cw.DEFAULT_TEXT_ERRORS,
                   input_csv_delimiter=cw.DEFAULT_CSV_DELIMITER, input_csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR,
                   output_csv_delimiter=cw.DEFAULT_CSV_DELIMITER, output_csv_quotechar=cw.DEFAULT_CSV_QUOTECHAR, output_csv_quoting=cw.DEFAULT_CSV_QUOTING,
                   metadata_file=None,
                   log_level=cw.DEFAULT_LOG_LEVEL):
        self.set_log_config(log_level=log_level)
        to_typed_csv(input_file=input_file, output_file=output_file,
               input_text_encoding=input_text_encoding, input_text_errors=input_text_errors,
               output_text_encoding=output_text_encoding, output_text_errors=output_text_errors,
               input_csv_delimiter=input_csv_delimiter, input_csv_quotechar=input_csv_quotechar,
               output_csv_delimiter=output_csv_delimiter, output_csv_quotechar=output_csv_quotechar, output_csv_quoting=output_csv_quoting,
               metadata_file=metadata_file)
        return 0

from . import pivot
