"""
Deterministic resume coaching helpers for the local Resume Builder app.

The browser UI can ask a local LLM for deeper rewrites, but these helpers keep
the product useful and testable even when Ollama is not running.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

ACTION_VERBS = frozenset(
    {
        "accelerated",
        "achieved",
        "automated",
        "built",
        "created",
        "delivered",
        "designed",
        "drove",
        "improved",
        "increased",
        "launched",
        "led",
        "managed",
        "optimized",
        "owned",
        "reduced",
        "shipped",
        "streamlined",
        "trained",
    }
)

WEAK_OPENERS = (
    "responsible for",
    "worked on",
    "helped with",
    "assisted with",
    "participated in",
    "involved in",
)

STOPWORDS = frozenset(
    {
        "about",
        "across",
        "after",
        "also",
        "and",
        "are",
        "based",
        "both",
        "can",
        "candidate",
        "company",
        "customer",
        "customers",
        "data",
        "description",
        "develop",
        "development",
        "each",
        "experience",
        "from",
        "have",
        "include",
        "including",
        "into",
        "job",
        "more",
        "must",
        "our",
        "role",
        "skills",
        "team",
        "teams",
        "that",
        "the",
        "their",
        "this",
        "through",
        "using",
        "with",
        "work",
        "working",
        "years",
    }
)

SECTION_HINTS = {
    "summary": ("summary", "profile", "objective"),
    "experience": ("experience", "employment", "work history"),
    "skills": ("skills", "technologies", "tools"),
    "education": ("education", "certification", "certifications"),
}


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z][a-z0-9+#.-]{2,}", text.lower())


def _shorten(text: str, limit: int = 4000) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3].rstrip() + "..."


def split_bullets(text: str) -> list[str]:
    """Return likely resume bullets from pasted resume/accomplishment text."""
    bullets: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[\-*•\u2022\d.)\s]+", "", line).strip()
        if len(line) >= 12:
            bullets.append(line)
    return bullets


def has_metric(text: str) -> bool:
    return bool(
        re.search(
            r"(\d+|%|\$|\bpercent\b|\bmillion\b|\bthousand\b|\bhours?\b|\bdays?\b|\bweeks?\b|\bx\b)",
            text.lower(),
        )
    )


def starts_with_action_verb(text: str) -> bool:
    words = _words(text)
    return bool(words and words[0] in ACTION_VERBS)


def extract_keywords(job_description: str, limit: int = 14) -> list[str]:
    """Extract high-signal keywords from a job description without dependencies."""
    words = [w.strip(".-") for w in _words(job_description)]
    counts = Counter(
        word
        for word in words
        if len(word) >= 4 and word not in STOPWORDS and not word.isdigit()
    )
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [word for word, _ in ranked[:limit]]


def keyword_gaps(resume_text: str, job_description: str, limit: int = 8) -> list[str]:
    resume_words = set(_words(resume_text))
    return [keyword for keyword in extract_keywords(job_description) if keyword not in resume_words][
        :limit
    ]


def _present_sections(resume_text: str) -> list[str]:
    lowered = resume_text.lower()
    present: list[str] = []
    for section, hints in SECTION_HINTS.items():
        if any(hint in lowered for hint in hints):
            present.append(section)
    return present


def rewrite_bullet(bullet: str) -> str:
    """Create a stronger bullet draft without inventing outcomes."""
    original = re.sub(r"\s+", " ", bullet).strip()
    cleaned = original
    for opener in WEAK_OPENERS:
        if cleaned.lower().startswith(opener):
            cleaned = cleaned[len(opener) :].strip(" :-")
            break

    lowered = cleaned.lower()
    if any(word in lowered for word in ("automate", "script", "system", "tool", "dashboard")):
        verb = "Built"
    elif any(word in lowered for word in ("lead", "manage", "mentor", "train")):
        verb = "Led"
    elif any(word in lowered for word in ("reduce", "save", "faster", "cost", "time")):
        verb = "Reduced"
    elif any(word in lowered for word in ("increase", "growth", "revenue", "sales")):
        verb = "Increased"
    else:
        verb = "Improved"

    if starts_with_action_verb(cleaned):
        draft = cleaned[0].upper() + cleaned[1:]
    else:
        draft = f"{verb} {cleaned[:1].lower()}{cleaned[1:]}"

    if has_metric(draft):
        return draft.rstrip(".") + "."
    return (
        draft.rstrip(".")
        + " -- add a truthful metric for scope, speed, revenue, cost, quality, or volume."
    )


def analyze_resume(profile: dict[str, Any]) -> dict[str, Any]:
    """Score a resume draft and return concrete coaching outputs."""
    target_role = str(profile.get("target_role", "")).strip()
    experience_level = str(profile.get("experience_level", "")).strip() or "unspecified"
    resume_text = str(profile.get("resume_text", "")).strip()
    job_description = str(profile.get("job_description", "")).strip()
    accomplishments = profile.get("accomplishments", "")
    if isinstance(accomplishments, list):
        accomplishment_text = "\n".join(str(item) for item in accomplishments)
    else:
        accomplishment_text = str(accomplishments)

    combined_resume = "\n".join(part for part in (resume_text, accomplishment_text) if part)
    bullets = split_bullets(combined_resume)
    sections = _present_sections(resume_text)
    gaps = keyword_gaps(combined_resume, job_description) if job_description else []

    score = 45
    strengths: list[str] = []
    issues: list[str] = []

    word_count = len(_words(combined_resume))
    if word_count >= 250:
        score += 12
        strengths.append("Substantial resume detail is available for coaching.")
    elif word_count >= 90:
        score += 7
    else:
        issues.append("Add more role, project, and impact detail before finalizing.")

    if target_role:
        score += 8
        strengths.append(f"Target role is defined: {target_role}.")
    else:
        issues.append("Choose a target role so the resume can be tailored.")

    if sections:
        score += min(10, len(sections) * 3)
    missing_sections = [name for name in SECTION_HINTS if name not in sections]
    if missing_sections:
        issues.append("Consider adding clear sections for: " + ", ".join(missing_sections) + ".")

    metric_count = sum(1 for bullet in bullets if has_metric(bullet))
    metric_ratio = metric_count / len(bullets) if bullets else 0.0
    if metric_ratio >= 0.45:
        score += 15
        strengths.append("Many bullets already include measurable impact.")
    elif metric_ratio >= 0.2:
        score += 8
    else:
        issues.append("Quantify more bullets with scope, frequency, dollars, time, or percentages.")

    action_count = sum(1 for bullet in bullets if starts_with_action_verb(bullet))
    action_ratio = action_count / len(bullets) if bullets else 0.0
    if action_ratio >= 0.55:
        score += 10
        strengths.append("Several bullets begin with strong action verbs.")
    elif bullets:
        issues.append("Start more bullets with direct action verbs such as built, led, improved, or reduced.")

    if job_description:
        keywords = extract_keywords(job_description)
        coverage = 1.0 - (len(gaps) / len(keywords) if keywords else 0.0)
        score += round(max(0.0, coverage) * 10)
        if gaps:
            issues.append("Tailor language to match important job keywords.")
        else:
            strengths.append("Resume language already covers the strongest job-description keywords.")

    improved_bullets = [rewrite_bullet(bullet) for bullet in bullets[:6]]
    if not improved_bullets and accomplishment_text:
        improved_bullets = [rewrite_bullet(accomplishment_text)]

    summary_bits = []
    if target_role:
        summary_bits.append(target_role)
    if experience_level != "unspecified":
        summary_bits.append(experience_level)
    role_phrase = " / ".join(summary_bits) if summary_bits else "Resume candidate"
    keyword_phrase = ", ".join(extract_keywords(job_description, limit=5)) if job_description else ""
    professional_summary = (
        f"{role_phrase} with experience aligned to the resume details provided"
        + (f" and target keywords including {keyword_phrase}" if keyword_phrase else "")
        + ". Replace this with a sharper summary after validating the specific accomplishments."
    )

    score = max(0, min(100, int(score)))
    return {
        "score": score,
        "target_role": target_role,
        "experience_level": experience_level,
        "word_count": word_count,
        "metric_bullet_count": metric_count,
        "bullet_count": len(bullets),
        "keyword_gaps": gaps,
        "present_sections": sections,
        "strengths": strengths,
        "issues": issues,
        "improved_bullets": improved_bullets,
        "professional_summary": professional_summary,
        "next_steps": [
            "Pick one target job and mirror its most important skill language truthfully.",
            "Rewrite bullets as action + scope + measurable outcome.",
            "Remove generic duties that do not prove impact for the target role.",
        ],
    }


def build_ai_prompt(profile: dict[str, Any], analysis: dict[str, Any] | None = None) -> str:
    analysis = analysis or analyze_resume(profile)
    return f"""You are an expert resume coach. Improve the resume for the target role while following these rules:
