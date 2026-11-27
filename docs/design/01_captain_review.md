# 01 CAPTAIN review

Status: draft, 2026-11-27. Covers the papers, docs, website and source code of
CAPTAIN (Conservation Area Prioritization Through Artificial INtelligence),
plus a hands-on install and run of v3.0.0rc1.

This is the synthesis. The detailed, fully cited notes it draws on are:

- [`review-notes/captain_literature.md`](review-notes/captain_literature.md):
  papers, preprints, website, docs, reception. Reference keys such as [S22]
  in this document point to that file's References section.
- [`review-notes/captain_code.md`](review-notes/captain_code.md): repositories,
  architecture with `repo:file:line` citations, install log, benchmark, and a
  "Reproduce the run" section.

Companion document: [`02_prioritizr_review.md`](02_prioritizr_review.md).

## Summary

1. **What it is.** A small neural network that scores grid cells from about
   13 per-cell summary features, trained with evolution strategies (a
   gradient-free optimiser) to maximise a reward accumulated while a
   population simulator runs forward in time. The output is a sequence of
   protected cells, which is also a ranking [S22; captain_code section 3].
2. **What is genuinely different from prioritizr.** It plans sequentially
   under changing threats, costs and climate, scores outcomes after simulated
   dynamics (species persistence, extinction-risk class change) rather than
   representation, and can optimise any computable, nonlinear reward
   [S22, Methods; C3-REWARDS].
3. **The published evidence is weaker than the headline.** CAPTAIN has only
   been compared with Marxan and simple heuristics, never with an exact ILP
   solver. The Marxan margin shrank from 96.8% to 64% of simulations between
   preprint and publication once Marxan got a budget, a greedy species/cost
   rule beat CAPTAIN in the one-shot setting (Supplementary Table 3, not
   mentioned in the main text), and the "dynamic" Marxan baseline was never
   re-optimised as data changed [S21-pre; S22; S22-SI].
4. **Our hands-on static test agrees.** On CAPTAIN's own static objective with
   its own toy data, the shipped example's trained plan scored 0.739 (150
   epochs: 0.934), below a 30-line greedy rule (0.990) and an exact MILP
   (0.9999, 25 s with HiGHS). One dataset, one seed, and a static problem,
   which is not CAPTAIN's design target (see "Hands-on run").
5. **Software is now decent, licence is the blocker.** v3 (PyTorch, Nov 2026)
   has 391 passing tests, 82% coverage, CI and good docs. But all versions are
   CC BY-NC-ND 4.0 (non-commercial, no derivatives), development happens in a
   private repo by one developer, and the authors list a company, Captain
   Technologies Ltd, as an affiliation [C3-README; C24].
6. **The untested question that matters.** Does a learned sequential policy
   beat simply re-solving an exact static plan each step with current data
   (a rolling-horizon prioritizr loop), scored in CAPTAIN's own simulator?
   Nobody has run this. It is the natural core of the hands-on comparison.

## 1. Bibliography in one table

| Year | Work | Type | Key point |
|---|---|---|---|
| 2021 | Silvestro et al., bioRxiv 10.1101/2021.04.13.439752 [S21-pre] | Preprint | Claimed 97% wins and 40% less loss vs Marxan |
| 2022 | Silvestro, Goria, Sterner, Antonelli. *Nature Sustainability* 5: 415-424. doi:10.1038/s41893-022-00851-6 [S22] | Main paper | CAPTAIN v1; data, code and Marxan configs on Zenodo 10.5281/zenodo.5643665 |
| 2025 | Silvestro et al. *COSUST* 77: 101587 [S25-COSUST] | Opinion | 30x30 and financial disclosure metrics |
| 2026 | Silvestro et al. *Global Change Biology* 32: e71165 [S26-GCB] | Paper | CAPTAIN v2, restoration, carbon vs extinction risk, Atlantic Forest |
| 2026 | Silvestro et al. *Environmental Research Letters* 21: 181002 [S26-ERL] | Perspective | RL from human feedback for stakeholder priorities; cites prioritizr |
| 2026 | Alejo et al. *Earth's Future* 14: e2025EF007560 [A26] | Independent application | CAPTAIN for Canada's 30x30; validated only against random and existing PAs |
| 2026 | Butikofer et al., bioRxiv [B26] | Preprint | Crop wild relatives under climate change |
| 2026 | Quintero Ossa et al., arXiv:2611.32948 [QO26] | Preprint (3 days old) | Swaps ES for PPO; finds decision granularity, not the optimiser, drives gains. Numbers read from HTML only, recheck against PDF |

