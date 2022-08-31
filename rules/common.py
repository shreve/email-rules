"""
Model for understanding Common config files.

    rules.yml

"""

from typing import Union, List
from ruamel.yaml import YAML
from pydantic import BaseModel, Field

from rules.ruleset import Ruleset

yaml = YAML(typ="safe")


class CommonMatch(BaseModel):
    """Data used to generate a match."""

    fromin: List[str] = []
    from_: List[str] = Field([], alias="from")
    to: List[str] = []
    subject: List[str] = []
    body: List[str] = []
    list: List[str] = []
    headers: List[str] = []


class CommonRule(BaseModel):
    """An individual Common rule."""

    name: Union[str, None]
    match: CommonMatch
    folder: Union[str, None]
    label: Union[str, None]
    redirect: Union[List[str], None]
    mark_read: Union[bool, None]
    notify: Union[bool, None]
    archive: Union[bool, None]


class CommonRuleset(Ruleset):
    """A collection of Common rules."""

    rules: List[CommonRule]
    rule_class = CommonRule
    file_loader = yaml
    default_filename = "rules.yaml"

    suffix = ".yaml"

    def convert_to_common(self):
        """Convert to a CommonRuleset."""

        return self
