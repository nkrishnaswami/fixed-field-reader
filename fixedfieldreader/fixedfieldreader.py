"""This contains classes for reading files with lines structured as
fixed-width fields and a factory for creating them.

"""
from collections import namedtuple
import logging
import struct

from .error import *


logger = logging.getLogger(__name__)


class FixedFieldReaderBase(object):
    """Base class for reading iterables of lines structured as fixed-width
    fields.

    """
    def __init__(self, file, struct, names, wholeline, badlines):
        """@param file the file (iterable of lines) to read.
        @param struct the struct instance for the fields.
        @param names an iterable of field names.
        @param wholeline if true, throw an exception if the field
          sizes do not comprise the entire line.
        @param badlines one of 'error' (raise an exception), 'warn'
          (print a warning and continue), and 'ignore' (silently
          continue) to control behavior on processing malformed
          records.

        """
        self.file = file
        self.struct = struct
        self.names = names
        if badlines not in {'error', 'warn', 'ignore'}:
            raise InitError(
                '`badlines` must be one of "error", "warn" or "ignore", not "{}"'.format(
                    badlines))
        self.badlines = badlines
        if wholeline:
            self.unpack = self.struct.unpack
        else:
            self.unpack = self.struct.unpack_from
        self.line_num = None

    def _readlines(self):
        for line_num, line in enumerate(self.file, 1):
            self.line_num = line_num
            yield line
        
    def _split(self, line):
        line = line.rstrip(b'\r\n')
        try:
            return (
                x.strip().decode('utf-8')
                for x in self.unpack(line)
            )
        except struct.error as error:
            raise RowLengthError(
                self.line_num,
                str(error) + " but line is {} bytes".format(len(line)),
                exp_len=self.struct.size,
                act_len=len(line))


class FixedFieldReader(FixedFieldReaderBase):
    """Class for reading files with lines structured as fixed-width fields
    and providing fields as tuples.

    """
    def __init__(self, file, struct, names, wholeline, badlines='error'):
        super().__init__(file, struct, names, wholeline, badlines)

    def __iter__(self):
        for line in self._readlines():
            try:
                yield self._split(line)
            except Error as e:
                if self.badlines == 'error':
                    raise
                elif self.badlines == 'warn':
                    logger.warn(str(e))
                else:
                    pass


class FixedFieldDictReader(FixedFieldReaderBase):
    """Class for reading files with lines structured as fixed-width fields
    and providing fields as dicts.

    """
    def __init__(self, file, struct, names, wholeline, badlines='error'):
        super().__init__(file, struct, names, wholeline, badlines)

    def __iter__(self):
        for line in self._readlines():
            try:
                yield dict(zip(self.names,self._split(line)))
            except Error as e:
                if self.badlines == 'error':
                    raise
                elif self.badlines == 'warn':
                    logger.warn(str(e))
                else:
                    pass


class FixedFieldReaderFactory(object):
    """Class for creating FixedFieldReaders from iterables of tuples
    describing their fields.

    """
    Descriptor = namedtuple('Descriptor', ['name', 'len', 'type'])

    def __init__(self, *descriptors):
        self.descriptors = [
            self.Descriptor(*descriptor) for descriptor in descriptors
        ]
        self.fmtstring = ' '.join(
            str(descriptor.len) + descriptor.type
            for descriptor in self.descriptors
        )
        self.struct = struct.Struct(self.fmtstring)
        self.names = [
            descriptor.name for descriptor in self.descriptors
            if descriptor.type != 'x'
        ]

    def reader(self, file, *, wholeline=False, usedict=False, badlines='error'):
        if usedict:
            return FixedFieldDictReader(file, self.struct, self.names, wholeline, badlines)
        else:
            return FixedFieldReader(file, self.struct, self.names, wholeline, badlines)
