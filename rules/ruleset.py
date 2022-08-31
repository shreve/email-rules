"""Base class for loading a set of rules."""

from typing import List, Callable, Any


class Ruleset:
    """A collection of rules."""

    rule_class: Callable
    rules: List
    default_filename: str
    file_loader: Any

    def __init__(self, rules: List):
        self.rules = rules

    @classmethod
    def load(cls, filename=None):
        """Load a list of files from a JSON file."""

        if not filename:
            filename = cls.default_filename

        with open(filename, encoding="utf-8") as file:
            return cls(
                rules=list(
                    map(
                        lambda x: cls.rule_class(**x if x else None),
                        cls.file_loader.load(file),
                    )
                )
            )

    def save(self, filename=None):
        """Save a list of files to a JSON file."""

        if not filename:
            filename = self.default_filename

        with open(filename, "w", encoding="utf-8") as file:
            self.file_loader.dump(self.rules, file)

    def convert_to_common(self):
        """Convert to a CommonRuleset."""

        raise NotImplementedError(
            f"Not implemented yet: {self.__class__.__name__}.convert_to_common"
        )
