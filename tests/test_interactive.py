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


def test_common_parent_error():
    # from merdb.api.tacit_interactive import *
    # import pandas as pd

    # def add(col): return col.sum()
    #
    #
    # input_df = pd.DataFrame([
    #     ["toronto", 10],
    #     ["montreal", 20],
    #     ["toronto", 30],
    #     ["halifax", 5]
    # ], columns=["location", "population"])
    #
    # # people = table(input_df)
    # # total = agg(people, add, "population")
    #
    # r = t(input_df) | agg(lambda c: add(c), "population")
    #
    # print(r)
    #

    data = {
        'price': [100, 50, 150],
        'volume': [2, 1, 1]
    }

    trades_df = pd.DataFrame(data)

    print(trades_df)

    weighted_avg_price = (trades_df['price'] * trades_df['volume']).sum() / trades_df['volume'].sum()
    print('Weighted average price by Pandas:', weighted_avg_price)

    tt = t(trades_df)
    mul = tt | map(lambda r: r['price'] * r['volume'], "mul")
    mul_sum = mul | agg(lambda c: c.sum(), "mul", "mul_sum")
    suma = tt | agg(lambda c: c.sum(), "volume", "sum")
    zipped = mul_sum | join_inner(suma)
    result = zipped | map(lambda r: r["mul_sum"] / r["mul"], "total")

    print("Mul")
    print(mul)
    print("Mul Sum")
    print(mul_sum)
    print("Suma")
    print(suma)
    print("zipped")
    print(zipped)
    # print("r")
    #

def is_senior(r: Row[C.age: int, C.name: str]) -> bool:
    return r['age'] > 35


def double_age(r: Row[C.age: int]) -> int:
    return r.age * 2
