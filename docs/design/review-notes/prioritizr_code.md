# prioritizr source code review (for the CAPTAIN comparison)

> Detailed working notes from the 2026-11-27 review. The synthesis is
> [`../02_prioritizr_review.md`](../02_prioritizr_review.md).

Reviewed: <https://github.com/prioritizr/prioritizr> at commit
`1461139cdca5b8f8808682d71f649578452c50db` (2026-10-23, "Add scip solver and
minor bug fixes", PR #413), branch `main`, package version 9.0.1.1.
All file:line references below are relative to the repo root at that commit.
GitHub data (issues, PRs, releases) retrieved with `gh` on 2026-11-27.

Scope: source code only. Papers and docs are covered elsewhere.

---

## 1. Repo health

| Item | Value | Source |
|---|---|---|
| Licence | GPL-3 (GitHub API reports no detected licence file, only the DESCRIPTION field) | `DESCRIPTION:93`; `gh repo view` licenseInfo = null |
| Version | 9.0.1.1 (dev after CRAN 9.0.1) | `DESCRIPTION:3`, `NEWS.md:1,37` |
| R requirement | R >= 4.1.0 | `DESCRIPTION:87-88` |
| Imports | utils, methods, parallel, R6, rlang, cli, sf, units, terra, Matrix, assertthat, magrittr, exactextractr, tibble, withr | `DESCRIPTION:54-69` |
| Suggests (solvers) | gurobi, rcbc, cplexAPI, lpsymphony, Rsymphony, highs, scip (plus slam) | `DESCRIPTION:70-86` |
| Suggests (other) | testthat, knitr, rmarkdown, prioritizrdata, fields, vroom, igraph, ape | `DESCRIPTION:70-86` |
| LinkingTo | Rcpp, RcppArmadillo, BH | `DESCRIPTION:89-92` |
| R source | 202 files, 44,216 lines, of which ~21,350 are roxygen comment lines | `wc` on `R/*.R` |
| C++ source | 5,043 lines across `src/*.cpp`, `src/*.h` (about 40 `rcpp_*` files) | `wc` on `src/` |
| Exports | 183 `export()` entries | `NAMESPACE` |
| Man pages | 162 | `man/` |
| Tests | 171 files, 46,622 lines, 1,206 `test_that()` blocks (testthat 3e) | `tests/testthat/`, `DESCRIPTION:304` |
| Commits | 848; first 2017-02-05, last 2026-10-23 | `git log` |
| Activity by year | 2017:166, 2018:217, 2019:86, 2020:184, 2021:112, 2022:25, 2023:21, 2024:13, 2025:15, 2026:9 | `git log` |
| Contributors | ~15 author identities; Jeffrey Hanson dominates (~700 commits across 4 identities), then Richard Schuster (~80 across 4 identities), Nina Morrell (~35), Matt Strimas-Mackey (21), Jason Everett (1) | `git shortlog -sn HEAD` |
| Stars/forks | 139 / 30 | `gh repo view` |
| Releases (GitHub) | 9.0.1 (2026-09-24), 8.1.0 (2025-11-10), 8.0.4 (2024-06), 8.0.3, 8.0.2, 7.2.2, 7.1.1, 7.0.1, 3.0.4 | `gh release list` |
| Open issues / PRs | 16 open issues; 1 open PR (#419, `add_separation_constraints()`) | `gh issue list`, `gh pr list` |
| Discussions | Disabled | `gh repo view` hasDiscussionsEnabled=false |

Interpretation: commit counts have dropped since 2021 but commits are now large
squash-merged PRs (for example the 2026-06-06 multi-objective PR #401), so
commit count understates activity. 2026 saw a major release (9.0.0: multi-
objective optimization) and a CRAN release (9.0.1). Bus factor is low: one
author writes most of the code.

### CI and coverage

- Workflows in `.github/workflows/`: `R-CMD-check-ubuntu.yaml`, `-macos`,
  `-windows`, `-fedora`, `-revdep`, `documentation.yaml`,
  `test-coverage.yaml`.
- Coverage via covr and Codecov (`.github/workflows/test-coverage.yaml:34-42`),
  thresholds in `codecov.yml` (project and patch threshold 20%, patch
  informational). Badge in `README.Rmd:19`.
- Commercial solvers are not installed in CI (`gurobi=?ignore`,
  `cplexAPI=?ignore` in `.github/workflows/R-CMD-check-ubuntu.yaml:72-73`;
  `gurobi=?ignore` in `test-coverage.yaml`). So Gurobi and CPLEX code paths are
  only tested locally by maintainers (unverified how often).
- Tests skip heavily: 375 `skip_on_cran`, 259 `skip_if_not_installed`, 221
  `skip_if_no_fast_solvers_installed` calls across `tests/testthat/`.

---

## 2. Architecture

### 2.1 Object model: R6, copy-on-modify, pipe composition

- `ConservationProblem` is an R6 class (`R/ConservationProblem-class.R:28`).
  Fields: `data` list (planning units, costs, `rij_matrix`, etc.), `defaults`
  flags, and one slot each for `objective`, `decisions`, `targets`, `weights`,
  `portfolio`, `solver`, plus lists `constraints` and `penalties`
  (`R/ConservationProblem-class.R:32-77`).
- Every `add_*` call goes through a method such as `add_objective()`
  (`R/ConservationProblem-class.R:1070-1083`) that does
  `self$clone(deep = TRUE)`, replaces the slot (warning on overwrite) and
  returns the clone. Constraints and penalties are appended
  (`R/ConservationProblem-class.R:1102-1122`). So the user-facing API is
  functional and pipeable even though objects are R6.
- All components inherit from `ConservationModifier`
  (`R/ConservationModifier-class.R:21-115`), which provides `data`, `internal`,
  `calculate(x, y)` (precomputation hook, line 67) and a
  `compressed_formulation` flag (line 36). Thin abstract subclasses
  `Objective` (`R/Objective-class.R:19-51`, adds `has_targets`, `has_weights`,
  abstract `apply()`), `Constraint`, `Penalty`, `Decision`, `Portfolio`,
  `Target`, `Weight`, `Solver`.
- Concrete components are anonymous R6 subclasses defined inline in each
  `add_*` function. Example: `add_min_set_objective()` defines
  `"MinimumSetObjective"` inside the call and its `apply()` calls
  `rcpp_apply_min_set_objective()` (`R/add_min_set_objective.R:101-130`).
- Input type dispatch uses S4 generics on R6/S3 classes registered with
  `setOldClass`, for example `problem()` has methods for
  (SpatRaster, SpatRaster), (data.frame, character), (numeric, data.frame),
  (matrix, data.frame), (sf, SpatRaster), (sf, character), and zone variants
  (`R/problem.R:499-1174`). `raster`/`sp` classes were deprecated in 9.0.1
  (`NEWS.md:43-49`).

### 2.2 Compile step: ConservationProblem to matrix model

`compile()` / `internal_compile()` (`R/compile.R:52-349`) builds an
`OptimizationProblem` in a fixed order:

1. Sanity checks: objective required (`:76-87`), targets required if the
   objective needs them (`:90-103`), warnings for unused targets or weights
   (`:105-131`).
2. Decide compressed versus expanded formulation (`:165-173`): expanded is
   used only if a constraint requires it (each modifier declares
   `compressed_formulation`). Expanded formulation adds y_ijz variables per
   feature, PU and zone (`src/rcpp_add_rij_data.cpp:52-74`) and is
   incompatible with negative feature values (`R/compile.R:175-226`).
3. Targets table (feature, zone, sense, value) or "fake" targets for
   objectives that do not use targets (`R/compile.R:228-257`).
4. `rcpp_add_rij_data()` writes the feature-by-PU rows of A
   (`R/compile.R:287-289`; `src/rcpp_add_rij_data.cpp:6-51`).
5. Decisions (`R/compile.R:291-292`): set vtype/lb/ub for every PU-zone
   column (`src/rcpp_apply_decisions.cpp:5-23`). Binary "B", proportion "C"
   in [0,1], semicontinuous "S"/"C" in [0, upper_limit]
   (`R/add_binary_decisions.R:79`, `R/add_proportion_decisions.R:67`,
   `R/add_semicontinuous_decisions.R:76`).
6. Objective `apply()` (`R/compile.R:294-295`). For min set: costs into
   `obj`, NA costs fix the column to 0, target rows get sense and rhs, model
   sense "min" (`src/rcpp_apply_min_set_objective.cpp:5-46`).
7. Zone allocation constraints (sum over zones <= 1, or = 1 with
   mandatory allocation) (`R/compile.R:297-312`).
8. `calculate()` for all constraints, then locked constraints first so that
   penalties can use locked values, then penalties, then remaining
   constraints (`R/compile.R:314-348`).

Locked constraints are pure bound changes (`src/rcpp_apply_locked_constraints.cpp:16,22`
sets `_lb[idx]` / `_ub[idx]`). Linear constraints append one row
(`src/rcpp_add_linear_constraints.cpp:9-25`). Boundary penalties linearise
the quadratic x_i x_j term with auxiliary continuous variables b_ij
(col id "b") and AND constraints b <= x_i, b <= x_j, and only when the sign
requires it b >= x_i + x_j - 1 (`src/rcpp_apply_boundary_penalties.cpp:142-215`);
there is an alternative "knapsack" formulation
(`R/add_boundary_penalties.R:494-514`, `src/rcpp_apply_boundary_penalties2.cpp`).

### 2.3 Rcpp layer

- C++ class `OPTIMIZATIONPROBLEM` (`src/optimization_problem.h:8-107`) is a
  plain COO sparse model: `_A_i`, `_A_j`, `_A_x`, `_obj`, `_lb`, `_ub`,
  `_rhs`, `_sense`, `_vtype`, `_row_ids`, `_col_ids`, `_modelsense`,
  `_obj_id`, plus problem dimensions. Wrapped as an external pointer in the R6
  `OptimizationProblem` (`R/OptimizationProblem-class.R:24-339`), which exposes
  getters (`obj()`, `A()`, `rhs()`, ...) and a few mutators (`set_obj`,
  `set_lb`, `set_ub`, `append_linear_constraints`,
  `remove_last_linear_constraint`, `shuffle_columns`, `copy`;
  `R/OptimizationProblem-class.R:210-310`).
- Each modifier has a matching `rcpp_apply_*` function that pushes rows,
  columns and coefficients. Row ids such as `"spp_target"`, `"budget"`, `"b1"`
  are used later to find rows (for example `R/eval_rank_importance.R:451`).
- Minor code smells spotted: the sized constructor reserves `_rhs` with
  `ncol` and `_lb`/`_ub` with `nrow` (swapped, harmless because only
  `reserve()`) (`src/optimization_problem.h:17-24`); the list-based
  `optimization_problem()` asserts `length(x$rhs) >= length(x$number_of_features)`,
  which always compares against 1 (`R/optimization_problem.R:125`), probably
  intended `x$number_of_features`.
- Open issue #408 proposes migrating from Rcpp to cpp11.

### 2.4 Solvers

- Abstract `Solver` (`R/Solver-class.R:19-306`): `calculate()` builds the
  solver-specific model, `run()` solves, `solve()` = calculate + run + clear
  (`:126-135`). It also defines in-place mutators used by portfolios and
  importance functions: `set_variable_ub`, `set_variable_lb`,
  `set_constraint_rhs`, `set_start_solution`, `remove_start_solution`
  (`:54-114`), and multi-objective hooks `default_solve_multiobj`
  (`:163`) and `solve_multiobj` (`:295`).
- Default solver priority: gurobi > cplexAPI > rcbc > highs > lpsymphony >
  Rsymphony > scip (`R/standalone-assertions_solvers.R:54-73`;
  dispatch in `R/add_default_solver.R:56-95`). The roxygen for
  `default_solver_name` omits scip (`R/standalone-assertions_solvers.R:47-49`).
  A no-op `add_compile_solver()` is available for testing via
  `PRIORITIZR_ENABLE_COMPILE_SOLVER=TRUE` (`R/add_compile_solver.R:13-18,41`).
- Warm starts: `start_solution` argument supported by Gurobi, HiGHS and CBC
  (`R/add_gurobi_solver.R:86-93,327-341`, `R/add_highs_solver.R:104-108,222-239`,
  `R/add_cbc_solver.R`). Format is the same as planning-unit data, so any
  externally produced solution (for example a CAPTAIN output) can be used as a
  MIP start.
- Gurobi uses native multi-objective when available
  (`R/add_gurobi_solver.R:423-442`), other solvers fall back to
  `default_solve_multiobj` (hierarchical by repeated solves with added
  constraints).
- `write_problem()` exports LP/MPS via Rsymphony or Gurobi
  (`R/write_problem.R:1-60`), useful for reproducible benchmarks outside R.

### 2.5 Solve, portfolios

- `solve.ConservationProblem()` (`R/solve.R:287-363`): compile, presolve check
  (numerical range checks; `force`/`run_checks` to bypass), then
  `a$portfolio$run(opt, a$solver)` (`:325`), optional duplicate removal, then
  formatting back to the input data type with attributes `objective`,
  `status`, `runtime`, `gap` (`R/solve.R:496-530`).
- Portfolios: shuffle (column order randomisation), cuts (repeatedly adds a
  cut forbidding the previous solution, `R/add_cuts_portfolio.R:119-172` with
  `rcpp_forbid_solution`), and Gurobi-only solution pool portfolios:
  extra, top, gap (`R/add_extra_portfolio.R:103`, `R/add_top_portfolio.R:106`,
  `R/add_gap_portfolio.R:131` check `inherits(solver, "GurobiSolver")`).
  Background in issue #134.

### 2.6 Multi-objective (new in 9.0.0)

- `multi_problem()` bundles several `problem()` objects sharing planning units
  (`R/multi_problem.R:124`); class `MultiConservationProblem`
  (`R/MultiConservationProblem-class.R:25-40`) has an `approach` slot.
- Approaches: hierarchical/lexicographic `add_hier_approach()`
  (`R/add_hier_approach.R:363`), weighted sum `add_wtd_sum_approach()`
  (`R/add_wtd_sum_approach.R:218`), reference point `add_ref_point_approach()`
  (`R/add_ref_point_approach.R:226`).
- `multi_compile()` stacks the individual models into one with an objective
  matrix (`R/multi_compile.R:58-90`; `src/rcpp_compile_multi_obj_problem.cpp`,
  261 lines).
- `NEWS.md:103-150`: new cost penalties/constraints for exploring trade-offs;
  `budget = NULL` allowed for use within multi-problems (`NEWS.md:57-65`);
  function renames (`add_max_utility_objective` to `add_max_wtd_sum_objective`,
  `add_max_features_objective` to `add_max_n_targets_met_objective`) with
  deprecation shims (`R/deprecated.R:245,261`).

### 2.7 Catalogue of formulation components (from `DESCRIPTION` Collate and `R/`)

- Objectives: min set, min shortfall, min largest shortfall, max cover,
  max n targets met, max weighted sum, max phylo div, max phylo end,
  min penalties.
- Targets: absolute, relative, manual, group, auto, plus 2026 `spec_*` target
  methods (Rodrigues, Jung, Polak, Ward, Watson, Wilson, Duran, Sreekar,
  RL species/ecosystem, pop size, interp area/absolute, rule, min/max).
- Constraints: locked in/out/manual, bounded, linear, contiguity, feature
  contiguity, neighbor, mandatory allocation, cost constraints.
- Penalties: boundary, connectivity, asym connectivity, linear, neighbor,
  cost.
- Decisions: binary, proportion, semicontinuous. Zones via `zones()`.

### 2.8 Evaluation and importance

Summaries (`R/eval_*_summary.R`): cost, n, boundary, connectivity, asym
connectivity, feature representation, target coverage, objective.
Importance: Ferrier irreplaceability, rare richness, replacement cost, rank
importance.

**Key point for benchmarking CAPTAIN: eval_* functions score arbitrary
solutions, not only prioritizr outputs.** `solution` is any `numeric`,
`matrix`, `data.frame`, `sf` or `SpatRaster` matching the planning-unit format
(`R/eval_cost_summary.R:14-17`; generic and type check in
`R/planning_unit_solution_status.R:28-43`). The only structural requirement is
that NA cells match the NA cost cells exactly
(`R/planning_unit_solution_status.R:368-400`). Verified empirically (section 5).

- Pure evaluation (no solver): cost, n, boundary, connectivity,
  feature representation, target coverage, objective summaries, Ferrier,
  rare richness.
- Re-optimising (need a solver; solution only defines the selected set):
  `eval_replacement_importance()` locks the solution in, then frees one PU at
  a time and re-solves (`R/eval_replacement_importance.R:240-331`);
  `eval_rank_importance()` (below).
- `eval_objective_summary()` evaluates the problem's objective (optionally
  with penalties) on the given solution (`R/eval_objective_summary.R:81-113`),
  which gives a like-for-like objective value for a CAPTAIN solution.

---

## 3. Time, dynamics, sequential planning, uncertainty

### 3.1 In the code

No temporal, multi-period, stochastic or dynamic formulation exists.
A case-insensitive grep of `R/` and `vignettes/` for multi-period,
multi-stage, time step, temporal, sequential, dynamic, uncertain, stochastic,
scenario, future, climate returns only documentation prose and citations
(for example "uncertain future" in the citation at `R/add_hier_approach.R:244`)
and nothing in the formulation code. The model is single-shot and static:
one A matrix, one decision vector, no time index on any variable.

Closest existing mechanisms:

1. **`eval_rank_importance()` is an incremental, nested, budget-ramped
   sequence of solves.** It compiles once, restricts variables to the given
   solution, then for each budget step sets the budget rhs, **locks in
   previous selections via lower bounds**, warm-starts from the previous
   solution and re-solves (`R/eval_rank_importance.R:449-510`, lock-in at
   `:479-482`, warm start at `:484-486`). This is structurally the greedy
   "acquire a bit more each step, never un-acquire" loop that CAPTAIN's
   sequential protection-per-step resembles, but with exact optimisation at
   each step, static data, and no state transitions (no species dynamics,
   no habitat loss between steps). Design background: issue #337 (Jung et al.
   nested budgets; Martin Jung comment on proportion decisions across steps).
2. **Locked-in constraints from prior solutions**: `add_locked_in_constraints()`
   accepts numeric, logical, matrix, character (column), sf and SpatRaster
   (`R/add_locked_in_constraints.R:183-384`), so a user can manually iterate
   (solve, update data, lock in, re-solve). This is the standard "rolling
   horizon by hand" pattern and is how a CAPTAIN-like dynamic workflow would
   be emulated today.
3. **Hierarchical multi-objective** (`add_hier_approach()`) is used for
   robustness under uncertainty in Schuster et al. 2023 (cited at
   `R/add_hier_approach.R:244`, discussed by maintainers in issue #315).
4. **Solver mutators** (`set_variable_lb/ub`, `set_constraint_rhs`,
   `set_start_solution`; `R/Solver-class.R:54-114`) let a loop modify a
   compiled model in place without recompiling, the building block for any
   sequential feature.
5. Uncertainty is delegated to an external package: `robust.prioritizr`
   (Frankie Cho) listed in the new Software extensions vignette
   (`vignettes/software_extensions.Rmd:29`).

### 3.2 In issues and branches

- `gh search issues` for "multi-period", "time step", "reinforcement",
  "adaptive", "budget over time", "stochastic": no hits.
- "dynamic"/"temporal": only incidental (#148 formulations doc, #139 FAQ, #26
  importance).
- "CAPTAIN": only issue #410 (Software extensions vignette), where Jeffrey
  Hanson lists "Captain" among non-R conservation planning tools explicitly
  out of scope for that vignette (issue #410 body).
- "uncertainty"/"robust"/"climate": #377 (target setting), #134 (solution
  pools), #315 (risk layers: maintainers recommend linear penalties, locked
  out, feature updating, linear constraints, or hierarchical optimisation),
  #275 (BLM sensitivity), #236 (3D marine).
- Remote branches (33) contain nothing temporal: they are about
  multi-objective (`multi-obj`, `new-multiobj_hierarchical-v2`, ...),
  targets, solvers, speed-ups (`speedup-blm`, `fast-rij`), `shiny`.
- Open issues (16) include #414 replication criteria (PR #419 separation
  constraints), #408 cpp11 migration, #375 low-cost commercial solver poll,
  #16 ROI support. None concern dynamics.

