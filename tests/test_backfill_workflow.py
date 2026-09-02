from pathlib import Path

import yaml


class WorkflowLoader(yaml.SafeLoader):
    pass


for first_char, resolvers in WorkflowLoader.yaml_implicit_resolvers.copy().items():
    WorkflowLoader.yaml_implicit_resolvers[first_char] = [
        resolver
        for resolver in resolvers
        if resolver[0] != "tag:yaml.org,2002:bool"
    ]


def test_backfill_workflow_is_manual_bounded_and_gemini_only():
    data = yaml.load(
        Path(".github/workflows/backfill-feed.yml").read_text(),
        Loader=WorkflowLoader,
    )
    dispatch = data["on"]["workflow_dispatch"]
    assert set(dispatch["inputs"]) == {"since", "until", "limit"}
    assert dispatch["inputs"]["limit"]["default"] == "15"

    job = data["jobs"]["backfill"]
    run_step = next(step for step in job["steps"] if step.get("id") == "backfill")
    assert set(run_step["env"]) == {"GEMINI_API_KEY", "GEMINI_ANALYSIS_MODEL"}
    assert "pipeline.backfill_feed" in run_step["run"]
    assert "--direct-only" in run_step["run"]
    assert any(step.get("run") == "npm run build" for step in job["steps"])
