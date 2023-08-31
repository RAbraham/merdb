import uuid
from typing import *
import modin.pandas as md
import pandas as pd
from dataclasses import dataclass
from merdb.api.common import names
from merdb.core import Map, Where, Source, InMemoryTable, Order, TableReference, Join, BinaryOperation, \
    UnaryOperation, Aggregate, Rename, Select, JoinKind, Recurse, Limit
from abc import ABC, abstractmethod

MDF = md.DataFrame


def modin_limit(op: Limit, source: md.DataFrame) -> md.DataFrame:
    return source.head(op.limit)
def modin_select(op: Select, source: md.DataFrame) -> md.DataFrame:
    return source[list(op.columns)]


def modin_rename(op: Rename, source: md.DataFrame) -> md.DataFrame:
    return source.rename(columns=op.columns)


def modin_filter(op: Where, source: md.DataFrame) -> md.DataFrame:
    input_df = source
    filter_df = input_df.apply(op.func, axis=1)
    return input_df[filter_df]


def modin_map(op: Map, source: md.DataFrame) -> md.DataFrame:
    input_df = source.copy(deep=True)
    input_df[op.column] = input_df.apply(op.func, axis=1)
    return input_df


# def modin_recurse(op: Recurse, start: md.DataFrame):
#     prev = start
#     apply_pd = op.until(table(prev))().df()
#     if apply_pd.empty:
#         return start
#     apply_md = md.DataFrame(apply_pd)
#     _next = md.concat([prev, apply_md])
#     while not _next.equals(prev):
#         prev = _next
#         apply_pd = op.until(table(prev))().df()
#         if apply_pd.empty:
#             break
#         apply_md = md.DataFrame(apply_pd)
#         _next = md.concat([prev, apply_md])
#     return _next

def apply_branch(op, prev):
    _df = op.until(table(prev))().df()
    return md.DataFrame(_df)


def modin_recurse(op: Recurse, start: md.DataFrame):
    import ipdb;
    ipdb.set_trace()

    prev = start
    _next = apply_branch(op, prev)
    total = md.concat([prev, _next])
    while not total.equals(prev):
        prev = total
        _next = apply_branch(op, prev)
        total = md.concat([prev, _next])
    return total


def modin_aggregate(op: Aggregate, source: md.DataFrame) -> md.DataFrame:
    by = op.by
    func = op.func
    if op.name:
        col_name = op.name
    else:
        col_name = func.__name__ if func.__name__ != "<lambda>" else "__agg__"

    if by:
        _func = lambda df: df[op.column].agg(func)
        r = source.groupby(op.by).apply(_func).reset_index()
        r = r.rename(columns={"__reduced__": col_name})
        return r
    else:
        r = source[op.column].agg(func)
        result_df = md.DataFrame(data=[[r]], columns=[col_name])
        return result_df


def modin_order(op: Order, source: md.DataFrame) -> md.DataFrame:
    input_df = source
    _ordered_df = input_df.sort_values(by=names(op.columns()), ascending=op.ascending())
    return _ordered_df


def modin_join(op: Join, x: md.DataFrame, y: md.DataFrame):
    if op.on is None:
        return md.merge(x, y, left_index=True, right_index=True, how=op.kind.value)
    if op.kind != JoinKind.CROSS:
        return md.merge(x, y, how=op.kind.value, on=op.on)
    else:
        return md.merge(x, y, how=op.kind.value)


class DB(ABC):
    @abstractmethod
    def add_dfs(self, dfs: Dict[str, pd.DataFrame]):
        pass


def intersect(dfs1, dfs2):
    return set(dfs1.keys()).intersection(set(dfs2.keys()))


class ModinDB(DB):
    def __init__(self, tables: Dict[str, md.DataFrame] = None):
        self.tables = tables or {}
        pass

    def add_dfs(self, dfs: Dict[str, pd.DataFrame]):
        tables = {name: md.DataFrame(df) for name, df in dfs.items()}
        _intersect = intersect(self.tables, dfs)
        if _intersect:
            raise ValueError(f"These keys already exist in the database: {intersect}")

        self.tables = {**tables, **self.tables}
        return self

    def query(self, query: Source) -> InMemoryTable:
        tree = dependency_tree(self.tables, query)
        _df = tree.run()
        return mdf_to_mem_table(_df)

