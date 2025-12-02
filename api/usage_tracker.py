"""API usage tracking and cost calculation."""

import sqlite3
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from .config import settings


# Model pricing per million tokens (as of Dec 2024)
# Source: https://openrouter.ai/models
MODEL_PRICING = {
    "anthropic/claude-sonnet-4": {
        "input": 3.0,    # $3 per 1M input tokens
        "output": 15.0   # $15 per 1M output tokens
    },
    "anthropic/claude-3-5-sonnet": {
        "input": 3.0,
        "output": 15.0
    },
    "anthropic/claude-3-5-haiku": {
        "input": 1.0,
        "output": 5.0
    },
    "anthropic/claude-3-haiku": {
        "input": 0.25,
        "output": 1.25
    },
    "google/gemini-flash-1.5": {
        "input": 0.075,
        "output": 0.30
    },
    "google/gemini-pro-1.5": {
        "input": 1.25,
        "output": 5.0
    },
    "meta-llama/llama-3.1-70b-instruct": {
        "input": 0.35,
        "output": 0.40
    },
    "meta-llama/llama-3.1-405b-instruct": {
        "input": 2.0,
        "output": 2.0
    },
    "openai/gpt-4o": {
        "input": 2.5,
        "output": 10.0
    },
    "openai/gpt-4o-mini": {
        "input": 0.15,
        "output": 0.60
    },
}


@dataclass
class UsageLog:
    """API usage log entry."""
    api_name: str
    endpoint: str
    model_used: Optional[str]
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    url: Optional[str]
    success: bool
    error_message: Optional[str] = None


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate estimated cost for an API call.

    Args:
        model: Model identifier (e.g., 'anthropic/claude-sonnet-4')
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Estimated cost in USD
    """
    if model not in MODEL_PRICING:
        # Unknown model, use conservative estimate
        return 0.0

    pricing = MODEL_PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]

    return round(input_cost + output_cost, 6)


def log_api_usage(log: UsageLog) -> None:
    """
    Log an API usage entry to the database.

    Args:
        log: UsageLog entry to store
    """
    try:
        conn = sqlite3.connect(settings.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO api_usage_log (
                api_name,
                endpoint,
                model_used,
                input_tokens,
                output_tokens,
                estimated_cost_usd,
                url,
                success,
                error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            log.api_name,
            log.endpoint,
            log.model_used,
            log.input_tokens,
            log.output_tokens,
            log.estimated_cost_usd,
            log.url,
            log.success,
            log.error_message
        ))

        conn.commit()
        conn.close()
    except Exception as e:
        # Don't let logging failures break the API
        print(f"Failed to log API usage: {e}")


def get_usage_stats(days: int = 30) -> dict:
    """
    Get API usage statistics for the last N days.

    Args:
        days: Number of days to include (default 30)

    Returns:
        Dictionary with usage statistics
    """
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Total stats
    cursor.execute("""
        SELECT
            COUNT(*) as total_calls,
            SUM(input_tokens) as total_input_tokens,
            SUM(output_tokens) as total_output_tokens,
            SUM(estimated_cost_usd) as total_cost,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_calls,
            SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_calls
        FROM api_usage_log
        WHERE timestamp >= datetime('now', ? || ' days')
    """, (f"-{days}",))

    totals = dict(cursor.fetchone())

    # By API
    cursor.execute("""
        SELECT
            api_name,
            COUNT(*) as calls,
            SUM(estimated_cost_usd) as cost
        FROM api_usage_log
        WHERE timestamp >= datetime('now', ? || ' days')
        GROUP BY api_name
        ORDER BY cost DESC
    """, (f"-{days}",))

    by_api = [dict(row) for row in cursor.fetchall()]

    # By model
    cursor.execute("""
        SELECT
            model_used,
            COUNT(*) as calls,
            SUM(input_tokens) as input_tokens,
            SUM(output_tokens) as output_tokens,
            SUM(estimated_cost_usd) as cost,
            AVG(estimated_cost_usd) as avg_cost_per_call
        FROM api_usage_log
        WHERE timestamp >= datetime('now', ? || ' days')
            AND model_used IS NOT NULL
        GROUP BY model_used
        ORDER BY cost DESC
    """, (f"-{days}",))

    by_model = [dict(row) for row in cursor.fetchall()]

    # Daily breakdown
    cursor.execute("""
        SELECT
            DATE(timestamp) as date,
            COUNT(*) as calls,
            SUM(input_tokens) as input_tokens,
            SUM(output_tokens) as output_tokens,
            SUM(estimated_cost_usd) as cost
        FROM api_usage_log
        WHERE timestamp >= datetime('now', ? || ' days')
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    """, (f"-{days}",))

    daily = [dict(row) for row in cursor.fetchall()]

    # Most expensive analyses
    cursor.execute("""
        SELECT
            url,
            model_used,
            input_tokens,
            output_tokens,
            estimated_cost_usd as cost,
            timestamp
        FROM api_usage_log
        WHERE timestamp >= datetime('now', ? || ' days')
            AND estimated_cost_usd > 0
        ORDER BY estimated_cost_usd DESC
        LIMIT 10
    """, (f"-{days}",))

    top_expensive = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "period_days": days,
        "totals": totals,
        "by_api": by_api,
        "by_model": by_model,
        "daily": daily,
        "top_expensive": top_expensive
    }
