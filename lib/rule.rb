class Rule
  attr_accessor :name, :redirect, :folder, :label, :match

  # Booleans
  attr_accessor :mark_read, :notify, :archive

  def initialize(args)
    args.each do |k, v|
      self.send("#{k}=", v)
    end
  end

  def self.from_rule(rule)
    Rule.new(rule)
  end
end
