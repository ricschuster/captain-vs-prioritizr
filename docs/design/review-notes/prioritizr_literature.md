# prioritizr: literature and documentation review

> Detailed working notes from the 2026-11-27 review. The synthesis is
> [`../02_prioritizr_review.md`](../02_prioritizr_review.md).

Compiled 2026-11-27 for the captain-vs-prioritizr comparison. Scope: published
literature, CRAN metadata, the prioritizr.net website and the help/vignettes
shipped with the package. Source code is reviewed separately.

Evidence conventions:

- `[R n]` points to the numbered references at the end.
- `[local 8.1.0]` means checked in the locally installed prioritizr 8.1.0
  (`/usr/local/lib/R/site-library/prioritizr`, help pages via `tools::Rd_db()`,
  `NEWS.md`, vignettes in `doc/`).
- `[web]` means prioritizr.net, which currently documents the development
  version (9.0.1.x), so it can be ahead of CRAN.
- `UNVERIFIED` marks claims I could not confirm from a primary source.

Version caveat: CRAN is at **9.0.1** (published 2026-09-24) [R1], but the local
install is **8.1.0** (2025-11-10). Several 9.x features (multi-objective
`multi_problem()`, cost penalties/constraints, renamed objectives) are only
described here from release notes and the website [R2, R3]. Any hands-on
comparison should pin a version; I recommend upgrading to 9.0.1 first.

---

## 1. Bibliography

### 1.1 The package itself

| Item | Citation | Verified via |
|---|---|---|
| Main paper | Hanson JO, Schuster R, Strimas-Mackey M, Morrell N, Edwards BPM, Arcese P, Bennett JR, Possingham HP (2025) Systematic conservation prioritization with the prioritizr R package. *Conservation Biology* 39(1): e14376. doi:10.1111/cobi.14376. Online first 2024-09-13, hence both "2024" and "2025" appear in citations (the package's own publication record lists it as 2024). | `citation("prioritizr")` [local 8.1.0]; OpenAlex [R4] |
| Software | prioritizr: Systematic Conservation Prioritization in R. CRAN, doi:10.32614/CRAN.package.prioritizr. GPL-3. | CRAN [R1]; OpenAlex |

What the 2025 paper claims (from the abstract [R4]): flexible problem-building
interface; commercial (Gurobi) and open-source (CBC, SYMPHONY) exact solvers
"identify optimal solutions in a short period"; spatial (Shapefile, GeoTIFF)
and tabular inputs; importance evaluation; a Washington State (USA) avifauna
case study (costs, existing PAs, locked-out areas, fragmentation) identifying
12,400 km2 of priorities; and a solver benchmark concluding that "open source
and commercial solvers were able to quickly solve large-scale conservation
planning problems, [but] commercial solvers were required for complex,
large-scale problems". OpenAlex records 155 citations (queried 2026-11-27;
OpenAlex counts typically undercount relative to Google Scholar).

### 1.2 Methodological foundations

| Topic | Reference | Relevance to the comparison |
|---|---|---|
| ILP for reserve selection, the case for exact methods | Rodrigues ASL, Cerdeira JO, Gaston KJ (2000) Flexibility, efficiency, and accountability: adapting reserve selection algorithms to more complex conservation problems. *Ecography* 23: 565-574. doi:10.1111/j.1600-0587.2000.tb00175.x | Early argument that exact optimization is feasible and accountable. |
| | Rodrigues ASL, Gaston KJ (2002) Optimisation in reserve selection procedures: why not? *Biological Conservation* 107: 123-129. doi:10.1016/S0006-3207(02)00042-3 | Same line of argument, against heuristics. |
| ILP vs simulated annealing (Marxan) | Beyer HL, Dujardin Y, Watts ME, Possingham HP (2016) Solving conservation planning problems with integer linear programming. *Ecological Modelling* 328: 14-22. doi:10.1016/j.ecolmodel.2016.02.005 | Linearization of the Marxan boundary/connectivity objective that prioritizr's penalties build on. Note: prioritizr help pages cite this as volume "228" (e.g. `?add_boundary_penalties`, `?add_connectivity_penalties` [local 8.1.0]); the correct volume is 328 (OpenAlex). Minor doc fix. |
| Exact solvers vs Marxan, benchmark | Schuster R, Hanson JO, Strimas-Mackey M, Bennett JR (2020) Exact integer linear programming solvers outperform simulated annealing for solving conservation planning problems. *PeerJ* 8: e9258. doi:10.7717/peerj.9258 | Key quantitative claim set (section 4). Cited by `?add_default_solver` for solver ranking. |
| Marxan | Ball IR, Possingham HP, Watts M (2009) Marxan and relatives: software for spatial conservation prioritisation. In Moilanen A, Wilson KA, Possingham HP (eds) *Spatial Conservation Prioritisation*. OUP. (book chapter, no DOI checked) | Origin of boundary penalty formulation and the "selection frequency" idea that portfolios emulate. |
| Marxan with Zones | Watts ME et al. (2009) Marxan with Zones. *Environmental Modelling & Software* 24: 1513-1521. doi:10.1016/j.envsoft.2009.06.005 | Conceptual basis of `zones()`. |
| Connectivity (asymmetric) | Beger M et al. (2010) Incorporating asymmetric connectivity into spatial decision making for conservation. *Conservation Letters* 3: 359-368. doi:10.1111/j.1755-263X.2010.00123.x | Basis of `add_asym_connectivity_penalties()` [local 8.1.0]. |
| Contiguity | Önal H, Briers RA (2006) Optimal selection of a connected reserve network. *Operations Research* 54: 379-388 (DOI not checked). | Flow-based contiguity constraints (`add_contiguity_constraints()`, `add_feature_contiguity_constraints()`) [local 8.1.0]. |
| Neighbour penalties | Williams JC, ReVelle CS, Levin SA (2005) Spatial attributes and reserve design models: a review. *Environmental Modeling and Assessment* 10: 163-181 (DOI not checked). | Cited by `add_neighbor_penalties()` [local 8.1.0]. |
| Connectivity (Hanson) | Hanson JO, Fuller RA, Rhodes JR (2019) Conventional methods for enhancing connectivity in conservation planning do not always maintain gene flow. *Journal of Applied Ecology* 56: 913-922. doi:10.1111/1365-2664.13315 | Feature-contiguity motivation. |
| | Hanson JO, Vincent JG, Schuster R, et al. (2022) A comparison of approaches for including connectivity in systematic conservation planning. *Journal of Applied Ecology* 59: 2507-2519. doi:10.1111/1365-2664.14251 | Compares connectivity approaches inside prioritizr. |
| Surrogates / niches (Hanson) | Hanson JO et al. (2017) Environmental and geographic variables are effective surrogates for genetic variation in conservation planning. *PNAS* 114: 12755-12760. doi:10.1073/pnas.1711009114 | |
| | Hanson JO et al. (2020) Global conservation of species' niches. *Nature* 580: 232-234. doi:10.1038/s41586-020-2138-7 | |
| Project prioritization (sister package oppr) | Hanson JO, Schuster R, Strimas-Mackey M, Bennett JR (2019) Optimality in prioritizing conservation projects. *Methods in Ecology and Evolution* 10: 1655-1663. doi:10.1111/2041-210X.13264 | Action/project selection with ILP; closest prioritizr-family tool to "which actions, under budget". |
| Importance: replacement cost | Cabeza M, Moilanen A (2006) Replacement cost: a practical measure of site value for cost-effective reserve planning. *Biological Conservation* 132: 336-342. doi:10.1016/j.biocon.2006.04.025 | `eval_replacement_importance()` |
| Importance: Ferrier | Ferrier S, Pressey RL, Barrett TW (2000) A new predictor of the irreplaceability of areas... *Biological Conservation* 93: 303-325. doi:10.1016/S0006-3207(99)00149-4 | `eval_ferrier_importance()` |
| Importance: rarity-weighted richness | Williams P et al. (1996) *Conservation Biology* 10: 155-174 (cited in `?eval_rare_richness_importance`); see also Albuquerque F, Beier P (2015) *PLoS ONE* 10: e0119905. doi:10.1371/journal.pone.0119905 | `eval_rare_richness_importance()` |
| Importance: incremental rank | Jung M et al. (2021) Areas of global importance for conserving terrestrial biodiversity, carbon and water. *Nature Ecology & Evolution* 5: 1499-1509. doi:10.1038/s41559-021-01528-7 | `eval_rank_importance()` "based on Jung et al. 2021" [local 8.1.0]. Also source of `spec_jung_targets()`. |

