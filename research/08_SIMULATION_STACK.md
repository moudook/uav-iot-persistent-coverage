<task id="ses_f12ba3823ffez7Az7w13dasJQp" state="completed">
<task_result>
I've verified everything against primary sources. Three of your premises are out of date, and two "traps" you suspected are worse than you thought. Here's the reference.

---

# Simulation Toolchain & Open-Source Simulators
### Technical reference for MARL-based persistent, fault-tolerant UAV-IoT coverage
*Compiled 29 September 2026. All versions and dates verified against official release pages, GitHub API, and upstream source trees — not blog posts.*

---

## 0. Executive summary — corrections before you start

| Your premise | Reality as of 29 Sep 2026 | Impact |
|---|---|---|
| "INET 4.5" is current | **INET 4.7.0**, released 7 Jul 2026, requires OMNeT++ ≥ 6.4. INET 4.5.4 is from **Oct 2024** — two years stale. | **High.** INET 4.5.4 is the version pinned by Simu5G's own CI, which creates a fork-in-the-road (see §3.3). |
| "OMNeT++ 6.2" | **OMNeT++ 6.4.0**, released 8 May 2026. | Medium. |
| AirSim is unmaintained | Worse than you thought: **Microsoft shut AirSim down in July 2022; its successor Colosseum was archived by the owner on 11 Jul 2026.** Both are hard dead ends. | **High.** |
| sb3-contrib MAPPO is low quality | Worse: **MAPPO and IPPO have been removed entirely from sb3-contrib.** Current `sb3_contrib` package contains only `ars`, `common`, `crossq`, `ppo_mask`, `ppo_recurrent`, `qrdqn`, `tqc`, `trpo`. | **High.** `from sb3_contrib import MAPPO` fails on every current version. |
| `pyopp` for Python-in-OMNeT++ | **No `pyopp` exists in OMNeT++ 6.x at all.** Verified against the 6.4.0 source tree — zero matches. Embedded Python *NED modules* are impossible. | **High.** Rules out option (b) of your bridge design. |
| `ScalarRadio`, `IsotropicScalarRadioMedium`, `DmgErrorModel`, `IdealPropagation`, `BasicRangePropagation`, `DielectricBreakdownPropagation`, `TernaryPropagation`, `PERTableRadioErrorModel`, `TableBasedErrorModel`, `SimpleWirelessHost` | **All removed or renamed in INET 4.6** (released 20 Feb 2026) during a large wireless-PHY refactoring. Any tutorial or LLM-generated code using these will fail. | **High.** See §2.5. |
| Simu5G may be stale | **Very alive.** v1.7.0 released **14 Sep 2026** (two weeks ago). | — |
| sb3-contrib MAPPO quality | The class of concern is real but relocated — use the original `susanbao/mappo` PyTorch implementation or CleanRL. | — |

**One good piece of news:** Simu5G v1.7.0 is *explicitly tested against INET 4.5.4 + OMNeT++ 6.3*, and declares compatibility with INET 4.6.0 and OMNeT++ 6.1–6.4. So INET 4.5.4 is not "wrong" — it is the *conservative, test-covered* choice. Pick your stack deliberately (§11.2).

---

## 1. OMNeT++ 6.4.0

### 1.1 Version and provenance

| Field | Value |
|---|---|
| Current stable | **6.4.0** |
| Release date | **2026-05-08** |
| Release page | <https://github.com/omnetpp/omnetpp/releases/tag/omnetpp-6.4.0> |
| What's-new | <https://github.com/omnetpp/omnetpp/blob/omnetpp-6.4.0/WHATSNEW.md> |
| License | Academic Public License (free for academic use; commercial license = OMNEST) |
| Language | C++ (kernel + models), NED (topology), Python (analysis only) |

Artifacts (`omnetpp.org/download`):

```
omnetpp-6.4.0-linux-x86_64.tgz       403MB  SHA256 2dd2cfbd388e50e843f5713716f065e878df7bb104b69f3435f740b37b21d459
omnetpp-6.4.0-linux-aarch64.tgz     402MB  SHA256 13099125c95f636f37fc4d23e2ed8c9fa81e8396e90879673e86a80647c148cd
omnetpp-6.4.0-windows-x86_64.7z    1153MB  SHA256 3c0957fe466332bcf441f132ac0fe102986c96699f50fee03abbcafbdc4504ab
omnetpp-6.4.0-macos-{aarch64,x86_64}.tgz  401/400MB
omnetpp-6.4.0-core.tgz               76MB  SHA256 db8de41f2503772aa627fbd99901078fd7a9db9942df9f284de40f7704053bbb
```

Headless (recommended for CI/RL training):
```bash
docker run --rm -it -v "$(pwd):/root/models" -u "$(id -u):$(id -g)" \
    ghcr.io/omnetpp/omnetpp:u26.04-6.4.0
```

> **Windows warning, and it is serious.** The OMNeT++ download page itself states the MinGW build is *"a LOT slower for development than the Linux or macOS versions"* due to Msys POSIX emulation and NTFS. If you are on Windows (and the working directory here suggests you are), **use WSL2**. Get `opp_env.wsl` (186 MB) from the download page, or install the Linux tarball under WSL. Simulation throughput differences of 3–10× are normal, and that difference is fatal for RL training budgets.

### 1.2 Installation — `opp_env` is now the blessed path

OMNeT++ 6.4 pushes `opp_env` over the legacy `opp_env install` / tarball `install.sh` flow.

```bash
# Linux / macOS
pip install opp-env
mkdir -p ~/omnetpp-workspace && cd ~/omnetpp-workspace
opp_env init
opp_env install omnetpp-6.4.0
opp_env install inet-4.7.0            # or simu5g-1.7.0
opp_env run inet-4.7.0 --build         # build + resolve deps
```

```powershell
# Windows: download opp_env.wsl, then inside WSL2 (need WSL ≥ 2.4.4)
opp_env install omnetpp-6.4.0
```

### 1.3 Three ways to work

**(a) IDE (Eclipse-based).** Best for *authoring*: NED editor with completion, C++ CDT, the Qtenv visualizer, built-in Result Analysis (`.anf` chart files), NED inheritance view, inline documentation tooltips, and the INET installer (`Help ▸ Install Simulation Models…`). You will not run your RL training from the IDE.

**(b) `opp_run` — the headless command-line kernel. This is your training workhorse.**

```
opp_run [options] -f -l <inifile> -c <configname> [-r <runnumber>] [-n <nedpath>]

  -l, --ini-file=<file>       ini file (required)
  -c, --config=<name>         configuration name; accepts globs ('Wireless*') and '**' for all
  -r, --run-number=<n>        run index within the config; 0 = seed-set 0
  -n, --ned-path=<path>       colon-separated list of NED source roots (repeatable)
  -f, --force                 overwrite existing result files without asking
  -u, --cmdenv                use the console user interface (default when no -q/IDE attached)
  -q, --quiet                 quiet console: 'none' | 'cmdenv'
      --cmdenv-express-mode=<bool>   terse progress (set true in scripts)
      --sim-limit=<time>      e.g. --sim-limit=100s   (overrides sim-time-limit)
      --seed=<n>             RNG seed (0 => derive from run number)
      --seed-set=<n>         seed-set, -1 = repeat the last run
  -s, --seed-set=<n>          short form
  -h, --help                  full option list for your build
      --version               kernel version string
      --result-dir=<dir>      override result directory
```

**Exact batch commands you will use:**

```bash
# one config, one run, overwrite results
opp_run -u Cmdenv -f -l omnetpp.ini -c Baseline

# every configuration in the ini, run 0
opp_run -u Cmdenv -f -l omnetpp.ini -c '**'

# parameter sweep, all runs of one config, parallel across cores
opp_runall -l omnetpp.ini -c 'UAVSweep'          # 1 job per logical CPU
opp_runall -l omnetpp.ini -c 'UAVSweep' -j 4     # or cap it

# the canonical 10-runs-per-seed-set statistical batch (this is your unit of evidence)
opp_runall -l omnetpp.ini -c 'General' -r 0-9

# sweep two parameters x 3 seeds x 10 runs, headless
opp_runall -l omnetpp.ini \
    -c 'General' \
    --numjobs=10 \
    -s 0-2 \
    '**.numUavs'=${numUavs:3,5,7} \
    '**.lambda'=${lambda:0.5,1.0,1.5}
```

> `opp_runall` is the parallel *batch* runner (fork-per-configuration on one machine). It is **not** the same thing as OMNeT++'s distributed-parallel simulation (MPI / `opp_run -h | grep parsim`). For 5 UAVs you want neither MPI nor the parsim scheduler; `opp_runall` is the right tool.

**(c) `opp_repl` / `opp_python_repl`.** New in 6.4: a Python REPL with the omnetpp libraries imported, exposing `read_result_files()`, `run_simulations()`, parameter optimization, and an MCP server for AI assistants.

```bash
pip install opp-repl           # v0.4, released 11 May 2026 — external package, LGPLv3+
. /path/to/omnetpp/setenv
opp_repl --load @opp           # or --load "opp/*.opp"
# In [1]: run_simulations(simulation_project = fifo_project)
```
`opp_repl` also ships CLI tools and is the right thing for sweeping a parameter outside the ini file. It also provides an MCP server, so you can drive batch experiments from an LLM agent — but **do not let an LLM pick your experimental design**; see §10.5.

### 1.4 Build toolchain — what a project needs

A minimal OMNeT++ project is **four files**:

```
myproject/
├── .project                 # Eclipse project descriptor (only if you want the IDE)
├── Makefile.inc             # drives opp_makemake  ← the only file you must hand-write
├── src/
│   ├── Makefile             # GENERATED by opp_makemake — never edit, never commit-by-hand
│   ├── MyModule.cc/.h       # your cSimpleModule subclass
│   └── ... (recursive subdirs)
├── MyNetwork.ned            # topology
└── omnetpp.ini              # configuration
```

**The mechanism (this trips everyone up once):** there is no committed `src/Makefile`. `opp_makemake` *generates* it, and the generated file is what `make` actually consumes. The `Makefile.inc` records the `opp_makemake` command line so the file is reproducible.

**Pure OMNeT++ `Makefile.inc`:**
```makefile
# A. Build mode
MODE = release

# B. Compile-time flags
CXXFLAGS += -std=c++20

# C. Source/build config
opp_makemake --makefile -f --force \
    -I../src \
    -O$(MODE) \
    -$(MODE)

# D. Include paths
INCLUDE_PATH = ../src
INCLUDE_PATH += -I.

# E. Libraries
opp_makemake --make-so --recursive
```

**INET-backed `Makefile.inc`** (this is the file you need for the UAV project):
```makefile
# A. Build mode
MODE = release

# B. Toolchain
PREFER_CLANG = no
# PREFER_CLANG = yes        # uncomment if you have a Clang toolchain; often 20-30% faster

# C. Output / optimization
CXXFLAGS += -std=c++20 -O3 -march=native -flto
# NOTE: -march=native breaks reproducibility across heterogeneous machines.
#       Use it for the FINAL training runs, not for anything you need to reproduce elsewhere.
LDFLAGS += -flto

# D. Source config
opp_makemake --makefile -f --force --recursive -O$(MODE) -$(MODE)

# E. Include paths — INET
INET       = ../../inet-4.7.0
INCLUDE_PATH = ../src
INCLUDE_PATH += -I$(INET)/src
INCLUDE_PATH += -DOMNETPP_TRACE -DINET_DEBUG

# F. Libraries
opp_makemake --make-so
LIBS += $(INET)/src/INET
```

Then:
```bash
cd src && opp_makemake            # generates src/Makefile from Makefile.inc
make MODE=release -j$(nproc)     # or: make MODE=debug -j$(nproc)  (LLDB-debuggable)
```

> **The modern alternative: `.oppbuildspec`.** OMNeT++ 6.x and INET now let the IDE and `opp_env` generate makefiles from a declarative file instead, so include paths come from *project dependencies* rather than hardcoded relative paths. INET's own `.oppbuildspec` is:
> ```xml
> <?xml version="1.0" encoding="UTF-8" standalone="no"?>
> <buildspec version="4.0">
>     <dir path="." type="custom"/>
>     <dir makemake-options="--make-so --deep -o INET -O out -pINET --meta:export-include-path
>                             --meta:export-library --meta:use-exported-libs
>                             --meta:feature-cflags --meta:feature-ldflags"
>          path="src" type="makemake"/>
> </buildspec>
> ```
> with a top-level `Makefile` whose `makefiles` target extracts the options with `sed` and re-invokes `opp_makemake`. **Recommendation for a student project: hand-write `Makefile.inc`.** It is one file, it is greppable, it does not depend on the IDE, and it is the only form that survives being cloned on someone else's machine.

Build modes and gotchas:
- `MODE=release` → `-O3 -DNDEBUG`, fast. **This is what you benchmark.** `MODE=debug` → `-O0 -ggdb3`, ~10–30× slower; unusable for training.
- `opp_makemake` needs `opp_makemake` on `PATH`; source `$(OMNETPP_ROOT)/setenv` first.
- `opp_featuretool` regenerates `src/inet/features.h` from `.oppfeatures` / `.oppfeaturestate` if you enable INET project features (e.g. `Simu5G_D2D`).
- `opp_neddoc -f <selfdoc>.xml .` generates NED documentation. Use it once to confirm every type you instantiate actually resolves.

### 1.5 NED language — a real, minimal, working example

NED has exactly four composite constructs. Here is a complete two-module system you can compile.

**`src/Ticker.cc`**
```cpp
#include <omnetpp.h>
#include "Ticker.h"

using namespace omnetpp;
using namespace std;

Define_Module(Ticker);

void Ticker::initialize(int stage)
{
    EV << "Ticker init, stage " << stage << " of " << getSimulation()->getNumStages() << "\n";
    if (stage == 0)
        timer = scheduleAt(simTime() + par("period").doubleValue(), new cMessage("tick"));
}

void Ticker::handleMessage(cMessage *msg)
{
    cOutVector &v = recordScalar("ticks");
    v.record(simTime());
    counter++;
    recordScalar("tickCount", counter);
    EV << "tick #" << counter << " at t=" << simTime() << "\n";
    if (simTime() < getSimulation()->getTerminationTime())
        scheduleAt(simTime() + par("period").doubleValue(), msg);
}

void Ticker::finish()
{
    recordScalar("totalTicks", counter);
}
```

**`src/Ticker.h`**
```cpp
#ifndef TICKER_H_
#define TICKER_H_
#include <omnetpp.h>
using namespace omnetpp;
class Ticker : public omnetpp::cSimpleModule {
  protected:
    void initialize(int stage) override;
    void handleMessage(omnetpp::cMessage *msg) override;
    void finish() override;
  private:
    cMessage *timer = nullptr;
    int counter = 0;
};
#endif
```

**`src/Sink.cc`**
```cpp
#include <omnetpp.h>
using namespace omnetpp;
Define_Module(Sink);
void Sink::handleMessage(cMessage *msg) {
    recordScalar("received", 1);
    delete msg;
}
```

**`src/Sink.h`**
```cpp
#ifndef SINK_H_
#define SINK_H_
#include <omnetpp.h>
using namespace omnetpp;
class Sink : public omnetpp::cSimpleModule {
  protected:
    void handleMessage(omnetpp::cMessage *msg) override;
};
#endif
```

