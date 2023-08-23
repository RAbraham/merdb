from sspipe import p, px
import merdb.api.base as b
import merdb.resource as r

_ = px
def pp(func):
    return lambda *args, **kwargs: p(func, *args, **kwargs)

table = pp(r.table)
filter_with = pp(b.where)
order_by = pp(b.order_by)
limit = pp(b.limit)
map = pp(b.map)
join_inner = pp(b.join_inner)
join_cross = pp(b.join_cross)
select = pp(b.select)
rename = pp(b.rename)
show = pp(b.show)
