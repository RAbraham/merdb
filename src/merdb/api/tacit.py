import merdb.api.base as b
import merdb.resource as r


# TODO: duplication in filter_with, order_by etc.?

def make_tacit(func):
    return lambda *args, **kwargs: TacitOperation(func, *args, **kwargs)

mt = make_tacit
agg = mt(b.agg)
where = mt(b.where)
order_by = mt(b.order_by_str)
map = mt(b.map)
join_inner = mt(b.join_inner)
join_cross = mt(b.join_cross)
select = mt(b.select)
rename = mt(b.rename)
show = mt(b.show)



def table(df):
    return TacitTable(df)

class CompositeTacitOperation:
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2  = op2

    def operate(self, source):
        return self.op2.operate(self.op1.operate(source))

    def __or__(self, op):
        c = CompositeTacitOperation(self, op)
        return c



class TacitOperation:
    def __init__(self, op, *args, **kwargs):
        self.op = op
        self.args = args
        self.kwargs = kwargs

    def operate(self, source):
        return self.op(source, *self.args, **self.kwargs)

    def __or__(self, op):
        c = CompositeTacitOperation(self, op)
        return c


class TacitTable:
    def __init__(self, df):
        self.df = df
        self.table = r.table
        self.source= self.table(df)

    def __or__(self, op):
        self.source = op.operate(self.source)
        return self

    def __call__(self, *args, **kwargs):
        return self.source()

