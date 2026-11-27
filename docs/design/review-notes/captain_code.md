# CAPTAIN source code review (for the prioritizr team)

> Detailed working notes from the 2026-11-27 review. The synthesis is
> [`../01_captain_review.md`](../01_captain_review.md).

Reviewer notes, 2026-11-27. Scope: CAPTAIN's code, installation and a hands-on run.
Papers and the website are covered elsewhere.

Citation conventions: `repo:path:lines` refers to the cloned repositories at the commits
listed below. Anything I did not verify myself is marked **(unverified)**.

| Repo | Commit reviewed | What it is |
|---|---|---|
| `captain-project/captain-project` (v1) | `main` 03e4d2b, `dev` a60fd0e | Code of the 2022 Nature Sustainability paper |
| `captain-project/captain2` (v2) | bc19736 | Code of the 2025 bioRxiv restoration preprint |
| `captain-project/example_data_captain2` | main | Example data and driver scripts for v2 |
| `captain-project/captain3` (v3) | 5a9183f (tag `v3.0.0rc1`) | Current release candidate, a full rewrite |
| `captain-project/notebooks` | main | v1 Jupyter tutorials |

Main conclusion up front: there are three unrelated code bases. v1 (the paper) is a
numpy simulator plus evolution strategies, trained on simulated systems and applied to
empirical Marxan-format data. v3 (Nov 2026) is a clean PyTorch rewrite that trains the
policy directly on the user's raster data. Anything the prioritizr team engages with
should be v3; v1 is useful only to understand the paper.

---

## 1. Finding the code

- The GitHub organisation `captain-project` hosts all repos (`gh repo list captain-project`).
  The v3 `pyproject.toml` lists `Homepage = "https://www.captain-project.net"` and
  `Repository = "https://github.com/captain-project/captain3"`
  (`captain3:pyproject.toml:35-38`).
- v3 README says "Primary development occurs in a private repository; this public
  repository is updated with each release" (`captain3:README.md`, "Notice" section). The
  toy data README names that private repo `captain-ng`
  (`captain3example_data/README.md`, downloaded data).
- Also in the org: `captain-app` (MIT, Electron GUI fork for v1, last push 2022-09-15) and
  the website repo. Not reviewed.

## 2. Repo health

| | v1 `captain-project` | v2 `captain2` | v3 `captain3` |
|---|---|---|---|
| Licence | CC BY-NC-ND 4.0 (`LICENSE.md`) | CC BY-NC-ND 4.0 (`CAPTAIN-License.pdf`, README); but `setup.py:56` classifier says AGPL v3 (inconsistent) | CC BY-NC-ND 4.0 (`pyproject.toml:7`, README "License") |
| Language | Python (numpy, numba), one R script | Python | Python (PyTorch) |
| Size | 7.5k lines of Python on `main` | 16.9k lines | ~4.2k lines package code; ~20k lines incl. tests, docs, examples |
| Commits | 20 on main (2021-12-21 to 2023-12-13), 31 on dev | 22 (2025-05-01 to 2025-09-23) | 40 (2026-03-05 to 2026-11-04) |
| Contributors | D. Edler (9), D. Silvestro (8), K. Dhanjal-Adams (3) | D. Silvestro only | D. Silvestro only (39 + 1 web) |
| Releases / tags | none; PyPI `captain-project` 0.1.16 (uploaded 2022-08-31) | none | tag `v3.0.0rc1`, GitHub pre-release 2026-11-05 |
| PyPI | yes (v1 only) | no | no; install from git. Note PyPI name `captain` belongs to an unrelated package (Jaymon/captain), and v3's import name is also `captain` |
| Stars / forks | 56 / 9 | 7 / 4 | 3 / 2 |
| Issues / PRs | 2 open issues (2022), both user problems with empirical workflow | 1 open PR ("Compilation/load fixes I needed") | none |
| Tests | none | none | 391 unit + integration tests, 1 skipped, 82% line coverage (my run) |
| CI | a cibuildwheel workflow was added then removed (commits 2022-08-31) | none | GitHub Actions: ruff, mypy, pytest on 3.11-3.13 (`.github/workflows/ci.yml`) |
| Docs | README + 4 notebooks in `notebooks` repo | README + example repo | README, CHANGELOG, `docs/` (quickstart, training, inference, architecture), 3 tutorials, 8 example scripts |

Metadata from `gh repo view`, `gh issue list`, `gh pr list`, `gh release list` and
`git log` on 2026-11-27.

Observations:

- **Licence is the single biggest barrier.** CC BY-NC-ND 4.0 forbids distributing
  adapted material and commercial use. CC licences are not designed for software and
  are not OSI-approved. Practically: prioritizr (GPL-3) cannot vendor, port or ship
  modified CAPTAIN code; a prioritizr wrapper that calls an unmodified, user-installed
  CAPTAIN is probably fine but should be checked; any NGO "commercial" use is a grey
  area. README offers "commercial licensing inquiries" (`captain3:README.md`, License).
