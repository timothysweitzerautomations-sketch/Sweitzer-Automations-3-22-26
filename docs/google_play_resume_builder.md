# Google Play readiness: AI Resume Builder

This checklist captures the release work needed before publishing the AI Resume
Builder in Google Play Console.

## Current status

- The resume builder MVP lives in `resume_builder/` as a local browser app plus a
  Python stdlib server.
- The current Android project in `android/` still packages the Revenue Pulse and
  Flip Tracker dashboards. It does **not** yet package the resume builder UI.
- The MVP can call local Ollama on a desktop, but Android users will not have a
  local Ollama server available by default.

Before creating a production Play release, choose one mobile architecture:

1. **On-device only:** port the deterministic coaching logic into Java/Kotlin or
   browser JavaScript and keep resume text on the device.
2. **Hosted AI backend:** package the WebView/mobile UI and send resume text to a
   controlled HTTPS backend that performs AI coaching.
3. **Hybrid:** do deterministic checks on device, then make hosted AI rewrites an
   explicit opt-in feature.

## Recommended Play Console setup

- App name: choose a consumer-facing resume product name instead of the current
  repo/app name.
- Package/application ID: use a dedicated immutable ID, for example
  `com.sweitzer.resumebuilder`. Do not reuse it for unrelated apps.
- Release format: upload a signed Android App Bundle (`.aab`) for production.
- Target SDK: keep aligned with current Play requirements. The Android project
  currently targets SDK 35.
- Store listing: prepare screenshots, feature graphic, short description, full
  description, support email, and privacy-policy URL.
- Content rating: answer as a productivity/business app, with AI-generated
  content disclosure where applicable.

## Privacy and Data safety notes

Resume text can contain names, addresses, phone numbers, emails, employment
history, education history, salary clues, immigration details, and other personal
or sensitive information. Treat all pasted resume content as personal data.

If the app is **strictly on-device**:

- State clearly that resume text is processed on the device.
- Avoid analytics events that include resume text, job descriptions, or generated
  resume content.
- Disclose any diagnostic collection separately if crash reporting or analytics
  is added later.

If the app uses a **hosted backend or third-party AI API**:

- Use HTTPS only.
- Disclose that resume text and job descriptions are transmitted for AI coaching.
- Explain retention, deletion, subprocessors, and whether content is used to train
  models.
- Provide a user-visible way to request deletion if server-side content is stored.
- Avoid logging raw resumes, job descriptions, prompts, or generated outputs.

Google Play Data safety answers must match the implementation. Do not claim "no
data collected" if resume text leaves the device, is logged, or is retained.

## Store listing draft

Short description:

> Improve your resume with targeted AI coaching, keyword gaps, and stronger bullet
> drafts.

Full description starter:

> AI Resume Builder helps job seekers tailor a resume to a target role. Paste your
> current resume and a job description to see a readiness score, missing keywords,
> clearer bullet drafts, and next-step coaching. The app is designed to avoid
> inventing employers, degrees, dates, or metrics; it prompts you to add truthful
> proof where details are missing.

Suggested screenshot set:

1. Resume input screen with target role and job description fields.
2. Readiness score and keyword gaps.
3. Stronger bullet draft examples.
4. Privacy/local-processing explainer.

## Android implementation checklist

- Decide whether the Play app is a separate product from the existing Sweitzer
  Automations wrapper.
- Add or replace Android assets so the WebView opens the resume builder screen.
- Remove unnecessary Internet permission if the final app is on-device only.
- If hosted AI is used, keep Internet permission and add explicit in-app copy
  before sending resume text.
- Add app-specific launcher icons, app label, package ID, versioning, and signing.
- Test rotation, back navigation, offline behavior, and large pasted resumes.
- Build and upload a signed `.aab` through Android Studio or Gradle signing
  configuration.

## Pre-submit QA

- Confirm the app does not invent facts in generated resume content.
- Confirm users can edit all generated text before using it.
- Confirm privacy copy matches actual data flow.
- Confirm no raw resumes are written to local logs or remote logs.
- Run Android release build locally and install on at least one physical device.
- Complete closed testing before production rollout.

