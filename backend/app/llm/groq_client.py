"""
Groq LLM client for generating explanations.
Uses FREE Groq models only. LLM is used ONLY for explanation, never decision-making.
"""
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
import httpx

from app.core.config import settings
from app.llm.prompt_builder import (
    build_analysis_prompt,
    build_security_explanation_prompt,
    build_refactor_recommendation_prompt,
    truncate_for_token_limit,
)


@dataclass
class LLMResponse:
    """Response from LLM API."""
    content: str
    tokens_used: int
    model: str
    success: bool
    error: Optional[str] = None


class GroqClient:
    """
    Client for Groq API.
    Uses free models only (llama3-8b-8192, etc.)
    """

    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.max_tokens = settings.GROQ_MAX_TOKENS
        self.temperature = settings.GROQ_TEMPERATURE

    def is_configured(self) -> bool:
        """Check if Groq API is configured."""
        return bool(self.api_key)

    def _make_request(self, prompt: str) -> LLMResponse:
        """
        Make a request to Groq API.

        Args:
            prompt: The prompt to send

        Returns:
            LLMResponse with result or error
        """
        if not self.is_configured():
            return LLMResponse(
                content="",
                tokens_used=0,
                model=self.model,
                success=False,
                error="Groq API key not configured"
            )

        # Truncate prompt if needed
        prompt = truncate_for_token_limit(prompt)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a senior software architect providing code analysis insights. Be concise, specific, and actionable. Use Markdown formatting."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    tokens = data.get("usage", {}).get("total_tokens", 0)

                    return LLMResponse(
                        content=content,
                        tokens_used=tokens,
                        model=self.model,
                        success=True
                    )
                else:
                    error_msg = f"API error: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", error_msg)
                    except Exception:
                        pass

                    return LLMResponse(
                        content="",
                        tokens_used=0,
                        model=self.model,
                        success=False,
                        error=error_msg
                    )

        except httpx.TimeoutException:
            return LLMResponse(
                content="",
                tokens_used=0,
                model=self.model,
                success=False,
                error="Request timed out"
            )
        except Exception as e:
            return LLMResponse(
                content="",
                tokens_used=0,
                model=self.model,
                success=False,
                error=str(e)
            )

    def generate_analysis_explanation(
        self,
        scores: Dict[str, Any],
        security_summary: Dict[str, Any],
        maintainability_summary: Dict[str, Any],
        architecture_summary: Dict[str, Any],
        tech_debt: Dict[str, Any],
        repo_name: str
    ) -> LLMResponse:
        """
        Generate a comprehensive explanation of analysis results.

        Args:
            scores: Score results
            security_summary: Security analysis summary
            maintainability_summary: Maintainability summary
            architecture_summary: Architecture summary
            tech_debt: Technical debt summary
            repo_name: Repository name

        Returns:
            LLMResponse with explanation
        """
        prompt = build_analysis_prompt(
            scores=scores,
            security_summary=security_summary,
            maintainability_summary=maintainability_summary,
            architecture_summary=architecture_summary,
            tech_debt=tech_debt,
            repo_name=repo_name
        )

        return self._make_request(prompt)

    def generate_security_explanation(
        self,
        security_summary: Dict[str, Any],
        repo_name: str
    ) -> LLMResponse:
        """
        Generate a security-focused explanation.

        Args:
            security_summary: Security analysis summary
            repo_name: Repository name

        Returns:
            LLMResponse with security explanation
        """
        prompt = build_security_explanation_prompt(
            security_summary=security_summary,
            repo_name=repo_name
        )

        return self._make_request(prompt)

    def generate_refactor_recommendations(
        self,
        tech_debt: Dict[str, Any],
        maintainability_summary: Dict[str, Any],
        architecture_summary: Dict[str, Any]
    ) -> LLMResponse:
        """
        Generate refactoring recommendations.

        Args:
            tech_debt: Technical debt summary
            maintainability_summary: Maintainability summary
            architecture_summary: Architecture summary

        Returns:
            LLMResponse with recommendations
        """
        prompt = build_refactor_recommendation_prompt(
            tech_debt=tech_debt,
            maintainability_summary=maintainability_summary,
            architecture_summary=architecture_summary
        )

        return self._make_request(prompt)


# Global client instance
groq_client = GroqClient()


def get_fallback_explanation(
    scores: Dict[str, Any],
    security_summary: Dict[str, Any],
    tech_debt: Dict[str, Any]
) -> str:
    """
    Generate a basic explanation when LLM is unavailable.
    This ensures the system functions even without LLM.

    Args:
        scores: Score results
        security_summary: Security summary
        tech_debt: Tech debt summary

    Returns:
        Basic markdown explanation
    """
    security_score = scores.get("security_score", 0)
    maintainability_score = scores.get("maintainability_score", 0)
    architecture_score = scores.get("architecture_score", 0)
    debt_index = scores.get("tech_debt_index", 0)
    urgency = scores.get("refactor_urgency", "Unknown")

    # Determine overall health
    avg_score = (security_score + maintainability_score + architecture_score) / 3

    if avg_score >= 80:
        health_status = "healthy"
        health_desc = "The codebase is in good condition."
    elif avg_score >= 60:
        health_status = "fair"
        health_desc = "The codebase has some areas needing attention."
    elif avg_score >= 40:
        health_status = "concerning"
        health_desc = "The codebase requires significant improvements."
    else:
        health_status = "critical"
        health_desc = "The codebase needs immediate attention."

    # Build explanation
    lines = [
        "## Executive Summary",
        f"The codebase is in **{health_status}** condition. {health_desc}",
        "",
        "## Key Metrics",
        f"- **Security Score:** {security_score}/100",
        f"- **Maintainability Score:** {maintainability_score}/100",
        f"- **Architecture Score:** {architecture_score}/100",
        f"- **Technical Debt Index:** {debt_index}/100",
        f"- **Refactor Urgency:** {urgency}",
        "",
        "## Security Overview",
    ]

    total_issues = security_summary.get("total_issues", 0)
    critical = security_summary.get("critical_count", 0)
    high = security_summary.get("high_count", 0)

    if total_issues == 0:
        lines.append("No security vulnerabilities detected.")
    else:
        lines.append(f"Found {total_issues} security issues.")
        if critical > 0:
            lines.append(f"- **{critical} critical** issues require immediate attention.")
        if high > 0:
            lines.append(f"- **{high} high** severity issues should be addressed soon.")

    lines.extend([
        "",
        "## Recommendations",
    ])

    if urgency == "Critical":
        lines.append("1. **Immediate:** Address all critical security vulnerabilities.")
        lines.append("2. **Short-term:** Reduce complexity in high-complexity functions.")
        lines.append("3. **Medium-term:** Refactor architectural issues.")
    elif urgency == "High":
        lines.append("1. Fix high-severity security issues.")
        lines.append("2. Improve documentation coverage.")
        lines.append("3. Address circular dependencies.")
    else:
        lines.append("1. Maintain current code quality standards.")
        lines.append("2. Address any remaining warnings.")
        lines.append("3. Consider incremental improvements.")

    lines.extend([
        "",
        "---",
        "*This is an automated summary. Enable Groq API for detailed AI-powered insights.*"
    ])

    return "\n".join(lines)