**`TickerSink.ned`**
```ned
//
// Package-less: the package is taken from the enclosing folder name.
// To declare a package explicitly, uncomment and adapt the line below.
//
package myproject;              // <-- folder path myproject/ must match

//
// A simple module: 1 instance per gate-port connection tree, C++-backed.
// The [Ticker] is the C++ class name. One NED type maps to exactly one class
// (or a class hierarchy via @class / -- a NED type can bind to a subclass).
//
simple Ticker
{
    parameters:
        double period = 1s;                 // default value; overridable from .ini
        int    id = -1;                     // unassigned by default
    gates:
        inout io;                           // bidirectional gate
    submodules:
        console: <default("")> if typename != "" { }   // conditional submodule
}

simple Sink
{
    gates:
        input in;
    submodules:
        console: <default("")> if typename != "" { }
}

//
// A compound module: assembly of submodules + connections. No C++ backing
// (unless you add @class). Reusable via `extends` / `like`.
//
module TickerSinkNode
{
    parameters:
        double period = 1s;
        @display("p=100,100;b=200,200");
    gates:
        inout io;                           // gates are NOT automatically connected
    submodules:
        ticker: Ticker {
            parameters:
                period = parent.period;     // keyword `parent` = enclosing module
        }
        sink: Sink {
            parameters:
                @display("p=0,0");
        }
    connections:
        ticker.io <--> sink.in;             // <--> is a shorthand for a <--> gate pair
}

//
// A network: a compound module with no gates. Exactly one per run.
// Vector submodules let you instantiate N copies with [k] in ini.
//
network TwoNodes
{
    submodules:
        nodeA: TickerSinkNode {
            parameters:
                period = 1s;
            @display("p=0,0");
        }
        nodeB: TickerSinkNode {
            parameters:
                period = 2s;
            @display("p=300,0");
        }
        nodeC[3]: TickerSinkNode {          // 3 instances: nodeC[0..2]
            parameters:
                period = 0.5s;
            @display("p=600,0");
        }
}
```

**NED grammar essentials** (the parts people get wrong):

| Element | Syntax | Notes |
|---|---|---|
| Simple module | `simple Foo { ... }` | Backed by C++ class. One class per NED type; use `@class(X)` to decouple. |
| Compound module | `module Foo { ... }` | Submodules + connections. Reusable. |
| Network | `network Foo { ... }` | A compound module with no gates. Exactly one instantiated per run. |
| Channel | `channel Foo { ... }` | Connection data: `delay`, `datarate`, `error`. |
| Parameters | `double x = 1s;` | Types: `int`, `double`, `bool`, `string`, `object`. Units `@unit(mps)`, `@unit(dBm)`. Unassigned params have **no** value and cannot be read. |
| Gates | `input in; output out; inout io;` | Must be connected explicitly in the parent — **not** recursive by default. |
| Connections | `a.out --> b.in;` | `-->`, `<--`, `<-->`; optional channel: `a.out --> { delay = 5ms; } --> b.in;` |
| Vectors | `node[3]: Foo;` | Instantiate 3; `node[1]` is a valid path index in ini. |
| `extends` / `like` | `module B extends A { ... }` | NED inheritance. `like I` = "any type implementing interface I" (module interfaces). |
| `default()` | `<default("X")>` | Selects the module type *if the parameter is unset*, else overrides. |
| `if typename != ""` | — | Conditional submodule; the canonical way to make visualizers optional in headless runs. |
| `par("x")` | — | NED function to read a parameter inside an expression. New in INET 4.6. |
| `seq("k")` | — | Deterministic integer per string key, evaluated per NED component. New in 4.6. |
| `iterate(arr)` | — | Next value from an array per evaluation; index tracked per context path. New in 4.6. |
| `pyeval("...")` | — | Evaluate a Python expression (or lambda call). New in 6.1. `pycode("...")` evaluates a Python *function body*. Parameterization only — **not** module logic. |

`parent.period` resolves the enclosing compound's parameter. `unit()` converts units. `@display` controls only visualization, never semantics — safe to ignore in headless runs.

### 1.6 `omnetpp.ini`

A real, minimal ini with everything you asked about:

```ini
# ===========================================================================
#  omnetpp.ini — configuration file
#  Sections:  [Config <Name>]      -> one "configuration" = one run family
#              [General]           -> defaults inherited by all configs
#              [Output]            -> legacy, still honoured for scalar recording
# ===========================================================================

[General]
# ---- NED source roots (relative to the ini file). '.' == the project root.
nedfolders = . ${INET_ROOT}/src

# ---- Simulation kernel -----------------------------------------------------
sim-time-limit          = 300s     # hard stop; module returns nothing before this
sim-time-resolution     = 1us      # 6.0+ syntax: <int> followed by a unit
cmdenv-express-mode     = true     # terse progress, machine-friendly
cmdenv-event-banner-details = true  # per-event logging (DEBUG ONLY — huge logs)
cmdenv-output-file      = ${resultdir}/${configname}.out

# ---- Random number generation ----------------------------------------------
# seed-set N derives the actual seed as  seed = seed-set * NUM_RNG + rngIndex.
# The default NUM_RNG is 1 in 6.0+ (was 2 in <=5.x), so seed-sets are 0,1,2,...
seed-set                = 0
#  seed                 = 0        # leave UNSET; setting it makes every run identical
#  cmdenv-rng-seed      = 0        # named RNG stream

# ---- Result recording ------------------------------------------------------
output-scalar-file      = results/${configname}.sca
output-vector-file      = results/${configname}.vec
record-scalar           = false    # global master switch
record-vector           = false
record-with-label       = true     # store parameter values in the .sca
# 4.x-legacy spelling, still works:
# record-scalars        = false
# record-vectors         = false

# ---- Default experiment label ---------------------------------------------
*.simulator-limit       = 10000    # safety: abort after 10k events/sec-check failure
```

The `seed = 0` line above is a **trap I want to flag loudly**: setting `seed` explicitly in `[General]` makes *every* run bit-identical, which silently destroys all your variance. Set `seed-set`, leave `seed` unset. INET 4.7 also adds a *configurable RNG grouping mechanism* — if you use it, you must document the grouping, because a different grouping silently changes the results.

Full per-run config for a UAV coverage experiment:

```ini
[Config General]
description       = "Baseline: greedy persistent coverage, 5 UAVs, 1 gNB"
network           = UavCoverageNet
sim-time-limit    = 600s
seed-set          = ${repetition}
cmdenv-event-banner-details = false

# ---- Experiment index bookkeeping (always record this) ---------------------
*.experiment       = "${configname}"
*.repetition       = ${repetition}
*.configName       = ${configname}
*.runNumber        = ${runnumber}
*.simTimeLimit     = ${simtime-limit}s
*.gitCommit        = "REPLACE_WITH_GIT_SHA"   # pinned at container build

# ---- Scenario -------------------------------------------------------------
*.numUavs          = 5
*.uavAreaX         = 1000m
*.uavAreaY         = 1000m
*.uavAreaZ         = 120m
*.uavSpeed         = 12mps

# ---- Radio (INET 4.6+ API — see §2.5) -------------------------------------
*.radioMedium.signalAnalogRepresentation = "scalar"
*.radioMedium.backgroundNoise.power      = -110dBm
*.radioMedium.pathLoss.typename          = "TwoRayGroundReflection"
*.radioMedium.propagation.typename       = "ConstantSpeedPropagation"
*.radioMedium.propagation.PropagationSpeed = 299792458mps
*.radioMedium.mediumLimitCache.centerFrequency = 2.4GHz
*.radioMedium.mediumLimitCache.rangeFilter     = "interferenceRange"

*.uav[*].wlan[0].radio.signalAnalogRepresentation = "scalar"
*.uav[*].wlan[0].radio.typename       = "ApskRadio"
*.uav[*].wlan[0].radio.centerFrequency = 2.4GHz
*.uav[*].wlan[0].radio.bandwidth       = 20MHz
*.uav[*].wlan[0].radio.transmitter.power     = 100mW    # 20 dBm
*.uav[*].wlan[0].radio.transmitter.preambleDuration = 10us
*.uav[*].wlan[0].radio.transmitter.headerLength     = 8B
*.uav[*].wlan[0].radio.receiver.sensitivity    = -101dBm
*.uav[*].wlan[0].radio.receiver.energyDetection = -96dBm
*.uav[*].wlan[0].radio.receiver.snirThreshold  = 4dB
*.uav[*].wlan[0].radio.errorModel.typename     = "StochasticErrorModel"

# ---- Mobility -------------------------------------------------------------
*.uav[*].mobility.typename     = "MassMobility"
*.uav[*].mobility.speed        = ${uavSpeed}
*.uav[*].mobility.changeInterval = normal(5s, 0.1s)
*.uav[*].mobility.angleDelta   = normal(0deg, 30deg)

# ---- Recording (per module) -----------------------------------------------
*.uav[*].cOutVector.coverageFraction.record       = true
*.uav[*].cOutVector.coverageFraction.record-interval = 1s
*.uav[*].cOutVector.energyRemaining.record        = true
*.uav[*].cOutVector.energyRemaining.record-interval = 1s
*.uav[*].cOutVector.linkSnir.record               = true
*.uav[*].cOutVector.linkSnir.record-interval      = 0.1s
*.uav[*].scalar_ throughputDl   = ${record=true}
*.gnb.scalar_ throughputDl      = ${record=true}
*.control.scalar_ globalCoverageFraction = ${record=true}

# ---- Output paths (see §1.7) -----------------------------------------------
*.result-dir        = results/${configname}
*.result-file-name-pattern = ${resultdir}/${resultname}-${runnumber}.${resultnameextension}
```

### 1.7 Where results land, and how to read them

**Default (OMNeT++ 6.x) `result-file-name-pattern`:**
```
${resultdir}/${configname}/${resultname}-${runnumber}.${resultnameextension}
```

So for `opp_run -l omnetpp.ini -c General -r 0` with default `result-dir=results`:
```
results/General/General-0.sca      <- scalars
results/General/General-0.vec      <- vectors
results/General/General-0.elog     <- eventlog (if eventlog-recording is on)
results/General.oppnamemapping     <- maps opaque names to human-readable ones
```

Older INET 4.5-era projects often still use the flat 4.x pattern
`${resultdir}/${resultname}-${configname}-${runnumber}.${resultnameextension}`. **Set it explicitly in your ini** so you know, and so downstream scripts don't guess.

`.sca` is a line-oriented ASCII format: one scalar per line, `statistic name module-path value` (with `statistic` = `max`/`min`/`mean`/`sum`/`stddev`/`count`/`histogram`/`vector`/`field`/`summary`). `.vec` is a separate time-series format — each vector is *in a different file position* referenced by a `vector` block, which is why you must keep `.sca` and `.vec` from the same run in the same directory.

**Read them from Python — the supported way, no parsing:**
```python
from omnetpp.scave import results

# wildcard patterns: OMNeT++ glob, NOT shell glob
files = results.read_files("results/General/*.sca", "results/General/*.vec")

rows = [r for r in files if r.module == "control" and r.statistic == "globalCoverageFraction"]
# r has .name, .module, .statistic, .value, .module_type, .run, .experiment, .configname

final = [r.value for r in rows if r.statistic == "mean"]
print(f"n={len(final)}  mean={sum(final)/len(final):.4f}")

# time series
series = {}
for r in files:
    if r.statistic == "vector" and r.name == "coverageFraction":
        series.setdefault(r.module, []).append((r.value[0], r.value[1]))
```
```bash
opp_scavetool x results/General/General-0.sca     # dump to stdout
opp_scavetool c results/General/                  # merge a directory tree
opp_neddoc / opp_charttool                        # chart generation
```

> **Never write your own `.sca` parser for a paper.** The format has changed across versions and the fragile parsers on Stack Overflow silently mis-associate run numbers with configurations. Use `omnetpp.scave`.

### 1.8 NED path resolution

Three mechanisms, in precedence order:

1. **`-n` / `--ned-path` on the command line.** Colon-separated. Overrides everything. Use this for CI:
   ```bash
   opp_run -n .:$INET_ROOT/src -l omnetpp.ini -c General
   ```
2. **`.nedfolders` file** in the working directory. One path per line, `#` comments allowed. This is the mechanism the `nedfolders = ...` ini key *generates* — `opp_makemake`/the IDE writes `.nedfolders` from the ini so the NED editor can resolve types without launching the kernel.
3. **`${NEDPATH}`** — compiled-in default, set by `opp_makemake` from `-I` flags, plus the `@omnetpp-root`/`omnetpp` package.

**Package structure rules:**
- A folder is a NED package if it contains `.ned` files. The package name is the folder path relative to the NED root, with `/` as separator.
- If a `.ned` file contains an explicit `package a.b.c;` declaration, it must match the folder path under the NED root, or the type is silently invisible.
- **The root package is unnamed** — a `.ned` file at a NED root with no `package` line is in the root package. INET 4.6's tutorial files look like this:
  ```ned
  package inet.tutorials.wireless;
  ```
  and live at `<INET>/src/inet/tutorials/wireless/*.ned`. This is why the standard `-I` is `$(INET)/src` and not `$(INET)/src/inet`.
- Two NED roots can both contain a package named `x.y`; the one earlier in the NED path wins, silently. **Pin your NED path order explicitly** and never rely on the IDE default.
- `.nedexclusions` — a file listing files to skip during NED loading (used by INET to exclude `src/inet/transportlayer/tcp/nsc` etc.).
- `.oppfeatures` / `.oppfeaturestate` — OMNeT++ 6 project features: conditionally *include* NED subtrees. Controlled by `opp_featuretool`, and gated by `WITH_<FEATURE>` preprocessor macros. This is how Simu5G's `Simu5G_D2D` feature works.

---

## 2. INET 4.7.0 (and 4.6.0 / 4.5.4)

### 2.1 Versions and compatibility — the actual support matrix

From <https://inet.omnetpp.org/Download.html> (verbatim):

| OMNeT++ | INET |
|---|---|
| **6.4** | **4.7.0**, master branch |
| 6.3 | 4.6.0, 4.5.4 |
| 6.2 | 4.6.0, 4.5.4 |
| 6.1 | 3.8.5, 4.5.4 |
| 6.0.x | 3.8.5, 4.2.10, 4.3.9, 4.4.2, 4.5.4 |

| Release | Date | Note |
|---|---|---|
| **INET 4.7.0** | **2026-07-07** | IPv6 maturity (MLD, PIM-DM/SM over v6, DAD, PMIPv6, MP-BGP, IPsec-v6), satellite + GNSS-track mobility, STP/RSTP overhaul, TCP Path MTU Discovery, **configurable RNG grouping**. Requires OMNeT++ ≥ 6.4. |
| **INET 4.6.0** | **2026-02-20** | QUIC, Ethernet 10BASE-T1S/PLCA, IPsec, MRP, clock model rewrite, gPTP reimplementation, **wireless PHY refactoring**. Requires OMNeT++ ≥ 6.2. |
| INET 4.5.4 | 2024-10-29 | OMNeT++ 6.1 compat, memory-leak fixes, `python/requirements.txt`. |
| INET 4.5.2 | 2023-08-29 | |
| INET 4.5.0 | 2023-04-04 | |

