import tomllib
from pathlib import Path

DEFAULT_LANGUAGE = "en_US"


class Language:
    def __init__(self, dict_: dict[str, str]):
        for key, value in dict_["meta"].items():
            setattr(self, key, value)
        self.strings = dict_["strings"]

    def __getitem__(self, key: str) -> str:
        return self.strings[key]


class LangManager:
    langs_path: Path = Path(__file__).parent / "langs"

    def __init__(self):
        self.langs: dict[str, Language] = {}
        for code in get_available_langcodes():
            self.add_language_from_langcode(code)

    def get(self, key: str, code: str):
        try:
            language = self.langs[code]
        except KeyError:
            raise ValueError(f"Invalid langcode {code}")
        try:
            out = language[key]
        except KeyError:
            if code == DEFAULT_LANGUAGE:
                raise ValueError(f"Invalid language key {key}")
            out = self.get_from_default(key)
        return out

    def get_from_default(self, key: str) -> str:
        return self.get(key, DEFAULT_LANGUAGE)

    def add_language_from_dict(self, dict_: dict[str, str]) -> None:
        language = Language(dict_)
        self.langs[language.langcode] = language

    def add_language_from_toml(self, toml_str: str) -> None:
        return self.add_language_from_dict(tomllib.loads(toml_str))

    def add_language_from_file(self, file: Path | str) -> None:
        with open(file, mode="r", encoding="utf-8") as fp:
            return self.add_language_from_toml(fp.read())

    def add_language_from_langcode(self, langcode: str) -> None:
        return self.add_language_from_file(
            self.langs_path / f"{langcode}.toml"
        )


def get_available_langcodes() -> list[str]:
    path = LangManager.langs_path
    codes = []
    for file in path.iterdir():
        if not file.is_file():
            continue
        if file.suffix == ".toml":
            codes.append(file.stem)
    return codes
