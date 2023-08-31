I took a career break to build this. If you like it and are looking to hire a ML engineer, please contact me :) 

CAUTION: PROTOTYPE! NO PRODUCTION USE, not even development. 

Merdb is a data processing library that
* is a relational api like SQL to query data
* has Unix like pipes to compose operators using the `|` syntax
* scales to multi core or a cluster(via Modin)
* processes data too big to fit into memory
* support interactive and optimized processing(optimizations in roadmap)

# Install
```shell
pip install merdb
```
# Example

```python
import pandas as pd
from merdb.interactive import *
# for lazy(TBD) use `from merdb.lazy import *`

def is_senior(row) -> bool:
    return row['age'] > 35


def double_age(row) -> int:
    return row["age"] * 2


cols = ["name", "age"]
people_df = pd.DataFrame([
    ["Raj", 35],
    ["Sona", 20],
    ["Abby", 70],
    ["Abba", 90],
], columns=cols)

# One can specify functions without any source data like quadruple age
quadruple_age = map(double_age, "age") | map(double_age, "age")

result = (t(people_df) # convert people_df to a merdb table
          | where(is_senior)
          | order_by("name", "asc")
          | quadruple_age # Unix like pipe syntax making it easy to refactor out intermediate processing
          | select("age")
          | rename({"age": "new_age"})
          )

# Convert to Pandas Dataframe and print
print(result.df())

```

