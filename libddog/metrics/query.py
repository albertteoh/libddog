import enum
from typing import Any, Dict, List, Optional

from libddog.common.bases import Renderable


class QueryNode:
    def codegen(self) -> str:
        raise NotImplemented


class Metric(QueryNode):
    def __init__(self, *, name: str) -> None:
        self.name = name

    def codegen(self) -> str:
        return self.name


class FilterOperator(enum.Enum):
    EQUAL = 1
    NOT_EQUAL = 2


class FilterCond(QueryNode):
    pass


class Tag(FilterCond):
    def __init__(
        self, *, tag: str, value: str, operator: FilterOperator = FilterOperator.EQUAL
    ) -> None:
        self.tag = tag
        self.value = value
        self.operator = operator

    def codegen(self) -> str:
        key = self.tag

        if self.operator is FilterOperator.NOT_EQUAL:
            key = f"!{key}"

        return f"{key}:{self.value}"


class TmplVar(FilterCond):
    """A filter using a template variable."""

    def __init__(self, *, tvar: str) -> None:
        assert not tvar.startswith("$")

        self.tvar = tvar

    def codegen(self) -> str:
        return "$%s" % self.tvar


class Filter(QueryNode):
    def __init__(self, *, conds: List[FilterCond]) -> None:
        self.conds = conds

    def codegen(self) -> str:
        return "{%s}" % ", ".join((cond.codegen() for cond in self.conds))

    def __and__(self, other: Optional["Filter"]) -> "Filter":
        if other:
            conds = self.conds + other.conds
            return self.__class__(conds=conds)

        return self


class AggFunc(enum.Enum):
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    SUM = "sum"

    def codegen(self) -> str:
        return self.value


class By(QueryNode):
    def __init__(self, *, tags: List[str]) -> None:
        self.tags = tags

    def codegen(self) -> str:
        return " by {%s}" % ", ".join((tag for tag in self.tags))


class As(enum.Enum):
    RATE = "rate"
    COUNT = "count"

    def codegen(self) -> str:
        return ".as_%s()" % self.value


class Aggregation(QueryNode):
    def __init__(
        self, *, func: AggFunc, by: Optional[By] = None, as_: Optional[As] = None
    ) -> None:
        self.func = func
        self.by = by
        self.as_ = as_  # 'as' is a keyword in Python


class RollupFunc(enum.Enum):
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    SUM = "sum"
    COUNT = "count"
    DEFAULT = ""  # yes, it's supposed to be the empty string

    def codegen(self) -> str:
        return self.value


class QueryFunc(QueryNode):
    pass


class Rollup(QueryFunc):
    def __init__(self, *, func: RollupFunc, period_s: Optional[int] = None) -> None:
        self.func = func
        self.period_s = period_s

    def codegen(self) -> str:
        period_s = "%s" % self.period_s if self.period_s else ""
        args = [
            self.func.codegen(),
            period_s,
        ]
        args = [arg for arg in args if arg]

        # func == DEFAULT and period_s unset
        if not args:
            return ""

        return ".rollup(%s)" % ", ".join(args)


class FillFunc(enum.Enum):
    LINEAR = "linear"
    LAST = "last"
    ZERO = "zero"
    NULL = "null"


class Fill(QueryFunc):
    def __init__(self, *, func: FillFunc, limit_s: int = 300) -> None:
        self.func = func
        self.limit_s = limit_s

    def codegen(self) -> str:
        limit_s = "%s" % self.limit_s if self.limit_s else ""
        args = [self.func.value, limit_s]
        args = [arg for arg in args if arg]
        return ".fill(%s)" % ", ".join(args)


class Query(QueryNode, Renderable):
    _instance_counter = 1

    def __init__(
        self,
        *,
        metric: Metric,
        filter: Optional[Filter] = None,
        agg: Aggregation,
        funcs: Optional[List[QueryFunc]] = None,
        name: Optional[str] = None,
        data_source: str = "metrics",
        aggregator: str = "unused",  # TODO: remove
        query: str = "unused",  # TODO: remove
    ) -> None:
        self.metric = metric
        self.filter = filter
        self.agg = agg
        self.funcs = funcs or []
        self.name = name or self.get_next_unique_name()
        self.data_source = data_source
        self.aggregator = aggregator
        self.query = query

    def get_next_unique_name(self) -> str:
        counter = self.__class__._instance_counter
        self.__class__._instance_counter += 1
        return "q%s" % counter

    def codegen(self) -> str:
        agg_func = self.agg.func.codegen()
        agg_by = self.agg.by.codegen() if self.agg.by else ""
        agg_as = self.agg.as_.codegen() if self.agg.as_ else ""
        metric = self.metric.codegen()
        filter = self.filter.codegen() if self.filter else ""

        funcs = "".join([func.codegen() for func in self.funcs])

        query = "%s:%s%s%s%s%s" % (
            agg_func,
            metric,
            filter,
            agg_by,
            agg_as,
            funcs,
        )

        return query

    def as_dict(self) -> Dict[str, Any]:
        dct = {
            "aggregator": self.agg.func.value,
            "data_source": self.data_source,
            "name": self.name,
            "query": self.codegen(),
        }

        return dct
