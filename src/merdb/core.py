from typing import *
from dataclasses import dataclass
from enum import Enum
import pandas as pd

# TODO. move away from T and C to just strings?
StrOrList = Union[str, List[str]]
On = StrOrList
By = StrOrList


class JoinKind(Enum):
    INNER = "inner"
    OUTER = "full"
    LEFT = "left"
    RIGHT = "right"
    CROSS = "cross"


@dataclass
class InMemoryTable:
    table: pd.DataFrame

    def df(self):
        return self.table


@dataclass
class Column:
    name: str


@dataclass
class Source:
    pass


@dataclass
class TableReference(Source):
    name: str


@dataclass
class Operation(Source):
    pass


@dataclass
class UnaryOperation(Source):
    pass


@dataclass
class BinaryOperation(Operation):
    pass


from abc import ABC, abstractmethod


class DB(ABC):
    # @abstractmethod
    # def mymethod(self):
    #     pass
    pass


@dataclass
class Where(UnaryOperation):
    func: Callable
    source: Source
    db: DB

    def run(self):
        # TODO: in abstract class?
        if self.db:
            return self.db.query(self)
        else:
            raise ValueError("No DB set. Create an explicit DB and call db.query(query)")

    def __call__(self, *args, **kwargs):
        return self.run()


@dataclass
class Map(UnaryOperation):
    func: Callable
    column: str
    source: Source
    db: DB

    def run(self):
        # TODO: in abstract class?
        if self.db:
            return self.db.query(self)
        else:
            raise ValueError("No DB set. Create an explicit DB and call db.query(query)")

    def __call__(self, *args, **kwargs):
        return self.run()


@dataclass
class Rename(UnaryOperation):
    db: DB
    source: Source
    columns: Dict[str, str]

    def run(self):
        # TODO: in abstract class?
        if self.db:
            return self.db.query(self)
        else:
            raise ValueError("No DB set. Create an explicit DB and call db.query(query)")

    def __call__(self, *args, **kwargs):
        return self.run()


@dataclass
class Select(UnaryOperation):
    db: DB
    source: Source
    columns: List[str]

    def run(self):
        # TODO: in abstract class?
        if self.db:
            return self.db.query(self)
        else:
            raise ValueError("No DB set. Create an explicit DB and call db.query(query)")

    def __call__(self, *args, **kwargs):
        return self.run()


@dataclass
class Aggregate(UnaryOperation):
    func: Callable
    by: By
    column: str
    name: str
    source: Source
    db: DB

    def run(self):
        # TODO: in abstract class?
        if self.db:
            return self.db.query(self)
        else:
            raise ValueError("No DB set. Create an explicit DB and call db.query(query)")

    def __call__(self, *args, **kwargs):
        return self.run()


@dataclass
class Limit(UnaryOperation):
    limit: int
    source: Source
    db: DB

    def run(self):
        # TODO: in abstract class?
        if self.db:
            return self.db.query(self)
        else:
            raise ValueError("No DB set. Create an explicit DB and call db.query(query)")

    def __call__(self, *args, **kwargs):
        return self.run()


@dataclass
class Order(UnaryOperation):
    orders: List[Tuple[Column, bool]]
    source: Source
    # Call it runner
    db: DB

    def columns(self):
        return [x[0] for x in self.orders]

    def ascending(self):
        return [x[1] for x in self.orders]

    def run(self):
        # TODO: in abstract class?
        if self.db:
            return self.db.query(self)
        else:
            raise ValueError("No DB set. Create an explicit DB and call db.query(query)")

    def __call__(self, *args, **kwargs):
        return self.run()


# TODO: Change from x and y to left and right

@dataclass
class Recurse(UnaryOperation):
    db: DB
    source: Source
    until: Callable

    def run(self):
        # TODO: in abstract class?
        if self.db:
            return self.db.query(self)
        else:
            raise ValueError("No DB set. Create an explicit DB and call db.query(query)")

    def __call__(self, *args, **kwargs):
        return self.run()


@dataclass
class Join(BinaryOperation):
    kind: JoinKind
    left: Source
    right: Source
    on: On
    db: DB

    def run(self):
        # TODO: in abstract class?
        if self.db:
            return self.db.query(self)
        else:
            raise ValueError("No DB set. Create an explicit DB and call db.query(query)")

    def __call__(self, *args, **kwargs):
        return self.run()
