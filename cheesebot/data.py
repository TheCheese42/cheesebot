import json
from enum import IntEnum
from pathlib import Path
from typing import Any


class DataType(IntEnum):
    JSON = 0

    @property
    def ext(self):
        if self == self.JSON:
            return ".json"

    @property
    def deserialize(self):
        if self == self.JSON:
            return json.loads


def get_data(data: str, type_: DataType) -> Any:
    """
    Retrieve data from the data directory.

    :param data: The filename without the extension.
    :type data: str
    :param type_: The type of the data to be requested.
    :type type_: DataType
    :returns: The result of deserializing the acquired data.
    :rtype: Any
    """
    with open(
        Path(__file__).parent / "data" / f"{data}{type_.ext}",
        "r",
        encoding="utf-8",
    ) as fp:
        file_content = fp.read()

    deserialized = type_.deserialize(file_content)
    return deserialized
