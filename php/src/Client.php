<?php

declare(strict_types=1);

namespace PlagiarismCheckerPlus;

/**
 * Client for the Plagiarism Checker Plus public API.
 */
final class Client
{
    public const DEFAULT_BASE_URL = 'https://app.plagiarismcheckerplus.com/api/public/v1';
    public const VERSION = '1.0.0';

    private string $apiKey;
    private string $baseUrl;
    private Transport $transport;

    public function __construct(string $apiKey, string $baseUrl = self::DEFAULT_BASE_URL, ?Transport $transport = null)
    {
        if ($apiKey === '') {
            throw new \InvalidArgumentException('apiKey is required');
        }
        $this->apiKey = $apiKey;
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->transport = $transport ?? new StreamTransport();
    }

    /**
     * Submit text. $tools: any of "plagiarism" and "ai_detect".
     *
     * @param list<string> $tools
     * @return array<string, mixed>
     */
    public function createScan(string $text, array $tools, ?string $name = null): array
    {
        $body = ['text' => $text, 'tools' => array_values($tools)];
        if ($name !== null) {
            $body['name'] = $name;
        }
        return $this->request('POST', '/scans', [], $body);
    }

    /** @return array<string, mixed> */
    public function getScan(string $id, bool $includeText = false): array
    {
        return $this->request('GET', '/scans/' . rawurlencode($id), $includeText ? ['include_text' => 'true'] : []);
    }

    /** @return array<string, mixed> */
    public function listScans(?int $page = null, ?int $limit = null): array
    {
        return $this->request('GET', '/scans', array_filter(['page' => $page, 'limit' => $limit], static fn ($v) => $v !== null));
    }

    /** @return array<string, mixed> */
    public function getAccount(): array
    {
        return $this->request('GET', '/account');
    }

    /**
     * Poll until the scan is completed or failed, honouring Retry-After on 429.
     *
     * @param callable(float): void|null $sleep Seconds to sleep; defaults to usleep.
     * @return array<string, mixed>
     */
    public function waitForScan(
        string $id,
        float $timeout = 300.0,
        float $interval = 2.0,
        float $maxInterval = 10.0,
        bool $includeText = false,
        ?callable $sleep = null
    ): array {
        $sleep = $sleep ?? static function (float $seconds): void {
            usleep((int) round($seconds * 1_000_000));
        };
        $deadline = microtime(true) + $timeout;
        $delay = $interval;
        while (true) {
            $wait = $delay;
            try {
                $scan = $this->getScan($id, $includeText);
                if (in_array($scan['status'] ?? null, ['completed', 'failed'], true)) {
                    return $scan;
                }
                $delay = min($delay * 1.5, $maxInterval);
            } catch (ApiException $e) {
                if ($e->getStatus() !== 429) {
                    throw $e;
                }
                $wait = $e->getRetryAfter() ?? $delay;
            }
            if (microtime(true) + $wait > $deadline) {
                throw new ScanTimeoutException(sprintf('Scan %s did not finish within %s seconds', $id, $timeout));
            }
            $sleep($wait);
        }
    }

    /**
     * @param array<string, scalar> $query
     * @param array<string, mixed>|null $body
     * @return array<string, mixed>
     */
    private function request(string $method, string $path, array $query = [], ?array $body = null): array
    {
        $url = $this->baseUrl . $path . ($query ? '?' . http_build_query($query) : '');
        $headers = [
            'Authorization' => 'Bearer ' . $this->apiKey,
            'Accept' => 'application/json',
            'User-Agent' => 'plagiarism-checker-plus-php/' . self::VERSION,
        ];
        $payload = null;
        if ($body !== null) {
            $headers['Content-Type'] = 'application/json';
            $payload = json_encode($body, JSON_THROW_ON_ERROR | JSON_UNESCAPED_UNICODE);
        }
        $response = $this->transport->send($method, $url, $headers, $payload);
        $data = $response->body === '' ? null : json_decode($response->body, true);
        if ($response->status < 200 || $response->status >= 300) {
            $error = is_array($data) && is_array($data['error'] ?? null) ? $data['error'] : [];
            throw new ApiException(
                (string) ($error['message'] ?? 'HTTP ' . $response->status),
                $response->status,
                isset($error['code']) ? (string) $error['code'] : null,
                ApiException::parseRetryAfter($response->header('Retry-After')),
                $data
            );
        }
        return is_array($data) ? $data : [];
    }
}
