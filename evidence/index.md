# Evidence index

Every run recorded in the orchestrator database, including failed, aborted and safe-stopped
runs. Runs labelled `test` are scripted test runs and are not scenario evidence.

| Run | Workflow | Labels | State | Reason | Created (UTC) | Evidence |
|-----|----------|--------|-------|--------|---------------|----------|
| run_1491b1c537664814 | scn-a | demonstration | COMPLETED |  | 2026-10-16T14:18:01.268394+00:00 | [run_1491b1c537664814/](run_1491b1c537664814/) |
| run_bc533834c7dc4e5e | scn-b | demonstration | COMPLETED |  | 2026-10-16T14:25:00.018878+00:00 | [run_bc533834c7dc4e5e/](run_bc533834c7dc4e5e/) |
| run_77723ef73ccf4ea7 | scn-b | demonstration, fault-injection | FAILED | rolled_back:tests_failed | 2026-10-16T14:32:22.645609+00:00 | [run_77723ef73ccf4ea7/](run_77723ef73ccf4ea7/) |
| run_03a5a6d9a2154bea | scn-b-compensate | demonstration, fault-injection | FAILED | compensated:smoke_failed | 2026-10-16T14:35:14.061348+00:00 | [run_03a5a6d9a2154bea/](run_03a5a6d9a2154bea/) |
| run_fe1eef2844a541f2 | scn-c | demonstration | COMPLETED |  | 2026-10-16T14:40:40.481263+00:00 | [run_fe1eef2844a541f2/](run_fe1eef2844a541f2/) |
| run_5defbd091d494e4c | scn-c | demonstration, fault-injection | COMPLETED |  | 2026-10-16T14:44:37.273198+00:00 | [run_5defbd091d494e4c/](run_5defbd091d494e4c/) |
| run_4fae12b6c3f14ca6 | scn-c | demonstration | ABORTED | clarification option C: Withdraw the request | 2026-10-16T14:47:06.359816+00:00 | [run_4fae12b6c3f14ca6/](run_4fae12b6c3f14ca6/) |