Contrast: Moilanen / Zonation (heuristic ranking, the main non-ILP
alternative):

- Moilanen A et al. (2005) Prioritizing multiple-use landscapes for
  conservation: methods for large multi-species planning problems. *Proc R Soc
  B* 272: 1885-1891. doi:10.1098/rspb.2005.3164
- Moilanen A et al. (2022) Novel methods for spatial prioritization with
  applications in conservation, land use planning and ecological impact
  avoidance (Zonation 5). *Methods in Ecology and Evolution* 13: 1062-1072.
  doi:10.1111/2041-210X.13819

Zonation produces a complete priority ranking by iterative removal; prioritizr
produces a solution for a given target/budget. `eval_rank_importance()` is the
prioritizr-native way of producing a nested, ranking-like output (section 3.3).

### 1.3 Dynamic, multi-period, sequential and uncertain planning (literature)

This is the area where CAPTAIN positions itself, so the relevant OR and
conservation literature is listed in more detail.

| Reference | Method | Notes |
|---|---|---|
| Costello C, Polasky S (2004) Dynamic reserve site selection. *Resource and Energy Economics* 26: 157-174. doi:10.1016/j.reseneeco.2003.11.005 | Stochastic dynamic programming (SDP) with heuristics | Sites lost stochastically over time; budget arrives per period. Shows static solutions can be suboptimal. |
| Meir E, Andelman S, Possingham HP (2004) Does conservation planning matter in a dynamic and uncertain world? *Ecology Letters* 7: 615-622. doi:10.1111/j.1461-0248.2004.00624.x | Simulation of incremental acquisition under site loss | Found simple greedy/opportunistic rules can rival optimal static plans when sites are lost during slow implementation. Directly relevant to the CAPTAIN argument. |
| Wilson KA, McBride MF, Bode M, Possingham HP (2006) Prioritizing global conservation efforts. *Nature* 440: 337-340. doi:10.1038/nature04366 | SDP over regions, return-on-investment | Classic dynamic allocation; tractable only at coarse resolution. |
| Visconti P, Pressey RL, Segan DB, Wintle BA (2010) Conservation planning with dynamic threats. *Biological Conservation* 143: 756-767. doi:10.1016/j.biocon.2009.12.018 | Simulation of scheduling rules under dynamic threats | |
| Alagador D, Cerdeira JO, Araújo MB (2014) Shifting protected areas: scheduling spatial priorities under climate change. *Journal of Applied Ecology* 51: 703-713. doi:10.1111/1365-2664.12230 | Sequential (time-step) ILP-style scheduling with release of sites | Shows that allowing release of redundant sites raises long-term persistence when budgets are small. The closest "ILP for multi-period planning" precedent. |
| Bonneau M, Sabbadin R, Johnson FA, Stith B (2018) Dynamic minimum set problem for reserve design: heuristic solutions for large problems. *PLoS ONE* 13: e0193093. doi:10.1371/journal.pone.0193093 | Heuristics for dynamic min-set (Marxan plus site-ordering; augmented greedy) | Dynamic min-set formalised as an MDP; exact solution intractable at scale. |
| Haight RG, Snyder SA (2009) Integer programming methods for reserve selection and design. In Moilanen et al. (eds) *Spatial Conservation Prioritisation*, OUP. | Review incl. scenario/multi-period IP formulations | UNVERIFIED in detail (not re-read). |
| Schuster R, Buxton RT, Hanson JO, et al. (2023) Protected area planning to conserve biodiversity in an uncertain future. *Conservation Biology* 37: e14048. doi:10.1111/cobi.14048 | Hierarchical multi-objective ILP with risk layers (governance, land use, climate) | Treats risk as extra objectives rather than modelling dynamics. Cited on the prioritizr multi-objective page [web]. |
| Cho F, Hanson JO (2026) robust.prioritizr: Robust Systematic Conservation Prioritization. *EcoEvoRxiv* preprint. doi:10.32942/X2609W | Chance-constrained programming and CVaR on top of prioritizr | Case study: Victoria, Australia, 872 species, 12,988 PUs, 4 climate scenarios x 5 time steps; robust plans met objectives across more futures than conventional plans [R5]. Time steps are treated as scenarios to be robust against, not as sequential decisions. |
| Buenafe KCV et al. (2023) A metric-based framework for climate-smart conservation planning. *Ecological Applications* 33: e2852. doi:10.1002/eap.2852 | Climate metrics as features/costs in prioritizr (spatialplanr) | |
| Alagador D (2023) Effective conservation planning of Iberian amphibians based on a regionalization of climate-driven range shifts. *Conservation Biology* 37: e14026. doi:10.1111/cobi.14026 | prioritizr application with climate | Listed in prioritizr publication record. |

