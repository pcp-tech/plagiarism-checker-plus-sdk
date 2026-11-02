<?php

declare(strict_types=1);

namespace PlagiarismCheckerPlus;

final class Response
{
    /** @param array<string, string> $headers */
    public function __construct(public int $status, public array $headers, public string $body)
    {
    }

    public function header(string $name): ?string
    {
        foreach ($this->headers as $key => $value) {
            if (strcasecmp($key, $name) === 0) {
                return $value;
            }
        }
        return null;
    }
}
