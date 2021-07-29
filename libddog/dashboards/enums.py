import enum


class BackgroundColor(enum.Enum):
    BLUE = "blue"
    GREEN = "green"
    ORANGE = "orange"
    PINK = "pink"
    PURPLE = "purple"
    WHITE = "white"
    YELLOW = "yellow"
    VIVID_BLUE = "vivid_blue"
    VIVID_GREEN = "vivid_green"
    VIVID_ORANGE = "vivid_orange"
    VIVID_PINK = "vivid_pink"
    VIVID_PURPLE = "vivid_purple"
    VIVID_YELLOW = "vivid_yellow"
    TRANSPARENT = "transparent"


class Comparator(enum.Enum):
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="


class ConditionalFormatPalette(enum.Enum):
    WHITE_ON_GREEN = "white_on_green"
    WHITE_ON_RED = "white_on_red"
    WHITE_ON_YELLOW = "white_on_yellow"


class DisplayType(enum.Enum):
    LINES = "line"
    AREAS = "area"
    BARS = "bars"


class LayoutType(enum.Enum):
    ORDERED = "ordered"
    # have not validated the other alternatives yet


class LineType(enum.Enum):
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"


class LineWidth(enum.Enum):
    NORMAL = "normal"
    THIN = "thin"
    THICK = "thick"


class Palette(enum.Enum):
    CLASSIC = "dog_classic"
    COOL = "cool"
    WARM = "warm"
    PURPLE = "purple"
    ORANGE = "orange"
    GRAY = "grey"  # yes the typo is intentional lol


class ResponseFormat(enum.Enum):
    SCALAR = "scalar"
    TIMESERIES = "timeseries"
    # have not validated the other alternatives yet


class Scale(enum.Enum):
    LINEAR = "linear"
    LOG = "log"
    POW = "pow"
    SQRT = "sqrt"


class TextAlign(enum.Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class TickEdge(enum.Enum):
    RIGHT = "right"
    LEFT = "left"
    BOTTOM = "bottom"
    TOP = "top"


class TitleAlign(enum.Enum):
    LEFT = "left"
    # have not validated the other alternatives yet


class VerticalAlign(enum.Enum):
    BOTTOM = "bottom"
    CENTER = "center"
    TOP = "top"
