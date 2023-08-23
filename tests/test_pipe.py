import pandas as pd

DF = pd.DataFrame
from merdb.api.pipe import _, table, filter_with, order_by, map, select, rename, limit
from pandas.testing import assert_frame_equal

from merdb.api.common import Row, C


def test_pipe():
    cols = ["name", "age"]
    people_df = DF([
        ["Rajiv", 35],
        ["Sonal", 20],
        ["Aby", 70],
        ["Abba", 90],
    ], columns=cols)

    quadruple_age = _ | map(_, double_age, "age") | map(_, double_age, "age")
    # quadruple_age =  _ | map(_, double_age, "age") | map(_, double_age, "age")
    # quadruple_age =  _ | _.map(double_age, "age") | _.map(double_age, "age")
    result = (people_df
              | table(_)
              | filter_with(_, is_senior)
              | order_by(_, "name", True)
              | quadruple_age
              | select(_, "age")
              | rename(_, {"age": "new_age"}))

    exp_df = DF([
        [90 * 4],
        [70 * 4],
    ], columns=["new_age"])

    assert_frame_equal(result().df(), exp_df)


def test_composable_pipelines():
    cols = ["name", "age"]
    people_df = DF([
        ["Rajiv", 35],
        ["Sonal", 20],
        ["Aby", 70],
        ["Abba", 90],
    ], columns=cols)

    # composable pipes
    double_map = map(_, double_age, "age") | map(_, double_age, "age")
    # double_map = map(_, double_age, "age") | map(_, double_age, "age")
    make_senior = filter_with(_, is_senior) | order_by(_, "name", True)
    # make_senior = filter_with(_, is_senior) | order_by(_, "name", True)
    # make_senior = _.filter_with(is_senior) | _.order_by("name", True)
    result = (people_df
              | table(_)
              | make_senior
              | double_map)

    exp_df = DF([
        ["Abba", 180 * 2],
        ["Aby", 140 * 2],
    ], columns=["name", "age"])

    assert_frame_equal(result().df(), exp_df)


def test_limit():
    cols = ["name", "age"]
    df = DF([
        ["Rajiv", 35],
        ["Sonia", 20],
        ["Aby", 70],
        ["Abba", 90],
    ], columns=cols)

    cols = ["name", "age"]
    exp_df = DF([
        ["Rajiv", 35],
        ["Sonia", 20],
    ], columns=cols)

    result = df | table(_) | limit(_, 2)

    assert_frame_equal(result().df(), exp_df)


def is_senior(r: Row[C.age: int, C.name: str]) -> bool:
    return r['age'] > 35


def double_age(r: Row[C.age: int]) -> int:
    return r.age * 2