Conclusion: dynamic or sequential planning has never been a tracked feature
request in prioritizr's issue tracker. Any CAPTAIN-motivated feature would be
new ground.

---

## 4. Extension points

### 4.1 Adding an objective, constraint or penalty

Pattern (well established, roughly 100-300 lines R plus one C++ file):

1. Write `add_foo()` that validates input and calls
   `x$add_constraint(R6::R6Class("FooConstraint", inherit = Constraint, public = list(name=..., data=..., calculate=..., apply=function(x, y) rcpp_apply_foo(x$ptr, ...)))$new())`
   (template: `R/add_min_set_objective.R:101-130`).
2. Implement `rcpp_apply_foo()` that appends rows/cols to the
   `OPTIMIZATIONPROBLEM` vectors (template: `src/rcpp_add_linear_constraints.cpp`).
3. Register in `DESCRIPTION` Collate, add roxygen, tests, `NEWS.md`.
Base classes and `optimization_problem()`/`OptimizationProblem` are exported
(`NAMESPACE:170-179,310`), so external packages can do this without forking
(robust.prioritizr, MultiscaleSCP, patchwise do so per the extensions
vignette, unverified in their code). Users who do not want C++ can use
`add_linear_constraints()` / `add_linear_penalties()` with arbitrary
per-PU coefficients.

