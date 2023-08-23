import pandas as pd
from pandas.testing import assert_frame_equal
from merdb.api.base import where, order_by, join_inner, map, agg, rename, select, limit
from merdb.api.common import Row, T, C
from merdb.resource import make_db, table

DF = pd.DataFrame


# test group
# test larger than memory datasets with filter UDF.
# test lazy and eager? Have a separate namespace for eager? e.g from merdb.interactive import filter_with
# test_filter_from_memory ( add to some db)
# T.table and T.schema.table?
# row as dictionary access
# agg(people, add, "*") # select distinct(*) from table?

def test_filter():
    input_df = DF([
        ["Rajiv", 35],
        ["Sonia", 40],
        ["Aby", 70]
    ], columns=["name", "age"])

    db = make_db()
    db = db.add_dfs({"people": input_df})

    seniors = where(T.people, is_senior)
    act = db.query(seniors)

    exp_df = DF([
        ["Sonia", 40],
        ["Aby", 70]
    ], columns=["name", "age"])

    assert_frame_equal(act.df(), exp_df)


def test_order():
    input_df = DF([
        ["Rajiv", 35],
        ["Abba", 20],
        ["Sonia", 40],
        ["Aby", 70]
    ], columns=["name", "age"])
    db = make_db()
    db = db.add_dfs({"people": input_df})
    ordered = order_by(T.people, "name", True)
    act = db.query(ordered)

    exp_df = DF([
        ["Abba", 20],
        ["Aby", 70],
        ["Rajiv", 35],
        ["Sonia", 40],
    ], columns=["name", "age"])

    assert_frame_equal(act.df(), exp_df)


def test_multiple_queries():
    input_df = DF([
        ["Rajiv", 35],
        ["Sonia", 20],
        ["Aby", 70],
        ["Abba", 90],
    ], columns=["name", "age"])
    db = make_db()
    db = db.add_dfs({"people": input_df})

    seniors = where(T.people, is_senior)
    ordered = order_by(seniors, "name", True)
    act = db.query(ordered)

    exp_df = DF([
        ["Abba", 90],
        ["Aby", 70],
    ], columns=["name", "age"])

    assert_frame_equal(act.df(), exp_df)


def test_multiple_queries_table_format():
    people_df = DF([
        ["Rajiv", 35],
        ["Sonia", 20],
        ["Aby", 70],
        ["Abba", 90],
    ], columns=["name", "age"])
    db = make_db()
    people = table(people_df, db)
    seniors = where(people, is_senior)
    ordered = order_by(seniors, "name", True)

    exp_df = DF([
        ["Abba", 90],
        ["Aby", 70],
    ], columns=["name", "age"])

    assert_frame_equal(ordered.run().df(), exp_df)
    assert_frame_equal(ordered().df(), exp_df)


def test_no_db_table():
    people_df = DF([
        ["Rajiv", 35],
        ["Sonia", 20],
        ["Aby", 70],
        ["Abba", 90],
    ], columns=["name", "age"])
    people = table(people_df)
    seniors = where(people, is_senior)
    ordered = order_by(seniors, "name", True)

    exp_df = DF([
        ["Abba", 90],
        ["Aby", 70],
    ], columns=["name", "age"])

    assert_frame_equal(ordered().df(), exp_df)


def test_join_inner():
    data_courses = {
        'Courses': ["Spark", "PySpark", "Python", "pandas"],
        'Fee': [20000, 25000, 22000, 30000],
        'Duration': ['30days', '40days', '35days', '50days'],
        'Course_ID': ['r1', 'r2', 'r3', 'r4']
    }
    courses = pd.DataFrame(data_courses)

    data_discounted_courses = {
        'Courses': ["Spark", "Java", "Python", "Go"],
        'Discount': [2000, 2300, 1200, 2000],
        'Course_ID': ['r1', 'r6', 'r3', 'r5']
    }
    discounted_courses = pd.DataFrame(data_discounted_courses)
    db = make_db()
    db = db.add_dfs({"courses": courses, "discounted_courses": discounted_courses})

    discounted_courses = join_inner(T.courses, T.discounted_courses, 'Course_ID' )
    # join_inner(_, T.discounted_courses, 'Course_ID' )
    # _.join_inner(T.discounted_courses, 'Course_ID' )
    # _ | table_b.join_left(_, 'Course_ID' )

    exp_df = DF([
        ["Spark", 20000, "30days", "r1", "Spark", 2000],
        ["Python", 22000, "35days", "r3", "Python", 1200]

    ], columns=['Courses_x', 'Fee', 'Duration', 'Course_ID', "Courses_y", "Discount"])

    act = db.query(discounted_courses)
    assert_frame_equal(act.df(), exp_df)

def test_rename():
    data = [
        ["Rajiv", 35],
        ["Sonia", 40],
        ["Aby", 70]
    ]
    input_df = DF(data, columns=["name", "age"])
    t = table(input_df)
    r = rename(t, {"name": "new_name", "age": "new_age"})
    exp_df = DF(data, columns=["new_name", "new_age"])
    assert_frame_equal(r().df(), exp_df)

def test_select():
    data = [
        ["Rajiv", 35, "Toronto"],
        ["Sonia", 40, "Toronto"],
        ["Aby", 70, "Scarborough"]
    ]
    input_df = DF(data, columns=["name", "age","location"])
    t = table(input_df)

    r = select(t, "name", "location")

    exp_df = input_df[["name", "location"]]
    assert_frame_equal(r().df(), exp_df)


