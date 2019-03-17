from collections import OrderedDict
import fixedfieldreader as ffr
from io import BytesIO, StringIO
import logging

field_descs = [
    ('f1', 2, 'x'),
    ('f2', 3, 's'),
    ('f3', 1, 's'),
]

data = BytesIO(
    b'112223\n'
    b'112223\n'
    b' 1 223\n'
    b' 1 22 \n'
    b'   22 \n'
    b'      '
)
output_dicts = [
    OrderedDict([('f2', '222'), ('f3', '3')]),
    OrderedDict([('f2', '222'), ('f3', '3')]),
    OrderedDict([('f2', '22'), ('f3', '3')]),
    OrderedDict([('f2', '22'), ('f3', '')]),
    OrderedDict([('f2', '22'), ('f3', '')]),
    OrderedDict([('f2', ''), ('f3', '')]),
]

factory = ffr.FixedFieldReaderFactory(*field_descs)

def reader_wholeline_usedict_test_success():
    for exp, act in zip(output_dicts,
                        factory.reader(data, wholeline=True, usedict=True)):
        assert exp == act

def reader_wholeline_usedict_test_rowerror():
    for line in [b'1122233', b'11222']:
        try:
            for fields in factory.reader([line], wholeline=True, usedict=True):
                pass
        except ffr.Error as e:
            assert e.line_num == 1
            assert e.exp_len == 6
            assert e.act_len == len(line)
        else:
            assert False

def reader_wholeline_nousedict_test_success():
    for exp, act in zip((tuple(odict.values()) for odict in output_dicts),
                        factory.reader(data, wholeline=True, usedict=False)):
        assert exp == act

def reader_nowholeline_usedict_test_success():
    for exp, act in zip(output_dicts,
                        factory.reader(data, wholeline=False, usedict=True)):
        assert exp == act

def reader_nowholeline_nousedict_test_success():
    for exp, act in zip((tuple(odict.values()) for odict in output_dicts),
                        factory.reader(data, wholeline=False, usedict=False)):
        assert exp == act

def reader_nowholeline_usedict_test_rowerror():
    line = b'11222' 
    try:
        for fields in factory.reader([line], wholeline=False, usedict=True):
            pass
    except ffr.Error as e:
        assert e.line_num == 1
        assert e.exp_len == 6
        assert e.act_len == len(line)
    else:
        assert False

def reader_nowholeline_usedict_test_norowerror():
    try:
        for fields in factory.reader([b'1122233'], wholeline=False, usedict=True):
            assert {'f2': '222', 'f3': '3'} == fields
    except ffr.Error as e:
        assert False

def reader_nowholeline_usedict_test_warnbadlines():
    lines = [b'11222', b'1122233']
    exp = 'Error at line 1: unpack_from requires a buffer of at least 6 bytes but line is 5 bytes'
    sio = StringIO()
    handler = logging.StreamHandler(sio)
    logger = logging.getLogger('fixedfieldreader')
    logger.addHandler(handler)
    try:
        for fields in factory.reader(lines, wholeline=False, usedict=True, badlines='warn'):
            assert {'f2': '222', 'f3': '3'} == fields
    except ffr.Error as e:
        logger.removeHandler(handler)
        assert False
    logger.removeHandler(handler)
    assert sio.getvalue().strip() == exp

def reader_nowholeline_usedict_test_ignorebadlines():
    lines = [b'11222', b'1122233']
    exp = ''
    sio = StringIO()
    handler = logging.StreamHandler(sio)
    logger = logging.getLogger('fixedfieldreader')
    logger.addHandler(handler)
    try:
        for fields in factory.reader(lines, wholeline=False, usedict=True, badlines='ignore'):
            assert {'f2': '222', 'f3': '3'} == fields
    except ffr.Error as e:
        logger.removeHandler(handler)
        assert False
    logger.removeHandler(handler)
    assert sio.getvalue().strip() == exp