Constraint: everything must be linear (or linearisable) and the variable
space is fixed at PU x zone (+ optional per-feature y and penalty auxiliaries).
Ordering inside compile is hard coded (`R/compile.R:287-348`), so components
that need to see other components' rows rely on that ordering.

### 4.2 Where a "sequential" or "multi-stage" feature could plug in

Options, from least to most invasive:

- **Workflow helper outside compile** (lowest effort): a function like
  `eval_rank_importance()` that compiles once and loops over stages using
  solver mutators, carrying lock-ins forward, and optionally updating
  costs/feature data between stages via a user callback (requires recompiling
  or `set_obj()` for cost changes; feature data changes need new A rows, so
  recompile). This is a rolling-horizon/greedy heuristic, analogous to
  CAPTAIN's step-wise policy but with exact per-step optimisation. Template:
  `R/eval_rank_importance.R:364-520`.
- **Multi-stage deterministic MILP** (moderate to high): stack T copies of the
  PU variables with linking constraints x_{j,t} >= x_{j,t-1} (protection is
  irreversible), per-period budgets, and time-indexed feature data. The
  `multi_compile()` machinery already stacks several models sharing PUs
  (`src/rcpp_compile_multi_obj_problem.cpp`), which is a structural precedent,
  but today it shares one set of PU variables across problems rather than
  indexing by time. The zones mechanism could be abused to represent periods
  (zone = period of protection) with mandatory-allocation-like constraints,
  but zones are mutually exclusive allocations, so "protected in t implies
  protected in t+1" needs new constraints. Model size grows by factor T.
