"""This contains classes for reading files with lines structured as
fixed-width fields and a factory for creating them.

"""
from collections import namedtuple
import struct


class FixedFieldReaderBase(object):
    """Base class for reading files with lines structured as fixed-width
    fields.

    """
    def __init__(self, file, struct, names, wholeline):
        """@param file the file to read.
        @param struct the struct instance for the fields.
        @param names an iterable of field names.
        @param wholeline if true, throw an exception if the field
          sizes do not comprise the entire line.

        """
        self.file = file
        self.struct = struct
        self.names = names
        if wholeline:
            self.unpack = self.struct.unpack
        else:
            self.unpack = self.struct.unpack_from

    def _split(self, line, lineno):
        line = line.rstrip(b'\r\n')
        try:
            return (
                x.strip().decode('utf-8')
                for x in self.unpack(line)
            )
        except struct.error as error:
            raise RuntimeError(
                str(error) +
                " but line {} is {} bytes".format(lineno+1, len(line)))


class FixedFieldReader(FixedFieldReaderBase):
    """Class for reading files with lines structured as fixed-width fields
    and providing fields as tuples.

    """
    def __init__(self, file, struct, names, wholeline):
        super().__init__(file, struct, names, wholeline)

    def readlines(self):
        for lineno, line in enumerate(self.file.readlines()):
            yield self._split(line, lineno)


class FixedFieldDictReader(FixedFieldReaderBase):
    """Class for reading files with lines structured as fixed-width fields
    and providing fields as dicts.

    """
    def __init__(self, file, struct, names, wholeline):
        super().__init__(file, struct, names, wholeline)

    def readlines(self):
        for lineno, line in enumerate(self.file.readlines()):
            yield dict(zip(self.names,self._split(line, lineno)))


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

    def reader(self, file, wholeline=False, usedict=False):
        if usedict:
            return FixedFieldDictReader(file, self.struct, self.names, wholeline)
        else:
            return FixedFieldReader(file, self.struct, self.names, wholeline)
