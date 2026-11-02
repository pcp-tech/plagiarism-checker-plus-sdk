# frozen_string_literal: true

require_relative "lib/plagiarism_checker_plus"

Gem::Specification.new do |spec|
  spec.name = "plagiarism_checker_plus"
  spec.version = PlagiarismCheckerPlus::VERSION
  spec.authors = ["Plagiarism Checker Plus"]
  spec.email = ["contact@plagiarismcheckerplus.com"]
  spec.summary = "Official Ruby client for the Plagiarism Checker Plus API."
  spec.description = "Plagiarism checks with sources and AI writing detection through the Plagiarism Checker Plus API."
  spec.homepage = "https://plagiarismcheckerplus.com"
  spec.license = "MIT"
  spec.required_ruby_version = ">= 2.7"
  spec.metadata = {
    "homepage_uri" => "https://plagiarismcheckerplus.com",
    "documentation_uri" => "https://plagiarismcheckerplus.com/integrations/api",
    "source_code_uri" => "https://github.com/pcp-tech/plagiarism-checker-plus-sdk"
  }
  spec.files = Dir["lib/**/*.rb", "README.md", "LICENSE"]
  spec.require_paths = ["lib"]
end
