-- SourceInfo Database Schema
-- Tracks news source credibility and political lean for content rating

CREATE TABLE IF NOT EXISTS sources (
    domain TEXT PRIMARY KEY,
    name TEXT,

    -- NewsGuard data
    newsguard_score INTEGER,  -- 0-100
    newsguard_rating TEXT,    -- "High Credibility", "Generally Credible", "Proceed with Caution", "Low Credibility"

    -- 9 NewsGuard criteria (pass/fail/na + points)
    criteria_false_content TEXT,           -- pass/fail + points (max 22)
    criteria_responsible_gathering TEXT,   -- pass/fail + points (max 18)
    criteria_corrections TEXT,             -- pass/fail + points (max 12.5)
    criteria_news_opinion_separation TEXT, -- pass/fail + points (max 12.5)
    criteria_avoids_deceptive_headlines TEXT, -- pass/fail + points (max 10)
    criteria_ownership_disclosure TEXT,    -- pass/fail + points (max 7.5)
    criteria_labels_advertising TEXT,      -- pass/fail/na + points (max 7.5)
    criteria_reveals_leadership TEXT,      -- pass/fail + points (max 5)
    criteria_content_creator_info TEXT,    -- pass/fail + points (max 5)

    -- AllSides data
    political_lean INTEGER,  -- -2=Left, -1=Lean Left, 0=Center, 1=Lean Right, 2=Right
    political_lean_label TEXT,  -- Human readable: "Left", "Lean Left", "Center", "Lean Right", "Right"

    -- Source classification
    source_type TEXT,  -- news_media, opinion, wire_service, think_tank, fact_check, author, news_aggregator

    -- Descriptive content (for potential future embedding)
    description TEXT,
    ownership_summary TEXT,

    -- Metadata
    newsguard_updated DATE,
    allsides_updated DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_political_lean ON sources(political_lean);
CREATE INDEX IF NOT EXISTS idx_newsguard_score ON sources(newsguard_score);
CREATE INDEX IF NOT EXISTS idx_source_type ON sources(source_type);

-- View for finding counternarrative sources
CREATE VIEW IF NOT EXISTS counternarrative_pairs AS
SELECT
    s1.domain as source_domain,
    s1.name as source_name,
    s1.political_lean as source_lean,
    s1.newsguard_score as source_credibility,
    s2.domain as counter_domain,
    s2.name as counter_name,
    s2.political_lean as counter_lean,
    s2.newsguard_score as counter_credibility
FROM sources s1
CROSS JOIN sources s2
WHERE s1.political_lean != 0
  AND s2.political_lean != 0
  AND s1.political_lean * s2.political_lean < 0  -- opposite sides
  AND s2.newsguard_score >= 60  -- minimum credibility threshold
ORDER BY s1.domain, s2.newsguard_score DESC;
