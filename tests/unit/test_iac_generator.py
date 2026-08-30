"""Phase 5 — IaC skeleton generator tests (deterministic file templating)."""

from pdlc_agent.tools.iac_generator import generate_terraform_skeleton


def _generate(tmp_path, **overrides):
    params = dict(
        slug="stock-tracker",
        project_id="hl2-gcpp-ccoe-ge-h-agenti-1711",
        region="us-central1",
        dataset_id="stock_tracker",
        table_id="fact_daily_price",
        secret_id="stock-api-key",
        cron_schedule="0 21 * * 1-5",
        base_dir=str(tmp_path),
    )
    params.update(overrides)
    return generate_terraform_skeleton(**params)


def test_writes_main_tf_and_readme(tmp_path):
    result = _generate(tmp_path)
    written = [p for p in result["files"]]
    assert any(p.endswith("main.tf") for p in written)
    assert any(p.endswith("README.md") for p in written)
    for p in written:
        assert __import__("pathlib").Path(p).exists()


def test_main_tf_contains_bigquery_and_secret_resources(tmp_path):
    _generate(tmp_path)
    content = (tmp_path / "stock-tracker" / "main.tf").read_text()
    assert "stock_tracker" in content
    assert "fact_daily_price" in content
    assert "stock-api-key" in content
    assert "hl2-gcpp-ccoe-ge-h-agenti-1711" in content


def test_main_tf_flags_scheduler_wiring_for_verification(tmp_path):
    """Must not silently hallucinate the Scheduler->Cloud Run Job wiring."""
    _generate(tmp_path)
    content = (tmp_path / "stock-tracker" / "main.tf").read_text()
    assert "TODO(verify)" in content
    assert "0 21 * * 1-5" in content


def test_directory_is_named_after_slug(tmp_path):
    result = _generate(tmp_path, slug="other-request")
    assert result["directory"].endswith("other-request")
