require "json"
require "yaml"

if not File.exists?("rules.yaml")
  FileUtils.cp("rules.example.yaml", "rules.yaml")
end

input = YAML.load(File.read("rules.yaml"))
output = []

DEFAULT = {
  name: "",
  combinator: "any",
  markRead: false,
  stop: false,
  fileIn: nil,
  redirectTo: nil,
  skipInbox: false,

  # Don't really know anything other than how we're sorting
  discard: false,
  markSpam: false,
  markFlagged: false,

  # Features we're not using
  conditions: nil,
  snoozeUntil: nil,
  previousFileInName: nil,
  showNotification: false,
}

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

def generate_config(rule)
  if rule.key?("mailbox")
    DEFAULT.dup.merge(
      fileIn: rule["mailbox"],
      name: "File into #{rule["mailbox"]}",
      markRead: rule["mark_read"],
      showNotification: rule["notify"],
      skipInbox: true,
      stop: true,
      search: generate_search(rule["match"])
    )
  else
    DEFAULT.dup.merge(
      redirectTo: [ rule["redirect"] ],
      name: "Redirect to #{rule["name"]}",
      search: generate_search(rule["match"])
    )
  end
end

input.each do |rule|
  output.push(generate_config(rule))
end

File.write("mailrules.json", JSON.pretty_generate(output))