def test_map_new_column():
    input_df = DF([
        ["Rajiv", 35],
        ["Sonia", 40],
        ["Aby", 70]
    ], columns=["name", "age"])

    db = make_db()
    db = db.add_dfs({"people": input_df})

    doubles = map(T.people, double_age, "double_age")
    act = db.query(doubles)

    exp_df = DF([
        ["Rajiv", 35, 70],
        ["Sonia", 40, 80],
        ["Aby", 70, 140]
    ], columns=["name", "age", "double_age"])

    assert_frame_equal(act.df(), exp_df)

    exp_df_same_column = DF([
        ["Rajiv", 70],
        ["Sonia", 80],
        ["Aby", 140]
    ], columns=["name", "age"])

    doubles_edit_column = map(T.people, double_age, "age")
    act_edit_column = db.query(doubles_edit_column)
    assert_frame_equal(act_edit_column.df(), exp_df_same_column)


def test_map_same_column():
    input_df = DF([
        ["Rajiv", 35],
        ["Sonia", 40],
        ["Aby", 70]
    ], columns=["name", "age"])

    db = make_db()
    db = db.add_dfs({"people": input_df})

    exp_df_same_column = DF([
        ["Rajiv", 70],
        ["Sonia", 80],
        ["Aby", 140]
    ], columns=["name", "age"])
    doubles_edit_column = map(T.people, double_age, "age")
    act_edit_column = db.query(doubles_edit_column)
    assert_frame_equal(act_edit_column.df(), exp_df_same_column)


def test_agg_format():
    def add(col): return col.sum()

    input_df = pd.DataFrame([
        ["toronto", 10],
        ["montreal", 20],
        ["toronto", 30],
        ["halifax", 5]
    ], columns=["location", "population"])

    people = table(input_df)
    total = agg(people, add, "population")
    exp_df = DF([
        [65],
    ], columns=["add"])

    assert_frame_equal(total.run().df(), exp_df)

    total_by_location = agg(people, add, "population", by=["location"])
    exp_df_by_location = pd.DataFrame([
        ["halifax", 5],
        ["montreal", 20],
        ["toronto", 40]
    ], columns=["location", "add"])
    assert_frame_equal(total_by_location().df(), exp_df_by_location)

    ## many columns
    input_data = [
        ["ontario", "toronto", 2020, 100],
        ["quebec", "montreal", 2020, 50],
        ["ontario", "ottawa", 2020, 200],
        ["alberta", "calgary", 2020, 25],
        ["quebec", "quebec city", 2020, 50],
        ["ontario", "toronto", 2021, 100],
        ["quebec", "montreal", 2021, 50],
        ["ontario", "ottawa", 2021, 200],
        ["alberta", "calgary", 2021, 25],
        ["quebec", "quebec city", 2021, 50],
    ]
    input_df = pd.DataFrame(data=input_data, columns=["province", "city", "year", "population"])
    people = table(input_df)
    total_by_province_and_city = agg(people, add, "population", by=["province", "city"])
    exp_data = [['alberta', 'calgary', 50],
                ['ontario', 'ottawa', 400],
                ['ontario', 'toronto', 200],
                ['quebec', 'montreal', 100],
                ['quebec', 'quebec city', 100]]
    exp_df_by_province_and_city = pd.DataFrame(exp_data, columns=["province", "city", "add"])
    assert_frame_equal(total_by_province_and_city().df(), exp_df_by_province_and_city)

# def test_limit():
#     cols = ["name", "age"]
#     df = DF([
#         ["Rajiv", 35],
#         ["Sonia", 20],
#         ["Aby", 70],
#         ["Abba", 90],
#     ], columns=cols)
#
#     cols = ["name", "age"]
#     exp_df = DF([
#         ["Rajiv", 35],
#         ["Sonia", 20],
#     ], columns=cols)
#
#     result = limit(table(df), 2)
#
#     assert_frame_equal(result().df(), exp_df)


# # Define the test function
# def test_recursion():
#     data = [
#         ["Alice", "Carol"],
#         ["Bob", "Carol"],
#         ["Carol", "Dave"],
#         ["Carol", "George"],
#         ["Dave", "Mary"],
#         ["Eve", "Mary"],
#         ["Mary", "Frank"],
#     ]
#
#
#     input_df = DF(data, columns=["parent", "child"])
#     parent_of = table(input_df)
#
#     frank_parent = parent_of | where(_, lambda r: r.child == "Frank") | select(_, "parent")
#     is_ancestor = lambda r: r.parent == r.child
#     get_ancestors = _ | join_inner(_ , parent_of) | where(_, is_ancestor) | select(_, "parent")
#     result = recurse(frank_parent, get_ancestors)
#
#
#     # Define the expected result DataFrame
#     exp_df = pd.DataFrame()
#
#     # # Assert that the result matches the expected result
#     # pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_result.reset_index(drop=True))
#     assert_frame_equal(result().df(), exp_df)


def find_staff(manager_id, df):
    staff = df[df['manager_id'] == manager_id]

    if staff.empty:
        return None

    result = pd.DataFrame()

    # Check if the manager itself is in the staff DataFrame
    manager = df[df['staff_id'] == manager_id]
    if not manager.empty:
        result = pd.concat([result, manager])

    for _, row in staff.iterrows():
        sub_staff = find_staff(row['staff_id'], df)
        if sub_staff is not None:
            result = pd.concat([result, sub_staff, staff])  # Include the entire staff DataFrame of the current manager

    return result



def double_age(r: Row[C.age: int]) -> int:
    return r.age * 2


def is_senior(r: Row[C.age: int, C.name: str]) -> bool:
    return r['age'] > 35

