from typing import *
from merdb.core import TableReference, Column
from dataclasses import make_dataclass

class TableSugar:
    def __getattr__(self, name):
        return TableReference(name)

T = TableSugar()

class ColumnSugar:
    def __getattr__(self, name):
        return Column(name)

C = ColumnSugar()

class RowSugar:
    def __getitem__(self, item):
        if  isinstance(item, slice):
            item = (item, )
        specs = []
        for col_spec in item:
           specs.append((col_spec.start.name, col_spec.stop))
        return make_dataclass("RowSpec", specs)


Row = RowSugar()


def table(name: str) -> TableReference:
    return TableReference(name)

def names(columns: List[Column]):
    return [c.name for c in columns]
