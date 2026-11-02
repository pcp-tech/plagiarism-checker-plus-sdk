# Plagiarism Checker Plus for Java

Official client for the [Plagiarism Checker Plus API](https://plagiarismcheckerplus.com/integrations/api). Java 11+, uses `java.net.http`, no runtime dependencies.

The API needs a paid plan. A key on the free plan returns `403 plan_required`.

```xml
<dependency>
  <groupId>com.plagiarismcheckerplus</groupId>
  <artifactId>sdk</artifactId>
  <version>1.0.0</version>
</dependency>
```

```java
import com.plagiarismcheckerplus.sdk.ApiException;
import com.plagiarismcheckerplus.sdk.PlagiarismCheckerPlus;
import java.util.List;
import java.util.Map;

PlagiarismCheckerPlus client = new PlagiarismCheckerPlus(System.getenv("PCP_API_KEY"));

try {
    Map<String, Object> created = client.createScan(essayText, List.of("plagiarism", "ai_detect"), "essay-draft-1");
    Map<String, Object> scan = client.waitForScan((String) created.get("id"));

    @SuppressWarnings("unchecked")
    Map<String, Object> results = (Map<String, Object>) scan.get("results");
    System.out.println(results);
    // aiDetection.score is a likelihood, not proof that the text was written by AI.
} catch (ApiException e) {
    if (ApiException.TEXT_TOO_SHORT.equals(e.getErrorCode())) {
        System.out.println("Send at least 30 words for plagiarism, 50 for AI detection.");
    } else {
        throw e;
    }
}
```

Responses are `Map<String, Object>` values that mirror the API's JSON, so new fields reach you without an SDK update.

## Methods

| Method | API call |
|---|---|
| `createScan(text, tools, name)` | `POST /scans` |
| `getScan(id, includeText)` | `GET /scans/{id}` |
| `listScans(page, limit)` | `GET /scans` |
| `getAccount()` | `GET /account` |
| `waitForScan(id)` or `waitForScan(id, timeout, interval, maxInterval, includeText)` | Polls until `completed` or `failed` |

`waitForScan` starts at 2 seconds, grows by 1.5× up to 10 seconds, waits for `Retry-After` on `429`, and throws `ScanTimeoutException` after 300 seconds by default.

Failed calls throw `ApiException` with `getStatus()`, `getErrorCode()` (such as `plan_required`, `text_too_short`, `doc_too_long`, `insufficient_words`) and `getRetryAfterSeconds()`.

Run the tests with `mvn test`.

MIT licensed. Copyright (c) 2026 Plagiarism Checker Plus.
