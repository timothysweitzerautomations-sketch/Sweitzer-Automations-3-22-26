from __future__ import annotations

from pathlib import Path


def test_resume_builder_ui_is_static_and_on_device(project_root: Path) -> None:
    index = (project_root / "resume_builder" / "index.html").read_text()
    app = (project_root / "resume_builder" / "app.js").read_text()

    assert 'src="app.js"' in index
    assert "/api/" not in index
    assert "fetch(" not in app
    assert "XMLHttpRequest" not in app
    assert "ollama" not in app.lower()


def test_android_packages_resume_builder_without_internet(project_root: Path) -> None:
    manifest = (project_root / "android" / "app" / "src" / "main" / "AndroidManifest.xml").read_text()
    gradle = (project_root / "android" / "app" / "build.gradle").read_text()
    activity = (
        project_root
        / "android"
        / "app"
        / "src"
        / "main"
        / "java"
        / "com"
        / "sweitzer"
        / "resumebuilder"
        / "MainActivity.java"
    ).read_text()

    assert "android.permission.INTERNET" not in manifest
    assert 'applicationId "com.sweitzer.resumebuilder"' in gradle
    assert "copyResumeBuilderAssets" in gradle
    assert "resume_builder/index.html" in activity

