"""Content analysis using OpenRouter LLM API."""

import httpx
import json
from typing import Optional
from dataclasses import dataclass, field
from .config import settings
from .usage_tracker import log_api_usage, calculate_cost, UsageLog

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Analysis prompt template
ANALYSIS_PROMPT = """You are an expert media analyst. Analyze the following news article for quality, bias, and reliability.

ARTICLE CONTENT:
{content}

Provide a structured analysis in the following JSON format:

{{
  "summary": "2-3 sentence summary of what the article is about",

  "inflammatory_language": {{
    "score": <1-10, where 1=neutral/factual, 10=highly inflammatory>,
    "examples": ["list of specific inflammatory phrases found"],
    "explanation": "brief explanation of the inflammatory language used"
  }},

  "unsupported_claims": {{
    "score": <1-10, where 1=well-sourced, 10=many unsupported claims>,
    "claims": [
      {{
        "claim": "the specific claim made",
        "issue": "why it's unsupported (no source, vague attribution, etc.)"
      }}
    ],
    "explanation": "overall assessment of sourcing quality"
  }},

  "emotional_manipulation": {{
    "score": <1-10, where 1=objective, 10=highly manipulative>,
    "techniques": ["list of manipulation techniques detected"],
    "explanation": "how the article attempts to influence reader emotions"
  }},

  "factual_reporting": {{
    "score": <1-10, where 1=opinion/speculation, 10=factual reporting>,
    "strengths": ["what the article does well factually"],
    "weaknesses": ["factual issues or gaps"]
  }},

  "bias_indicators": {{
    "detected_lean": "<Left|Lean Left|Center|Lean Right|Right|Unknown>",
    "indicators": ["specific phrases or framing that indicate bias"],
    "explanation": "assessment of political or ideological bias"
  }},

  "overall_quality": {{
    "score": <1-100, overall quality/reliability score>,
    "grade": "<A|B|C|D|F>",
    "recommendation": "brief recommendation for readers"
  }}
}}

Return ONLY valid JSON, no additional text or markdown formatting."""


@dataclass
class AnalysisScores:
    """Individual analysis scores."""
    inflammatory_language: int
    unsupported_claims: int
    emotional_manipulation: int
    factual_reporting: int
    overall_quality: int
    overall_grade: str


@dataclass
class ContentAnalysis:
    """Full content analysis result."""
    url: str
    success: bool

    # Summary
    summary: Optional[str] = None

    # Scores
    scores: Optional[AnalysisScores] = None

    # Detailed findings
    inflammatory_examples: list[str] = field(default_factory=list)
    inflammatory_explanation: Optional[str] = None

    unsupported_claims: list[dict] = field(default_factory=list)
    claims_explanation: Optional[str] = None

    manipulation_techniques: list[str] = field(default_factory=list)
    manipulation_explanation: Optional[str] = None

    factual_strengths: list[str] = field(default_factory=list)
    factual_weaknesses: list[str] = field(default_factory=list)

    detected_bias: Optional[str] = None
    bias_indicators: list[str] = field(default_factory=list)
    bias_explanation: Optional[str] = None

    recommendation: Optional[str] = None

    # Metadata
    model_used: Optional[str] = None
    error: Optional[str] = None


