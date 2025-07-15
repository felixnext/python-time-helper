"""Various Const Formats."""

DATE_FORMATS = [
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y.%m.%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y.%m.%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%dT%H:%M",
    "%Y.%m.%d %H:%M",
    "%Y-%m-%d",
    "%Y.%m.%d",
    "%m-%d-%Y",
    "%m/%d/%Y",
    "%m/%d/%y",
    "%d.%m.%Y",
    "%m.%d.%Y",
    # ISO 8601 with Z suffix (although isoparse handles these, good for fallback)
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%SZ",
]
