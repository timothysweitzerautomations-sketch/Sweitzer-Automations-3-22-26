const ACTION_VERBS = new Set([
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
]);

const WEAK_OPENERS = [
  "responsible for",
  "worked on",
  "helped with",
  "assisted with",
  "participated in",
  "involved in",
];

const STOPWORDS = new Set([
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
]);

const SHORT_TECH_TERMS = new Set(["ai", "bi", "ci", "cd", "go", "ml", "qa", "r", "sql", "ui", "ux"]);

const SECTION_HINTS = {
  summary: ["summary", "profile", "objective"],
  experience: ["experience", "employment", "work history"],
  skills: ["skills", "technologies", "tools"],
  education: ["education", "certification", "certifications"],
};

function words(text) {
  return (text.toLowerCase().match(/[a-z][a-z0-9+#.-]{1,}/g) || []);
}

function splitBullets(text) {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim().replace(/^[\-*\u2022\d.)\s]+/, "").trim())
    .filter((line) => line.length >= 12);
}

function hasMetric(text) {
  return /(\d+|%|\$|\bpercent\b|\bmillion\b|\bthousand\b|\bhours?\b|\bdays?\b|\bweeks?\b|\bx\b)/i.test(text);
}

function startsWithActionVerb(text) {
  const found = words(text);
  return found.length > 0 && ACTION_VERBS.has(found[0]);
}

function extractKeywords(jobDescription, limit = 14) {
  const counts = new Map();
  for (const raw of words(jobDescription)) {
    const word = raw.replace(/^[.-]+|[.-]+$/g, "");
    if (!word || word.match(/^\d+$/)) continue;
    if (word.length < 4 && !SHORT_TECH_TERMS.has(word)) continue;
    if (STOPWORDS.has(word)) continue;
    counts.set(word, (counts.get(word) || 0) + 1);
  }
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, limit)
    .map(([word]) => word);
}

function keywordGaps(resumeText, jobDescription, limit = 8) {
  const resumeWords = new Set(words(resumeText));
  return extractKeywords(jobDescription).filter((keyword) => !resumeWords.has(keyword)).slice(0, limit);
}

function presentSections(resumeText) {
  const lowered = resumeText.toLowerCase();
  return Object.entries(SECTION_HINTS)
    .filter(([, hints]) => hints.some((hint) => lowered.includes(hint)))
    .map(([section]) => section);
}

function rewriteBullet(bullet) {
  const original = bullet.replace(/\s+/g, " ").trim();
  let cleaned = original;
  const lower = cleaned.toLowerCase();
  for (const opener of WEAK_OPENERS) {
    if (lower.startsWith(opener)) {
      cleaned = cleaned.slice(opener.length).replace(/^[\s:-]+/, "");
      break;
    }
  }

  const lowered = cleaned.toLowerCase();
  let verb = "Improved";
  if (/(automate|script|system|tool|dashboard)/.test(lowered)) verb = "Built";
  else if (/(lead|manage|mentor|train)/.test(lowered)) verb = "Led";
  else if (/(reduce|save|faster|cost|time)/.test(lowered)) verb = "Reduced";
  else if (/(increase|growth|revenue|sales)/.test(lowered)) verb = "Increased";

  let draft = cleaned;
  if (!startsWithActionVerb(cleaned)) {
    draft = `${verb} ${cleaned.slice(0, 1).toLowerCase()}${cleaned.slice(1)}`;
  } else {
    draft = cleaned.slice(0, 1).toUpperCase() + cleaned.slice(1);
  }

  if (hasMetric(draft)) return `${draft.replace(/\.$/, "")}.`;
  return `${draft.replace(/\.$/, "")} -- add a truthful metric for scope, speed, revenue, cost, quality, or volume.`;
}

