# 02 prioritizr review

Status: draft, 2026-11-27. The same kind of review as
[`01_captain_review.md`](01_captain_review.md), done for prioritizr so both
tools are described on the same terms. Readers know prioritizr well, so this
focuses on what matters for the comparison rather than on basics.

Detailed, fully cited notes:

- [`review-notes/prioritizr_literature.md`](review-notes/prioritizr_literature.md):
  papers, docs, formulation inventory, dynamic-planning literature. Keys such
  as [R8] point to its References section.
- [`review-notes/prioritizr_code.md`](review-notes/prioritizr_code.md): source
  review at commit `1461139` (2026-10-23, version 9.0.1.1) with file:line
  citations.

## Summary

1. **What it is.** A composable builder for static mixed integer linear
   programs, solved to proven optimality or a reported gap by exact solvers.
   Main citation: Hanson et al. 2025, *Conservation Biology* 39: e14376,
   doi:10.1111/cobi.14376 (online September 2024).
2. **No notion of time.** Nothing in the code, branches or issues models
   dynamics, multiple periods, stochasticity or adaptive decisions
   [prioritizr_code section 3]. Uncertainty lives in the separate
   robust.prioritizr package (chance constraints, CVaR), which treats future
   time steps as scenarios to be robust against, not as sequential decisions
   [R5].
3. **Sequential planning today is a manual loop:** update data, lock in what
   is already protected, re-solve with the period's budget. Each step is
   (near) optimal; the sequence has no look-ahead. `eval_rank_importance()`
   already implements the machinery for such a loop (compile once, lock in,
   warm start) [`R/eval_rank_importance.R:449-510`].
4. **Benchmarking CAPTAIN is cheap.** `eval_*` functions score any external
   solution that matches the planning-unit format and NA pattern; we checked
   this with a random raster solution [`R/planning_unit_solution_status.R:368-400`].
   What is missing is a helper to score a ranking at a set of budgets.
5. **Watch the defaults in any benchmark.** Every solver defaults to
   `gap = 0.1`, so out-of-the-box solutions are only guaranteed within 10% of
   optimal. Use `gap = 0` or report the gap.

## 1. Position in the literature

- Exact optimisation over heuristics: Rodrigues et al. 2000; Rodrigues and
  Gaston 2002; Beyer et al. 2016 (linearised Marxan objective; note several
  help pages cite volume "228", the correct volume is 328).
- Evidence on performance: Schuster et al. 2020 (*PeerJ* 8: e9258) found exact
  ILP plans 12-30% cheaper than Marxan and the best solver on average 1,071
  times faster [R8]. The solver benchmark vignette (up to 606,180 planning
  units, 6 h limit) finds Gurobi and CPLEX fastest; SYMPHONY took one to two
  days on large min-shortfall problems with penalties [R9].
- Dynamic and sequential planning, the ground CAPTAIN claims:

| Work | Approach | Relevance |
|---|---|---|
| Costello and Polasky 2004 | Stochastic dynamic programming, heuristics | Static plans can be suboptimal when sites are lost over time |
| Meir et al. 2004 | Simulation of incremental acquisition | Simple sequential rules can rival optimal static plans; so a myopic prioritizr loop is a strong baseline |
| Wilson et al. 2006 | SDP over regions | Classic dynamic allocation, coarse resolution only |
| Alagador et al. 2014 | Time-step ILP-style scheduling with site release | Closest precedent for multi-period ILP |
| Bonneau et al. 2018 | Dynamic min set as an MDP, heuristics | Exact dynamic solution intractable at scale |
| Schuster et al. 2023 | Hierarchical multi-objective with risk layers | Risk as extra objectives, not dynamics |
| Cho and Hanson 2026 (robust.prioritizr) | Chance constraints, CVaR | Robust static plans over climate scenarios |

Full references with DOIs: prioritizr_literature section 1.3. No published
head-to-head of CAPTAIN against prioritizr or any exact solver was found.

