"""Phase 5 — IaC skeleton generation for an APPROVED architecture.

Only fires after Gate 2 (architecture review approval) — this turns a decision
into the infra prerequisites the JIRA breakdown already lists as its own tasks.

Deterministic templating for the primitives we can generate with verified
syntax (grounded in the vendored google-agents-cli-deploy terraform-patterns
skill: google_bigquery_dataset/table, google_secret_manager_secret + IAM member
resources). Anything requiring current, version-sensitive wiring we are NOT
confident about (the exact Cloud Scheduler -> Cloud Run Jobs HTTP invocation
contract) is left as an explicit, flagged TODO rather than hallucinated HCL —
same doc-gate discipline as the code-generation rule in docs/architecture.md.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

_MAIN_TF_TEMPLATE = """\
# Generated IaC skeleton for: {slug}
# Pattern: lightweight (Cloud Run Job + Cloud Scheduler + BigQuery + Secret Manager)
# Review before `terraform apply` — see README.md in this folder.

resource "google_bigquery_dataset" "{tf_name}_dataset" {{
  dataset_id = "{dataset_id}"
  project    = "{project_id}"
  location   = "{region}"
}}

resource "google_bigquery_table" "{tf_name}_table" {{
  dataset_id = google_bigquery_dataset.{tf_name}_dataset.dataset_id
  table_id   = "{table_id}"
  project    = "{project_id}"
}}

resource "google_secret_manager_secret" "{tf_name}_secret" {{
  secret_id = "{secret_id}"
  project   = "{project_id}"
  replication {{
    auto {{}}
  }}
}}

resource "google_secret_manager_secret_iam_member" "{tf_name}_secret_access" {{
  secret_id = google_secret_manager_secret.{tf_name}_secret.secret_id
  project   = "{project_id}"
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:{project_id}-compute@developer.gserviceaccount.com"
}}

# TODO(verify): Cloud Run Job + Cloud Scheduler wiring is version-sensitive
# (the exact HTTP invocation contract for triggering a Cloud Run Job execution
# from Cloud Scheduler changes across API versions). Verify the current syntax
# against Google Cloud's docs (or delegate to a research-grounded agent) before
# adding `google_cloud_run_v2_job` and `google_cloud_scheduler_job` resources
# here. Target schedule: "{cron_schedule}".
"""

_README_TEMPLATE = """\
# Generated infra skeleton: {slug}

Scaffolded by the PDLC agent's IaC tool after architecture approval (Gate 2).
Covers the verified-syntax primitives only — see the TODO in `main.tf` for the
piece that needs verification before `terraform apply`.

## What's generated
- BigQuery dataset `{dataset_id}` + table `{table_id}`
- Secret Manager secret `{secret_id}` + accessor IAM binding

## Not yet generated (flagged, not guessed)
- Cloud Run Job + Cloud Scheduler wiring (needs current-syntax verification)

## Apply
Review `main.tf`, resolve the TODO, then:
```
terraform init && terraform plan
```
"""


def generate_terraform_skeleton(
    slug: str,
    project_id: str,
    region: str,
    dataset_id: str,
    table_id: str,
    secret_id: str,
    cron_schedule: str,
    base_dir: str = "infra/generated",
) -> dict[str, Any]:
    """Write a minimal, honestly-scoped Terraform skeleton for an approved design.

    Args:
        slug: short kebab-case identifier for the request, used as the output
            subfolder name.
        project_id, region: target GCP project and region.
        dataset_id, table_id: BigQuery dataset/table to provision.
        secret_id: Secret Manager secret to provision (e.g. the source API key).
        cron_schedule: intended cron schedule (recorded, not yet wired — see TODO).
        base_dir: directory the skeleton is written under (relative to cwd).

    Returns:
        {directory, files: [paths written]}.
    """
    tf_name = slug.replace("-", "_")
    directory = Path(base_dir) / slug
    directory.mkdir(parents=True, exist_ok=True)

    main_tf = directory / "main.tf"
    main_tf.write_text(
        _MAIN_TF_TEMPLATE.format(
            slug=slug,
            tf_name=tf_name,
            project_id=project_id,
            region=region,
            dataset_id=dataset_id,
            table_id=table_id,
            secret_id=secret_id,
            cron_schedule=cron_schedule,
        ),
        encoding="utf-8",
    )

    readme = directory / "README.md"
    readme.write_text(
        _README_TEMPLATE.format(slug=slug, dataset_id=dataset_id, table_id=table_id, secret_id=secret_id),
        encoding="utf-8",
    )

    return {"directory": str(directory), "files": [str(main_tf), str(readme)]}
