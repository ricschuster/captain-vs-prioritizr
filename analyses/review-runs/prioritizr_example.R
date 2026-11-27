.libPaths(c(Sys.getenv("SCRATCH_RLIB"), .libPaths()))
suppressPackageStartupMessages({library(prioritizr); library(terra)})
cat("prioritizr", as.character(packageVersion("prioritizr")), "\n")
pu <- get_sim_pu_raster(); f <- get_sim_features()
cat("PUs (non-NA):", sum(!is.na(values(pu))), " features:", nlyr(f), "\n")
base <- problem(pu, f) %>% add_min_set_objective() %>%
  add_relative_targets(0.1) %>% add_binary_decisions()
res <- list()
for (s in c("gurobi","highs","cbc","rsymphony")) {
  p <- switch(s,
    gurobi = add_gurobi_solver(base, gap = 0, verbose = FALSE),
    highs = add_highs_solver(base, gap = 0, verbose = FALSE),
    cbc = add_cbc_solver(base, gap = 0, verbose = FALSE),
    rsymphony = add_rsymphony_solver(base, gap = 0, verbose = FALSE))
  t <- system.time(sol <- try(solve(p), silent = TRUE))[["elapsed"]]
  if (inherits(sol, "try-error")) { cat(s, "ERROR", conditionMessage(attr(sol,"condition")), "\n"); next }
  cat(sprintf("%-10s wall=%.2fs solver_runtime=%.3fs status=%s obj=%.3f gap=%s selected=%d\n",
    s, t, attr(sol,"runtime"), attr(sol,"status"), attr(sol,"objective"),
    format(attr(sol,"gap")), sum(values(sol), na.rm=TRUE)))
  res[[s]] <- sol
}
# boundary penalty variant with HiGHS
pb <- base %>% add_boundary_penalties(penalty = 0.005) %>% add_highs_solver(gap = 0, verbose = FALSE)
t <- system.time(sb <- solve(pb))[["elapsed"]]
cat(sprintf("highs+BLM wall=%.2fs obj=%.3f selected=%d\n", t, attr(sb,"objective"), sum(values(sb), na.rm=TRUE)))
# evaluate an arbitrary externally produced solution (random selection), as one would a CAPTAIN output
set.seed(1)
ext <- pu; v <- values(ext); idx <- which(!is.na(v)); v[idx] <- 0
v[sample(idx, sum(values(res$highs), na.rm=TRUE))] <- 1; values(ext) <- v
p <- add_highs_solver(base, verbose = FALSE)
cat("\n== eval on prioritizr solution\n")
print(eval_cost_summary(p, res$highs)); print(head(eval_target_coverage_summary(p, res$highs)[, c("feature","relative_target","relative_held","met")], 5))
cat("\n== eval on arbitrary external (random) solution, same n selected\n")
print(eval_cost_summary(p, ext)); tc <- eval_target_coverage_summary(p, ext)
print(head(tc[, c("feature","relative_target","relative_held","met")], 5)); cat("targets met:", sum(tc$met), "/", nrow(tc), "\n")
print(eval_boundary_summary(p, ext))
cat("\n== ferrier importance on external solution (first rows)\n")
fi <- eval_ferrier_importance(p, ext); print(fi)
t <- system.time(ri <- eval_replacement_importance(p, res$highs))[["elapsed"]]
cat(sprintf("replacement importance (HiGHS) wall=%.2fs\n", t))
t <- system.time(rk <- eval_rank_importance(add_min_shortfall_objective(problem(pu,f), budget=1) %>% add_relative_targets(0.1) %>% add_highs_solver(verbose=FALSE), res$highs, n = 5))[["elapsed"]]
cat(sprintf("rank importance n=5 (HiGHS) wall=%.2fs\n", t)); print(attr(rk, "budgets"))