- **Stochastic / scenario-based** (high): two-stage or scenario trees belong
  in robust.prioritizr-like extensions, not core.

### 4.3 Importing an external solution or ranking (e.g. from CAPTAIN)

- Selected-set solutions: directly usable by all `eval_*_summary()`
  functions, `eval_ferrier_importance()`, `eval_rare_richness_importance()`,
  `eval_replacement_importance()` (which uses it as the base set), as a
  `start_solution` for Gurobi/HiGHS/CBC, and as locked-in constraints.
  Requirement: same format and NA pattern as the planning units
  (`R/planning_unit_solution_status.R:368-400`).
- Proportional or fractional outputs: accepted (`numeric` values), so
  partial protection levels can be evaluated.
- Rankings (order of acquisition, as CAPTAIN produces over time steps): no
  direct importer. Options: (a) threshold the ranking at budget levels and
  evaluate each prefix with `eval_*_summary()`, giving a performance curve
  comparable to `eval_rank_importance()` budgets; (b) compare with prioritizr's
  own `eval_rank_importance()` output (nested optimal-per-step ranking).
  A small helper ("evaluate a ranking at budgets") would be a cheap, useful
  interoperability feature.
- Optimality gap of an external solution: compute the optimal objective with
  prioritizr (gap = 0) and compare with `eval_objective_summary()` on the
  CAPTAIN solution. Note CAPTAIN optimises a different, simulated objective
  (species loss under dynamics), so the comparison is only meaningful on a
  shared static metric (cost, targets met, shortfall).

