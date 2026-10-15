"""The running app must match the generated contract (specs/.../contracts/shortener-api.openapi.yaml)."""
from shortener.openapi import CONTRACT, generate, load, render


def test_app_matches_committed_contract(svc):
    svc.client()
    assert svc.app.openapi() == load(), "contract drift: run `python -m shortener.openapi` and review"
    assert render(generate()) == CONTRACT.read_text(encoding="utf-8")


def test_responses_carry_the_contract_fields(svc):
    schemas = load()["components"]["schemas"]
    c = svc.client()
    created = svc.create(c, "https://example.com/").json()
    assert set(created) == set(schemas["LinkOut"]["properties"])
    stats = c.get(f"/api/v1/links/{created['code']}/stats",
                  headers={"X-API-Key": svc.keys["consumer"]}).json()
    assert set(stats) == set(schemas["StatsOut"]["properties"])
    problem = c.get("/zzzzzzz").json()
    assert set(problem) == set(schemas["Problem"]["properties"])
    assert set(c.get("/health/ready").json()) == set(schemas["ReadyOut"]["properties"])
