import json
import unittest

from plagiarism_checker_plus import (
    ErrorCodes,
    PlagiarismCheckerPlus,
    PlagiarismCheckerPlusError,
    ScanTimeoutError,
)


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, method, url, headers, body):
        self.calls.append((method, url, dict(headers), body))
        status, headers_out, payload = self.responses.pop(0)
        return status, headers_out, json.dumps(payload).encode() if payload is not None else b""


class ClientTest(unittest.TestCase):
    def test_create_scan(self):
        t = FakeTransport([(202, {}, {"id": "s1", "status": "processing"})])
        client = PlagiarismCheckerPlus("pcp_test", transport=t)
        self.assertEqual(client.create_scan("text", ["plagiarism"], "draft")["id"], "s1")
        method, url, headers, body = t.calls[0]
        self.assertEqual(method, "POST")
        self.assertEqual(url, "https://app.plagiarismcheckerplus.com/api/public/v1/scans")
        self.assertEqual(headers["Authorization"], "Bearer pcp_test")
        self.assertEqual(json.loads(body), {"text": "text", "tools": ["plagiarism"], "name": "draft"})

    def test_query_parameters(self):
        t = FakeTransport([(200, {}, {"id": "s1"}), (200, {}, {"data": []})])
        client = PlagiarismCheckerPlus("k", transport=t)
        client.get_scan("s1", include_text=True)
        client.list_scans(page=2, limit=5)
        self.assertTrue(t.calls[0][1].endswith("/scans/s1?include_text=true"))
        self.assertTrue(t.calls[1][1].endswith("/scans?page=2&limit=5"))

    def test_error_code(self):
        t = FakeTransport([(403, {}, {"error": {"code": "plan_required", "message": "Paid plan needed"}})])
        client = PlagiarismCheckerPlus("k", transport=t)
        with self.assertRaises(PlagiarismCheckerPlusError) as ctx:
            client.get_account()
        self.assertEqual(ctx.exception.status, 403)
        self.assertEqual(ctx.exception.code, ErrorCodes.PLAN_REQUIRED)

    def test_wait_honours_retry_after(self):
        t = FakeTransport([
            (200, {}, {"id": "s1", "status": "processing"}),
            (429, {"Retry-After": "3"}, {"error": {"code": "rate_limited", "message": "Slow down"}}),
            (200, {}, {"id": "s1", "status": "completed"}),
        ])
        waits = []
        client = PlagiarismCheckerPlus("k", transport=t)
        scan = client.wait_for_scan("s1", interval=1.0, sleep=waits.append)
        self.assertEqual(scan["status"], "completed")
        self.assertEqual(waits, [1.0, 3.0])

    def test_wait_times_out(self):
        t = FakeTransport([(200, {}, {"id": "s1", "status": "processing"})])
        client = PlagiarismCheckerPlus("k", transport=t)
        with self.assertRaises(ScanTimeoutError):
            client.wait_for_scan("s1", timeout=0.01, interval=1.0, sleep=lambda s: None)


if __name__ == "__main__":
    unittest.main()