---

## 5. Hands-on run

Environment: WSL2 Linux, 16 cores, R 4.6.1. System has prioritizr 8.1.0;
the reviewed commit (9.0.1.1) was installed into a scratch library
(`R CMD INSTALL -l <scratch>/rlib`, about 2 to 3 minutes). Solvers present:
gurobi, highs, rcbc, Rsymphony, lpsymphony, cplexAPI; scip absent.
Scripts: `analyses/review-runs/prioritizr_example.R`, `prioritizr_solver_gap.R`.

Data: `get_sim_pu_raster()` (90 non-NA PUs) and `get_sim_features()`
(5 features). Problem: min set, 10% relative targets, binary decisions.
Compiled model: 90 columns, 5 rows, 450 non-zeros.

| Solver | gap | Wall (s) | Solver runtime (s) | Objective |
|---|---|---|---|---|
| gurobi | 0.1 | 1.08 | 0.030 | 1987.399 |
| highs | 0.1 | 1.50 | 0.167 | 1980.222 |
| cbc | 0.1 | 1.83 | 0.555 | 2184.792 |
| gurobi | 0 | 3.88 (6.11 first run) | 2.862 (4.687) | 1978.910 |
| highs | 0 | 5.44 (6.95) | 4.560 (5.358) | 1978.910 |
| cbc | 0 | 1.89 (2.01) | 0.695 (1.046) | 1978.910 |
| rsymphony | 0 | 115.87 | 115.022 | 1978.910 |