def mdf_to_mem_table(_df):
    return InMemoryTable(to_df(_df))


# class ModinDB(DB):
#     def __init__(self, tables: Dict[str, md.DataFrame] = None):
#         self.tables = tables or {}
#         pass
#     def add_dfs(self, dfs: Dict[str, pd.DataFrame]):
#         tables = {name: md.DataFrame(df) for name, df in dfs.items()}
#         return ModinDB(tables)
#
#     def query(self, query: Source) -> InMemoryTable:
#         tree = dependency_tree(self.tables, query)
#         _df = tree.run()
#         return InMemoryTable(to_df(_df))

class ModinTable:
    def __init__(self, df: md.DataFrame, db: DB, name: str):
        self.df = df
        self.db = db
        self.name = name
        self.db.add_dfs({name: df})

    def __call__(self, *args, **kwargs):
        return mdf_to_mem_table(self.df)


def _table(source, db: DB, name: str = None):
    name = name or str(uuid.uuid4())
    if isinstance(source, pd.DataFrame):
        return ModinTable(md.DataFrame(source), db, name)
    elif isinstance(source, md.DataFrame):
        return ModinTable(source, db, name)
    else:
        raise ValueError("Not Implemented")


class TableSingleton:
    def __init__(self, db: DB = None):
        self.db = db or ModinDB()

        pass

    def __call__(self, source, db: DB = None, name: str = None):
        if db:
            self.db = db
        return _table(source, self.db, name)


table = TableSingleton()


def dependency_tree(tables, query):
    if isinstance(query, TableReference):
        return MTable(tables[query.name])
    elif isinstance(query, BinaryOperation):
        # TODO: dupe with Operation
        left = query.left
        right = query.right
        previous_left = dependency_tree(tables, left)
        previous_right = dependency_tree(tables, right)
        modin_func_op = make_modin_func(query)
        return MBinaryOperation(previous_left, previous_right, modin_func_op)

    elif isinstance(query, UnaryOperation):
        source = query.source
        previous = dependency_tree(tables, source)
        modin_func_op = make_modin_func(query)
        # TODO: Change to MUnaryOperation
        return MUnaryOperation(previous, modin_func_op)
    elif isinstance(query, ModinTable):
        t = tables[query.name]
        return MTable(t)
    else:
        raise ValueError(f"Unsupported Type:{query}")


FUNC = {
    Rename: modin_rename,
    Recurse: modin_recurse,
    Select: modin_select,
    Where: modin_filter,
    Order: modin_order,
    Join: modin_join,
    Limit: modin_limit,
    Map: modin_map,
    Aggregate: modin_aggregate
}


def make_modin_func(query):
    f = FUNC[type(query)]
    if not f:
        raise ValueError(f"Unsupported Query:{query}")
    # TODO APM?
    if isinstance(query, UnaryOperation):
        return lambda df: f(query, df)
    elif isinstance(query, BinaryOperation):
        return lambda left_df, right_df: f(query, left_df, right_df)


@dataclass
class MSource:
    def run(self):
        raise ValueError("Not Implemented")

#
# @dataclass
# class ModinTable:
#     table: md.DataFrame
#
#     def df(self):
#         return self.table

@dataclass
class MTable(MSource):
    df: md.DataFrame

    def run(self):
        return self.df


@dataclass
class MUnaryOperation(MSource):
    source: MSource
    func: Callable

    def run(self):
        return self.func(self.source.run())


@dataclass
class MBinaryOperation(MSource):
    left: MSource
    right: MSource
    func: Callable

    def run(self):
        return self.func(self.left.run(), self.right.run())


def to_df(modin_df):
    return modin_df._to_pandas().reset_index(drop=True)

# def to_df(modin_df):
#     return modin_df.reset_index(drop=True)

def size(df: MDF):
    return df.size
