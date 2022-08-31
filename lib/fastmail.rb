class FastmailConfig
  attr_accessor :name, :redirectTo, :fileIn, :search, :markRead,
    :showNotification, :skipInbox, :discard, :markSpam, :markFlagged,
    :conditions, :snoozeUntil, :previousFileInName, :combinator

  DEFAULT = {
    name: "",
    combinator: "any",
    markRead: false,
    stop: false,
    fileIn: nil,
    redirectTo: nil,
    skipInbox: false,
    showNotification: false,

    # Don't really know anything other than how we're sorting
    discard: false,
    markSpam: false,
    markFlagged: false,

    # Features we're not using
    conditions: nil,
    snoozeUntil: nil,
    previousFileInName: nil,
  }

  def initialize(values)
    values.each do |key, value|
      self.send("#{key}=", value)
    end
  end

  def to_rule
    Rule.new(
      name: self.name,
      redirect: self.redirectTo[0],
      folder: self.fileIn,
      match: parse_search(self.search),
      mark_read: self.markRead,
      notify: self.showNotification,
      archive: self.skipInbox,
    )
  end

  def self.from_rule(rule)
    FastmailConfig.new(
      name: rule.name,
      redirectTo: ([rule.redirect] if rule.redirect),
      fileIn: rule.folder,
      search: generate_search(rule.match),
      markRead: rule.mark_read,
      showNotification: rule.notify,
      skipInbox: rule.archive,
    )
  end

  def to_h
    DEFAULT.dup.merge({
      name: self.name,
      redirectTo: self.redirectTo,
      fileIn: self.fileIn,
      search: self.search,
      markRead: self.markRead,
      showNotification: self.showNotification,
      skipInbox: self.skipInbox,
      discard: self.discard,
      markSpam: self.markSpam,
      markFlagged: self.markFlagged,
      conditions: self.conditions,
      snoozeUntil: self.snoozeUntil,
      previousFileInName: self.previousFileInName,
      combinator: self.combinator,
    })
  end
end

def generate_search(params)
  params.map do |field, values|
    values.map do |value|
      if value.include?(" ")
        value = "(#{value})"
      end
      "#{field}:#{value}"
    end
  end.flatten.join(" OR ")
end

def parse_search(query)
  search = Hash.new([])
  query.split(" OR ").map do |term|
    field, value = term.split(":")
    value = value.sub(/^\(/, "").sub(/\)$/, "")
    search[field] += [value]
    search[field].sort!
  end
  search
end
