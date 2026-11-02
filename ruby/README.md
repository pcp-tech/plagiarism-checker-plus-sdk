# Plagiarism Checker Plus for Ruby

Official client for the [Plagiarism Checker Plus API](https://plagiarismcheckerplus.com/integrations/api). Ruby 2.7+, standard library only.

The API needs a paid plan. A key on the free plan returns `403 plan_required`.

```sh
gem install plagiarism_checker_plus
```

```ruby
require "plagiarism_checker_plus"

client = PlagiarismCheckerPlus::Client.new(api_key: ENV.fetch("PCP_API_KEY"))

begin
  created = client.create_scan(essay_text, %w[plagiarism ai_detect], name: "essay-draft-1")
  scan = client.wait_for_scan(created["id"])

  plagiarism = scan.dig("results", "plagiarism") || {}
  puts "Matched: #{plagiarism['score']}%"
  (plagiarism["sources"] || []).each { |source| puts source["url"] }

  # A likelihood, not proof that the text was written by AI.
  puts "AI likelihood: #{scan.dig('results', 'aiDetection', 'score')}%"
rescue PlagiarismCheckerPlus::Error => e
  raise unless e.code == PlagiarismCheckerPlus::ErrorCodes::TEXT_TOO_SHORT

  puts "Send at least 30 words for plagiarism, 50 for AI detection."
end
```

## Methods

| Method | API call |
|---|---|
| `create_scan(text, tools, name: nil)` | `POST /scans` |
| `get_scan(id, include_text: false)` | `GET /scans/{id}` |
| `list_scans(page: nil, limit: nil)` | `GET /scans` |
| `get_account` | `GET /account` |
| `wait_for_scan(id, timeout: 300, interval: 2, max_interval: 10)` | Polls until `completed` or `failed` |

`wait_for_scan` grows the delay by 1.5× up to `max_interval`, waits for `Retry-After` on `429`, and raises `ScanTimeoutError` when `timeout` passes.

Failed calls raise `PlagiarismCheckerPlus::Error` with `status`, `code` (such as `plan_required`, `text_too_short`, `doc_too_long`, `insufficient_words`) and `retry_after`.

Run the tests with `ruby -Ilib test/test_client.rb`.

MIT licensed. Copyright (c) 2026 Plagiarism Checker Plus.
