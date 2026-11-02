# Plagiarism Checker Plus SDKs

Official client libraries for the [Plagiarism Checker Plus API](https://plagiarismcheckerplus.com/integrations/api). Check text for plagiarism, with the matching sources, and for likely AI-generated content, with a likelihood for each sentence.

| Language | Folder | Package |
|---|---|---|
| JavaScript / TypeScript | [`js`](js) | `plagiarism-checker-plus` (npm) |
| Python | [`python`](python) | `plagiarism-checker-plus` (PyPI) |
| PHP | [`php`](php) | `plagiarismcheckerplus/sdk` (Composer) |
| Ruby | [`ruby`](ruby) | `plagiarism_checker_plus` (RubyGems) |
| Go | [`go`](go) | `github.com/pcp-tech/plagiarism-checker-plus-sdk/go` |
| Java | [`java`](java) | `com.plagiarismcheckerplus:sdk` (Maven) |
| C# / .NET | [`csharp`](csharp) | `PlagiarismCheckerPlus` (NuGet) |

Every library offers the same calls:

- `createScan(text, tools, name?)`: submit text. `tools` is any of `plagiarism` and `ai_detect`.
- `getScan(id, includeText?)`: read a scan and its results.
- `listScans(page?, limit?)`: list scans, newest first.
- `getAccount()`: plan and remaining words.
- `waitForScan(id)`: poll until the scan is `completed` or `failed`, backing off and honouring `Retry-After`.

Errors carry the HTTP status and the API's error code, such as `plan_required`, `text_too_short`, `doc_too_long` or `insufficient_words`.

## Before you start

- **A paid plan is required.** A key on the free plan authenticates and then returns `403 plan_required`.
- Create an API key in **Settings → API** in the app. It is shown once.
- The rate limit is 60 requests a minute per key.
- Each tool is billed at the full word count: 800 words checked for both plagiarism and AI uses 1,600 words.
- Minimum length is 30 words for `plagiarism` and 50 for `ai_detect`.
- Scans are asynchronous and usually finish in 30 to 90 seconds.
- An AI score is a likelihood, not proof that text was written by AI. A similarity score shows matching text, not intent.

The API reference is [`openapi.json`](openapi.json), copied from `https://app.plagiarismcheckerplus.com/api/public/v1/openapi.json`.

## License

MIT. Copyright (c) 2026 Plagiarism Checker Plus.
