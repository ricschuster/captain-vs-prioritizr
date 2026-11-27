# Review runs (2026-11-27)

Small scripts used during the CAPTAIN and prioritizr reviews
(`docs/design/01_captain_review.md`, `docs/design/02_prioritizr_review.md`).
They are exploratory, not the hands-on comparison, and the stack for that is
still to be chosen (ADR pending).

| Script | What it does | How to run |
|---|---|---|
| `captain_eval_static.py` | Rebuilds CAPTAIN v3's static toy example, reproduces its reward exactly, and compares the trained plan with random, greedy and exact MILP (HiGHS) plans. Exports the problem and plans to `static_toy_problem.npz`. | See `docs/design/review-notes/captain_code.md` section 10. Needs a CAPTAIN v3.0.0rc1 venv plus `highspy`, and a copy of `examples/static_prioritization.py` pointed at the toy data. Arguments: `<run dir> <out dir>`. |
| `prioritizr_example.R` | Min set on prioritizr's simulated data with four solvers at `gap = 0`, a boundary penalty variant, `eval_*` on an arbitrary external solution, and replacement and rank importance. | `SCRATCH_RLIB=<lib with prioritizr 9.0.1.1> Rscript prioritizr_example.R` |
| `prioritizr_solver_gap.R` | Same problem, Gurobi, HiGHS and CBC at `gap = 0.1` and `gap = 0`. | As above. |

`SCRATCH_RLIB` points at a library holding the reviewed prioritizr commit
(`1461139`); leave it empty to use the installed version. Gurobi, HiGHS, CBC
(`rcbc`) and Rsymphony must be installed for every branch to run.