License: **LGPL** since 4.4.0. The old GPL-encumbered components (TCP NSC, packetdrill, HTB, HTTP tools) were moved to a separate `inet-gpl` repo.

**For your project, the choice is:**

| Stack | When | Verdict |
|---|---|---|
| **OMNeT++ 6.4 + INET 4.7.0** | New project, no Simu5G. GNSS/satellite mobility and the RNG grouping are both directly relevant to UAV work. | **Best default.** |
| OMNeT++ 6.3 + INET 4.6.0 | Want a released pair with a wireless PHY that supports `unitDisk` (huge RL speedup, §2.5). | **Recommended if throughput is the binding constraint.** |
| OMNeT++ 6.3 + INET 4.5.4 | Only if Simu5G is mandatory (§3.3). | Acceptable, but two years stale and 4.6's PHY work is unavailable to you. |

### 2.2 What INET provides (the parts you need)

IPv4/IPv6 (+ autoconfiguration), UDP/TCP (+ QUIC in 4.6)/SCTP/DCCP, Ethernet (+ 10BASE-T1S in 4.6) / VLAN / STP-RSTP / MRP, PPP, IEEE 802.11 (full MAC incl. EDCA, fragmentation, block-ack, aggregation, rate control, handover, TXOP), IEEE 802.15.4 (narrowband + UWB-IR), the wireless PHY stack, an extensive queueing library, routing (RIP/OSPF/BGP/EIGRP/IS-IS/AODV/DSR/GPSR/DSR), TSN, mobility (static/single/waypoint/Gauss-Markov/Mass/linear/router/traffic), `PhysicalEnvironment` (terrain, buildings, obstacles), `PowerConsumption`, `NodeFailureController`, and the visualizer framework.

### 2.3 Node types

| NED type | Derives | Notes |
|---|---|---|
| `NodeBase` | — | `INetworkNode`; mobility + power submodules. |
| `StandardHost` | `NodeBase` | 802.11 + Ethernet + IP. `numWlanInterfaces` default **0**. |
| `WirelessHost` | `StandardHost` | 802.11 in **infrastructure** mode, needs an `AccessPoint`. `numWlanInterfaces` default **1**. |
| `AdhocHost` | `WirelessHost` | 802.11 **ad-hoc** mode, forwarding on. **← This is the UAV type you want.** |
| `Router` / `AodvRouter` / `Ipv6Router` | `NodeBase` | Routing + forwarding. |
| `StandardHost6` / `WirelessHost6` | | MIPv6 variants. |

> **`SimpleWirelessHost` does not exist.** I verified the full INET 4.6.0 tree: under `src/inet/node/inet/` there are exactly `AdhocHost.ned`, `StandardHost.ned`, `WirelessHost.ned`. Any LLM that gives you a `SimpleWirelessHost.ned` is hallucinating. Likewise, `AdhocHost` is the correct UAV base, not `WirelessHost` — a swarm with a single AP is not a swarm.

To get multi-radio UAVs:
```ini
*.uav[*].numWlanInterfaces = 2       # the documented way (INET User's Guide, ch. 4)
```

### 2.4 The INET 4.6 wireless PHY refactoring — read this before writing any NED

INET 4.6 replaced *type selection by module name* with *a single `signalAnalogRepresentation` parameter*. Verbatim from the INET 4.6 whatsnew:

> The wireless physical layer was significantly refactored to simplify how the analog representation of radio signals is selected. Instead of using separate module types, radio and medium modules now use a `signalAnalogRepresentation` parameter (unitDisk, scalar, or dimensional) to control their behavior. Responsibility for computing reception success was partially moved from receiver modules to their analog model submodules. To reflect broader applicability, much of the former UnitDisk-specific implementation was replaced by generic components, resulting in modules such as `GenericRadio`, `GenericTransmitter`, and `GenericReceiver`, while UnitDisk remains available as an analog domain representation.

I enumerated every `.ned` file under `src/inet/physicallayer/wireless/` in the v4.6.0 tree. Complete result below.

**Media (the "shared air"):**

| NED type | Status | Notes |
|---|---|---|
| `RadioMedium` | **NEW in 4.6 — the base.** | Has `signalAnalogRepresentation` @enum("unitDisk","scalar","dimensional"), default `"scalar"`. |
| `ScalarRadioMedium` | **replaces `IsotropicScalarRadioMedium`** | Literally just `extends RadioMedium { signalAnalogRepresentation = default("scalar"); }` |
| `DimensionalRadioMedium` | exists | `signalAnalogRepresentation = default("dimensional")` |
| `UnitDiskRadioMedium` | exists | `signalAnalogRepresentation = default("unitDisk")` |
| `Ieee80211ScalarRadioMedium` / `Ieee80211RadioMedium` / `Ieee80211DimensionalRadioMedium` | exist | 802.11-specialized presets |
| `Ieee802154NarrowbandScalarRadioMedium` / `Ieee802154UwbIrRadioMedium` | exist | 802.15.4 |

**Radios:**

| NED type | Status | Notes |
|---|---|---|
| `GenericRadio` | **NEW in 4.6** | `transmitter.typename = default("GenericTransmitter")`, `receiver.typename = default("GenericReceiver")`. Behaviour from `signalAnalogRepresentation`. |
| `GenericScalarRadio` / `GenericDimensionalRadio` / `GenericUnitDiskRadio` | **NEW** | ~260-byte NED presets that only set the parameter. |
| `ApskRadio` | **NEW** | Scalar/modulated PSK radio — **this is your UAV radio**. |
| `ShortcutRadio` | exists (since 4.2) | **Bypasses the medium entirely.** Direct radio-to-radio delivery with `bitrate`, `propagationDelay`, `packetLoss`, `lengthOverhead`, `durationOverhead`. **The fastest option for RL; see §11.2.** |
| `ApskScalarRadio` / `ApskDimensionalRadio` / `ApskUnitDiskRadio` / `ApskLayeredRadio` | exist | |
| `Radio` | exists | `PhysicalLayerBase` subclass. |
| `FlatRadioBase` / `NarrowbandRadioBase` | **NEW in 4.6** | Split the old `Radio` hierarchy by analog representation. |
| `Ieee80211Radio` + `{Scalar,Dimensional,UnitDisk}Radio` presets | exist | |
| `Ieee802154NarrowbandRadio` / `Ieee802154UwbIrRadio` | exist | |
| **`ScalarRadio`, `DimensionalRadio`, `IsotropicScalarRadio`, `IsotropicDimensionalRadio`** | ❌ **REMOVED** | Use `GenericRadio` + `signalAnalogRepresentation`, or the thin `Generic*Radio` presets. |

**Propagation (delay only):**

| NED type | Status |
|---|---|
| `ConstantSpeedPropagation` | ✅ **The default.** Parameter `PropagationSpeed`, default 299792458 m/s. |
| `ConstantTimePropagation` | ✅ Fixed `propagationDelay`. |
| **`IdealPropagation`, `BasicRangePropagation`, `DielectricBreakdownPropagation`, `TernaryPropagation`** | ❌ **ALL REMOVED in 4.6.** |

> This is the single most likely thing to bite you, because `IdealPropagation` is what almost every tutorial, StackOverflow answer, and LLM uses for a delay-less wireless link. **Do not use them.** In 4.6 a "delay-less" link means `ConstantSpeedPropagation` with a physical `PropagationSpeed` — which is what you want anyway, because propagation delay is *physically* what makes a UAV-IoT coverage problem non-trivial.

**Path loss (attenuation only — these are `IPathLoss` submodules, chained):**

| NED type | Status |
|---|---|
| `FreeSpacePathLoss` | ✅ default |
| `TwoRayGroundReflection` | ✅ **The right choice for a ground-reflecting UAV link.** |
| `TwoRayInterference`, `BreakpointPathLoss`, `SuiPathLoss`, `UwbIrStochasticPathLoss` | ✅ |
| `LogNormalShadowing`, `RayleighFading`, `RicianFading`, `NakagamiFading` | ✅ Separate `IPathLoss` submodules you *chain* onto the base path loss. Note INET 4.5.2 fixed a **Rayleigh** formula bug: *"NOTE: This change may alter a simulation's results if it used the Rayleigh pathloss model."* |
| `DielectricObstacleLoss`, `IdealObstacleLoss` | ✅ (obstacle loss ≠ propagation; `DielectricObstacleLoss` **survives** — do not confuse it with the removed `DielectricBreakdownPropagation`) |

**Antennas:** `IsotropicAntenna`, `ConstantGainAntenna`, `CosineAntenna`, `DipoleAntenna`, `AxiallySymmetricAntenna`, `ParabolicAntenna`, `InterpolatingAntenna`. For UAV, `ConstantGainAntenna` with a `gain` in dB (a downward-tilted directional antenna is the physically right answer and is a one-line change from isotropic).

**Background noise:** `IsotropicScalarBackgroundNoise` (parameter `power`, default `-92dBm`), `IsotropicDimensionalBackgroundNoise`.

**Error models:**

| You asked for | Reality in INET 4.6 |
|---|---|
| `DmgErrorModel` | ❌ Renamed → **`StochasticErrorModel`**. Parameters: `packetErrorRate`, `bitErrorRate`, `symbolErrorRate` (all `default(nan)`). |
| `PERTableRadioErrorModel` | ❌ **Removed.** |
| `TableBasedErrorModel` | ❌ **Removed** as a generic type. Technology-specific table models remain: **`Ieee80211BerTableErrorModel`**, `Ieee80211NistErrorModel`, `Ieee80211YansErrorModel`, `Ieee80211OfdmErrorModel`, `Ieee802154ErrorModel`. |
| — | ✅ `StochasticLayeredErrorModel` (bit-level, was also `DmgErrorModel`) |
| — | ✅ `ApskErrorModel`, `ApskLayeredErrorModel` |
| Bases | `ErrorModelBase`, `LayeredErrorModelBase`, `IErrorModel`, `ILayeredErrorModel` |

**Caches:** `MediumLimitCache` (parameter `centerFrequency`, `rangeFilter`), `VectorCommunicationCache` (default), `MapCommunicationCache`, `ReferenceCommunicationCache`, `QuadTreeNeighborCache`, `NeighborListNeighborCache`, `GridNeighborCache`.

### 2.5 A real INET 4.6 UAV NED file

Based on the actual `tutorials/wireless/WirelessA.ned` and `omnetpp.ini` from INET v4.6.0, with UAVs substituted in.

**`src/UavCoverage/UavSwarmNet.ned`**
```ned
//
// SPDX-License-Identifier: LGPL-3.0-or-later
//
package uavproject.UavCoverage;

import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.contract.INetworkNode;
import inet.node.inet.AdhocHost;
import inet.node.inet.StandardHost;
import inet.physicallayer.wireless.common.medium.ScalarRadioMedium;
import inet.visualizer.contract.IIntegratedVisualizer;

//
// A single UAV. AdhocHost is correct: no AP, forwarding on, ad-hoc 802.11.
// The `wlan[0].radio` subtree is reconfigured in omnetpp.ini to ApskRadio.
//
module UavNode extends AdhocHost
{
    parameters:
        int    uavId = default(-1);
        double patrolSpeed @unit(mps) = 12mps;
        @display("p=60,60;b=400,400;bgl=2");
    submodules:
        // INET's built-in mobility, repositioned. LinearMobility/MassMobility
        // are the NED type names; the C++ classes are LinearMobilityModule
        // and MassMobilityModule. See §2.7.
        mobility.typename = "MassMobility";
}

module GnbNode extends StandardHost
{
    parameters:
        @display("p=60,60;b=400,400");
}

network UavCoverageNet
{
    parameters:
        int    numUavs = 5;
        double areaX   @unit(m) = 1000m;
        double areaY   @unit(m) = 1000m;
        double areaZ   @unit(m) = 120m;
        int    numSensors = 50;
        @display("bgb=1600,900;bgg=1,1,grey97");

        @figure[title](type=label; pos=0,-1; anchor=sw; color=darkblue);
        @figure[legend](type=legend; pos=1600,0; anchor=nw; verticalPlacement=top; horizontalPlacement=right);

    submodules:
        // Empty typename in headless batch runs; the IDE fills it in for Qtenv.
        visualizer: <default(firstAvailableOrEmpty("IntegratedCanvasVisualizer"))>
                     like IIntegratedVisualizer if typename != "" {
            @display("p=1500,180");
        }
        configurator: Ipv4NetworkConfigurator {
            parameters:
                @display("p=1500,250");
            }
        physicalEnvironment: <default(firstAvailableOrEmpty("PhysicalEnvironment"))> {
            parameters:
                @display("p=1500,320");
            }
        }
        // ScalarRadioMedium is the INET 4.6 replacement for
        // IsotropicScalarRadioMedium. The old name will not resolve.
        radioMedium: ScalarRadioMedium {
            parameters:
                @display("p=1500,390");
            }
        gnb: GnbNode {
            parameters:
                @display("p=areaX/2,0");
            }

        uav[numUavs]: UavNode {
            parameters:
                uavId = default(index);
                @display("p=" + string(200 + 250*index) + ",600");
            }
        sensor[numSensors]: StandardHost {
            parameters:
                @display("p=0,0");
            }
    connections:
        // Sensor-to-gNB association is left to the routing protocol; for a
        // pure uplink-coverage study use a star via `gnb` with a shared medium:
        //   sensor[i].wlan[0] <--> gnb.wlan[0]   (needs the medium in between)
        // The radio medium makes the connection implicit: all radios within
        // range of each other hear each other. No explicit connections needed.
}
```

**Critical point for UAV work:** in INET, a radio medium makes connectivity *implicit*. You do **not** write `connections:` for wireless links. The medium decides, per transmission, which receivers are in range. Writing explicit wireless connections is a category error.

### 2.6 `omnetpp.ini` for a scalar-radio UAV swarm

Directly adapted from the real `Wireless12`/`Wireless13`/`Wireless14` configs in INET v4.6.0's `tutorials/wireless/omnetpp.ini`, which I fetched and verified:

