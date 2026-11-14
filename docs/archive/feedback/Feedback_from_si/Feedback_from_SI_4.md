# Is your UAV coverage paper novel enough to publish? An honest assessment

**Short answer:** this isn't LARP. You have a real simulator, real bug-hunting and a credible corrected result. But the paper claims more novelty than it has, and one modelling issue would sink it with an informed reviewer. That same issue is also your best opportunity for a genuine contribution.

## What the web search shows

I searched for your main claims. Several close neighbours appeared in the last few months.

**Your "central invention" (bounds before learning) has a direct precedent.** Babarytskyi (arXiv, Oct 2026) states the same thesis almost word for word: "such ceilings should be computed before any learning experiment and quoted alongside every result." That paper also evaluates PPO against closed-form coverage ceilings for drone meshes [Source](https://arxiv.org/abs/2610.20823). You cite it as [38], which is right. But that makes it hard to keep calling the feasibility-certified framework "the central invention." Beyond the framing, the math is thin:
- The packing lower bound N ≥ K·P(A,R) is the textbook duality between packing and covering. It's a correct lemma, not a research result.
- "If the feasible set is empty, the binary metric is zero for every policy" is true by definition. A reviewer will see it as obvious.
- Your own paper admits the oracle ceiling is 1.000 at the evaluated configuration, so normalising by it changes nothing. A reviewer will say the framework is vacuous exactly where you use it.

**MAPPO for persistent UAV coverage with energy masks is a crowded area.** POGS-QMIX (Drones, Sept 2026) already does persistent multi-UAV coverage with:
- parameter-shared agents;
- a return-energy action mask applied in both exploration and bootstrapping;
- energy-stress tests;
- random and non-learning baselines;
- multi-seed confidence intervals [Source](https://www.mdpi.com/2504-446X/10/9/688).

PPO for connectivity-preserving swarm coverage with graph aggregation also exists [Source](https://arxiv.org/html/2605.17999v1).

**The honest-negative-result angle is taken too.** Pandhe (SSRN, Oct 2026) reports MAPPO losing to a frontier heuristic for multi-robot coverage. That paper reads much like your first draft: a corrected pseudoreplication error, non-deterministic evaluation, and a paired t-test at n = 3 [Source](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7556699). A controlled multi-seed MAPPO coverage study also exists [Source](https://www.mdpi.com/2673-2688/7/10/411).

**What does seem new** is the combination: K-redundant coverage of fixed IoT sensors, plus connectivity, charging contention and reserve recovery, all under one learned decentralised controller. Combinations count as contributions, but only if the experiments show the combination matters. Right now they mostly don't.

## Problems a reviewer will raise

### 1. Your setup isn't persistent (the biggest issue)

I computed this from your own Table VII, so check my arithmetic:
- Each pad adds 0.0002 × 30,000 J = 6 J per 0.2 s step, which is **30 W**. Your paper confirms this: a full charge takes 1000 s.
- An airborne UAV draws at least **55 W** (50 W hover + 5 W avionics), and about 80 W while moving.

In the long run, energy has to balance:

n_airborne × 55 W ≤ S × 30 W = 60 W

So **about one UAV can stay airborne indefinitely, but K-coverage needs eight.** Persistent K-coverage at your configuration is infeasible by roughly a factor of 8, under any policy.

Your 400 s episodes look fine only because the fleet spends its initial charge. Nine packs hold 270 kJ, and eight UAVs hovering for 400 s need about 176 kJ. At the 10,000-step target your report mentions (2000 s), you'd need about 880 kJ but have at most 270 + 120 = 390 kJ. That limits the fraction of time the region can be K-covered to **at most about 0.44**, whatever controller you use.

This is exactly the "infeasible configuration reported as a coverage number" failure your paper warns about, one level deeper. Your packing certificate checks space, and nothing checks energy.

### 2. The baseline is weak

Your strongest comparison is an untuned hand-written rule. At N = 8 = 4K, the nominal task is close to a static placement problem: fly to the 4K formation you constructed yourselves, then hold it. A classical controller would do exactly that:
- compute the oracle formation;
- assign UAVs to slots with the Hungarian algorithm;
- fly there along a connectivity-safe path;
- swap UAVs for charging with a relieve-before-leave rule.

I'd expect it to score near 1.0 on nominal. Without that baseline, "+0.028 over a heuristic" won't convince anyone.

### 3. The learner's observation and shaping encode the rule

The observation gives bearings to the nearest under-covered sensors, and the shaping rewards closing distance to the nearest deficit. That is the rule's logic built into the inputs and reward. That's fine, but frame the result as "learning on top of structure," not as learning beating hand design.

### 4. Planning breaks your decentralisation claim

Innovation 10 rolls a cloned global simulator forward over joint actions. That is centralised model-based search, and it contradicts the paper's decentralised-execution premise.

### 5. Writing and framing

The abstract retracts an earlier number. There are 11 contributions, and claim-audit counts appear in the abstract. An unpublished first preprint shouldn't retract anything; move the bug story to an appendix on lessons learned. Most venues want 6–10 pages with one clear story.

## Innovations to try, ranked by value per unit of compute

All of these run on a CPU.

### A. Energy-flow certificate and energy-aware ceiling (top priority, a few days, no training)

Extend your certificate from space to energy and pad throughput:
- **Steady-state bound:** n_air · P_air ≤ S · P_pad.
- **Finite-horizon bound:** airborne UAV-seconds ≤ (stored energy + S · P_pad · T) / P_air.
- **Energy-aware oracle:** a small linear program (a fluid relaxation) that maximises time-averaged CK subject to energy flow and pad capacity. It is cheap to solve and gives a ceiling below 1.0, so normalising by it finally means something.

This fixes the vacuous-ceiling criticism, catches the infeasibility in your own configuration, and is a natural extension of what you've built. Combining the spatial packing bound with energy-flow and pad-throughput bounds into one certificate for persistent K-coverage is something I didn't find in what I searched. Then choose a configuration that is persistently feasible with little slack, for example more pads, faster charging, battery swaps, or N above 4K. Small slack is what makes charging rotation matter.

### B. A strong classical baseline (2–3 days)

Build the formation + Hungarian assignment + relieve-before-leave rotation scheduler described above. It will probably beat MAPPO on nominal, and that's fine. It lets you ask the question a reviewer cares about: **where does learning add value over operations-research-style scheduling?** Your Fig. 1c already hints at an answer: the learner wins on low connectivity and failures, and loses on small batteries and spread starts.

### C. "Learning to spend redundancy" (the core research idea, 1–2 weeks)

With K = 2, redundancy doubles as an energy buffer. One of a sensor's two UAVs can leave to charge while the sensor stays 1-covered. Make that trade-off the research question:
- Report both ≥1-coverage and ≥K-coverage, plus maximum refresh time.
- Let the policy learn when to break redundancy, when to hand over, and when to charge early.
- Add the uncertainty that fixed schedules handle badly: noise in battery drain, random failure times, and wind-induced power variation. A fixed rotation schedule is optimal when everything is deterministic and fragile when it isn't. That is where a learned reactive policy can honestly win.

This gives the paper a sharp thesis instead of a general framework.

### D. Distil the planner into the policy (2–3 days)

Your planner gives +0.021 but uses centralised test-time compute. Collect the actions the planner picks and fine-tune the actor on them with behaviour cloning, or with PPO plus a KL term toward the planner (a lightweight expert-iteration scheme). If even half the gain survives in the decentralised policy, that is a clean, cheap and novel-enough result, and it removes the decentralisation problem.

### E. Zero-shot scaling (1 day, evaluation only)

Your ego-centric observation has a fixed size, so train at N = 8 and evaluate at N = 6–16 and on different field sizes, against the classical baseline. Results that generalise across fleet sizes are valued, and this costs almost no compute.

### What to drop

Attention, intrinsic motivation, action repeat and shuffling all measured null or negative. Keep them as one line in an appendix at most.

## A paper that could get accepted

One possible framing: *"Energy-Flow Feasibility and Learned Redundancy Management for Persistent K-Coverage UAV Networks."* It would have three contributions:
1. A spatial + energy + pad-throughput certificate with an LP ceiling, including the finding that a typical configuration is infeasible for persistent operation.
2. A strong scheduling baseline and the regimes where MARL beats it, with uncertainty and failures as the deciding factor.
3. Planner-distilled decentralised MAPPO.

Keep it to 8–10 pages, and move the audit and bug history to an appendix or the repository.

## How it would fare at each tier

| Venue tier | Current version | After A + B + C (+ D) |
|---|---|---|
| arXiv | Fine (no review) | Fine |
| Indian or regional IEEE conference (e.g. NCC, COMSNETS workshops, ANTS) | Borderline: overstated novelty, weak baseline | Good chance |
| Mid-tier IEEE wireless conference or workshop (VTC, ICC/Globecom workshops), AAMAS ALA workshop, MDPI *Drones* | Likely reject (the persistence flaw plus the weak baseline) | Realistic target |
| Top venues (NeurIPS, ICRA, TMC) | No | Unlikely without a much broader study |

Being undergraduates doesn't hold you back. The engineering discipline is above average, and your corrected protocol (frozen policies, held-out scenes, paired intervals) is better than much of the published UAV-RL work. What's missing is a sharp, defensible core claim. The energy-flow issue gives you one, and it would look much better coming from you than from a reviewer.