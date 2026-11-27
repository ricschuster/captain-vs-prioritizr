# CLAUDE.md

Working rules and durable context for this project. This file is loaded into
context automatically, so keep it to direction and rules, not a task list.

## Project name

captain-vs-prioritizr

## Project purpose

A learning and evaluation project: understand CAPTAIN (Conservation Area
Prioritization Through Artificial INtelligence, https://www.captain-project.net/),
a reinforcement-learning approach to spatial conservation prioritization, and
compare it with prioritizr (https://prioritizr.net/), the integer linear
programming (ILP) based R package. The owner is a prioritizr developer; the
practical question is whether CAPTAIN's ideas (or the tool itself) are worth
deeper engagement by the prioritizr team, for example through features,
interoperability, benchmarks, or collaboration. See
`docs/design/00_project_brief.md` for the full brief.

## Project status

Just created from the template (2026-11-27). Next milestone: a literature and
software review of CAPTAIN (papers, code, docs) written up in `docs/design/`,
followed by a hands-on comparison on a shared example. Open GitHub issues are
the live task tracker.

## Scope

In scope: reading CAPTAIN's papers and source, running it, conceptual and
empirical comparison with prioritizr (problem formulation, objectives,
optimality guarantees, dynamic vs static planning, data needs, runtime,
usability), and a recommendation for the prioritizr team.

Not in scope: building a new prioritization tool, or changing prioritizr
itself in this repo (prototypes that touch prioritizr belong in a prioritizr
branch). Be fair to both tools: report CAPTAIN's strengths honestly, and
cite sources (paper, docs page, or file and line in its code) for factual
claims about either tool. Do not expand scope without a design note in
`docs/design/` or an ADR in `docs/decisions/`.

## Stack

Not fixed yet. Expected: R for prioritizr analyses and Python for CAPTAIN,
with Quarto or R Markdown for write-ups. Record the choice in an ADR in
`docs/decisions/` once made.

## Commands

None yet; fill in once the stack is chosen (`CONTRIBUTING.md` Setup should
match).

## Repo structure

- `docs/design/`: brief, review notes and comparison write-ups.
- `docs/decisions/`: ADRs.
- `docs/handoffs/`: session handoffs.

## Working rules

- Branch from `main`; one short-lived branch per change. Open a pull request
  into `main`; CI must pass before merge.
- Conventional Commits (for example `feat: ...`, `fix: ...`, `chore: ...`,
  `docs: ...`).
- No em dashes in code, comments, docs, commit messages, or user-facing text.
- Significant technical or design decisions get an ADR in `docs/decisions/`.
- Design notes live in `docs/design/`; session handoffs in `docs/handoffs/`.
- Keep changes small and focused; update docs when behaviour or design changes.
