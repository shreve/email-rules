"""

Much of this is inspired by the following:
    https://github.com/dimagi/gmail-filters/blob/master/gmailfilterxml/xmlschemas.py
"""

import hashlib
from functools import partial
from typing import Union, List
from datetime import datetime
import xml.etree.ElementTree as ET
from pydantic import BaseModel, Field as PydanticField

from eulxml.xmlmap import (
    load_xmlobject_from_file,
    XmlObject,
    StringField,
    NodeListField,
)

from eulxml.xmlmap.fields import SingleNodeManager, Field, DateTimeField

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "apps": "http://schemas.google.com/apps/2006",
}
UTCDATETIMEFORMAT = "%Y-%m-%dT%H:%M:%S"


class GmailRule(BaseModel):
    """An individual Gmail mail routing rule."""

    title: Union[str, None]
    id: Union[str, None]
    updated: datetime

    from_: Union[str, None] = PydanticField(None, alias="from")
    subject: Union[str, None]
    to: Union[str, None]
    hasTheWord: Union[str, None]
    doesNotHaveTheWord: Union[str, None]

    label: Union[str, None]

    shouldArchive: Union[bool, None]
    shouldMarkAsRead: Union[bool, None]
    shouldNeverSpam: Union[bool, None]
    shouldAlwaysMarkAsImportant: Union[bool, None]
    shouldNeverMarkAsImportant: Union[bool, None]

    size: Union[float, None]

    # One of s_ss (smaller) or s_sl (larger) is required
    sizeOperator: str = "s_sl"
    # One of s_sb (bytes) s_skb (kilobytes) or s_smb (megabytes)
    sizeUnit: str = "s_smb"

    # These are the gmail properties that we can set on an entry.
    PROPERTIES = [
        "from",
        "subject",
        "to",
        "hasTheWord",
        "doesNotHaveTheWord",
        "label",
        "shouldArchive",
        "shouldMarkAsRead",
        "shouldNeverSpam",
        "shouldAlwaysMarkAsImportant",
        "shouldNeverMarkAsImportant",
        "size",
        "sizeOperator",
        "sizeUnit",
    ]

    def __repr__(self):
        body = " ".join([f"{key}={value!r}" for key, value in self.__dict__.items()])
        return f"{self.__class__.__name__}({body})"

    def properties(self) -> List[dict]:
        val = [
            {"name": key, "value": value}
            for key, value in self.dict().items()
            if key in self.PROPERTIES and value is not None
        ]
        if self.from_:
            val.append({"name": "from", "value": self.from_})
        return val


class GmailRuleset(BaseModel):
    """A collection of Gmail rules."""

    title: Union[str, None]
    ids: Union[List[str], None]
    updated: datetime
    author: dict

    rules: List[GmailRule] = []

    suffix = ".xml"

    @classmethod
    def load(cls, filename: str = None) -> "GmailRuleset":
        """Load a list of rules from an XML document."""

        if filename is None:
            filename = "mailFilters.xml"

        xml = load_xmlobject_from_file(filename, xmlclass=GmailRulesetFile)

        data = {
            "title": xml.title,
            "ids": xml.ids,
            "updated": xml.updated,
            "author": {"name": xml.author_name, "email": xml.author_email},
            "rules": [],
        }

        for entry in xml.entries:
            rule = GmailRule(
                title=entry.title,
                id=entry.id,
                updated=entry.updated,
                **{prop.name: prop.value for prop in entry.properties},
            )

            data["rules"].append(rule)

        ruleset = cls(**data)

        return ruleset

    @classmethod
    def from_common_ruleset(cls, ruleset: "CommonRuleset") -> "GmailRuleset":
        """Convert a CommonRuleset to a GmailRuleset."""

        data = {
            "title": "Mail Filters",
            "ids": [],
            "updated": datetime.now(),
            "author": {
                "name": "Jacob Shreve",
                "email": "shreve@umich.edu",
            },
            "rules": [],
        }

        for rule in ruleset.rules:
            idx = int.from_bytes(
                hashlib.blake2b(rule.name.encode("utf-8"), digest_size=4).digest(),
                "big",
            )
            grule = GmailRule(
                title=rule.name,
                id=idx,
                updated=datetime.now(),
            )

            if rule.label:
                grule.label = rule.label
            if rule.archive is not None:
                grule.shouldArchive = rule.archive
            if rule.mark_read is not None:
                grule.shouldMarkAsRead = rule.mark_read
            grule.hasTheWord = generate_search(rule.match)

            data["ids"].append(idx)
            data["rules"].append(grule)

        return cls(**data)

    def save(self, filename: str = None) -> None:
        """Save the ruleset to an XML document."""

        if filename is None:
            filename = "gen-mailFilters.xml"

        entries = [
            GmailEntry(
                title=rule.title,
                id=rule.id,
                updated=rule.updated,
                properties=[
                    EntryProperty(**property) for property in rule.properties()
                ],
            )
            for rule in self.rules
        ]

        xml = GmailRulesetFile(
            title=self.title,
            ids=self.ids,
            updated=self.updated,
            author_name=self.author["name"],
            author_email=self.author["email"],
            entries=entries,
        )

        with open(filename, "wb") as file:
            xml.serializeDocument(file, pretty=True)