For contrast (CAPTAIN side, reviewed elsewhere): Silvestro D, Goria S,
Sterner T, Antonelli A (2022) Improving biodiversity protection through
artificial intelligence. *Nature Sustainability* 5: 415-424.
doi:10.1038/s41893-022-00851-6. A web search found comparisons of CAPTAIN
against Marxan but **no published head-to-head comparison of CAPTAIN with
prioritizr or another exact ILP solver** (search 2026-11-27; absence not
exhaustively verified). This is a real gap the project could fill.

### 1.4 Notable applications (selection)

The package ships a publication record vignette with 120 entries in 8.1.0
(research articles 2017-2026, reviews, book chapters) [local 8.1.0,
`doc/publication_record.Rmd`]. Representative high-profile uses:

- Schuster R et al. (2019) Optimizing the conservation of migratory species
  over their full annual cycle. *Nature Communications* 10: 1754.
  doi:10.1038/s41467-019-09723-8 (multiple seasons as features: a
  time-structured but static formulation).
- Hanson JO et al. (2020) *Nature* 580: 232-234 (above).
- Jung M et al. (2021) *Nature Ecology & Evolution* 5: 1499-1509 (above;
  listed in the publication record).
- Chapman M et al. (2025) Meeting European Union biodiversity targets under
  future land-use demands. *Nature Ecology & Evolution* 9: 810-821.
  doi:10.1038/s41559-025-02671-1 (scenario-driven future land use).
- Brito-Morales I et al. (2022) climate-smart 3D high-seas protected areas,
  *Nature Climate Change* 12: 402-407 (from publication record; DOI not
  checked).
- Liczner AR et al. (2023) bumble bee priorities in Canada under current and
  future climate, *Conservation Science and Practice* 5: e12994 (from
  publication record).
- Welch H et al. (2023/2024) planning unit size in *dynamic management*
  strategies, *Conservation Biology* 38: e14201 (from publication record):
  here "dynamic" means re-solving frequently on changing data (dynamic ocean
  management), not sequential decision optimization.

---

## 2. Formulation inventory

Function names below are from the CRAN 8.1.0 namespace [local 8.1.0] and the
current reference index [web, R3]. Renames in 9.0.0 are flagged.

All problems are mixed integer linear programs. Notation: x_i decision for
planning unit (PU) i, c_i cost, r_ij amount of feature j in PU i, t_j target,
w_j feature weight, B budget.

### 2.1 Objectives

| Function | Type | Form (from help pages [local 8.1.0]) |
|---|---|---|
| `add_min_set_objective()` | Min-set | min sum c_i x_i s.t. sum r_ij x_i >= t_j for all j |
| `add_max_cover_objective()` | Budgeted | Historical max coverage (Church and ReVelle 1974): maximize number (weighted) of features with any representation (> 0) subject to cost <= B. Prior to v3.0.0 this name was the utility objective (NEWS 3.0.0.0). |
| `add_max_utility_objective()` -> renamed `add_max_wtd_sum_objective()` in 9.0.0 [R2] | Budgeted | max sum_j w_j a_j, a_j = sum_i r_ij x_i, cost <= B. In 8.1.0 includes a tiny cost tie-breaker (-s c_i x_i); 9.0.0 removed tie-breakers for run time [R2]. |
| `add_max_features_objective()` -> renamed `add_max_n_targets_met_objective()` in 9.0.0 [R2] | Budgeted | Maximize (weighted) number of targets met, cost <= B (inspired by Cabeza and Moilanen 2001). |
| `add_min_shortfall_objective()` | Budgeted | min sum_j w_j y_j s.t. sum_i r_ij x_i + t_j y_j >= t_j, cost <= B (Arponen et al. 2005 inspired). |
| `add_min_largest_shortfall_objective()` | Budgeted | Minimize max_j relative shortfall; not compatible with weights. |
| `add_max_phylo_div_objective()`, `add_max_phylo_end_objective()` | Budgeted | Maximize phylogenetic diversity / endemism of met targets on a tree (`ape`). In 9.0.1 `ape` is optional. |
| `add_min_penalties_objective()` (new 8.0.6) | Budgeted | Minimize only the penalties subject to targets and budget; intended for hierarchical multi-objective workflows [local 8.1.0]. |

