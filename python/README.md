# Plagiarism Checker Plus for Python

Official client for the [Plagiarism Checker Plus API](https://plagiarismcheckerplus.com/integrations/api). Python 3.8+, standard library only, fully typed.

The API needs a paid plan. A key on the free plan returns `403 plan_required`.

```sh
pip install plagiarism-checker-plus
```

```python
import os
from plagiarism_checker_plus import ErrorCodes, PlagiarismCheckerPlus, PlagiarismCheckerPlusError

client = PlagiarismCheckerPlus(os.environ["PCP_API_KEY"])

try:
    scan_id = client.create_scan(essay_text, ["plagiarism", "ai_detect"], name="essay-draft-1")["id"]
    scan = client.wait_for_scan(scan_id)

    plagiarism = scan["results"].get("plagiarism") or {}
    print("Matched:", plagiarism.get("score"), "%")
    for source in plagiarism.get("sources", []):
        print(source["url"])

    # A likelihood, not proof that the text was written by AI.
    print("AI likelihood:", (scan["results"].get("aiDetection") or {}).get("score"), "%")
except PlagiarismCheckerPlusError as error:
    if error.code == ErrorCodes.TEXT_TOO_SHORT:
        print("Send at least 30 words for plagiarism, 50 for AI detection.")
    else:
        raise
```

## Methods

| Method | API call |
|---|---|
| `create_scan(text, tools, name=None)` | `POST /scans` |
| `get_scan(scan_id, include_text=False)` | `GET /scans/{id}` |
| `list_scans(page=None, limit=None)` | `GET /scans` |
| `get_account()` | `GET /account` |
| `wait_for_scan(scan_id, timeout=300, interval=2, max_interval=10)` | Polls until `completed` or `failed` |

`wait_for_scan` grows the delay by 1.5× up to `max_interval`, waits for `Retry-After` on `429`, and raises `ScanTimeoutError` when `timeout` passes.

Failed calls raise `PlagiarismCheckerPlusError` with `status`, `code` (such as `plan_required`, `text_too_short`, `doc_too_long`, `insufficient_words`) and `retry_after`.

Run the tests with `python -m unittest discover -s tests` and `PYTHONPATH=src`.

MIT licensed. Copyright (c) 2026 Plagiarism Checker Plus.
