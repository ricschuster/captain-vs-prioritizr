"""Evaluate the CAPTAIN static plan against random, greedy and exact (MILP) plans.

Uses the environment built by the (copied) CAPTAIN static_prioritization example, so
the objective is exactly CAPTAIN's reward:
  R(x) = sum_s w_s min(h_s.x, t*P_s)/P_s / sum_s w_s  -  c.x / sum(c)
with w_s = THREAT_WEIGHTS[init_status_s], t = PROTECTION_TARGET, P_s = initial pop,
subject to sum(x) == n_target cells. Exports inputs and plans for a later prioritizr run.
"""
import sys
import time
from pathlib import Path

import numpy as np

RUN_DIR = Path(sys.argv[1])  # dir holding the copied static_prioritization.py
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(RUN_DIR))
import static_prioritization as sp  # noqa: E402
import highspy  # noqa: E402

ep = sp.create_episode_runner()
env = ep.env
w_path = sp.results_dir() / sp.MODEL_FILE

t0 = time.time()
info, total_reward = ep.run_episode(np.load(w_path))
t_inf = time.time() - t0
x_captain = env.protected_cells_mask.cpu().numpy().astype(float)

env.reset()
h = env.h.cpu().numpy().astype(float)            # (S, N) populations (static: = K)
cost = env.costs.data.cpu().numpy().mean(0).astype(float)
P = h.sum(1)
status = env.ext_risk.init_status.cpu().numpy()
w = np.asarray(sp.THREAT_WEIGHTS, float)[status] * (P > 0)
t = sp.PROTECTION_TARGET
n_target = int(x_captain.sum())
S, N = h.shape


def reward(x):
    prot = h @ x
    pop = (w * np.minimum(prot, t * P) / np.where(P > 0, P, 1)).sum() / (w * t).sum()
    return pop - cost @ x / cost.sum(), pop, cost @ x / cost.sum()


def summary(name, x, secs):
    r, pop, c = reward(x)
    share = (h @ x) / P
    print(f"{name:10s} cells={int(x.sum()):5d} reward={r:.4f} pop_term={pop:.4f} "
          f"cost_share={c:.4f} species>=target={int((share >= t - 1e-9).sum())}/{S} "
          f"min_share={share.min():.3f} time={secs:.1f}s")


print(f"N cells={N}, species={S}, budget={n_target} cells, zero-cost cells={(cost == 0).sum()}")
print(f"CAPTAIN env reward (internal) = {total_reward:.4f}")
summary("captain", x_captain, t_inf)

rng = np.random.default_rng(1)
xr = np.zeros(N); xr[rng.choice(N, n_target, replace=False)] = 1
summary("random", xr, 0)

# Greedy: repeatedly add cell with max marginal reward (batch of 1 percent at a time)
t0 = time.time()
xg = np.zeros(N); prot = np.zeros(S)
batch = max(1, n_target // 100)
while xg.sum() < n_target:
    rem = np.maximum(t * P - prot, 0)
    gain = (w[:, None] / np.where(P > 0, P, 1)[:, None] * np.minimum(h, rem[:, None])).sum(0) / (w * t).sum()
    gain -= cost / cost.sum()
    gain[xg == 1] = -np.inf
    k = int(min(batch, n_target - xg.sum()))
    idx = np.argpartition(-gain, k)[:k]
    xg[idx] = 1; prot = h @ xg
summary("greedy", xg, time.time() - t0)

# Exact MILP with HiGHS: max sum_s a_s y_s - c.x/C ; y_s <= h_s.x ; y_s <= tP_s ; sum x = n
t0 = time.time()
hs = highspy.Highs(); hs.setOptionValue("output_flag", False)
hs.setOptionValue("mip_rel_gap", 1e-4); hs.setOptionValue("time_limit", 300.0)
inf = highspy.kHighsInf
a = w / np.where(P > 0, P, 1) / (w * t).sum()
hs.addVars(N + S, np.zeros(N + S), np.r_[np.ones(N), t * P])
hs.changeColsCost(N + S, np.arange(N + S), np.r_[cost / cost.sum(), -a])  # minimize
hs.changeColsIntegrality(N, np.arange(N), np.full(N, highspy.HighsVarType.kInteger))
for s in range(S):
    nz = np.nonzero(h[s])[0]
    hs.addRow(-inf, 0.0, len(nz) + 1, np.r_[nz, N + s].astype(np.int32), np.r_[-h[s, nz], 1.0])
hs.addRow(n_target, n_target, N, np.arange(N, dtype=np.int32), np.ones(N))
hs.run()
xo = np.round(np.array(hs.getSolution().col_value[:N]))
summary("milp", xo, time.time() - t0)
print("MILP status:", hs.modelStatusToString(hs.getModelStatus()),
      "gap:", hs.getInfo().mip_gap)

coords = env.sdms.coords
np.savez_compressed(OUT / "static_toy_problem.npz", h=h, cost=cost, P=P, w=w, target=t,
                    n_target=n_target, row=coords[0], col=coords[1],
                    x_captain=x_captain, x_random=xr, x_greedy=xg, x_milp=xo,
                    species=np.array(env.sdms.names))
print("saved", OUT / "static_toy_problem.npz")
