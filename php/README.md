# Plagiarism Checker Plus for PHP

Official client for the [Plagiarism Checker Plus API](https://plagiarismcheckerplus.com/integrations/api). PHP 8.1+, no dependencies.

The API needs a paid plan. A key on the free plan returns `403 plan_required`.

```sh
composer require plagiarismcheckerplus/sdk
```

```php
use PlagiarismCheckerPlus\ApiException;
use PlagiarismCheckerPlus\Client;

$client = new Client(getenv('PCP_API_KEY'));

try {
    $created = $client->createScan($essayText, ['plagiarism', 'ai_detect'], 'essay-draft-1');
    $scan = $client->waitForScan($created['id']);

    echo 'Matched: ', $scan['results']['plagiarism']['score'] ?? '-', "%\n";
    foreach ($scan['results']['plagiarism']['sources'] ?? [] as $source) {
        echo $source['url'], "\n";
    }

    // A likelihood, not proof that the text was written by AI.
    echo 'AI likelihood: ', $scan['results']['aiDetection']['score'] ?? '-', "%\n";
} catch (ApiException $e) {
    if ($e->getErrorCode() === ApiException::TEXT_TOO_SHORT) {
        echo "Send at least 30 words for plagiarism, 50 for AI detection.\n";
    } else {
        throw $e;
    }
}
```

## Methods

| Method | API call |
|---|---|
| `createScan($text, $tools, $name = null)` | `POST /scans` |
| `getScan($id, $includeText = false)` | `GET /scans/{id}` |
| `listScans($page = null, $limit = null)` | `GET /scans` |
| `getAccount()` | `GET /account` |
| `waitForScan($id, $timeout = 300, $interval = 2, $maxInterval = 10)` | Polls until `completed` or `failed` |

`waitForScan` grows the delay by 1.5× up to `$maxInterval`, waits for `Retry-After` on `429`, and throws `ScanTimeoutException` when `$timeout` passes.

Failed calls throw `ApiException` with `getStatus()`, `getErrorCode()` (such as `plan_required`, `text_too_short`, `doc_too_long`, `insufficient_words`) and `getRetryAfter()`. Pass your own `Transport` to the constructor for proxies or tests.

Run the tests with `composer test`.

MIT licensed. Copyright (c) 2026 Plagiarism Checker Plus.