## 2. Formulation inventory (9.0.x)

| Component | Available |
|---|---|
| Objectives | min set, min shortfall, min largest shortfall, max cover, max weighted sum (was max utility), max n targets met (was max features), max phylo div / end, min penalties |
| Multi-objective (9.0.0) | `multi_problem()` with hierarchical, reference-point and weighted-sum approaches; epsilon-constraint in moec.prioritizr |
| Targets | absolute, relative, manual, plus `add_auto_targets()` / `add_group_targets()` with about 19 `spec_*` methods (Rodrigues, Jung, Red List based, interpolated, and others) |
| Constraints | locked in / out / manual, bounded, linear, contiguity, feature contiguity, neighbour, mandatory allocation, cost |
| Penalties | boundary (two formulations), connectivity, asymmetric connectivity, linear, neighbour, cost; Cohon calibration |
| Decisions | binary, proportion, semicontinuous; zones |
| Portfolios | cuts, shuffle (any solver); extra, top, gap (Gurobi only) |
| Importance | replacement cost, Ferrier, rarity-weighted richness, rank (Jung et al. 2021) |
| Solvers | Gurobi, CPLEX, CBC, HiGHS, lpsymphony, Rsymphony; SCIP in dev only; no lp_solve |

Sources: prioritizr_literature section 2; prioritizr_code section 2.7.

## 3. Architecture (code)

- `ConservationProblem` is an R6 object; each `add_*` deep-clones it and fills
  a slot (objective, decisions, targets, solver, portfolio) or appends to the
  constraints and penalties lists [`R/ConservationProblem-class.R:1070-1122`].
  Components are anonymous R6 subclasses of `ConservationModifier` with
  `calculate()` and `apply()`.
- `compile()` builds a sparse COO MILP in C++ in a fixed order: feature rows,
  decisions, objective, zone rows, locked bounds, penalties, other constraints
  [`R/compile.R:52-349`]. Boundary penalties are linearised with auxiliary AND
  variables [`src/rcpp_apply_boundary_penalties.cpp:142-215`].
- Solvers share mutators (`set_variable_lb/ub`, `set_constraint_rhs`,
  `set_start_solution`) that let a loop change a compiled model in place
  [`R/Solver-class.R:54-114`]. Warm starts work with Gurobi, HiGHS and CBC, so
  a CAPTAIN solution could be used as a MIP start.
- `write_problem()` exports LP/MPS for benchmarks outside R.

