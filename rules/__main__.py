"""The main rule program."""

import sys
import argparse
from pathlib import Path

from rules.gmail import GmailRuleset
from rules.fastmail import FastmailRuleset
from rules.common import CommonRuleset

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Common email filtering rules")

    parser.add_argument(
        "command",
        help="Command to run",
        choices=["convert"],
    )
    parser.add_argument(
        "filename",
        help="The filename to convert",
        type=Path,
    )
    parser.add_argument(
        "--from",
        help="The source ruleset type",
        choices=["common", "gmail", "fastmail"],
        dest="source",
    )
    parser.add_argument(
        "--to",
        help="The destination ruleset type",
        choices=["common", "gmail", "fastmail"],
        required=True,
    )

    args = parser.parse_args()

    if args.command == "convert":

        # Make sure the source file exists.
        if not args.filename.exists():
            print(f"{args.filename} does not exist")
            sys.exit(1)

        # Type to detect the source from the filename.
        if not args.source:
            for type_ in ["common", "gmail", "fastmail"]:
                if type_ in args.filename.name:
                    args.source = type_
                    break

        # Check to make sure we have work to do.
        if args.source == args.to:
            print("Source and destination formats are the same. No convertion needed.")
            sys.exit(1)

        # Load the ruleset
        if args.source == "common" or args.source is None:
            ruleset = CommonRuleset.load(args.filename)
        elif args.source == "gmail":
            ruleset = GmailRuleset.load(args.filename)
        elif args.source == "fastmail":
            ruleset = FastmailRuleset.load(args.filename)

        # Always convert to the common format first
        common_ruleset = ruleset.convert_to_common()

        # Convert to the destination format
        if args.to == "common":
            new_ruleset = common_ruleset
        elif args.to == "gmail":
            new_ruleset = GmailRuleset.from_common_ruleset(common_ruleset)
        elif args.to == "fastmail":
            new_ruleset = FastmailRuleset.from_common_ruleset(common_ruleset)

        # Make sure we save to an appropriate destination with extension and label.
        dest = args.filename.with_name(
            "".join([args.filename.stem, ".", args.to, new_ruleset.suffix])
        )
        new_ruleset.save(dest)
        print(f"Saved to {dest}")