All exact runs agree (10 PUs selected, objective 1978.910). Note that proving
optimality on this tiny knapsack-like instance takes seconds for Gurobi and
HiGHS and almost two minutes for SYMPHONY, while the default gap 0.1 is
near-instant. Runtimes are single runs, not benchmarks.

Other timings (HiGHS): min set + boundary penalty 0.005 (gap 0): 11.98 s,
objective 1978.937; `eval_replacement_importance()` on the optimal solution:
11.63 s; `eval_rank_importance()` with min shortfall and n = 5 budgets:
6.78 s (budgets 395.8, 791.6, 1187.3, 1583.1, 1978.9).

External solution test: a random selection of 10 PUs (a stand-in for a
CAPTAIN output) was passed as a `SpatRaster` to the eval functions without
any conversion: `eval_cost_summary` 2078 (vs 1979 optimal),
`eval_target_coverage_summary` 1/5 targets met (vs 5/5),
`eval_boundary_summary` 3.45, and `eval_ferrier_importance` returned per-feature
and total layers. Confirms eval_* accept arbitrary solutions.

---

## 6. Code quality

- **Style**: consistent tidyverse-like style, 80-column wrapping, explicit
  `pkg::fun` calls, assertions at the top of every exported function
  (`assert_required()`, `assert()` wrappers around assertthat;
  `R/standalone-assertions_*.R`). No lintr config in the repo.
