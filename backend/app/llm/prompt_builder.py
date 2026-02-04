"""
Prompt builder for LLM explanations.
Constructs structured prompts from analysis summaries.
IMPORTANT: Never sends raw source code to LLM - only JSON summaries.
"""
from typing import Dict, Any, Optional
import json


def build_analysis_prompt(
    scores: Dict[str, Any],
    security_summary: Dict[str, Any],
    maintainability_summary: Dict[str, Any],
    architecture_summary: Dict[str, Any],
    tech_debt: Dict[str, Any],
    repo_name: str
) -> str:
    """
    Build a prompt for LLM to explain analysis results.

    IMPORTANT: This function receives only pre-computed summaries,
    never raw source code. The LLM explains results, not analyzes code.

    Args:
        scores: Score results dictionary
        security_summary: Security analysis summary
        maintainability_summary: Maintainability analysis summary
        architecture_summary: Architecture analysis summary
        tech_debt: Technical debt summary
        repo_name: Name of the repository

    Returns:
        Formatted prompt string
    """
    # Build structured JSON summary for LLM
    analysis_summary = {
        "repository": repo_name,
        "scores": {
            "security": scores.get("security_score", 0),
            "maintainability": scores.get("maintainability_score", 0),
            "architecture": scores.get("architecture_score", 0),
            "tech_debt_index": scores.get("tech_debt_index", 0),
            "refactor_urgency": scores.get("refactor_urgency", "Unknown"),
        },
        "security": {
            "risk_level": security_summary.get("risk_level", "Unknown"),
            "total_issues": security_summary.get("total_issues", 0),
            "critical_count": security_summary.get("critical_count", 0),
            "high_count": security_summary.get("high_count", 0),
            "top_issues": [
                {
                    "title": i.get("title", ""),
                    "severity": i.get("severity", ""),
                    "description": i.get("description", "")[:100],
                }
                for i in security_summary.get("top_issues", [])[:5]
            ],
        },
        "maintainability": {
            "avg_complexity": maintainability_summary.get("average_complexity", 0),
            "avg_maintainability_index": maintainability_summary.get("average_maintainability_index", 0),
            "high_complexity_functions": len(maintainability_summary.get("high_complexity_functions", [])),
            "documentation_coverage": maintainability_summary.get("avg_documentation_score", 0),
        },
        "architecture": {
            "total_modules": architecture_summary.get("total_modules", 0),
            "circular_dependencies": architecture_summary.get("circular_dependencies_count", 0),
            "hub_modules_count": len(architecture_summary.get("hub_modules", [])),
            "modularity_score": architecture_summary.get("modularity_score", 0),
        },
        "tech_debt": {
            "index": tech_debt.get("index", 0),
            "urgency": tech_debt.get("urgency", "Unknown"),
            "priority_items_count": len(tech_debt.get("priority_items", [])),
        },
    }

    prompt = f"""You are a senior software architect reviewing code analysis results. Based on the following JSON summary of static analysis metrics (NOT raw code), provide a concise, actionable explanation.

ANALYSIS SUMMARY:
```json
{json.dumps(analysis_summary, indent=2)}
```

Provide your response in Markdown format with these sections:

## Executive Summary
A 2-3 sentence overview of the codebase health.

## Key Findings
List the 3-5 most important findings as bullet points.

## Security Assessment
Brief assessment of security posture and critical issues to address.

## Maintainability Assessment
Brief assessment of code maintainability and complexity concerns.

## Recommended Actions
Numbered list of 3-5 prioritized actions to improve the codebase.

Keep your response concise (under 400 words). Focus on actionable insights, not generic advice. Reference specific metrics from the analysis."""

    return prompt


def build_security_explanation_prompt(
    security_summary: Dict[str, Any],
    repo_name: str
) -> str:
    """
    Build a focused prompt for security-specific explanation.

    Args:
        security_summary: Security analysis summary
        repo_name: Name of the repository

    Returns:
        Formatted prompt string
    """
    summary = {
        "repository": repo_name,
        "risk_level": security_summary.get("risk_level", "Unknown"),
        "total_issues": security_summary.get("total_issues", 0),
        "severity_breakdown": security_summary.get("severity_breakdown", {}),
        "top_issues": [
            {
                "id": i.get("id", ""),
                "title": i.get("title", ""),
                "severity": i.get("severity", ""),
                "cwe": i.get("cwe", ""),
                "description": i.get("description", "")[:150],
            }
            for i in security_summary.get("top_issues", [])[:7]
        ],
    }

    prompt = f"""You are a security expert reviewing vulnerability scan results. Based on this JSON summary, provide a security assessment.

SECURITY SCAN SUMMARY:
```json
{json.dumps(summary, indent=2)}
```

Provide a brief Markdown response (under 250 words) covering:

## Risk Assessment
Overall security risk level and why.

## Critical Issues
The most important vulnerabilities to fix immediately.

## Remediation Priority
Ordered list of what to fix first.

Be specific about the vulnerabilities found. Reference CWE IDs where available."""

    return prompt


def build_refactor_recommendation_prompt(
    tech_debt: Dict[str, Any],
    maintainability_summary: Dict[str, Any],
    architecture_summary: Dict[str, Any]
) -> str:
    """
    Build a prompt for refactoring recommendations.

    Args:
        tech_debt: Technical debt summary
        maintainability_summary: Maintainability analysis summary
        architecture_summary: Architecture analysis summary

    Returns:
        Formatted prompt string
    """
    summary = {
        "tech_debt_index": tech_debt.get("index", 0),
        "refactor_urgency": tech_debt.get("urgency", "Unknown"),
        "priority_items": tech_debt.get("priority_items", [])[:8],
        "complexity_issues": {
            "high_complexity_count": len(maintainability_summary.get("high_complexity_functions", [])),
            "avg_complexity": maintainability_summary.get("average_complexity", 0),
        },
        "architecture_issues": {
            "circular_dependencies": architecture_summary.get("circular_dependencies_count", 0),
            "god_modules": len([i for i in architecture_summary.get("top_issues", []) if "god" in i.get("type", "").lower()]),
        },
    }

    prompt = f"""You are a technical lead planning a refactoring effort. Based on this technical debt analysis, provide refactoring recommendations.

TECHNICAL DEBT SUMMARY:
```json
{json.dumps(summary, indent=2)}
```

Provide a Markdown response (under 300 words) with:

## Refactoring Priority
What to tackle first and why.

## Quick Wins
2-3 improvements that can be done quickly.

## Strategic Improvements
2-3 larger refactoring efforts for long-term health.

## Risk Mitigation
How to refactor safely without introducing regressions.

Be practical and specific to the issues found."""

    return prompt


def truncate_for_token_limit(prompt: str, max_chars: int = 4000) -> str:
    """
    Truncate prompt if it exceeds character limit.
    Groq models have token limits, so we need to be conservative.

    Args:
        prompt: Original prompt
        max_chars: Maximum characters allowed

    Returns:
        Truncated prompt
    """
    if len(prompt) <= max_chars:
        return prompt

    # Find a good truncation point
    truncated = prompt[:max_chars]

    # Try to end at a complete JSON block
    last_brace = truncated.rfind("}")
    if last_brace > max_chars * 0.7:
        truncated = truncated[:last_brace + 1]

    # Add truncation notice
    truncated += "\n```\n[Summary truncated for length]\n"

    return truncated
