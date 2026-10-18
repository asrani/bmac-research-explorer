# BMAC Research Explorer

A local Streamlit prototype accompanying the revised BMAC conference paper.

## Run

Requires Python 3.10+.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local address printed by Streamlit. Run from this directory to load the included theme configuration. No accounts, APIs, or credentials are needed.

## Features

- Adjustable hub count, forwarding time, token holding time, occupancy, and heuristic mixture weight.
- Waiting-time curves and sensitivity to ring size.
- Step-by-step token traversal with a ring diagram.
- Static workload results and PDF download.
- CSV exports of analytical distances and reported results.

## Scientific scope

This is an explanatory model, not a Noxim replacement or a cycle-accurate BMAC implementation. Ideal bidirectional traversal has global knowledge of the requester. The paper's local backtracking rule is not simulated. The mixture is illustrative and unvalidated. No synthetic energy, area, or experimental performance results are generated. The model omits residual holding time and competing request queues.

The reported-data tab preserves source values (61%, 83%, 36%; ratios 1.62x and 1.84x) and flags the rounding discrepancy. A hotspot ratio is intentionally left unspecified. Exact raw-data verification and full controller semantics remain author tasks.

## Verify

```sh
python -m unittest discover -s tests
```