No independent critique or benchmark of CAPTAIN was found (Web of Science and
Scopus not searched) [captain_literature section 1.4].

## 2. Method

Plain-language framing for an ILP reader: there is no mathematical program and
no optimality certificate. CAPTAIN searches over the weights of a scoring
function, judging each candidate by running the simulator.

| Element | v1 (2022 paper) | v3 (3.0.0rc1, current) |
|---|---|---|
| Planning units | Blocks of grid cells (5x5 in simulations) [S22] | Raster cells only, regular grid; distances in cell units regardless of CRS [`captain3:captain/utils/grid_utils.py:31-35`] |
| Simulator | Individual-based, stochastic: mortality, dispersal, disturbance, selective disturbance, climate [S22-SI] | Deterministic population matrix; carrying capacity from SDM x (1 - sensitivity x disturbance); future layers linearly interpolated; no randomness, no observation error [`bioenv.py:271-343`, `396-422`] |
| Effect of protection | Disturbance reset and frozen; climate not mitigated [S22] | Disturbance removed entirely in the cell, the only benefit mechanism [`bioenv.py:403`] |
| Policy | Tiny MLP (4+2 or 8 hidden nodes), softmax over units, one unit per step [S22-SI] | Per-cell MLP, 241 weights for 13 features and 16 hidden units; protects top-k cells per step; never sees species identities [`policy_network.py:22-107`, `240-315`] |
| Training | Parallel evolution strategies on many simulated systems, then transfer to real data [S22] | Natural ES on the user's own dataset [`evolution_train.py:65-106`] |
| Budget | Monetary, unit costs from disturbance [S22-SI] | **Number of cells**, cost only as a feature and a reward penalty [`budget_manager.py:10-39`; `rewards.py:70-105`] |
| Objectives | Species loss, value loss, area [S22] | Extinction-risk class change, cost, protected population share with target, worst-served species, species value, layer overlap, connectivity (ECA) [`rewards.py`] |
| Monitoring | Fixed regimes compared (full, citizen science with error, initial only); not learned [S22, Methods] | None |
| Outputs | Selection frequency across replicates [S22] | Protection raster, time of protection per cell, per-decision rank of every cell, KMZ [`inference_recorder.py:35-62`; `export.py:89-189`] |

Two v3 rewards are worth knowing by name, because they are already linear
programs in the static case:

- `CalcRewardProtectedPopulation(target = t)` is a weighted minimum-shortfall
  objective with one relative target for all species [`rewards.py:292-414`].
- `CalcRewardWorstSpecies` is a soft max-min, close in spirit to
  `add_min_largest_shortfall_objective()` [`rewards.py:458-518`].

## 3. Evaluation claims and how fair they are

Headline (S22): CAPTAIN beats Marxan in 64% of 250 simulations (9.2% less
species loss) one-shot and 77.2% (18.5%) staged; on Madagascar trees it meets
all targets in 68% of replicates versus 2% for Marxan.

Points that weaken the claim, each with evidence in captain_literature
section 3.3:

- **Sensitive to baseline setup.** Preprint margins (96.8%, 40%) fell to 64%
  and 9.2% after reviewers had Marxan run with a budget [S21-pre; S22]. Marxan's
  budget is still a soft penalty.
- **Greedy beats CAPTAIN one-shot.** Mean change in species loss vs random:
  greedy -28.4%, CAPTAIN -26.7%, Marxan -21.2% (one-shot); CAPTAIN -26.0%,
  greedy -23.0%, Marxan -13.4% (staged) [S22-SI, Table 3]. The greedy baseline
  is not in the main text. Marxan losing to greedy in both settings points at
  the Marxan formulation, not at static optimisers in general.
