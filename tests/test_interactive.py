import pandas as pd
DF = pd.DataFrame

from merdb.api.tacit_interactive import t, where, order_by, map, select, rename, Row, C, Column
from pandas.testing import assert_frame_equal

def test_tacit():
    cols = ["name", "age"]
    people_df = DF([
        ["Rajiv", 35],
        ["Sonal", 20],
        ["Aby", 70],
        ["Abba", 90],
    ], columns=cols)

    result = t(people_df) | where(is_senior)

    exp_df = DF([
        ["Aby", 70],
        ["Abba", 90],
    ], columns=["name", "age"])

    assert_str(result, exp_df)


def test_columns():
    cols = ["name", "age"]
    people_df = DF([
        ["Rajiv", 35],
        ["Sonal", 20],
        ["Aby", 70],
        ["Abba", 90],
    ], columns=cols)

    result = t(people_df).columns()
    assert list(result) == [Column("name"), Column("age")]




def test_tacit_2():
    cols = ["name", "age"]
    people_df = DF([
        ["Rajiv", 35],
        ["Sonal", 20],
        ["Aby", 70],
        ["Abba", 90],
    ], columns=cols)

    result = t(people_df) | where(is_senior) | map(double_age, "age")

    exp_df = DF([
        ["Aby", 70 * 2],
        ["Abba", 90 * 2],
    ], columns=["name", "age"])

    assert_str(result, exp_df)


def assert_str(result, exp_df):
    assert str(result) == str(exp_df)
    assert result.__repr__() == exp_df.__repr__()


def test_pipe():
    cols = ["name", "age"]
    people_df = DF([
        ["Rajiv", 35],
        ["Sonal", 20],
        ["Aby", 70],
        ["Abba", 90],
    ], columns=cols)

    quadruple_age =  map(double_age, "age") | map(double_age, "age")
    result = (t(people_df)
              | where(is_senior)
              # | where(is_senior)
              # | where(lambda r: r.age > 35)
              # | where(__.['age] > 35)
              # | where(a_func(__.age))
              | order_by("name", "asc")
              | quadruple_age
              | select("age")
              | rename({"age": "new_age"})
              )

    exp_df = DF([
        [90 * 4],
        [70 * 4],
    ], columns=["new_age"])


    assert_str(result, exp_df)



def is_senior(r: Row[C.age: int, C.name: str]) -> bool:
    return r['age'] > 35


def double_age(r: Row[C.age: int]) -> int:
    return r.age * 2
