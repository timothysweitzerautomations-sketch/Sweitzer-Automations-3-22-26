from __future__ import annotations

from resume_builder.resume_engine import (
    analyze_resume,
    build_ai_prompt,
    extract_keywords,
    has_metric,
    rewrite_bullet,
)


def test_extract_keywords_prioritizes_repeated_job_terms() -> None:
    keywords = extract_keywords(
        "We need an analyst with Python, Python automation, reporting, dashboards, and SQL."
    )

    assert keywords[:3] == ["python", "analyst", "automation"]
    assert "with" not in keywords


def test_analyze_resume_reports_keyword_gaps_and_metrics() -> None:
    profile = {
        "target_role": "Operations Analyst",
        "experience_level": "Mid-level",
        "resume_text": """
Summary
Operations specialist.

Experience
- Built a spreadsheet tracker that reduced weekly reconciliation time by 40%.
- Worked on order routing and vendor updates.

Skills
Excel, vendor management
""",
        "job_description": "Operations analyst role requiring Python automation, SQL dashboards, and vendor reporting.",
    }

    result = analyze_resume(profile)

    assert result["score"] > 50
    assert result["metric_bullet_count"] == 1
    assert "python" in result["keyword_gaps"]
    assert "sql" in result["keyword_gaps"]
    assert "summary" in result["present_sections"]
    assert result["improved_bullets"]


def test_rewrite_bullet_adds_metric_prompt_without_inventing_number() -> None:
    rewritten = rewrite_bullet("Responsible for improving onboarding process")

    assert rewritten.startswith("Improved improving onboarding process")
    assert "truthful metric" in rewritten
    assert not has_metric(rewritten)


def test_build_ai_prompt_forbids_fabrication() -> None:
    profile = {
        "target_role": "Customer Success Manager",
        "experience_level": "Senior",
        "resume_text": "Led renewals process and trained teammates.",
        "job_description": "Customer success manager with renewals and stakeholder management.",
    }

    prompt = build_ai_prompt(profile)

    assert "Do not invent employers" in prompt
    assert "Target role: Customer Success Manager" in prompt
    assert "bracketed placeholders" in prompt

