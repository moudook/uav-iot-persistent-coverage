P = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\Mlawn-midsem-tex.tex"
s = open(P, encoding="utf-8").read()

# E2: restore audit/PHY-validation subsection
if "\\subsection{Claim audit and physical-layer validation}" not in s:
    anchor = "\\subsection{History of this measurement}"
    assert anchor in s, "history anchor missing"
    audit = r"""\subsection{Claim audit and physical-layer validation}
\label{sec:validation}

Every non-measurement claim of this paper --- the physical model, the
feasibility bounds, the protocol statements and the determinism claims --- is
recomputed by an automated claim audit that records, for each statement, the
artefact or derivation that supports it: \tokAuditItems{} items, of which
\tokAuditPass{} pass, \tokAuditInfo{} are informational, and \tokAuditFail{}
fail.  The audit does not cover the measurements of this paper; those are the
artefacts themselves.

The physical-layer claim is the one that is audited most carefully, because
its cheap version would be a runtime cross-validation and its honest version
is an algebraic equivalence.  The Python reference PHY and INET's
\texttt{BreakpointPathLoss} implement the same function to $\tokPhyDelta$~dB
over $\tokPhyRows$ (distance, exponent) points, and that equivalence is what
is claimed.  A runtime path-loss cross-validation was attempted with a
transmit-power negative control: the available per-receiver SNR statistic
tracks the transmit power exactly but is independent of the receiver's
distance, so it cannot support such a cross-validation, and the negative
control is what exposed it.  A dedicated 802.11 physical-layer scenario runs
to completion in the OMNeT++/INET co-simulation and produces scalar and vector
outputs; the instrument it provides, and the reason it cannot measure what we
would like it to measure, are recorded with the scenario.

"""
    s = s.replace(anchor, audit + anchor, 1)
    print("E2 applied")
else:
    print("E2 already present")

# E3: energy ref
old3 = "the cost of charging contention in the energy results of Section~\\ref{sec:results_energy} is a lower bound"
if old3 in s:
    s = s.replace(old3,
                  "the cost of charging contention in the small-battery stress regime (Table~\\ref{tab:stress}) is a lower bound",
                  1)
    print("E3 applied")
else:
    print("E3 already applied")

open(P, "w", encoding="utf-8").write(s)
print("done")
