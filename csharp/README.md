# Plagiarism Checker Plus for .NET

Official client for the [Plagiarism Checker Plus API](https://plagiarismcheckerplus.com/integrations/api). Targets .NET 8 and .NET Standard 2.0. Uses `HttpClient` and `System.Text.Json`.

The API needs a paid plan. A key on the free plan returns `403 plan_required`.

```sh
dotnet add package PlagiarismCheckerPlus
```

```csharp
using PlagiarismCheckerPlus;

var client = new PlagiarismCheckerPlusClient(Environment.GetEnvironmentVariable("PCP_API_KEY")!);

try
{
    var created = await client.CreateScanAsync(essayText, new[] { "plagiarism", "ai_detect" }, "essay-draft-1");
    var scan = await client.WaitForScanAsync(created["id"]!.GetValue<string>());

    var plagiarism = scan["results"]?["plagiarism"];
    Console.WriteLine($"Matched: {plagiarism?["score"]}%");
    foreach (var source in plagiarism?["sources"]?.AsArray() ?? new System.Text.Json.Nodes.JsonArray())
        Console.WriteLine(source?["url"]);

    // A likelihood, not proof that the text was written by AI.
    Console.WriteLine($"AI likelihood: {scan["results"]?["aiDetection"]?["score"]}%");
}
catch (PlagiarismCheckerPlusException e) when (e.Code == ErrorCodes.TextTooShort)
{
    Console.WriteLine("Send at least 30 words for plagiarism, 50 for AI detection.");
}
```

Responses are `JsonObject` values that mirror the API's JSON.

## Methods

| Method | API call |
|---|---|
| `CreateScanAsync(text, tools, name)` | `POST /scans` |
| `GetScanAsync(id, includeText)` | `GET /scans/{id}` |
| `ListScansAsync(page, limit)` | `GET /scans` |
| `GetAccountAsync()` | `GET /account` |
| `WaitForScanAsync(id, timeout, interval, maxInterval)` | Polls until `completed` or `failed` |

`WaitForScanAsync` starts at 2 seconds, grows by 1.5× up to 10 seconds, waits for `Retry-After` on `429`, and throws `ScanTimeoutException` after 5 minutes by default.

Failed calls throw `PlagiarismCheckerPlusException` with `Status`, `Code` (such as `plan_required`, `text_too_short`, `doc_too_long`, `insufficient_words`) and `RetryAfter`.

Run the tests with `dotnet test tests/PlagiarismCheckerPlus.Tests`.

MIT licensed. Copyright (c) 2026 Plagiarism Checker Plus.
