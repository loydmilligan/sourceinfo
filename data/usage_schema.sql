-- API usage tracking schema

CREATE TABLE IF NOT EXISTS api_usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- API details
    api_name TEXT NOT NULL,  -- 'openrouter', 'jina'
    endpoint TEXT NOT NULL,  -- '/api/content/analyze'
    model_used TEXT,         -- 'anthropic/claude-sonnet-4', null for jina

    -- Token usage
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER GENERATED ALWAYS AS (input_tokens + output_tokens) VIRTUAL,

    -- Cost tracking
    estimated_cost_usd REAL DEFAULT 0.0,

    -- Request details
    url TEXT,                -- Article URL being analyzed
    success BOOLEAN NOT NULL DEFAULT 1,
    error_message TEXT,

    -- Metadata
    user_agent TEXT,
    ip_address TEXT
);

CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_usage_api_name ON api_usage_log(api_name);
CREATE INDEX IF NOT EXISTS idx_api_usage_model ON api_usage_log(model_used);
CREATE INDEX IF NOT EXISTS idx_api_usage_success ON api_usage_log(success);
