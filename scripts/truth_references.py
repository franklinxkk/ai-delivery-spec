"""Read Product Truth references with their owning record and source location."""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any, NamedTuple


# These records live in separate review/change artifacts or a secret registry.
EXTERNAL_ID_PATTERNS = {
    "review_refs": re.compile(r"REVIEW-[A-Z0-9]+(?:-[A-Z0-9]+)*"),
    "change_refs": re.compile(r"CHG-[A-Z0-9]+(?:-[A-Z0-9]+)*"),
    "secret_refs": re.compile(r"SECRET-[A-Z0-9-]+"),
}


class Reference(NamedTuple):
    owner: str | None
    field: str
    target: str
    path: str

    @property
    def external(self) -> bool:
        return self.field in EXTERNAL_ID_PATTERNS

    @property
    def valid_locator(self) -> bool:
        return bool(EXTERNAL_ID_PATTERNS[self.field].fullmatch(self.target))

    def record(self) -> dict[str, str | None]:
        target = self.target
        if self.field == "secret_refs" and not self.valid_locator:
            target = "<invalid secret locator>"
        return {"from_id": self.owner, "source": self.field, "to_id": target, "path": self.path}


def iter_references(value: Any, owner: str | None = None, path: str = "") -> Iterator[Reference]:
    if isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_references(item, owner, f"{path}[{index}]")
    elif isinstance(value, dict):
        if isinstance(value.get("id"), str):
            owner = value["id"]
        for key, child in value.items():
            if not isinstance(key, str):
                continue
            location = f"{path}.{key}" if path else key
            if (key.endswith("_ref") or key == "supersedes") and isinstance(child, str):
                yield Reference(owner, key, child, location)
            elif (key.endswith("_refs") or key == "editable_by") and isinstance(child, list):
                for index, target in enumerate(child):
                    if isinstance(target, str):
                        yield Reference(owner, key, target, f"{location}[{index}]")
            else:
                yield from iter_references(child, owner, location)
