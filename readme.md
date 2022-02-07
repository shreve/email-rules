Email Rules
===========

I mean, email is ok. It could be better though.

This project makes it easier to generate auto sorting rules for your Fastmail
account. For example, 

```yaml
# rules.yaml
- mailbox: Mailbox Name
  mark_read: false
  notify: true
  match:
    to:
      - me@example.com
    from:
      - Marketer
    subject:
      - Order received
    body:
      - Track package
    headers:
      - List-Id
```

`rules.example.yaml` is full of examples that I think would work well for most
people, or would at least be a good starting point. I've edited it and ignored
`rules.yaml` because mine contained somewhat private info, like the Shop app
forwarding email.

## Usage

1. Copy `rules.example.yaml` to `rules.yaml` or let the script do it for you
2. Edit the rules as you see fit
3. Run `ruby email.rb`
4. Import to Fastmail at https://www.fastmail.com/settings/filters
