================================================================================
COMPREHENSIVE DIFF: OLD_MIDSEM_REPORT.pdf vs Mlawn-midsem-tex.pdf
================================================================================

OLD: 48393 chars, 8 sections
NEW: 191812 chars, 9 sections
Ratio: 4.0x larger

================================================================================
1. STRUCTURAL DIFFERENCES
================================================================================

OLD sections:
  - I. INTRODUCTION
  - II. LITERATURE SURVEY
  - III. SYSTEM MODEL
  - IV. PROPOSED ML ALGORITHM
  - V. COMPARISON MODELS
  - VI. PERFORMANCE METRICS
  - VII. EXPERIMENTAL DESIGN MATRIX
  - VIII. CONCLUSION

NEW sections:
  - I. INTRODUCTION
  - II. LITERATURE SURVEY
  - III. SYSTEM MODEL
  - IV. PROPOSED ML ALGORITHM
  - V. COMPARISON MODELS
  - VI. PERFORMANCE METRICS
  - VII. EXPERIMENTAL DESIGN MATRIX
  - VIII. RESULTS
  - IX. CONCLUSION

NEW only: {'VIII. RESULTS', 'IX. CONCLUSION'}
OLD only: {'VIII. CONCLUSION'}

================================================================================
2. ABSTRACT COMPARISON
================================================================================

OLD abstract (2241 chars):
Persistent and Fault-Tolerant UAV-IoT Coverage: A
Multi-Agent Reinforcement Learning Framework
for Joint Coverage, Connectivity, and Energy
Management
Himanshu Nagwanshi
Surya Prakash S
Harsh Varshney
Gaddam Viswaijeth
CS24BT055@iitdh.ac.in
CS23BT068@iitdh.ac.in
cs23bt004@iitdh.ac.in
CS23BT076@iitdh.ac.in
Department of Computer Science and Engineering
Indian Institute of Technology Dharwad, Dharwad, India
Abstract—UAV swarms can provide temporary wireless cover-
age for Internet-of-Things (IoT) deployments in areas where fixed
infrastructure is unavailable, damaged, or insufficient. Persistent
operation is considerably harder than one-shot deployment be-
cause coverage, inter-UAV connectivity, battery depletion, limited
charging resources, and UAV failures are tightly coupled. This
paper formulates the problem of maintaining at least K UAVs
over every ground sensor while preserving a connected swarm
and respecting finite energy and safety constraints. The resulting
decision process is modelled as a cooperative Decentralized Par-
tially Observable Markov Decision Process (Dec-POMDP). We
propose a Multi-Agent Proximal Policy Optimization (MAPPO)
controller under centralized training and decentralized execution
(CTDE). Each UAV executes a shared policy from local observa-
tions, while a centralized critic is used only during training. The
learned controller is combined with an explicit feasibility mask,
a reserve-UAV recovery mechanism, and a small infrastructure-
side charging 