- **Objective mismatch.** Marxan minimised cost to hold 10 individuals per
  species; scoring was persistence after 25 simulated steps. A
  budget-constrained min-shortfall or max-coverage formulation is the fair
  static comparator and was not tested.
- **Dynamic baseline was not dynamic.** Marxan was solved once at step 3 and
  its units then added one per step, while CAPTAIN re-observed every step. This
  confounds "learned policy" with "fresh data" [S22-SI].
- **In-distribution testing.** Trained and tested on the same simulator; S26-GCB
  later reports policies do best in the region they were trained on.
- **Small problem.** 100 units and a budget of about 11, trivial for an exact
  solver.
- **Madagascar margin is about one species.** Median species missing target:
  CAPTAIN 0 (range 0-14), Marxan without BLM 1 (range 0-3) [S22-SI, Table 4].
  This is a static problem where an exact solver gives a provable yes/no on
  whether all targets fit the budget. Data are on Zenodo.

Fair credit: the simulation framework lets the authors ask questions static
tools cannot pose (value of recurrent monitoring, effect of detection error,
objective trade-offs over time), the policy learned complementarity without
being told species sensitivities, and the authors published everything needed
to check their work [S22-Z].

## 4. Software

| | v1 `captain-project` | v2 `captain2` | v3 `captain3` |
|---|---|---|---|
| Period | 2021-2023 | 2025 | Mar-Nov 2026 |
| Stack | numpy, numba | Python | PyTorch, GPU optional |
| Tests / CI | none | none | 391 tests, 82% line coverage, ruff + mypy + pytest on 3.11-3.13 |
| Distribution | PyPI `captain-project` 0.1.16 | git | git, tag `v3.0.0rc1` (import name `captain` clashes with an unrelated PyPI package) |
| Contributors | 3 | 1 | 1 (public snapshots of private `captain-ng`) |
| Licence | CC BY-NC-ND 4.0 | CC BY-NC-ND 4.0 (`setup.py` says AGPL, inconsistent) | CC BY-NC-ND 4.0 |

Source: captain_code section 2. The three versions are separate code bases
with separate APIs. Anything the prioritizr team engages with should be v3.

Code quality of v3: readable typed Python, clean extension points (subclass
`CalcReward` for a new reward), efficient, explainability hooks. Weaknesses:
lower-bound-only dependency pins with a lock file that forces CUDA torch on
Linux; only approximately reproducible (same-seed runs diverged from epoch 5
because of per-worker tie-break RNG, and reward calibration uses unseeded
global randomness); the training log keeps the last epoch's weights, not the
best; configuration by editing constants in example scripts; v3 ships no
baselines except "no protection" [captain_code section 7].

**Licence implications** (not legal advice): prioritizr (GPL-3) cannot vendor,
port or ship modified CAPTAIN code. Calling an unmodified, user-installed
CAPTAIN from a wrapper is probably fine but should be checked. Whether NCC or
consultancy use counts as "commercial" is unclear. The README invites
commercial licensing inquiries.

## 5. Hands-on run

Environment: WSL2, 16 cores, no GPU. `uv sync` wanted several GB of CUDA
wheels, so we used a Python 3.12 venv with CPU-only torch 2.10. Commands are in
captain_code section 10; our evaluation script is
[`analyses/review-runs/captain_eval_static.py`](../../analyses/review-runs/captain_eval_static.py).

- Test suite: 391 passed, 1 skipped, about 40 s.
- Synthetic `run_episode.py`: under 1 s.
- Toy dataset (58,315 cells, 30 species): static example about 2.5 min;
  dynamic calibrate, train (20 epochs) and inference about 9 min.

**Static benchmark on CAPTAIN's own objective.** Budget 5,831 cells (10%),
target 10% of each species' population, threat weights, cost penalty. Our
reimplementation of the reward reproduces CAPTAIN's internal value exactly.

| Plan | Reward | Species at 10% target | Time |
|---|---|---|---|
| CAPTAIN, 40 epochs (example default) | 0.739 | 15/30 | 121 s training |
| CAPTAIN, 150 epochs | 0.934 | 21/30 | 385 s training |
| Random cells | 0.885 | 10/30 | 0 s |
| Greedy marginal gain | 0.990 | 30/30 | 1 s |
| Exact MILP (HiGHS, gap 1e-4) | 0.9999 | 24/30, all others at 9.997% or above | 22-28 s |

