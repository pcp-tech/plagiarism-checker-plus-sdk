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

The API needs a paid plan. A key on the free plan returns `403 plan_required`.

An AI score is a likelihood, not proof that someone used AI.

The API reference is [`spec/openapi.json`](spec/openapi.json), copied from `https://app.plagiarismcheckerplus.com/api/public/v1/openapi.json`.

For AI assistants, see the hosted MCP server: https://github.com/pcp-tech/plagiarism-checker-plus-mcp

## License

MIT. Copyright (c) 2026 Plagiarism Checker Plus.
