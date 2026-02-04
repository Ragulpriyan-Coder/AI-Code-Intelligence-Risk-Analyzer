"""LLM integration module for explanations."""
from app.llm.groq_client import (
    GroqClient,
    LLMResponse,
    groq_client,
    get_fallback_explanation,
)
from app.llm.prompt_builder import (
    build_analysis_prompt,
    build_security_explanation_prompt,
    build_refactor_recommendation_prompt,
)

__all__ = [
    "GroqClient",
    "LLMResponse",
    "groq_client",
    "get_fallback_explanation",
    "build_analysis_prompt",
    "build_security_explanation_prompt",
    "build_refactor_recommendation_prompt",
]
