# extras.py - namedtuple reader/writer

# TODO: provide rename in openers

from __future__ import unicode_literals

import collections

from ._common import PY2, DIALECT, lazyproperty
from ._dispatch import register_reader, register_writer
from . import readers, writers

__all__ = ['NamedTupleReader']


@register_reader('namedtuple', 'text')
@register_reader('namedtuple', 'bytes')
class NamedTupleReader(object):
    """:func:`csv23.reader` yielding namedtuples of ``unicode`` strings (PY3: ``str``)."""

    def __init__(self, stream, dialect=DIALECT, rename=False, encoding=False, **kwargs):
        self._reader = readers.reader(stream, dialect, encoding, **kwargs)
        self._rename = rename
        self._row_cls = None

    def __iter__(self):
        return self

    def __next__(self):
        make_row = self._make_row
        return make_row(next(self._reader))

    if PY2:
        next = __next__
        del __next__

    @lazyproperty
    def _make_row(self):
        assert self._row_cls is None
        try:
            header = next(self._reader)
        except StopIteration:
            raise RuntimeError('missing header line for namedtuple fields')
        if callable(self._rename):
            header = map(self._rename, header)
            rename = False
        else:
            rename = self._rename
        self._row_cls = collections.namedtuple('Row', header, rename=rename)
        return self._row_cls._make

    @property
    def dialect(self):
        return self._reader.dialect

    @property
    def line_num(self):
        return self._reader.line_num

    @property
    def row_cls(self):
        return self._row_cls
