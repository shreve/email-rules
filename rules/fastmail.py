"""
Model for understanding Fastmail config files.

    mailrules.json

"""

import json
from datetime import datetime
from typing import Union, List
from pydantic import BaseModel, Field

from rules.common import CommonRule, CommonMatch
from rules.ruleset import Ruleset


class FastmailRule(BaseModel):
    """An individual Fastmail mail routing rule."""

    # What's this rule about?
    name: str

    # What are we looking for in the message?
    combinator: str
    search: str
    conditions: Union[str, None]
    previousFileInName: Union[str, None]

    # Where should this message go?
    fileIn: Union[str, None]  # label or folder
    discard: bool  # delete
    redirectTo: Union[List[str], None]
    snoozeUntil: Union[dict, None]

    # What should we do with this message?
    markFlagged: bool
    markRead: bool
    markSpam: bool
    showNotification: bool
    skipInbox: bool  # archive

    # Can we do anything else after this rule?
    stop: bool

    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)

    @classmethod
    def from_common_rule(cls, rule: CommonRule) -> "FastmailRule":
        """Convert a CommonRule to a FastmailRule."""

        return cls(
            name=rule.name,
            combinator="any",
            search=generate_search(rule.match),
        )


class FastmailRuleset(Ruleset):
    """A collection of Fastmail rules."""

    rules: List[FastmailRule]
    rule_class = FastmailRule
    file_loader = json
    default_filename = "mailrules.json"

    suffix = ".json"

    @classmethod
    def from_common_ruleset(cls, ruleset: "CommonRuleset") -> "FastmailRuleset":
        """Convert a CommonRuleset to a FastmailRuleset."""

        return cls(
            rules=[FastmailRule.from_common_rule(rule) for rule in ruleset.rules]
        )


def generate_search(match: CommonMatch) -> str:
    """Convert a match into a search query"""

    query = ""
    return query
    # for (key, values) in match.dict().items():


# def generate_search(params)
#   params.map do |field, values|
#     values.map do |value|
#       if value.include?(" ")
#         value = "(#{value})"
#       end
#       "#{field}:#{value}"
#     end
#   end.flatten.join(" OR ")
# end
