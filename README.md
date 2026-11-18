# Plagiarism Checker Plus SDKs

Official client libraries for the [Plagiarism Checker Plus API](https://plagiarismcheckerplus.com/integrations/api): plagiarism checks with linked sources, and AI writing detection with a likelihood for each sentence.

Each language now lives in its own repository:

| Language | Repository | Install |
|---|---|---|
| JavaScript / TypeScript | [plagiarism-checker-plus-js](https://github.com/pcp-tech/plagiarism-checker-plus-js) | `npm install plagiarism-checker-plus` |
| Python | [plagiarism-checker-plus-python](https://github.com/pcp-tech/plagiarism-checker-plus-python) | `pip install plagiarism-checker-plus` |
| PHP | [plagiarism-checker-plus-php](https://github.com/pcp-tech/plagiarism-checker-plus-php) | `composer require plagiarismcheckerplus/sdk` |
| Ruby | [plagiarism-checker-plus-ruby](https://github.com/pcp-tech/plagiarism-checker-plus-ruby) | `gem install plagiarism_checker_plus` |
| Go | [plagiarism-checker-plus-go](https://github.com/pcp-tech/plagiarism-checker-plus-go) | `go get github.com/pcp-tech/plagiarism-checker-plus-go` |
| Java | [plagiarism-checker-plus-java](https://github.com/pcp-tech/plagiarism-checker-plus-java) | Maven `com.plagiarismcheckerplus:sdk` |
| C# / .NET | [plagiarism-checker-plus-dotnet](https://github.com/pcp-tech/plagiarism-checker-plus-dotnet) | `dotnet add package PlagiarismCheckerPlus` |

Get a free API key at https://app.plagiarismcheckerplus.com/developers (test keys are free and unlimited).

- **Test keys** (`pcp_test_...`) are free and unlimited on every plan. They never run a check and return fixed sample results in the same shape as a real scan, marked `"sandbox": true`.
- **Free API trial**: each free account gets 2,000 live API words once, with no card. When it cannot cover a request, the API returns `402 trial_exhausted`.
- **Paid app plans** (Student, Personal, Team) use their plan words for API calls.
- **API plans**: Starter $29/month (300,000 words), Growth $99/month (1,500,000 words), Scale $399/month (7,500,000 words). **Pay as you go**: words from $6 (50,000 words, $0.12 per 1,000 words).
- See [API pricing](https://plagiarismcheckerplus.com/api-pricing). Keys, usage, billing and webhooks are in the [developer portal](https://app.plagiarismcheckerplus.com/developers).

Since version 1.1.0 every SDK has constants for the billing errors (`trial_exhausted`, `insufficient_words`, `key_cap_reached`, all `402`) and a helper that verifies webhook signatures (`PCP-Signature: t=<unix>,v1=<hex HMAC-SHA256(secret, "<t>.<raw body>")>`, events `scan.completed` and `scan.failed`). `plan_required` is no longer returned; its constant is kept, marked deprecated, so existing code still compiles.

An AI score is a likelihood, not proof that someone used AI.

The API reference is [`spec/openapi.json`](spec/openapi.json), copied from `https://app.plagiarismcheckerplus.com/api/public/v1/openapi.json`.

- Plagiarism Checker API overview: https://plagiarismcheckerplus.com/integrations/api
- AI Detector API overview: https://plagiarismcheckerplus.com/ai-detector-api
- API pricing: https://plagiarismcheckerplus.com/api-pricing
- API reference (try requests in the browser): https://app.plagiarismcheckerplus.com/api-docs
- Developer portal (keys, usage, billing, webhooks): https://app.plagiarismcheckerplus.com/developers

For AI assistants, see the hosted MCP server: https://github.com/pcp-tech/plagiarism-checker-plus-mcp

## License

MIT. Copyright (c) 2026 Plagiarism Checker Plus.
