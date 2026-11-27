.libPaths(c(Sys.getenv("SCRATCH_RLIB"), .libPaths()))
suppressPackageStartupMessages({library(prioritizr); library(terra)})
pu <- get_sim_pu_raster(); f <- get_sim_features()
base <- problem(pu, f) %>% add_min_set_objective() %>% add_relative_targets(0.1) %>% add_binary_decisions()
o <- compile(base); cat("model: ncol", o$ncol(), "nrow", o$nrow(), "ncell", o$ncell(), "\n")
for (g in c(0.1, 0)) for (s in c("gurobi","highs","cbc")) {
  p <- switch(s, gurobi = add_gurobi_solver(base, gap = g, verbose = FALSE),
    highs = add_highs_solver(base, gap = g, verbose = FALSE),
    cbc = add_cbc_solver(base, gap = g, verbose = FALSE))
  t <- system.time(sol <- solve(p))[["elapsed"]]
  cat(sprintf("gap=%.1f %-7s wall=%.2fs solver_runtime=%.3fs obj=%.3f\n", g, s, t, attr(sol,"runtime"), attr(sol,"objective")))
}