- Bus factor of one for v2 and v3. Development is in a private repo with public
  snapshots, so public history does not show the real development process.
- Each version is a new repo with a new API; nothing carries over. v1 issues (e.g.
  `captain-project` issue #2) were answered by "use the dev branch".

## 3. Architecture of v3 (`captain3`, the version to engage with)

Package layout (`captain3:README.md`, "Project Structure"; `captain3:docs/architecture.md`):

```text
captain/agents/       policy_network.py, feature_extractor.py, rewards.py, reward_aggregator.py, spatial_cnn.py
captain/algorithms/   episode.py, evolution_train.py, scheduler.py, budget_manager.py, inference_recorder.py, train_utils.py
captain/data/         spatial_data.py, extinction_risk.py
captain/environment/  bioenv.py
captain/utils/        data_loader.py, grid_utils.py, connectivity.py, export.py, plots.py
```

Plain-language summary for an ILP person: CAPTAIN defines a **simulator** (an "environment")
of species populations on a raster. A planning **episode** runs T time steps; at each step
the **policy** (a tiny neural network) gives every cell a score from a handful of per-cell
summary features, the top-k unprotected cells are protected, the simulator advances, and
a **reward** is accumulated. **Training** searches over the network's weights (a few
hundred numbers) to maximise total episode reward with evolution strategies, a
derivative-free method: perturb the weights randomly, run an episode per perturbation,
move the weights towards the perturbations that scored better. The output is a
**sequence** of protected cells (when each cell was protected), i.e. a ranking.

### 3.1 Environment / simulator (`captain/environment/bioenv.py`)

- **Grid and data.** Everything is a raster. `SpatialData` stores only valid (mask) cells
  as a `(channels, n_cells)` tensor and keeps row/col indices as `coords`
  (`captain/data/spatial_data.py:28-110`; `captain/utils/grid_utils.py:102-128`).
  Inputs are GeoTIFF or `.npy` (`captain/utils/data_loader.py:15-56`).
- **Species.** One habitat-suitability layer (SDM output in [0, 1]) per species, plus a
  trait table: growth rate, disturbance sensitivity, conservation status, minimum
  suitability threshold (`docs/quickstart.md` step 3; example data `species_tbl.csv`).
- **Carrying capacity.** `K[s, x] = species_k[s] * SDM[s, x] (0 below threshold) *
  (1 - sensitivity[s] * effective_disturbance[x])`, with
  `effective_disturbance = (1 - protection) * disturbance` (plus an optional edge-effect
  term) (`bioenv.py:396-422`). So **protection removes disturbance entirely in a cell**
  (`bioenv.py:403`); that is the only mechanism by which protection helps.
- **Population dynamics** (`bioenv.py:271-343`), per step: for cells below K, dispersal
  `h <- h @ D^T` with `D[i, j] = exp(-dist/lambda)` for neighbours within a Chebyshev
  window (default 3 cells) and 1 on the diagonal (`grid_utils.py:10-46`); then
  multiplicative growth and clamp to K. For cells above K (e.g. after habitat or
  disturbance change) a nonlinear mortality `h -= d (1 - exp(1 - h/K)) (h - K)`
  (`bioenv.py:321-341`). D is not row-normalised, so "dispersal" adds individuals
  (spread/recolonisation) rather than moving them. Populations start at K
  (`bioenv.py:382-384`). Distances are in cell index units, not metres
  (`grid_utils.py:31-35`), and the toy data is on an EPSG:4326 grid.
- **Climate change / dynamic inputs.** SDMs, disturbance and costs can each have a
  "future" layer; CAPTAIN interpolates linearly per step (`grid_utils.py:208-212`,
  `spatial_data.py:183-197`, `spatial_data.py:437-479`).
- **Stochasticity.** None in the v3 dynamics: `bioenv.py` and `SpatialData` contain no
  random draws. An optional `StochasticSpatialData` (Perlin-noise disturbance events,
  `spatial_data.py:308-371`) is exported but only used in `examples/plot_input_data.py`.
  This is a notable change from v1, which simulated stochastic demography, random
  disturbance and climate (see section 4). With deterministic dynamics, v3 training is an
  optimisation of one fixed scenario, not of a policy that is robust over scenarios.
- **Extinction-risk model** (`captain/data/extinction_risk.py:131-174`): each species'
  IUCN-like class = initial class + bucket(population decline since t0) - bucket(gain in
  protected share of population), clamped to 0..4. Thresholds default to
  `(i/n)^(1/alpha)` (`extinction_risk.py:98-118`). This is a CAPTAIN-specific heuristic,
  not IUCN criteria.
- **Optional extras:** edge effects (`bioenv.py:185-202`, `bioenv.py:424-478`),
  locked-out cells (`action_mask`, `bioenv.py:106-109`, `bioenv.py:510-519`), and
  existing protected areas via an initial protection matrix (advanced tutorial,
  **(unverified in detail)**).

### 3.2 Observations / features (`captain/agents/feature_extractor.py`)

