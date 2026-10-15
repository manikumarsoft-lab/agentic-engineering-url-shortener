import pytest

from orchestrator.graph import GraphError, load_workflow_text

VALID = """
name: demo
version: 1.0.0
defaults: {timeout_s: 30, max_attempts: 3, backoff_s: 0.5}
nodes:
  - {id: a, agent: noop, produces: [design]}
  - {id: b, agent: noop, depends_on: [a]}
  - {id: c, agent: noop, depends_on: [a], consumes: [design], retry: {max_attempts: 1}}
  - {id: g, gate: {roles: [approver], timeout_s: 60, binds: [design]}, depends_on: [b, c]}
  - {id: d, agent: noop, depends_on: [g], fallback: {agent: emit, params: {}}}
"""


def test_loads_nodes_defaults_and_overrides():
    wf = load_workflow_text(VALID)
    assert list(wf.nodes) == ["a", "b", "c", "g", "d"]
    assert wf.nodes["b"].timeout_s == 30 and wf.nodes["b"].max_attempts == 3
    assert wf.nodes["c"].max_attempts == 1
    assert wf.nodes["g"].is_gate and wf.nodes["g"].gate.binds == ("design",)
    assert wf.nodes["d"].fallback.agent == "emit"


def test_downstream_closure_and_consumers():
    wf = load_workflow_text(VALID)
    assert wf.downstream({"c"}) == {"g", "d"}
    assert wf.downstream({"a"}) == {"b", "c", "g", "d"}
    assert wf.consumers("design") == {"c"}


@pytest.mark.parametrize("body, message", [
    ("- {id: a, agent: noop, depends_on: [b]}\n  - {id: b, agent: noop, depends_on: [a]}", "cycle"),
    ("- {id: a, agent: noop, depends_on: [zzz]}", "unknown dependency"),
    ("- {id: a, agent: noop}\n  - {id: a, agent: noop}", "duplicate"),
    ("- {id: a}", "exactly one"),
    ("- {id: a, agent: noop, on_failure: explode}", "on_failure"),
])
def test_invalid_graphs_are_refused(body, message):
    with pytest.raises(GraphError, match=message):
        load_workflow_text(f"name: bad\nversion: 1\nnodes:\n  {body}\n")