Multi-objective (9.0.0, not in 8.1.0) [R2, R6]: `multi_problem()` combining
named `problem()`s, with `add_hier_approach()` (lexicographic with `rel_tol`
degradation), `add_ref_point_approach()` (reference point with
normalization), `add_wtd_sum_approach()`; helpers
`approach_weights_matrix()`, `approach_rel_tol_matrix()`; epsilon-constraint in
the separate moec.prioritizr package. In 9.0.1 budget-limited objectives accept
`budget = NULL` for use within `multi_problem()` [R2].

### 2.2 Targets

- `add_absolute_targets()`, `add_relative_targets()`, `add_manual_targets()`
  (per feature/zone, with sense `>=`, `<=`, `=`).
- `add_loglinear_targets()`: **deprecated in 8.1.0**, replaced by
  `spec_interp_absolute_targets()` (NEWS 8.1.0 [local]).
- New in 8.1.0: `add_auto_targets()` and `add_group_targets()` with target
  setting methods `spec_absolute_targets()`, `spec_area_targets()`,
  `spec_duran_targets()`, `spec_interp_absolute_targets()`,
  `spec_interp_area_targets()`, `spec_jung_targets()`, `spec_max_targets()`,
  `spec_min_targets()`, `spec_polak_targets()`, `spec_pop_size_targets()`,
  `spec_relative_targets()`, `spec_rl_ecosystem_targets()`,
  `spec_rl_species_targets()`, `spec_rodrigues_targets()`,
  `spec_rule_targets()`, `spec_ward_targets()`, `spec_watson_targets()`,
  `spec_wilson_targets()`; `spec_sreekar_targets()` added in 9.0.0.1 dev [R2].
  Several are IUCN Red List based (criteria A and B; e.g.
  `spec_rl_species_targets(status, criterion_a, criterion_b, ...)` with
  subcriteria A1-A4 that reference past or future population reduction)
  [local 8.1.0]. Note: these encode time only through the target *size*, not
  through dynamics.
- `add_feature_weights()` (single use only from 8.1.0).

### 2.3 Constraints

`add_locked_in_constraints()`, `add_locked_out_constraints()`,
`add_manual_locked_constraints()`, `add_manual_bounded_constraints()`,
`add_linear_constraints()` (arbitrary sum_i a_i x_i {<=,=,>=} b),
`add_neighbor_constraints()` (each selected PU needs >= k selected neighbours),
`add_contiguity_constraints()` (all selected PUs form one connected component,
Önal and Briers 2006 flow formulation), `add_feature_contiguity_constraints()`
(per-feature connectivity), `add_mandatory_allocation_constraints()` (zones:
every PU must be allocated to some zone), `add_cost_constraints()` (9.0.0)
[local 8.1.0; R2, R3]. Deprecated: `add_connected_constraints()`,
`add_corridor_constraints()` [R3].

Locked constraints accept numeric indices, logical, matrix, column names, `sf`,
`Spatial`, `Raster`, `SpatRaster` [local 8.1.0 `?add_locked_in_constraints`].
This is the hook used for sequential workflows (section 3).

### 2.4 Penalties

