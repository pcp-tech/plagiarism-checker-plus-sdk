<?php

declare(strict_types=1);

namespace PlagiarismCheckerPlus;

/**
 * A non-2xx response. getErrorCode() is the API's code, such as plan_required.
 */
class ApiException extends \RuntimeException
{
    public const PLAN_REQUIRED = 'plan_required';
    public const TEXT_TOO_SHORT = 'text_too_short';
    public const DOC_TOO_LONG = 'doc_too_long';
    public const INSUFFICIENT_WORDS = 'insufficient_words';

    public function __construct(
        string $message,
        private int $status,
        private ?string $errorCode,
        private ?float $retryAfter,
        private mixed $body
    ) {
        parent::__construct($message, $status);
    }

    public function getStatus(): int
    {
        return $this->status;
    }

    public function getErrorCode(): ?string
    {
        return $this->errorCode;
    }

    /** Seconds from Retry-After, if sent. */
    public function getRetryAfter(): ?float
    {
        return $this->retryAfter;
    }

    public function getBody(): mixed
    {
        return $this->body;
    }

    public static function parseRetryAfter(?string $value): ?float
    {
        if ($value === null || $value === '') {
            return null;
        }
        if (is_numeric($value)) {
            return max(0.0, (float) $value);
        }
        $time = strtotime($value);
        return $time === false ? null : max(0.0, (float) ($time - time()));
    }
}
