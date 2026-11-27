# CAPTAIN: literature and documentation review

> Detailed working notes from the 2026-11-27 review. The synthesis is
> [`../01_captain_review.md`](../01_captain_review.md).

Prepared 2026-11-27 for the captain-vs-prioritizr project. Scope: papers,
preprints, supplementary material, website, public docs and tutorials, and
wider reception. Source-code review is being done separately, so code is only
referenced here where the public docs describe it. Reference keys in square
brackets (for example [S22]) point to the References section at the end.

Reading note for a prioritizr/ILP reader: in reinforcement learning (RL) terms,
CAPTAIN learns a *policy* (a small neural network that scores planning units
from per-unit features) by repeatedly running a simulated landscape forward in
time and adjusting the network weights to increase a cumulative *reward*
(for example, number of species not lost). There is no explicit mathematical
program and no optimality certificate; quality is judged empirically by
running the trained policy in held-out simulations or on data.

---

## 0. Key findings in brief

1. **Core citation confirmed.** Silvestro D, Goria S, Sterner T, Antonelli A
   (2022) Improving biodiversity protection through artificial intelligence.
   *Nature Sustainability* 5(5): 415-424. doi:10.1038/s41893-022-00851-6
   [S22]. An author manuscript is on Europe PMC (PMC7612764) and scripts, data
   and the Supplementary Information are on Zenodo (doi:10.5281/zenodo.5643665,
   CC BY 4.0) [S22-Z].
