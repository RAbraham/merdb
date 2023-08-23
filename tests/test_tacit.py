import pandas as pd

DF = pd.DataFrame
from merdb.api.tacit import table, where, order_by, map, select, rename
from pandas.testing import assert_frame_equal

from merdb.api.common import Row, C

def test_tacit():
    cols = ["name", "age"]
    people_df = DF([
        ["Rajiv", 35],
        ["Sonal", 20],
        ["Aby", 70],
        ["Abba", 90],
    ], columns=cols)

    result = table(people_df) | where(is_senior)

    exp_df = DF([
        ["Aby", 70],
        ["Abba", 90],
    ], columns=["name", "age"])

    assert_frame_equal(result().df(), exp_df)

def test_tacit_2():
    cols = ["name", "age"]
    people_df = DF([
        ["Rajiv", 35],
        ["Sonal", 20],
        ["Aby", 70],
        ["Abba", 90],
    ], columns=cols)

    result = table(people_df) | where(is_senior) | map(double_age, "age")

    exp_df = DF([
        ["Aby", 70 * 2],
        ["Abba", 90 * 2],
    ], columns=["name", "age"])

    assert_frame_equal(result().df(), exp_df)


def test_pipe():
    cols = ["name", "age"]
    people_df = DF([
        ["Rajiv", 35],
        ["Sonal", 20],
        ["Aby", 70],
        ["Abba", 90],
    ], columns=cols)

    quadruple_age =  map(double_age, "age") | map(double_age, "age")
    result = (table(people_df)
              | where(is_senior)
              | order_by("name", "asc")
              | quadruple_age
              | select("age")
              | rename({"age": "new_age"})
              )

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
    exp_df = DF([
        ["Abba", 90 * 4],
        ["Aby",  70 * 4],
    ], columns=["name", "age"])

    # cop = a composite operation
    # op = an atomic operation


    # composable pipes with table directly: i.e. table(..) | cop1 | cop2
    make_senior = where(is_senior) | order_by("name", "asc")
    double_map = map(double_age, "age") | map(double_age, "age")
    result = table(people_df) | make_senior | double_map
    assert_frame_equal(result().df(), exp_df)


    # op1 | cop1
    exp_df_op_and_cop =  DF([
        ["Aby",  70 * 4],
        ["Abba", 90 * 4],
    ], columns=["name", "age"])
    op_and_cop = where(is_senior) | double_map
    result_op_and_cop = table(people_df) | op_and_cop
    assert_frame_equal(result_op_and_cop().df(), exp_df_op_and_cop)


    #  cop1 | cop2
    cop_and_cop =  make_senior | double_map
    result_cop_and_cop = table(people_df) | cop_and_cop
    assert_frame_equal(result_cop_and_cop().df(), exp_df)


    #  cop1 | op1
    cop_and_op = make_senior | map(lambda r: r.age * 4, "age")
    result_cop_and_op = table(people_df) | cop_and_op
    assert_frame_equal(result_cop_and_op().df(), exp_df)


def is_senior(r: Row[C.age: int, C.name: str]) -> bool:
    return r['age'] > 35


def double_age(r: Row[C.age: int]) -> int:
    return r.age * 2
