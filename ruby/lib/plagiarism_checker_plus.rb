# frozen_string_literal: true

require "json"
require "net/http"
require "time"
require "uri"

# Client for the Plagiarism Checker Plus public API. Standard library only.
module PlagiarismCheckerPlus
  VERSION = "1.0.0"
  DEFAULT_BASE_URL = "https://app.plagiarismcheckerplus.com/api/public/v1"

  module ErrorCodes
    PLAN_REQUIRED = "plan_required"
    TEXT_TOO_SHORT = "text_too_short"
    DOC_TOO_LONG = "doc_too_long"
    INSUFFICIENT_WORDS = "insufficient_words"
  end

  # A non-2xx response. +code+ is the API's error code, such as plan_required.
  class Error < StandardError
    attr_reader :status, :code, :retry_after, :body

    def initialize(message, status: 0, code: nil, retry_after: nil, body: nil)
      super(message)
      @status = status
      @code = code
      @retry_after = retry_after
      @body = body
    end
  end

  class ScanTimeoutError < StandardError; end

  # Response passed back by a transport.
  Response = Struct.new(:status, :headers, :body)

  # Default transport using Net::HTTP.
  class NetHttpTransport
    def initialize(timeout: 30)
      @timeout = timeout
    end

    def call(method, url, headers, body)
      uri = URI(url)
      request = Net::HTTPGenericRequest.new(method, !body.nil?, true, uri.request_uri, headers)
      request.body = body if body
      http = Net::HTTP.new(uri.host, uri.port)
      http.use_ssl = uri.scheme == "https"
      http.open_timeout = @timeout
      http.read_timeout = @timeout
      response = http.request(request)
      Response.new(response.code.to_i, response.each_header.to_h, response.body.to_s)
    end
  end

  def self.parse_retry_after(value)
    return nil if value.nil? || value.to_s.empty?
    return [Float(value), 0.0].max if value.to_s.match?(/\A\d+(\.\d+)?\z/)

    [Time.httpdate(value.to_s) - Time.now, 0.0].max
  rescue ArgumentError
    nil
  end

  class Client
    # transport: anything responding to call(method, url, headers, body) -> Response.
    def initialize(api_key:, base_url: DEFAULT_BASE_URL, transport: NetHttpTransport.new)
      raise ArgumentError, "api_key is required" if api_key.nil? || api_key.empty?

      @api_key = api_key
      @base_url = base_url.chomp("/")
      @transport = transport
    end

    # Submit text. tools: any of "plagiarism" and "ai_detect".
    def create_scan(text, tools, name: nil)
      body = { text: text, tools: tools }
      body[:name] = name unless name.nil?
      request("POST", "/scans", body: body)
    end

    def get_scan(id, include_text: false)
      request("GET", "/scans/#{URI.encode_www_form_component(id)}", query: include_text ? { include_text: "true" } : nil)
    end

    def list_scans(page: nil, limit: nil)
      request("GET", "/scans", query: { page: page, limit: limit })
    end

    def get_account
      request("GET", "/account")
    end

    # Poll until the scan is completed or failed, honouring Retry-After on 429.
    def wait_for_scan(id, timeout: 300, interval: 2.0, max_interval: 10.0, include_text: false, sleeper: method(:sleep))
      deadline = Process.clock_gettime(Process::CLOCK_MONOTONIC) + timeout
      delay = interval
      loop do
        wait = delay
        begin
          scan = get_scan(id, include_text: include_text)
          return scan if %w[completed failed].include?(scan["status"])

          delay = [delay * 1.5, max_interval].min
        rescue Error => e
          raise unless e.status == 429

          wait = e.retry_after || delay
        end
        if Process.clock_gettime(Process::CLOCK_MONOTONIC) + wait > deadline
          raise ScanTimeoutError, "Scan #{id} did not finish within #{timeout} seconds"
        end

        sleeper.call(wait)
      end
    end

    private

    def request(method, path, query: nil, body: nil)
      url = @base_url + path
      params = (query || {}).reject { |_, v| v.nil? }
      url += "?#{URI.encode_www_form(params)}" unless params.empty?
      headers = {
        "Authorization" => "Bearer #{@api_key}",
        "Accept" => "application/json",
        "User-Agent" => "plagiarism-checker-plus-ruby/#{VERSION}"
      }
      payload = nil
      unless body.nil?
        headers["Content-Type"] = "application/json"
        payload = JSON.generate(body)
      end
      response = @transport.call(method, url, headers, payload)
      data = response.body.to_s.empty? ? nil : (JSON.parse(response.body) rescue nil)
      return data || {} if response.status.between?(200, 299)

      error = data.is_a?(Hash) && data["error"].is_a?(Hash) ? data["error"] : {}
      retry_header = response.headers.find { |k, _| k.to_s.casecmp?("retry-after") }&.last
      raise Error.new(error["message"] || "HTTP #{response.status}",
                      status: response.status,
                      code: error["code"],
                      retry_after: PlagiarismCheckerPlus.parse_retry_after(retry_header),
                      body: data)
    end
  end
end
