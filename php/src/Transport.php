<?php

declare(strict_types=1);

namespace PlagiarismCheckerPlus;

/**
 * Sends one HTTP request. Swap in your own for proxies or tests.
 */
interface Transport
{
    /** @param array<string, string> $headers */
    public function send(string $method, string $url, array $headers, ?string $body): Response;
}