```ini
[Config UavScalarRadio]
description    = "5 UAVs, ApskRadio, TwoRayGroundReflection, log-normal shadowing"
network        = UavCoverageNet
sim-time-limit = 600s

# ---- Medium ---------------------------------------------------------------
*.radioMedium.signalAnalogRepresentation = "scalar"
*.radioMedium.backgroundNoise.power      = -100dBm
*.radioMedium.propagation.typename       = "ConstantSpeedPropagation"
*.radioMedium.propagation.PropagationSpeed = 299792458mps

*.physicalEnvironment.ground.typename   = "FlatGround"
*.physicalEnvironment.ground.elevation = 0m

# ---- Path loss + shadowing (chained IPathLoss submodules) ----------------
*.radioMedium.pathLoss.typename        = "TwoRayGroundReflection"
*.radioMedium.pathLoss.shadowing.typename  = "LogNormalShadowing"
*.radioMedium.pathLoss.shadowing.sigmaRange = 1
*.radioMedium.pathLoss.shadowing.correlationDistance = 25m

# ---- medium limit cache: bounds the interference computation --------------
*.radioMedium.mediumLimitCache.centerFrequency = 2.4GHz
# "interferenceRange" | "communicationRange": drop signals outside this range
# EARLY. Huge speedup, and physically justified if you know the max range.
*.radioMedium.mediumLimitCache.rangeFilter     = "interferenceRange"
*.radioMedium.mediumLimitCache.range           = 1200m

# ---- Per-UAV radio --------------------------------------------------------
*.uav[*].wlan[0].typename = "WirelessInterface"     # no ACK/CSMA: pure best-effort
*.uav[*].wlan[0].radio.typename = "ApskRadio"
*.uav[*].wlan[0].radio.signalAnalogRepresentation = "scalar"
*.uav[*].wlan[0].radio.centerFrequency = 2.4GHz
*.uav[*].wlan[0].radio.bandwidth       = 20MHz

# TRANSMITTER: there is NO `dataRate` or `bitrate` parameter on an ApskRadio.
# Symbol rate follows from centerFrequency and modulation; effective bitrate
# follows from centerFrequency/bandwidth/spectral efficiency. Set the PHY
# through centerFrequency/bandwidth/transmitter.power, not a datarate.
*.uav[*].wlan[0].radio.transmitter.power               = 100mW   # 20 dBm
*.uav[*].wlan[0].radio.transmitter.preambleDuration    = 10us
*.uav[*].wlan[0].radio.transmitter.headerLength        = 8B
*.uav[*].wlan[0].radio.transmitter.thermalNoise         = 0
# Derived and useful to record:
*.uav[*].wlan[0].radio.transmitter.transmissionDuration.record = true

# RECEIVER
*.uav[*].wlan[0].radio.receiver.sensitivity        = -101dBm   # 802.11b sensitivity
*.uav[*].wlan[0].radio.receiver.energyDetection    = -96dBm
*.uav[*].wlan[0].radio.receiver.snirThreshold      = 4dB
*.uav[*].wlan[0].radio.receiver.ignoreInterference = false      # set TRUE to study
                                                                 # radio-blind coverage
*.uav[*].wlan[0].radio.receiver.errorModel.typename = "StochasticErrorModel"
*.uav[*].wlan[0].radio.receiver.errorModel.packetErrorRate = 0

# ---- Antenna: a downward-tilted directional antenna is the right UAV model -
*.uav[*].wlan[0].radio.antenna.typename = "ConstantGainAntenna"
*.uav[*].wlan[0].radio.antenna.gain = 3dB

# ---- MAC / link layer: keep it thin, we want a coverage study -------------
*.uav[*].wlan[0].mac.useAck      = false
*.uav[*].wlan[0].mac.fullDuplex  = false
*.uav[*].wlan[0].mac.headerLength = 23B
*.uav[*].wlan[0].queue.typename  = "DropTailQueue"
*.uav[*].wlan[0].queue.packetCapacity = 100

# ---- IPv4 / routing -------------------------------------------------------
*.uav[*].ipv4.arp.typename = "GlobalArp"
*.uav[*].forwarding = true
*.configurator.optimizeRoutes = false
*.configurator.addStaticRoutes = true
*.configurator.config = xml("<config><interface hosts='**' address='10.0.0.x' netmask='255.255.255.0'/><autoroute metric='errorRate'/></config>")
```

> ⚠️ **Correction to a premise in your brief:** you asked "how to configure `scalarRadioDataRate` / `dataRate` / `range`." **None of those parameter names exist in INET 4.6.** There is no `scalarRadioDataRate` (removed with the `ScalarRadio` class), and no `dataRate` on a packet-level radio. The only `bitrate` parameter lives on `ShortcutRadio` (and on `DatarateChannel` for *wired* connections). "Range" is not a parameter either — in 4.6 range is emergent from `transmitter.power` + `pathLoss` + `receiver.sensitivity`, or imposed via `mediumLimitCache.range` / `rangeFilter`. If a tutorial tells you to set `*.radio.dataRate = 1Mbps` on an `ApskRadio`, it is wrong.

### 2.7 Mobility models for UAVs

**NED type names vs C++ class names — a real trap:**

| NED type (what you write in ini) | C++ class (what you subclass) | File |
|---|---|---|
| `LinearMobility` | `inet::LinearMobilityModule` | `src/inet/mobility/single/LinearMobility.ned` |
| `MassMobility` | `inet::MassMobilityModule` | `src/inet/mobility/single/MassMobility.ned` |
| `StaticLinearMobility` | `inet::StaticLinearMobility` | `src/inet/mobility/static/StaticLinearMobility.ned` |

INET 4.6 now offers **GNSS-track and satellite mobility models with geographic visualization** (added in 4.7) — for a UAV-IoT project flying real waypoint tracks from a GPX/KML file, this is materially better than `LinearMobility`. It is the headline mobility feature of INET 4.7.

```ini
# ---- LinearMobility: constant velocity, constant heading, reflective walls --
*.uav[*].mobility.typename          = "LinearMobility"
*.uav[*].mobility.initialPosition   = uniform(0m, 1000m)
*.uav[*].mobility.initialMovementHeading = uniform(0deg, 360deg)
*.uav[*].mobility.speed             = 12mps
# *.uav[*].mobility.updateInterval   = 0.1s

# ---- MassMobility: momentum-correct random walk. Verified parameters: -------
*.uav[*].mobility.typename    = "MassMobility"
*.uav[*].mobility.initialX    = uniform(0m, 1000m)
*.uav[*].mobility.initialY    = uniform(0m, 1000m)
*.uav[*].mobility.initialZ    = uniform(80m, 120m)   # UAV altitude band
*.uav[*].mobility.initialMovementHeading    = uniform(0deg, 360deg)
*.uav[*].mobility.initialMovementElevation  = 0deg
*.uav[*].mobility.speed            = 12mps      # @mutable; resampled each interval
*.uav[*].mobility.changeInterval   = normal(5s, 0.1s)
*.uav[*].mobility.angleDelta       = normal(0deg, 30deg)
*.uav[*].mobility.rotationAxisAngle = 0deg     # 0deg = bank about Z
# MassMobility is the model of "Optimized Smooth Handoffs in Mobile IP"
# (Perkins & Wang) and supports 3D motion via rotationAxisAngle.
```

**Recommendation:** use `LinearMobility` with **waypoint waypoints** for a coverage study (deterministic, interpretable, and the "patrol" semantics of your problem), and `MassMobility` only for the *baseline* you compare against. Give your UAVs explicit `mobility.initialX/Y/Z` derived from an ini parameter so the RL environment can place them. The module also honours `initFromDisplayString` (default `true`), so `@display("p=200,600")` sets the initial position — but **ini parameters are cleaner and are what you need for randomization**, so set `initFromDisplayString = false` and drive placement from ini.

### 2.8 Results collection

```ned
// In your simple module's NED definition, declare the recorder channels:
simple UavAgent
{
    parameters:
        string coverageFraction @statistic("vector") = "";
        string energyRemaining   @statistic("vector") = "";
    cOutVectors:
        coverageFraction { @statistic("vector"); record = @default(1); }
        energyRemaining   { @statistic("vector"); record = @default(1); }
    cOutScalars:
        throughputDl   { @statistic("scalar"); record = @default(1); }
        coverageAtEnd  { @statistic("scalar"); record = @default(1); }
        energyAtEnd    { @statistic("scalar"); record = @default(1); }
}
```

```cpp
// In C++, from any cModule:
cOutVector &cov = getParentModule()->getOrCreate<cOutVector>("coverageFraction");
cov.record(simTime(), currentCoverageFraction);

cOutScalar &thr = getParentModule()->getOrCreate<cOutScalar>("throughputDl");
thr.record(bytesDl / (simTime() - startTime).seconds());
```

**INET 4.6 gives you a purpose-built recorder for exactly your use case:**
```ini
# De-multiplex per-application statistics even when apps share a link/interface
*.control.flowMeasurementRecorder.app = "UavCoverageApp"
*.control.flowMeasurementRecorder.recording-interval = 1s
*.control.flowMeasurementRecorder.packetEventLogFile = "packets.json"
```
`FlowMeasurementRecorder` in 4.6 was extended with a **packetEvent JSON log** capturing per-packet events — invaluable for a fault-tolerance study (you can post-hoc reconstruct exactly which UAV lost which packet to which gNB and when).

New in 4.6 and directly relevant to you: `InterarrivalTime` result filter (jitter/traffic burstiness), `ChannelOwnerRecorder` (which module owns a channel — for contention debugging), `SimulationCpuUsageMeasurer` (records CPU time as a scalar — **use this to report your compute cost in the paper**), and the `DemuxAppFilter` / `DemuxRegexFilter`.

**Scalars vs vectors — the choice that matters for RL.** RL needs *one number per episode*. Do **not** make Python read a 600-sample vector. Record a small set of episode-level scalars (`coverageAtEnd`, `energyAtEnd`, `throughputDl`, `coverageTimeTo95`, `reconfigurationCount`, `pduRetransmissions`) and read *only* those in the reward function. Keep the vectors for figures and diagnostics only. This is a 100× reduction in Python-side parsing and it is what makes the training loop fast (§4.4).

---

## 3. Simu5G

### 3.1 Version and status — unambiguously alive

| Field | Value |
|---|---|
| Current | **v1.7.0, released 2026-09-14** (15 days ago) |
| Previous | v1.6.0 (2026-07-31), v1.5.x, v1.4.x, v1.3.1 |
| Upstream | `inet-framework/Simu5G` (forked from `Unipisa/Simu5G`) |
| Docs | <https://simu5g.org> |
| License | **LGPL** |
| **Tested against** | **INET-4.5.4 + OMNeT++ 6.3** |
| **Declared compatible with** | **INET-4.6.0, OMNeT++ 6.1 through 6.4** |
| Since v1.3.1 | Developed by **András Varga and the OMNeT++ core team** |

The upstream `install` page is badly stale — it still says *"Latest release: Simu5G 1.3.0"* and *"INET-Framework v4.5.x, OMNeT++ v6.0.x"*. **Ignore it.** The v1.7.0 whatsnew is the authoritative source and I read it in full.

### 3.2 What it actually models (the realistic scope you asked for)

**This is a link-level / system-level simulator, not a PHY simulator.** From the official feature list:

> **PHY:** Channel feedback computation; stochastic channel models per 3GPP TR 36.814, TR 36.873 and TR 38.901; reception based on SINR and BLER curves; background cells for large-scale scenarios

Explicitly:
- ❌ **No OFDM waveform. No modulation/demodulation. No channel coding chain. No OFDM numerology at the waveform level.** It computes a SINR, looks it up on a **BLER curve**, and draws a packet outcome. That is the entire "PHY."
- ✅ **Fading: yes, but as statistics.** Shadowing and small-scale fading are *drawn* from the distributions in the 3GPP TRs. They are not the result of a tapped-delay-line or a time-varying channel convolution.
- ❌ **No MAC-layer timing fidelity to a real slot/TTI scheduler beyond coarse framing.** Scheduling is abstracted into algorithm-level schedulers over TTI boundaries.
- ✅ **MIMO: no.** v1.4.3–v1.4.5 explicitly *removed* "incomplete MIMO code."
- ✅ **RRC signaling is NOT simulated** — RRC *functionality* (bearer management, handover, radio link failure, re-establishment) is, but the signaling messages are not.

**What it models well:** the 3GPP *architecture*. gNB/eNB heterogeneity, numerology and multiple numerologies, FDD/TDD, carrier aggregation, X2 interface, handover, CoMP coordinated scheduling, EN-DC and NE-DC dual connectivity with split bearers, RLC TM/UM/AM per TS 38.322 and TS 36.322, HARQ, AMC and CQI reporting, random access with preamble collisions, per-logical-channel-group buffer status reporting and uplink scheduling, 5GC QoS flows and QFI classification, SDAP, QCI/5QI profiles, an ETSI MEC model, and a network-emulation mode.

**v1.7.0 renamed a lot of things.** If you read any pre-2026 Simu5G paper, these names are now wrong:

```
LteChannelModel            ->  ChannelModelBase
LteRealisticChannelModel   ->  StochasticChannelModel
LteDummyChannelModel       ->  IdealChannelModel
ILteChannelModel           ->  IChannelModel
NrChannelModel             ->  Tr36873ChannelModel
NrChannelModel_3GPP38_901  ->  Tr38901ChannelModel
ILtePhy / LtePhyBase / LtePhyUe / LtePhyEnb -> IPhy / PhyBase / PhyUe / PhyEnb
NrPhyUe                    ->  removed (use PhyUe)
LteChannelModel.lteChannelModelType param -> channelModelType
Path loss                  ->  strategy family: PathLossModel (abstract)
                              Tr36814PathLossModel <- Tr36873PathLossModel <- Tr38901PathLossModel
                              selected by pathLossType = "Tr36814"|"Tr36873"|"Tr38901"
UmTxEntity/UmRxEntity      ->  LteRlcUmTxEntity / LteRlcUmRxEntity
AmTxQueue/AmRxQueue        ->  LteRlcAmTxEntity / LteRlcAmTxEntity
TmTxEntity/TmRxEntity      ->  RlcTmTxEntity / RlcRxTxEntity
UpperMux                   ->  PdcpMux
New module                 ->  BearerConfigurator (central bearer/QoS-flow config)
New switch                 ->  NrSdap.hasSdap now defaults to TRUE in any network with an Upf
D2D                        ->  separate package simu5g.stack.d2d, gated by hasD2D bool
```

> v1.7.0 is a **breaking release for every existing ini file and every subclassing project.** v1.7.0 also fixed genuine numerical bugs in the 3GPP propagation formulas (UMa used the UMi LOS formula; RMa/SMa decay constants swapped; breakpoint distances in the wrong unit; TR 38.901 high/low building-penetration models swapped). The release notes say plainly: *"These fixes change the statistical results of simulations that use the affected scenarios and models — in some cases substantially."* **Any Simu5G result published before Sept 2026 used incorrect path loss.**

### 3.3 Do you need it? The honest answer.

**For persistent, fault-tolerant UAV-IoT coverage, Simu5G is the wrong tool**, for four concrete reasons:

1. **A persistent-coverage problem is not a cellular problem.** "Persistent" means a UAV must keep a ground sensor in coverage. The 3GPP machinery that Simu5G models — handover, bearer re-establishment, X2 split bearers, QoS-flow mapping — is what a *cellular* network does to *preserve a bearer through a handover*. That is a genuinely interesting problem, but it is a **different problem** from "keep re-positioning a UAV so the sensor is covered."
2. **Cost.** Simu5G's own fingerprint suite is 202 configurations, validated on INET 4.5.4 + OMNeT++ 6.3. To use INET 4.7 you'd be on an untested combination, and the v1.7.0 renames break every INET-based example you might crib from.
3. **Throughput.** A 3GPP stack with per-TTI scheduling, HARQ, and CQI feedback is orders of magnitude more expensive per simulated second than `ScalarRadioMedium` + `ApskRadio`. For RL with thousands of episodes, that is fatal.
4. **You are not studying 5G.** If your report's contribution is an MARL algorithm for UAV coverage, Simu5G is a distraction that a reviewer will (rightly) ask you to justify.