async def analyze_content(
    url: str,
    content: str,
    model: str = "anthropic/claude-sonnet-4",
    timeout: float = 120.0
) -> ContentAnalysis:
    """
    Analyze article content using OpenRouter LLM.

    Args:
        url: The article URL (for reference)
        content: The article text to analyze
        model: OpenRouter model ID
        timeout: Request timeout in seconds

    Returns:
        ContentAnalysis with detailed findings
    """
    if not settings.openrouter_api_key:
        return ContentAnalysis(
            url=url,
            success=False,
            error="OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable."
        )

    # Truncate very long articles to avoid token limits
    max_chars = 15000  # ~4k tokens
    truncated_content = content[:max_chars]
    if len(content) > max_chars:
        truncated_content += "\n\n[Article truncated for analysis...]"

    prompt = ANALYSIS_PROMPT.format(content=truncated_content)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://sourceinfo.app",
                    "X-Title": "SourceInfo Content Analyzer"
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,  # Lower for more consistent analysis
                    "max_tokens": 2000
                },
                timeout=timeout
            )

            if response.status_code != 200:
                return ContentAnalysis(
                    url=url,
                    success=False,
                    error=f"OpenRouter API error: {response.status_code} - {response.text}"
                )

            result = response.json()

            # Extract the response content
            response_text = result["choices"][0]["message"]["content"]

            # Extract token usage for cost tracking
            usage_data = result.get("usage", {})
            input_tokens = usage_data.get("prompt_tokens", 0)
            output_tokens = usage_data.get("completion_tokens", 0)
            cost = calculate_cost(model, input_tokens, output_tokens)

            # Parse JSON response
            try:
                # Handle potential markdown code blocks
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]

                analysis_data = json.loads(response_text.strip())
            except json.JSONDecodeError as e:
                return ContentAnalysis(
                    url=url,
                    success=False,
                    error=f"Failed to parse LLM response as JSON: {str(e)}",
                    model_used=model
                )

            # Build the ContentAnalysis object
            analysis_result = ContentAnalysis(
                url=url,
                success=True,
                summary=analysis_data.get("summary"),
                scores=AnalysisScores(
                    inflammatory_language=analysis_data.get("inflammatory_language", {}).get("score", 0),
                    unsupported_claims=analysis_data.get("unsupported_claims", {}).get("score", 0),
                    emotional_manipulation=analysis_data.get("emotional_manipulation", {}).get("score", 0),
                    factual_reporting=analysis_data.get("factual_reporting", {}).get("score", 0),
                    overall_quality=analysis_data.get("overall_quality", {}).get("score", 0),
                    overall_grade=analysis_data.get("overall_quality", {}).get("grade", "?")
                ),
                inflammatory_examples=analysis_data.get("inflammatory_language", {}).get("examples", []),
                inflammatory_explanation=analysis_data.get("inflammatory_language", {}).get("explanation"),
                unsupported_claims=analysis_data.get("unsupported_claims", {}).get("claims", []),
                claims_explanation=analysis_data.get("unsupported_claims", {}).get("explanation"),
                manipulation_techniques=analysis_data.get("emotional_manipulation", {}).get("techniques", []),
                manipulation_explanation=analysis_data.get("emotional_manipulation", {}).get("explanation"),
                factual_strengths=analysis_data.get("factual_reporting", {}).get("strengths", []),
                factual_weaknesses=analysis_data.get("factual_reporting", {}).get("weaknesses", []),
                detected_bias=analysis_data.get("bias_indicators", {}).get("detected_lean"),
                bias_indicators=analysis_data.get("bias_indicators", {}).get("indicators", []),
                bias_explanation=analysis_data.get("bias_indicators", {}).get("explanation"),
                recommendation=analysis_data.get("overall_quality", {}).get("recommendation"),
                model_used=model,
                error=None
            )

            # Log successful API usage
            log_api_usage(UsageLog(
                api_name="openrouter",
                endpoint="/chat/completions",
                model_used=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost_usd=cost,
                url=url,
                success=True
            ))

            return analysis_result

    except httpx.TimeoutException:
        # Log failed API call
        log_api_usage(UsageLog(
            api_name="openrouter",
            endpoint="/chat/completions",
            model_used=model,
            input_tokens=0,
            output_tokens=0,
            estimated_cost_usd=0.0,
            url=url,
            success=False,
            error_message="Request timed out"
        ))
        return ContentAnalysis(
            url=url,
            success=False,
            error="Analysis request timed out",
            model_used=model
        )
    except Exception as e:
        # Log failed API call
        log_api_usage(UsageLog(
            api_name="openrouter",
            endpoint="/chat/completions",
            model_used=model,
            input_tokens=0,
            output_tokens=0,
            estimated_cost_usd=0.0,
            url=url,
            success=False,
            error_message=str(e)
        ))
        return ContentAnalysis(
            url=url,
            success=False,
            error=f"Analysis failed: {str(e)}",
            model_used=model
        )
