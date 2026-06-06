# Google Play readiness: AI Resume Builder

This checklist captures the release work for publishing the on-device AI Resume
Builder in Google Play Console.

## Current status

- The resume builder MVP lives in `resume_builder/` as static HTML and JavaScript.
- The Android project in `android/` now packages `resume_builder/index.html` and
  `resume_builder/app.js` into a WebView app.
- The Android app loads local assets through `WebViewAssetLoader`.
- The Android manifest does not request Internet permission.
- Resume text, job descriptions, scoring, keyword-gap detection, and bullet
  suggestions run on-device only in this MVP.

Architecture decision for v1: **on-device only**. Hosted AI can be added later as
an explicit opt-in feature, but doing so will require privacy-policy, backend,
rate-limit, and Play Data safety updates.

## Recommended Play Console setup

- App name: `AI Resume Builder` unless you choose a more specific brand name.
- Package/application ID: `com.sweitzer.resumebuilder`. Keep this ID stable once
  it is published.
- Release format: upload a signed Android App Bundle (`.aab`) for production.
- Target SDK: keep aligned with current Play requirements. The Android project
  currently targets SDK 35.
- Store listing: prepare screenshots, feature graphic, short description, full
  description, support email, and privacy-policy URL.
- Content rating: answer as a productivity/business app. There is no hosted AI
  in v1, but the app does generate local resume suggestions from user-provided
  text.

## Privacy and Data safety notes

Resume text can contain names, addresses, phone numbers, emails, employment
history, education history, salary clues, immigration details, and other personal
or sensitive information. Treat all pasted resume content as personal data.

For the current on-device-only build:

- Resume text and job descriptions are processed locally in the WebView.
- The app does not transmit resume text to a server.
- The app does not request Internet permission.
- The app does not include analytics, ads, crash reporting, or hosted AI calls.
- Do not log raw resumes, job descriptions, prompts, or generated outputs if
  diagnostic logging is added later.

Suggested Play Data safety posture for the current build: no data collected or
shared by the app. Verify this again before submission; the answer must change if
you add network calls, analytics, ads, crash reporting, accounts, cloud sync, or
hosted AI.

If hosted AI is added later:

- Use HTTPS only.
- Make sending resume text an explicit opt-in action.
- Disclose that resume text and job descriptions are transmitted for AI coaching.
- Explain retention, deletion, subprocessors, and whether content is used to train
  models.
- Provide a user-visible way to request deletion if server-side content is stored.
- Avoid logging raw resumes, job descriptions, prompts, or generated outputs.

## Store listing draft

Short description:

> Improve your resume with private, on-device coaching, keyword gaps, and stronger
> bullet drafts.

Full description starter:

> AI Resume Builder helps job seekers tailor a resume to a target role without
> sending resume text to a server. Paste your current resume and a job description
> to see a readiness score, missing keywords, clearer bullet drafts, and next-step
> coaching. The app is designed to avoid inventing employers, degrees, dates, or
> metrics; it prompts you to add truthful proof where details are missing.

Suggested screenshot set:

1. Resume input screen with target role and job description fields.
2. Readiness score and keyword gaps.
3. Stronger bullet draft examples.
4. Privacy/on-device-processing explainer.

## Android implementation checklist

Completed for the current MVP branch:

- Android app opens the resume builder screen instead of the older dashboards.
- Gradle copies only `resume_builder/index.html` and `resume_builder/app.js` into
  app assets.
- App label is `AI Resume Builder`.
- Application ID is `com.sweitzer.resumebuilder`.
- Internet permission is removed.

Still needed before a public Play release:

- Replace launcher icons with resume-builder-specific artwork.
- Create a signed release `.aab`.
- Add a privacy-policy URL that matches the on-device-only data flow.
- Capture phone screenshots from a release-like build.
- Test rotation, back navigation, offline behavior, and large pasted resumes.
- Run closed testing before production rollout.

## Pre-submit QA

- Confirm the app does not invent facts in generated resume content.
- Confirm users can edit or ignore all generated text before using it.
- Confirm privacy copy matches actual data flow.
- Confirm no raw resumes are written to local logs or remote logs.
- Confirm the release manifest has no Internet permission.
- Run Android release build locally and install on at least one physical device.
- Complete closed testing before production rollout.