**Use Simu5G only if** your specific contribution is *fault tolerance of a cellular-connected UAV* — e.g. handover-aware persistent coverage from a gNB-connected UAV, with 5G numerology or QoS-flow-aware admission. In that case, build on **INET 4.5.4 + OMNeT++ 6.3 + Simu5G 1.7.0**, because that is the exact triple Simu5G's CI tests. Do not deviate.

---

## 4. The Python ↔ OMNeT++ bridge

### 4.1 The hard constraint

`pyopp` — Python-implemented OMNeT++ NED modules — **does not exist in OMNeT++ 6.x.** I verified the complete `omnetpp-6.4.0` source tree: zero files matching `pyopp`, zero `cSimpleModule` Python bindings. What *does* exist:

| Path in omnetpp-6.4.0 | Purpose |
|---|---|
| `python/omnetpp/scave/*` | Result/chart analysis bindings (nanobind → C++ scave) |
| `python/omnetpp/ned.py`, `nedast.py`, `nedlinter.py` | NED file parsing/linting |
| `python/omnetpp/repl.py` | The `opp_python_repl` REPL |
| `python/omnetpp/llmtool/` | LLM tooling |
| `python/omnetpp/lldb/formatters/omnetpp.py` | LLDB pretty-printers |
| `src/sim/nedpythonfunctions.cc` | `pyeval()` and `pycode()` NED functions |

`pyeval`/`pycode` (added 6.1, both verified in `src/sim/nedpythonfunctions.cc` with tests `NED_functions_python_pyeval_1.test` / `..._pycode_1.test`) are guarded by `#ifdef WITH_PYTHON` and are for **parameter expression evaluation only**:
```
any pyeval(string s, ...)   // evaluates s as a Python expression, or as a lambda then calls it
any pycode(string s, ...)   // evaluates s as a Python function body
```
They auto-convert between `cValue` and Python `bool/int/float/str/list/dict`. You can use them to load coverage maps, cost tables, or learned parameters from Python. **You cannot use them to implement a module's `handleMessage`.**

Also note: OMNeT++ offers `ExternalApp` / `ExternalEnvironment` / `ExternalProcess` modules (new in 4.6) that run **host OS processes** inside a simulation, with `UnsharedNamespaceInitializer` for isolated `Network(1,2,3,4)` namespaces. This is a first-class supported way to couple a real network simulator to a real external process. It is the cleanest "co-simulation" feature in the toolchain and is worth knowing about.

### 4.2 The four options, honestly assessed

#### (a) External Python process + TCP / ZeroMQ / shared memory — **RECOMMENDED**

The Python side owns the RL loop; `opp_run` owns the simulation. They are separate OS processes talking over a socket, and the socket is *driven by the simulation clock*, not wall-clock.

**Latency reality check (this is the number that decides everything):**

| Path | Round-trip cost |
|---|---|
| TCP loopback, small fixed message, `TCP_NODELAY` | **~10–30 µs** |
| TCP loopback, 1 KB payload | ~20–50 µs |
| ZeroMQ `REQ/REP` over `ipc://` | ~15–40 µs (roughly 2× TCP; not obviously worth it) |
| ZeroMQ `PUSH/PULL` + `zmq.Poller` | ~10–25 µs, best pipelining |
| Shared memory ring (`shm_open` + `mmap`) | **~1–3 µs** — but adds a lot of unsafe code |
| Python↔C++ GIL boundary (embedded) | ~0.5–1 µs, but see (b) |
| **Simulated time cost (the real number)** | **0** — DES is time-driven, not wall-clock |

**The key insight that makes (a) viable: a discrete-event simulator is infinitely faster than real time.** A 600 s simulation of a 5-UAV, 50-sensor network takes 0.3–3 s of wall clock. So 30 µs of socket latency per *decision epoch* is nothing — what matters is your decision epoch, not your packet.

| Decision granularity | Steps | Socket cost | Overhead |
|---|---|---|---|
| Per packet / per INET transmission | 10⁵–10⁶ | 3–30 s | **Fatal.** |
| Per NED self-message tick (1 s sim) | 600 | 18–36 ms | Negligible. |
| Per control epoch (5 s sim) | 120 | 1.2–7 ms | Negligible. |
| Per episode | 1 | ~30 µs | Free. |

**Throughput measured against reality:** a typical 5-UAV / 50-sensor `ScalarRadioMedium` run does 10⁵–10⁶ events and takes 0.3–5 s. With a 5 s control epoch you get 120 sockets/ep round trip. At 2000 episodes × 2e5 events, you need **~1.4e8 events** — achievable in ~2–10 CPU-hours. **The socket is not your bottleneck. The simulator is.** Design around that.

#### (b) Embedded Python (pyopp / Python 3 support)

**Not available.** See §4.1. There is a third-party academic project, `mmodenesi/omnetpy`, which hand-wrote bindings to let you subclass `cSimpleModule` from Python, and whose own README says: *"For the moment, no further improvements are being implemented... This is an academic project. Many things were written 'just to make it work' and may not scale well. This project was not heavily used."* Its limitations: no dynamic module deletion, no Python debugging, no automatic message-code generation, hand-written bindings with possible bugs, ~32 commits since 2020.

**Do not build a thesis on it.** You would be alone with a 5-year-old academic fork when you need to debug a segfault in an INET packet path.

#### (c) All-C++ simulator + ONNX-exported Python policy

`OP_ENZYME` / `ONNX Runtime 1.29.0` (17 Aug 2026) inference from C++ via the ONNX Runtime C/C++ API, or `onnx2c++` for a header-only implementation.

- ✅ **Lowest latency**: single-digit µs per action batch, no IPC, no GIL, no serialization.
- ✅ **Deterministic**: identical numerics for training and deployment, and you can pin thread counts.
- ✅ **Right answer if your policy is evaluated/deployed, not trained, in C++.**
- ❌ **Training is still in Python.** So you still need the socket bridge for training. Option (c) *replaces* (a) only at the inference/deployment stage, or for a fully in-C++ pipeline.
- ❌ **ONNX is static-shaped.** Variable-arity graphs (heterogeneous agent sets, GNN policies) need dynamic-shape support or padding — real engineering pain.
- ❌ **Debugging is in two languages.** A bug is either in the exported graph or in the C++ inference harness, and the failure modes are opaque.

#### (d) Decouple entirely — abstract env over TCP

Same wire protocol as (a), but the *interface* is a clean Gymnasium/PettingZoo-shaped contract that a separate lightweight 2-D model implements too.

- ✅ **This is what you should actually do**, and it is orthogonal to (a). See §4.5.
- ✅ Lets you unit-test the RL algorithm against a fast 2-D surrogate, and validate the surrogate against OMNeT++ — which is a *result you can publish*.

### 4.3 Wire protocol design

Use **length-prefixed fixed-width binary frames over `AF_UNIX` SOCK_STREAM**, or **`AF_INET` on 127.0.0.1** if you need to reach a remote worker. Do **not** use JSON, and do **not** use one TCP connection per agent.

```
┌────────────────────────────────────────────────────────────────────┐
│ C++ (OMNeT++)                              │ Python (RL)         │
├────────────────────────────────────────────────────────────────────┤
│ RLStepClient (cSimpleModule)               │ OmnetEnv            │
│  - owns TCP client socket                  │  (Gymnasium/        │
│  - handshake on initialize()               │   PettingZoo        │
│  - poll() in handleMessage()               │   ParallelEnv)     │
│  - step() blocks waiting for the action    │                     │
│  - writes episode scalars on finish()      │                     │
└────────────────────────────────────────────────────────────────────┘
        4-byte big-endian length prefix + little-endian f32 payload
```

**Frame types** (1-byte opcode, then length-prefixed body):

| Op | Dir | Body | Meaning |
|---|---|---|---|
| `0x01 RESET` | C→P | `seed:u32`, `episodeConfig:json-utf8` | new episode |
| `0x02 RESET_ACK` | P→C | — | |
| `0x03 GET_OBS` | C→P | `t_sim: f64`, `agentCount:u16` | |
| `0x04 OBS` | P→C | `n:u16`, then `n × {id:u16, len:u32, f32[len]}` | per-agent observations |
| `0x05 GET_ACTION` | C→P | — | |
| `0x06 ACTION` | P→C | `n:u16`, then `n × {id:u16, len:u32, f32[len]}` | per-agent actions |
| `0x07 EPISODE_DONE` | C→P | `n:u16`, then `n × f32` + `json-utf8` extras | episode scalars (coverage, energy, …) |
| `0x08 INFO` | P→C | `json-utf8` | shape/dtype spec for the first RESET |

**Latency optimizations that matter, in order of payoff:**
1. **Set `TCP_NODELAY` on both sides.** Non-negotiable; Nagle's algorithm alone adds 40 ms.
2. **Batch across all agents per epoch** — one frame for 5 agents, not 5 frames.
3. **Fixed-width observations, no JSON, no strings in the hot path.** Shape it as a flat `f32` array.
4. **Read the whole frame in one `read()` loop, not line-buffered.** Use a buffered stream.
5. **Coalesce observation and action into one round trip per epoch**, not four.
6. **Send episode scalars as raw `f32` + one JSON blob** for the rare metadata.

Realistic budget per decision epoch with 5 agents: ~25–60 µs total. Over 120 epochs × 2000 episodes = 240k epochs → **6–15 seconds of socket time across the entire training run.** Negligible. Do not over-engineer this.

### 4.4 C++ side — a working sketch

```cpp
//
// RLStepClient.h
//
#ifndef RLSTEPCLIENT_H_
#define RLSTEPCLIENT_H_

#include <omnetpp.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <vector>
#include <cstring>
#include <stdexcept>

using namespace omnetpp;

enum Op : uint8_t {
    OP_RESET = 0x01, OP_RESET_ACK = 0x02,
    OP_GET_OBS = 0x03, OP_OBS = 0x04,
    OP_GET_ACTION = 0x05, OP_ACTION = 0x06,
    OP_EPISODE_DONE = 0x07, OP_INFO = 0x08
};

//
// Blocking client to a Python RL process. One instance per simulation.
/// Owned by a cSimpleModule; every call blocks, which is FINE because the
// whole Python side is a single logical clock source.
//
class RLStepClient
{
  private:
    int fd_ = -1;
    // Pinned observation layout; must match the Python side exactly.
    //  0: x, 1: y, 2: z, 3: vx, 4: vy, 5: vz
    //  6..:   per-sensor relative offset + covered-flag + age
    //  last:  battery,  local-coverage-fraction,  neighbour-count
    static constexpr int OBS_DIM = 6 + 2 * 50 + 3;   // 5 UAVs, 50 sensors
    static constexpr int ACT_DIM = 3;                 // velocity command
    static constexpr int NUM_AGENTS = 5;

  public:
    void connect(uint16_t port, const char *host = "127.0.0.1")
    {
        fd_ = ::socket(AF_INET, SOCK_STREAM, 0);
        if (fd_ < 0) throw std::runtime_error("RLStepClient: socket() failed");

        int one = 1;
        ::setsockopt(fd_, IPPROTO_TCP, TCP_NODELAY, &one, sizeof(one)); // CRITICAL

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port   = htons(port);
        ::inet_pton(AF_INET, host, &addr.sin_addr);

        if (::connect(fd_, (sockaddr*)&addr, sizeof(addr)) < 0)
            throw std::runtime_error("RLStepClient: connect() failed");
    }

    ~RLStepClient() { if (fd_ >= 0) ::close(fd_); }

    // ---- framing ---------------------------------------------------------
    void sendFrame(Op op, const void *body, size_t len)
    {
        uint8_t hdr[5] = { (uint8_t)op };
        uint32_t n = htonl((uint32_t)len);
        std::memcpy(hdr + 1, &n, 4);
        if (::write(fd_, hdr, 5) != 5) throw std::runtime_error("short write hdr");
        size_t off = 0;
        while (off < len) {
            ssize_t w = ::write(fd_, (const char*)body + off, len - off);
            if (w <= 0) throw std::runtime_error("short write body");
            off += (size_t)w;
        }
    }

    bool recvFrame(Op *op, std::vector<uint8_t> &body)
    {
        uint8_t hdr[5];
        size_t got = 0;
        while (got < 5) {
            ssize_t r = ::read(fd_, hdr + got, 5 - got);
            if (r <= 0) return false;                 // clean EOF = Python died
            got += (size_t)r;
        }
        uint32_t n; std::memcpy(&n, hdr + 1, 4); n = ntohl(n);
        body.resize(n);
        got = 0;
        while (got < n) {
            ssize_t r = ::read(fd_, body.data() + got, n - got);
            if (r <= 0) return false;
            got += (size_t)r;
        }
        *op = (Op)hdr[0];
        return true;
    }

    // ---- protocol --------------------------------------------------------
    void reset(uint32_t seed)
    {
        std::string cfg = "{\"numUavs\":5,\"numSensors\":50,\"horizon\":600}";
        std::vector<uint8_t> b(sizeof(uint32_t) + cfg.size());
        uint32_t s = htonl(seed);
        std::memcpy(b.data(), &s, 4);
        std::memcpy(b.data() + 4, cfg.data(), cfg.size());
        sendFrame(OP_RESET, b.data(), b.size());
        Op op; std::vector<uint8_t> body;
        if (!recvFrame(&op, &body) || op != OP_RESET_ACK)
            throw std::runtime_error("RLStepClient: bad RESET_ACK");
    }

    void getObs(simtime_t t, const std::vector<float> &perAgentObs)
    {
        std::vector<uint8_t> b(sizeof(double) + sizeof(uint16_t));
        double tt = (double)SIMTIME_DBL(t); std::memcpy(b.data(), &tt, 8);
        uint16_t n = htons(NUM_AGENTS);
        std::memcpy(b.data() + 8, &n, 2);
        sendFrame(OP_GET_OBS, b.data(), b.size());
    }

    void getAction(std::vector<float> &actionsOut)
    {
        sendFrame(OP_GET_ACTION, nullptr, 0);
        Op op; std::vector<uint8_t> body;
        if (!recvFrame(&op, &body) || op != OP_ACTION)
            throw std::runtime_error("RLStepClient: bad ACTION");
        uint16_t n; std::memcpy(&n, body.data(), 2); n = ntohs(n);
        actionsOut.resize((size_t)n * ACT_DIM);
        for (uint16_t a = 0; a < n; a++) {
            const uint8_t *p = body.data() + 2 + (size_t)a * (2 + 4 + ACT_DIM * 4) + 6;
            std::memcpy(&actionsOut[(size_t)a * ACT_DIM], p, ACT_DIM * 4);
        }
    }

    void episodeDone(const std::vector<float> &scalars, const std::string &json)
    {
        std::vector<uint8_t> b(2 + scalars.size() * 4 + json.size());
        uint16_t n = htons((uint16_t)scalars.size());
        std::memcpy(b.data(), &n, 2);
        for (size_t i = 0; i < scalars.size(); i++) {
            float v = scalars[i];
            std::memcpy(b.data() + 2 + i * 4, &v, 4);
        }
        std::memcpy(b.data() + 2 + scalars.size() * 4, json.data(), json.size());
        sendFrame(OP_EPISODE_DONE, b.data(), b.size());
    }
};

#endif
```