Caveats: one dataset, one seed, default hyperparameters, and a static problem.
36,449 of 58,315 cells have zero cost, so the problem has many alternative
optima. CAPTAIN's claimed advantage is in the dynamic setting.

**Dynamic toy pipeline.** Over 20 training epochs, almost all improvement came
from moving protection onto cheap cells (cost term -8.88 to -1.96); the
extinction-risk term barely moved (-2.59 to -2.47). The docs' own 100-epoch
study shows the same pattern [`docs/training.md:138-141`]. Final risk classes
at step 50: LC 24, NT 3, EN 1, CR 2 with the plan, versus LC 20, NT 5, VU 1,
EN 2, CR 2 with no protection. We built no non-RL baseline for the dynamic
case yet.

The problem and all four static plans are exported as
`static_toy_problem.npz` so the problem can be rebuilt in prioritizr. It is not
committed: it is derived from CAPTAIN's toy dataset, whose licence we have not
checked, and the script regenerates it.

## 6. Strengths (stated fairly)

1. Explicitly sequential: optimises when as well as where, with protection
   feeding back into future dynamics.
2. Outcome-based objectives, addressing the long-standing critique that
   representation targets are not outcomes.
3. Value-of-information experiments (monitoring regimes, detection error).
4. Any computable reward, no linearisation needed.
5. Fast inference once trained; GPU support; scales to large rasters.
6. Open data for the 2022 study; good v3 docs and tests.
7. An active research programme, including an independent Canadian
   application [A26].

## 7. Limitations

1. No optimality guarantee or gap; the policy class (rank cells by a small
   MLP of aggregate features) may not contain good solutions for
   complementarity-driven problems, as the static benchmark suggests.
2. Results depend on a simulator with many imputed parameters (growth,
   carrying capacity from Red List status, random sensitivities).
3. Hard constraints are soft: budgets in cells, cost and targets via reward
   weights. Locked-out cells and existing PAs are supported; per-feature
   targets, monetary budgets, vector planning units and boundary penalties are
   not.
4. Reward engineering and noisy training; 15 minutes on a toy problem, tens of
   hours on realistic ones [C3-TRAIN; QO26].
5. Licence, single developer, private upstream, commercial entity.

## 8. Ideas relevant to prioritizr

These feed `03_comparison.md` and the recommendation; none are decisions yet.

1. **Benchmark first.** (a) Static: rebuild the v3 toy problem and the
   Madagascar data in prioritizr (min shortfall with budget, `gap = 0`).
   (b) Dynamic: in CAPTAIN's simulator, compare the learned policy, a one-shot
   prioritizr plan, a rolling-horizon prioritizr plan re-solved each step, and
   greedy. Follow Equihua et al. 2024 [E24] in checking RL against known optima.
2. **Sequential planning helper in prioritizr** (rolling horizon, built like
   `eval_rank_importance()`), and possibly a deterministic multi-period MILP
   (Alagador et al. 2014 style).
3. **Stress-test a static plan under dynamics.** Use an external simulator
   (CAPTAIN's, licence permitting, as an unmodified evaluator) to score
   prioritizr solutions over time.
4. **Ranking evaluation helper.** Score a CAPTAIN-style ranking at a set of
   budgets with `eval_*` functions.
5. **Outcome-oriented targets and risk-sensitive objectives** (CVaR in QO26
   parallels robust.prioritizr).

## 9. Open questions

1. Would prioritizr meet all Madagascar targets within budget in every
   replicate, and at what cost?
2. In CAPTAIN's simulator, does a learned policy beat a rolling-horizon exact
   re-solve?
3. How sensitive are CAPTAIN priorities to imputed simulator parameters, seeds
   and ES hyperparameters?
4. Would the authors relicense, or allow a benchmark harness? Does
   "NonCommercial" affect NCC use?
5. Is per-dataset training the intended v3 workflow, or is transfer from
   simulated systems still supported?
6. Do the full texts of A26 (Canada) and B26 compare against any other
   planning tool?