class EntryPrefixMapper:
    """Map values with a string prefix between XML and python"""

    def __init__(self, prefix):
        self.prefix = prefix

    def to_xml(self, value) -> str:
        if value is None:
            return ""
        if isinstance(value, list):
            value = ",".join(value)
        return f"{self.prefix}{value}"

    def to_python(self, value) -> Union[str, List[str]]:
        if value.text is None:
            return ""
        value = value.text[len(self.prefix) :]
        if "," in value:
            value = value.split(",")
        return value


class UTCDateTimeMapper:
    """Map UTC timestamps between XML and python"""

    def to_xml(self, value) -> str:
        if value is None:
            return ""
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")

    def to_python(self, value) -> datetime:
        return datetime.strptime(value.text, "%Y-%m-%dT%H:%M:%SZ")


SingleNodeField = partial(Field, manager=SingleNodeManager())
EntryIdField = partial(
    SingleNodeField, mapper=EntryPrefixMapper("tag:mail.google.com,2008:filter:")
)
EntryIdListField = partial(
    SingleNodeField, mapper=EntryPrefixMapper("tag:mail.google.com,2008:filters:")
)


class EntryProperty(XmlObject):
    """A GMail filter property tag"""

    ROOT_NAME = "property"
    ROOT_NS = NS["apps"]
    name = StringField("@name")
    value = StringField("@value")


class GmailEntry(XmlObject):
    """A GMail filter entry tag"""

    ROOT_NAME = "entry"
    ROOT_NAMESPACES = NS
    ROOT_NS = NS["atom"]
    ORDER = ("category_term", "title", "id", "updated", "content", "properties")

    category_term = StringField("atom:category/@term")
    content = StringField("atom:content")
    title = StringField("atom:title")
    id = EntryIdField("atom:id")
    updated = DateTimeField("atom:updated", format=UTCDATETIMEFORMAT)
    properties = NodeListField("apps:property", EntryProperty)

    def __init__(self, node=None, context=None, **kwargs):
        if node is None:
            if "category_term" not in kwargs:
                kwargs["category_term"] = "filter"
            if "title" not in kwargs:
                kwargs["title"] = "Mail Filter"
            if "content" not in kwargs:
                kwargs["content"] = ""
        super().__init__(node, context, **kwargs)


class GmailRulesetFile(XmlObject):

    ROOT_NAME = "feed"
    ROOT_NS = NS["atom"]
    ROOT_NAMESPACES = NS
    ORDER = ("title", "ids", "updated", "author_name", "author_email", "entries")

    title = StringField("atom:title")
    ids = EntryIdListField("atom:id")
    updated = DateTimeField("atom:updated", format=UTCDATETIMEFORMAT)
    author_name = StringField("atom:author/atom:name")
    author_email = StringField("atom:author/atom:email")
    entries = NodeListField("atom:entry", GmailEntry)

    def __init__(self, node=None, context=None, **kwargs):
        if node is None and "title" not in kwargs:
            kwargs["title"] = "Mail Filters"
        if node is None and "ids" not in kwargs:
            kwargs["ids"] = list(map(lambda x: x.id, kwargs["entries"]))
        super().__init__(node, context, **kwargs)


def generate_search(match: "CommonMatch") -> str:
    """Convert a match into a search query
    fromin and headers aren't supported by GMail search
    """

    query = []

    def wrap_strings(strings: List[str]) -> List[str]:
        return list(map(lambda x: (f"({x})" if " " in x else x), strings))

    known_fields = ["to", "from_", "subject", "list"]
    for field in known_fields:
        value = getattr(match, field)

        if not value:
            continue

        value = wrap_strings(value)

        if len(value) > 1:
            value = "{" + " ".join(value) + "}"
        else:
            value = value[0]

        if field == "from_":
            field = "from"

        query.append(f"{field}:{value}")

    if match.body:
        query.append(" ".join(wrap_strings(match.body)))

    return " OR ".join(query)