2. **The programme has grown into a family of papers and a company.** Peer
   reviewed follow-ups now include restoration with carbon and biodiversity
   objectives (*Global Change Biology* 2026, doi:10.1111/gcb.71165) [S26-GCB],
   an RLHF (reinforcement learning from human feedback) perspective paper
   (*Environmental Research Letters* 2026, doi:10.1088/1748-9326/aea2ab)
   [S26-ERL], a 30x30 and financial disclosure opinion paper (*COSUST* 2025)
   [S25-COSUST], and an independent-team application to Canada's 30x30
   targets (*Earth's Future* 2026) [A26]. Several preprints and conference
   abstracts extend it further. Authors now list "Captain Technologies Ltd,
   London" as an affiliation [S26-ERL-pre, S26-GCB-pre].
3. **The Marxan comparison is weaker than the abstract suggests.** The
   published simulation benchmark reports CAPTAIN beating Marxan in 64% of
   simulations (mean 9.2% less species loss) for one-shot protection and 77.2%
   (18.5%) for staged protection [S22, Results, Fig. 5]. But: (a) the preprint
   reported 96.8% and 40% before Marxan was given an explicit budget
   constraint [S21-pre v2], so the result is sensitive to how Marxan is set
   up; (b) a simple greedy heuristic (species-per-cost ratio) did slightly
   *better* than CAPTAIN in the one-shot setting (species loss -28.4% vs
   -26.7% relative to random) and was close in the staged setting (-23.0% vs
   -26.0%), but appears only in Supplementary Table 3, not in the main text
   [S22-SI, Table 3]; (c) in the "dynamic" comparison Marxan was optimised
   once at step 3 and its units were then placed one per step, not
   re-optimised as data were updated [S22-SI, Comparison with Marxan]; (d)
   Marxan's target (10 individuals per species inside protected units) is not
   the quantity being scored (species persisting after 25 steps of simulated
   dynamics) [S22-SI].
4. **The Madagascar empirical comparison was static and the margin is
   small.** Both tools received the same one-shot, presence-absence problem
   (1,517 trees, 22,394 units, 10%-of-range targets, budget of at most 10% of
   units). CAPTAIN met all targets in 68% of 50 replicates versus 2% for
   Marxan without BLM and 0% with BLM 0.1, but the median number of species
   missing their target was 0 for CAPTAIN and 1 (range 0-3) for Marxan without
   BLM [S22, Results; S22-SI, Table 4]. This is exactly the kind of problem an
   exact ILP solver handles well; no ILP/prioritizr comparison has been
   published (none found).
5. **No independent benchmark or critique found.** I found no study, by
   anyone outside the CAPTAIN group, comparing CAPTAIN with Marxan, Zonation
   or prioritizr. The only post-2022 head-to-head work is a CAPTAIN-group
   arXiv preprint swapping the optimiser (ES to PPO), which finds that
   decision granularity, not the learning algorithm, drives most of the gain
   [QO26].
6. **Software status.** CAPTAIN v3 (3.0.0rc1, released 2026-11-04) is a
   PyTorch rewrite with GPU support, SDM raster inputs, multi-objective
   rewards, regional agents, connectivity and edge effects, and a new static
   single-step mode [C3-README, C3-CHANGELOG]. Licence across v1-v3 is
   **CC BY-NC-ND 4.0** (non-commercial, no derivatives), and "primary
   development occurs in a private repository" [C3-README, C1-README]. These
   two facts matter a lot for any interoperability or code-sharing plan.

---

## 1. Bibliography

### 1.1 Core CAPTAIN papers (CAPTAIN group)

| Key | Citation | Status | Notes |
|---|---|---|---|
| S21-pre | Silvestro D, Goria S, Sterner T, Antonelli A. Optimising biodiversity protection through artificial intelligence. bioRxiv doi:10.1101/2021.04.13.439752. v1 2021-04-14, v2 2021-10-02 [bioRxiv API]. | Preprint | Earlier version of S22. Reports "97% of cases" and "40%" vs Marxan (abstract; Results) [S21-pre v2]. |
| S22 | Silvestro D, Goria S, Sterner T, Antonelli A (2022). Improving biodiversity protection through artificial intelligence. *Nature Sustainability* 5(5): 415-424. doi:10.1038/s41893-022-00851-6. Published online 2022-03-24. | Peer reviewed | Main paper. Author manuscript: Europe PMC PMC7612764. |
| S22-Z | Silvestro D et al. (2022). Supplementary data for: Improving biodiversity protection through artificial intelligence. Zenodo doi:10.5281/zenodo.5643665 (CC BY 4.0). | Data/code | Contains Supplementary_information.pdf, trained models, empirical data/analysis, CAPTAIN code snapshot, Marxan scripts. |
| S25-COSUST | Silvestro D, Goria S, Groom B, Sterner T, Antonelli A (2025). The 30 by 30 biodiversity commitment and financial disclosure: metrics matter. *Current Opinion in Environmental Sustainability* 77: 101587. doi:10.1016/j.cosust.2025.101587 (SSRN preprint doi:10.2139/ssrn.4594937, 2023). | Peer reviewed (opinion) | Argues cheapest-land 30x30 and simplistic disclosure metrics give smaller benefits; highlights AI approaches [Crossref abstract via search]. Full text not read. |
| S26-GCB | Silvestro D, Goria S, Rau E-P, Ferreira de Lima RA, Groom B, Jacobsson P, Sterner T, Antonelli A (2026). Using artificial intelligence to optimize ecological restoration for climate and biodiversity. *Global Change Biology* 32: e71165. doi:10.1111/gcb.71165. Preprint: bioRxiv doi:10.1101/2025.01.31.635975 (v1 2025-02-06 to v4 2026-10-08). | Peer reviewed | "CAPTAIN v.2" multi-objective RL for restoration (carbon, extinction risk, cost); Atlantic Forest case study. I read preprint v4. |
| S26-ERL | Silvestro D, Goria S, Rau E-P, Sterner T, Antonelli A (2026). Reconciling top-down and bottom-up conservation priorities with reinforcement learning from human feedback. *Environmental Research Letters* 21: 181002. doi:10.1088/1748-9326/aea2ab. Preprint: EcoEvoRxiv doi:10.32942/X2T651 (first titled "Reconciling top-down conservation priorities with bottom-up local needs", 2025-11-21). | Peer reviewed (perspective) | Proposes an RLHF architecture; no empirical results. I read the EcoEvoRxiv PDF. Cites prioritizr (Hanson et al. 2025, *Conserv. Biol.* 39: e14376) as an example of SCP software. |
| B26 | Butikofer L, Silvestro D, Rubio Teso ML, Molina AS, Lara-Romero C, Garcia Valdes R, Broennimann O, Iriondo JM, et al. (2026). Future-proofing agrobiodiversity: climate and niche-aware conservation planning using reinforcement learning. bioRxiv doi:10.64898/2026.05.04.722509. | Preprint | New CAPTAIN routines for range shifts and niche coverage of European crop wild relatives (186 then 1,140 taxa). No Marxan/prioritizr comparison mentioned in abstract. |
| QO26 | Quintero Ossa AM, Silvestro D, Rudd-Jones J, Perez-Ortiz M (2026). Beyond Expected Value: PPO with Distributional Critics for Systematic Conservation Planning. arXiv:2611.32948 (submitted 2026-11-24). | Preprint, v1 | Replaces CAPTAIN's Evolution Strategies optimiser with PPO plus an Implicit Quantile Network (CVaR objective); New Zealand marine data, 583 species. |

### 1.2 Applications and conference work using CAPTAIN

| Key | Citation | Notes |
|---|---|---|
| A26 | Alejo C, Luers A, Ventimiglia A, Arce-Plata M-I, Matthews HD (2026). Maximizing Nature-Based Solutions Using Artificial Intelligence to Align Global Biodiversity, Climate, and Water Targets. *Earth's Future* 14: e2025EF007560. doi:10.1029/2025EF007560. | **Canada 30x30** conservation and restoration scenarios with CAPTAIN, v1-style workflow (train on simulations, apply to empirical data). Static, one-shot. Authors are from Concordia, Future Earth Canada, Microsoft and Universite de Montreal; no CAPTAIN developers. Compared only with random selection and existing PAs; no other planning tool is mentioned. Full text read; details in section 3.4. |
| H26 | Horn K, Silvestro D, Wallis C, Leitao PJ, Daldaban E, Rudolph A (2026). Identifying valuable forest habitats for conservation in north-western Germany using AI and citizen science. EGU General Assembly 2026, EGU26-4011. | Ten forest bird indicator species, 2016-2024 habitat models, select 30% of forest sites in North Rhine-Westphalia, scenarios with and without opportunity costs. Conference abstract only. |
| G25 | Guevara M, Rowden A, Silvestro D (2025). Use of Artificial Intelligence to Assist Marine Spatial Planning: Development of a 'Proof-of-Concept' Study for New Zealand. One Ocean Science Congress 2025, OOS2025-857. | Compares CAPTAIN priorities with existing MPAs; reports CAPTAIN "can substantially change where MPAs should be placed". Abstract only. Likely the same NZ marine dataset used in QO26 (unverified). |
| C24 | Silvestro D (2024). We built an AI tool to help set priorities for conservation in Madagascar: what we found. *The Conversation*, 2024-03-26 (republished by phys.org and AIhub). | Popular piece. Reports the Madagascar tree application from S22; no new quantitative results. Discloses Silvestro co-founded CAPTAIN Technologies Ltd. The Kew-led Madagascar review it links (Ralimanana et al. 2022, *Science* 378: eadf1466) is a broad review; I found no evidence that it used CAPTAIN (unverified). |
| DL23 | Deng et al. (2023). Advancements of "CAPTAIN" in Plants Conservation Compared to Traditional Techniques. *Cambridge Explorations in Arts and Sciences* 1(2). doi:10.61603/ceas.v1i2.25. | Appears to be a student-journal review; not read; low evidential weight. |

### 1.3 Related RL-for-conservation work (not CAPTAIN, but context for reception)

| Key | Citation | Relevance |
|---|---|---|
| L22 | Lapeyrolerie M, Chapman MS, Norman KEA, Boettiger C (2022). Deep reinforcement learning for conservation decisions. *Methods in Ecology and Evolution*. doi:10.1111/2041-210X.13954. | Independent (Boettiger lab) introduction to deep RL for conservation (fisheries quotas, tipping points). Warns that "the required expertise and computational cost may place these applications beyond the reach of all but large, international technology firms" and calls for public benchmark challenges [Crossref abstract]. |
| E24 | Equihua J, Beckmann M, Seppelt R (2024). Connectivity conservation planning through deep reinforcement learning. *Methods in Ecology and Evolution* 15: 779-790. doi:10.1111/2041-210X.14300. | Independent DRL for budget-constrained connectivity planning; shows DRL "converges to the known optimums in a small example" and "approximates high-quality solutions" on a larger one [Crossref abstract]. A model for how to benchmark RL against known optima. |
| SCH20 | Schuster R, Hanson JO, Strimas-Mackey M, Bennett JR (2020). Exact integer linear programming solvers outperform simulated annealing for solving conservation planning problems. *PeerJ* 8: e9258. | Directly relevant: CAPTAIN's only external baseline was Marxan (simulated annealing). |

### 1.4 Critiques and commentaries

- **None found** that specifically critique CAPTAIN or re-run its benchmarks.
  Searches covered general web, Crossref, and terms combining CAPTAIN with
  Marxan, prioritizr, Zonation, critique, benchmark, ILP. I did not search
  Web of Science or Scopus citation lists (no access), so a published comment
  could exist; treat "none found" as unverified absence.
- S22 acknowledgements thank Atte Moilanen and Bob Pressey (among others) for
  feedback on an earlier manuscript [S22, Acknowledgements]; this shows the SCP
  community saw it pre-publication but is not a review.
- QO26 (CAPTAIN co-authored) is the closest thing to a methodological critique
  of CAPTAIN's optimiser: it states that ES "lacks per-timestep credit
  assignment" and that much of the apparent algorithmic gain came from finer
  decision granularity [QO26].
- Wider context: Araujo (2025, *Nat. Rev. Biodivers.* 1: 279-281, "Conflicting
  rationalities limit the uptake of spatial conservation prioritizations") and
  Wyborn and Evans (2021) on global priority maps are cited by S26-ERL as
  critiques of top-down SCP in general, not of CAPTAIN [S26-ERL-pre, refs].

---

## 2. Method (as published in S22, "CAPTAIN v1")

All of this section is from S22 Methods and the Supplementary Information
(S22-SI) unless noted.

### 2.1 Problem framing

- Framed as a **stochastic control problem**: the system state S_t evolves
  through time and is influenced by discrete protect actions chosen by a
  protection policy pi_Y [S22, Methods, "Policy definition and optimization
  algorithm"].
- **State**: S_t = {H_t, D_t, F_t, T_t, C_t, P_t, B_t}: individuals per species
  per cell, disturbance, selective disturbance, climate, protection cost,
  protection status, remaining budget [S22, Methods, Eq. 1; S22-SI Table 1].
- **Two action types**: (1) *monitoring*, which determines what the agent
  observes, and (2) *protecting*, which selects a protection unit [S22,
  Methods]. In all experiments the monitoring policy pi_X is **fixed a
  priori** (frequency and which features); only the protection policy is
  optimised [S22, Methods]. So despite the framing, CAPTAIN v1 does not learn
  *where or when to monitor*; it compares hand-specified monitoring regimes.
- **Planning units**: "protection units" of equal size made of one or more
  grid cells (5x5 cells in simulations) [S22, Methods; Fig. 2 caption].
- **Episode**: a full simulation of T steps (25 in the main experiments;
  30 in Fig. 4) [S22-SI, Experiments; S22 Fig. 4 caption].
- **Action granularity**: unless stated otherwise, at most **one protection
  unit per time step**, if the budget allows (Cost(Y, S_t) < B_t) [S22,
  Methods]. A "one-time" variant spends all budget in a single step [S22,
  Results, Benchmarking].
- **Effect of protection**: disturbance in the unit is reset to an arbitrarily
  low level and the unit is immune to future disturbance increases; climate
  change is **not** mitigated by protection; an optional buffer models edge
  effects [S22, Methods].
- **Reward**: cumulative value of species that do not go extinct over the
  episode. Equal values minimise species extinctions; other values give
  phylogenetic diversity or economic value objectives; alternatively the
  reward can be protected area [S22, Methods, "Conservation planning within a
  reinforcement learning framework"]. A species is counted extinct when its
  total population falls below 10 individuals [S22-SI, Comparison with
  Marxan].

### 2.2 Biodiversity simulator

- **Individual-based, spatially explicit** with natural mortality,
  replacement, and dispersal. Offspring dispersal decays exponentially with
  distance (dispersal rate lambda); recruitment fills each cell up to carrying
  capacity K [S22-SI, Supplementary Methods, Eqs 1-2].
- **Disturbance** D reduces carrying capacity to (1 - D)K and raises
  mortality according to species sensitivity d_s [S22-SI, Eq. 3]. **Selective
  disturbance** F (for example logging of particular species) kills a fraction
  f_s F of individuals without changing K [S22-SI].
- **Climate**: a temperature layer (latitudinal gradient, warming over time);
  mortality rises linearly with distance outside a species' realised thermal
  tolerance (derived from its initial range) [S22-SI].
- **Default experiment**: 50 x 50 cells, K = 1,000 per cell, 500 species,
  Weibull population sizes, 2.5 million individuals; ranges from a diffusion
  process; mortality 0.01; growth 1; dispersal lambda = 0.1; d_s ~ Beta(1,1);
  f_s ~ Beta(0.2, 0.7); phylogenies from a birth-death process; economic
  values with spatial structure (20% of species 100x more valuable) [S22-SI,
  Experiments settings].
- **Cost**: C_c = 0.2 + 0.4 D_c per cell, i.e. disturbed land costs up to 3x
  more; unit cost is the sum over its cells [S22-SI]. Budget 55, so at most
  11 of 100 units (fewer if disturbed units are chosen) [S22-SI].
- Disturbance starts at 0 and spreads via random diffusion; mean disturbance
  rises roughly tenfold (0.07 to 0.7) over 20 steps [S22-SI, Supp. Fig. 3].

### 2.3 Monitoring (data acquisition) regimes compared

[S22, Results; S22-SI]

- **Full Recurrent Monitoring**: presence and abundance every step.
- **Citizen-science Recurrent Monitoring**: presence/absence only every step,
  with 5% non-detection (inversely related to abundance) and 5%
  misidentification; also tested with 25% error.
- **Full Initial Monitoring**: presence and abundance at step 1 only.
- Monitoring has a constant cost, equal across policies [S22, Methods]; I did
  not find this cost being traded off against protection in the experiments.

### 2.4 Policy (network) and features

- **Features per protection unit** (S22-SI Table 2): x1 number of species not
  already in protected units (a complementarity feature); x2 number of such
  species that are "rare" (population below a threshold set by a learned
  meta-parameter q); x3 mean relative population change since last
  monitoring; x4 budget; x5 unit cost; x6 already-protected indicator; x7 and
  x8 cumulative value of unprotected (rare, declining) species.
- Species-specific sensitivities are **not** given to the policy; the authors
  argue they can be inferred from relative abundance changes (x3) [S22,
  Methods].
- **Network**: feed-forward, shared weights across units (each unit's feature
  vector goes through the same small network), ReLU hidden layer(s), softmax
  over units giving a probability of protecting each unit [S22, Methods, Eqs
  2-5]. Actual sizes were tiny: two hidden layers of 4 and 2 nodes, or one of
  8 nodes [S22-SI]. Training samples actions from the softmax; deployment
  takes the arg-max [S22, Methods].
- The authors note weight sharing loses spatial information and suggest a
  convolutional layer as a "natural next step" [S22, Methods]. (v3 now ships an
  experimental CNN extractor [C3-README].)

### 2.5 Training algorithm

- **Parallelised Evolution Strategies** (Salimans et al. 2017), with an
  advantage-like baseline borrowed from policy-gradient methods: perturb
  weights with Gaussian noise, run one full episode per perturbation on
  parallel workers, update weights by the noise-weighted reward improvement
  relative to a running average; learning rate 0.1 [S22, Methods, Eq. 6].
  This is gradient-free with respect to the simulator and the policy.
- Training runs: 6 parallel simulations per epoch, 1,000 epochs, each episode
  on a new randomly generated system of 25 steps [S22-SI].
- Evaluation: 250 fresh simulations with fixed seeds shared across policies
  [S22-SI].
- In v3, docs describe the trainer as Natural Evolution Strategies with
  z-scored advantages by default [C3-ARCH, C3-CHANGELOG]. QO26 reports ES with
  32 perturbations per iteration at K = 1,000, and 64 perturbations for the
  K = 50 run, which took about 58 h to epoch 110 of 150 [QO26, Tables 1-2].

### 2.6 Objectives supported (v1)

Minimise species loss; minimise value loss (economic or other per-species
value, including phylogenetic diversity); maximise protected area [S22,
Methods]. Later versions add extinction-risk class transitions, carbon,
cost penalties, protected population share, worst-served species, layer
overlap and connectivity (Section 5).

### 2.7 Applying a trained policy to empirical data (Madagascar)

[S22, Methods, "Analysis of Madagascar endemic tree diversity"]

- Data: Carrasco et al. (2020) SDM-derived presence/absence for 1,517 endemic
  tree species on 22,394 units of 5 x 5 km; cost proportional to a threat
  layer.
- **No retraining**: the "One-time protection" model trained on simulations
  was applied directly. The authors say training or fine-tuning (transfer
  learning) on the empirical system would be possible and perhaps desirable.
- Because SDM presence ignores degradation, they **resampled presences**: each
  species got a random sensitivity d_s ~ U(0,1), and presence in unit c was
  drawn as Bernoulli(1 - d_s D_c). Repeated 50 times; results are selection
  frequencies across replicates.
- Target handling: the monitoring step was modified so a species counts as
  protected only once >= 10% of its range is in protected units.
- Static, single step, all units placed at once; budget = cost of the
  cheapest 10% of units (2,239 units maximum).

---

## 3. Evaluation claims and fairness assessment

### 3.1 What was compared

| Comparison | Baselines | Problem type | Source |
|---|---|---|---|
| Monitoring regimes and objectives | Random policy | Dynamic (25 steps) simulation | S22 Figs 2-3, SI Table 3 |
| Complementarity check | 10,000 random draws; "naive" top-20 richness | One simulation | S22 Fig. 4 |
| Simulated benchmark | Marxan 4.0.6; greedy; random | One-shot and staged, simulation | S22 Fig. 5, SI Table 3 |
| Empirical benchmark | Marxan (BLM 0 and 0.1) | Static, single step, real data | S22 Fig. 6, SI Table 4 |

No comparison with Zonation or prioritizr (or any ILP solver) appears in S22,
S26-GCB, S26-ERL, QO26 or B26 (B26 judged from abstract only).

### 3.2 Headline numbers (S22)

- Full Recurrent Monitoring protects on average 26% more species than random;
  citizen-science recurrent 24.9%; Full Initial Monitoring 20%. Recurrent
  policies beat random in 97.2% of simulations, initial-only in 91.2%
  [S22, Results].
- Value-loss objective reduces species loss by only 10.9% vs random;
  area-maximising objective protects 27.6% more cells but causes 13.6% more
  species loss than random [S22, Results; SI Table 3].
- **Vs Marxan (simulation)**: one-shot, CAPTAIN better in 64% of 250
  simulations, mean improvement 9.2% in prevented species loss; staged, better
  in 77.2%, mean 18.5% [S22, Results, Fig. 5].
- **Vs Marxan (Madagascar)**: all targets met in 68% of replicates vs at most
  2% for Marxan; median protected range fraction 22% vs 14% [S22, Results;
  SI Table 4].
- Abstract: "consistently outperforms available state-of-the-art software
  using simulated and empirical data" [S22, Abstract].

### 3.3 Fairness assessment (my reading, with evidence)

**(a) The comparison shrank substantially between preprint and publication.**
Preprint v2 reported CAPTAIN beating Marxan in 96.8% of simulations with
Marxan causing 40% more species loss (one-time) and 92% / 24% (recurrent), and
attributed part of the gap to Marxan not "explicitly incorporating a finite
budget" [S21-pre v2, Results "Empirical applications and benchmarking"]. In
the published paper Marxan was set up with COSTTHRESH = 55 and threshold
penalties, and the margins fell to 64% / 9.2% and 77.2% / 18.5% [S22; S22-SI].
This is to the authors' credit (they fixed it), but it shows the result is
highly sensitive to baseline configuration, and Marxan's COSTTHRESH is a soft
penalty rather than a hard budget constraint.

**(b) A greedy heuristic is competitive, and beats CAPTAIN in the one-shot
case.** Supplementary Table 3 (mean % change in species loss vs random,
250 simulations) [S22-SI, Table 3]:

| Setting | CAPTAIN | Greedy (species/cost ratio) | Marxan |
|---|---|---|---|
| Staged ("dynamic protection") | -26.0 (Full recurrent) | -23.0 | -13.4 |
| One-shot ("all budget spent at once") | -26.7 (Full monitoring) | **-28.4** | -21.2 |

The greedy baseline is described in the SI Methods but the main text and
abstract mention only random, "naive" and Marxan baselines [S22, main text;
checked by full-text search]. In the one-shot case, a few-lines heuristic
outperformed both CAPTAIN and Marxan on average. That Marxan lost to greedy in
both settings suggests the Marxan formulation, not the class of static
optimisers, was the weak point.

**(c) Objective mismatch.** Marxan was given a target of 10 individuals per
species within protected units (mirroring the extinction threshold) and
minimised cost subject to a soft budget [S22-SI]. Performance was then scored
as species persisting after 25 steps of increasing disturbance and climate
change. A min-cost-to-meet-a-weak-target formulation will pick the cheapest
units that touch each species and will not use spare budget to buffer
populations. This is reflected in Marxan protecting more area (+14.0% vs
random, one-shot) while losing more species [S22-SI, Table 3]. A
budget-constrained maximum-coverage or minimum-shortfall formulation (for
example prioritizr's min_shortfall or max_features objectives with
abundance-based or higher targets) would be the like-for-like static
comparator; it was not tested.

**(d) The "dynamic" Marxan baseline was not adaptive.** In the staged
experiment Marxan was "monitored and the model optimized as in the One-time
protection policy, but the selected units were established one at a time"
[S22-SI, Comparison with Marxan]. CAPTAIN, by contrast, re-observed the
system every step (Full Recurrent Monitoring). So the staged comparison
confounds (i) learned policy vs optimiser with (ii) recurrent data vs a
snapshot at step 3. A fair dynamic baseline is a rolling-horizon re-solve
(re-run the static optimiser each step on the current state and remaining
budget). That was not done.

**(e) In-distribution evaluation.** The policy was trained and tested on the
authors' own simulator with the same generative settings (new random seeds).
Marxan has no access to the simulator. That is a legitimate test of "does
learning from a dynamic model help when the world behaves like the model", but
not of robustness to model misspecification. S26-GCB later reports that
policies "achieve higher and more consistent performance when applied within
the region used in their optimization" and fine-tunes on the target region
[S26-GCB-pre v4, Results "Restoration priorities ... Atlantic Forest"],
consistent with this concern.

**(f) Small simulated problem.** 100 units, budget for at most 11 [S22-SI].
Static versions of this problem are trivial for an exact ILP solver, so
"state of the art" for the static sub-problem is an exact optimum, not
simulated annealing [SCH20].

**(g) Madagascar margin is about one species.** SI Table 4 (means over 50
resampled datasets) [S22-SI, Table 4]:

| Metric | CAPTAIN | Marxan BLM 0 | Marxan BLM 0.1 |
|---|---|---|---|
| % replicates meeting target for all species | 0.68 | 0.02 | 0 |
| % replicates missing target for < 10 species | 0.94 | 1 | 0 |
| Percentage of species protected | 99.98 | 99.93 | 99.35 |
| Median n species missing target | 0 (0-14) | 1 (0-3) | 202 (159-237) |
| Median fraction of range protected | 0.22 | 0.14 | 0.14 |
| Median n protected units (max 2,239) | 1,876 | 1,949 | 2,196 |

So without BLM, Marxan typically misses one species' target, and its worst
replicate misses 3, while CAPTAIN's worst misses 14. CAPTAIN's higher median
range coverage reflects a different behaviour (it keeps adding units), while
Marxan stops near the 10% target because it minimises cost; these are
different objectives. The BLM = 0.1 run used Carrasco et al.'s setting with a
new budget penalty and clearly struggled, but BLM has no CAPTAIN equivalent
[S22, Methods]. With an exact solver, whether all 1,517 targets can be met
within the budget is a yes/no question with a provable answer per replicate;
given CAPTAIN found such solutions in 68% of replicates, feasible solutions
exist there and an ILP minimum-set or minimum-shortfall formulation would be
expected to find them (my inference, unverified; a good candidate benchmark).

**(h) "Higher resolution, more interpretable maps."** Both tools used the same
5 x 5 km units [S22, Methods]; the difference in Fig. 6 is that CAPTAIN's
selection-frequency map is more spatially discriminating than Marxan's with
BLM. "Resolution" here means sharper ranking, not finer planning units. The
interpretability claim is qualitative.

**(i) What is fair to credit.** The simulation framework is genuinely
dynamic and lets the authors test questions static tools cannot pose
(value of recurrent monitoring, effect of monitoring error, objective
trade-offs over time). The policies were trained without access to
species sensitivities and still learned complementarity (Fig. 4b). The
greedy and random baselines, scripts and data are public on Zenodo [S22-Z],
which made this assessment possible.

### 3.4 Later evaluation claims

- **S26-GCB (restoration, v2)**: compares five reward weightings of carbon vs
  extinction risk (all restoring the same area). In simulations, extinction
  risk improved for 30% of 500 species under the carbon-only policy vs 71-76%
  under the others; CR species decreased 36% and EN 73% from Policy 1 to 5.
  Atlantic Forest (3,789 tree and shrub species, 16,263 units, restore 30%):
  carbon-only policy left about 7 times more species unprotected than the
  balanced policy, which cost about 18% of carbon [S26-GCB-pre v4, Results,
  Discussion]. Baselines: rule-based selections (for example threatened
  species per cost) "yielded substantially worse outcomes" (Table S3, not
  read) [S26-GCB-pre v4]. No Marxan, Zonation or prioritizr comparison.
- **QO26** (verified against the v1 PDF, 2026-11-27): NZ marine data, 583
  species, 800 x 500 grid, 17,000-cell budget, synthetic Perlin-noise
  disturbance with intensity drawn from U(0.05, 0.5) per episode [QO26,
  Section 2]. Final species counts by category, 10 disturbance draws, greedy
  evaluation [QO26, Table 1]:

  | Model | LC | NT | VU | EN | CR | Training |
  |---|---|---|---|---|---|---|
  | No protection | 395 | 86 | 30 | 12 | 60 | |
  | ES, K = 1,000 | 532 | 24 | 18 | 4 | 5 | about 300 s per iteration |
  | ES, K = 50 | 545 | 27 | 6 | 0 | 5 | 110 iterations, about 58 h |
  | PPO, K = 50 | 530 | 38 | 9 | 0 | 6 | 300 iterations, about 19 h |
  | IQN, alpha = 1, K = 50 | 540 | 28 | 10 | 0 | 5 | 200 iterations, about 43 h |
  | IQN CVaR, alpha = 0.25, K = 50 | 548 | 20 | 8 | 2 | 5 | 200 iterations, about 55 h |

  Authors conclude "Granularity, not the optimiser, is therefore the primary
  driver of the recovery" and that their earlier ES K = 1,000 vs PPO
  comparison "overstated PPO's algorithmic contribution" [QO26, Section 3].
  At matched K = 50, PPO is worse than ES on NT (38 vs 27) and VU (9 vs 6);
  the paper says PPO's advantage is "training efficiency, not raw outcome
  quality". The ES K = 1,000 baseline used 32 perturbations per iteration, but
  the K = 50 ES run behind the 58 h figure used 64 perturbations and 8 workers
  and was evaluated at epoch 110 of 150 [QO26, Table 2 caption]. Single
  training run per model, "indicative rather than statistically conclusive";
  zero outcome variance across disturbance seeds. The only baseline is no
  protection; Marxan and Zonation are named in the Introduction only, and
  prioritizr or ILP solvers are not mentioned. No code or data release for
  the PPO/IQN implementation was found [QO26].
- **A26** (full text and Supporting Information read 2026-11-27): Canada,
  10 x 10 km planning units (about 93,500 implied by "16,600 planning units
  = 17.75% of the total area"), 59 threatened species from IUCN and BirdLife
  area of habitat maps built with the `aoh` R package (48 birds, 11 mammals,
  6 plants, 1 reptile, 1 amphibian) [A26, Section 2.2]. CAPTAIN workflow
  follows S22: 100 simulated environments, a network with 8 hidden ReLU
  neurons and softmax sampling, parallel ES for 100 epochs, then applied to
  the empirical Canada environment; no version number or runtime is given
  [A26, Section 2.3]. Training budget was "arbitrarily defined as 10%" of
  total cost, while the empirical scenarios target about 17.75% of area
  (conservation) or about 7% (restoration). Reward: maximise occurrence of
  threatened species and "guarantee at least 10%" of each range while
  avoiding high costs. Co-benefits (ecological integrity, carbon, surface
  water) enter only through the cost layer, with ad hoc tenfold cost
  reductions chosen by comparing 1, 0.5 and 0.1 multipliers (Figures
  S8-S13); PUs with human footprint of 5 or more get the maximum cost. PUs
  with 50 km2 or more of existing PA are excluded (12.25%). Ten replicates per
  scenario; selection frequencies used to trim units beyond the area target.
  Validation is against random selection and existing PAs only, reported as
  average outcomes (species per 100 km2, tC/ha, and so on) [A26, Section 2.3;
  Figures 3, 5, S16, S19]. Whether every species reached its 10% target is
  not reported in the paper or the Supporting Information. Marxan, Zonation,
  prioritizr and ILP are not mentioned. Data and code on Zenodo,
  doi:10.5281/zenodo.17259008 [A26, Availability Statement]. Article licence
  CC BY-NC-ND. Funding: NSERC Alliance grant with Microsoft.

---

## 4. Practicalities (from website, READMEs and docs)

### 4.1 Website and repositories

- Website: <https://www.captain-project.net/> (Home, Download, Team,
  Publications). Currently promotes CAPTAIN 3 ("The new CAPTAIN (v.3.0.0rc1)
  is available"), lists v2 and v1 as legacy, and points to GitHub Discussions
  for support [CP-WEB]. Publications page lists S22, S26-GCB, S25-COSUST and
  S26-ERL [CP-PUB]. Team: Silvestro (ETH Zurich, Gothenburg), Goria (Thymia
  Ltd CTO), Sterner (Gothenburg economics), Antonelli (Kew, Gothenburg)
  [CP-TEAM]. Contact domain captaintech.ai [CP-TEAM; S26-GCB-pre].
- GitHub organisation captain-project (GitHub API, 2026-11-27):

| Repo | Purpose | Created | Last push | Stars | Licence field |
|---|---|---|---|---|---|
| captain-project | v1 (S22) | 2021-12-21 | 2023-12-13 (dev branch also 2023-12-13) | 56 | "Other" (CC BY-NC-ND 4.0 in LICENSE.md) |
| notebooks | v1 Jupyter tutorials | | 2022-12-04 | | |
| captain-app | v1 cross-platform desktop GUI | | 2022-09-15 | | |
| captain2 | v2 "(in development)", restoration/multi-objective | 2025-05-01 | 2025-09-23 (v.2.02) | 7 | "Other" (CAPTAIN-License.pdf) |
| example_data_captain2 | v2 examples | | 2026-02-19 | | |
| captain3 | v3 "Preview of CAPTAIN v.3" | 2026-03-04 | 2026-11-05 | 3 | none detected by GitHub; README and pyproject say CC BY-NC-ND 4.0 |

- Only one tagged release in the organisation: **v3.0.0rc1, 2026-11-05**
  (changelog dated 2026-11-04; a "3.0.0 beta preview" in August 2026)
  [C3-CHANGELOG; GitHub API]. v3 README: "Primary development occurs in a
  private repository; this public repository is updated with each release"
  and "feature requests may be prioritized based on our internal development
  roadmap" [C3-README].

### 4.2 Installation and dependencies

- v1: Python 3; notebooks for simulation, policy optimisation, policy
  application to simulated and to empirical data [C1-NB].
- v2: Python 3.11 or 3.12, `pip install .` in a venv [C2-README].
- v3: Python >= 3.11 (CI on 3.11-3.13), installed with `uv sync`; package name
  `captain3`, import name `captain`. Dependencies: numpy >= 2, torch >= 2.2,
  scipy, scikit-learn, numba, rasterio, rioxarray, matplotlib, seaborn,
  pillow, pyperlin. CUDA 13 PyTorch wheels configured; Windows long-path
  workaround documented. Not on PyPI or conda as far as I can see (installed
  from git) [C3-README; C3-PYPROJECT].

### 4.3 Inputs (v3, per quick start)

- Area mask (.npy); directory of **present SDM GeoTIFFs** and matching
  **future SDM** directory (interpolated over n time steps); disturbance and
  cost GeoTIFFs each with a future variant; species trait table CSV (minimum
  habitat suitability threshold, growth rate, IUCN-style conservation status,
  sensitivity to disturbance) [C3-QS].
- Carrying capacity in the quick start is set from conservation status
  (100 / status), and initial extinction risk from status in 5 classes
  [C3-QS]. These are modelling choices the user must supply or impute.
- Budget is expressed as a **number of cells** to protect in total and per
  time step (`GlobalBudgetManager(total_target, cells_per_time_step)`), with
  cost entering as a reward penalty rather than a hard monetary budget in the
  quick start [C3-QS; C3-REWARDS]. (Code-level confirmation is for the code
  reviewer.) S26-GCB likewise constrained the number of restored cells and
  penalised cost in the reward [S26-GCB-pre v4, Results].

### 4.4 Outputs

- Trained policy weights (flat NumPy array); episode info including protected
  cells [C3-QS].
- Optional per-decision `.npz` records of features, scores, eligibility,
  selected cells and ranks, intended for explainability analyses [C3-INF].
- KMZ/KML export for Google Earth or QGIS [C3-INF; C3-CHANGELOG].
- In S22, priority maps were selection frequencies across replicates [S22].

### 4.5 Tutorials and documentation

- v1: four notebooks [C1-NB]. v3: quick start, training guide (optimiser,
  reward calibration, convergence study), inference guide, architecture
  overview, toy example, rewards tutorial, advanced example (edge effects,
  existing PAs, connectivity, static prioritisation) [C3-README]. The training
  guide reports a toy run of about 58,000 cells, 10% protected, 100 epochs,
  "about 15 minutes per run on a laptop" with 4 CPU workers [C3-TRAIN].
- Documentation quality for v3 is good and candid (for example, it explains
  that a worst-species reward gives no signal early in training and needs a
  weight schedule, and that reward calibration can make early epochs
  unstable) [C3-REWARDS].

### 4.6 Licence and commercial context

- v1: "licensed jointly by Daniele Silvestro, Stefano Goria, Thomas Sterner,
  and Alexandre Antonelli on the Creative Commons
  Attribution-NonCommercial-NoDerivatives 4.0 International Public License";
  other uses require contacting the team [C1-README].
- v3: CC BY-NC-ND 4.0; "For commercial licensing inquiries or permission to
  deviate from these terms, please contact the development team" [C3-README].
- CC BY-NC-ND is not an OSI open-source licence and is unusual for software:
  "NoDerivatives" bars sharing modified versions, and "NonCommercial" may
  complicate use by NGOs or consultancies doing paid work (legal
  interpretation unverified). Captain Technologies Ltd (London) appears as an
  author affiliation from 2025 onwards [S26-GCB-pre; S26-ERL-pre; H26] and
  Silvestro is described as its co-founder [C24]. S26-ERL nonetheless argues
  the RLHF framework "should be implemented as an open-source well-documented
  tool" [S26-ERL-pre, "From theory to practice"].

---

## 5. How CAPTAIN has evolved (v1 to v3), from docs and papers

| Aspect | v1 (S22, 2022) | v2 (S26-GCB, 2025-2026) | v3 (3.0.0rc1, 2026-11) |
|---|---|---|---|
| Inputs | Simulated systems; empirical presence/absence | SDMs, carbon proxies, IUCN status, land use, cost | Present and future SDM rasters, trait table, disturbance and cost rasters with future variants [C3-QS] |
| Dynamics | Individual-based, disturbance, selective disturbance, climate | Same family; restoration reduces disturbance | Population matrix with dispersal, growth, carrying capacity; time-varying SDMs, disturbance and costs; edge effects [C3-ARCH] |
| Objectives | Species loss, value loss, area | Multi-objective: carbon, extinction risk classes, cost | Extinction-risk classes, cost, species value, protected population share, worst-served species, layer overlap, connectivity (ECA); reward weight schedules [C3-REWARDS] |
| Policy | Tiny MLP, softmax over units, one unit per step | MLP; robustness to architecture tested | Per-cell MLP scoring, **top-k** cells per decision; experimental CNN; regional agents [C3-ARCH, C3-README] |
| Training | Parallel ES | ES | NES with z-scored advantages, CPU pool or GPU [C3-ARCH, C3-TRAIN] |
| Static mode | "one-time" policy | | `EpisodeRunner(env_dynamics=False)` single step without dynamics [C3-CHANGELOG] |

The v3 extinction-risk reward re-classifies species each step as initial IUCN
status plus a bucket for population decline minus a bucket for gain in
protected share, with thresholds 4%, 16%, 36%, 64% when alpha = 0.5
[C3-REWARDS]. This is a heuristic proxy, not a Red List assessment, and QO26
also notes the categories are model projections [QO26].

---

## 6. Strengths (reported fairly)

1. **Explicitly sequential, dynamic planning.** CAPTAIN optimises *when* as
   well as *where*, under changing threats, costs and climate-driven range
   shifts (future SDMs in v3), with protection that alters future dynamics
   [S22; C3-QS]. Static ILP formulations do not model this feedback.
2. **Outcome-based objectives.** It scores species persistence or extinction
   risk change after simulated dynamics, rather than representation of
   current features. This directly addresses a long-standing SCP critique
   that representation targets are not outcomes.
3. **Value-of-information experiments.** Monitoring regimes and data error
   can be compared within one framework; finding that presence/absence with
   5-25% error recovers most of the benefit of full abundance monitoring is
   useful [S22, Results; SI Table 3].
4. **Flexible, nonlinear rewards.** Any computable function of the simulated
   end state (worst-served species, connectivity ECA, carbon, risk classes)
   can be optimised without linearisation [C3-REWARDS].
5. **Scales to large rasters with GPU support** and fast inference once
   trained (a trained policy is a scoring function) [C3-README].
6. **Learned without knowing species sensitivities**, inferring them from
   observed trends [S22, Methods].
7. **Openness of the original study.** Scripts, data, trained models and
   Marxan configuration on Zenodo [S22-Z]; good v3 docs and tests [C3-README].
8. **Active programme.** Restoration, RLHF, agrobiodiversity, marine,
   regional applications, and an independent Canada application [S26-GCB,
   S26-ERL, B26, G25, H26, A26].

## 7. Limitations and assumptions

1. **No optimality guarantees or gap.** ES/PPO-trained policies are
   heuristics; quality is only known empirically, and the published empirical
   baselines are Marxan and simple heuristics [S22]. In one-shot simulation a
   greedy ratio rule did better on average [S22-SI, Table 3].
2. **Simulator dependence.** Results rest on a simulator with many invented or
   imputed parameters (growth, carrying capacity from status, sensitivity
   drawn at random for Madagascar, imputation for the Atlantic Forest)
   [S22, Methods; S26-GCB-pre; C3-QS]. Atlantic Forest priorities overlapped
   only 74-94% across imputation runs depending on policy [S26-GCB-pre v4].
3. **Transfer from simulations to reality is not guaranteed**; the authors
   themselves fine-tune on target regions and report better performance
   in-region [S26-GCB-pre v4].
4. **Hard constraints are soft.** Budgets are expressed as cell counts with
   cost as a reward penalty (v3 quick start, S26-GCB); targets are encoded via
   features or rewards rather than constraints [C3-QS; S22, Methods]. There is
   no direct equivalent of locked-in/locked-out constraints in the docs I
   read, although "existing protected areas" are supported in the advanced
   example [C3-README]. (Unverified at code level.)
5. **Reward engineering and training instability.** Docs describe
   calibration multipliers of 10-50x, early-epoch instability, and reward
   terms that give no training signal without schedules [C3-REWARDS].
6. **Compute and expertise.** Training is tens of hours on realistic problems
   [QO26] (15 minutes on a toy problem [C3-TRAIN]); L22 warns about the
   expertise and compute barrier for RL in conservation generally.
7. **Stochastic, replicate-based outputs**: priority maps are frequencies over
   replicates and training seeds; QO26 notes single training runs are not
   statistically conclusive.
8. **Licence and governance**: CC BY-NC-ND, private primary development,
   commercial entity [C3-README; C1-README; C24].
9. **Monitoring is not optimised** in the published work (fixed a priori),
   despite the framing [S22, Methods].
10. **Planning units are grid cells or blocks of cells**; I found no support
    for irregular planning units (polygons) in the docs (unverified).

---

## 8. Ideas potentially relevant to prioritizr

These are ideas to evaluate, not recommendations yet.

1. **A shared benchmark is the obvious first collaboration.** The published
   evidence never pits CAPTAIN against an exact solver. Candidate designs:
   - *Static*: Madagascar trees (data on Zenodo [S22-Z]) or the v3 toy data,
     prioritizr min_set / min_shortfall / max_features with the same budget
     and 10% targets vs CAPTAIN v3 static mode. Report target attainment,
     cost, optimality gap, runtime.
   - *Dynamic*: use CAPTAIN's simulator as an evaluation environment and
     compare (i) a learned CAPTAIN policy, (ii) a one-shot prioritizr plan,
     (iii) a **rolling-horizon prioritizr** plan re-solved each step on the
     current state and remaining budget, (iv) greedy. This isolates the value
     of learning vs simply re-optimising with new data, which S22 did not
     separate (Section 3.3 d).
   - Follow E24's model: check RL against known optima on small instances.
2. **Sequential and multi-period planning in prioritizr.** CAPTAIN's main
   conceptual contribution is staged budgets under changing threats. prioritizr
   could support this via multi-period formulations (per-period budget
   constraints, decision variables indexed by time, threat-dependent future
   feature values) or a documented rolling-horizon workflow. Feasibility and
   scale are open questions.
3. **Simulation-based evaluation of static plans.** Even without learning, a
   "stress-test this solution under dynamics" step (feature loss under
   projected threat, climate-shifted SDMs) would help prioritizr users. CAPTAIN
   v3's environment, if licence permits use (not modification), could be an
   external evaluator; or prioritizr could export solutions as rasters for it.
4. **Outcome-oriented targets.** CAPTAIN's extinction-risk class reward
   resembles piecewise targets on protected share; worst-served species
   resembles prioritizr's existing min-largest-shortfall objective;
   connectivity ECA and edge effects map onto connectivity and boundary
   penalties. A side-by-side mapping would clarify what is genuinely new
   (the dynamics) vs what prioritizr already expresses exactly.
5. **Future-climate SDMs as features.** Using present and future suitability
   jointly (v3, B26) can be represented in prioritizr as multiple feature
   layers with targets on each; worth a vignette.
6. **Value of information and monitoring.** S22's monitoring experiments
   suggest a prioritizr-adjacent analysis: how plan quality degrades with
   detection error or stale data. prioritizr's evaluation functions could be
   paired with simulated data degradation.
7. **Risk-sensitive objectives.** QO26's CVaR objective parallels robust and
   chance-constrained optimisation in ILP; a comparison of formulations could
   be a joint methods paper.
8. **Learned policies as heuristics or warm starts.** For very large or
   nonlinear problems, a learned scoring function could provide starting
   solutions for a MIP solver; speculative.
9. **Stakeholder feedback.** S26-ERL's RLHF idea (pairwise preferences, spatial
   annotations, MaxMin aggregation across groups) has ILP analogues: locked
   in/out, penalties from annotated layers, and max-min objectives across
   stakeholder groups. Interesting for prioritizr's participatory use cases.
10. **Interoperability constraints.** Raster-based inputs (GeoTIFF SDMs, cost
    and threat layers) are easy to share between tools. Code-level
    integration (for example an R wrapper around CAPTAIN, or porting its
    simulator) is limited by CC BY-NC-ND; any such step needs the authors'
    permission.

---

## 9. Open questions

1. Would an exact ILP (prioritizr) meet all Madagascar targets within budget
   in every resampled replicate, and at what cost relative to CAPTAIN? (Data
   on Zenodo.)
2. How does a rolling-horizon static optimiser compare with a learned policy
   in CAPTAIN's own simulator? This is the crux of whether RL adds value
   beyond re-planning with fresh data.
3. How sensitive are CAPTAIN priorities to the simulator parameters users
   must impute (growth, carrying capacity, sensitivity)?
4. Licence: would the authors allow a benchmark harness or R interface, and
   does NonCommercial affect NCC or consultant use? Is a more permissive
   licence planned for v3.0.0?
5. Does v3 support irregular planning units, hard budgets in currency, and
   locked-in/out constraints? (Code reviewer to confirm.)
6. Citation-based reception: how many independent groups use CAPTAIN (needs
   Web of Science or Scopus citation search; not done).
7. Resolved: A26 (Canada) compares only with random selection and existing
   PAs and reports no runtime (full text read; see section 3.4). Its data and
   code are on Zenodo (10.5281/zenodo.17259008), which makes it a candidate
   Canadian benchmark.
8. Does B26 (agrobiodiversity) compare with any SCP tool in its full text?

---

## References

Primary CAPTAIN literature

- [S21-pre] Silvestro D, Goria S, Sterner T, Antonelli A. Optimising
  biodiversity protection through artificial intelligence. bioRxiv
  2021.04.13.439752, v2 posted 2021-10-02.
  <https://doi.org/10.1101/2021.04.13.439752> (read v2 PDF).
- [S22] Silvestro D, Goria S, Sterner T, Antonelli A (2022). Improving
  biodiversity protection through artificial intelligence. Nature
  Sustainability 5(5): 415-424. <https://doi.org/10.1038/s41893-022-00851-6>.
  Author manuscript read via Europe PMC full text, PMC7612764:
  <https://europepmc.org/article/PMC/PMC7612764>
- [S22-SI] Supplementary Information for S22 (Supplementary Methods, Figs
  1-6, Tables 1-4), from Supplementary_information.zip in [S22-Z].
- [S22-Z] Silvestro D, Goria S, Sterner T, Antonelli A (2022). Supplementary
  data for: Improving biodiversity protection through artificial
  intelligence. Zenodo. <https://doi.org/10.5281/zenodo.5643665>
- [S25-COSUST] Silvestro D, Goria S, Groom B, Sterner T, Antonelli A (2025).
  The 30 by 30 biodiversity commitment and financial disclosure: metrics
  matter. Current Opinion in Environmental Sustainability 77: 101587.
  <https://doi.org/10.1016/j.cosust.2025.101587> (abstract only).
- [S26-GCB] Silvestro D, Goria S, Rau E-P, de Lima RAF, Groom B, Jacobsson P,
  Sterner T, Antonelli A (2026). Using Artificial Intelligence to Optimize
  Ecological Restoration for Climate and Biodiversity. Global Change Biology
  32: e71165. <https://doi.org/10.1111/gcb.71165>
- [S26-GCB-pre] Preprint of S26-GCB, bioRxiv, v4 posted 2026-10-08.
  <https://doi.org/10.1101/2025.01.31.635975> (read v4 PDF).
- [S26-ERL] Silvestro D, Goria S, Rau E-P, Sterner T, Antonelli A (2026).
  Reconciling top-down and bottom-up conservation priorities with
  reinforcement learning from human feedback. Environmental Research Letters
  21: 181002. <https://doi.org/10.1088/1748-9326/aea2ab>
- [S26-ERL-pre] EcoEvoRxiv preprint of S26-ERL.
  <https://doi.org/10.32942/X2T651> ; PDF read from
  <https://ecoevorxiv.org/repository/object/10866/download/25388/>
- [B26] Butikofer L, Silvestro D, et al. (2026). Future-proofing
  agrobiodiversity: climate and niche-aware conservation planning using
  reinforcement learning. bioRxiv. <https://doi.org/10.64898/2026.05.04.722509>
  (abstract only).
- [QO26] Quintero Ossa AM, Silvestro D, Rudd-Jones J, Perez-Ortiz M (2026).
  Beyond Expected Value: PPO with Distributional Critics for Systematic
  Conservation Planning. arXiv:2611.32948. <https://arxiv.org/abs/2611.32948>
  (v1, submitted 2026-11-24; read via arXiv HTML and checked against the PDF).

Applications, commentary and related work

- [A26] Alejo C, Luers A, Ventimiglia A, Arce-Plata M-I, Matthews HD (2026).
  Maximizing Nature-Based Solutions Using Artificial Intelligence to Align
  Global Biodiversity, Climate, and Water Targets. Earth's Future 14:
  e2025EF007560. <https://doi.org/10.1029/2025EF007560> (full text and
  Supporting Information read; data and code at
  <https://doi.org/10.5281/zenodo.17259008>).
- [H26] Horn K, Silvestro D, Wallis C, Leitao PJ, Daldaban E, Rudolph A
  (2026). Identifying valuable forest habitats for conservation in
  north-western Germany using AI and citizen science. EGU26-4011.
  <https://meetingorganizer.copernicus.org/EGU26/EGU26-4011.html>
- [G25] Guevara M, Rowden A, Silvestro D (2025). Use of Artificial
  Intelligence to Assist Marine Spatial Planning: Development of a
  'Proof-of-Concept' Study for New Zealand. OOS2025-857.
  <https://meetingorganizer.copernicus.org/OOS2025/OOS2025-857.html>
- [C24] Silvestro D (2024). We built an AI tool to help set priorities for
  conservation in Madagascar: what we found. The Conversation, 2024-03-26.
  <https://theconversation.com/we-built-an-ai-tool-to-help-set-priorities-for-conservation-in-madagascar-what-we-found-224882>
- [DL23] Deng et al. (2023). Advancements of "CAPTAIN" in Plants
  Conservation Compared to Traditional Techniques. Cambridge Explorations in
  Arts and Sciences 1(2). <https://doi.org/10.61603/ceas.v1i2.25> (not read).
- [L22] Lapeyrolerie M, Chapman MS, Norman KEA, Boettiger C (2022). Deep
  reinforcement learning for conservation decisions. Methods in Ecology and
  Evolution. <https://doi.org/10.1111/2041-210X.13954> (abstract).
- [E24] Equihua J, Beckmann M, Seppelt R (2024). Connectivity conservation
  planning through deep reinforcement learning. Methods in Ecology and
  Evolution 15: 779-790. <https://doi.org/10.1111/2041-210X.14300> (abstract).
- [SCH20] Schuster R, Hanson JO, Strimas-Mackey M, Bennett JR (2020). Exact
  integer linear programming solvers outperform simulated annealing for
  solving conservation planning problems. PeerJ 8: e9258.
  <https://doi.org/10.7717/peerj.9258>
- Ralimanana H et al. (2022). Madagascar's extraordinary biodiversity:
  Threats and opportunities. Science 378: eadf1466.
  <https://doi.org/10.1126/science.adf1466> (checked metadata only).
- Carrasco J, Price V, Tulloch V, Mills M (2020). Selecting priority areas
  for the conservation of endemic trees species and their ecosystems in
  Madagascar considering both conservation value and vulnerability to human
  pressure. Biodiversity and Conservation 29: 1841-1854 (source of the
  Madagascar data; cited in S22, not read).

Website, repositories and docs (accessed 2026-11-27)

- [CP-WEB] <https://www.captain-project.net/>
- [CP-PUB] <https://www.captain-project.net/publications>
- [CP-TEAM] <https://www.captain-project.net/team>
- [C1-README] <https://github.com/captain-project/captain-project> (README.md
  and LICENSE.md)
- [C1-NB] <https://github.com/captain-project/notebooks> (README.md)
- [C2-README] <https://github.com/captain-project/captain2> (README.md)
- [C3-README] <https://github.com/captain-project/captain3> (README.md)
- [C3-PYPROJECT] <https://github.com/captain-project/captain3/blob/main/pyproject.toml>
- [C3-CHANGELOG] <https://github.com/captain-project/captain3/blob/main/CHANGELOG.md>
- [C3-QS] <https://github.com/captain-project/captain3/blob/main/docs/quickstart.md>
- [C3-ARCH] <https://github.com/captain-project/captain3/blob/main/docs/architecture.md>
- [C3-TRAIN] <https://github.com/captain-project/captain3/blob/main/docs/training.md>
- [C3-INF] <https://github.com/captain-project/captain3/blob/main/docs/inference.md>
- [C3-REWARDS] <https://github.com/captain-project/captain3/blob/main/tutorials/rewards/README.md>
- GitHub REST API metadata for the captain-project organisation (repo dates,
  stars, tags, releases), queried 2026-11-27.
- bioRxiv API version history for 10.1101/2021.04.13.439752 and
  10.1101/2025.01.31.635975; Crossref API metadata for all DOIs above.
