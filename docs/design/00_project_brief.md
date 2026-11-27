# 00 Project Brief

## What this is

captain-vs-prioritizr is a learning and evaluation project on CAPTAIN
(https://www.captain-project.net/), a reinforcement-learning framework for
conservation area prioritization, and how it compares with prioritizr
(https://prioritizr.net/).

It is a review and benchmarking exercise, not a new software package. The
goal is to give the prioritizr team an informed answer to "is CAPTAIN
something we should look into more, and if so, how?"

## Who it is for

- The prioritizr development team (primary).
- Conservation planners curious how the two approaches differ (secondary,
  since the repo is public).

Readers are assumed to know systematic conservation planning and prioritizr
well, and to be less familiar with reinforcement learning.

## The core idea (one screen)

prioritizr formulates conservation planning as an exact optimization problem
(ILP) over a static snapshot of features and costs, and solves it to proven
(near-)optimality. CAPTAIN, as we currently understand it (to be verified in
the review), trains a policy with reinforcement learning on simulated
biodiversity dynamics, and protects sites sequentially over time under a
budget, reacting to changing threats and to what monitoring reveals. This
project pins down exactly what each tool optimizes, under what assumptions,
and where each one is the better fit.

## MVP scope

1. CAPTAIN review: papers, docs, source code, install and run a provided
   example. Written up in `docs/design/01_captain_review.md`.
2. Conceptual comparison with prioritizr: problem formulation, objectives,
   constraints, optimality, treatment of time and uncertainty, data inputs,
   outputs, performance, licensing, maintenance. Written up in
   `docs/design/02_comparison.md`.
3. Hands-on comparison on one shared dataset (where feasible), with results
   and caveats.
4. Recommendation for the prioritizr team: ignore, watch, borrow ideas,
   interoperate, or collaborate.

## Explicit non-goals (for now)

- Building or changing prioritizr features in this repo.
- An exhaustive benchmark across many datasets.

## Design principles

1. Fairness: compare each tool on the problem it was designed for, and say
   when a comparison is apples to oranges.
2. Cite everything: factual claims point to a paper, docs page, or source
   file and line.
3. Reproducibility: any empirical result comes with the code to rerun it.

## Open questions

- Can CAPTAIN be run on static, real-world planning data in a way that makes
  a like-for-like comparison with prioritizr meaningful?
- Is CAPTAIN actively maintained, and how mature is its code?
- Which of its ideas (dynamic/sequential planning, learned policies) could
  map onto prioritizr, for example as a multi-period or adaptive workflow?