- **Documentation**: roxygen markdown throughout (about 21k comment lines);
  reusable doc snippets generated by R functions inside roxygen, for example
  `solution_format_documentation()` (`R/planning_unit_solution_status.R:404+`).
  Every exported function has examples gated by `do_run_example()`. Vignettes
  include package overview, connectivity, zones, calibrating trade-offs,
  solver benchmarks, Gurobi installation, software extensions, publication
  record. pkgdown site at prioritizr.net. Issue #148 (open since early years)
  requests full objective function formulations in docs: mathematical
  formulations are still not fully documented per objective.
- **Error messages**: cli-based, structured with `i`/`x` bullets and topic
  links (`R/compile.R:77-131`). Internal invariants use `.internal = TRUE`.
  Presolve checks catch numerical issues before solving (`R/presolve_check.R:184-270`).
- **Tests**: large testthat 3e suite (1,206 blocks), many solver-specific
  and skipped on CRAN; coverage reported to Codecov. Commercial solvers not in
  CI.
- **API stability**: generally careful deprecation (`R/deprecated.R`, using
  `cli_defunct` for removed functions such as
  `predefined_optimization_problem` at `R/deprecated.R:225`). But 9.0.0 made
  breaking changes: two objective renames, removed tie-breaking cost terms
  from several objectives (behaviour change), moved `remove_duplicates` from
  `add_shuffle_portfolio()` to `solve()`, and simulated data CRS changed
  (`NEWS.md:124-150`). 9.0.1 dropped raster/sp support (`NEWS.md:43-49`).
  Expect a moving API across majors.
