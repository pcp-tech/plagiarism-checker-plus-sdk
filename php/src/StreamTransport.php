<?php

declare(strict_types=1);

namespace PlagiarismCheckerPlus;

/**
 * Default transport using PHP streams, so no extension or dependency is needed.
 */
final class StreamTransport implements Transport
{
    public function __construct(private float $timeout = 30.0)
    {
    }

    public function send(string $method, string $url, array $headers, ?string $body): Response
    {
        $lines = [];
        foreach ($headers as $name => $value) {
            $lines[] = $name . ': ' . $value;
        }
        $context = stream_context_create(['http' => [
            'method' => $method,
            'header' => implode("\r\n", $lines),
            'content' => $body ?? '',
            'timeout' => $this->timeout,
            'ignore_errors' => true,
        ]]);
        $raw = @file_get_contents($url, false, $context);
        if ($raw === false) {
            throw new ApiException('Request failed: ' . (error_get_last()['message'] ?? 'unknown error'), 0, null, null, null);
        }
        $status = 0;
        $responseHeaders = [];
        foreach ($http_response_header ?? [] as $line) {
            if (preg_match('#^HTTP/\S+\s+(\d{3})#', $line, $m)) {
                $status = (int) $m[1];
                $responseHeaders = [];
            } elseif (str_contains($line, ':')) {
                [$name, $value] = explode(':', $line, 2);
                $responseHeaders[trim($name)] = trim($value);
            }
        }
        return new Response($status, $responseHeaders, $raw);
    }
}