Health: GPL-3 (DESCRIPTION only, no licence file GitHub detects); 44k lines
of R (about half roxygen) and 5k of C++; 1,206 `test_that` blocks; CI on four
OSes plus revdep and coverage, but Gurobi and CPLEX are excluded from CI; 848
commits since 2017, Jeffrey Hanson wrote most of them (low bus factor); 16
open issues. The 9.0.0 release changed the API (objective renames, removed
cost tie-breakers), and 9.0.1 dropped raster/sp. Full mathematical
formulations are still undocumented (issue #148).

Minor bugs found, both verified in the source:

- `R/optimization_problem.R:125` asserts
  `length(x$rhs) >= length(x$number_of_features)`; the right side is always 1,
  probably meant `x$number_of_features`.
- `src/optimization_problem.h:17-24` reserves `_rhs` with `ncol` and
  `_lb`/`_ub` with `nrow` (swapped). Harmless, `reserve()` only.

## 4. Extension points relevant to CAPTAIN

From least to most invasive (prioritizr_code section 4):

1. **Ranking evaluation helper.** Threshold a ranking at given budgets and
   call `eval_*_summary()` on each prefix; compare with
   `eval_rank_importance()`. Small.
2. **Rolling-horizon workflow helper.** Compile once, loop over periods using
   solver mutators, carry lock-ins forward, let a user callback update costs
   or features (feature changes need a recompile). Template:
   `R/eval_rank_importance.R:364-520`. Moderate.
3. **Deterministic multi-period MILP.** Time-indexed decisions with
   `x[j, t] >= x[j, t - 1]`, per-period budgets, time-indexed features.
   `multi_compile()` stacks models over shared planning units, a partial
   precedent; zones are mutually exclusive and do not fit directly. Model size
   grows by a factor of T. Larger.
4. **Stochastic or scenario-tree formulations.** Belong in robust.prioritizr
   style extensions rather than core.

Issue tracker: no requests for dynamic, multi-period, adaptive or
reinforcement-learning features. CAPTAIN appears only in issue #410, listed as
an out-of-scope non-R tool for the extensions vignette.

## 5. Hands-on run

prioritizr 9.0.1.1 (reviewed commit) installed into a scratch library; the
system copy is 8.1.0 and should be upgraded before the comparison. Simulated
data: 90 planning units, 5 features, min set, 10% relative targets. Scripts:
[`analyses/review-runs/`](../../analyses/review-runs/).

| Solver | gap 0.1 runtime | gap 0 runtime | Objective at gap 0 |
|---|---|---|---|
| Gurobi | 0.03 s | 2.9-4.7 s | 1978.91 |
| HiGHS | 0.17 s | 4.6-5.4 s | 1978.91 |
| CBC | 0.56 s | 0.7-1.0 s | 1978.91 |
| Rsymphony | not run | 115 s | 1978.91 |

Single runs, not a benchmark. At gap 0.1, CBC returned 2184.79, 10.4% above
the optimum, which shows why the default gap matters. A random 10-unit raster
solution passed straight into `eval_cost_summary()`,
`eval_target_coverage_summary()` (1 of 5 targets met),
`eval_boundary_summary()` and `eval_ferrier_importance()` without conversion.

## 6. Strengths and gaps, side by side with CAPTAIN

| | prioritizr | CAPTAIN |
|---|---|---|
| Guarantee | Optimal or within a reported gap, for the stated problem | None; quality judged empirically |
| Time | Static snapshot; manual rolling-horizon loop | Sequential by design |
| Dynamics | None; future layers only as extra features | Simulated populations, disturbance, climate |
| Objectives | Linear or linearisable; rich target, constraint and penalty vocabulary | Any computable reward; few hard constraints |
| Budget | Monetary, hard constraint | Cell count; cost as reward penalty |
| Planning units | Raster, vector, tabular | Regular raster only |
| Reproducibility | Deterministic given solver | Approximate (same seed diverges) |
| Uncertainty | robust.prioritizr (static robust) | Simulator-based; risk-sensitive PPO variant in preprint |
| Licence | GPL-3 | CC BY-NC-ND 4.0 |
| Maturity | Since 2016, about 16k CRAN downloads a year, 155 citations of the main paper (OpenAlex) | v3 is a Nov 2026 release candidate |

Caveat against overstating prioritizr's gap: a deterministic multi-period ILP
for known future trajectories is fully expressible in MILP today. What is
missing is a convenience layer, not a capability. True stochastic dynamic
optimisation is intractable at planning-unit scale, which is why CAPTAIN uses
RL, and RL gives no guarantee either.

## 7. Open questions

1. Can CAPTAIN's per-step objective be written as a prioritizr problem, so a
   `gap = 0` rolling-horizon loop serves as the baseline policy? (For the
   static case the CAPTAIN code review shows it can.)
2. Is a sequential workflow helper or a ranking evaluation helper worth adding
   to prioritizr or an extension package?
3. Does warm-starting an exact solve from a CAPTAIN solution speed it up?
4. How does `eval_rank_importance()` order compare with CAPTAIN's protection
   order on the same static problem?
5. Does robust.prioritizr already cover the uncertainty part of CAPTAIN's
   pitch, leaving adaptivity as its distinct contribution?