function buildResumeOutput(profile) {
  const targetRole = (profile.target_role || "").trim();
  const experienceLevel = (profile.experience_level || "unspecified").trim() || "unspecified";
  const resumeText = (profile.resume_text || "").trim();
  const jobDescription = (profile.job_description || "").trim();
  const accomplishments = (profile.accomplishments || "").trim();
  const combinedResume = [resumeText, accomplishments].filter(Boolean).join("\n");
  const bulletList = splitBullets(combinedResume);
  const sections = presentSections(resumeText);
  const gaps = jobDescription ? keywordGaps(combinedResume, jobDescription) : [];

  let score = 45;
  const strengths = [];
  const issues = [];
  const wordCount = words(combinedResume).length;

  if (wordCount >= 250) {
    score += 12;
    strengths.push("Substantial resume detail is available for coaching.");
  } else if (wordCount >= 90) {
    score += 7;
  } else {
    issues.push("Add more role, project, and impact detail before finalizing.");
  }

  if (targetRole) {
    score += 8;
    strengths.push(`Target role is defined: ${targetRole}.`);
  } else {
    issues.push("Choose a target role so the resume can be tailored.");
  }

  if (sections.length) score += Math.min(10, sections.length * 3);
  const missingSections = Object.keys(SECTION_HINTS).filter((section) => !sections.includes(section));
  if (missingSections.length) {
    issues.push(`Consider adding clear sections for: ${missingSections.join(", ")}.`);
  }

  const metricCount = bulletList.filter(hasMetric).length;
  const metricRatio = bulletList.length ? metricCount / bulletList.length : 0;
  if (metricRatio >= 0.45) {
    score += 15;
    strengths.push("Many bullets already include measurable impact.");
  } else if (metricRatio >= 0.2) {
    score += 8;
  } else {
    issues.push("Quantify more bullets with scope, frequency, dollars, time, or percentages.");
  }

  const actionCount = bulletList.filter(startsWithActionVerb).length;
  const actionRatio = bulletList.length ? actionCount / bulletList.length : 0;
  if (actionRatio >= 0.55) {
    score += 10;
    strengths.push("Several bullets begin with strong action verbs.");
  } else if (bulletList.length) {
    issues.push("Start more bullets with direct action verbs such as built, led, improved, or reduced.");
  }

  if (jobDescription) {
    const keywords = extractKeywords(jobDescription);
    const coverage = keywords.length ? 1 - gaps.length / keywords.length : 0;
    score += Math.round(Math.max(0, coverage) * 10);
    if (gaps.length) issues.push("Tailor language to match important job keywords.");
    else strengths.push("Resume language already covers the strongest job-description keywords.");
  }

  const keywordPhrase = jobDescription ? extractKeywords(jobDescription, 5).join(", ") : "";
  const summaryParts = [];
  if (targetRole) summaryParts.push(targetRole);
  if (experienceLevel !== "unspecified") summaryParts.push(experienceLevel);
  const rolePhrase = summaryParts.length ? summaryParts.join(" / ") : "Resume candidate";

  return {
    score: Math.max(0, Math.min(100, Math.trunc(score))),
    targetRole,
    experienceLevel,
    wordCount,
    bulletCount: bulletList.length,
    metricBulletCount: metricCount,
    keywordGaps: gaps,
    presentSections: sections,
    strengths,
    issues,
    improvedBullets: bulletList.slice(0, 6).map(rewriteBullet),
    professionalSummary:
      `${rolePhrase} with experience aligned to the resume details provided` +
      (keywordPhrase ? ` and target keywords including ${keywordPhrase}` : "") +
      ". Replace this with a sharper summary after validating the specific accomplishments.",
    nextSteps: [
      "Pick one target job and mirror its most important skill language truthfully.",
      "Rewrite bullets as action + scope + measurable outcome.",
      "Remove generic duties that do not prove impact for the target role.",
    ],
  };
}

function buildPrompt(profile, output) {
  return `You are an expert resume coach. Improve this resume for the target role.

Rules:
- Do not invent employers, degrees, certifications, metrics, dates, tools, or achievements.
- If a metric is missing, use bracketed placeholders such as [percent] or [dollar amount].
- Keep the candidate's experience truthful and concise.
- Prefer ATS-friendly language and strong bullet structure.

Target role: ${profile.target_role || ""}
Experience level: ${profile.experience_level || ""}
Keyword gaps to consider: ${output.keywordGaps.join(", ") || "none detected"}

Current resume:
${profile.resume_text || ""}

Job description:
${profile.job_description || ""}

Extra accomplishments or notes:
${profile.accomplishments || ""}

Return:
1. A stronger professional summary.
2. 6-8 rewritten resume bullets.
3. A short list of missing proof points the candidate should provide.
4. ATS keywords to add only where truthful.`;
}

function setList(selector, items, emptyText) {
  const el = document.querySelector(selector);
  el.innerHTML = "";
  const values = items && items.length ? items : [emptyText];
  values.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    el.appendChild(li);
  });
}

function setTags(selector, items) {
  const el = document.querySelector(selector);
  el.innerHTML = "";
  const values = items && items.length ? items : ["No major gaps detected"];
  values.forEach((item) => {
    const tag = document.createElement("span");
    tag.className = "tag";
    tag.textContent = item;
    el.appendChild(tag);
  });
}

function render(output) {
  const score = output.score || 0;
  document.querySelector("#scoreValue").textContent = score;
  document.querySelector("#scoreRing").style.setProperty("--angle", `${score * 3.6}deg`);
  document.querySelector("#sourceLine").textContent =
    "On-device analysis complete. Resume text was processed in this app only.";
  document.querySelector("#wordCount").textContent = output.wordCount || 0;
  document.querySelector("#bulletCount").textContent = output.bulletCount || 0;
  document.querySelector("#metricCount").textContent = output.metricBulletCount || 0;
  document.querySelector("#summary").textContent = output.professionalSummary || "";

  setTags("#keywordGaps", output.keywordGaps);
  setList("#strengths", output.strengths, "Add more detail and the coach will identify strengths.");
  setList("#issues", output.issues, "No major issues detected.");
  setList("#bullets", output.improvedBullets, "Paste resume bullets to generate rewrites.");
  setList("#nextSteps", output.nextSteps, "Keep tailoring the resume to the target role.");
  document.querySelector("#results").classList.remove("hidden");
}

function showError(message) {
  const formError = document.querySelector("#formError");
  formError.textContent = message;
  formError.classList.remove("hidden");
}

function clearError() {
  const formError = document.querySelector("#formError");
  formError.textContent = "";
  formError.classList.add("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#resumeForm");
  let latestPrompt = "";

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    clearError();
    const profile = Object.fromEntries(new FormData(form).entries());
    if (!profile.resume_text && !profile.accomplishments) {
      showError("Paste a resume or add accomplishments before generating coaching.");
      return;
    }
    const output = buildResumeOutput(profile);
    latestPrompt = buildPrompt(profile, output);
    render(output);
  });

  document.querySelector("#copyPrompt").addEventListener("click", async () => {
    if (!latestPrompt) return;
    await navigator.clipboard.writeText(latestPrompt);
    const button = document.querySelector("#copyPrompt");
    button.textContent = "Copied";
    setTimeout(() => {
      button.textContent = "Copy offline prompt";
    }, 1200);
  });
});