Per-cell features only, computed from the simulated state (`feature_extractor.py:48-71`,
`281-399`): time, mean disturbance, neighbourhood disturbance, species richness, log total
population, five "number of species present in this cell by current risk class" counts,
cost, whether protected, neighbourhood protection; optional edge exposure, buffer
value, connectivity linking value, "worst-served species" value, and arbitrary static
layers. Features are z-scored with statistics from the initial state and clipped to
[-5, 5] (`feature_extractor.py:413-443`).

Important consequence: the network never sees species identities, only per-cell
aggregates. That is what lets a trained model be applied to a dataset with different
species, but it also means the policy cannot reason about complementarity except through
those aggregates (e.g. "worst_species_value") and through re-observing after each batch.

Monitoring / observation error: v3 has no observation-error model (the features are read
directly from the true simulated state). v1 had explicit monitoring modes and observation
error (see section 4).

### 3.3 Action space, budget and cost

- Action = choose `k` cells: the policy scores all cells, protected or locked cells are
  masked to `-inf`, and the top-k (with 1e-7 tie-break noise) are protected
  (`captain/agents/policy_network.py:240-315`). There is no sampling, so the policy is
  deterministic given its weights.
- **Budget is a number of cells, not money.** `GlobalBudgetManager(total_target,
  cells_per_time_step, feature_updates_per_time_step)` caps how many cells are protected
  per step and in total (`captain/algorithms/budget_manager.py:10-39`); the regional
  manager does this per region (`budget_manager.py:42-94`). Features are recomputed
  `feature_updates_per_time_step` times within a step (`algorithms/episode.py:134-177`).
- **Cost enters only as a policy feature and as a reward penalty**
  (`CalcRewardPersistentCost`, `agents/rewards.py:70-105`: `cost . protection`, added
  every time step). A cost budget constraint as in prioritizr's `add_min_shortfall_objective`
  does not exist; you trade cost against benefit through reward weights.