- **Internals**: R6 objects whose components are anonymous classes created
  inside functions make introspection slightly awkward (class names are
  strings like "MinimumSetObjective"), but the pattern is uniform. The
  deep-clone-on-every-add design is simple and safe; for very large rij
  matrices it may cost memory (unverified; data are stored in `data` list and
  deep cloned).

---

## 7. Implications for the CAPTAIN comparison (code-level)

- prioritizr is a static, single-period, exact MILP framework. Its
  guarantees (optimal or within a stated gap, reported via `attr(, "gap")`)
  are exactly what CAPTAIN lacks; CAPTAIN's dynamic, simulation-in-the-loop
  policy is exactly what prioritizr lacks.
- The cheapest high-value interoperability is evaluation: eval_* already
  scores any external solution, so a CAPTAIN benchmark harness needs only
  data alignment (same PU grid, NA mask) and possibly a ranking-to-budget
  prefix helper.
- A sequential feature has a natural template (`eval_rank_importance()`
  loop + lock-in + warm start) and could be prototyped as a workflow helper
  without touching compile. A true multi-stage MILP is a larger design
  change.
- Warm-starting a MILP with a CAPTAIN solution (`start_solution`) is an
  interesting, zero-code experiment: does a learned heuristic speed up
  exact solves?

## Open questions / unverified

- How often maintainers run Gurobi/CPLEX tests locally (not in CI).
- Whether external extension packages (robust.prioritizr etc.) subclass
  prioritizr R6 classes or only call exported `add_*` functions (not checked).
- Memory cost of deep cloning on large problems (not measured).
- Actual coverage percentage (Codecov dashboard not fetched).
