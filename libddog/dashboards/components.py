from typing import Any, Dict, List, Optional, Sequence, Set

from libddog.common.bases import Renderable
from libddog.common.errors import UnresolvedFormulaIdentifiers
from libddog.common.types import JsonDict
from libddog.dashboards.enums import (
    Comparator,
    ConditionalFormatPalette,
    DisplayType,
    LineType,
    LineWidth,
    Palette,
    Scale,
)
from libddog.metrics.query import Query
from libddog.parsing.parse_formula import parse_formula_identifiers


class Size:
    def __init__(
        self, *, width: Optional[int] = None, height: Optional[int] = None
    ) -> None:
        self.width = width
        self.height = height

    @classmethod
    def get_defaults(cls) -> Dict[Any, Any]:
        from libddog.dashboards.widgets import Note, QueryValue, Timeseries

        return {
            Note: (2, 2),
            QueryValue: (2, 2),
            Timeseries: (4, 2),
            # add remaining widget types...
        }

    @classmethod
    def backfill(cls, obj: Any, instance: Optional["Size"]) -> "Size":
        instance = cls() if instance is None else instance

        defaults = cls.get_defaults()
        dims = defaults.get(obj.__class__)
        if dims:
            width, height = dims
            if not instance.width:
                instance.width = width
            if not instance.height:
                instance.height = height

            return instance

        raise NotImplementedError


class Position:
    def __init__(self, *, x: Optional[int] = 0, y: Optional[int] = 0) -> None:
        self.x = x
        self.y = y


class Layout(Renderable):
    def __init__(self, *, size: Size, pos: Position) -> None:
        self.size = size
        self.pos = pos

    def as_dict(self) -> JsonDict:
        return {
            "layout": {
                "x": self.pos.x,
                "y": self.pos.y,
                "width": self.size.width,
                "height": self.size.height,
            },
        }


class Style(Renderable):
    def __init__(
        self,
        *,
        line_type: LineType = LineType.SOLID,
        line_width: LineWidth = LineWidth.NORMAL,
        palette: Palette = Palette.CLASSIC,
    ) -> None:
        self.line_type = line_type
        self.line_width = line_width
        self.palette = palette

    def as_dict(self) -> JsonDict:
        return {
            "line_type": self.line_type.value,
            "line_width": self.line_width.value,
            "palette": self.palette.value,
        }


class YAxis(Renderable):
    def __init__(
        self,
        *,
        include_zero: bool = True,
        scale: Scale = Scale.LINEAR,
        label: str = "",
        min: Optional[int] = None,
        max: Optional[int] = None,
    ) -> None:
        self.include_zero = include_zero
        self.scale = scale
        self.label = label
        self.min = min
        self.max = max

    def as_dict(self) -> JsonDict:
        return {
            "include_zero": self.include_zero,
            "scale": self.scale.value,
            "label": self.label,
            "min": str(self.min) if self.min is not None else "auto",
            "max": str(self.max) if self.max is not None else "auto",
        }


class Formula(Renderable):
    def __init__(self, text: str, alias: Optional[str] = None) -> None:
        self.text = text
        self.alias = alias

    def validate(self, queries: List[Query]) -> None:
        idents = parse_formula_identifiers(self.text)

        resolved_idents: Set[str] = set()
        for ident in idents:
            for query in queries:
                if query.name == ident:
                    resolved_idents.add(ident)

        missing_idents = idents - resolved_idents
        if missing_idents:
            raise UnresolvedFormulaIdentifiers(
                "identifiers %r not present in %r" % (missing_idents, self.text)
            )

    def as_dict(self) -> JsonDict:
        dct = {"formula": self.text}
        if self.alias:
            dct["alias"] = self.alias

        return dct


class ConditionalFormat(Renderable):
    def __init__(
        self, *, comparator: Comparator, value: float, palette: ConditionalFormatPalette
    ) -> None:
        self.comparator = comparator
        self.value = value
        self.palette = palette

    def as_dict(self) -> JsonDict:
        return {
            "comparator": self.comparator.value,
            "value": self.value,
            "palette": self.palette.value,
        }


class Request(Renderable):
    def __init__(
        self,
        *,
        title: Optional[str] = None,
        query: Optional[Query] = None,
        queries: Optional[List[Query]] = None,
        formulas: Optional[List[Formula]] = None,
        conditional_formats: Optional[Sequence[ConditionalFormat]] = None,
        display_type: DisplayType = DisplayType.LINES,
        style: Optional[Style] = None,
        on_right_yaxis: bool = False,
    ) -> None:
        assert query or queries

        self.title = title
        self.query = query
        self.queries = queries or [query]
        self.formulas = formulas or []
        self.conditional_formats = conditional_formats or []
        self.display_type = display_type
        self.style = style or Style()
        self.on_right_yaxis = on_right_yaxis

    def as_dict(self) -> JsonDict:
        # if we have only queries but no formulas then synthesize a formula per query
        formulas = self.formulas
        if not formulas:
            for query in self.queries:
                formula = Formula(text="%s" % query.name, alias=self.title)
                formulas.append(formula)

        # validate that variables used in formula correspond to query names
        for formula in formulas:
            formula.validate(self.queries)

        formula_dicts = [form.as_dict() for form in formulas]
        query_dicts = [query.as_dict() for query in self.queries]

        return {
            "conditional_formats": [cf.as_dict() for cf in self.conditional_formats],
            "display_type": self.display_type.value,
            "formulas": formula_dicts,
            "on_right_yaxis": self.on_right_yaxis,
            "queries": query_dicts,
            "style": self.style.as_dict(),
        }


class TemplateVariableDefinition(Renderable):
    def __init__(self, *, name: str, tag: str, default_value: str) -> None:
        self.name = name
        self.tag = tag
        self.default_value = default_value

    def as_dict(self) -> JsonDict:
        return {"name": self.name, "prefix": self.tag, "default": self.default_value}


class PopulatedTemplateVariable(Renderable):
    def __init__(self, *, tmpl_var: TemplateVariableDefinition, value: str) -> None:
        self.tmpl_var = tmpl_var
        self.value = value

    def as_dict(self) -> JsonDict:
        return {"name": self.tmpl_var.name, "value": self.value}


class TemplateVariablesPreset(Renderable):
    def __init__(
        self, *, name: str, populated_vars: List[PopulatedTemplateVariable]
    ) -> None:
        self.name = name
        self.populated_vars = populated_vars

    def as_dict(self) -> JsonDict:
        return {
            "name": self.name,
            "template_variables": [tmp.as_dict() for tmp in self.populated_vars],
        }