- Protection is binary and permanent; partial protection or other actions (restoration
  was v2's focus) are not in v3's action set **(v2 restoration not reviewed in depth)**.

### 3.4 Rewards / objectives (`captain/agents/rewards.py`, `reward_aggregator.py`)

The total reward is `sum_terms(episode_sum_of_term * weight * calibration * schedule)`
(`reward_aggregator.py:124-134`). Terms:

| Class | What it measures | Lines |
|---|---|---|
| `CalcRewardExtRisk` | change in counts of species per risk class, weighted e.g. `[1, 0, -8, -16, -32]` | `rewards.py:108-205` |
| `CalcRewardPersistentCost` | `-cost . protection` per step | `rewards.py:70-105` |
| `CalcRewardProtectedPopulation` | threat-weighted, range-normalised protected share of each species' initial population, optionally capped at a per-species `target` | `rewards.py:292-414` |
| `CalcRewardWorstSpecies` | mean protected fraction of the worst `q` share of species (soft maximin) | `rewards.py:458-518` |
| `CalcRewardSpeciesValue` | trait-weighted population (e.g. a "value" trait) | `rewards.py:208-277` |
| `CalcRewardLayerOverlap` | protected share of any layer | `rewards.py:521-559` |
| `CalcRewardConnectivity` | gain in Equivalent Connected Area between PA units via least-cost paths | `rewards.py:562-597`, `utils/connectivity.py` |

For a prioritizr developer: `CalcRewardProtectedPopulation(target=t)` with weights is
exactly a **weighted minimum-shortfall objective with relative targets** (`min(held,
t * total) / total`), and `CalcRewardWorstSpecies` is close to a maximin/
`add_max_features_objective` flavour. With `env_dynamics=False` both are linear-with-caps
in the binary decisions, i.e. MILP-representable. I verified this by reproducing CAPTAIN's
reward exactly in my own code (section 6).

Reward scaling is ad hoc: `get_reward_calibrated_weights` runs probe episodes and rescales
each term to unit standard deviation (`algorithms/evolution_train.py:303-350`), and
`advantage_normalization="zscore"` standardises rewards per epoch (`evolution_train.py:32-62`).
Multi-objective trade-offs are therefore set by weights on calibrated scales, which is
harder to interpret than prioritizr's explicit targets plus budget.

### 3.5 Policy network (`captain/agents/policy_network.py`)

- PyTorch. `CellNN` is an MLP applied independently to each cell, with shared weights:
  `features -> Linear -> ReLU (x n hidden layers) -> Linear -> 1 score`
  (`policy_network.py:22-107`). The examples use one hidden layer of 16 or 32 units:
  241 parameters for 13 features and 16 hidden units (my run). This is a very small
  model, essentially a learned nonlinear scoring rule over ~13 features.
- Experimental CNN variant (`SpatialCNN`, `CellCNNPolicy`, `FeatureExtractorCNN`) that
  adds learned spatial-context features (`policy_network.py:110-150`, `agents/spatial_cnn.py`).
- `RegionalPolicyNetwork` selects top-k within each region (`policy_network.py:350-460`).
- Seeded initialisation with Kaiming-uniform weights (`policy_network.py:191-206`).

### 3.6 Training algorithm (`captain/algorithms/evolution_train.py`, `scheduler.py`)

- Natural Evolution Strategies / OpenAI-style ES: noise `eps_i ~ N(0, I)`, evaluate
  `theta + sigma * eps_i`, update `theta += alpha / (n sigma) * sum_i A_i eps_i`
  (`evolution_train.py:65-106`, `393-449`). No gradients, no value function, no replay.
- Defaults: `alpha = 0.2`, `sigma = 0.2`, decays 0.99 per epoch, floors 1e-4 / 0.01;
  sigma adapts to keep the Jaccard similarity between perturbations' plans near 0.8
  (`scheduler.py:21-85`). Examples use 6 perturbations per epoch and 20 to 1000 epochs;
  the docs' convergence study suggests about 40 epochs for the toy global agent
  (`docs/training.md:118-160`).
- Parallelism: `multiprocessing` pool with `forkserver`, one `EpisodeRunner` per worker,
  barrier to ensure each worker has a runner (`evolution_train.py:241-273`, `110-135`);
  on CUDA the examples run sequentially on the GPU.
- Checkpoints save weights, scheduler and RNG state (`evolution_train.py:459-532`).
- The training logger saves the **last** epoch's weights, not the best
  (`algorithms/train_utils.py:143-163`). With noisy ES this matters (section 6).

### 3.7 Applying a model / outputs

- In v3 the "empirical data" is the training environment: `examples/train_policy.py`
  builds `BioEnv` from the user's rasters and trains on it; `examples/run_inference.py`
  rebuilds the same environment, loads `trained_weights.npy`, runs one episode with
  `NoRewards()`, and compares against a no-protection run (`docs/inference.md`,
  `tutorials/toy_example/README.md` section 1). Applying weights trained on one dataset
  to another is technically possible (features are species-agnostic and the feature
  count is fixed), but the docs present same-data training as the workflow.
- Required inputs: area mask; per-species present (and optionally future) suitability
  rasters; disturbance raster(s); cost raster(s); species trait table (status, growth,
  sensitivity, min suitability, optional dispersal); optional regions, existing PAs,
  locked-out cells, connectivity units (`docs/quickstart.md`; `examples/*.py`).
- Outputs: protection raster and protection-through-time raster (step at which each cell
  was protected), extinction-risk summaries, plots, training log TSV, KMZ/KML polygons
  (`captain/utils/export.py:89-189`), and optional per-decision `.npz` files with
  features, scores and a **rank of every eligible cell** (`algorithms/inference_recorder.py:35-62`,
  `docs/inference.md`). So the output is both a selected set and a priority ranking.

### 3.8 Baselines in the code

- v3: only a "no protection" run in `run_inference.py` (`tutorials/toy_example/README.md`
  section 1, step 5). No random, greedy, Marxan, Zonation or ILP baseline.
- v1/v2: a Marxan interface (`captain-project:captain/algorithms/marxan_setup.py:20-104`)
  that writes `puvspr.dat`, `pu.dat`, `spec.dat` (targets = a fixed number of individuals,
  SPF 10, no BLM), shells out to a `./marxan` binary not included in the repo, and reads
  `output_best.csv`. It contains hard-coded personal paths (`marxan_setup.py:113-116` on
  the dev branch). v1 also had random-policy options in `runOptimizedPolicy.py`
  **(not checked in detail)**.

## 4. v1 (paper code) in brief, for context

- numpy/numba; policy in `captain-project:captain/agents/policy.py:7-187`: per-cell
  shared-weight NN (ReLU hidden layer) whose scores go through a softmax to give
  **sampling probabilities** over cells (`policy.py:65-160`), i.e. a stochastic policy.
- ~28 hand-crafted per-cell features including rare / small-range / non-protected species
  counts, population and range changes, cost, budget left, climate
  (`captain/agents/state_monitor.py:460-630`), with min-max scaling (`state_monitor.py:656-671`).
- Reward modes: species loss, species value, protected area, phylogenetic diversity loss
  (`captain/biodivsim/BioDivEnv.py:688-702`).
- Training: ES with `ProcessPoolExecutor`, each worker running a different **simulated**
  system (`captain/algorithms/geneticStrategies.py:80-96`, `331-380`). The trained model
  was then applied to empirical data via a Marxan-format reader (`build_empirical_env`,
  `run_policy_empirical`, `summarize_policy_empirical` returning a per-PU "Priority"
  selection frequency across replicates (`notebooks:Analysis_empirical_data.ipynb`).
- Pinned to 2022-era dependencies (`numpy~=1.21`, `gym~=0.21`, `pyproject.toml`); I did
  not attempt to install v1. v2 pins `numpy==1.23.4` and Python 3.10-3.12
  (`captain2:setup.py:6-48`).

## 5. Install and run (v3)

### 5.1 What I did

Machine: WSL2 Linux x86_64, 16 cores, 15 GB RAM, no GPU, `/tmp` is a 7.6 GB tmpfs.
System Python is 3.14 (too new for the CI matrix 3.11-3.13); `uv 0.13.1` available.

1. `uv sync` (the README route) would pull CUDA torch wheels from PyPI per `uv.lock`
   (`torch 2.10.0`, 102 `nvidia` mentions in `uv.lock`), several GB, which did not fit the
   free tmpfs space. Workaround: a Python 3.12 venv with CPU-only torch 2.10.0 from the
   PyTorch CPU index, then `uv pip install captain3[dev]` from the clone. This bypasses
   the lock file (resolved: numpy 2.5.5, scipy 1.18.1, numba 0.68.1, rasterio 1.5.2).
   Took 17 s with a warm uv cache. Venv size 1.5 GB.
2. `import captain` reports `3.0.0rc1`.
3. Test suite: **391 passed, 1 skipped in 40 s**; with coverage, 82% line coverage
   (lowest: `utils/data_loader.py` 19%, `data/spatial_data.py` 64%, `utils/plots.py` 64%).
4. `examples/run_episode.py` (synthetic 60x60 grid, 20 species, random untrained
   policy): runs in under 1 s; prints reward components and final risk-class counts.
5. Toy dataset (58,315 valid cells, 30 species, 59 MB download) and
   `examples/static_prioritization.py` (one-shot plan, 10% of cells, per-species target
   10%, threat weights, cost penalty; 40 epochs, 6 perturbations, 4 workers).
6. My own evaluation of that static plan against random, greedy and exact MILP plans on
   CAPTAIN's own objective (section 6).
7. The dynamic toy pipeline: `calibrate_rewards.py`, `train_policy.py` (20 epochs, 50
   time steps), `run_inference.py`.

### 5.2 Run outputs

`run_episode.py` (untrained policy, synthetic data):

```text
Grid: 3594 cells, 20 species | Features: 13 | Policy parameters: 241
Total reward: -267.9561 | Protected cells: 500 | Time: 0.09s (183.7 steps/sec)
Reward components: extinction_risk: 2.9500, cost: -270.9061
Final extinction risk: LC 18, NT 2, VU 0, EN 0, CR 0
```

`static_prioritization.py` on the toy data, as shipped (40 epochs, seed 123):

- 121 s training (about 3 s per epoch, 6 episodes per epoch on 4 CPU workers; another
  heavy job was running on the machine), 151 s wall time including loading.
- Console summary: 5,831 cells protected; protected share of each species' population
  min 0.0%, median 8.9%, max 19.8%; 15 of 30 species at or above the 10% target; 0.0% of
  total cost. Writes `protection_plan.png`, `reward_over_training.png`,
  `training_log.tsv`, `trained_weights.npy` (241 float64 weights, 2 KB).
- Training curve is noisy: per-epoch mean perturbation reward ranged 0.42 to 0.93 and
  was not monotone (`training_log.tsv`).

Same script with `N_EPOCHS = 150` (my only change besides `DATA_DIR`): 385 s training;
15 of 30 -> 21 of 30 species at target, min share 5.0%. Mean episode reward by epoch block:
0.74 (epochs 0-24), 0.80, 0.88, 0.87, 0.89, 0.92 (epochs 125-149).

Reproducibility check: the 40- and 150-epoch runs use the same seed, so their first 40
epochs should match. Epochs 0-4 are identical; from epoch 5 they differ in the 4th
decimal and drift (e.g. epoch 10: 0.6200 vs 0.6236). Likely cause: each pool worker has
its own tie-break RNG (`policy_network.py:186-188`, `251`) and `pool.map` does not fix
which worker evaluates which perturbation. Results are approximately, not exactly,
reproducible on CPU with multiple workers.

## 6. Benchmark on CAPTAIN's own static objective (my code)

Because `CalcRewardProtectedPopulation(target)` minus `CalcRewardPersistentCost` with
`env_dynamics=False` is linear-with-caps in the decisions, the static example's objective
is a small MILP. I rebuilt the environment with the example's own
`create_episode_runner()` and computed, for the same budget (5,831 cells = 10% of cells):

`R(x) = sum_s w_s min(h_s . x, 0.1 P_s) / P_s / sum_s (0.1 w_s)  -  c . x / sum(c)`

with `h` the initial population matrix, `P_s` total population, `w_s` the threat weight
of the species' initial class, `c` the cost layer. My `R` reproduces CAPTAIN's internal
episode reward exactly (0.7393 and 0.9342 for the two trained policies), so the
comparison is on CAPTAIN's objective, not mine. Script:
`analyses/review-runs/captain_eval_static.py`. Note: 36,449 of 58,315 cells have zero cost, so the
cost term is easy to drive to 0 and the problem has many alternative optima.

| Plan | Reward R | Population term | Cost share | Species at 10% target (tol 1e-4) | Min species share | Time |
|---|---|---|---|---|---|---|
| CAPTAIN, 40 epochs (example default) | 0.739 | 0.739 | 0.000 | 15/30 | 0.000 | 121 s train |
| CAPTAIN, 150 epochs | 0.934 | 0.935 | 0.0005 | 21/30 | 0.050 | 385 s train |
| Random 5,831 cells | 0.885 | 0.984 | 0.099 | 10/30 | 0.085 | 0 s |
| Greedy marginal gain (100 batches, 30 lines of numpy) | 0.990 | 1.000 | 0.010 | 30/30 | 0.101 | 1 s |
| Exact MILP (HiGHS 1.16, gap 1e-4) | 0.9999 | 1.000 | 0.000 | 24/30 (all >= 0.09997) | 0.09997 | 22-28 s |

Reading this fairly:

- This is one dataset, one seed, the example's default hyperparameters and a static
  problem, which is not what CAPTAIN is designed for. Its claimed advantage is in dynamic,
  sequential decisions under changing climate, disturbance and costs, where an exact
  ILP is not directly available. I did not test that setting against alternatives.
- Still, on a problem that prioritizr would solve exactly in seconds, the shipped
  example's RL plan is worse than a random plan after 40 epochs and still clearly below a
  trivial greedy heuristic and the exact optimum after 150 epochs. ES with 241 weights
  searches a restricted family of scoring rules ("rank cells by an MLP of 13 aggregate
  features"), which may not contain the optimum for target-based complementarity.
- The exported problem (`h`, `cost`, weights, target, cell coordinates, and all four
  plans) is written to `<work dir>/out150/static_toy_problem.npz` (not committed), ready to be rebuilt in
  prioritizr as a cross-check: PU cost 1, `add_min_shortfall_objective(budget = 5831)`,
  `add_relative_targets(0.1)`, `add_feature_weights(w)`, and the cost term as
  `add_linear_penalties()` on `c / sum(c)` (prioritizr's shortfall is normalised by the
  target rather than by total amount, so the weights need rescaling to match `R` exactly).

### 6.1 Dynamic toy pipeline (the intended use case)

`calibrate_rewards.py` -> `train_policy.py` -> `run_inference.py` on the toy data as
shipped (50 time steps, 1,000 cells per step, 5,831 cells total, rewards = extinction
risk + cost, 20 epochs, 6 perturbations, 4 workers, seed 123):

- Calibration: 24 s; multipliers `extinction_risk 2.93`, `cost 0.57`
  (`reward_calibration.json`).
- Training: 452 s (about 20 s per epoch). Uncalibrated term totals per episode, epoch 0 ->
  9 -> 19: extinction risk -2.59 -> -2.51 -> -2.47; cost -8.88 -> -2.19 -> -1.96. So
  almost all of the 20-epoch improvement came from moving protection onto cheap cells;
  the biodiversity term barely moved. The docs' 100-epoch study shows the same pattern
  (extinction risk -1.04 -> -0.87, cost -9.67 -> -0.55; `docs/training.md:138-141`).
- Inference: 33 s. Final (step 50) risk classes with the trained plan: LC 24, NT 3, VU 0,
  EN 1, CR 2; with no protection: LC 20, NT 5, VU 1, EN 2, CR 2
  (`inference/Extinction_risk_future*.png`). Protection is placed in the first 6 steps
  (1,000 cells per step), as a protection-through-time map; KMZ export reported "New
  protection: 5831 cells in 197 polygons". Outputs (13 MB): protection maps, per-feature
  maps, XAI `.npz` files with features, scores and ranks per decision, score maps.
- I did not build a non-RL baseline for the dynamic case (e.g. protect prioritizr's or a
  greedy static plan in the same 6 steps and score it with CAPTAIN's simulator). That is
  the natural next experiment (section 9).

## 7. Code quality assessment (v3)

Strengths:

- Readable, modern, typed Python with docstrings on nearly every public class and
  function; consistent `(features|species, cells)` tensor layout; ruff + mypy in CI.
- Clear extension points: subclass `CalcReward` for a new reward, add features via
  `feature_set` or `static_features`, swap the `nn.Module` policy
  (`docs/architecture.md`, "Extension Points"). A target-based reward already exists
  (`CalcRewardProtectedPopulation(target=...)`).
- Real test suite (391 tests, 82% coverage) and CI on 3 Python versions; CHANGELOG with
  breaking changes called out; PEP 440 versioning; stated API stability for 3.0.
- Efficient: sparse dispersal matrices, GPU support, per-step costs small; a 58k-cell
  static episode takes well under a second.
- Explainability hooks (`InferenceRecorder`) and KMZ export are thoughtful touches for users.

Weaknesses / risks:

- Licence (CC BY-NC-ND) and single-developer, private-upstream model (section 2).
- Dependencies are lower-bound only in `pyproject.toml` (`numpy>=2.0.0`, `torch>=2.2.0`,
  ...); reproducibility depends on `uv.lock`, which forces CUDA torch on Linux x86_64.
- Reproducibility: trainer and policy are seeded (`evolution_train.py:229`,
  `policy_network.py:186-189`) and the dynamics are deterministic, but reward calibration
  draws probe weights from the global, unseeded `np.random`
  (`evolution_train.py:315-320`), and `run_inference.py` defaults to `SEED = None`.
- Training is noisy and the logger keeps the last epoch's weights rather than the best
  (`train_utils.py:163`); there is no early stopping or validation on held-out scenarios.
- Configuration is by editing module-level constants in example scripts (no CLI or config
  file in v3; v2 used config files). Example scripts write outputs into the data folder.
- Raster-only, regular grid; distances in cell units regardless of CRS (cells of unequal
  area in EPSG:4326 are treated equally).
- Many modelling constants are heuristics without documented empirical grounding
  (extinction-risk buckets, dispersal kernel, protection fully removing disturbance).

Extensibility questions from the brief:

- Different reward, e.g. targets: yes, already present (`CalcRewardProtectedPopulation`
  with `target`, `CalcRewardWorstSpecies`), and new `CalcReward` subclasses are easy.
- Different simulator: `BioEnv` is a concrete class without an abstract interface; the
  episode runner, features and rewards read many `BioEnv` attributes directly, so a new
  simulator would have to mimic that surface (duck typing). Feasible but not designed for.
- Static data: yes, `EpisodeRunner(env_dynamics=False)` (`algorithms/episode.py:75-79`)
  plus `n_steps=1` gives one-shot prioritisation (`examples/static_prioritization.py`).

## 8. Interoperability with prioritizr

What maps directly:

- Planning units: CAPTAIN v3 PUs are raster cells. A prioritizr raster problem (terra
  `SpatRaster` PUs and features) maps one-to-one: cost raster -> `costs`; feature
  rasters (probabilities/abundances) -> `sdms` (values must be in [0, 1], species-level
  `species_k` scales them); `locked_out` -> `action_mask`; `locked_in` -> initial
  `protection_matrix`. The budget manager counts all protected cells
  (`budget_manager.py:28`), so the advanced example adds the number of pre-protected
  cells to the target by hand (`examples/train_policy_advanced.py:216-225`).
- Relative targets -> `CalcRewardProtectedPopulation(target=t)`, but only one scalar
  target for all species (`rewards.py:322`, `355`); per-feature targets would need a
  small subclass. Feature weights -> `threat_weights` indexed by risk class, not per
  feature; per-feature weights would also need a subclass.
- Budget: prioritizr budgets are in cost units; CAPTAIN's are in number of cells. With
  equal costs they coincide; otherwise CAPTAIN can only penalise cost in the reward.
- Boundary penalties / connectivity: no BLM equivalent; `edge_factor` (edge effects) and
  `CalcRewardConnectivity` (ECA between existing PA units) are different constructs.

What does not map:

- Vector / irregular PUs. v3 needs a regular grid (`flatten_grid`, row/col `coords`).
  A table of PUs could in principle be fed as a 1 x N "raster" with
  `env_dynamics=False`, but the neighbourhood features (`disturbance_conv`,
  `protection_matrix_conv`) and dispersal would then be meaningless. v1's
  `build_empirical_env` read Marxan `puvsp`/`pu` tables (`notebooks:Analysis_empirical_data.ipynb`),
  so the v1 API was closer to prioritizr's tabular inputs than v3 is.
- Species traits (growth, sensitivity, status) that CAPTAIN needs are not part of a
  prioritizr problem; a comparison must invent or source them.

Export/import formats: v3 reads GeoTIFF/.npy rasters and a CSV trait table; writes PNG
plots, TSV logs, `.npy` weights, `.npz` decision files with per-cell rank, KMZ/KML. The
protection raster is reconstructable via `SpatialData.to_grid()` /
`reconstruct_grid` (`spatial_data.py:220-283`) and can be written with rasterio, so a
CAPTAIN plan can be read straight into R (`terra::rast`) and evaluated with prioritizr's
`eval_*_summary()` functions. Conversely, a prioritizr solution raster can be loaded as
the initial `protection_matrix` and run through CAPTAIN's simulator with
`NoBudgetManager()` to evaluate it under CAPTAIN's dynamics (the
`run_inference.py` "no protection" baseline shows the pattern). This "evaluate each
tool's plan in the other's metric" design is the cheapest fair benchmark.

## 9. Open questions

- Does CAPTAIN's dynamic, sequential planning beat a static plan (e.g. prioritizr's
  solution protected in cost or rank order over the same time steps) when evaluated in
  CAPTAIN's own simulator? This is the comparison where RL could plausibly add value, and
  it is not in the code base.
- Is there an intended workflow for training on simulated scenarios and transferring (as
  in v1), or is v3 per-dataset training only? The pretrained v3 model is described only
  as "a pre-trained model" (`captain3:README.md`, Examples).
- Licence: would the authors relicense (e.g. GPL/MIT) for interoperability work?
- Is the private `captain-ng` repo the source of truth, and will public issues/PRs be
  accepted?
- How sensitive are results to ES hyperparameters, seeds and number of epochs?
  The docs' convergence study used 3 seeds (`docs/training.md:118-160`); my static run
  suggests large epoch-to-epoch variance.

## 10. Reproduce the run

All paths below are under `S`, a scratch working directory outside the repo.
The evaluation script lives in this repo at `analyses/review-runs/captain_eval_static.py`;
copy it to `$S/work/eval_static.py` before step 7.
Requires `uv` (I used 0.13.1), git, curl, unzip. About 1.5 GB for the venv, 60 MB data.

```bash
S=/path/to/scratch
mkdir -p $S/src $S/work $S/data/toy $S/notes

# 1. Source (v3 at tag v3.0.0rc1 = commit 5a9183f)

git clone https://github.com/captain-project/captain3.git $S/src/captain3
git -C $S/src/captain3 checkout v3.0.0rc1

# 2. Environment: Python 3.12 + CPU-only torch (the README's `uv sync` pulls CUDA wheels,

#    several GB; use it instead if you have the disk space / a GPU)

uv venv --python 3.12 $S/work/venv3
VIRTUAL_ENV=$S/work/venv3 uv pip install --index-url https://download.pytorch.org/whl/cpu "torch==2.10.0"
VIRTUAL_ENV=$S/work/venv3 uv pip install "$S/src/captain3[dev]"
VIRTUAL_ENV=$S/work/venv3 uv pip install highspy          # only for my MILP benchmark
$S/work/venv3/bin/python -c "import captain; print(captain.__version__)"   # 3.0.0rc1

# 3. Tests (391 passed, 1 skipped, ~40 s)

cd $S/work && $S/work/venv3/bin/python -m pytest $S/src/captain3/tests -q -p no:cacheprovider \
  --rootdir=$S/src/captain3 --cov=captain --cov-report=term

# 4. Synthetic example, no download (< 5 s)

$S/work/venv3/bin/python -I $S/src/captain3/examples/run_episode.py

# 5. Toy data (59 MB; link from captain3 docs/quickstart.md)

curl -sL -o $S/data/toy/toy.zip "https://polybox.ethz.ch/index.php/s/qYTHM7difqrBmo4/download"
(cd $S/data/toy && unzip -q toy.zip)        # -> $S/data/toy/captain3example_data

# 6. Static prioritisation example (copy the script, point DATA_DIR at the data; ~2.5 min)

mkdir -p $S/work/run_static
sed 's#^DATA_DIR = .*#DATA_DIR = Path("'$S'/data/toy/captain3example_data")#' \
  $S/src/captain3/examples/static_prioritization.py > $S/work/run_static/static_prioritization.py
(cd $S/work/run_static && $S/work/venv3/bin/python -I static_prioritization.py)

# 6b. Same with 150 epochs (~7 min)

mkdir -p $S/work/run_static150
sed -e 's/^N_EPOCHS = 40/N_EPOCHS = 150/' \
    -e 's/f"static_p{TARGET_PROTECTED_CELLS_FRACTION}_t{PROTECTION_TARGET}"/f"static_p{TARGET_PROTECTED_CELLS_FRACTION}_t{PROTECTION_TARGET}_e150"/' \
    $S/work/run_static/static_prioritization.py > $S/work/run_static150/static_prioritization.py
(cd $S/work/run_static150 && $S/work/venv3/bin/python -I static_prioritization.py)

# 7. Benchmark vs random / greedy / MILP (my script, ~45 s); writes out*/static_toy_problem.npz

$S/work/venv3/bin/python -I $S/work/eval_static.py $S/work/run_static    $S/work/out
$S/work/venv3/bin/python -I $S/work/eval_static.py $S/work/run_static150 $S/work/out150

# 8. Dynamic pipeline (~9 min total)

mkdir -p $S/work/run_dynamic
for f in calibrate_rewards train_policy run_inference; do
  sed 's#^DATA_DIR = .*#DATA_DIR = Path("'$S'/data/toy/captain3example_data")#' \
    $S/src/captain3/examples/$f.py > $S/work/run_dynamic/$f.py; done
cd $S/work/run_dynamic
$S/work/venv3/bin/python -I calibrate_rewards.py   # calibrate_rewards imports train_policy from its own dir
$S/work/venv3/bin/python -I train_policy.py
$S/work/venv3/bin/python -I run_inference.py

# outputs: $S/data/toy/captain3example_data/global_w1.0_w1.0_p0.1/{global_log.tsv,trained_weights.npy,inference/}

```

Notes: example scripts are configured by editing constants at the top of each file (no
CLI). They write results into the data folder. Runtimes were measured while another heavy
job (an R package compile) shared the 16-core CPU. The pretrained v3 model
(`https://polybox.ethz.ch/index.php/s/wZ5AMXPdzboZSm2/download`, 241 weights, trained
1,000 epochs with 17,000 protected cells on the full 258 MB dataset) was downloaded and
inspected but not run, because its matching dataset is the large one.