`add_boundary_penalties()` (Marxan-style boundary length, linearized per
Beyer et al. 2016; `edge_factor`; a `formulation` argument added in 8.1.0 to
offer an alternative faster formulation, default `"simple"`),
`add_connectivity_penalties()` (symmetric), `add_asym_connectivity_penalties()`
(Beger et al. 2010), `add_linear_penalties()` (per-PU linear term, e.g.
threat or opportunity cost), `add_neighbor_penalties()` (new 8.0.6.7;
"especially useful when working with large-scale problems or open source
solvers"), `add_cost_penalties()` (9.0.0), plus `calibrate_cohon_penalty()`
(new 8.0.6.7: automatic penalty calibration by the Cohon method)
[local 8.1.0 NEWS; R2, R3].

### 2.5 Decision types

`add_binary_decisions()` (default), `add_proportion_decisions()` (continuous
x_i in [0, 1]: LP relaxation, useful for very large problems or partial
management), `add_semicontinuous_decisions(upper_limit)` (x_i in [0, u])
[local 8.1.0].

### 2.6 Zones

`zones()` lets features and costs differ by zone; decisions become x_iz with
at most one zone per PU (or proportions summing to <= 1); targets, locked
constraints, penalties (zone-to-zone matrices) and
`add_mandatory_allocation_constraints()` are zone-aware. Management zones
vignette ships with the package [local 8.1.0].

### 2.7 Portfolios

| Function | Mechanism | Solver requirement |
|---|---|---|
| `add_default_portfolio()` | single solution | any |
| `add_extra_portfolio()` | all solutions found during search (Gurobi pool) | Gurobi >= 8 |
| `add_top_portfolio(number_solutions)` | n best solutions (Gurobi pool) | Gurobi >= 8 |
| `add_gap_portfolio(number_solutions, pool_gap)` | n solutions within `pool_gap` of optimal; "useful for... selection frequencies... (similar to Marxan)" | Gurobi >= 9, binary decisions only |
| `add_cuts_portfolio(number_solutions)` | re-solve with cuts forbidding previous solutions | any |
| `add_shuffle_portfolio(number_solutions)` | re-solve with randomly reordered formulation; may return duplicates | any |
| `add_single_portfolio()` | (9.0.0, new) | |
| `add_pool_portfolio()` | deprecated | |

[local 8.1.0; R2, R3]

### 2.8 Importance (irreplaceability)

`eval_replacement_importance()` (Cabeza and Moilanen 2006: re-solve with each
selected PU locked out; exact but costly, one solve per selected PU),
`eval_ferrier_importance()` (Ferrier et al. 2000; min-set problems),
`eval_rare_richness_importance()` (Williams et al. 1996),
`eval_rank_importance()` (incremental budgets, Jung et al. 2021). Old names
`replacement_cost()`, `ferrier_score()`, `rarity_weighted_richness()` are
deprecated [local 8.1.0; R3].

### 2.9 Solvers

| Function | Backend / R package | Notes |
|---|---|---|
| `add_gurobi_solver()` | Gurobi, `gurobi` | Commercial, free academic licence. Supports start solution, solution pools, `objbound` attribute (8.1.0), Gurobi 13 (8.1.0.1). |
| `add_cplex_solver()` | IBM CPLEX, `cplexAPI` | Commercial, free academic licence. |
| `add_cbc_solver()` | COIN-OR CBC, `rcbc` (GitHub only, not CRAN) | Recommended open-source option in the vignettes. |
| `add_highs_solver()` | HiGHS, `highs` (CRAN) | Added 7.2.2.x; start solution support needs dev `highs` (9.0.0). |
| `add_lpsymphony_solver()` | SYMPHONY, `lpsymphony` (Bioconductor) | |
| `add_rsymphony_solver()` | SYMPHONY, `Rsymphony` | |
| `add_scip_solver()` | SCIP | Development version 9.0.1.1 only [R2]. |
| `add_default_solver()` | Ranked: Gurobi > CPLEX > CBC > HiGHS > lpsymphony > Rsymphony | [local 8.1.0 `?add_default_solver`] |

lp_solve (`lpSolveAPI`) is **not** a supported solver in 8.1.0 or the current
reference index [local 8.1.0; R3]. **Default `gap = 0.1` (10% relative gap) for
every solver** (`formals()` [local 8.1.0]): out-of-the-box solutions are only
guaranteed within 10% of optimal. Any benchmark against CAPTAIN must set
`gap = 0` (or report the gap) to make optimality claims.

### 2.10 Evaluation and utilities

Summaries: `eval_cost_summary()`, `eval_n_summary()`,
`eval_feature_representation_summary()`, `eval_target_coverage_summary()`,
`eval_boundary_summary()`, `eval_connectivity_summary()`,
`eval_asym_connectivity_summary()`, `eval_objective_summary()` (9.x).
Utilities: `presolve_check()`, `compile()`, `write_problem()` (export
MPS/LP), `marxan_problem()` (import Marxan inputs), matrix builders
(`boundary_matrix()`, `adjacency_matrix()`, `proximity_matrix()`,
`connectivity_matrix()`, `rij_matrix()`), simulation (`simulate_data()`,
`simulate_species()`, `simulate_cost()`) [local 8.1.0; R3]. `write_problem()`
and the `compile()`d `OptimizationProblem` (obj, A, rhs, sense, lb, ub, vtype)
are natural interoperability hooks for an external sequential driver.

---

## 3. Time, uncertainty and dynamics

### 3.1 What is built in

Short answer: **nothing in core prioritizr models time or stochastic dynamics
explicitly.** A grep of all shipped vignettes for "dynamic", "sequential",
"time step", "multi-period", "uncertain(ty)" and "probabil(ity)" finds no
methods content on these topics, only data descriptions and publication titles
[local 8.1.0, `doc/*.Rmd`]. The 8.1.x to 9.0.1.x release notes mention no
uncertainty, robust, multi-period or climate functionality (WebFetch summary
of NEWS, [R2]). Specifically:

- No `add_constant_targets()` or any multi-time-step target function exists
  (not in namespace [local 8.1.0] or reference index [R3]).
- No probabilistic/robust targets in core. These live in **robust.prioritizr**
  (CRAN 1.1.0, 2026-05-29; Cho and Hanson): chance-constrained programming
  (Charnes and Cooper 1959) and CVaR (Rockafellar and Uryasev 2000), a
  confidence-level parameter trading robustness against cost, no
  distributional assumptions, exact MILP solvers [R5, R7].
- Time enters only indirectly:
  - Features can be time-indexed layers (e.g. current and future SDM
    projections, or seasons as in Schuster et al. 2019) with targets per
    layer: a static plan robust to or covering several snapshots.
  - Red List target methods use population-reduction criteria (A1-A4), which
    refer to past/future declines, only to size targets.
  - `get_sim_complex_historical_features()` exists in the simulated data set
    [R3], but its documentation page could not be retrieved (UNVERIFIED what
    "historical" denotes).
- Multi-objective (9.0.0) can treat risk layers as objectives (the Schuster
  et al. 2023 approach) [R6].

### 3.2 Standard workflow to approximate dynamic or sequential planning

There is no official vignette for this. The pattern used in the literature and
supported by the API is a **rolling-horizon (myopic) loop**:

1. At step t, update features (e.g. habitat loss, climate projection for t)
   and costs.
2. `add_locked_in_constraints()` for PUs already protected at t-1 (or
   `add_manual_bounded_constraints()` for proportion decisions); optionally
   `add_locked_out_constraints()` for PUs lost/converted.
3. Solve a budget-limited objective (`add_min_shortfall_objective()`,
   `add_max_utility_objective()`) with the per-period budget, or a min-set
   with a `add_linear_constraints()` cap on per-step spend.
4. Record, simulate change, repeat.

Each step is solved to (near) optimality, but the sequence is **myopic**: it
does not optimize over future states, so it is not guaranteed optimal for the
multi-period problem. Meir et al. (2004) and Costello and Polasky (2004) are
the canonical demonstrations that this can matter. Alternatively a
deterministic multi-period ILP (x_it variables with cumulative budget and
"once protected stays protected" constraints, as in Alagador et al. 2014) can
be built by hand: stack time steps as extra "zones" or via `compile()` and
custom constraints, but prioritizr offers no helper. UNVERIFIED whether anyone
has published a zones-as-time-steps trick with prioritizr.

### 3.3 Nested / ranked outputs as a proxy for scheduling

`eval_rank_importance()` solves a sequence of budget-limited problems with
increasing budgets, each constrained to lie within the full solution
(upper bounds from `solution`) and to contain the previous increment (lower
bounds from the previous step, warm-started with CBC/Gurobi), and scores each
PU by the fraction of increments in which it is selected [local 8.1.0
`?eval_rank_importance`, steps 3 to 9]. This is effectively a **nested,
greedy-in-budget acquisition schedule**: a defensible "what to protect first"
order under a static world. It is the most natural prioritizr-native
counterpart to a CAPTAIN policy rollout, but it still assumes no change in
features or costs between increments.

---

## 4. Optimality and performance claims

- **Guarantee**: for the formulated MILP, solvers return a solution with a
  certified relative gap (default 10%); `gap = 0` yields proven optimality
  given enough time. 8.1.0 exposes the best bound as `attr(x, "objbound")`
  (Gurobi only) [local 8.1.0 NEWS]. Status, gap and runtime are attached to
  solutions (see attributes listed in `?eval_rank_importance`). Guarantees
  apply only to the static, deterministic formulation (and to linear proxies,
  e.g. boundary length penalties for fragmentation).
- **Schuster et al. 2020** (BC, Canada case study) [R8]: EILP plans were
  **12-30% cheaper** than Marxan simulated annealing; best EILP solver was **on
  average 1,071 times faster** than SA; advantages held with boundary
  penalties; no calibration needed (Marxan requires SA parameter
  calibration). Authors argue this enables real-time use in stakeholder
  meetings and rapid sensitivity analysis.
- **Beyer et al. 2016**: showed the Marxan objective with boundary terms can be
  linearized and solved exactly; ILP outperformed SA in solution quality and
  time on their test problems (abstract not available in OpenAlex; claim
  per general knowledge, mark UNVERIFIED in detail).
- **Package benchmark** (Solver benchmarks vignette, [R9]): 72 features;
  1,478, 12,902, 102,242 and 606,180 PUs; targets 10/15/20/30%; min-set
  (boundary penalty 0, 1e-5, 1e-3) and min-shortfall (budget 10% of total
  cost; penalty 0, 1e-14, 1e-13); 6 h time limit. Findings: CPLEX and Gurobi
  fastest and similar; on the largest min-set problem with low penalty Gurobi
  finished "in under half an hour in all cases"; CBC generally fast, sometimes
  slightly faster without penalties, but sometimes much slower; SYMPHONY
  solvers took "over a whole day" to "one to two whole days" on large
  min-shortfall problems with penalties; some runs hit the time limit. Code
  and results: github.com/prioritizr/benchmark.
- **Hanson et al. 2025** reaches the same qualitative conclusion: open-source
  fine for large simple problems, commercial needed for complex large ones
  [R4].
- **Scale caveat**: problem size grows with PUs x features (rij nonzeros) and
  quadratically-linearized penalties add variables/constraints per PU pair;
  contiguity constraints are known to be expensive (flow formulation). The new
  `add_neighbor_penalties()` and alternative boundary formulation are explicit
  responses to run-time issues [local 8.1.0 NEWS].

---

## 5. Practicalities

| Aspect | Detail | Source |
|---|---|---|
| Current CRAN version | 9.0.1, published 2026-09-24 | [R1] |
| Release history (CRAN) | 0.1.2 (2016-12) ... 7.0.1 (2021-03), 7.1.1 (2021-10), 7.2.2 (2022-09), 8.0.0 (2023-03), 8.0.2 (2023-05), 8.0.3 (2023-08), 8.0.4 (2024-06), 8.0.6 (2025-01), 8.1.0 (2025-11), 9.0.1 (2026-09). Roughly 1 to 3 CRAN releases per year, with many dev versions in between (e.g. 8.0.6.1 to 8.0.6.8). | crandb timeline [R10]; GitHub releases |
| Licence | GPL-3 | [R1], DESCRIPTION |
| Maintainer | Richard Schuster (cre); authors Hanson, Schuster, Morrell, Strimas-Mackey, Edwards, Watts, Arcese, Bennett, Possingham | DESCRIPTION [local 8.1.0] |
| R requirement | R >= 4.1.0 | [R1] |
| Inputs (planning units) | `terra::rast()` (and legacy `raster`), `sf` (and legacy `sp`), `data.frame`, `matrix`, `numeric` vector; features as rasters, column names, or long-format data frames (rij). Support for `raster`/`sp` classes **deprecated in 9.0.1**. | [local 8.1.0 `?problem`]; [R2] |
| Outputs | Solutions returned in the same class as PU input (raster layer per zone, sf columns `solution_1_zone_1`, etc.), with attributes runtime, status, objective, gap (and objbound for Gurobi). | [local 8.1.0] |
| Imports | sf, terra, raster, exactextractr, Matrix, igraph, ape, R6, Rcpp-compiled internals (libs/ directory present); igraph and ape optional from 9.0.1 | DESCRIPTION; [R2] |
| Website and vignettes | prioritizr.net: Package overview, Getting started (prioritizr), Connectivity tutorial, Calibrating trade-offs, Management zones, Gurobi installation guide, Solver benchmarks, Publication record; Software extensions (new in 9.0.1) | [local 8.1.0 `doc/`]; [R2, R11] |
| GitHub | github.com/prioritizr/prioritizr: 139 stars, 30 forks, 17 open issues, created 2017-02 (queried 2026-11-27) | `gh api` |
| CRAN downloads (RStudio mirror only) | 16,328 in the 12 months to 2026-11-26; 117,336 total since 2016 | cranlogs API [R12] |
| Citations | Hanson et al. 2025: 155 (OpenAlex); Schuster et al. 2020: 76 (OpenAlex) | OpenAlex [R4] |

Ecosystem (prioritizr.net Software extensions page [R11] and CRAN reverse
dependencies [R1]):

- Reverse imports on CRAN: MultiscaleSCP, prior3D, priorCON, robust.prioritizr;
  reverse suggests: multiscape, phylospatial [R1].
- Formulation extensions: moec.prioritizr (epsilon-constraint
  multi-objective), MultiscaleSCP (H3 multiscale), patchwise (whole-patch
  features), priorCON (graph community connectivity), prior3D (depth
  dimension; Doxa et al. 2024, *Ecological Modelling* 499: 110919,
  doi:10.1016/j.ecolmodel.2024.110919), robust.prioritizr (uncertainty).
- Data/workflow: prioritizrdata (example data; in Suggests), wdpar (WDPA
  cleaning; Hanson 2022 JOSS 7: 4594), oceandatr, spatialplanr (climate-smart
  workflows).
- Accessibility: wheretowork (Shiny app, NCC), shinyplanr.
- Sister package: oppr (project prioritization; Hanson et al. 2019 MEE).
- The extensions page lists **no package for restoration scheduling or
  multi-period planning** [R11].

---

## 6. Known limitations and gaps (stated fairly)

Where prioritizr is strong (relevant to the CAPTAIN comparison):

- Provable optimality (or bounded gap) for the stated problem; reproducible,
  deterministic outputs given solver and seed; transparent algebraic
  formulation users can audit (`compile()`, `write_problem()`).
- Rich, composable constraint/penalty/zone vocabulary, now with multi-objective
  approaches and an extensions ecosystem; fast enough for interactive use on
  10^4 to 10^5 PUs with commercial solvers [R8, R9].
- Mature, heavily used and documented, with a large application base [local
  publication record].

Gaps that CAPTAIN-style methods target:

1. **Static snapshot.** One decision at one time. No state transitions, no
   modelling of habitat loss, species response, or budget arriving over time.
   Sequential use is a manual myopic loop (section 3.2) without
   look-ahead.
2. **Deterministic inputs.** Core treats rij, costs and targets as known.
   Uncertainty handling is via scenarios-as-features, portfolios, hierarchical
   risk objectives, or the separate robust.prioritizr (static robust
   optimization, not adaptive/recourse) [R5].
3. **No feedback/adaptive policy.** No monitoring-update-decide loop, no
   learning of a policy that generalizes to new landscapes; each problem is
   solved from scratch (warm starts aside).
4. **Linearity.** Objectives must be linear (or linearizable) in decisions.
   Non-linear benefit functions (e.g. species-area curves, persistence
   probabilities) need piecewise approximations; population dynamics cannot
   be embedded directly. (Note `spec_interp_*` targets interpolate targets, not
   benefit curves.)
5. **Solver dependence.** Large or penalty-heavy problems effectively need
   Gurobi/CPLEX (licence friction outside academia); CBC requires the
   GitHub-only `rcbc` [R9; local package overview]. Default gap of 10% is
   easily overlooked.
6. **Scale of complex spatial constraints.** Contiguity and dense connectivity
   matrices scale poorly (motivation for `add_neighbor_penalties()`).

Caveats against overstating the gap:

- A deterministic multi-period ILP (Alagador et al. 2014 style) is fully
  expressible in MILP; it is a missing *convenience*, not a fundamental
  limitation, for known future trajectories.
- Literature (Meir et al. 2004) shows that under strong uncertainty simple
  sequential heuristics can match optimal static plans, which cuts both ways:
  it motivates dynamic methods, but also suggests that a myopic prioritizr
  loop may be a strong baseline for CAPTAIN to beat.
- True stochastic dynamic optimization (SDP/MDP) is intractable at PU scale,
  which is exactly why RL (CAPTAIN) or heuristics are used; RL gives no
  optimality guarantee either.

---

## 7. Open questions for the comparison

1. Is there any published head-to-head of CAPTAIN vs prioritizr (or Gurobi on
   the same objective)? None found; Silvestro et al. 2022 compares to Marxan.
2. Can CAPTAIN's per-step objective be written as a prioritizr problem so a
   myopic prioritizr loop (with `gap = 0`) serves as the baseline policy?
3. Would a thin helper for multi-period problems (time-indexed decisions,
   per-period budgets, no-release or release constraints, Alagador et al. 2014)
   be a worthwhile prioritizr feature or extension package?
4. How does `eval_rank_importance()` ordering compare with CAPTAIN's
   protection order in a static world?
5. Does robust.prioritizr (chance constraints/CVaR) already cover the
   uncertainty part of CAPTAIN's value proposition, leaving only adaptivity?
6. Confirm `get_sim_complex_historical_features()` purpose (doc page not
   retrievable).
7. Version pinning: upgrade local install from 8.1.0 to 9.0.1 before hands-on
   work (function renames affect scripts).

---

## References

- [R1] CRAN, prioritizr package page. <https://cran.r-project.org/package=prioritizr> (accessed 2026-11-27).
- [R2] prioritizr release notes (NEWS). <https://prioritizr.net/news/index.html> (accessed 2026-11-27); 8.1.0 and earlier also in local `NEWS.md`.
- [R3] prioritizr reference index. <https://prioritizr.net/reference/index.html> (accessed 2026-11-27; reflects dev 9.0.1.x).
- [R4] Hanson JO, Schuster R, Strimas-Mackey M, Morrell N, Edwards BPM, Arcese P, Bennett JR, Possingham HP (2025) Systematic conservation prioritization with the prioritizr R package. *Conservation Biology* 39: e14376. <https://doi.org/10.1111/cobi.14376> (metadata and abstract via OpenAlex <https://api.openalex.org/works/doi:10.1111/cobi.14376>).
- [R5] Cho F, Hanson JO (2026) robust.prioritizr: Robust Systematic Conservation Prioritization. EcoEvoRxiv. <https://doi.org/10.32942/X2609W>
- [R6] prioritizr multi-objective approaches reference page. <https://prioritizr.net/reference/approaches.html>
- [R7] CRAN, robust.prioritizr. <https://cran.r-project.org/package=robust.prioritizr>
- [R8] Schuster R, Hanson JO, Strimas-Mackey M, Bennett JR (2020) Exact integer linear programming solvers outperform simulated annealing for solving conservation planning problems. *PeerJ* 8: e9258. <https://doi.org/10.7717/peerj.9258>
- [R9] prioritizr Solver benchmarks vignette. <https://prioritizr.net/articles/solver_benchmarks.html> ; data and code <https://github.com/prioritizr/benchmark>
- [R10] CRAN release timeline via crandb. <https://crandb.r-pkg.org/prioritizr/all> ; GitHub releases <https://github.com/prioritizr/prioritizr/releases>
- [R11] prioritizr Software extensions vignette. <https://prioritizr.net/articles/software_extensions.html>
- [R12] cranlogs API. <https://cranlogs.r-pkg.org/downloads/total/2025-11-27:2026-11-26/prioritizr>
- Alagador D, Cerdeira JO, Araújo MB (2014) *J Appl Ecol* 51: 703-713. <https://doi.org/10.1111/1365-2664.12230>
- Alagador D (2023) *Conserv Biol* 37: e14026. <https://doi.org/10.1111/cobi.14026>
- Albuquerque F, Beier P (2015) *PLoS ONE* 10: e0119905. <https://doi.org/10.1371/journal.pone.0119905>
- Beger M et al. (2010) *Conserv Lett* 3: 359-368. <https://doi.org/10.1111/j.1755-263X.2010.00123.x>
- Beyer HL, Dujardin Y, Watts ME, Possingham HP (2016) *Ecol Model* 328: 14-22. <https://doi.org/10.1016/j.ecolmodel.2016.02.005>
- Bonneau M, Sabbadin R, Johnson FA, Stith B (2018) *PLoS ONE* 13: e0193093. <https://doi.org/10.1371/journal.pone.0193093>
- Buenafe KCV et al. (2023) *Ecol Appl* 33: e2852. <https://doi.org/10.1002/eap.2852>
- Cabeza M, Moilanen A (2006) *Biol Conserv* 132: 336-342. <https://doi.org/10.1016/j.biocon.2006.04.025>
- Chapman M et al. (2025) *Nat Ecol Evol* 9: 810-821. <https://doi.org/10.1038/s41559-025-02671-1>
- Costello C, Polasky S (2004) *Resour Energy Econ* 26: 157-174. <https://doi.org/10.1016/j.reseneeco.2003.11.005>
- Doxa A et al. (2024) prior3D. *Ecol Model* 499: 110919. <https://doi.org/10.1016/j.ecolmodel.2024.110919>
- Ferrier S, Pressey RL, Barrett TW (2000) *Biol Conserv* 93: 303-325. <https://doi.org/10.1016/S0006-3207(99)00149-4>
- Hanson JO et al. (2017) *PNAS* 114: 12755-12760. <https://doi.org/10.1073/pnas.1711009114>
- Hanson JO, Fuller RA, Rhodes JR (2019) *J Appl Ecol* 56: 913-922. <https://doi.org/10.1111/1365-2664.13315>
- Hanson JO, Schuster R, Strimas-Mackey M, Bennett JR (2019) oppr. *Methods Ecol Evol* 10: 1655-1663. <https://doi.org/10.1111/2041-210X.13264>
- Hanson JO et al. (2020) *Nature* 580: 232-234. <https://doi.org/10.1038/s41586-020-2138-7>
- Hanson JO et al. (2022) *J Appl Ecol* 59: 2507-2519. <https://doi.org/10.1111/1365-2664.14251>
- Jung M et al. (2021) *Nat Ecol Evol* 5: 1499-1509. <https://doi.org/10.1038/s41559-021-01528-7>
- Meir E, Andelman S, Possingham HP (2004) *Ecol Lett* 7: 615-622. <https://doi.org/10.1111/j.1461-0248.2004.00624.x>
- Moilanen A et al. (2005) *Proc R Soc B* 272: 1885-1891. <https://doi.org/10.1098/rspb.2005.3164>
- Moilanen A et al. (2022) *Methods Ecol Evol* 13: 1062-1072. <https://doi.org/10.1111/2041-210X.13819>
- Rodrigues ASL, Cerdeira JO, Gaston KJ (2000) *Ecography* 23: 565-574. <https://doi.org/10.1111/j.1600-0587.2000.tb00175.x>
- Rodrigues ASL, Gaston KJ (2002) *Biol Conserv* 107: 123-129. <https://doi.org/10.1016/S0006-3207(02)00042-3>
- Schuster R et al. (2019) *Nat Commun* 10: 1754. <https://doi.org/10.1038/s41467-019-09723-8>
- Schuster R et al. (2023) *Conserv Biol* 37: e14048. <https://doi.org/10.1111/cobi.14048>
- Silvestro D, Goria S, Sterner T, Antonelli A (2022) *Nat Sustain* 5: 415-424. <https://doi.org/10.1038/s41893-022-00851-6>
- Visconti P, Pressey RL, Segan DB, Wintle BA (2010) *Biol Conserv* 143: 756-767. <https://doi.org/10.1016/j.biocon.2009.12.018>
- Watts ME et al. (2009) Marxan with Zones. *Environ Model Softw* 24: 1513-1521. <https://doi.org/10.1016/j.envsoft.2009.06.005>
- Wilson KA, McBride MF, Bode M, Possingham HP (2006) *Nature* 440: 337-340. <https://doi.org/10.1038/nature04366>
- Not DOI-checked (cited from prioritizr help pages): Ball, Possingham and Watts (2009) Marxan and relatives (OUP chapter); Önal and Briers (2006) *Oper Res* 54: 379-388; Williams, ReVelle and Levin (2005) *Environ Model Assess* 10: 163-181; Williams et al. (1996) *Conserv Biol* 10: 155-174; Haight and Snyder (2009) OUP chapter; Hanson (2022) wdpar, *JOSS* 7: 4594.