NEW abstract (4145 chars):
Persistent and Fault-Tolerant UAV-IoT Coverage: A
Multi-Agent Reinforcement Learning Framework
for Joint Coverage, Connectivity, and Energy
Management
Himanshu Nagwanshi
Surya Prakash S
Harsh Varshney
Gaddam Viswaijeth
CS24BT055@iitdh.ac.in
CS23BT068@iitdh.ac.in
cs23bt004@iitdh.ac.in
CS23BT076@iitdh.ac.in
Department of Computer Science and Engineering
Indian Institute of Technology Dharwad, Dharwad, India
Abstract—UAV swarms can provide temporary wireless cover-
age for Internet-of-Things deployments where fixed infrastruc-
ture is unavailable, damaged or insufficient, but persistent opera-
tion couples coverage, inter-UAV connectivity, battery depletion,
charging contention and UAV failures. This paper formulates
the problem of maintaining at least K UAVs over every ground
sensor while preserving a connected swarm, and models it as a
cooperative Decentralized Partially Observable Markov Decision
Process (Dec-POMDP). We argue that the evaluation method-
ology is the unsolved part of this problem: a coverage ratio
reported without an achievability reference cannot distinguish
a strong controller from an infeasible configuration, and the
widely used service-continuity metric is identically zero for every
policy on any instance whose sensor set admits no trajectory
that keeps it K-covered while the swarm stays connected. We
therefore introduce a feasibility-certified evaluation framework
that derives a rigorous lower bound on the fleet size needed for
K-coverage of a bounded region, supplies a teleporting placement
oracle that certifies the instance is coverable — at the reported
configuration the ceiling is 1.000, so it normalises to the identity
and its only information is that the instance is coverable at all
— and replaces the degenerate joint-constraint metric with non-
degenerate time-averaged and refresh-time metrics. Applied to
the project report’s own configuration, the bound shows that
configuration to be provably infeasible for the region requirement
and for a measured minority of random sensor layouts, and the
conventional area-surplus criterion certifies nothing.
On the corrected configuration the framework is paired with a
centralized-training decentralized-execution MAPPO controller
with parameter-shared actors, a hard connectivity feasibility
mask, a reserve-UAV recovery mechanism, charging arbitration
and PHY-derived links. A hand-designed reactive rule outper-
forms the learned controller by 0.298 of persistent coverage (95%
interval [0.248,

================================================================================
3. SECTION-BY-SECTION LENGTH COMPARISON
================================================================================
  I. INTRODUCTION:
    OLD:   4340 chars
    NEW:  12331 chars
    Ratio: 2.84x
  II. LITERATURE SURVEY:
    OLD:   3343 chars
    NEW:  18047 chars
    Ratio: 5.40x
  III. SYSTEM MODEL:
    OLD:  18833 chars
    NEW:  45226 chars
    Ratio: 2.40x
  IV. PROPOSED ML ALGORITHM:
    OLD:   8353 chars
    NEW:  19707 chars
    Ratio: 2.36x
  V. COMPARISON MODELS:
    OLD:   3870 chars
    NEW:   3878 chars
    Ratio: 1.00x
  VI. PERFORMANCE METRICS:
    OLD:   2375 chars
    NEW:   8556 chars
    Ratio: 3.60x
  VII. EXPERIMENTAL DESIGN MATRIX:
    OLD:    168 chars
    NEW:    220 chars
    Ratio: 1.31x
  VIII. RESULTS: NEW ONLY, 60630 chars
  IX. CONCLUSION: NEW ONLY, 18875 chars

================================================================================
4. NEW SECTION VIII: RESULTS (full content)
================================================================================
All experiments use the corrected, feasible configuration
N = 8, K = 2, Rcov = 35 m on an 80 × 80 m field
(Section III-G), the clustered initial deployment and the 2000-
step episode of Section III-O. Every controller is evaluated on
the same scenes with the same seeds, and the rule baselines
and the learned controllers are trained on the same budget.
The teleporting placement oracle reaches CK = 1.000 on this
configuration; it is the ceiling against which every coverage
number below is meant to be read, and it is what makes
the comparison meaningful: the oracle establishes that the
configuration is coverable, so a controller that falls short of
it falls short as a controller and not because the instance was
infeasible.
Two things are true of this configuration, and we report
both. First, the task is not hard at the parameters the project
specifies: a deterministic reactive heuristic that assigns UAVs
to uncovered sensors reaches CK = 0.953 while maintaining
full connectivity. Second, the learned controller does not reach
that figure, and the arms below bound how much of the gap
each candidate explanation can account for. Three candidate
explanations can be tested with controlled arms — the content


TABLE XII
BASE COMPARISON ON THE CORRECTED CONFIGURATION. THE LEARNED
CONTROLLER IS TRAINED 8 TIMES AND ITS ROW IS THE MEAN OVER
THOSE 8 RUNS, WITH THE ± THE SEED-TO-SEED SPREAD; THE RULE
BASELINES ARE DETERMINISTIC AND CARRY NO SPREAD OF THEIR OWN.
“UNEXEC.” IS THE NUMBER OF SAMPLED ACTIONS THAT THE SAFETY
FILTER OR THE JOINT PROJECTION DID NOT EXECUTE, WHICH IS THE SIZE
OF THE GAP BETWEEN THE POLICY GRADIENT AND THE TRAJECTORY;
THE TWO LEARNED BASELINES’ ROWS CARRY DASHES IN THE LAST TWO
COLUMNS BECAUSE THEIR ARTEFACT RECORDS THE COVERAGE, THE
CONNECTIVITY AND THE SERVICE CONTINUITY BUT NOT THE FILTER’S
INTERVENTION COUNT OR THE ENERGY BUDGET. THE TWO LEARNED
BASELINES ARE IMPLEMENTATIONS OF THE METHOD FAMILIES OF
TABLE IX, NOT REPRODUCTIONS OF THE CITED PAPERS. THE TWO
LEARNED BASELINES ARE TRAINED FOR 20 EPISODES, A SMALLER
BUDGET THAN THE PROPOSED METHOD’S, AND THE CREDIT ARM OF
SECTION VIII-D RE-MEASURES THE SAME LOCAL-CRITIC LEARNER AT
THE BASE BUDGET.
Task metrics
Unexec. Energy
Model
CK
AG
SC
CovDef*
Fixed
0.372
1.000 0.000
–
249.80
176850
Greedy
0.784
0.965 0.066
–
5008.80 210802
Reactive
0.953
1.000 0.753
–
1508.80 182530
Reactive (local assignment)
0.972
1.000 0.778
–
1624.80 184721
Independent DQN
0.381 ± 0.069 0.996 0.000
0.619
–
–
Masked PPO (local critic)
0.625 ± 0.054 0.988 0.007
0.375
–
–
MAPPO (proposed)
0.674 ± 0.060 0.987 0.010
0.326
0.10
207532
MAPPO (argmax)
0.418 ± 0.062 0.993 0.000
0.582
0.03
183926
Oracle (ceiling)
1.000
1.000 1.000
0.000
–
0
* CovDef is the time-averaged coverage deficit.
of the observation, the energy model, and the credit assignment
of the team reward — and the arms are reported whichever
way they come out, with the resolution at which each was
measured.
Before those arms, one measurement of what the framework
is for, because it is the claim the framework makes first. On
the report’s original configuration, N = 5, K = 2, Rcov =
35 m, which Section III-G proves infeasible for the region
requirement, the same reactive heuristic reaches CK = 0.648
with connectivity availability 1.000 — over the 5 scenes of
that configuration — while the service-continuity metric is
0.000. A reader with no achievability reference would read that
coverage ratio as a reasonably good controller and the joint
metric as a controller that never achieves the requirement, and
neither reading would say whether the zero is the controller’s
fault or the instance’s. The teleporting oracle on the same
scenes reaches 0.990, so the twenty sensors themselves are
coverable and this shortfall is a controller shortfall; it is the
certificate that says the region is not coverable at all, and it is
the certificate that makes the reading decidable. That is what
the framework contributes here, and it is why the results below
are on a configuration the certificate admits.
The rule baselines separate sharply, and the ordering is
informative. The Fixed formation, which never moves, covers
0.372 of the sensor-steps: it is the floor that the initial
deployment alone provides, and it is also the controller that
never satisfies both invariants at once. The Greedy recharge
controller, which returns to a pad when its battery falls below a
threshold and otherwise holds station, reaches 0.784 by trading
coverage for energy. The Reactive heuristic, which moves the
swarm towards the uncovered sensors, reaches 0.953 with full
connectivity and a service continuity of 0.753, and it is the
strongest of the three classic rules.
The learned controller does not reach the heuristic. The
strongest controller in the table is the unprivileged reactive
rule, at 0.972, and the gap to it is 0.298 of persistent coverage;
the 95% interval on that gap, which is a one-sample interval
over the learned controller’s 8 training runs with the evalua-
tion scenes held fixed, is [0.248, 0.349]. The two sources of
variation are reported separately, as Section VI promises: the
seed-to-seed spread of the learned controller is 0.060 (standard
error 0.021) and the scene-to-scene spread of a fixed controller
is 0.098 (standard error 0.044), and the interval above is over
the first of the two. The scene-to-scene variation does not enter
this interval, because every controller is evaluated on the same
scenes and it therefore cancels in the difference — to the extent
that the difficulty of a scene enters every controller additively
and with the same size, which we state as an assumption
and whose per-scene scores are in the artefact, so that it is
checkable rather than merely asserted.
The privileged reactive heuristic is also the controller with
the most information, and the comparison should be read with
that in mind. It is given the exact set of under-covered sensors,
which corresponds to an unbounded broadcast of the coverage
state; the learned policy receives a fixed-size summary of it.
Part of the gap between them is therefore a difference of
information rather than of control. That is a caveat that is
easy to assert and easy to get wrong, so we measured it
rather than leaving it as one: a second version of the same
rule, with the motion and recharge logic unchanged but the
global coverage state removed — each UAV judges only the
sensors within twice the coverage radius of its own position,
and there is no assignment, so UAVs that want the same sensor
contend for it — is reported as Reactive (local assignment)
in Table XII. It reaches 0.972 with connectivity availability
1.000 and a service continuity of 0.778, against the privileged
version’s 0.953, 1.000 and 0.753. The privileged version is in
fact slightly WORSE than the unprivileged one (-0.019), so
the global coverage state is not what gives the rule its edge —
the global round-robin assignment makes the UAVs contend
for sensors, and the local rule does better — and the gap to
the learned controller is therefore not an information artefact
at all.
The connectivity invariant deserves a sentence, because the
reported availability is below 1.000 and the filter is claimed
to guarantee connectivity. The guarantee is about actions:
the mask evaluates the prospective graph for every candidate
action, and the joint projection restores the previous config-
uration when a set of individually admissible actions would
jointly disconnect the swarm. The step-by-step accounting in
the artefact tests that claim, and it holds: of the 4 transitions
into a disconnected graph, 4 follow a UAV leaving the active
set, 0 follow a teleport and 0 are unexplained — each of them
is a UAV whose pack emptied away from a charging pad,
and none follows a move, so the projection’s guarantee is


not violated by any executed move, and the availability below
1.000 is the price of a UAV leaving rather than a hole in the
filter. The other source is the recovery mechanism: when a
UAV’s pack empties away from a pad it is removed from the
active set, and the swarm can be left disconnected until the
reserve UAV re-seats it at a charging pad and it flies back. The
availability below 1.000 is that mechanism’s signature, and it is
the price of a UAV leaving the active set with no re-seating: the
reserve was never activated in the base configuration, where
no failure is injected. The scope of the probe is narrow and
we state it: it drives the swarm with every stored policy (the
learned controller), and it establishes that the projection leaves
no hole over the moves it took; it does not speak for a policy
trained with a different observation or a different budget.
The mission-relevant quantity is the joint invariant, and
it separates the two controllers far more sharply than the
coverage does. The reactive heuristic satisfies the coverage re-
quirement and the connectivity requirement simultaneously in
0.753 of the mission, against 0.010 for the learned controller.
The coverage ratio is a weak proxy for that: a controller can
hold a high per-sensor coverage while never covering every
sensor at the same instant, which is what the learned controller
does, and the service continuity metric is therefore the one that
distinguishes these two controllers most sharply, even though
we criticise it for a different reason elsewhere.
It is worth separating the two sources of variation in the
headline number, because they behave differently. Across the
8 training runs of the learned controller the coverage varies
by 0.060 (the standard error of the mean is 0.021); across the
5 evaluation scenes it varies by 0.098 (the standard error of
the mean over the scenes is 0.044). The scene component is
common to every controller in the comparison, because they
are all evaluated on the same scenes, and it therefore cancels
in every difference this paper reports; the seed component
does not, and it is the seed component that the training-seed
spread measures. A reader comparing two controllers should
read the seed component as the uncertainty of the comparison
and the scene component as a property of the configuration.
Two caveats belong with these numbers. The spread quoted for
a learned controller is the spread of its per-seed means, and
each per-seed mean averages five evaluation scenes of a single
rollout, so it contains the rollout-to-rollout variation of a policy
that samples at every step and not only the variation between
training runs. And the cancellation of the scene component in
a difference is an assumption rather than an identity: it holds
if the difficulty of a scene enters every controller additively
and with the same size, and it fails if a scene is hard for one
controller and easy for the other. The per-scene scores are in
the artefact, so the assumption is checkable rather than merely
asserted.
The question that this comparison invites — whether more
training would have closed the gap — deserves an answer
rather than an assumption, because a hand-designed rule
embeds a human’s solution while the learner receives a fixed
budget. Figure 8 plots the per-episode coverage of every
training run on the training scene, against the reference rule;
the first training run’s per-episode coverage, measured on the
training scene, runs from 0.594 to 0.805 over its 25 episodes,
and its mean over the first five episodes (0.669) is the same
as its mean over the last five (0.696): that is one run, and
it is not evidence that the curve has flattened, because the
increments between the budgets the sweep below covers are
still increasing. The best single episode, 0.805, is on a training
scene and was never evaluated off it; the final policy of that
run scores 0.761 on the unseen scenes, so the training-scene
figure is not an estimate of the deployed performance. Two
things about that curve limit what it can support, and both
are stated rather than assumed: it is a single run, so it carries
no seed-to-seed spread and no interval, and it is measured
on the scene the policy trains on. The budget is therefore
bounded rather than eliminated: at this configuration the curve
on the training scene is flat over the budget we can afford, and
we do not claim that a larger budget would not change the
picture. The sweep behind that statement trains independent
runs at each of three budgets rather than reading one run’s
curve at different points, so it compares budgets and does
not restate the curve: 8 episodes: 0.588, 16 episodes: 0.624,
25 episodes: 0.674, and the coverage moves by +0.086 over
the range the sweep covers, which is about 29% of the gap
of 0.298, and the increments between successive budgets are
+0.036, +0.050; the last of them, +0.050, is 4.8 standard
errors from zero (the standard error of the difference is 0.010,
paired over the same 8 training seeds), so the coverage does
keep rising with the budget over the range the sweep covers.
The two measurements differ in what they can support, and
the difference is worth stating rather than smoothing over:
the curve flattens on the scene the policy trains on, while
the sweep’s last increment IS resolved against zero, so the
coverage is still rising at the longest budget we ran. A
flattening training curve is therefore not evidence that the
budget has stopped mattering, and we do not use it as such;
we do not extrapolate the sweep past the budgets it covers, and
we do not claim that a larger budget would close the gap. The
sweep is not the end of the question, and the arm that settles it
is the paired one: the paired comparison over the same training
seeds does resolve a real gain, +0.086 with a 95% interval of
[+0.036, +0.135], and that interval’s upper limit of 0.135 is
below the gap of 0.298: more training does help, and over
the 8–25 episode range the sweep covers the whole of its
measured effect is too small to account for the shortfall, so the
budget is excluded as the explanation of the shortfall OVER
THAT RANGE. Two things are not claimed. The increments
are increasing (+0.036, +0.050) and the last of them is still
resolved against zero, so the sweep has not saturated; and an
interval on a measured range is a bound on that range and not
on the budgets beyond it, so a larger budget is not excluded
by this measurement. Settling that would need the sweep to
run until the paired increment is unresolved, which this paper
does not do.
Figure 7 is the sweep: the coverage at the three budgets
with the seed-to-seed spread, the strongest rule for reference,
and the size of the gap between them.


8
16
25
0.5
0.6
0.7
0.8
0.9
gap 0.298
the unprivileged reactive rule (0.953)
training over 8–25 episodes: ∆= +0.086
95% CI [+0.036, +0.135] — 29% of the gap
bars: ±1 s.d. over the 8 training seeds
training episodes
persistent coverage
the strongest rule
the learned controller
Fig. 7. The training-budget sweep. The learned controller is trained on the
same eight seeds at 8, 16 and 25 episodes and evaluated on the same scenes;
the bars are ±1 standard deviation over the training seeds. The paired gain
over the sweep’s range is +0.086 (95% interval [+0.036, +0.135]), about
29% of the gap, whose upper limit is below the gap of 0.298: more training
does help, and over the range the sweep covers the whole of its effect is too
small to account for the shortfall.
The learned controller does not reach the heuristic, and the
two learned baselines locate the reason. The Masked PPO with
a local critic differs from the proposed method in exactly one
respect: each agent has its own actor and its own critic on
its own observation, instead of a parameter-shared actor with
a centralised critic. It reaches 0.625 at a 20-episode budget,
against the proposed method’s 0.674 at the base budget, a
difference of −0.049 that is small beside the seed-to-seed
spread of the learner, and Section VIII-D re-measures that
same local-critic learner at the base budget, where it reaches
0.639, and tests the comparison properly, on paired training
seeds. The Independent DQN arm, at 0.381, is the value-based
point of comparison and shows what the task costs a controller
that does not use the framework’s mechanisms at all. Vanilla
MAPPO, which removes the framework’s observation terms,
reward shaping, charging arbitration, reserve-UAV mechanism
and action mask, shows how much of the learned method’s
behaviour survives without them.
a) On the evaluation protocol, which is not neutral.: The
rule baselines are deterministic, so they have no sampling step;
the learned policy is evaluated by sampling, because Eq. (30)
specifies a sampled policy. The sampling is seeded: the stream
is derived from the evaluation seed alone, so an evaluation is
a function of (policy, scene), every controller sees the same
stream on the same scene, and the numbers in this section can
be recomputed from the stored policies.
Two further properties of the measurement are pinned rather
than left to the machine, because both of them change the
result. The floating-point kernels differ between the CPU and
the GPU, so the same seed trained on the two gives different
weights — the difference is small, and it compounds through
the updates — and the order of the reductions depends on
the thread count, so it changes them too. A device chosen by
how much GPU memory happened to be free would therefore
make a training run a function of the machine’s momentary
load rather than of its seed, and a variant and the arm it is
compared against could end up on different devices, which is
not a paired comparison at all. The device and the thread count
are consequently part of the protocol, every artefact records
the device it was produced on, and the audit checks that a
training run is a function of its seed.
We report the deterministic version of the same actor as
well, and the difference is large: the argmax policy reaches
0.418 against 0.674 for the sampled one, although it travels
a comparable distance (5044 m against 9834 m), so it is
not a static controller — it is a different and worse one,
and the difference between them is the contribution of the
exploration that the reward does not price. The comparison
with the deterministic baselines is therefore not like-for-like
in either direction: sampling makes the learned controller take
risks it would not take deterministically, and it is scored on
the mean of a distribution of trajectories rather than on one of
them. Reporting both rows is the point.
One further number in the table is worth stating, because
it disposes of a concern that the framework raises. The safety
filter and the joint projection together left 0.10 of the 16 000
actions sampled in an episode unexecuted — one action in
160000 — so the policy gradient is very nearly consistent with
the trajectory that was actually taken; the ”the executed action
is not the chosen action” problem, which is real in masked
reinforcement learning, is not what limits this controller.
The learned controller also burns more energy than the
heuristic (207532 J against 182530 J over the same episode)
while stranding more UAVs (0.6 against 0.4 per episode),
which is the cost of moving deliberately rather than the
price of wandering. Its connectivity availability is below 1.000
because UAVs leave the active set when a pack empties away
from a pad, and not because the safety filter leaks: over
2000 steps driven by the learned controller the graph was
disconnected on no step in which the active set was unchanged
(Section VIII-C).
A. What the local observation must contain
The observation of Eq. (4) is the interface between the
framework’s communication assumption and the shared policy,
and the claim that parameter sharing requires the observation
to break the permutation symmetry is testable. Table XIII
compares three observations under identical seeds, budget and
evaluation scenes: the local observation alone; that observation
plus the one-hot agent identity; and that plus the broadcast
coverage-map summary and the bearing to the charging pad,
which is the configuration the paper proposes.
The three arms are cumulative, and arm C is the proposed
configuration; the component ablation of the next section
isolates the three observation terms individually. Arm A is
the observation of Eq. (4) as originally written.
Arm A has the property that the shared-actor symmetry
collapse predicts. The deterministic policy nearly collapses to


1
5
10
15
20
25
0.2
0.4
0.6
0.8
training episode
persistent coverage
the eight training runs
the unprivileged rule
Fig. 8.
The per-episode persistent coverage of each training run of the
proposed controller, on the training scene, against the reactive heuristic’s
coverage on the evaluation scenes. The curves have flattened over the budget
the experiments use, but only on the scene the policy trains on; the budget
sweep below is what says whether that carries over to unseen scenes, and it
does not resolve it. The per-episode values are on the training scene and are
therefore not the deployed performance.
TABLE XIII
WHAT THE LOCAL OBSERVATION MUST CONTAIN. “DISTINCT” IS THE
NUMBER OF DISTINCT ACTIONS THE DETERMINISTIC (ARGMAX) POLICY
SELECTS ACROSS THE EIGHT UAVS, AND “SPREAD” IS THE MEAN
DISTANCE OF A UAV FROM THE SWARM CENTROID.
Task metrics
Distinct Spread (m)
Observation
CK
AG
SC
A local only
0.640 ± 0.080 0.986 0.009 1.84 / 8
11.3
B + identity
0.648 ± 0.092 0.993 0.007 2.43 / 8
11.8
C + identity + map 0.674 ± 0.060 0.987 0.010 1.85 / 8
11.0
a single action — the “Distinct” column counts 1.84 distinct
actions out of eight — and the swarm’s spread is 11.3 m,
which is the radius of the initial cluster rather than the extent
of a deployment. This is the failure that Foerster et al.’s
condition (ii) is about: with an observation that does not break
the permutation symmetry, a parameter-shared network is a
single function of the observation, so two agents in symmetric
states must receive the same action distribution, and no amount
of training can change that. The consequence is measurable
rather than theoretical, and the diagnostic that exposes it is a
count of distinct actions, which costs nothing and which the
raw coverage number does not make visible.
Arm B adds the one-hot identity, and the condition does
what it says about specialisation: the number of distinct actions
rises from 1.84 to 2.43 out of eight, and the swarm disperses
rather than standing still. Its effect on the coverage, paired
over the shared training seeds, is +0.008 with a 95% interval
of [−0.121, +0.137], so we do not claim that the identity buys
coverage at this budget: what it buys is the ability to specialise,
which the distinct-action count measures directly and which
the coverage does not.
Arm C adds the broadcast coverage-map summary and the
pad bearing, and it is the configuration the paper proposes. The
spread rises to 11.0 m — the swarm moves further — while
the distinct-action count falls to 1.85, so the policy moves
more but decides more uniformly. That is the signature of a
policy that is following the map rather than dividing the work,
and the paired effect on the coverage is +0.034 (95% interval
[−0.033, +0.102]).
So the observation terms change what the policy does —
how far it travels, and whether it can specialise at all — much
more clearly than they change the coverage it achieves. That
is worth stating, because the alternative reading of the same
table is that the observation does not matter, and it is not
what the data support. A coverage map tells a controller where
the work is; it does not tell it which UAV should do it, and
turning a location into an assignment requires per-agent credit,
which a shared team reward does not supply. The map makes
the deficiency visible, and therefore actionable-looking, and a
policy without the credit to act on it chases.
The arms share their training seeds, so the comparisons
are paired: adding the agent identity (+0.008, 95% interval
[-0.121, +0.137], an upper limit below the gap of 0.298); the
full observation of the proposed configuration (+0.034, 95%
interval [-0.033, +0.102], an upper limit below the gap of
0.298). Each upper limit is below the gap of 0.298 to the
unprivileged reactive rule, so the content of the observation
is not what accounts for the gap; what the observation terms
buy is the ability to specialise at all, and the identity raises
the number of distinct actions a policy takes from 1.84 to 2.43
out of eight, which is the specialisation the arms measure.
The resolution of the summary makes no difference to the
coverage: G = 0: 0.640, G = 4: 0.643, G = 8: 0.651,
and the largest of the differences is 0.011, inside the seed-to-
seed spread of the learner (0.060). What the summary does
change is the swarm’s behaviour: the spread grows, from
9.0 m without it to 10.6 m and 10.3 m with it, because a
policy that follows the deficit spreads the swarm out instead
of keeping it together. The map is therefore neither what makes
the controller work nor what stops it working: it is a channel
the policy uses to move differently, and the difference it makes
is visible in the trajectory rather than in the score.
The observation terms are priced individually in Table XIII.
The reason is easy to see in retrospect. Without a direction to
the charger a UAV cannot come home, so the swarm drains
its packs in the field; and a swarm that has drained its packs
is not a swarm that can be asked to cover anything.
B. Energy management, and the reward that was missing it
The step-level diagnostic of the learned policy produced a
surprising number: under the previous energy rule the policy
stranded 5.7 of the eight UAVs per episode, while the reactive
heuristic stranded 0.4. A stranded UAV has an empty pack
away from a charging pad; it can no longer fly, it leaves the
swarm, and it stops covering. The obvious reading is that the
controller has failed at energy management, and the obvious
fix is a reward term that prices the consequence of an empty
pack. Table XIV tests that reading with four controlled arms:


TABLE XIV
THE ENERGY-MANAGEMENT DIAGNOSIS. “STRANDED” IS THE MEAN
NUMBER OF UAVS THAT RUN OUT OF ENERGY AWAY FROM A PAD PER
EPISODE, AND “RETURNS” THE MEAN NUMBER OF RETURN-TO-CHARGE
TRANSITIONS.
Task metrics
Stranded Returns
Variant
CK
AG
SC
A
0.674 0.987 0.010
0.4
543.3
B
0.684 1.000 0.029
0.0
0.0
C
0.656 0.989 0.002
0.8
509.4
D
0.624 0.957 0.004
5.7
105.3
* A: the proposed configuration; B: + a pack that cannot run out; C: without the threshold
term; D: with the previous energy rule.
−0.2
0
0.2
0.4
obs. B: identity
obs. C: full obs.
energy B: no constraint
energy C: no threshold
energy D: prev. rule
credit: per-agent critic
+0.008
+0.034
+0.010
−0.018
−0.050
−0.035
difference in persistent coverage
below the gap
past the gap
paired mean
the gap 0.298
gap 95% CI
Fig. 9. The controlled arms against the gap (paired 95% intervals; the dashed
line is the gap of 0.298).
the same policy with a pack that cannot run out, the same
policy without the threshold-violation term of Table V, and
the same policy under the earlier energy rule of the safety
filter.
Figure 9 draws every controlled arm’s interval against the
gap it would have to explain, with the gap’s own interval as a
band: it is the picture of the argument the tables below make
in numbers.
The first version of this section told a different story, and
the difference is worth recording, because it is the clearest
example in this work of a diagnostic leading to a repair rather
than to a conclusion. The step-level diagnostic of the learned
policy produced an alarming number: with the previous energy
rule, the policy stranded 5.7 of the eight UAVs per episode,
while the reactive rules stranded 0.4. A stranded UAV has an
empty pack away from a charging pad; it can no longer fly, it
leaves the swarm, and it stops covering. The obvious reading
was that the controller had failed at energy management, and
the obvious fix was a reward term that prices the consequence
of an empty pack.
What the diagnostic actually found was a defect in the safety
filter rather than a property of the policy. The mask’s energy
test admitted a departure with a flat battery, so a UAV could
fly until its pack was empty away from a pad; the correction
is to require a UAV to retain, after the move, the energy to
reach a charging pad plus the reserve margin. The stranding
falls from 5.7 UAVs per episode to 0.4, and the return-to-
charge transitions rise from 105 to 543 per episode, because
the UAVs now come home instead of dying in the field. The
coverage the repair adds is +0.050 on the same training seeds
(95% interval [-0.015, +0.115], which includes zero), so the
repair’s effect on the coverage is not resolved by this arm. The
defect was therefore real and the repair was correct, and the
repair is already part of the proposed configuration: it is not
a candidate explanation of the residual gap, because the gap
is measured against a controller that has the repair in it. What
the repair does show is that the safety filter, not the policy,
was limiting the earlier configuration, and that a defect of this
kind is worth a third of the total gap — which is why the
claim audit checks the filters and not only the rewards.
It is worth being explicit about what this arm does and
does not show. It is not a statement that the energy constraint
is inactive: the two rules differ by 5.2 stranded UAVs per
episode and by 438 return-to-charge transitions, so the test
is doing substantial work and the swarm’s energy behaviour
differs markedly between them. Nor is it a statement that the
energy mechanism is what the learned controller gets wrong:
the comparison is between two versions of the same controller,
and it says what the filter is worth, not what the learner is
missing. A difference of this width is also a statement about
the resolution of the arm and not about the component, and
we report that resolution with the interval.
The energy model is not what accounts for the gap, and
Table XIV says so. The three interventions are paired with
the proposed configuration – they share its training seeds –
so each one is reported as an interval rather than as a point,
and each interval’s upper limit is below the gap of 0.298 to
the unprivileged reactive rule: removing the energy constraint
(+0.010, 95% interval [-0.056, +0.075], an upper limit below
the gap of 0.298); removing the threshold term (-0.018, 95%
interval [-0.047, +0.011], an upper limit below the gap of
0.298); the previous energy rule (-0.050, 95% interval [-0.115,
+0.015], an upper limit below the gap of 0.298). The energy
model is therefore not what accounts for the gap, and the paper
does not claim that it is.
That is the sequence the framework is for. A coverage
comparison on its own would have reported that the learned
controller mismanages energy, and a reward re-weighting
would have been the wrong repair. The controlled arms are
what showed that the energy model was not the problem, and
the defect they exposed in the filter was the actual problem.
By the end of that sequence the energy explanation had
been removed from the list, and what remained — the credit
assignment of a shared team reward — was neither supported
nor refuted by it.
C. Component ablation
Table XV removes, one component at a time, from the full
configuration: each variant is trained on the same configuration


TABLE XV
COMPONENT ABLATION ON THE FEASIBLE BASE CONFIGURATION. EVERY
VARIANT IS TRAINED ON THE SAME CONFIGURATION WITH THE SAME
BUDGET AND FROM THE SAME TRAINING SEEDS, AND DIFFERS FROM THE
FULL CONFIGURATION IN EXACTLY ONE COMPONENT — THE LAST ROW
EXCEPTED, WHICH REMOVES THE FRAMEWORK’S MECHANISMS
TOGETHER. THE ± IS THE SEED-TO-SEED SPREAD OF THE TRAINING
RUNS, AND ∆CK IS THE PAIRED DIFFERENCE FROM THE FULL
CONFIGURATION, MEASURED ON THE SAME TRAINING RUNS: A POSITIVE
NUMBER IS WHAT THE COMPONENT IS WORTH.
Task metrics
Stranded
∆CK
Variant
CK
AG
SC
CovDef
Full (proposed)
0.674 ± 0.060 0.987 0.010
0.326
0.6
+0.000
no-criticality term
0.649 ± 0.055 0.987 0.005
0.351
0.6
+0.025
no-degraded-service term 0.664 ± 0.050 0.988 0.007
0.336
0.5
+0.010
no-energy-cost term
0.670 ± 0.045 0.982 0.012
0.330
0.5
+0.004
no-under-coverage term
0.577 ± 0.128 0.998 0.006
0.423
1.0
+0.097
no-reserve UAV
0.674 ± 0.060 0.987 0.010
0.326
0.6
+0.000
no-charging arbitration
0.661 ± 0.050 0.985 0.006
0.339
0.6
+0.013
with the same budget and from the same training seeds, and
differs from the full configuration in exactly one component.
Every variant is trained on the same configuration with the
same budget and from the same set of 8 training seeds, and
differs from the full configuration in exactly one component,
so a difference is attributable to that component. The budget is
the base comparison’s (25 episodes), and the full configuration
of this table is the first 8 of the base comparison’s training runs
— the same policies, not a cheaper experiment — so the two
tables describe the same learner. Because the variants share
the training seeds, the comparison is paired: a difference is
measured on the same training runs, and what is reported is a
confidence interval for that difference rather than a comparison
of two numbers against a threshold. A threshold would be the
wrong instrument here, and it is worth saying why, because
the older version of this table used one. A rule that calls a
difference “measurable” when it exceeds some other number
— the learner’s own seed-to-seed spread, say — has a false-
positive rate that depends on the spread of that other number,
and it buys nothing in power: at three training seeds it would
flag roughly one null component in three, while still being
unable to detect a true effect of the size it flags. The arms
below are measured at 8 training seeds, and the paired interval
is what makes the number they report mean something. The
paired interval does not have that failure mode, and it also
reports the resolution of the measurement, which is the number
a reader actually needs. The paired comparison, in which
every variant is trained on the same training seeds as the
full configuration, separates the components into two groups.
The differences below are the FULL configuration minus the
variant, so a positive number is what the component is worth.
The components whose 95% confidence interval for the paired
difference excludes zero are the under-coverage term (+0.097,
95% CI [+0.020, +0.174]); every other component’s interval
includes zero, and the worst resolution anywhere in the table
is 0.042 of persistent coverage, which is the WIDEST arm’s
resolution: the resolution is per-arm, and each arm’s own
interval is in the table The table is a family of 6 paired tests and
the intervals above are unadjusted, so the correction is stated:
with a Bonferroni correction over the table the threshold is
α = 0.0083, and no component’s paired p-value survives it,
so every component above is reported as suggestive rather than
resolved.
What the intervals do and do not say is worth stating
precisely, because a null result of this width is a statement
about the resolution of the measurement and not about the
component. The widest of the arms resolves no effect smaller
than about 0.042 of persistent coverage, at this training budget
and with this number of training seeds, so the resolution is
per-arm and a reader who wants a particular component’s
resolution must read it off that component’s interval. The
intervals are per-arm and are not adjusted for the number of
arms, so a reader who wants a family-wise statement should
treat the set of arms as one test with several comparisons
rather than as several independent tests. The intervals do not
show that a component is unnecessary. A component can be
redundant with another, in which case removing either one
alone costs nothing while removing both costs a great deal; and
a component that matters only at a larger budget is invisible
at this one. The budget sweep above speaks to the second
case for the full configuration: the coverage moves by +0.086
over the range the sweep covers, which is about 29% of the
gap of 0.298, and the increments between successive budgets
are +0.036, +0.050; the last of them, +0.050, is 4.8 standard
errors from zero (the standard error of the difference is 0.010,
paired over the same 8 training seeds), so the coverage does
keep rising with the budget over the range the sweep covers;
and the paired arm puts a bound on it, the paired comparison
over the same training seeds does resolve a real gain, +0.086
with a 95% interval of [+0.036, +0.135], and that interval’s
upper limit of 0.135 is below the gap of 0.298: more training
does help, and over the 8–25 episode range the sweep covers
the whole of its measured effect is too small to account for
the shortfall, so the budget is excluded as the explanation
of the shortfall OVER THAT RANGE. Two things are not
claimed. The increments are increasing (+0.036, +0.050) and
the last of them is still resolved against zero, so the sweep
has not saturated; and an interval on a measured range is a
bound on that range and not on the budgets beyond it, so a
larger budget is not excluded by this measurement. Settling
that would need the sweep to run until the paired increment is
unresolved, which this paper does not do. The arms here are
each measured at the single budget the base comparison uses,
so for the individual components we do not claim budget-
independence, and we do not extrapolate the sweep past the
budgets it covers, and we do not claim that a larger budget
would close the gap.
Two of the null results are explained rather than merely
reported. The articulation-point term makes no measurable
difference because the safety filter already forbids any move
that would create an articulation point, so on an executed
trajectory the quantity it measures is nearly constant and
the term has almost no variance to act on: the constraint is
enforced by the filter, and the reward term is a readout of it.


TABLE XVI
COMPONENT ABLATION ON THE S8 COMBINED-STRESS SCENARIO (A
FAILURE AT STEP 500, ONE CHARGING PAD, B = 15 KJ, Rcomm = 30 M,
Rcov = 30 M). THE VARIANTS ARE TRAINED FOR 6 EPISODES, A
QUARTER OF THE BASE COMPARISON’S BUDGET, WHICH IS WHY THE
FULL CONFIGURATION SCORES FAR LOWER HERE THAN IT DOES IN THE
SCENARIO MATRIX.
Task metrics
Stranded
∆CK
Variant
CK
AG
SC
CovDef
Full (proposed)
0.303 ± 0.105 0.808 0.000
0.697
5.0
+0.000
no-criticality term
0.303 ± 0.103 0.808 0.000
0.697
5.1
-0.000
no-degraded-service term 0.293 ± 0.092 0.800 0.000
0.707
5.2
+0.010
no-energy-cost term
0.303 ± 0.105 0.808 0.000
0.697
5.0
+0.000
no-under-coverage term
0.313 ± 0.117 0.806 0.000
0.687
5.0
-0.010
no-reserve UAV
0.493 ± 0.021 0.981 0.000
0.507
2.1
-0.190
no-charging arbitration
0.297 ± 0.098 0.800 0.000
0.703
5.2
+0.006
no-action mask
0.253 ± 0.067 0.829 0.000
0.747
5.5
+0.050
no agent identity
0.299 ± 0.087 0.803 0.000
0.701
5.0
+0.004
no coverage map
0.319 ± 0.120 0.821 0.000
0.681
4.8
-0.016
no pad bearing
0.295 ± 0.091 0.803 0.000
0.705
5.2
+0.007
Vanilla MAPPO
0.484 ± 0.036 0.996 0.000
0.516
2.0
-0.181
The degraded-service term is close to inert for the same reason,
since the filter keeps the graph connected whenever the active
set is unchanged. In other words, the terms that look as though
they should matter most are the ones the hard constraints have
already discharged, and the terms that do matter are the ones
the filter cannot enforce: who covers what, and how the energy
is spent.
Table XVI repeats the ablation on the combined-stress sce-
nario, where the reserve and arbitration mechanisms actually
fire. The ordering of the components cannot be read off this
table: the components whose paired interval excludes zero
are the reserve UAV (-0.190, 95% interval [-0.277, -0.104]),
the action mask (+0.050, 95% interval [+0.006, +0.094]), the
whole design (-0.181, 95% interval [-0.255, -0.107]); and the
components whose interval includes zero – the criticality term
(-0.000, 95% interval [-0.011, +0.010]), the degraded-service
term (+0.010, 95% interval [-0.035, +0.055]), the energy-
cost term (+0.000, 95% interval [-0.000, +0.000]), the under-
coverage term (-0.010, 95% interval [-0.060, +0.039]), the
charging arbitration (+0.006, 95% interval [-0.012, +0.024]),
the agent identity (+0.004, 95% interval [-0.117, +0.125]),
the coverage map (-0.016, 95% interval [-0.150, +0.118]), the
pad bearing (+0.007, 95% interval [-0.121, +0.136]) – are not
separated by this table at all. The differences below are the
FULL configuration minus the variant, so a negative number is
what the component is worth on this scenario. The differences
between the variants are of the same order as the width of the
intervals, so the table reports what the stress scenario does to
the swarm and not which component matters. The framework’s
recovery mechanism, which re-seats an exhausted UAV at a
charging pad, is a plausible mechanism for the behaviour of
the stress scenario — a re-seated UAV is out of communication
range of the swarm until it flies back — but this table does
not resolve it, and we do not claim it.
TABLE XVII
THE CHEAPEST TEST OF THE CREDIT-ASSIGNMENT HYPOTHESIS. THE
TWO ARMS DIFFER IN THE LEARNER THAT PRODUCES THE ADVANTAGE: A
PARAMETER-SHARED ACTOR WITH A CENTRALISED CRITIC, OR A
PER-AGENT ACTOR WITH A PER-AGENT LOCAL CRITIC. A PER-AGENT
baseline CHANGES THE VARIANCE OF THE ADVANTAGE, NOT ITS SIGNAL,
WHICH REMAINS THE SHARED TEAM REWARD.
Task metrics
Energy (J)
Learner
CK
AG
SC
CovIntegral
A
0.674 ± 0.060 0.987 0.010
0.326
–
B
0.639 ± 0.051 0.983 0.005
0.361
–
* Energy is not recorded in this artefact.
D. The credit assignment, and the cheapest test of it
The diagnosis of Sections VIII-A and VIII-B points at one
mechanism: with a shared team reward every agent receives
the same advantage, so the gradient cannot distinguish an agent
whose action helped from one whose action was irrelevant.
The literature calls this the credit-assignment problem, and
the remedies are known: the counterfactual advantage of
COMA, the difference-based estimator of DAE, the per-agent
value iteration of GPAE, and the advantage decomposition of
HAPPO/HATRPO [22]–[25]. None of them has been evaluated
on a persistent-coverage task, and the question of whether the
credit assignment is what limits a parameter-shared controller
in that setting appears to be open.
Table XVII is the cheapest test of it that does not require
implementing a new algorithm, and it is worth being exact
about what it does and does not change. The two arms differ in
the learner that produces the advantage. Arm A is the proposed
method: a parameter-shared actor with a centralised critic,
so every agent receives the same broadcast team advantage.
Arm B keeps the same simulator, the same observation, the
same action mask, the same team reward and the same episode
budget, and replaces the learner with a per-agent actor and a
per-agent local critic. Nothing else changes.
What that does and does not change is worth stating plainly,
because it bounds the conclusion. With a team reward rt
broadcast to every agent, the advantage is rt +γV (o′)−V (o).
Giving each agent its own value function re-centres and re-
scales that expression per agent, so the advantage is no longer
a single shared number, but it cannot decompose it, because
the advantage’s dependence on the other agents enters only
through the aggregate reward and through the observation,
which are symmetric in the other agents. Redistribution of
credit requires a per-agent reward, a joint-action critic, or a
counterfactual baseline.
The per-agent arm reaches 0.639 against 0.674 for the
shared one, a difference of −0.035 in persistent coverage.
Arm A is the proposed method on the first 8 of the base
comparison’s training runs — the same policies, not a cheaper
experiment — so the two rows of the first table and this table
describe the same learner. The two arms share their training
seeds, so the comparison is paired, and the 95% interval on the
paired difference is [−0.079, +0.009] over 8 training runs: the
difference is not resolved by this arm: the interval is [-0.079,


TABLE XVIII
SCENARIO MATRIX. EACH ROW IS THE MEAN OVER THE VARIANTS OF
THAT SCENARIO; M IS THE PROPOSED CONTROLLER, R THE REACTIVE
HEURISTIC AND RL THE SAME RULE WITHOUT ITS GLOBAL ACCESS TO
THE COVERAGE STATE, WHICH IS THE STRONGER OF THE TWO RULES ON
THE BASE CONFIGURATION.
CK
SC
ID Variable
M
R
RL
M
R
RL
S1 sensor density
0.623 0.892 0.965 0.016 0.263 0.730
S2 fleet size N
0.494 0.662 0.756 0.003 0.241 0.482
S3 battery capacity
0.561 0.883 0.947 0.004 0.363 0.706
S4 charging pads S
0.599 0.890 0.931 0.013 0.333 0.447
S5 Rcomm
0.562 0.894 0.888 0.002 0.478 0.723
S6 Rcov
0.585 0.795 0.892 0.054 0.483 0.461
S7 failure time
0.596 0.905 0.988 0.012 0.481 0.962
S8 combined stress
0.252 0.486 0.670 0.000 0.000 0.190
S9 initial deployment 0.710 0.906 0.994 0.054 0.491 0.980
+0.009], and its best case is 0.009 better, far short of the gap
of 0.298, and its worst case is 0.079 worse, so the cheapest
modification in the direction the diagnosis points has not been
shown to close the gap. The scope of that statement is the one
set out above: arm B supplies each agent with its own baseline
and unshares the actor, and neither of those changes the fact
that the reward the gradient sees is the same team reward for
every agent.
That is a useful negative result rather than a frustrating
one, for two reasons. It is consistent with the literature’s own
position: the per-agent estimators that do change the signal
are not trivial modifications, and the closest coverage-specific
evidence [26] uses a per-agent difference utility rather than a
per-agent advantage estimator, so the question on a persistent-
coverage task is genuinely open. And it narrows the search: a
reader who wants to close the gap now knows that the answer
is not “use a local critic”.
We therefore report the result as it stands: The residual is
consistent with the credit assignment of a shared team reward,
and the cheapest test of that diagnosis does not resolve it:
the per-agent local critic’s difference is -0.035 of persistent
coverage (95% interval [-0.079, +0.009]), which includes zero,
the two alternatives that the framework’s other controlled arms
rule out are ruled out, and the cheapest available remedy for
the credit assignment does not close it. The remedies that
change the signal — a difference reward, a counterfactual
baseline, a per-agent value iteration — are implementations of
different algorithms, and we do not claim to have implemented
or evaluated them here.
E. Scenario matrix
Figure 10 is that matrix as a picture: one marker per variant,
the difference between the learned controller and the stronger
of the two rules.
Table XVIII is the scenario matrix: it says whether the
ordering survives outside the configuration it was measured
on. Each row is the mean over the variants of that scenario,
with the proposed controller and the two rules evaluated on
the same scenes. The scenario policies are trained at the base
comparison’s budget, and 8 policies are trained per distinct
S1
S2
S3
S4
S5
S6
S7
S8
S9
−0.6
−0.5
−0.4
−0.3
−0.2
−0.1
0
level with the rule
34 of 34 variants behind
scenario (each marker is one variant)
persistent coverage difference
Fig. 10.
The scenario matrix. The learned controller’s persistent coverage
minus that of the stronger of the two rules, for every variant of every scenario.
It is behind the stronger rule in 34 of the 34 variants, by between 0.080 and
0.598 of persistent coverage, so the ordering holds in every regime the matrix
tests. The 34 cells are not 34 independent measurements: they are 32 distinct
(configuration, scene) evaluations of six policy groups, each on a single scene,
so the matrix is not on the same measurement basis as the five-scene gap, and
a reader told only that a learned controller loses to a rule has been told the
ordering and the size of the deficit but not the cause, which the arms bound
without resolving.
(N, M, pads) combination, because the networks’ input sizes
depend on it; the scenarios that vary only the geometry of
the problem transfer within their combination. Every policy
of a combination is evaluated on the same scenes, so the row
is a mean over training runs rather than a statement about
one of them. The matrix is where the framework’s value is
most visible, because it shows which regime a controller is
good in rather than in which regime it was tuned. Counting
the scenario variants in which the learned controller is ahead,
behind or level with the stronger of the two rules gives 0 ahead,
34 behind and 0 level; the largest deficit is S6 (-0.598) and the
smallest deficit is S2 (-0.080). At the level of scenario means
the learned controller is behind the stronger rule in every
scenario, and behind it in 34 of the 34 variants, by between
-0.598 and -0.080 of persistent coverage, so the ordering is a
property of the method at this budget rather than of a particular
regime, and a reader told only that a learned controller loses
to a rule has been told the whole of it.
F. Claim Audit and Physical-Layer Validation
Every quantitative claim in this paper that is checkable is
recomputed by an automated audit from the same primitives
the simulator uses (analysis/claim_audit.py). Of 38
audited items, 34 are verified exactly, 4 are recorded for
transparency (battery-pack size, the power ratio, the charge
C-rate, and the density of the inter-UAV graph), and 0 fail.
Two findings of the audit are worth stating explicitly.
Three of the audited items are about the measurement
apparatus itself, and they are the ones a reader who has been
burned by an unreproducible pipeline should look at first. Item
R1 establishes that the evaluation of a sampled policy is a
function of (policy, scene): the sampling stream is seeded from
the evaluation seed alone, so the same policy on the same


scene gives the same number every time, and every controller
is measured on the same stream on the same scene. Item
T1 establishes that a training run is a function of its seed,
including when an evaluation is interleaved with it, because
the seed is set before the networks are constructed and so
the initialisation is seeded too. The same property was then
checked across two independent runs of a whole matrix: the
scenario matrix was measured twice, from scratch, and all 170
of the compared values agreed exactly, the largest difference
between the two runs being 0. Item I1 measures the claim
the framework makes first: on the report’s own infeasible
configuration a rule-based controller still reaches a respectable
coverage ratio while the joint metric is identically zero, so
neither metric alone distinguishes that instance from a feasible
one, and the certificate is what makes the reading decidable.
The area surplus is not a feasibility criterion. The audit
confirms that σ = NπR2
cov/(K|Ω|) exceeds one for the
deployed configuration, while the corner-packing bound of
Section III-G shows the configuration is nonetheless infeasible
at N = 5. The two facts are consistent precisely because σ
compares an area to an area, whereas K-covering a bounded
region is a covering problem.
The artefacts accompany the paper, and they are what
the paper is built from. The simulator, the controller, the
experiments and the artefact that holds every measurement
are in the repository that accompanies this preprint, under
ml_impl/: the learned baselines, the arms, the budget sweep,
the ablations and the scenario matrix write JSON or CSV
artefacts, and every number in this paper that comes from
a measurement is generated from those artefacts by a single
token table, so that a number cannot be quoted here that the
artefacts do not contain. The claim audit, the unit tests and the
assembly are runnable from the same tree, and the protocol
each artefact was measured under — the number of training
runs, the device, the training budget and the evaluation scenes
— is recorded inside the artefact itself where the artefact
carries it: the trained CSVs carry the number of training runs,
the device and the per-seed values, and the probe JSONs carry
their own parameters. Not every artefact carries every field yet,
and the gate now fails on a row whose device is recorded as
‘?’ rather than a device name.
The connectivity constraint is live in the regime the ex-
periments use. An earlier version of this paper measured
the density of the inter-UAV graph on a static grid and
reported that connectivity did not bind. That was the wrong
measurement: the experiments use a swarm that flies, so the
quantity that matters is the graph during the mission. Measured
over a 2000-step flight in the deployed regime, the mean node
degree is 3.63 of a possible 7, the graph is complete in only
12% of steps, and nodes of degree ≤1 occur in 23% of UAV-
steps. The H-step feasibility mask and the reserve mechanism
are therefore load-bearing rather than decorative, and the audit
reports the measurement rather than the inference.
The feasibility certificate is audited, not asserted. The audit
re-derives the packing bound and its two instances: it confirms
that the four corner discs are pairwise disjoint at the reported
parameters and that the region therefore needs N ≥4K = 8;
it verifies the tightness construction, finding that the worst-
covered point of the square lies 34.9 m from its nearest of
the 4K disc centres, inside Rcov = 35 m; and it measures the
packing number of the realised sensor sets over 30 random
draws, with a mean of 2.13 and a range of 2–3, which excludes
N = 5 for 4 of the 30 draws. The certificate is therefore
reported with the scope it actually has: unconditional for the
region, and a measured minority for a random sensor layout.
The
path-loss
model
is
shared
with
a
standards-
faithful simulator. The Python reference PHY and INET’s
BreakpointPathLoss are the same function: transcrib-
ing INET’s implementation (BreakpointPathLoss.cc)
gives PL(d) = l02 + 10α log10(d/dbp), which is exactly
the log-distance form used in Section III. With the pa-
rameters recorded by the OMNeT++ run (l01
= l02
=
40.04 dB, α
=
2, dbp
=
1 m, background noise
−93.99 dBm) the two agree to 0.012 dB over 24 (dis-
tance, exponent) combinations spanning 1–1000 m and n ∈
{2, 3.5} (analysis/phy_equivalence.py). The same
audit confirms that the link margin at the report’s two operating
radii is +43.2 dB (access link, 3-D slant range 61.0 m)
and +46.9 dB (inter-UAV link, 40.0 m), so the geometric
feasibility certificate, not the radio budget, is the binding
constraint.
A control configuration was required, and it caught a real
defect. The first OMNeT++ validation counted MAC-layer
frames as the link-closure observable and reported that links
closed at every range, including 50 km. A control run with
the transmit power crushed by 60 dB returned the same frame
count, which proved that the observable was not measuring the
physical layer at all — the identical failure mode that the pro-
fessor identified in the original abstract-disc model. The vali-
dation was therefore rebuilt around a measurement that must
respond to the transmit power, and the control configuration
is retained in the repository (PhyValidationControl) so
that the check is repeatable. We report this as a methodological
point rather than a result: a physical-layer claim that has not
been subjected to a negative control is not yet a measurement.
The second candidate observable, and why the runtime
cross-validation still does not exist. The obvious way to
make a runtime cross-validation is to read the received SNR
per receiver rather than a MAC-layer count, and INET’s
Radio module does expose exactly such a statistic, the
minSnir histogram. We therefore built a proper nega-
tive control for it: a transmit-power sweep in which the
only quantity that changes is the UAV’s transmit power,
over a 117 dB range, with receivers at 10, 30, 50 and
80 m and a UAV at 50 m altitude (run_phy_probe.sh,
analysis/phy_runtime_probe.py). Table XIX is the
probe. The result is specific, and it is reported here in full
because it is the evidence for what the paper does and does
not claim.
Three things follow. First, the control works: the reception
count falls from 500 to 0 as the transmit power is reduced
by 117 dB, so the radio chain is live and is genuinely


TABLE XIX
OMNET++/INET RUNTIME PROBE. THE ONLY DIFFERENCE BETWEEN
THE ROWS IS THE UAV’S TRANSMIT POWER. “RECEPTIONS” IS THE
NUMBER OF PACKETS THE RECEIVER RADIO DELIVERED TO THE UPPER
LAYER; “SNIRINET” IS THE REPORTED M I NSN I R STATISTIC. A ZERO IN
THE RECEPTION COUNT MEANS THE LINK IS BELOW THE RECEIVER’S
SENSITIVITY THRESHOLD, SO NOTHING IS DELIVERED; A DASH MEANS
THE STATISTIC WAS NOT REPORTED AT ALL, BECAUSE WITH NO
DELIVERED PACKET THERE IS NO RECEIVED SIGNAL TO REPORT IT ON.
Receptions at
Config
Ptx
10 m
30 m
50 m
80 m
SNIRINET
A
0.5 W (+27 dBm)
500
500
500
500
46.96 dB
B
1 mW (0 dBm)
500
500
500
500
19.97 dB
C
1 µW (−30 dBm)
0
0
0
0
—
D
1 pW (−90 dBm)
0
0
0
0
—
being exercised. Second, the statistic tracks the transmit power
exactly — a 27.0 dB reduction of Ptx produces a 27.0 dB
reduction of the reported SNR — so it is not simply a frozen
constant. Third, and decisively, it does not track the receiver
distance: the same value is reported for receivers at 10, 30,
50 and 80 m, although the configured path loss differs by
5.3 dB between the nearest and the farthest of them, and the
link-closure threshold is the same at every distance when the
configured path loss requires it to be 13.7 dB lower at 80 m.
The quantity a path-loss cross-validation needs is the SNR as
a function of distance, and that is exactly what this statistic
does not report.
The consequence for this paper is stated plainly. We there-
fore do not claim a runtime cross-validation of the physical
layer. What we do claim is the algebraic equivalence of the
two path-loss functions, established from INET’s own source
and its recorded parameters, to 0.012 dB. The broader method-
ological conclusion — that an instrument must be shown to
respond to a control before its readings can be believed — is
the part we would ask a reader to carry away, and the probe
is included in the repository so that the conclusion can be
re-checked.
Plasticity of the learned policy. A failure mode that does
not appear in reward curves or training loss is known in
the MAPPO literature: the accumulation of dormant neurons
in shared-parameter policies, which [37] report at 40–45%
for vanilla MAPPO, and which [38] and the graph-attention
line of work [18] treat as a structural limitation of MLP
critics. We therefore probe the trained shared actor directly.
The probe retains the hidden-layer activations and performs
one backward pass per agent, so that each agent’s gradient
contribution to each neuron is separable; a single shared
backward pass would expose only the summed gradient and
would hide exactly the per-agent effect that [37] warns about.
A neuron is called dormant when its mean absolute activation
falls below a fraction of the layer mean, silent when its mean
absolute gradient does, and dead when it is both.
Table XX reports the result for the trained policy. The actor
has no forward-dormant neurons in either hidden layer at
any threshold from 10−3 to 10−1 of the layer mean (the largest
dormant fraction measured is 0.000), and consequently no
TABLE XX
PLASTICITY PROBE OF THE TRAINED SHARED ACTOR (128 UNITS PER
HIDDEN LAYER). “DORMANT” MEANS THE MEAN ABSOLUTE ACTIVATION
IS BELOW THE STATED FRACTION OF THE LAYER MEAN; “SILENT” IS THE
SAME TEST ON THE MEAN ABSOLUTE PER-AGENT GRADIENT; “DEAD” IS
BOTH. EVERY ENTRY IS A MEASURED COUNT OR A MEASURED FRACTION:
THE ZEROS SAY THAT NO NEURON IN THAT LAYER FAILS THE TEST AT
THAT THRESHOLD, WHICH IS THE RESULT THE PROBE WAS RUN TO GET.
Layer
τ
Dormant
Silent
Dead
Dormant for some agent only
Hidden 1
10−3
0.000
0.094
0.000
0
Hidden 1
10−1
0.000
0.211
0.000
0
Hidden 2
10−3
0.000
0.117
0.000
0
Hidden 2
10−1
0.000
0.211
0.000
0
dead neurons, in contrast to the 40–45% dormancy reported
for vanilla MAPPO. Between 9% and 21% of the neurons are
gradient-silent, which is the expected and benign consequence
of a low-dimensional observation feeding a 128-unit layer, and
no neuron is dormant for one agent while alive for another.
The probe is not decorative: a test kills half the neurons of a
hidden layer by zeroing their incoming weights and asserts that
the probe reports them as dormant, and a second test asserts
that a healthy network is not reported as dead.

================================================================================
5. NEW SECTION IX: CONCLUSION (full content)
================================================================================
This paper defines a persistent and fault-tolerant UAV-IoT
coverage problem in which the swarm must jointly manage
redundant sensor coverage, inter-UAV connectivity, finite bat-
tery energy, charging contention, and UAV failures. Its central
contribution is a feasibility-certified evaluation framework:
a rigorous lower bound on the fleet size required for K-
coverage of a bounded region, a teleporting placement oracle
as an achievability ceiling against which every policy is
normalised, and a non-degenerate replacement for the all-
constraints-simultaneously service-continuity metric.
Feasibility certificate. The original N = 5, K = 2, Rcov =
35 m configuration is provably infeasible for K-covering the
region: the four corner K-coverage discs are pairwise disjoint,
so the general packing bound N
≥K P(Ω, Rcov) gives
N ≥4K = 8, and the bound is tight at these parameters.
For the sensor requirement the corner argument does not
transfer, and the packing bound applied to the realised sensor
set excludes N = 5 for a measured 13% of random draws;
we report that rather than the convenient unconditional claim.
All trained results use the corrected, feasible configuration
N = 8, K = 2, Rcov = 35 m, for which the same construction
shows that every sensor is K-covered for every layout. The
conventional area-surplus criterion, which exceeds one for the
very same configuration, does not certify feasibility, and the
two facts are consistent because an area is not a covering.
What the framework exposes. The framework is not only
a certificate; it is an instrument that can tell a reader why
a controller behaves as it does, and on this configuration
it says something uncomfortable. A hand-designed reactive
rule outperforms parameter-shared CTDE MAPPO: the gap
is 0.298 of persistent coverage, with a 95% interval of
[0.248, 0.349], and the learned controller is below it under


either deployment mode (sampled 0.674, argmax 0.418). Three
candidate explanations — the content of the observation, the
energy model, and the size of the training budget — were
each tested with a single-factor intervention paired with the
proposed configuration. Controlled arms bound how much of
the gap each alternative explanation can account for: adding
the agent identity (upper limit 0.137, margin +0.161); the full
observation of the proposed configuration (upper limit 0.102,
margin +0.196); removing the energy constraint (upper limit
0.075, margin +0.223); removing the threshold term (upper
limit 0.011, margin +0.287); the previous energy rule (upper
limit 0.015, margin +0.283), against a gap of 0.298. Every
arm’s upper limit is below the gap, so none of them can be
the whole of the explanation, by margins that are small but
positive. Every interval is paired over the same training seeds,
against the local-only arm A of the observation experiment and
the proposed configuration of the energy experiment and the
proposed configuration of the credit experiment. What remains
is a residual that is consistent with the credit assignment of a
shared team reward (The credit assignment of a shared team
reward is the explanation the residual is consistent with, and
the cheapest test of it does not resolve it), and with causes that
these arms do not test: the possibility that the hand-written
rule was tuned against the evaluation scenes, the limit of a
decentralised policy class, and the state-dependent corrections
that the safety filter and the joint projection impose on the
executed trajectory. Its privileged access to the coverage state
is not among them: that is measured in the first table, and it
is not the explanation. A non-detection in an arm of a given
width is a statement about the resolution of that arm and not
about the component, so we report the resolution of every
arm, and we do not claim that the remaining components are
unnecessary, that they would remain so at a larger training
budget, or that the credit assignment is the whole of the
explanation. We identify the remedy the residual suggests —
a per-agent signal rather than a better team signal — and we
do not claim to have implemented or evaluated it.
Scope of the physical-layer claim. The Python reference
PHY and INET’s BreakpointPathLoss are the same
function, to 0.012 dB over 24 (distance, exponent) points.
We deliberately do not claim a runtime cross-validation, and
the reason is measured rather than asserted: a transmit-power
sweep shows that the available per-receiver SNR statistic
tracks the transmit power exactly but is independent of the
receiver’s distance, so it cannot support a path-loss cross-
validation. A physical-layer claim that has not been subjected
to a negative control is not a measurement, and this is the one
we would most like a reader to carry away.
Honest limitations. (i) All results are on 2000-step episodes
(400 s of flight); the report’s 10 000-step target may change
conclusions, and in particular the credit-assignment limitation
may be partly a budget artefact; the two convergence mea-
surements bound that possibility but do not resolve it. (ii) The
single-component arms are measured with 8 training seeds,
and that bounds what they can resolve: their intervals have
half-widths between 0.000 and 0.042 of persistent coverage,
and the minimum detectable effect at eighty per cent power
for the widest of them is larger than its half-width; a null
from an arm of that width says that no effect of that size
was detected, not that the component is unnecessary. A null
result from an arm of that width says that no effect above that
resolution was detected; it does not say that the component
is unnecessary. A component that is redundant with another,
so that removing either alone costs nothing, is invisible to an
arm of this kind, and so is a component that matters only
at a larger training budget; settling either needs a budget
sweep or more seeds. We run the sweep, and for the full
configuration it settles the question it can reach: the budget
buys +0.086 of persistent coverage over 8 −−25 episodes,
and the paired comparison over the same training seeds puts
that gain at [+0.036, +0.135], an interval whose upper limit
is below the gap of 0.298 — so the budget is excluded as
the explanation of the shortfall, over the range the sweep
covers. That is a statement about the full configuration and
not about the individual components, which are each measured
at the single budget the base comparison uses, and it is not
a claim about budgets beyond the range the sweep covers.
(iii) The reactive heuristic is given the exact set of under-
covered sensors, which corresponds to an unbounded broad-
cast, while the learned policy receives a fixed-size summary;
part of the gap might therefore be a difference of information
and not of control. The arm reported in the first table, in
which the same rule runs without the global coverage state,
measures that, and the measurement does not support the
caveat. (iv) The evaluation seed determines both the scene
and the action-sampling stream, so the spread reported for a
controller does not separate the scene-to-scene variation from
the action-sampling variation. The two are common to every
controller and cancel in the comparisons this paper draws,
but they both enter the absolute numbers. (v) The comparison
is not compute-matched in the sense that a hand-designed
rule embeds a human’s solution while the learner receives a
fixed training budget, and the learned controller’s margin over
the other learned arms is small compared with the seed-to-
seed spread, so the differences between the learned methods
should be read with that spread in mind. A learning curve
and a budget sweep are what would speak to the first point,
and they are the two convergence measurements we report.
The four candidate explanations of Section VII are the ones
the framework’s own mechanisms suggest, and they do not
exhaust the possibilities; the explanation that survives them
was not pre-specified, so a study that had tested a different set
of arms could have reached a different conclusion. (vi) The
OMNeT++ Phase-2 scenario ran and its negative control is
reported, but the runtime instrument cannot support a path-loss
cross-validation, so the equivalence is established from INET’s
source rather than from a running simulation. (vii) Phase-3
(Simu5G PHY) is scaffolded but not executed with the learned
policy. (viii) The joint connectivity projection leaves no hole:
in a probe that drives the swarm with every stored policy
(the learned controller), 4 transitions into a disconnected graph
occurred, all 4 of them after a UAV left the active set, 0 after


a teleport and 0 unexplained, so every one of them follows a
UAV leaving rather than a move. The probe drives the swarm
with the stored policies, so it speaks for the deployed controller
on those runs; it does not speak for a policy trained with a
different observation or a different budget, and the projection’s
own revision count on the deployed configuration is 0.10 per
episode. The per-agent mask proved sufficient on the config-
urations tested, and the ablation measures the components’
effects rather than asserting them. (ix) The degenerate service-
continuity metric is retained for comparison but supplemented
by the non-degenerate alternatives.
REFERENCES
[1] C. H. Liu, Z. Chen, J. Tang, J. Xu, and C. Piao, “Energy-efficient
UAV control for effective and fair communication coverage: A deep
reinforcement learning approach,” IEEE Journal on Selected Areas
in Communications, vol. 36, no. 9, pp. 2059–2070, Sep. 2018, doi:
10.1109/JSAC.2018.2864373.
[2] J. Qiu, J. Lyu, and L. Fu, “Placement optimization of aerial base stations
with deep reinforcement learning,” arXiv:1911.08111, 2019.
[3] C. Yu, A. Velu, E. Vinitsky, J. Gao, Y. Wang, A. Bayen, and Y. Wu,
“The surprising effectiveness of PPO in cooperative multi-agent games,”
in Advances in Neural Information Processing Systems, 2022.
[4] B. Omoniwa, B. Galkin, and I. Dusparic, “Optimizing energy efficiency
in UAV-assisted networks using deep reinforcement learning,” IEEE
Wireless Communications Letters, vol. 11, no. 8, pp. 1590–1594, Aug.
2022, doi: 10.1109/LWC.2022.3167568.
[5] M. Zareh, L. Sabattini, and C. Secchi, “Decentralized biconnectivity
conditions in multi-robot systems,” in Proc. IEEE Conf. Decision and
Control (CDC), 2016, pp. 99–104, doi: 10.1109/CDC.2016.7798253.
[6] P. Basu and J. Redi, “Movement control algorithms for realization of
fault-tolerant ad hoc robot networks,” IEEE Network, vol. 18, no. 4, pp.
36–44, Jul.–Aug. 2004, doi: 10.1109/MNET.2004.1316760.
[7] N. Mathew, S. L. Smith, and S. L. Waslander, “Multi-robot ren-
dezvous planning for recharging in persistent tasks,” IEEE Trans-
actions on Robotics, vol. 31, no. 1, pp. 128–142, Feb. 2015, doi:
10.1109/TRO.2014.2380593.
[8] E. Arribas, V. Cholvi, and V. Mancuso, “Optimizing UAV resupply
scheduling for heterogeneous and persistent aerial service,” IEEE Trans-
actions on Robotics, vol. 39, no. 4, pp. 2639–2653, Aug. 2023, doi:
10.1109/TRO.2023.3263077.
[9] Z. Jiang, T. Song, B. Yang, and G. Song, “Fault-tolerant con-
trol for multi-UAV exploration system via reinforcement learning
algorithm,” Aerospace, vol. 11, no. 5, p. 372, May 2024, doi:
10.3390/aerospace11050372.
[10] M. R. Khan, G. R. V. Premkumar, and B. Van Scoy, “Robust UAV-
oriented wireless communications via multi-agent deep reinforcement
learning to optimize user coverage,” Drones, vol. 9, no. 5, p. 321, Apr.
2025, doi: 10.3390/drones9050321.
[11] T. Sun, N. Guo, H. Gu, Y. Peng, and Z. Feng, “Integrated commu-
nication and control for energy-efficient UAV swarms: A multi-agent
reinforcement learning approach,” arXiv:2509.23905, 2025.
[12] Z. Chen, Y. Huang, C. Zhu, and W. Zhou, “Multi-agent reinforcement
learning based trajectory design for UAV-assisted emergency wireless
communication,” in Proc. 10th Int. Conf. Computer and Communication
Systems (ICCCS), Chengdu, China, 2025, pp. 856–861, doi: 10.1109/IC-
CCS65393.2025.11069505.
[13] J. P. Carvalho and A. P. Aguiar, “Multi-agent reinforcement learning
for zero-shot coverage path planning with dynamic UAV networks,”
Robotics and Autonomous Systems, vol. 195, p. 105163, Jan. 2026, doi:
10.1016/j.robot.2025.105163.
[14] H. Mei, C. Xu, R. Li, and X. Luo, “Energy-aware persistent multi-UAV
coverage via reinforcement learning guided by user priority and outage,”
Drones, vol. 10, no. 9, p. 688, Sep. 2026, doi: 10.3390/drones10090688.
[15] A. Trotta, M. Di Felice, F. Montori, K. R. Chowdhury, and L. Bononi,
“Joint coverage, connectivity, and charging strategies for distributed
UAV networks,” IEEE Transactions on Robotics, vol. 34, no. 4, pp.
883–900, Aug. 2018, doi: 10.1109/TRO.2018.2839087.
[16] J. Scherer and B. Rinner, “Persistent multi-UAV surveillance with energy
and communication constraints,” in Proc. 16th Int. Conf. Emerging
Technologies and Factory Automation (ETFA), IEEE, 2016, pp. 1225–
1230, doi: 10.1109/COASE.2016.7743546.
[17] E. Hartuv, N. Agmon, and S. Kraus, “Scheduling spare drones for
persistent task performance under energy constraints,” in Proc. 16th
Conf. Autonomous Agents and MultiAgent Systems (AAMAS), 2018, pp.
532–540.
[18] R. Shi, X. Yu, Y. Wang, Y. Tian, Z. Liu, W. Wu, X.-P. Zhang, and M. M.
Veloso, “Symmetry-informed MARL: A decentralized and cooperative
UAV swarm control approach for communication coverage,” IEEE
Transactions on Mobile Computing, vol. 24, no. 9, pp. 8039–8056, Sep.
2025, doi: 10.1109/TMC.2025.3553285.
[19] D. Datsko, F. Nekovar, R. Penicka, and M. Saska, “Energy-aware multi-
UAV coverage mission planning with optimal speed of flight,” IEEE
Robotics and Automation Letters, vol. 9, no. 3, pp. 2893–2900, 2024,
doi: 10.1109/LRA.2024.3358581.
[20] M. A. Luna, M. S. Ale Isaac, A. R. Ragab, P. Campoy, P. Flores
Pe˜na, and M. Molina, “Fast multi-UAV path planning for optimal area
coverage in aerial sensing applications,” Sensors, vol. 22, no. 6, p. 2297,
2022, doi: 10.3390/s22062297.
[21] J. Foerster, S. K. H. Phan, and A. F. T. Ho, “Learning to communicate
with deep multi-agent reinforcement learning,” in Proc. 15th Conf.
Autonomous Agents and MultiAgent Systems (AAMAS), 2016, pp. 3–11.
[22] J. Foerster, T. Farquhar, F. Afouras, S. Nardelli, and S. Whiteson, “Coun-
terfactual multi-agent policy gradients,” in Proc. 32nd AAAI Conf. Arti-
ficial Intelligence, 2018, pp. 3502–3511, doi: 10.1609/aaai.v32i1.11682.
[23] W. Li, L. Xie, and H. Lu, “Difference advantage estimation for multi-
agent policy gradients,” in Proc. 39th Int. Conf. Machine Learning
(ICML), 2022, pp. 306–324, arXiv:2206.08300.
[24] J. Kim, J. Park, S. Kim, M. Jeon, S. Han, and B. Sung, “Generalized
per-agent advantage estimation for multi-agent policy optimization,” in
Proc. Int. Conf. Autonomous Agents and MultiAgent Systems (AAMAS),
2026, doi: 10.65109/OBIA4073, arXiv:2603.02654.
[25] J. G. Kuba, R. Cecil, E. Parisotto, and J. S. ˇSafr´anek, “Trust region
policy optimisation in multi-agent reinforcement learning,” in Proc.
39th Int. Conf. Machine Learning (ICML), 2022, pp. 21586–21610,
arXiv:2106.07490.
[26] Z. Sun, N. Wang, H. Lin, and X. Zhou, “Persistent coverage
of UAVs based on deep reinforcement learning with wonderful
life utility,” Neurocomputing, vol. 521, pp. 137–145, 2023, doi:
10.1016/j.neucom.2022.11.091.
[27] C. S. de Witt, J. K. G. Farquhar, A. S. K. Foerster, A. E. L. Fellowes,
and S. Whiteson, “Is independent learning all you need in the StarCraft
multi-agent challenge?” in Proc. Int. Conf. Learning Representations
(ICLR), 2021, arXiv:2011.09533.
[28] H. Fu, H. Yu, T. Xu, H. Yang, and W. Wu, “Revisiting some com-
mon practices in cooperative multi-agent reinforcement learning,” in
Proc. 39th Int. Conf. Machine Learning (ICML), 2022, pp. 7013–7026,
arXiv:2206.07505.
[29] J. Qiu, J. Lyu, and L. Fu, “Placement optimization of aerial base stations
with deep reinforcement learning,” in Proc. IEEE Int. Conf. Communi-
cations (ICC), 2020, pp. 1–6, doi: 10.1109/ICC40277.2020.9149258.
[30] S. Huang and S. Onta˜n´on, “A closer look at invalid action masking in
policy gradient algorithms,” in Proc. Int. FLAIRS Conf., vol. 35, 2022,
doi: 10.32473/flairs.v35i.130584.
[31] A. Al-Hourani, S. Kandeepan, and S. Lardner, “Optimal LAP altitude
for maximum coverage,” in IEEE Wireless Communications Letters, vol.
3, no. 6, pp. 569–572, Dec. 2014, doi: 10.1109/LWC.2014.2342736.
[32] 3GPP, “Study on enhanced LTE support for aerial vehicles,” 3GPP TR
36.777, Rel. 15, 2017.
[33] IEEE, IEEE Standard for Information Technology—Telecommunications
and information exchange between systems—Local and metropolitan
area networks—Specific requirements—Part 11: Wireless LAN Medium
Access Control (MAC) and Physical Layer (PHY) Specifications, IEEE
Std 802.11-2016, Dec. 2016.
[34] F. Pardo, A. Tavakoli, V. Levdik, and P. Kormushev, “Time limits in
reinforcement learning,” in Proc. 35th Int. Conf. Machine Learning
(ICML), 2018, pp. 4042–4051.
[35] Z. Song, K.-W. Chin, C. Yang, and M. Ros, “Methods to assign UAVs
for K-coverage and recharging in IoT networks,” IEEE Transactions
on Mobile Computing, vol. 23, no. 4, pp. 2504–2519, 2024, doi:
10.1109/TMC.2023.3259461.
[36] D. Rizvi and D. Boyle, “Multi-agent reinforcement learning with action
masking for UAV-enabled mobile communications,” IEEE Transactions
on Machine Learning in Communications and Networking, vol. 3, pp.
117–132, 2025, doi: 10.1109/TMLCN.2024.3521876.


[37] W. Qiu, Z. He, W. Zhao, and H. Masui, “PRIME: Plasticity recovery in
multi-agent environments for UAV-assisted emergency communication
networks,” arXiv:2607.17922, 2026.
[38] D. Babarytskyi, “Feasibility ceilings before learning: Sizing and timing
bounds for drone-mesh interception,” arXiv:2610.20823, Oct. 2026.
[39] J. Viana, V. R. Balaji, B. Galkin, L. Ho, and H. Claussen, “Learn-
ing compact terrain-context representations for feasibility-aware offline
reinforcement learning in UAV relaying networks,” arXiv:2604.00224,
2026.
[40] V. Datta and C. Nahak, “Radius of robust feasibility for ground coverage
in aerial sensor networks,” arXiv:2510.20213, 2025.
[41] E. Fan, Y. Chen, Z. Shan, M. Caesar, and J. Kim, “Communication-
aware multi-agent reinforcement learning for decentralized cooperative
UAV deployment,” arXiv:2603.16141, 2026.
[42] H. Lee, S. Jeong, N. Y. Kim, and J. Seo, “Quantum-based k-
coverage optimization for UAV-aided search and rescue missions,”
arXiv:2609.01930, 2026.
[43] B. Wang, Y. Wang, and S. Huang, “Priority-aware persistent coverage
with unbalanced revisit period constraints,” in Proc. 6th Int. Conf.
Computer, Control and Robotics (ICCCR), 2026, pp. 406–411.
[44] C. Zhang, C. Xu, G. Li, and B. He, “A distributed task allocation ap-
proach for multi-UAV persistent monitoring in dynamic environments,”
Scientific Reports, vol. 15, art. 6437, 2025, doi: 10.1038/s41598-025-
89787-3.


================================================================================
6. KEY QUANTITATIVE DIFFERENCES (numbers in NEW not in OLD)
================================================================================
Numbers in NEW but not OLD: 414
Notable (>=3 chars): ['0.0', '0.000', '0.0016', '0.002', '0.003', '0.004', '0.005', '0.006', '0.007', '0.008', '0.0083', '0.009', '0.010', '0.011', '0.012', '0.013', '0.015', '0.016', '0.018', '0.019', '0.020', '0.021', '0.024', '0.025', '0.029', '0.03', '0.033', '0.034', '0.035', '0.036', '0.039', '0.042', '0.044', '0.045', '0.047', '0.049', '0.050', '0.051', '0.054', '0.055', '0.056', '0.060', '0.062', '0.066', '0.067', '0.069', '0.075', '0.079', '0.080', '0.083']

================================================================================
7. KEY TERMS IN NEW NOT IN OLD
================================================================================
Significant new terms (1000):
  - -episode
  - -greedy
  - -second
  - ability
  - ablations
  - absence
  - absences
  - absorbing
  - abstract-disc
  - academic
  - accessor
  - accompanies
  - accompany
  - accounts
  - accumulation
  - achievability
  - achieves
  - achieving
  - action-masking
  - action-probability
  - action-sampling
  - actionable-looking
  - active-uav
  - actually
  - additively
  - addresses
  - adjacent
  - adjusted
  - admissibility
  - admissible
  - admitted
  - advance
  - advantage-decomposition
  - afouras
  - against
  - agent-specific
  - air-to-ground
  - airframe
  - al-hourani
  - alarming
  - algebraic
  - algebraically
  - all-constraints-simultaneously
  - all-simultaneous-constraint
  - alongside
  - alternative
  - although
  - analyse
  - analytic
  - another
  - anything
  - anywhere
  - apparatus
  - appears
  - appendix
  - applicable
  - applications
  - applied
  - approximate
  - approximation
  - arbitrate
  - area-surplus
  - argument
  - arrangement
  - arrives
  - artefact
  - artefacts
  - articulation
  - assembly
  - asserted
  - asserting
  - asserts
  - assigns
  - asymmetry
  - attained
  - attributable
  - attribute
  - audited
  - automated
  - automation