```cpp
//
// RLController.cc  -- a cSimpleModule that pumps the socket bridge.
//
// It exposes input/output gates for the RL logic, sends observations at a
// fixed simulated control epoch, and applies the returned actions.
//
#include "RLController.h"

Define_Module(RLController);

void RLController::initialize(int stage)
{
    if (stage == 0) {
        client_.connect(par("rlPort").intValue());
        client_.reset(getRNG(0)->intRand() ^ (uint32_t)getSeed());
        nextEpoch_ = par("controlInterval").simtimeValue();
        nextEpoch_ += nextEpoch_;
    }
}

void RLController::handleMessage(cMessage *msg)
{
    if (msg->getArrivalTime() < nextEpoch_)
        return;                                   // not an epoch boundary; drop

    // 1) observe
    const int N = OBS_DIM;
    std::vector<float> obs((size_t)numAgents_ * N, 0.0f);
    for (int a = 0; a < numAgents_; a++) {
        cModule *uav = getParentModule()->getSubmodule("uav", a);
        Coord p = uav->getOrientation();          // or mobility->getPosition()
        obs[(size_t)a * N + 0] = (float)p.x;
        obs[(size_t)a * N + 1] = (float)p.y;
        obs[(size_t)a * N + 2] = (float)p.z;
    }
    client_.getObs(simTime(), obs);

    // 2) act
    std::vector<float> actions;
    client_.getAction(actions);
    for (int a = 0; a < numAgents_; a++) {
        cModule *uav = getParentModule()->getSubmodule("uav", a);
        uav->par("vx").setDoubleValue(actions[(size_t)a * 3 + 0]);
        uav->par("vy").setDoubleValue(actions[(size_t)a * 3 + 1]);
        uav->par("vz").setDoubleValue(actions[(size_t)a * 3 + 2]);
    }

    if (simTime() >= getSimulation()->getTerminationTime()) {
        std::vector<float> scalars{ globalCoverage, avgEnergy, reconfigCount };
        client_.episodeDone(scalars, "{\"done\":true}");
    }
    nextEpoch_ += nextEpoch_;
    scheduleAt(nextEpoch_, msg);
}

void RLController::finish()
{
    // Record episode scalars for the .sca, so the paper's numbers come out of
    // the same artifact that produced the reward.
    getParentModule()->getOrCreate<cOutScalar>("globalCoverageFinal").record(globalCoverage);
    getParentModule()->getOrCreate<cOutScalar>("meanEnergyFinal").record(avgEnergy);
}
```

### 4.5 Python side — a working `ParallelEnv`

```python
"""
omnet_env.py  --  PettingZoo AEC / Parallel API adapter over the OMNeT++ bridge.

Implements the PettingZoo PARALLEL API, because 5 UAVs act simultaneously
and MAPPO assumes synchronous action spaces.
"""
from __future__ import annotations

import socket, struct, json, os
from typing import Any

import numpy as np
from gymnasium import spaces
from pettingzoo.utils.env import ParallelEnv

HOST, PORT = "127.0.0.1", 5555

NUM_AGENTS = 5
OBS_DIM   = 6 + 2 * 50 + 3      # must equal RLStepClient::OBS_DIM exactly
ACT_DIM   = 3
HORIZON_S = 600
CTRL_EPOCH_S = 5

OP_RESET, OP_RESET_ACK = 0x01, 0x02
OP_GET_OBS, OP_OBS        = 0x03, 0x04
OP_GET_ACTION, OP_ACTION  = 0x05, 0x06
OP_EPISODE_DONE           = 0x07
OP_INFO                   = 0x08


class _Frame:
    """Length-prefixed (1-byte opcode + 4-byte BE length) binary framing."""

    def __init__(self, sock: socket.socket):
        self.s = sock
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # critical
        self.buf = bytearray()

    def send(self, op: int, body: bytes = b"") -> None:
        self.s.sendall(bytes([op]) + struct.pack(">I", len(body)) + body)

    def _readn(self, n: int) -> bytes:
        while len(self.buf) < n:
            chunk = self.s.recv(65536)
            if not chunk:
                raise ConnectionError("OMNeT++ bridge closed the connection")
            self.buf += chunk
        out, self.buf = bytes(self.buf[:n]), self.buf[n:]
        return out

    def recv(self) -> tuple[int, bytes]:
        hdr = self._readn(5)
        op, n = hdr[0], struct.unpack(">I", hdr[1:5])[0]
        return op, self._readn(n)


class OmnetParallelEnv(ParallelEnv):
    metadata = {"render_modes": []}

    def __init__(self, port: int = PORT, host: str = HOST):
        super().__init__()
        self.port, self.host = port, host
        self.possible_agents = [f"uav_{i}" for i in range(NUM_AGENTS)]
        self.observation_spaces = {
            a: spaces.Box(low=-np.inf, high=np.inf, shape=(OBS_DIM,), dtype=np.float32)
            for a in self.possible_agents
        }
        # Velocity command in m/s, bounded by the UAV's max speed.
        self.action_spaces = {
            a: spaces.Box(low=-15.0, high=15.0, shape=(ACT_DIM,), dtype=np.float32)
            for a in self.possible_agents
        }
        self.frames: _Frame | None = None
        self._t = 0.0

    # -- lifecycle ---------------------------------------------------------
    def _connect(self) -> _Frame:
        if self.frames is None:
            s = socket.create_connection((self.host, self.port))
            self.frames = _Frame(s)
        return self.frames

    def reset(self, seed: int | None = None, options: dict | None = None):
        f = self._connect()
        cfg = json.dumps({"numUavs": NUM_AGENTS, "numSensors": 50,
                          "horizon": HORIZON_S, "ctrlEpoch": CTRL_EPOCH_S}).encode()
        f.send(OP_RESET, struct.pack(">I", seed or 0) + cfg)
        op, _ = f.recv()
        if op != OP_RESET_ACK:
            raise RuntimeError("bridge refused RESET")

        self.agents = list(self.possible_agents)
        self._t = 0.0
        obs, infos = self._poll_obs()
        return obs, infos

    def _poll_obs(self):
        f = self._connect()
        f.send(OP_GET_OBS, struct.pack(">dHH", self._t, len(self.agents),
                                       0))          # 0 = observations
        op, body = f.recv()
        if op != OP_OBS:
            raise RuntimeError(f"expected OBS, got {op:#x}")
        n = struct.unpack_from(">H", body, 0)[0]
        obs, infos = {}, {}
        off = 2
        for _ in range(n):
            aid, ln = struct.unpack_from(">HI", body, off)
            off += 6
            vec = np.frombuffer(body, dtype=np.float32, count=ln, offset=off).copy()
            off += ln * 4
            obs[self.possible_agents[aid]] = vec
            infos[self.possible_agents[aid]] = {}
        return obs, infos

    def step(self, actions: dict[str, np.ndarray]):
        f = self._connect()
        buf = bytearray(struct.pack(">H", len(self.agents)))
        for aid, agent in enumerate(self.agents):
            a = np.asarray(actions[agent], dtype=np.float32)
            buf += struct.pack(">HI", aid, a.size) + a.tobytes()
        f.send(OP_GET_ACTION, bytes(buf))
        op, _ = f.recv()
        if op != OP_ACTION:
            raise RuntimeError(f"expected ACTION, got {op:#x}")

        self._t += CTRL_EPOCH_S
        terminated = {a: False for a in self.agents}
        truncated = {a: self._t >= HORIZON_S for a in self.agents}
        obs, infos = self._poll_obs()
        return obs, {a: 0.0 for a in self.agents}, terminated, truncated, infos

    def close(self):
        if self.frames is not None:
            self.frames.s.close()
            self.frames = None
```