- Do not invent employers, degrees, certifications, metrics, dates, tools, or achievements.
- If a metric is missing, ask for it or use bracketed placeholders such as [percent] or [dollar amount].
- Keep the candidate's experience truthful and concise.
- Prefer ATS-friendly language and strong bullet structure.

Target role: {profile.get("target_role", "")}
Experience level: {profile.get("experience_level", "")}
Keyword gaps to consider: {", ".join(analysis.get("keyword_gaps", [])) or "none detected"}

Current resume:
{_shorten(str(profile.get("resume_text", "")), 5000)}

Job description:
{_shorten(str(profile.get("job_description", "")), 3500)}

Extra accomplishments or notes:
{_shorten(str(profile.get("accomplishments", "")), 2500)}

Return:
1. A stronger professional summary.
2. 6-8 rewritten resume bullets.
3. A short list of missing proof points the candidate should provide.
4. ATS keywords to add only where truthful.
"""


def build_fallback_response(profile: dict[str, Any]) -> dict[str, Any]:
    analysis = analyze_resume(profile)
    return {
        "source": "deterministic",
        "model": None,
        "analysis": analysis,
        "ai_prompt": build_ai_prompt(profile, analysis),
        "ai_response": (
            "Local AI was not used for this response. The structured coaching below is generated "
            "by the resume engine so you can keep working offline."
        ),
    }

