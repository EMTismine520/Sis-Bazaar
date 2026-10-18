from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "deploy-pages.yml"
WEB_ROOT = ROOT / "web"


def test_pages_workflow_deploys_web_directory_on_main():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "branches:" in workflow
    assert "- main" in workflow
    assert "workflow_dispatch:" in workflow
    assert "contents: read" in workflow
    assert "pages: write" in workflow
    assert "id-token: write" in workflow
    assert "actions/checkout@v4" in workflow
    assert "actions/configure-pages@v5" in workflow
    assert "enablement: true" in workflow
    assert "actions/upload-pages-artifact@v3" in workflow
    assert "path: ./web" in workflow
    assert "actions/deploy-pages@v4" in workflow


def test_pages_artifact_has_entrypoint_and_local_assets():
    assert (WEB_ROOT / "index.html").is_file()
    assert (WEB_ROOT / "assets" / "cooking" / "cooking-pot.png").is_file()
    assert (WEB_ROOT / "assets" / "vegetable-bag-v2.png").is_file()
    assert (WEB_ROOT / "assets" / "meat-bag-v1.png").is_file()