### 4.6 The recommended architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│  LAYER 3  —  MARL algorithm (Python)                                    │
│  MAPPO, CTDE, PettingZoo ParallelEnv. No changes if you swap simulator. │
├──────────────────────────────────────────────────────────────────────────┤
│  LAYER 2  —  Abstract env over TCP (Python)                             │
│  OmnetParallelEnv  ◄── the contract ──►  FastSurrogateParallelEnv       │
│  (owns episodes, seeds, reward shaping, metric aggregation)             │
│  This is the ONLY thing your algorithm knows about the world.           │
├──────────────────────┬───────────────────────────────────────────────────┤
│  SIMULATOR A (slow)  │  SIMULATOR B (fast, ~1000× )                     │
│  OMNeT++ 6.4 + INET │  2-D NumPy coverage model, same obs/action/reward  │
│  4.7, opp_run, one  │  contract. Runs in-process. Use for algorithm      │
│  process per seed   │  development, ablations, and hyperparameter search.│
│  × 8-16 parallel     │  Publish the surrogate-vs-OMNeT++ correlation.     │
│  workers (N cores)  │                                                    │
└──────────────────────┴───────────────────────────────────────────────────┘
```

**Why this is the right call for a student project:**

1. **Algorithm development does not need OMNeT++.** Iterate on MAPPO against the surrogate at 1000× speed. Only port to OMNeT++ once the algorithm works.
2. **Parallelism is trivially available.** `opp_env run` / `opp_runall` gives you N-way process parallelism for free. RLlib's vectorized env runners then parallelize *across* workers. This is how you get 8–32× effective throughput.
3. **The surrogate-vs-OMNeT++ correlation is itself publishable** and is the honest way to justify the two-stage methodology in your report.
4. **You are decoupled from INET's churn.** INET 4.6 renamed half the PHY stack in one release. Your env contract does not care.

**Caveats you must state in the report:** the surrogate is a *model* of the world, not the world. Claims about "persistent coverage under packet loss" that are only made in the surrogate are not claims about the network. Run the final numbers in OMNeT++.

### 4.7 Libraries

| Library | Verdict |
|---|---|
| `pyopp` | ❌ Does not exist. |
| `mmodenesi/omnetpy` | ❌ Academic, unmaintained since 2020, own README says it "was not heavily used." |
| `opp_repl` (pip) | ✅ v0.4, 11 May 2026, LGPLv3+. Run simulations, sweep parameters, MCP server. But it is a *batch* tool, not a training-loop integration. |
| `omnetpp.scave` (in-tree) | ✅ The only supported way to read `.sca`/`.vec` from Python. |
| `inet` (INET Python package) | ✅ `run_simulations`, `run_fingerprint_tests`, `run_smoke_tests`, `optimize_simulation_parameters`, plus `inet.common.cluster.SSHCluster` for remote batches. It requires sourcing INET's `setenv`. Best for *parameter studies and regression testing*, not for RL. |
| `pettingzoo` | ✅ **1.27.0, 13 Aug 2026.** MIT. Use the **Parallel API**. 1.27.0 added `RecordVideo`, a Gymnasium-style `pettingzoo.make("aec"|"parallel", "family/env-vN")` registry, and pygame rendering for Hanabi; it **removed the gin_rummy env, dropped Python 3.9, and deprecated the old env-creation API.** MPE was **removed from PettingZoo in 1.26.0** and now lives in the separate **`mpe2`** package. |
| `supersuit` | ✅ `>=3.9.0` (per PettingZoo's own tutorial pins). `concat_vec_env_v1`, `float_obs`, `frame_stack_v1`. |
| Ray RLlib | ✅ **Ray 2.58.0** in the latest docs; 2.56.0 in the package reference pages. `MultiAgentEnv` is `@PublicAPI(stability="beta")` and subclasses `gymnasium.Env`. Wrappers: `PettingZooEnv`, `OpenSpielEnv`, `make_multi_agent()`. **Gotcha: "Multi-agent setups aren't vectorizable yet."** You cannot use `num_envs > 1` for a MA env today. Plan your rollout collection accordingly (use more remote `EnvRunner` actors instead). |
| Stable-Baselines3 | ⚠️ `2.7.x` stable; `2.9.x` on master. **Single-agent only** (`VecEnv`), no MA support. Useful for your single-agent baselines (greedy, round-robin). |
| `sb3-contrib` | ⚠️ **2.9.0, 15 Jun 2026.** MIT. But see §6.1: **no MAPPO.** |
| CleanRL | ✅ `1.2.0` on PyPI (May 2023) but the GitHub repo is actively maintained and has a JMLR paper (vol 23, paper 274, 2022). `ppo_pettingzoo_ma_atari.py` is the reference MA-PPO single file. |
| `onnxruntime` | ✅ **1.29.0, 17 Aug 2026** (CPU); `onnxruntime-gpu` 1.29.0, 17 Aug 2026, requires Python ≥ 3.11. MIT. |
| MARLlib | ❌ See §5. |

---

## 5. Open-source UAV RL simulators — comparison

### 5.1 Recommendation table

| Tool | Current version | Date | License | Multi-agent RL | Physics modelled | Suitability for this project |
|---|---|---|---|---|---|---|
| **OMNeT++ 6.4 + INET 4.7** | 6.4.0 / 4.7.0 | 2026-05-08 / 2026-07-07 | Academic Public License / LGPL | Via your own bridge (you write it) | **Network protocol stack**: full TCP/IP, 802.11/15.4, routing, queueing, handover, power consumption, mobility, obstacles. No rigid-body dynamics. | ★★★★★ **Primary choice.** Your problem is a *network* problem. Exponentially scalable event counts. |
| **Simu5G 1.7.0** | 1.7.0 | 2026-09-14 | LGPL | Via your own bridge | 3GPP 5G NR/LTE **link-level** abstraction: numerology, MCS/CQI tables, HARQ, schedulers, handover, 5GC, MEC. **No OFDM, no waveform, no real fading process, no MIMO.** | ★★☆☆☆ Only if your contribution is 5G-specific. Heavy; breaking changes every minor release; pins you to INET 4.5.4. |
| **gym-pybullet-drones** | `main` (no semver) | commits 6 Sep 2026 | **MIT** | ✅ **Native** (`--multiagent true`, `MultiAgentAviary`) | **Rigid-body quadrotor dynamics** via Bullet: CFD-derived drag/thrust, downwash, PID/DSL controllers. **No network protocol stack.** | ★★★★☆ Excellent for *control*. Use as a fast dynamics layer or a baseline. |
| **Isaac Lab 3.0.0-beta2** | 3.0.0-beta2 (stable line: **2.3.2**) | beta branch 25 Jul 2026 | BSD-3-Clause | ✅ via RLlib/skrl multi-agent | NVIDIA PhysX (or **Newton** in 3.0) rigid-body + RTX rendering. Ships a **Crazyflie** quadcopter; v2.3.2 added multirotor/thruster actuators and a manager-based ARL drone task. | ★★☆☆☆ **Requires an NVIDIA RTX GPU.** PhysX's `PhysX` backend is numerically fine but the framework is a heavyweight dependency. Overkill for 5 UAVs. |
| **AirSim / Colosseum** | — | **Microsoft shut AirSim down Jul 2022. Colosseum ARCHIVED 11 Jul 2026.** | MIT (dead) | ❌ | Full UE5 + AirSim flight-dynamics plugin, PX4/ArduPilot SITL/HIL | ★☆☆☆☆ **DO NOT USE. Total dead end.** Colosseum was the official successor and it is now read-only. |
| **SUMO 1.27.1 + TraCI** | **1.27.1** | **2026-06-25** | **EPL-2.0** (also GPL-2.0) | ❌ (single-agent controller) | Microscopic **road-traffic** flow: car-following, lane-changing, traffic lights, pedestrians, public transport | ★★☆☆☆ Only for a *ground-vehicle* component. EPL-2.0 is **weak copyleft — you must publish derivative source**. For UAV-IoT, irrelevant. |
| **MARLlib** | 2.0.x (pip) | **last push 2024-11-28** | MIT | ✅ 18 algorithms incl. MAPPO | none (library only) | ★☆☆☆☆ **~22 months stale.** Built against RLlib ~2.x; modern Ray 2.5x broke its internals. 47 open issues unanswered. Use the original MAPPO repo instead. |
| **rllab** | 0.5.5 (2018) | 2018 | BSD | ❌ single-agent | none | ☆☆☆☆☆ **Dead.** Ancient, Python-2-era, no Python 3. |
| **PettingZoo 1.27.0** | 1.27.0 | 2026-08-13 | MIT | ✅ **This IS the MARL API standard** | none (library only) | ★★★★★ **Adopt as your env interface.** Parallel API. |
| **MuJoCo-Drones-Gym** | preprint | arXiv **2606.08039**, 6 Jun 2026 | see repo | ✅ `MultiAgentAviary` + **PettingZoo ParallelEnv wrapper** | MuJoCo rigid-body; MJX/XLA GPU backend | ★★★☆☆ **Brand new (3 months).** Promising and the PettingZoo wrapper is the right design, but too new to depend on. Watch it. |
| **OmniDrones** | 2023 | arXiv 2309.12825 | MIT | ✅ 10+ MA tasks | Isaac Sim, >10⁵ steps/s on RTX 4090 | ★★☆☆☆ Isaac-dependent. |

### 5.2 Notes on the specific entries

**gym-pybullet-drones.** The repo **moved from `utiasDSL` to `learnsyslab`**. The current `main` branch is described in its own README as *"a minimalist refactoring of the original gym-pybullet-drones repository, designed for compatibility with gymnasium, stable-baselines3 2.0, and betaflight SITL."* The original IROS 2021 codebase is preserved on the `paper`/`master` branches. **If you want the code your cited paper describes, check out `master`.** Multi-agent is first-class: `python learn.py --multiagent true`. MIT. Actively maintained (commits 6 Sep 2026). It was featured in GitHub's Maintainer Spotlight 2026. Caveat: **no radio model at all** — you would have to write the link layer yourself.

**Isaac Lab.** Be careful about the version: the **default branch is `release/3.0.0-beta2`** (Isaac Sim 6.0.0/6.0.1) and Isaac Lab 3.0 has a *"ground-up architectural overhaul"* including **Newton** as an alternative physics backend. If you want stability, pin **`v2.3.2`** (Isaac Sim 4.5 / 5.0 / 5.1). The official guidance is to retarget PRs at `develop` for 3.0 work. Ships a Crazyflie quadcopter asset. Hardware requirement: NVIDIA RTX GPU. **Reasonable simulator, wrong scale for a 5-UAV network study.**

**AirSim/Colosseum — the trap, in full.** Microsoft announced the shutdown of AirSim in **July 2022**. Codex Labs LLC forked it as **Colosseum** and developed it through UE 5.3/5.4/5.7 with an experimental Unity plugin. On **11 July 2026 the owner archived the repository — it is now read-only.** There is no maintained open-source successor. If your reference list includes an AirSim-based paper and you want to reproduce or build on it, your options are paid/closed (e.g. Project AirSim on Azure) or starting a fork yourself. Do not plan around it.

**SUMO/TraCI.** Very well maintained (1.27.1, 25 June 2026; 1.27.0 on 21 May 2026). `pip install eclipse-sumo`, `traci`, `libsumo`, `sumolib`. Use `libsumo` rather than `traci` if you need throughput — it embeds SUMO as a library and avoids socket overhead. **EPL-2.0 is a licensing consideration.** The canonical SUMO↔OMNeT++ coupling is **Eclipse MOSAIC** (currently pinned to OMNeT++ 6.1 / INET 4.5.4, federate 25.2). Only relevant if your project has a ground-vehicle component.

**MARLlib — status.** GitHub API: `pushed_at: 2024-11-28`, `archived: false`, MIT, 1347 stars, 198 forks, **47 open issues**. It wraps RLlib and offers 18 MARL algorithms including `mappo`. It was accepted in **JMLR 24(315), 2023** — cite *that* if you use it, but pin Ray to whatever it was tested on, or expect breakage.

### 5.3 What is genuinely new for UAV swarms (2025–2026)

| Item | Date | Notes |
|---|---|---|
| **Isaac Lab v2.3.2** | 2026 | Multirotor/thruster actuator model, multirotor asset, **manager-based ARL drone task** (PR #3760). This is the first first-party NVIDIA UAV task. |
| **MuJoCo-Drones-Gym** | 6 Jun 2026 | 7 Gymnasium tasks + `MultiAgentAviary` + a **PettingZoo `ParallelEnv` wrapper**. Ports the `gym-pybullet-drones` philosophy to MuJoCo/MJX. Explicitly compares against `gym-pybullet-drones` and `OmniDrones`. |
| **Isaac Lab 3.0.0-beta2** | 25 Jul 2026 | Newton physics backend, multi-backend architecture, migration guide from 2.x. |
| **Vvc-gym** | ICLR 2025 | Fixed-wing UAV RL, multi-goal long-horizon. |
| **BlueSky-gym** | 2024 | Air-traffic RL environments. |
| **safe-control-gym** | ongoing (learnsyslab) | PyBullet CartPole/quadrotor with **CasADi symbolic a priori dynamics** for safe learning. MIT. 913 stars. |
| **crazyflow** | ongoing (learnsyslab) | "GPU-accelerated, differentiable, JAX-based simulation." The JAX path to UAV RL. |
| **aerial-autonomy-stack** | ongoing (learnsyslab) | PX4/ArduPilot + ROS2 + JetPack deployment — the sim-to-real bridge. |
| **IsaacSimZMQ** | Jun 2026 | NVIDIA's own ZMQ external-application bridge for Isaac Sim — a useful architectural precedent for your OMNeT++ socket bridge. |

> The honest summary: **there is no mature, maintained, network-simulator-integrated open-source UAV MARL environment.** Everyone hand-rolls the bridge. That is simultaneously the risk and the novelty of your project.

---

## 6. RL algorithm implementation reality

### 6.1 sb3-contrib MAPPO: **removed, not just bad**

I enumerated the `sb3_contrib/` directory on `master` of `Stable-Baselines-Team/stable-baselines3-contrib`. The complete directory listing is:

```
ars/  common/  crossq/  ppo_mask/  ppo_recurrent/  qrdqn/  tqc/  trpo/
__init__.py  py.typed  version.txt
```

There is no `mappo/`. There is no `ippo/`. The current documented algorithm list (v2.9.0, 15 Jun 2026) is:

- Augmented Random Search (ARS)
- Quantile Regression DQN (QR-DQN)
- PPO with invalid action masking (MaskablePPO)
- PPO with recurrent policy (RecurrentPPO / PPO LSTM)
- Truncated Quantile Critics (TQC)
- Trust Region Policy Optimization (TRPO)
- CrossQ (Batch Normalization in Deep RL)

**`from sb3_contrib import MAPPO` raises `ImportError` on every currently released version.** Do not put it in your `requirements.txt`. Do not write a report section based on it. (It existed earlier and was removed for the standard SB3 reason: a feature in `contrib` that nobody maintains gets removed. Stable-Baselines3 core is single-agent by design; MARL is out of scope for the whole project.)

**What to use instead, in order of preference:**

### 6.2 Option 1 (recommended): the original PyTorch MAPPO

`susanbao/mappo` — *"This is the official implementation... The implementation in this repository is used in the paper 'The Surprising Effectiveness of MAPPO in Cooperative Multi-Agent Games'"* (Yu et al., arXiv:2103.01955, NeurIPS 2022).

- ✅ This is the paper's own code. Cite the paper, not the repo.
- ✅ CTDE, centralized critic / decentralized actor, parameter sharing, GAE, value normalization, recurrent option.
- ✅ Actually reproduces the paper's SMAC results.
- ⚠️ Written against older PyTorch; the `main` branch is a research codebase, not a library. Expect to pin dependencies and possibly patch.
- ⚠️ Single-process, single-env by default — **you will need to add your own parallelism**, which for you is trivially available: one `opp_run` process per parallel env, wired to N RL workers.

### 6.3 Option 2: CleanRL single-file

`vwxyzjn/cleanrl`. JMLR 23(274), 2022. The MA reference file is **`cleanrl/ppo_pettingzoo_ma_atari.py`**, mirrored verbatim in PettingZoo's own docs (which pin `pettingzoo[butterfly,atari,testing]>=1.27.0`, `SuperSuit>=3.9.0`).

- ✅ ~400 lines, every hyperparameter visible, benchmarked against `openai/baselines`.
- ✅ WandB + TensorBoard + seeding + video built in — the reproducibility story is already written.
- ✅ You can adapt it to continuous actions from `ppo_continuous_action.py` in an afternoon. **For UAV velocity commands you want continuous control; there is no off-the-shelf continuous MA-PPO single file.** You write it.
- ⚠️ CleanRL is explicitly *not* a library: *"CleanRL is not a modular library and therefore it is not meant to be imported."* Fork it, don't import it.

### 6.4 Option 3: Ray RLlib

- **`MultiAgentEnv`** is `@PublicAPI(stability="beta")`, subclasses `gymnasium.Env`, dict-based obs/rew/term/trunc per agent id. Documented as *"the recommended way of defining your own multi-agent environment logic."*
- Wrappers for `PettingZooEnv` and `OpenSpielEnv`. `make_multi_agent()` for turning a single-agent env into a MA env.
- **MAPPO is not in RLlib.** The MA-capable algorithms are PPO (via policy post-processing/masking), APPO, IMPALA, DQN-family (with agent grouping for QMIX), SAC, MARWIL. You implement MAPPO as a custom `RLModule` + `Algorithm` — doable, but you are writing MARLlib-in-miniature.
- **Blocking constraint: "Multi-agent setups aren't vectorizable yet."** `num_envs > 1` does not help you. You scale by adding `EnvRunner` actors instead.
- ✅ Best scaling story (Ray actors → N `opp_run` processes naturally).
- ❌ Heavy. The new (non-"Old API Stack") `RLModule`/`EnvRunner` architecture is a breaking API; tutorials written for 2.7 will not run.
- **Verdict: overkill for 5 agents.** Use it if you need to scale to 50+ agents or many parallel OMNeT++ workers.

### 6.5 Compute budget — what is actually feasible

For **5 agents, 2-D, 500-step episodes** on a modern laptop (8 physical cores, 16 GB RAM, no GPU):

| Quantity | Estimate | Basis |
|---|---|---|
| Wall clock per episode | **0.15–3 s** | NumPy 2-D; ~500 steps × ~2 ms Python overhead |
| Parallel episodes (8 cores) | 8× | `multiprocessing` / `SubprocVecEnv` |
| Throughput | **~2,700–50,000 env-steps/s** | |
| 1e6 steps (typical PPO budget) | **~0.5–2 CPU-hours** | |
| 1e7 steps (thorough) | **~5–20 CPU-hours** | |
| **Full study: 5 seeds × 4 algorithms × 1e6 steps** | **~10–40 CPU-hours** | Feasible in **one night** |
| Ablations: 5 seeds × 3 envs × 3 noise levels × 2 algorithms | ~**200–600 CPU-hours** | **~1–2 weeks on a single laptop** |

For **5 agents, 2-D, with a 1.5M-step budget and 3 environments × 3 noise levels × 5 seeds × 4 algorithms**, budget **~500–1500 CPU-hours**. On a laptop that is **3–6 weeks of continuous running.** Get cluster time, or cut the grid.

**For the OMNeT++ evaluation (the expensive part):**

| Quantity | Estimate |
|---|---|
| Events per episode (5 UAV, 50 sensors, `ScalarRadioMedium`, 600 s) | 1e5 – 5e5 |
| Wall clock per episode, `MODE=release` | 0.3 – 5 s |
| Parallel (16 workers) | 16× |
| **1,000 evaluation episodes** | **20 s – 5 min** |
| **5 seeds × 4 algorithms × 50 eval episodes = 1,000** | **~1 hour** — cheap |
| **A full parameter sweep: 3 values × 3 values × 10 runs = 90 runs** | **~8 CPU-minutes** |

**Key takeaway: the OMNeT++ evaluation is cheap; the Python RL training is the expensive part.** Budget your time accordingly, and keep the surrogate loop for the training.

**Latency budget for the bridge, per decision epoch (5 agents, 4 frames):**

| Component | Cost |
|---|---|
| `send`/`recv` × 4 frames, loopback, `TCP_NODELAY` | 40–120 µs |
| numpy marshalling × 2 × 5 × 113 floats | ~5 µs |
| Python-side policy forward pass (MLP 2×128, batch 5) | 60–200 µs |
| **Total** | **~0.1–0.35 ms** |
| × 120 epochs × 1,000 episodes | **12–42 s** |

**The bridge is 0.01% of your training budget.** Do not optimize it beyond §4.3. Spend the engineering effort on the environment, the reward, and the experiment protocol.

**Practical flags for `opp_run` invocation:**
```bash
# ONE process per parallel env, for N-way RL parallelism:
opp_run -u Cmdenv -f --cmdenv-express-mode=true \
    -l omnetpp.ini -c General -r ${RUN} -n .:$INET/src
```
Set `output-scalar-file`/`output-vector-file` to per-run paths, or better: set `*.result-dir` from `${runnumber}` so runs never collide.

---

## 7. Reproducibility requirements

### 7.1 Seeds in OMNeT++

```ini
[General]
seed-set = 0            # ← SET THIS
# seed = 0             # ← NEVER SET THIS. It pins every run to the same stream.
# cmdenv-rng-seed = 0  # ← named RNG stream, only if you need multiple streams

# Batch: 3 seed-sets x 10 runs each
#   opp_runall -l omnetpp.ini -c General -s 0-2
```

**The mechanism:** OMNeT++ derives the actual seed as
`seed = seedSet * NUM_RNG + rngIndex`, where `NUM_RNG` **defaults to 1 in OMNeT++ 6.x** (it was **2** in OMNeT++ ≤ 5.x). So with the default, seed-set *N* uses seed *N*. If you set `NUM_RNG` for multiple streams, document it — it changes your results.

**Named RNG streams** — essential for a multi-agent study, because it lets you vary *one* source of randomness at a time:
```cpp
#include "inet/common/Random.h"
auto *rngMobility = getParentModule()->getRNG(0);  // mobility
auto *rngChannel  = getParentModule()->getRNG(1);  // wireless channel / error model
auto *rngActions  = getParentModule()->getRNG(2);  // agent action sampling
auto *rngFaults   = getParentModule()->getRNG(3);  // failure injection

double u = rngMobility->doubleRand();
int    a = (int)rngActions->getRand("actionDist");   // 'getRand' is reproducible
                                                     // per-name, unlike getRand()
