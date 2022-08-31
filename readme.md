Email Rules
===========

I mean, email is ok. It could be better though.

This project makes it easier to generate auto sorting rules for your Fastmail
account. Here's the schema for a common ruleset:

```yaml
# rules.yaml
- name: Mostly useless name for this rule

  # Where should this message go?
  folder: Folder
  label: Label
  redirect:
    - redirect@example.com

  # What should happen to this message?
  mark_read: true
  archive: true
  notify: true

  # Which messages should this apply to?
  match:
    to:
      - me@example.com
    from:
      - shipments@example.com
    subject:
      - Order received
    body:
      - Track package
    headers:
      - List-Id
    list:
      - listserve.email.marketing.example.com
    fromin:
      - contacts
```

`rules.example.yaml` is full of examples that I think would work well for most
people, or would at least be a good starting point. I've edited it and ignored
`rules.yaml` because mine contained somewhat private info, like the Shop app
forwarding email.

## Usage

```
$ python -m rules -h
usage: __main__.py [-h] [--from {common,gmail,fastmail}] --to {common,gmail,fastmail} {convert} filename

Common email filtering rules

positional arguments:
  {convert}             Command to run
  filename              The filename to convert

optional arguments:
  -h, --help            show this help message and exit
  --from {common,gmail,fastmail}
                        The source ruleset type
  --to {common,gmail,fastmail}
                        The destination ruleset type
```