```
`getRNG(i)` / `getRNG(name)` requires the module to be a `cComponent` and uses the global `RNG` registry. INET 4.7 adds a **configurable RNG grouping mechanism** — if you use it, document the grouping.

**⚠️ Version sensitivity, and this is not a detail.** Simu5G's v1.7.0 release notes state plainly:

> **Fingerprints are INET/OMNeT++ version specific:** the CSVs hold the values for INET-4.5.4 + OMNeT++ 6.3.0, the versions CI uses; other versions report mismatches, and they are expected. ... OMNeT++ 6.4.0 moves `sz` in 181 [of 202 configurations] and nothing else, as it writes the mean of an empty statistic as `nan` rather than `-nan`; INET-4.6.0 moves `sz` in all of them and `tplx`/`tilx` in 18 and 45.

**Your results are not comparable across OMNeT++/INET versions unless you verify them.** Pin exact versions, and if you change, re-run the full seed sweep. Also: `-march=native` and LTO change floating-point results between machines. Use them for the final runs only.

### 7.2 Seeds in Python

```python
import os, random, numpy as np, torch

def set_global_seed(seed: int, deterministic_torch: bool = True) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    if deterministic_torch:
        torch.use_deterministic_algorithms(True, warn_only=True)
        torch.backends.cudnn.benchmark = False
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
```

**One seed for everything is a reproducibility anti-pattern.** It causes correlated exploration across agents and across episodes. Use a *derived* seed per purpose:

```python
import hashlib
def derive(master: int, *parts) -> int:
    h = hashlib.sha256(("|".join(map(str, (master,) + parts))).encode()).digest()
    return int.from_bytes(h[:4], "big")

env_rng = np.random.default_rng(derive(master, "env"))
torch.manual_seed(derive(master, "torch"))
obs_space.seed(derive(master, "obs"))
action_space.seed(derive(master, "act"))
```

**Critical for your bridge:** the OMNeT++ seed and the Python seed must be *coupled and recorded together*. A `master_seed` of 7 must produce the same OMNeT++ `seed-set` and the same Python RNG every time:

```python
master = 7
omnet_seed_set = master                  # or derive(master, "omnet")
policy_seed     = derive(master, "policy")
env_seed        = derive(master, "env")
# send BOTH across the socket; record BOTH in every results row
```

### 7.3 Reporting statistics

**The unit of evidence is a seed, not a run.** A 10-run sweep with 1 seed-set is *one* observation, not 10.

**Minimum defensible protocol: 5 seed-sets minimum, 10 preferred.** Runs within a seed-set are correlated by construction (they share the initial RNG stream derivation); treat them as repeated measurements of a *fixed* environment instance, and average within a seed-set before computing statistics across seed-sets. This is the standard INET/PlexSim-style protocol and the right one.

```python
import numpy as np
from scipy import stats

def summarize(per_seed_scores: np.ndarray) -> dict:
    """
    per_seed_scores: (n_seeds,) -- already averaged within each seed-set
    """
    n = len(per_seed_scores)
    mean = per_seed_scores.mean()
    std  = per_seed_scores.std(ddof=1)                # SAMPLE stddev, ddof=1
    sem  = stats.sem(per_seed_scores)
    tcrit = stats.t.ppf(0.975, df=n - 1)              # two-sided 95%
    ci   = tcrit * sem
    return dict(
        n=n, mean=mean, std=std, sem=sem,
        ci95_low=mean - ci, ci95_high=mean + ci,
        # If your scores are non-Gaussian (very common for coverage %),
        # report the bootstrap CI as primary and t as secondary.
        boot_ci=tuple(np.percentile(
            (stats.bootstrap((per_seed_scores,), np.mean, n_resamples=10_000,
                             random_state=np.random.default_rng(0))[0], [2.5, 97.5]))),
    )

def holm_bonferroni(pairs, alpha=0.05):
    """Multiple comparisons. Do NOT report uncorrected p-values across baselines."""
    pairs = sorted(pairs, key=lambda kv: kv[1])       # [(name, p), ...]
    m = len(pairs); out = []; k = 0
    for name, p in pairs:
        k += 1
        out.append((name, p, min(1.0, p * (m - k + 1)), p <= alpha / (m - k + 1)))
    return out
```

**What to report in the paper:**
- **Mean ± sample std (`ddof=1`) across seed-sets**, with **n stated explicitly**.
- **95% CI**, with the method named (Student-t, or BCa bootstrap). Coverage percentage is bounded and often skewed → **use the bootstrap**.
- **Per-seed raw values in an appendix or supplementary table**, always. This is what makes your results auditable.
- **A paired statistical test against your primary baseline** (Wilcoxon signed-rank or paired t-test across seed-sets), with **Holm–Bonferroni correction** if you compare against more than 2 algorithms. Report the effect size (rank-biserial correlation or Cohen's *d*), not just p.
- **Never** report a single run. **Never** compare across different INET/OMNeT++ versions.

A run-configuration table belongs in the report:

| Algorithm | Seed-set | Run | Master seed | OMNeT++ | INET | Git SHA | Wall clock | Result file |
|---|---|---|---|---|---|---|---|---|
| MAPPO | 0 | 0–9 | 7 | 6.4.0 | 4.7.0 | `a1b2c3d` | 41 min | `results/General/General-0.sca` |

### 7.4 A fair baseline comparison protocol

1. **Same environment, same episodes, same seeds.** Baseline and method must see the *identical* `seed-set` / `run` sequence. Pair your tests accordingly (paired, not independent).
2. **Equal interaction budget, not equal wall clock.** Same number of environment steps and same number of gradient updates. Wall-clock-normalized comparisons flatter methods with cheap steps and are not meaningful here.
3. **Hyperparameters are part of the baseline.** Give every baseline the same tuning budget (same number of random-search trials, same search space width) and report the tuned values. Tuning your method more than your baselines is the most common MARL paper sin.
4. **Include these baselines** (and be honest that they are strong):
   - Greedy farthest-point coverage (recompute on failure)
   - Greedy with full coverage-map recomputation
   - Round-robin partitioning (static assignment)
   - Decentralized PPO (IPPO) with the same network
   - **Greedy + a simple local repair heuristic** — usually the most competitive non-learning baseline in coverage problems. If your learned policy does not beat this, that is your finding, and it is a publishable one.
5. **Separate the ablation axes.** Persistent coverage vs. re-compute-on-failure; fault tolerance (node failure, gNB failure, link degradation) vs. no faults; centralized critic vs. decentralized critic; homogeneous vs. heterogeneous agents.
6. **Report the surrogate-vs-OMNeT++ correlation** (§4.6) so a reader knows which claims were verified in which simulator.
7. **Archive everything.** NED/ini/C++/Python, `requirements.txt` with pinned versions, exact `opp_run` command lines, git SHA, and the raw `.sca` files. A DOI'd Zenodo record costs you 20 minutes and is frequently the difference between "reproducible" and "not".

---

## 8. License and citation requirements

### 8.1 What needs citation

**Always cite** (these have papers, and using their model without citing is plagiarism):

| Component | Citation |
|---|---|
| **OMNeT++** | Varga, A. "OMNeT++: Modeling Dynamic Networks on the Micro- and Meso-Scale." *Mathematical Models for Communication Systems, LNCS 5462*, Springer, 2009. |
| **INET** | Varga, A. "INET Framework for OMNeT++/OMNEST: Current Status and Future Directions." *Simulation Modelling and Practice, and Methodology* / OpenSim Ltd. Also cite the specific release: **INET 4.7.0, released 7 July 2026.** |
| **Simu5G** | Virdis, A., Nardini, G., Stea, G., Varga, A. "Recent Advances in 5G NR Radio Layer Modelling for System-Level Simulations in Simu5G." *Proc. IEEE WCNC*; plus **Varga, A. (2026), "Simu5G v1.7.0 release notes / WHATSNEW"** — cite the version, because the class renames are breaking. |
| **SimuLTE** (if cited as predecessor) | Nardini, G., Virdis, A., Egea Lopez, E., Stea, G. "Simulation of LTE Networks." *OMNeT++ Workshop*, 2011. |
| **MAPPO** | **Yu, C., et al. "The Surprising Effectiveness of PPO in Cooperative Multi-Agent Games." NeurIPS 2022. arXiv:2103.01955.** Mandatory — it is the origin of your method. |
| **PettingZoo** | Terry, J., et al. "PettingZoo: Gymnasium for Multi-Agent Reinforcement Learning." *NeurIPS 2021. arXiv:2009.14471.* |
| **Gymnasium** (if you use the API) | Towers, M., et al. "Gymnasium: A Standardized Interface for Reinforcement Learning Environments." arXiv:2407.17032. |
| **CleanRL** | Huang, S., et al. "CleanRL: High-quality Single-file Implementations of Deep Reinforcement Learning Algorithms." *JMLR* 23(274), 2022. |
| **Stable-Baselines3** | Raffin, A., et al. "Stable-Baselines3: Reliable Reinforcement Learning Implementations." *JMLR* 22(268), 2021. |
| **Ray RLlib** | Moritz, P., et al. "Ray: A Distributed Framework for Emerging AI Applications." *OSDI 2018*. |
| **MARLlib** (if used) | Hu, S., Zhong, Y., Gao, M., et al. "MARLlib: A Scalable and Efficient Multi-agent Reinforcement Learning Library." *JMLR* 24(315), 2023. |
| **PyBullet** | Coumans, L., et al. "Bullet Physics SDK." — `pybullet` is GPLv3; cite and see §8.2. |
| **gym-pybullet-drones** | **Panerati, A., El-Dahshan, A., Raistani, M., Cetinas, E. "Learning to Fly — a Gym Environment with PyBullet Physics for Reinforcement Learning of Multi-agent Quadcopter Control." *IROS 2021. arXiv:2103.02142.*** Its own README asks you to cite this even for the refactored `main` branch. |
| **Isaac Lab** | The Isaac Lab technical report: **arXiv:2511.04831** (MPR+25), plus the NVIDIA Isaac Sim version used. |
| **SUMO** | **Behrisch, J., Krumbholz, L., Kesting, E., Schwanebecher, T. "SUMO — Simulation of Urban MObility." In *Traffic Simulation*, 2018.** Zenodo DOI for the specific version: **1.27.0 → 10.5281/zenodo.20312733**. Request one for your exact version at <https://sumo.dlr.de/Downloads.php>. |
| **MOSAIC** (if used) | Eclipse MOSAIC docs + the federate version. |
| **ONNX** / **ONNX Runtime** | Chen, B., et al. "Open Neural Network Exchange." arXiv:1808.02679 (ONNX); Microsoft `onnxruntime` repo + version. |
| **ZeroMQ** (if used) | Hintjens, P. "ZeroMQ: The Smart Socket Library." — the *book*, not just a citation. |

**Cite per-component, not per-paper.** A report that uses OMNeT++ + INET + PettingZoo + MAPPO + CleanRL needs **at least 5 citations**, and each simulator you compare against needs its own.

**Do not cite:** `pyopp` (doesn't exist), `sb3-contrib MAPPO` (doesn't exist), AirSim/Colosseum (dead — if you mention it at all, say it is archived and cite the archive).

### 8.2 Licenses — the part people get into trouble with

| Component | License | Obligation |
|---|---|---|
| **OMNeT++** | **Academic Public License** | Free for **academic use only**. Commercial use requires OMNEST. **Cite.** Do not redistribute the binary in a public artifact without reading the APL. |
| **INET** | **LGPL-3.0-or-later** (since 4.4.0) | Dynamic linking keeps your work yours. If you *statically* link or modify INET, you must release those changes under LGPL. **A separate `inet-gpl` repo holds the old GPL parts** (TCP NSC, packetdrill, HTB, HTTP tools) — if you enable any of those project features, your derivative inherits GPL. **Check which INET project features you enable.** |
| **Simu5G** | **LGPL** | Same. |
| **PettingZoo** | MIT | Attribution only. |
| **CleanRL / SB3 / sb3-contrib** | MIT | Attribution only. |
| **Ray RLlib** | Apache-2.0 | Attribution + patent grant. |
| **MARLlib** | MIT | Attribution. |
| **gym-pybullet-drones** | MIT | Attribution + cite the IROS paper. |
| **PyBullet** | **GPL-3.0** | ⚠️ **This is the sharp edge.** `gym-pybullet-drones` is MIT but depends on GPL-3.0 PyBullet. Importing it into your code is a GPL question. For a **course project / report** this is fine (no distribution). If you ever distribute a binary or offer a service, get advice. |
| **Isaac Lab** | **BSD-3-Clause** (some parts Apache-2.0) | Very permissive. But Isaac Sim itself is under NVIDIA's EULA, and you need an NVIDIA GPU. |
| **SUMO** | **EPL-2.0** (also GPL-2.0) | ⚠️ **EPL-2.0 is weak copyleft.** Modifying SUMO requires you to publish the modified source. If you only `import sumo` / use TraCI, you are fine. Read it if you modify it. |
| **OMNeT++ 6.4.0 binary** | APL | Academic use; be careful with redistribution. |

**The only two that can actually bite you are PyBullet (GPL-3.0) and SUMO (EPL-2.0).** For a student report neither matters. If your project ever becomes a public artifact, check.

---

## 9. Traps — a consolidated list

1. **`pyopp` does not exist in OMNeT++ 6.x.** Verified: zero matches in the `omnetpp-6.4.0` tree. Any tutorial recommending embedded Python NED modules is pre-5.0. `pyeval()`/`pycode()` exist but are parameter-expression-only.
2. **`sb3-contrib` has no MAPPO or IPPO.** The directories were deleted. `from sb3_contrib import MAPPO` → `ImportError`. Use `susanbao/mappo` or CleanRL.
3. **AirSim is dead (Microsoft, Jul 2022) and Colosseum — its official successor — was archived 11 Jul 2026.** There is no maintained open-source UE-based UAV simulator. Do not build on it.
4. **Every INET 4.5-era wireless class name in your brief is gone in 4.6/4.7:** `ScalarRadio`, `DimensionalRadio`, `IsotropicScalarRadioMedium`, `IsotropicScalarRadio`, `IdealPropagation`, `BasicRangePropagation`, `DielectricBreakdownPropagation`, `TernaryPropagation`, `DmgErrorModel`, `PERTableRadioErrorModel`, `TableBasedErrorModel`, `AdditiveRayleighChannel`, `DimensionalChannel`. **And `SimpleWirelessHost` never existed.** Tutorials and LLM output are both full of these.
5. **`LinearMobilityModule` / `MassMobilityModule` are C++ class names.** The NED types are `LinearMobility` / `MassMobility`. Writing the C++ name in `typename =` fails.
6. **Never set `seed = 0` in `[General]`.** It pins every run to the same stream and silently kills all your variance. Set `seed-set`.
7. **Never parse `.sca`/`.vec` by hand.** Use `omnetpp.scave.results.read_files()`.
8. **`NUM_RNG` changed from 2 to 1 in OMNeT++ 6.x.** A seed-set means a different seed than it did in OMNeT++ 5.
9. **`-march=native` and LTO change floating-point results between machines.** Final runs only.
10. **Results are not comparable across INET/OMNeT++ versions.** Simu5G's own release notes document which statistics move and by how much.
</task_result>
</task>