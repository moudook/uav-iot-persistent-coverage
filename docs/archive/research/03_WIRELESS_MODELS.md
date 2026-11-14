# Wireless Channel Models for Simulating a UAV–IoT Network

### A mathematically complete reference for OMNeT++ 6.x + INET 4.5 + Simu5G with a Python/RL bridge

**Scope:** propagation and link-layer channel modelling for a persistent-coverage UAV swarm serving
ground IoT sensors. Every formula is given in LaTeX, with the exact primary source and the actual
numeric constants (not placeholders).

**Compiled:** 29 September 2026.

---

## Primary sources (exact identifiers)

| Key | Document | Version used here |
|---|---|---|
| **[38.901]** | 3GPP TR 38.901, *Study on channel model for frequencies from 0.5 to 100 GHz* | ETSI TR 138 901 **V16.1.0** (2020-11) and **V19.1.0** (2025-10) |
| **[38.214]** | 3GPP TS 38.214, *NR; Physical layer; Physical layer procedures for control* | as encoded in Simu5G `src/simu5g/stack/mac/amc/NrMcs.cc` |
| **[38.211]** | 3GPP TS 38.211, *NR; Physical channels and modulation* | numerology |
| **[38.104]** | 3GPP TS 38.104, *NR; Base station (BS) radio transmission and reception* | numerology validity |
| **[36.814]** | 3GPP TR 36.814, *Further advancements for E-UTRA physical layer aspect* | cited by Simu5G |
| **[36.873]** | 3GPP TR 36.873, *Study on spatial channel model for frequencies from 2 to 6 GHz* | cited by Simu5G |
| **[36.842]** | 3GPP TR 36.842, *Study on performance of 3GPP LTE radio interface* | BLER curves |
| **[38.811]** | 3GPP TR 38.811, *Study on NR to support non-terrestrial networks (NTN)* | Rel-15/16 |
| **[38.821]** | 3GPP TR 38.821, *Solutions for NR to support Non-Terrestrial Networks (NTN)* | Rel-16 |
| **[P.1816]** | ITU-R Recommendation P.1816 | shadow-fading correlation, cited *by* [38.901] §7.4.4 |
| **[Y.1540]** | ITU-T Recommendation Y.1540 (Dec. 2007 / 2011), *IP packet transfer and availability performance parameters* | metric definitions |
| **[Y.1541]** | ITU-T Recommendation Y.1541 (12/2011), *Network performance objectives for IP-based services* | QoS classes |
| **[RFC7679]** | IETF RFC 7679, *A One-Way Delay Metric for IP Performance Metrics (IPPM)* | aligned with [Y.1540] |
| **[RFC2680]** | IETF RFC 2680, *An IP Packet Delay Variation Metric for IPPM* | aligned with [Y.1540] |
| **[Rappaport]** | T. S. Rappaport, *Wireless Communications: Principles and Practice*, 2e, Prentice Hall, 2002 | Jakes/Clarke, two-ray, Okumura–Hata |
| **[Clarke]** | R. H. Clarke, "A statistical theory of coverage in a randomly dispersed radio system," IRE Trans. Commun., vol. 6, no. 2, pp. 389–397, 1958 | Clarke's model |
| **[Jakes]** | W. C. Jakes (ed.), *IEEE 802.11 Standard*, 1997 | sum-of-sinusoids |
| **[AlH14]** | A. Al-Hourani, S. Kandeepan, S. Lardner, "Optimal LAP altitude for maximum coverage," *IEEE Wireless Commun. Lett.*, vol. 3, no. 6, pp. 569–572, Dec. 2014 | aerial BS path loss |
| **[AlH20]** | A. Al-Hourani, "On the probability of line-of-sight in urban environments," *IEEE Wireless Commun. Lett.*, vol. 9, no. 8, pp. 1178–1181, Aug. 2020 | A2G LoS probability |
| **[INET45]** | INET Framework v4.5.0 (`inet-framework/inet`, tag `v4.5.0`) | exact module names, NED parameters and C++ math |
| **[Simu5G]** | Simu5G (`inet-framework/Simu5G`, tag `v1.7.0`) | exact channel-model parameters |

### Units and conventions used throughout

* $d$ in metres, $f_c$ in **GHz** wherever a 3GPP table says so, $h$ in metres.
* In [38.901] "Note 6": *$f_c$ denotes the center frequency normalized by 1 GHz, all distance
  related values are normalized by 1 m, unless it is stated otherwise.* Thus $\log_{10}(f_c)$
  in the tables means $\log_{10}(f_c/(1\text{ GHz}))$ and $\log_{10}(d)$ means $\log_{10}(d/(1\text{ m}))$.
* Power: dBm for absolute power, dB for ratios. $N_0$ is one-sided, per Hz.
* Sign convention of shadowing ([38.901] Table 7.5-6 NOTE 2): **positive SF means more received
  power than predicted by the path-loss model**, i.e. SF is subtracted from PL.

---

## 1. 3GPP TR 38.901 path-loss models

### 1.1 Geometry and distance definitions

[38.901] Figures 7.4.1-1 / 7.4.1-2 and equation (7.4-1):

$$
d_{3D} \;=\; \sqrt{d_{2D}^{2} + \left(h_{BS}-h_{UT}\right)^{2}}
\tag{1.1a}
$$

For indoor UTs the outdoor and indoor segments are added:

$$
d_{3D-out} + d_{3D-in} \;=\; \sqrt{\left(d_{2D-out}+d_{2D-in}\right)^{2} + \left(h_{BS}-h_{UT}\right)^{2}}
\tag{1.1b}
$$

* $h_{BS}$ — antenna height of the base station above ground, metres.
* $h_{UT}$ — antenna height of the user terminal above ground, metres.
* $d_{2D}$ — the **horizontal** (ground-plane) distance between Tx and Rx antennas, metres.
  **All breakpoint comparisons in [38.901] are made against $d_{2D}$, not $d_{3D}$.**
* $d_{3D}$ — the true slant range.
* $d_{2D-out}$ / $d_{2D-in}$ — horizontal distance outside / inside the building.

### 1.2 The breakpoint distance $d'_{\rm BP}$ — exact definition

There is exactly **one** breakpoint in [38.901]. It is defined two ways, depending on the scenario.

**For UMa and UMi-Street Canyon — [38.901] Table 7.4.1-1, Note 1:**

$$
d'_{\rm BP} \;=\; \frac{4\,h'_{BS}\,h'_{UT}\,f_c}{c},
\qquad
h'_{BS} = h_{BS}-h_E, \qquad h'_{UT} = h_{UT}-h_E
\tag{1.2a}
$$

with $f_c$ in **Hz** and $c = 3.0\times 10^{8}\ \mathrm{m/s}$, giving $d'_{\rm BP}$ in metres.

$h_E$ is the *effective environment height*:

$$
h_E =
\begin{cases}
1.0\ \mathrm{m}, & \text{UMi} \\[4pt]
1\ \mathrm{m}, \ \text{with probability } \dfrac{1}{1+C(d_{2D},h_{UT})}, \\[10pt]
\qquad \text{otherwise } h_E \sim \text{DiscreteUniform}\{12,15,\ldots,(h_{UT}-1.5)\}, & \text{UMa}
\end{cases}
\tag{1.2b}
$$

$$
C(d_{2D},h_{UT})=
\begin{cases}
0, & h_{UT} < 13\ \mathrm{m}\\[4pt]
\left(\dfrac{h_{UT}-13}{10}\right)^{1.5} g(d_{2D}), & 13\ \mathrm{m} \le h_{UT} \le 23\ \mathrm{m}
\end{cases}
\qquad
g(d_{2D})=
\begin{cases}
0, & d_{2D} \le 18\ \mathrm{m}\\[4pt]
\dfrac{5}{4}\left(\dfrac{d_{2D}}{100}\right)^{3}\exp\!\left(-\dfrac{d_{2D}}{150}\right), & d_{2D} > 18\ \mathrm{m}
\end{cases}
\tag{1.2c}
$$

[38.901] Note 1 explicitly warns that $h_E$ depends on **both** $d_{2D}$ and $h_{UT}$ and must be
re-drawn **per link**.

**For RMa (and, from Rel-19, SMa) — [38.901] Note 5:**

$$
d_{\rm BP} \;=\; \frac{2\pi\,h_{BS}\,h_{UT}\,f_c}{c}
\tag{1.2d}
$$

with the **raw** antenna heights (no $h_E$).

### 1.3 UMa — Urban Macro (the model you will use most)

**Validity ([38.901] Table 7.4.1-1, both Rel-16 and Rel-19 agree):**

* $1.5\ \mathrm{m} \le h_{UT} \le 22.5\ \mathrm{m}$, $h_{BS} = 25\ \mathrm{m}$ (nominal).
* $10\ \mathrm{m} \le d_{2D} \le 5\ \mathrm{km}$ (NLOS branch validity).
* Frequency: $0.5 < f_c < 100$ GHz ([38.901] Note 2, $f_H = 100$ GHz for UMa).

**LOS:**

$$
PL_{\rm UMa-LOS} =
\begin{cases}
PL_1, & 10\ \mathrm{m} \le d_{2D} \le d'_{\rm BP} \\[4pt]
PL_2, & d'_{\rm BP} \le d_{2D} \le 5\ \mathrm{km}
\end{cases}
\tag{1.3a}
$$

$$
PL_1 = 28.0 + 22\log_{10}(d_{3D}) + 20\log_{10}(f_c)
\tag{1.3b}
$$

$$
PL_2 = 28.0 + 40\log_{10}(d_{3D}) + 20\log_{10}(f_c) - 9\log_{10}\!\left(\left(d'_{\rm BP}\right)^{2} + \left(h_{BS}-h_{UT}\right)^{2}\right)
\tag{1.3c}
$$

The effective path-loss exponents are $n = 22/10 = 2.2$ below the breakpoint and $n = 40/10 = 4.0$
above it. Physically, $d'_{\rm BP}$ is where the direct ray and the first bounce ray equalise;
the final $\log_{10}$ term is the correction that makes $PL$ continuous in $d$ across $d'_{\rm BP}$.

**NLOS:**

$$
PL_{\rm UMa-NLOS} = \max\!\left(PL_{\rm UMa-LOS},\; PL'_{\rm UMa-NLOS}\right),
\qquad 10\ \mathrm{m} \le d_{2D} \le 5\ \mathrm{km}
\tag{1.3d}
$$

$$
PL'_{\rm UMa-NLOS} = 13.54 + 39.08\log_{10}(d_{3D}) + 20\log_{10}(f_c) - 0.6\,(h_{UT}-1.5)
\tag{1.3e}
$$

so $PL'_{\rm UMa-NLOS}$ has PLE $n = 3.908$ and frequency exponent $\gamma = 2$.

**Optional (alternative) UMa NLOS:**

$$
PL_{\rm UMa-NLOS}^{\rm(opt)} = 32.4 + 20\log_{10}(f_c) + 30\log_{10}(d_{3D})
\tag{1.3f}
$$
with $\sigma_{SF} = 7.8$ dB (alpha-beta-gamma-style form: PLE 3.0, $\gamma = 2$).

**Shadow fading standard deviation $\sigma_{SF}$ (dB), [38.901] Table 7.4.1-1:**

| Scenario | LOS | NLOS |
|---|---|---|
| UMa | 4 | 6 |
| UMa (optional form) | — | 7.8 |
| UMi-Street Canyon | 4 | 7.82 |
| UMi (optional form) | — | 8.2 |
| RMa (see §1.5) | 4 / 6 | 8 |
| InH-Office | 3 | 8.03 |
| InF | 4.3 (Rel-19) / 4 (Rel-16) | 5.7 / 7.2 / 5.9 / 4.0 |


### 1.4 UMi — Urban Micro (Street Canyon)

**Validity:** $1.5\ \mathrm{m} \le h_{UT} \le 22.5\ \mathrm{m}$, $h_{BS} = 10\ \mathrm{m}$,
$10\ \mathrm{m} \le d_{2D} \le 5\ \mathrm{km}$, $0.5 < f_c < 100$ GHz.

**LOS** (breakpoint $d'_{\rm BP}$, Note 1, with $h_E = 1.0$ m fixed for UMi):

$$
PL_1 = 32.4 + 21\log_{10}(d_{3D}) + 20\log_{10}(f_c)
\tag{1.4a}
$$

$$
PL_2 = 32.4 + 40\log_{10}(d_{3D}) + 20\log_{10}(f_c) - 9.5\log_{10}\!\left(\left(d'_{\rm BP}\right)^{2} + \left(h_{BS}-h_{UT}\right)^{2}\right)
\tag{1.4b}
$$

**NLOS:**

$$
PL'_{\rm UMi-NLOS} = 35.3\log_{10}(d_{3D}) + 22.4 + 21.3\log_{10}(f_c) - 0.3\,(h_{UT}-1.5)
\tag{1.4c}
$$

$$
PL_{\rm UMi-NLOS} = \max\!\left(PL_{\rm UMi-LOS},\; PL'_{\rm UMi-NLOS}\right)
\tag{1.4d}
$$

Optional: $PL^{\rm(opt)} = 32.4 + 20\log_{10}(f_c) + 31.9\log_{10}(d_{3D})$, $\sigma_{SF}=8.2$ dB.

Note the sign and factor of the height term: UMi LOS has **no** $h_{UT}$ term at all, and the
UMi NLOS height term is $-0.3(h_{UT}-1.5)$ whereas UMa NLOS has $-0.6(h_{UT}-1.5)$.

### 1.5 RMa — Rural Macro

**Validity ([38.901] Table 7.4.1-1):** $h_{BS}=35$ m, $h_{UT}=1.5$ m, $W=20$ m, $h=5$ m
(average building height / street width). Ranges: $5\le h\le 50$ m, $5\le W\le 50$ m,
$10\le h_{BS}\le 150$ m, $1\le h_{UT}\le 10$ m. Frequency $0.5<f_c<f_H$ with
**$f_H = 30$ GHz for RMa** ([38.901] Note 2); the >7 GHz part is validated on a single
24 GHz campaign.

**LOS** (breakpoint per Note 5):

$$
PL_{\rm RMa-LOS} =
\begin{cases}
PL_1, & 10\ \mathrm{m} \le d_{2D} \le d_{\rm BP}\\
PL_2, & d_{\rm BP} \le d_{2D} \le 10\ \mathrm{km}
\end{cases}
\tag{1.5a}
$$

$$
PL_1 = 20\log_{10}\!\left(\frac{40\pi\,d_{3D}\,f_c}{3}\right) + \min\!\left(0.03\,h^{1.72},\,10\right)\log_{10}(d_{3D}) - \min\!\left(0.044\,h^{1.72},\,14.77\right) + 0.002\log_{10}(h)\,d_{3D}
\tag{1.5b}
$$

$$
PL_2 = PL_1(d_{\rm BP}) + 40\log_{10}\!\left(\frac{d_{3D}}{d_{\rm BP}}\right)
\tag{1.5c}
$$

**RMa LOS shadowing is distance-dependent** (Rel-16 and Rel-19 both):

$$
\sigma_{SF} =
\begin{cases}
4\ \mathrm{dB}, & 10\ \mathrm{m} \le d_{2D} < d_{\rm BP}\\
6\ \mathrm{dB}, & d_{\rm BP} \le d_{2D} \le 10\ \mathrm{km}
\end{cases}
\tag{1.5d}
$$

**NLOS** ($10\ \mathrm{m}\le d_{2D}\le 5$ km, $\sigma_{SF}=8$ dB):

$$
PL_{\rm RMa-NLOS} = \max\!\left(PL_{\rm RMa-LOS},\; PL'_{\rm RMa-NLOS}\right)
\tag{1.5e}
$$

$$
PL'_{\rm RMa-NLOS} = 161.04 - 7.1\log_{10}(W) + 7.5\log_{10}(h)
 - \left(24.37 - 3.7\left(\frac{h}{h_{BS}}\right)^{2}\right)\log_{10}(h_{BS})
 + \left(43.42 - 3.1\log_{10}(h_{BS})\right)\left(\log_{10}(d_{3D}) - 3\right)
 + 20\log_{10}(f_c) - \left(3.2\left(\log_{10}(11.75\,h_{UT})\right)^{2} - 4.97\right)
\tag{1.5f}
$$

### 1.6 InH — Indoor Office, and InF — Indoor Factory

**InH-Office** ($1\ \mathrm{m} \le d_{3D} \le 150\ \mathrm{m}$, **no** breakpoint, **no** height terms):

$$
PL_{\rm InH-LOS} = 32.4 + 17.3\log_{10}(d_{3D}) + 20\log_{10}(f_c), \quad \sigma_{SF}=3\ \mathrm{dB}
\tag{1.6a}
$$

$$
PL_{\rm InH-NLOS} = \max\!\left(PL_{\rm InH-LOS},\; PL'_{\rm InH-NLOS}\right)
\tag{1.6b}
$$

$$
PL'_{\rm InH-NLOS} = 38.3\log_{10}(d_{3D}) + 17.30 + 24.9\log_{10}(f_c), \quad \sigma_{SF}=8.03\ \mathrm{dB}
\tag{1.6c}
$$

Optional InH NLOS: $PL' = 32.4 + 20\log_{10}(f_c) + 31.9\log_{10}(d_{3D})$, $\sigma_{SF}=8.29$ dB.

**InF** ($1 \le d_{3D} \le 600$ m). $S=$ sparse, $D=$ dense, $L=$ low, $H=$ high (factory clutter):

$$
PL_{\rm InF-LOS} = 31.84 + 21.50\log_{10}(d_{3D}) + 19.00\log_{10}(f_c), \quad \sigma_{SF} = 4.3\ \mathrm{dB}\ (\text{Rel-19}) / 4\ \mathrm{dB}\ (\text{Rel-16})
\tag{1.6d}
$$

$$
\begin{aligned}
\text{InF-SL:}\quad PL &= 33 + 25.5\log_{10}(d_{3D}) + 20\log_{10}(f_c), & \sigma_{SF}&=5.7\\[3pt]
\text{InF-DL:}\quad PL &= 18.6 + 35.7\log_{10}(d_{3D}) + 20\log_{10}(f_c), & \sigma_{SF}&=7.2\\[3pt]
\text{InF-SH:}\quad PL &= 32.4 + 23.0\log_{10}(d_{3D}) + 20\log_{10}(f_c), & \sigma_{SF}&=5.9\\[3pt]
\text{InF-DH:}\quad PL &= 33.63 + 21.9\log_{10}(d_{3D}) + 20\log_{10}(f_c), & \sigma_{SF}&=4.0
\end{aligned}
\tag{1.6e}
$$

with the mandated maxima:

$$
PL_{\rm NLOS} = \max\!\left(PL,\; PL_{\rm LOS}\right) \quad (\text{SL, SH, DH}),
\qquad
PL_{\rm NLOS} = \max\!\left(PL,\; PL_{\rm LOS},\; PL_{\rm InF-SL}\right) \quad (\text{DL})
\tag{1.6f}
$$

**InH/InF are essentially irrelevant for an outdoor UAV-IoT deployment** unless your sensors are
inside buildings, in which case add §1.7 (penetration loss) on top of an outdoor model.

### 1.7 SMa — Suburban Macro (Rel-19 only)

Added in Rel-19. Validity: $10\ \mathrm{m}\le d_{2D}<d_{\rm BP}$ and $d_{\rm BP}\le d_{2D}<5000$ m;
$25 < h_{BS} < 35$ m, $h = 10$ m, $W = 10$ m; $f_H = 37$ GHz. $\sigma_{SF} = 4/6$ dB (LOS,
below/above breakpoint) and $8$ dB (NLOS). The LOS/NLOS formulas are numerically identical to
RMa (1.5b)/(1.5c)/(1.5f) with $h=10$ m, $W=10$ m and $1\le h_{UT}\le 14$ m for NLOS.

### 1.8 O2I building penetration loss ([38.901] §7.4.3.1)

$$
PL = PL_b + PL_{tw} + PL_{in} + \mathcal{N}(0,\sigma_P^{2})
\tag{1.8a}
$$

where $PL_b$ is the outdoor path loss of §1.3–§1.6 with $d_{3D}$ replaced by
$d_{3D-out}+d_{3D-in}$.

$$
PL_{tw} = PL_{npi} - 10\log_{10}\!\left(\sum_{i=1}^{N} p_i \times 10^{\frac{-L_{material_i}}{10}}\right)
\tag{1.8b}
$$

with $L_{material_i} = a_{material_i} + b_{material_i}\cdot f$ ([38.901] Table 7.4.3-1):

| Material | Penetration loss $L$ [dB], $f$ in GHz |
|---|---|
| Standard multi-pane glass | $L_{glass} = 2 + 0.2f$ |
| IRR glass | $L_{IIRglass} = 23 + 0.3f$ |
| Concrete | $L_{concrete} = 5 + 4f$ |
| Wood | $L_{wood} = 4.85 + 0.12f$ |

The two official O2I models ([38.901] Table 7.4.3-2):

$$
PL_{tw} =
\begin{cases}
5 - 10\log_{10}\!\left(0.3\cdot 10^{-L_{glass}/10} + 0.7\cdot 10^{-L_{concrete}/10}\right) & \text{low-loss}\\[4pt]
5 - 10\log_{10}\!\left(0.7\cdot 10^{-L_{IIRglass}/10} + 0.3\cdot 10^{-L_{concrete}/10}\right) & \text{high-loss}
\end{cases}
\qquad
PL_{in} = 0.5\, d_{2D-in}
\tag{1.8c}
$$

with $\sigma_P = 4.4$ dB (low-loss) and $6.5$ dB (high-loss). $d_{2D-in}$ is the minimum of two
independent $\mathcal{U}[0,25]$ m draws (UMa, UMi) or $\mathcal{U}[0,10]$ m draws (RMa), and must be
generated **per UT**. Only the low-loss model applies to RMa; only the high-loss model to InF.
For backwards compatibility below 6 GHz, [38.901] Table 7.4.3-3 mandates a **flat 20 dB**
penetration loss with $\sigma_P = 0$ for UMa/UMi.

**O2I car penetration loss ([38.901] §7.4.3.2):** $PL = PL_b + \mathcal{N}(\mu,\sigma_P^2)$ with
$\mu = 9$ dB (or 20 dB for metallised windows), $\sigma_P = 5$ dB, valid 0.6–60 GHz.

### 1.9 LOS probability ([38.901] Table 7.4.2-1)

These are the functions that make the UMa/UMi/RMa models *random*: draw the LOS state once per
drop with probability $\Pr_{LOS}(d_{2D-out})$, then pick the corresponding path-loss branch.

$$
\Pr_{LOS}^{\rm RMa}(d_{2D-out}) =
\begin{cases}
1, & d_{2D-out} \le 10\ \mathrm{m}\\
\exp\!\left(-\dfrac{d_{2D-out}-10}{1000}\right), & d_{2D-out} > 10\ \mathrm{m}
\end{cases}
\tag{1.9a}
$$

$$
\Pr_{LOS}^{\rm UMi}(d_{2D-out}) =
\begin{cases}
1, & d_{2D-out} \le 18\ \mathrm{m}\\[4pt]
\dfrac{18}{d_{2D-out}} + \exp\!\left(-\dfrac{d_{2D-out}}{36}\right)\!\left(1-\dfrac{18}{d_{2D-out}}\right), & d_{2D-out} > 18\ \mathrm{m}
\end{cases}
\tag{1.9b}
$$

$$
\Pr_{LOS}^{\rm UMa}(d_{2D-out}) =
\begin{cases}
1, & d_{2D-out} \le 18\ \mathrm{m}\\[6pt]
\left[\dfrac{18}{d_{2D-out}} + \exp\!\left(-\dfrac{d_{2D-out}}{63}\right)\!\left(1-\dfrac{18}{d_{2D-out}}\right)\right]
\left[1 + C'(h_{UT})\,\dfrac{5}{4}\left(\dfrac{d_{2D-out}}{100}\right)^{3}\exp\!\left(-\dfrac{d_{2D-out}}{150}\right)\right]^{-1},
& d_{2D-out} > 18\ \mathrm{m}
\end{cases}
\tag{1.9c}
$$

$$
C'(h_{UT}) =
\begin{cases}
0, & h_{UT} \le 13\ \mathrm{m}\\
\left(\dfrac{h_{UT}-13}{10}\right)^{1.5}, & 13\ \mathrm{m} < h_{UT} \le 23\ \mathrm{m}
\end{cases}
\tag{1.9d}
$$

The $C'(h_{UT})$ factor encodes a **second LoS branch**: for tall UTs ($13 < h_{UT}\le 23$ m) that
can see over rooftops, LoS is possible again far from the BS. For ground sensors at $h_{UT}=1.5$ m,
$C'=0$, so $\Pr_{LOS}^{\rm UMa}$ decays monotonically.

Indoor variants ([38.901] Table 7.4.2-1):

$$
\Pr_{LOS}^{\rm InH\text{-}mixed}(d_{2D-in}) =
\begin{cases}
1, & d_{2D-in}\le 1.2\ \mathrm{m}\\
\exp\!\left(-\dfrac{d_{2D-in}-1.2}{4.7}\right), & 1.2 < d_{2D-in} < 6.5\ \mathrm{m}\\
\exp\!\left(-\dfrac{d_{2D-in}-6.5}{32.6}\right)\cdot 0.32, & d_{2D-in}\ge 6.5\ \mathrm{m}
\end{cases}
\tag{1.9e}
$$

$$
\Pr_{LOS}^{\rm InH\text{-}open}(d_{2D-in}) =
\begin{cases}
1, & d_{2D-in}\le 5\ \mathrm{m}\\
\exp\!\left(-\dfrac{d_{2D-in}-5}{70.8}\right), & 5 < d_{2D-in}\le 49\ \mathrm{m}\\
\exp\!\left(-\dfrac{d_{2D-in}-49}{211.7}\right)\cdot 0.54, & d_{2D-in}>49\ \mathrm{m}
\end{cases}
\tag{1.9f}
$$

For InF: $\Pr_{LOS,\text{sub}}(d_{2D}) = \exp\!\left(-\dfrac{d_{2D}}{k_{sub}}\right)$ with

$$
k_{sub} = \begin{cases}
\dfrac{d_{clutter}}{-\ln(1-r)}, & \text{InF-SL, InF-DL}\\[8pt]
-\dfrac{d_{clutter}}{\ln(1-r)}\cdot\dfrac{h_{BS}-h_{UT}}{h_c-h_{UT}}, & \text{InF-SH, InF-DH}
\end{cases}
\tag{1.9g}
$$

($d_{clutter}, r, h_c$ in [38.901] Table 7.2-4); InF-HH has $\Pr_{LOS}=1$.

> **Note in [38.901] Table 7.4.2-1:** *"The LOS probability is derived with assuming antenna heights
> of 3 m for indoor, 10 m for UMi, and 25 m for UMa."* This is another hard constraint that breaks
> for an aerial BS.


### 1.10 On "$d_1, d_2, d_3$, $d_{2p}, d_{3p}$" — a notation correction

This is a common misconception and it matters, because implementing it wrong silently changes the
path-loss slope.

* **There are no $d_1, d_2, d_3$ and no $d_{2p}, d_{3p}$ in 3GPP TR 38.901.** I read Table 7.4.1-1
  of both V16.1.0 and V19.1.0 directly: the only distances are $d_{2D}$, $d_{3D}$,
  $d_{2D-out}$, $d_{3D-out}$, $d_{2D-in}$, $d_{3D-in}$, $W$, $h$ — and there is exactly **one**
  breakpoint per scenario, $d'_{\rm BP}$ (UMa, UMi, Note 1) or $d_{\rm BP}$ (RMa, SMa, Note 5).
* The notation $d_{2p}, d_{3p}$ (and the associated three-segment $PL_1/PL_2/PL_3$ with breakpoints
  at $d_{2p}$ and $d_{3p}$) belongs to the **older 3GPP TR 25.996 (UMTS Spatial Channel Model)
  UMa path-loss model**, which predates and was superseded by [38.901]. Rel-16+ [38.901] uses a
  two-segment LOS model with a single breakpoint.
* The physically meaningful breakpoint — the $d_{2p}$ of the old model — survives unchanged in
  form as (1.2a): $d'_{\rm BP} = 4h'_{BS}h'_{UT}f_c/c$. For RMa it is the $2\pi$ form (1.2d).
* $d_1$ is the reference distance (1 m in the normalised 3GPP formulation, $d_0$ in log-distance
  notation). It is *not* a second distance.

**Concrete numeric check** of $d'_{\rm BP}$ for a 25 m UMa BS and a 1.5 m UE at 3.5 GHz:
$h_E = 1$ m (since $h_{UT}<13$ m $\Rightarrow C=0 \Rightarrow$ drawn with probability 1), so
$h'_{BS}=24$ m, $h'_{UT}=0.5$ m, and

$$
d'_{\rm BP} = \frac{4 \cdot 24 \cdot 0.5 \cdot 3.5\times10^{9}}{3\times10^{8}} = 560\ \mathrm{m}.
$$

For RMa at $h_{BS}=35$ m, $h_{UT}=1.5$ m, 700 MHz:
$d_{\rm BP} = 2\pi\cdot35\cdot1.5\cdot7\times10^{8}/3\times10^{8} \approx 769$ m.

### 1.11 Frequency and bandwidth validity

[38.901] Note 2: *"The applicable frequency range of the PL formula in this table is
$0.5 < f_c < f_H$ GHz, where $f_H = 30$ GHz for RMa, $f_H = 37$ GHz for SMa, and $f_H = 100$ GHz
for all the other scenarios."* Rel-19 adds: *"RMa pathloss model for >7 GHz is validated based on a
single measurement campaign conducted at 24 GHz."*

[38.901] §4 scope: *"Bandwidth is supported up to 10 % of the center frequency but no larger than 2 GHz."*

**Consequence for a 2.4 GHz UAV-IoT link:** 2.4 GHz is inside the UMa/UMi/InH band
($0.5<f_c<100$ GHz), and a 200 kHz channel is $\ll 10\%$ of 2.4 GHz, so the bandwidth constraint
is satisfied.

### 1.12 The height validity limits — the "$22.5$ m" question, resolved

The premise in the brief needs a precise correction.

**What [38.901] Table 7.4.1-1 actually says, for both LOS and NLOS:**

| Scenario | $h_{UT}$ range | $h_{BS}$ nominal |
|---|---|---|
| UMa | $1.5 \le h_{UT} \le 22.5$ m | $25$ m |
| UMi-Street Canyon | $1.5 \le h_{UT} \le 22.5$ m | $10$ m |
| RMa | $1 \le h_{UT} \le 10$ m | $35$ m (range $10 \le h_{BS}\le150$ m) |
| InH / InF | none — $d_{3D}$ only | none |

So:

1. **$22.5$ m is the upper bound on $h_{UT}$, the *user terminal* (ground UE) height — not a
   UAV-altitude exclusion.** It exists because $C(d_{2D},h_{UT})$ and $C'(h_{UT})$ are only
   calibrated up to 23 m. A ground sensor at $h_{UT}=1.5$ m is comfortably *inside* it.
2. **The real exclusion is $h_{BS}$.** The UMa model was calibrated with $h_{BS}=25$ m and the
   LoS-probability derivation assumes $h_{BS}=25$ m; UMi with $h_{BS}=10$ m. If you set
   $h_{BS}=100$ m (a UAV) **you are extrapolating outside the calibrated envelope**, and the
   $-9\log_{10}((d'_{\rm BP})^2 + (h_{BS}-h_{UT})^2)$ term of (1.3c) plus the
   $4h'_{BS}h'_{UT}f_c/c$ breakpoint are both evaluated at an uncalibrated $h_{BS}$.
3. **You cannot dodge this by calling the UAV a "UT"**, because then $h_{UT}=100$ m violates
   $h_{UT}\le 22.5$ m.
4. **[38.901] contains no aerial-communication scenario at all.** A full-text search of V19.1.0 for
   "UAV", "aerial", "HAP" and "satellite" in the propagation clauses returns only ISAC *sensing
   targets* (clause 7.9, radar cross-section of UAVs) — no aerial BS/A2G path-loss or LoS-probability
   model. The scope clause (V19.1.0 §4) lists the supported system-level scenarios as *urban
   microcell street canyon, urban macrocell, indoor office, rural macrocell, indoor factory, and
   suburban macrocell* — all terrestrial.

§10 gives the practical resolutions.

---

## 2. Shadowing and fading

### 2.1 Log-normal shadow fading — distribution

The complete link loss in [38.901] is

$$
PL_{\rm total} = PL(f_c,d,h) + \sigma_{SF}\,\zeta, \qquad \zeta \sim \mathcal{N}(0,1)
\tag{2.1a}
$$

i.e. in linear power,

$$
\frac{P_r}{P_t} = \frac{G_t G_r \lambda^2}{(4\pi)^2 d^{\,n}} \cdot 10^{-\sigma_{SF}\zeta/10}
\tag{2.1b}
$$

with $n$ the effective PLE of the relevant branch. $\sigma_{SF}$ is tabulated in §1.3.
Note the sign convention ([38.901] Table 7.5-6 NOTE 2): **positive SF = more power received than
the mean path loss predicts**, so SF is *subtracted* from PL in a power-summed SINR.

Outage probability over the shadowing marginal alone:

$$
P_{\rm out}(d) \;=\; \Pr\!\left[ PL_{\rm total} > PL_{\max} \right]
\;=\; 1 - \Phi\!\left(\frac{PL_{\max}-PL_{\rm mean}(d)}{\sigma_{SF}}\right)
\;=\; \frac{1}{2}\,\operatorname{erfc}\!\left(\frac{PL_{\max}-PL_{\rm mean}(d)}{\sigma_{SF}\sqrt{2}}\right)
\tag{2.1c}
$$

Required fade margin for target outage $p$:

$$
M_{\rm SF}(p) \;=\; \sigma_{SF}\,\Phi^{-1}\!\left(1-\frac{p}{2}\right) \;=\; \sigma_{SF}\,\sqrt{2}\,\operatorname{erfc}^{-1}(p)
\tag{2.1d}
$$

Numerically (dB):

| target outage $p$ | $\sigma_{SF}=4$ dB | $\sigma_{SF}=6$ dB | $\sigma_{SF}=7.82$ dB |
|---|---|---|---|
| 0.20 | 5.126 | 7.689 | 10.022 |
| 0.10 | 6.579 | 9.869 | 12.863 |
| 0.05 | 7.840 | 11.760 | 15.327 |
| 0.01 | 10.303 | 15.455 | 20.143 |

### 2.2 Spatial correlation of shadowing

[38.901] §7.4.4, equation (7.4-5), citing ITU-R P.1816:

$$
R(\Delta x) \;=\; \exp\!\left(-\frac{\Delta x}{d_{cor}}\right)
\tag{2.2a}
$$

where $\Delta x$ is the separation **in the horizontal plane** and $d_{cor}$ is the correlation
length. The normalised autocorrelation of the realised shadow-fading field at two locations is
exactly (2.2a). Jointly Gaussian shadowing with this correlation is the standard model; a
convenient exact construction is the first-order autoregressive / Gauss–Markov process

$$
\sigma_{SF}(t+\Delta t) = e^{-\Delta t/\tau_{c}}\,\sigma_{SF}(t) + \sqrt{1-e^{-2\Delta t/\tau_{c}}}\; w(t),
\quad w\sim\mathcal{N}(0,\sigma_{SF}^{2})
\tag{2.2b}
$$

with $\tau_c = d_{cor}/v$ for a mobile of speed $v$.

**Correlation distances for shadowing** ([38.901] Tables 7.5-6 Part-1 and Part-2, "Correlation
distance in the horizontal plane", metres):

| Parameter | UMi LOS | UMi NLOS | UMi O2I | UMa LOS | UMa NLOS | UMa O2I | RMa LOS | RMa NLOS | InH LOS | InH NLOS |
|---|---|---|---|---|---|---|---|---|---|---|
| **SF** | 10 | 13 | 7 | **37** | **50** | 7 | **37** | **120** | 10 | 6 |
| DS | 7 | 10 | 10 | 30 | 40 | 10 | 50 | 36 | 8 | 5 |
| ASD | 8 | 10 | 11 | 18 | 50 | 11 | 25 | 30 | 7 | 3 |
| ASA | 8 | 9 | 17 | 15 | 50 | 17 | 35 | 40 | 5 | 3 |
| K | 15 | — | — | 12 | — | — | 40 | — | 4 | — |
| ZSA | 12 | 10 | 25 | 15 | 50 | 25 | 15 | 50 | 4 | 4 |
| ZSD | 12 | 10 | 25 | 15 | 50 | 25 | 15 | 50 | 4 | 4 |

For the spatially-consistent GSCM procedure ([38.901] Table 7.6.3.1-2, metres):

| Random variable | RMa | UMi | UMa | InH | InF |
|---|---|---|---|---|---|
| cluster & ray specific | 50 | 15 (LOS), 15 (NLOS), 15 (O2I) | 12 (LOS), 15 (NLOS), 40 (O2I) | 50 (LOS), 15 (NLOS), 10 (O2I) | 10 |
| LOS/NLOS state | 60 | 50 | 50 | 50 | $2\,d_{clutter}/\ln\!\left(1/(1-r)\right)$ |
| indoor/outdoor state | 50 | 50 | 50 | N/A | N/A |

**Relevance to a UAV swarm:** a UAV at 15 m/s crosses its own 50 m UMa-NLOS correlation length in
$50/15 = 3.33$ s. That is the timescale on which a UAV's shadowing realisation must be re-drawn
for spatial consistency. [38.901] §7.6.3.2 ("Procedure A") also constrains the regeneration
distance to within 1 m of the true motion.

### 2.3 Ricean $K$-factor in [38.901]

Table 7.5-6 gives the LOS $K$-factor as a log-normal variable:

| Scenario | $\mu_K$ [dB] | $\sigma_K$ [dB] |
|---|---|---|
| UMi-Street Canyon LOS | 9 | 5 |
| UMa LOS | 9 | 3.5 |
| RMa LOS | 7 | 4 |
| InH-Office LOS | 7 | 4 |
| all NLOS | N/A | N/A |

i.e. $K_{\rm dB} \sim \mathcal{N}(\mu_K,\sigma_K^2)$ and $K_{\rm linear} = 10^{K_{\rm dB}/10}$.
$K$ is *not* generated in NLOS because LoS is absent.

### 2.4 Rayleigh and Ricean small-scale fading

**Rayleigh** — complex envelope $h = h_I + j h_Q$ with $h_I, h_Q \sim \mathcal{N}(0,\sigma_h^2)$:

$$
f_{|h|}(h) = \frac{2h}{\overline{|h|^2}}\exp\!\left(-\frac{h^2}{\overline{|h|^2}}\right),\quad
\overline{|h|^2} = 2\sigma_h^2,
\qquad \mathbb{E}[|h|^2] = 1
\tag{2.4a}
$$

**Rice** — a deterministic specular component plus a Rayleigh diffuse component:

$$
h(t) = \sqrt{\frac{K}{K+1}}\,e^{j\phi(t)} + \sqrt{\frac{1}{K+1}}\left(x(t) + j y(t)\right),
\qquad x,y\sim\mathcal{N}(0,1/2)
\tag{2.4b}
$$

$$
K \;\equiv\; \frac{\mathbb{E}[|h_{\rm LOS}|^2]}{\mathbb{E}[|h_{\rm scatter}|^2]} \quad\text{(linear)},
\qquad K_{\rm dB} = 10\log_{10}K
\tag{2.4c}
$$

Envelope density, with $\sigma^2 = 1/[2(K+1)]$ and $A=\sqrt{K/(K+1)}$:

$$
f_{|h|}(r)=\frac{r}{\sigma^2}\exp\!\left(-\frac{r^2+A^2}{2\sigma^2}\right) I_0\!\left(\frac{A r}{\sigma^2}\right), \qquad r\ge 0
\tag{2.4d}
$$

where $I_0(\cdot)$ is the modified Bessel function of the first kind, order zero.

**Exactly what INET does** ([INET45] `src/inet/physicallayer/wireless/common/pathloss/RicianFading.cc`):

```cpp
double c  = 1.0 / (2.0 * (k + 1));              // k = 10^(K_dB/10)
double x  = normal(0,1),  y = normal(0,1);
double rr = c * ( (x + sqrt(2*k))*(x + sqrt(2*k)) + y*y );
return rr * freeSpacePathLoss;
```

i.e. INET implements the envelope square

$$
|h|^2 = \frac{\left(X+\sqrt{2K}\right)^2 + Y^2}{2(K+1)},\qquad X,Y\sim\mathcal N(0,1),
\tag{2.4e}
$$

which is algebraically equivalent to (2.4b) with $K$ in linear units, multiplies the *linear*
free-space path loss, and is redrawn **independently for every packet** (see §4.8).
`RayleighFading.cc` is the same with the $K$ term dropped:
$|h|^2 = \tfrac12(X^2+Y^2)$. `NakagamiFading.ned` adds a `shapeFactor` parameter.

### 2.5 Clarke's / Jakes' model, Doppler spread and coherence time

**Maximum Doppler shift** for a link with relative speed $v$, wavelength $\lambda=c/f_c$:

$$
f_{D,\max} = \frac{v}{\lambda} = \frac{v\,f_c}{c}
\tag{2.5a}
$$

**Clarke's model** ([Clarke]): a sum of sinusoids with uniformly distributed angles of arrival
$\theta_n \sim \mathcal U[0, 2\pi)$ and amplitudes $\propto 1/\sqrt N$:

$$
h(t) = \sqrt{\frac{2}{N}}\sum_{n=0}^{N-1}\left[\cos\!\left(2\pi f_{D}\cos\theta_n\, t + \phi_n\right) + j\sin\!\left(2\pi f_{D}\cos\theta_n\, t + \phi_n\right)\right]
\tag{2.5b}
$$

**Jakes' equal-spaced form** ([Jakes]) sets $\theta_n = 2\pi n/N$. Using the identity
$\sum_{n=0}^{N-1}\cos(2\pi n/N)=0$ and the recursive reduction of the cosine series, this reduces
to the familiar $N/2$-term form

$$
h(t) = \frac{1}{\sqrt N}\sum_{n=0}^{N/2-1}\left[\cos\!\left(\frac{f_D t}{N}\,(2\pi n - \pi) + \phi_n\right) + j\sin\!\left(\frac{f_D t}{N}\,(2\pi n - \pi) + \phi_n\right)\right]
\tag{2.5c}
$$

**Doppler spectrum** (the "Jakes/Clarke spectrum"):

$$
S_h(f) = \frac{1}{\pi f_{D,\max}\sqrt{1-\left(f/f_{D,\max}\right)^2}},\qquad |f| < f_{D,\max}
\tag{2.5d}
$$

**Coherence time** (several definitions; the one most used in OFDM/simulation literature):

$$
T_c = \frac{9}{16\pi\,f_{D,\max}} \approx 0.179\,T_D,
\qquad
T_D = \frac{1}{f_{D,\max}} \text{ (Doppler spread)},
\qquad
T_c^{\rm alt} = \frac{0.423}{f_{D,\max}}
\tag{2.5e}
$$

**Coherence bandwidth** from the RMS delay spread $\sigma_\tau$ ([38.901] Table 7.5-6):

$$
B_c \approx \frac{1}{5\sigma_\tau}
\tag{2.5f}
$$

**Numerical values at 2.4 GHz** ($c=2.998\times10^{8}$ m/s):

| speed $v$ | $f_{D,\max}$ | $T_c = 9/(16\pi f_D)$ | $0.423/f_D$ |
|---|---|---|---|
| 5 m/s | 40.028 Hz | 4.473 ms | 10.57 ms |
| 10 m/s | 80.055 Hz | 2.237 ms | 5.284 ms |
| 20 m/s | 160.111 Hz | 1.118 ms | 2.642 ms |

At a 15 m/s UAV cruise: $f_{D,\max}=120$ Hz, $T_c\approx1.49$ ms — **the same order as a 1 ms NR
TTI and shorter than a 100-byte packet at 1 Mbit/s (0.8 ms plus headers)**. This is the formal
justification for resampling fast fading per transmission (per TTI) rather than per packet, and it
is exactly what Simu5G does (§6.3).

### 2.6 RMS delay spread values you can use

From [38.901] Table 7.5-6: $\lg DS = \log_{10}(DS/1\ \mathrm{s})$. Median (i.e. $10^{\mu_{\lg DS}}$)
values:

| Scenario | $\mu_{\lg DS}$ | Median $DS$ at 2.4 GHz |
|---|---|---|
| UMa LOS | $-6.955 - 0.0963\log_{10}f_c$ | 226 ns |
| UMa NLOS | $-6.62$ | 240 ns |
| UMi LOS | $-0.24\log_{10}(1+f_c)-7.14$ | 52.8 ns |
| UMi NLOS | $-0.24\log_{10}(1+f_c)-6.83$ | 116 ns |
| RMa LOS / NLOS / O2I | $-7.49/-7.43/-7.47$ | 32.4 / 37.2 / 33.9 ns |
| InH-Office LOS | $-0.01\log_{10}(1+f_c)-7.692$ | 20.3 ns |

(Note 6/7 of Table 7.5-6: for UMa below 6 GHz use $f_c = 6$; for UMi below 2 GHz use $f_c = 2$.)


---

## 3. Link budget, SINR and rate

### 3.1 Friis / free-space path loss

$$
\frac{P_r}{P_t} = \frac{G_t(\theta_t,\phi_t)\,G_r(\theta_r,\phi_r)\,\lambda^2}{(4\pi)^2\,d^{\,n}\,L_{sys}}
\tag{3.1a}
$$

With $\alpha=2$ and $L_{sys}=1$:

$$
PL_{\rm FS}[\mathrm{dB}] = 20\log_{10}\!\left(\frac{4\pi\,d\,f_c}{c}\right) = 32.4478 + 20\log_{10}\!\left(\frac{f_c}{\mathrm{GHz}}\right) + 20\log_{10}\!\left(\frac{d}{\mathrm{m}}\right)
\tag{3.1b}
$$

Sanity values at 2.4 GHz: 80.05 dB @ 100 m; 94.03 dB @ 500 m; 100.05 dB @ 1000 m; 109.59 dB @ 3000 m.

**Two-ray ground reflection** (relevant when both ends are elevated, i.e. aerial-to-aerial):

$$
PL_{\rm 2R}[\mathrm{dB}] = 40\log_{10}\!\left(\frac{4\pi\, d\, f_c}{c}\right) - 20\log_{10}(h_t h_r)
\equiv 40\log_{10}(d) + 40\log_{10}(f_c) - 20\log_{10}(h_t h_r) + 40\log_{10}\!\left(\frac{4\pi}{c}\right)
\tag{3.1c}
$$

$$
d_{\rm cross} = \frac{4\pi\,h_t\,h_r}{\lambda}
\tag{3.1d}
$$

For $d<d_{\rm cross}$ use free space; for $d \ge d_{\rm cross}$ use (3.1c). With $h_t=h_r=100$ m and
$f_c=2.4$ GHz: $d_{\rm cross} = 4\pi\cdot10^{4}/0.12490 \approx 1.006\times10^{6}$ m — far beyond
any UAV deployment, so **two-ray never engages for a UAV-to-ground link**, but could for a
UAV-to-UAV link at mmWave or with very high antennas. Implemented verbatim in INET
`TwoRayGroundReflection.cc`.

### 3.2 EIRP, antenna gains, isotropic vs directional

$$
\mathrm{EIRP} \;=\; P_t + G_t - L_{\rm feeder}
\tag{3.2a}
$$

$$
P_r \;=\; \mathrm{EIRP} + G_r(\theta_r) - PL - L_{\rm feeder,r} - L_{\rm body}
\tag{3.2b}
$$

An isotropic antenna has $G=1$ (0 dBi) by definition; the 3GPP indoor/UMa models use
$G_{BS}=18$ dBi (Simu5G `antennGainEnB` default) and $G_{UE}=0$ dBi (Simu5G `antennaGainUe`
default), 3GPP micro $G=5$ dBi.

**3GPP UMa base-station antenna pattern:**

$$
G(\varphi) = G_{\max} - \min\!\left(12\,\frac{\varphi}{\varphi_{3\mathrm{dB}}},\ 30\right)\ \mathrm{dB},
\qquad |\varphi|\le \varphi_{3\mathrm{dB}} = 65^\circ
\tag{3.2c}
$$

i.e. linear-in-dB roll-off at $12/\varphi_{3\mathrm{dB}}$ dB per degree, floored at 30 dB.

**INET antenna models** ([INET45], all extend `AntennaBase`):

* `IsotropicAntenna` — $G \equiv 0$ dB (1.0 linear) in every direction.
* `ConstantGainAntenna` — parameter `gain @unit(dB)`, constant.
* `AxiallySymmetricAntenna` — parameters `baseGain @unit(dB)`, `gains` (a string of
  `angle[deg] gain[dB]` pairs, **the first pair must be at 0 deg**),
  `axisOfSymmetry @enum("x","y","z") = "x"`. Gain is obtained by **linear interpolation** in the
  angle between the first and last pair, and is **clamped outside** the tabulated range. This is
  how you encode (3.2c) exactly, e.g. `gains = "0 18 32.5 15 65 -12 180 -30"`.
* `CosineAntenna` — parameters `maxGain @unit(dB)`, `beamWidth @unit(deg)` (3 dB beamwidth):

$$
\mathrm{exponent} = \frac{-3}{20\log_{10}\!\left(\cos(\mathrm{beamWidth})/4\right)},
\qquad
G(\alpha) = G_{\max}\,|\cos(\alpha/2)|^{\mathrm{exponent}}
\tag{3.2d}
$$

  ([INET45] `CosineAntenna.ned`, citing Li Chunjian, "Efficient Antenna Patterns for
  Three-Sector WCDMA Systems," eq. B.1–B.2).
* `ParabolicAntenna`, `DipoleAntenna`, `InterpolatingAntenna` also exist.

### 3.3 Thermal noise

$$
N_0 = k\,T \quad [\mathrm{W/Hz}], \qquad k = 1.380\,649\times10^{-23}\ \mathrm{J/K} \text{ (SI, exact)}
\tag{3.3a}
$$

$$
N_0\big|_{T=290\,\mathrm K} = 4.003\,882\times10^{-21}\ \mathrm{W/Hz} = \boxed{-173.9752\ \mathrm{dBm/Hz}}
\qquad
N_0\big|_{T=300\,\mathrm K} = -173.8280\ \mathrm{dBm/Hz}
\tag{3.3b}
$$

$$
N = k\,T\,B + N_{\rm other} = N_0 + 10\log_{10}\!\left(\frac{B}{1\ \mathrm{Hz}}\right) + F\ \ [\mathrm{dBm}]
\tag{3.3c}
$$

| $B$ | thermal $N$ (dBm, $F=0$) |
|---|---|
| 10 kHz | $-123.9752$ |
| 200 kHz | $-120.9649$ |
| 1 MHz | $-113.9752$ |
| 10 MHz | $-103.9752$ |
| 20 MHz | $-100.9649$ |

The engineering rule of thumb $-174\ \mathrm{dBm/Hz}$ is a rounding; the exact figure at 290 K is
$-173.98$. **Noise figure** $F$ [dB] adds to the noise floor: $N_{\rm eff}=N_{\rm th}+F$.

> Simu5G hard-codes `thermalNoise = -104.5dBm` with the NED comment *"Thermal Noise for 10 MHz of
> Bandwidth"*, and separately `ueNoiseFigure = 7dBm`, `bsNoiseFigure = 5dBm`, `cableLoss = 2dB`.
> In `getSINR()` it computes `totN = dBmToLinear(thermalNoise_ + link.noiseFigure)`. So Simu5G's
> noise floor is a **single pre-computed constant per simulation**, not $kTB$ evaluated at run time.
> If you change the carrier bandwidth you **must** also change `thermalNoise`, or your SINRs will be
> silently wrong.

### 3.4 SINR, SNR and the $E_b/N_0$ family

$$
\mathrm{SINR} = \frac{P_{r,\rm desired}}{\displaystyle\sum_{i\in\mathcal{I}} P_{r,i} + N_{\rm eff}}
\quad\Longrightarrow\quad
\mathrm{SINR}[\mathrm{dB}] = P_{r}[\mathrm{dBm}] - \left(N_{\rm eff} + 10\log_{10}\sum_i g_i\right)[\mathrm{dBm}]
\tag{3.4a}
$$

where $g_i$ are interference power ratios. Equivalently, with a SINR threshold $\Gamma$:

$$
P_{r,\min} = N_{\rm eff} + \Gamma + 10\log_{10}\sum_i g_i
\tag{3.4b}
$$

**Relations between $E_s/N_0$, $E_b/N_0$ and SINR** for a rate $R_b$ in bandwidth $B$
([INET45] `MqamModulationBase.cc` uses exactly this):

$$
\frac{E_b}{N_0} = \frac{E_s}{N_0}\cdot\frac{1}{Q_m},
\qquad
\frac{E_s}{N_0} = \mathrm{SINR}\cdot\frac{B}{R_b} = \frac{\mathrm{SINR}}{\eta},
\qquad
\frac{E_b}{N_0} = \mathrm{SINR}\cdot\frac{B}{Q_m R_b} = \frac{\mathrm{SINR}}{\eta}
\tag{3.4c}
$$

with $\eta = R_b/B$ bits/s/Hz. In INET's convention the modulation `bitrate` equals $R_b$ and the
transmitter `bandwidth` equals $B$, so `EbN0 = snir * bandwidth / bitrate`; and
`BpskModulation::calculateSER` uses `snir*B/R` directly as the argument to `0.5*erfc(sqrt(.))`,
because `0.5*erfc(sqrt(Eb/N0))` **is** the coherent BPSK SER.

### 3.5 Shannon capacity, spectral efficiency, link margin

$$
C = B\log_2\!\left(1+\mathrm{SINR}\right)\ \ [\mathrm{bit/s}],
\qquad
\eta = \frac{R_b}{B} = \log_2(1+\mathrm{SINR}),
\qquad
\mathrm{SINR} = 2^{\eta}-1 = 10^{\eta_{\rm dB}/10}-1
\tag{3.5a}
$$

$$
\mathrm{SINR}_{\rm dB} = 10\log_{10}\!\left(2^{\eta}-1\right)
\tag{3.5b}
$$

| $\eta$ (bit/s/Hz) | 0.25 | 0.5 | 0.75 | 1.0 | 1.5 | 2.0 | 3.0 | 4.0 | 5.0 | 6.0 | 8.0 | 8.91 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SINR [dB] | $-7.231$ | $-3.828$ | $-1.663$ | $0.000$ | $2.621$ | $4.771$ | $8.451$ | $11.761$ | $14.914$ | $17.993$ | $24.065$ | $26.813$ |

**Link margin** (engineering definition):

$$
M_{\rm link} = P_{r,\rm nominal} - P_{r,\min},
\quad
P_{r,\min} = N_{\rm eff} + \gamma\;[\mathrm{dB}],
\quad
M_{\rm link} = \mathrm{EIRP} + G_r + G_{\rm sys} - PL - N_{\rm eff} - \gamma
\tag{3.5c}
$$

**Maximum tolerable path loss** (the number you actually invert to get a coverage radius):

$$
PL_{\max} = \mathrm{EIRP} + G_r + G_{\rm sys} - N_{\rm eff} - \gamma
\tag{3.5d}
$$

where $G_{\rm sys} = -L_{\rm feeder} - L_{\rm body} - L_{\rm implementation}$.


### 3.6 Required $E_b/N_0$ for a target BER — exact curves

**Coherent BPSK in AWGN** (the standard reference; used verbatim by INET
`BpskModulation.cc`):

$$
P_s = \frac{1}{2}\operatorname{erfc}\!\left(\sqrt{E_b/N_0}\right)
\equiv \frac{1}{2}\left(1-\operatorname{erf}\!\left(\sqrt{E_b/N_0}\right)\right)
\tag{3.6a}
$$

**Coherent QPSK** (Gray-coded, one bit pair per axis; identical $P_b$ as BPSK):

$$
P_b = P_s = \frac{1}{2}\operatorname{erfc}\!\left(\sqrt{E_b/N_0}\right)
\tag{3.6b}
$$

**Rectangular M-QAM** — this is exactly INET's `MqamModulationBase::calculateBER`, with $M$ the
constellation size and $k=\log_2M$ bits per symbol:

$$
\boxed{\;
P_b = \frac{4}{k}\left(1-\frac{1}{\sqrt{M}}\right)\frac{1}{2}\operatorname{erfc}\!\left(\frac{1}{\sqrt{2}}\sqrt{\frac{3k}{M-1}\frac{E_b}{N_0}}\right)
\;}
\tag{3.6c}
$$

and `calculateSER`, with $E_s/N_0$:

$$
\boxed{\;
P_{sc} = 2\left(1-\frac{1}{\sqrt{M}}\right)\frac{1}{2}\operatorname{erfc}\!\left(\frac{1}{\sqrt{2}}\sqrt{\frac{3}{M-1}\frac{E_s}{N_0}}\right),
\qquad P_s = 1-\left(1-P_{sc}\right)^2
\;}
\tag{3.6d}
$$

**Numerical BER vs $E_b/N_0$** (exact evaluation of (3.6a), (3.6c), (3.6d)):

| $E_b/N_0$ [dB] | BPSK/QPSK $P_b$ | 64-QAM $P_b$ (3.6c) | 64-QAM $P_s$ (3.6d) |
|---|---|---|---|
| 0 | $7.865\times10^{-2}$ | $5.554\times10^{-2}$ | $3.055\times10^{-1}$ |
| 2 | $3.751\times10^{-2}$ | $2.896\times10^{-2}$ | $1.662\times10^{-1}$ |
| 4 | $1.250\times10^{-2}$ | $1.108\times10^{-2}$ | $6.535\times10^{-2}$ |
| 6 | $2.388\times10^{-3}$ | $2.622\times10^{-3}$ | $1.567\times10^{-2}$ |
| 8 | $1.909\times10^{-4}$ | $2.934\times10^{-4}$ | $1.760\times10^{-3}$ |
| 10 | $3.872\times10^{-6}$ | $1.011\times10^{-5}$ | $6.067\times10^{-5}$ |

Inverting (3.6a) exactly for a target BER:

$$
\left(\frac{E_b}{N_0}\right)_{\rm req} = \left[\operatorname{erfc}^{-1}\!\left(2P_b^{\rm target}\right)\right]^2,
\qquad
\gamma_{\rm req} = \frac{E_b}{N_0} - 10\log_{10}\eta
\tag{3.6e}
$$

giving (BPSK/QPSK): $\approx 9.6$ dB for $P_b=10^{-5}$, $\approx 14.0$ dB for $P_b=10^{-7}$.

**Packet error rate from BER** (INET `ApskErrorModel::computePacketErrorRate`, verbatim):

$$
P_{H} = 1-\left(1-P_b\right)^{L_{H}},
\qquad
P_{D} = 1-\left(1-P_b\right)^{L_{D}},
\qquad
\boxed{\;\mathrm{PER} = 1 - \left(1-P_b\right)^{L_H}\left(1-P_b\right)^{L_D}\;}
\tag{3.6f}
$$

for `SIGNAL_PART_WHOLE`; $1-(1-P_b)^{L_H}$ for the header part and $1-(1-P_b)^{L_D}$ for the data
part. With `corruptionMode` set to `chunk`/`byte`/`bit`, individual chunks are corrupted with the
corresponding probability instead of all-or-nothing.

### 3.7 5G NR CQI / MCS and the numerology

**Numerology** ([38.211] Table 5.3.2-1, [38.104]):

| $\mu$ | $\Delta f = 15\cdot 2^{\mu}$ kHz | slot duration $2^{\mu}$ ms | FR1 | FR2 |
|---|---|---|---|---|
| 0 | 15 | 1 | yes | yes |
| 1 | 30 | 2 | yes | yes |
| 2 | 60 | 4 | yes | yes |
| 3 | 120 | 8 | yes | yes |
| 4 | 240 | 16 | no (FR1 max 100 MHz) | yes |

$$
N_{\rm RB} = \frac{B}{12\,\Delta f} \quad (\Delta f \text{ in Hz}), \qquad
\text{subframe} = 1\ \mathrm{ms},\ \text{frame} = 10\ \mathrm{ms},\ \text{TTI} = 1\ \mathrm{slot}
\tag{3.7a}
$$

**CQI table** ([38.214] Table 7.2.3-1, as encoded in [Simu5G] `NrMcs.cc`; code rate $\times 1024$):

| CQI | Modulation | $R\cdot1024$ | $R$ | $\eta=Q_m R$ |
|---|---|---|---|---|
| 0 | out of range | 0 | 0 | 0 |
| 1 | QPSK | 78 | 0.076172 | 0.152344 |
| 2 | QPSK | 120 | 0.117188 | 0.234375 |
| 3 | QPSK | 193 | 0.188477 | 0.376953 |
| 4 | QPSK | 308 | 0.300781 | 0.601562 |
| 5 | QPSK | 449 | 0.438477 | 0.876953 |
| 6 | QPSK | 602 | 0.587891 | 1.175781 |
| 7 | 16QAM | 378 | 0.369141 | 1.476562 |
| 8 | 16QAM | 490 | 0.478516 | 1.914062 |
| 9 | 16QAM | 616 | 0.601562 | 2.406250 |
| 10 | 64QAM | 466 | 0.455078 | 2.730469 |
| 11 | 64QAM | 567 | 0.553711 | 3.322266 |
| 12 | 64QAM | 666 | 0.650391 | 3.902344 |
| 13 | 64QAM | 772 | 0.753906 | 4.523438 |
| 14 | 64QAM | 873 | 0.852539 | 5.115234 |
| 15 | 64QAM | 948 | 0.925781 | 5.554688 |

**MCS (iTBS) table** ([38.214] Tables 5.1.3.1-1 / 5.1.3.1-2, as encoded in [Simu5G] `NrMcs.cc`):

| iTBS | Mod | $R{\cdot}1024$ | $\eta$ | iTBS | Mod | $R{\cdot}1024$ | $\eta$ |
|---|---|---|---|---|---|---|---|
| 0 | QPSK | 120 | 0.234375 | 15 | 16QAM | 616 | 2.406250 |
| 1 | QPSK | 157 | 0.306641 | 16 | 16QAM | 658 | 2.570312 |
| 2 | QPSK | 193 | 0.376953 | 17 | 64QAM | 438 | 2.566406 |
| 3 | QPSK | 251 | 0.490234 | 18 | 64QAM | 466 | 2.730469 |
| 4 | QPSK | 308 | 0.601562 | 19 | 64QAM | 517 | 3.029297 |
| 5 | QPSK | 379 | 0.740234 | 20 | 64QAM | 567 | 3.322266 |
| 6 | QPSK | 449 | 0.876953 | 21 | 64QAM | 616 | 3.609375 |
| 7 | QPSK | 526 | 1.027344 | 22 | 64QAM | 666 | 3.902344 |
| 8 | QPSK | 602 | 1.175781 | 23 | 64QAM | 719 | 4.212891 |
| 9 | QPSK | 679 | 1.326172 | 24 | 64QAM | 772 | 4.523438 |
| 10 | 16QAM | 340 | 1.328125 | 25 | 64QAM | 822 | 4.816406 |
| 11 | 16QAM | 378 | 1.476562 | 26 | 64QAM | 873 | 5.115234 |
| 12 | 16QAM | 434 | 1.695312 | 27 | 64QAM | 910 | 5.332031 |
| 13 | 16QAM | 490 | 1.914062 | 28 | 64QAM | 948 | 5.554688 |
| 14 | 16QAM | 553 | 2.160156 | | | | |

The TBS table (`nInfoToTbs[94]`, TS 38.214 Table 5.1.3.2-1) is reproduced verbatim in
[Simu5G] `NrMcs.cc`; for $N_{info}>3824$, $TBS = \lfloor N_{info}\rfloor\cdot\frac{1000}{8}$ bits.

Simu5G additionally provides the **extended** table (`extended = true`), which reaches
256QAM at iTBS 20–27 and 0–4 / 5–10 / 11–19 for QPSK / 16QAM / 64QAM.

> The MCS $\eta$ values above are **gross** spectral efficiency (modulation x code rate), before
> the TS 38.214 layer-1 overhead ($\approx$14–17 % depending on $\mu$, PRB size and
> reference-signal configuration). A 12-PRB allocation at $\mu=0$ carries
> $12\times12\times14 = 2016$ subcarriers of $1/\Delta f$ each, i.e.
> $2016\times66.67 = 134.4\ \mu$s$ of payload per 1 ms slot — before CP, DMRS, CSI-RS and PDCCH.


---

## 4. How the simulation stack turns this into packet outcomes

### 4.1 INET 4.5 module names — and the renames from INET 3.x

**This is a frequent source of broken `.ned` files.** In INET 4.x the `...Channel` classes were
renamed `...RadioMedium`, and `DmgErrorModel` became `ApskErrorModel`.

| Old (INET <= 3.5 / tutorials on the web) | **INET 4.5 correct name** | NED package |
|---|---|---|
| `IpRadioChannel` | `IpRadioMedium` | `inet.physicallayer.wireless.common.medium` |
| `ScalarRadioChannel` | `ScalarRadioMedium` | `...wireless.common.medium` |
| `DimensionalRadioChannel` | `DimensionalRadioMedium` | `...wireless.common.medium` |
| `UnitdiskRadio` | **`UnitDiskRadio`** (capital D) | `inet.physicallayer.wireless.unitdisk` |
| `DmgErrorModel` | **`ApskErrorModel`** | `...wireless.apsk.packetlevel.errormodel` |
| `PERTableRadioErrorModel` | **does not exist in INET 4.x** | use `ApskErrorModel` or `StochasticErrorModel` |
| `IdealRadio` / `IdealRadioChannel` | `IdealWirelessRadio` / `IdealWirelessRadioMedium` | `...wireless.ideal` |
| `ApskScalarRadio` | `ApskScalarRadio` (unchanged) | `...wireless.apsk.packetlevel` |
| `ApskDimensionalRadio` | `ApskDimensionalRadio` (unchanged) | `...wireless.apsk.packetlevel` |

(`PERTableRadioModel` and `PerTableRadioErrorModel` were removed in INET 4.0; the replacement for
a lookup-table model in 4.5 is a custom `IErrorModel`, or `StochasticErrorModel` for a fixed PER.)

### 4.2 The three analog representations

`RadioMedium` (`[INET45]` `src/inet/physicallayer/wireless/common/medium/RadioMedium.ned`) chooses
the representation with a single parameter:

```ned
string signalAnalogRepresentation @enum("unitDisk","scalar","dimensional") = default("scalar");
```

**`ScalarAnalogModel`** — "computes with scalar analog power representation. In other words, the
signal power does not change over time or frequency, except for the boundaries of the signal."

```ned
bool ignorePartialInterference = default(false);
```

For a transmission $T$ received at radio $r$ at time $t$:

$$
P_r(t) = P_{t,\rm tx}\cdot G_t(\theta_t)\cdot G_r(\theta_r)\cdot PL(f_c, d(t))^{-1}\cdot OB^{-1}\cdot 10^{SF/10}\cdot \mathbb{1}\{\text{listening}\}
\tag{4.2a}
$$

computed **once per transmission** at the reception start
(`ScalarAnalogModel.cc::computeReception`).

**`DimensionalAnalogModel`** — power is a *function* of time and frequency $(t,f)$ represented by
"gain functions", so a receiver can see a changing SNR mid-packet.

```ned
bool attenuateWithCenterFrequency = default(true);
```

This is what you want for mmWave / OFDM / frequency-selective scenarios, or if you want a
frequency-selective (per-subcarrier) channel. It is much slower.

**`UnitDiskAnalogModel`** — no powers at all; pure geometry (see §4.6).

### 4.3 Path-loss (`IPathLoss`) models in INET 4.5

All in `inet.physicallayer.wireless.common.pathloss`:

| NED module | Key parameters (defaults) | Math |
|---|---|---|
| `FreeSpacePathLoss` | `double alpha = 2;` `double systemLoss @unit(dB) = 0dB;` | (4.3a) |
| `LogNormalShadowing` (extends FSPL) | `double sigma = 1;` | (4.3b) |
| `RayleighFading` (extends FSPL) | — | $\tfrac12(X^2+Y^2)\cdot L_{FS}$ |
| `RicianFading` (extends FSPL) | `double k @unit(dB) = 8dB;` | (2.4e) |
| `NakagamiFading` (extends FSPL) | `double shapeFactor = 1;` | Nakagami-$m$ |
| `BreakpointPathLoss` | `l01`, `l02`, `alpha1`, `alpha2`, `breakpointDistance @unit(m)` | (4.3c) |
| `TwoRayGroundReflection` (extends FSPL) | `physicalEnvironmentModule = "physicalEnvironment"` | (3.1c) |
| `SuiPathLoss`, `UwbIrStochasticPathLoss` | — | niche |

**`FreeSpacePathLoss.cc` — verbatim:**

```cpp
double FreeSpacePathLoss::computeFreeSpacePathLoss(m waveLength, m distance, double alpha, double systemLoss) const
{
    return distance.get() == 0.0 ? 1.0
         : (waveLength*waveLength).get() / (16*M_PI*M_PI*systemLoss*pow(distance.get(), alpha));
}
m FreeSpacePathLoss::computeRange(mps propagationSpeed, Hz frequency, double loss) const
{
    m waveLength = propagationSpeed / frequency;
    return m(pow((waveLength*waveLength).get()/(16.0*M_PI*M_PI*systemLoss*loss), 1.0/alpha));
}
```

i.e.

$$
L(d) = \frac{\lambda^{2}}{16\pi^{2}\,L_{sys}\,d^{\,\alpha}},
\qquad
d(L) = \left(\frac{\lambda^{2}}{16\pi^{2}\,L_{sys}\,L}\right)^{1/\alpha}
\tag{4.3a}
$$

with $\alpha$ the *path-loss exponent* (not the Rician exponent) and $L_{sys}=10^{systemLoss/10}$.
With $\alpha=2$, $L_{sys}=1$: $L = (\lambda/(4\pi d))^2$, i.e. exactly (3.1a). `computeRange` is
the exact inverse — the function to call when you want to derive a `communicationRange` from a
target SINR, which is exactly the right thing to do for a UAV-IoT "coverage radius" reward.

**`LogNormalShadowing.cc` — verbatim:**

```cpp
m d0 = m(1.0);
double freeSpacePathLoss = computeFreeSpacePathLoss(propagationSpeed/frequency, d0, alpha, systemLoss);
double PL_d0_db = 10.0*log10(1/freeSpacePathLoss);
double PL_db = PL_d0_db + 10*alpha*log10(unit(distance/d0).get()) + normal(0.0, sigma);
return math::dB2fraction(-PL_db);
```

$$
PL_{\rm dB}(d) = PL_{\rm d0} + 10\alpha\log_{10}\!\left(\frac{d}{d_0}\right) + \mathcal{N}(0,\sigma^2),
\qquad d_0 = 1\ \mathrm{m}
\tag{4.3b}
$$

**Critical caveat:** `LogNormalShadowing` draws an **independent** $\mathcal{N}(0,\sigma)$ for every
packet, with no spatial correlation whatsoever, and `sigma` is in **dB** (it is *not* converted
to/from linear). If you want [38.901]'s $\sigma_{SF}$ of 4/6/7.82 dB with 37/50/13 m correlation,
set `sigma = 4` (dB) and then **subclass** the model to add the correlation of (2.2a)/(2.2b).
INET 4.5 has no built-in spatially-correlated shadowing model.

**`BreakpointPathLoss.cc` — verbatim:**

```cpp
if (distance < breakpointDistance) return 1/(l01*pow(distance.get(), alpha1));
else                             return 1/(l02*pow(unit(distance/breakpointDistance).get(), alpha2));
```

$$
L(d) = \begin{cases}
\dfrac{1}{l_{01}\,d^{\alpha_1}}, & d < d_{BP}\\[8pt]
\dfrac{1}{l_{02}\,(d/d_{BP})^{\alpha_2}}, & d \ge d_{BP}
\end{cases}
\tag{4.3c}
$$

To match [38.901] UMa LOS, with the model in *linear* loss $L=10^{PL/10}$:

$$
L_{01} = 10^{-\left(28.0+20\log_{10}f_c\right)/10}\cdot\frac{1}{(1\ \mathrm{m})^{\alpha_1}},\quad
\alpha_1 = 2.2,\quad
L_{02} = \dfrac{L(d_{BP})}{d_{BP}^{\alpha_2}},\quad \alpha_2 = 4.0
\tag{4.3d}
$$

i.e. `alpha1 = 2.2`, `alpha2 = 4.0`, `breakpointDistance = d'BP`, and `l02` chosen so that
(4.3c) is continuous at the breakpoint. This reproduces the 40 dB/decade vs 22 dB/decade slope
difference of (1.3b)/(1.3c) but **not** the $-9\log_{10}(\cdot)$ $h_{BS}-h_{UT}$ correction; for
that you need a custom `IPathLoss` subclass.

### 4.4 Propagation-delay models

`inet.physicallayer.wireless.common.propagation`:

* `ConstantSpeedPropagation extends PropagationBase` — parameters
  `ignoreMovementDuringTransmission = true`, `ignoreMovementDuringPropagation = true`,
  `ignoreMovementDuringReception = true`; the delay is
  $$t_{prop} = \frac{d(t)}{v_{prop}},\qquad \text{PropagationBase.propagationSpeed @unit(mps) = 299792458mps}$$
* `ConstantTimePropagation` — parameter `propagationTime @unit(s) = 0s`; a fixed delay.

**Set `ignoreMovementDuringPropagation = false`** for a fast UAV: the receiver moves while the
wavefront travels, so the correct model is a closed-form interception solution rather than
$d(t)/c$. For a UAV at $v=15$ m/s over a 1 km link the naive error is
$1000\times15/(3\times10^{8}) = 50\ \mu$s — negligible against a 1 ms TTI, but not negligible
against a sub-$\mu$s target. Keep the flags mutually consistent: mixing
`ignoreMovementDuringPropagation=true` with `ignoreMovementDuringReception=false` is legal but
means the wavefront is computed at the transmit-time geometry and only the *reception* position
is updated.

### 4.5 Antenna models and how the angle is computed

The receiver antenna gain is evaluated at the angle between the antenna's orientation (from its
`StationaryMobilityModel`'s `getOrientation()`) and the direction to the transmitter. For a
downward-looking UAV this matters enormously: the elevation angle to a sensor at horizontal
distance $r$ from the nadir point is

$$
\theta = \arctan\!\left(\frac{h}{r}\right),
\qquad
\theta(45^\circ) \Leftrightarrow r = h, \quad
\theta(30^\circ) \Leftrightarrow r = \sqrt{3}\,h
\tag{4.5a}
$$

At $h=100$ m: $r=100$ m gives 45.00°, 300 m gives 18.18°, 600 m gives 9.32°, 1000 m gives 5.63°,
1179 m gives 4.78°.

### 4.6 `UnitDiskRadio` vs the real radio models — a full comparison

| | `UnitDiskRadio` + `UnitDiskRadioMedium` | `ApskDimensionalRadio` + `DimensionalRadioMedium` | `ApskScalarRadio` + `ScalarRadioMedium` |
|---|---|---|---|
| Representation | none (geometry only) | scalar per transmission | power x time x frequency gain functions |
| **Path loss model** | none | `pathLoss` submodule (default `FreeSpacePathLoss`) | same |
| **Shadowing** | none | only if your `IPathLoss` adds it | same |
| **Fast fading** | none | only if your `IPathLoss` adds it | same |
| **Reception decision** | distance: `d < communicationRange` **AND** no interfering tx within `interferenceRange` (unless `ignoreInterference = true`) | SNIR: `snir.getMin() > snirThreshold` (`snirThresholdMode = "min"`) or `snir.getMean() > snirThreshold` | same |
| Noise | none | `backgroundNoise` submodule | same |
| Antenna gain | **not used** | `IAntenna` | same |
| Sensitivity to movement | hard distance cut-off | smooth power | smooth power |
| Speed | ~1000x faster | slow | medium |
| Use for UAV-IoT? | **only** as an ablation/sanity baseline | recommended if you need frequency selectivity or time-varying power | **recommended default** |

**`UnitDiskTransmitter.ned` parameters, verbatim:**

```ned
double preambleDuration @unit(s) = default(0s);
int    headerLength     @unit(b) = default(96b);
double bitrate          @unit(bps);
double communicationRange @unit(m);
double interferenceRange @unit(m) = default(communicationRange);
double detectionRange      @unit(m) = default(interferenceRange);
```

**`UnitDiskReceiver.ned`:**

```ned
bool ignoreInterference = default(false);
```

The reception power state machine (`UnitDiskReception.h`) is
`POWER_UNDETECTABLE < POWER_DETECTABLE < POWER_INTERFERING < POWER_RECEIVABLE`, classified purely
by comparing $d$ to `detectionRange`, `interferenceRange`, `communicationRange`.

> **Do not use `UnitDiskRadio` as your main model.** Its `communicationRange` is a hard cut-off:
> it produces a coverage *disc*, not an altitude-dependent path-loss law, and it cannot represent
> the 40 dB/decade NLOS slope of (1.3e) or the LOS/NLOS state mixture of (1.9c). It is useful for
> debugging the RL agent's action space and for fast hyper-parameter sweeps.

**`SnirReceiverBase.cc` — the reception decision, verbatim:**

```cpp
snirThreshold = math::dB2fraction(par("snirThreshold"));
if (!strcmp("min",  par("snirThresholdMode").get())) snirThresholdMode = SnirThresholdMode::STM_MIN;
else if (!strcmp("mean", ...))                     snirThresholdMode = SnirThresholdMode::STM_MEAN;
...
bool SnirReceiverBase::computeIsReceptionSuccessful(...) const {
    if (snirThresholdMode == STM_MIN)     return snir->getMin()  > snirThreshold;
    else if (snirThresholdMode == STM_MEAN) return snir->getMean() > snirThreshold;
}
```

**`SnirReceiverBase.ned`:**

```ned
double snirThreshold @unit(dB);
string snirThresholdMode @enum("min","mean") = default("min");
```

`snirThresholdMode = "min"` is the conservative choice: with `DimensionalRadioMedium` the SNR
varies over the packet, and requiring the *worst* SNR over the packet to exceed the threshold is
physically the right interpretation of "can I decode this whole packet".

**`ErrorModelBase.ned` — the three tunables that matter:**

```ned
string corruptionMode @enum("packet","chunk","byte","bit") = default("packet");
string snirMode       @enum("min","mean")                   = default("min");
double snirOffset     @unit(dB) = default(0dB);
```

`snirOffset` is the INET hook for implementation impairments (CP-OFDM lobe overlap, oscillator
offset, etc.): the error model is evaluated at $\mathrm{SINR} - \texttt{snirOffset}$.


### 4.7 Error models in detail

**`ApskErrorModel`** (`...apsk.packetlevel.errormodel`) has **no parameters of its own** — it takes
the modulation from the transmission and calls the modulation's own `calculateBER`/`calculateSER`
(§3.6). The modulations (`...wireless.common.modulation`, resolved by
`ApskModulationBase::findModulation`) are: `BPSK`, `QPSK`, `QAM-16`, `QAM-64`, `QAM-256`,
`MQAM-<n>`, `MPSK-<n>`, `DSSS-OQPSK-16`, plus `DBPSK`, `DQPSK`, `QBPSK`, `16PPM`, `4PPM`, `2GFSK`,
`4GFSK`, `MFSK-<n>`.

`QPSKModulation` and `Qam64Modulation` are constructed from the *same* `MqamModulationBase` with
$M=4$ and $M=64$ respectively, so QPSK in INET uses (3.6c)/(3.6d) with $M=4$, $k=2$:

$$
P_b^{\rm QPSK} = \frac{4}{2}\left(1-\frac{1}{2}\right)\frac{1}{2}\operatorname{erfc}\!\left(\frac{1}{\sqrt 2}\sqrt{\frac{6}{3}E_b/N_0}\right)
= \frac{1}{2}\operatorname{erfc}\!\left(\sqrt{E_b/N_0}\right)
\tag{4.7a}
$$

— algebraically identical to (3.6b). INET's QPSK and BPSK therefore give the same BER curve, as
theory requires.

**`StochasticErrorModel`** (`...common.errormodel.packetlevel`):

```ned
double packetErrorRate  = default(nan);   // [0,1] or NaN
double bitErrorRate     = default(nan);
double symbolErrorRate  = default(nan);
```

An INET fixed-PER model independent of SINR. Useful to isolate the effect of a packet error rate
from the effect of SINR. **NaN = not set**, and NaN is ignored — so setting only `packetErrorRate`
gives you a constant PER.

**Bilevel (`...apsk.bitlevel.errormodel.ApskLayeredErrorModel`)** models bits in blocks with real
modulation/demodulation and error correction (`ConvolutionalCoder`, `ApskModulator`,
`ApskDemodulator`, `LayeredErrorModelBase`). Use this if you want to study coding/HARQ effects.

### 4.8 Per-packet vs per-block fading — the crucial distinction

| | Where fading is drawn | Consequence |
|---|---|---|
| **INET `RicianFading` / `RayleighFading` / `LogNormalShadowing`** | inside `IPathLoss::computePathLoss()`, i.e. **once per received packet** | fast fading and shadowing are both **i.i.d. per packet**. Physically wrong for both (fast fading decorrelates in ~1 ms; shadowing decorrelates in ~3 s). Net effect: SINR becomes memoryless => your PDR is far too *high* (bursty outages never happen) and your jitter is far too *low*. |
| **INET `ScalarRadioMedium`** | power computed once per transmission; `DimensionalRadioMedium` computes the min/mean over the packet's $(t,f)$ extent | still per-packet, but `snirThresholdMode="min"` correctly penalises packets that fade during transmission |
| **Simu5G `StochasticChannelModel`** | shadowing re-drawn only when the UE has moved $>$ `correlationDistance` (default 50 m); Jakes fading re-drawn **per carrier band (PRB) per TTI** | **per-block** fading, **spatially correlated** shadowing. Physically correct at TTI granularity. |
| **TR 38.901 GSCM** | clusters/paths generated per drop; spatial-consistency Procedure A/B of §7.6.3 updates them at most every 1 m of movement | per-$O(\mathrm{m})$ |

**The exact Simu5G fading code** (`StochasticChannelModel.cc::jakesFading`):

```cpp
double doppler_shift = (speed * f) / SPEED_OF_LIGHT;          // f_D,max   [Hz]
simtime_t t = simTime().dbl() - 0.001;                        // TTI = 1 ms
for (int i = 0; i < fadingPaths_; i++) {
    double phi_d = actualJakesData.angleOfArrival[i] * doppler_shift;
    double phi_i = actualJakesData.delaySpread[i].dbl() * f;
    double phi   = 2.00*M_PI*(phi_d*t.dbl() - phi_i);
    double attenuation = (1.00/sqrt(static_cast<double>(fadingPaths_)));
    re_h += attenuation*cos(phi);
    im_h -= attenuation*sin(phi);
}
return linearToDb(re_h*re_h + im_h*im_h);
```

i.e.

$$
|H_f|^2 = \left|\sum_{i=1}^{L}\frac{1}{\sqrt L}\Big(\cos\phi_i - j\sin\phi_i\Big)\right|^2,
\qquad
\phi_i = 2\pi\Big(\theta_i f_{D,\max}\, t - \tau_i f_c\Big)
\tag{4.8a}
$$

with $L = $ `numFadingPaths` (default 6), $\theta_i$ uniform in $[0,2\pi)$, $\tau_i$ the per-tap
delay spread. This is Cavers' simplification of Jakes: only $1/L$ amplitude per tap (isotropic
antenna => the $a^2$ weight is unity for unit fade depth) plus explicit frequency selectivity
through $\tau_i f_c$.

**The exact Simu5G shadowing correlation** (`StochasticChannelModel.cc::computeShadowing`):

```cpp
else if (((NOW - actualShadowingMap->at(key).first).dbl())*speed > correlationDistance_) {
    double time  = (NOW - actualShadowingMap->at(key).first).dbl();
    double space = time * speed;
    double a  = exp(-0.5*(space / correlationDistance_));        // <-- note the 0.5
    double z0 = <previous sample>;
    double z1 = a*z0 + sqrt(1 - a*a)*<new N(0,sigma)>;           // exponential average window
    ...
}
```

$$
\sigma(t) = a\,\sigma(t^{-}) + \sqrt{1-a^2}\,w,\qquad
a = \exp\!\left(-\frac{\Delta x}{2\,d_{cor}}\right),\qquad \Delta x = v\,\Delta t
\tag{4.8b}
$$

This is *not* the [38.901] correlation $e^{-\Delta x/d_{cor}}$: the factor $2$ in the denominator
means Simu5G's effective correlation length is $2\times$ `correlationDistance`. With the default
`correlationDistance = 50m`, the effective $d_{cor}$ is **100 m** — twice the [38.901] UMa-NLOS
value of 50 m. If you want exact [38.901] correlation, set `correlationDistance` to
`rSF/2` (e.g. 25 m for UMa NLOS).

### 4.9 A complete, correct INET NED skeleton

```ned
simple UavWirelessNode
{
    parameters:
        mobility: has Mobility;
        radio: <default("ApskScalarRadio")> like IWirelessRadio;
        medium: RadioMedium {
            @display("p=0,0");
            propagation: <default("ConstantSpeedPropagation")> like IPropagation {
                parameters:
                    propagationSpeed = 299792458mps;
                    ignoreMovementDuringPropagation = false;
                    ignoreMovementDuringReception = false;
            }
            analogModel: <default("ScalarAnalogModel")> like IAnalogModel;
            backgroundNoise: <default("IsotropicScalarBackgroundNoise")> like IBackgroundNoise {
                parameters:
                    power     = -121dBm;   // N0 + 10log10(B), NF folded in; B = 200 kHz, F = 7 dB
                    bandwidth = 200kHz;
            }
            // Custom: 3GPP TR 38.901 UMa LOS+NLOS as an IPathLoss subclass.
            pathLoss: <default("Tr38901UmaPathLoss")> like IPathLoss {
                parameters:
                    sigmaSfLos  = 4dB;
                    sigmaSfNlos = 6dB;
                    useLosProbability = true;
                    heightBs = 100m;      // CAVEAT: outside the [38.901] hBS = 25 m envelope
                    heightUt = 1.5m;
                    correlationDistance = 25m;  // = 50 m / 2, see (4.8b)
            }
        }
}
```

and the transmitter/receiver:

```ned
simple UavRadio extends ApskScalarRadio {
    parameters:
        transmitter.typename  = default("ApskScalarTransmitter");
        receiver.typename     = default("ApskScalarReceiver");
        receiver.errorModel.typename = default("ApskErrorModel");
        transmitter.centerFrequency = 2.4GHz;
        transmitter.bandwidth       = 200kHz;
        transmitter.bitrate         = 1Mbps;
        transmitter.power           = 20dBm;
        transmitter.ber             = 0;
        receiver.errorModel.corruptionMode = "packet";
        receiver.errorModel.snirMode       = "min";
        receiver.errorModel.snirOffset     = 0dB;
        antenna.typename = default("IsotropicAntenna");   // or AxiallySymmetricAntenna
        // OR use a threshold instead of an error model:
        //   receiver.typename = default("ApskScalarReceiver");
        //   receiver.snirThreshold = 6dB;
}
```

**Receiver noise figure in INET:** the packet-level radio model does **not** model a noise
figure. `IsotropicScalarBackgroundNoise.power` is the *total* noise, so you must fold $F$ in
yourself: `power = -174dBm + 10*log10(B) + F`. This is the single most common setup error in
UAV-IoT simulations: forgetting the $+7$ dB inflates the coverage radius by a factor
$10^{7/(10\alpha)} = 1.514\times$ in distance for the UMa NLOS exponent $\alpha = 3.908$.

---

## 5. Aerial-to-ground and aerial-to-aerial specifics

### 5.1 Why the LOS/NLOS state is everything for UAV

A UAV at height $h$ above street level sees ground users over building roofs until the elevation
angle $\theta$ drops below the local "roof horizon" angle. A ground user at horizontal distance
$r$ has elevation $\theta = \arctan(h/r)$. Empirically ([AlH14], [AlH20]) the LOS/NLOS transition
sits around $\theta_0 \approx \pi/3 = 60^\circ$ for suburban environments and lower for dense
urban.

Consequences:

1. **At low altitude** ($\theta$ large) most users are LOS: $\sigma_{SF}=4$ dB, PLE 2.2,
   $K = 9\pm3.5$ dB Rician.
2. **At high altitude** ($\theta$ small, users far away) most users are NLOS: $\sigma_{SF}=6$ dB,
   PLE 3.908, Rayleigh.
3. The two branches differ by **20–40 dB at 1 km** — this is the dominant lever in any
   altitude/position RL reward.

**TR 38.901 UMa LoS probability evaluated for a UAV-as-BS** (using (1.9c) with $h_{UT}=1.5$ m,
so $C'=0$):

$$
\Pr_{LOS}^{\rm UMa}(r)=\left[\frac{18}{r}+\exp\!\left(-\frac{r}{63}\right)\right]\!\left(1-\frac{18}{r}\right)
$$

| $r$ (m) | 18 | 50 | 100 | 200 | 500 | 1000 |
|---|---|---|---|---|---|---|
| $\Pr_{LOS}^{\rm UMa}$ | 1.000 | 0.612 | 0.196 | 0.041 | 0.0034 | 0.0006 |

This is the correct statement of the problem: **the terrestrial UMa LoS-probability function is
calibrated for a 25 m BS and predicts essentially zero LoS beyond ~500 m for a ground UE.** It
does *not* rise with UAV altitude, because the $h_{UT}$ term that produces the second LoS branch
for tall UTs is zero for a sensor on the ground. To get altitude-dependent LoS behaviour you must
either raise $h_{UT}$ (wrong role) or supply your own $P_{LOS}(\theta,h)$.

### 5.2 Al-Hourani A2G path loss

[AlH14] models the air-to-ground path loss as a free-space term plus a geometry correction plus a
state-dependent excess loss:

$$
PL_{\rm LoS}(d,h) = PL_{\rm FS}(d) + 20\log_{10}\!\left(\frac{\sqrt{d^{2}+h^{2}}}{d}\right) + \eta_{\rm LoS},
\qquad \eta_{\rm LoS} = 1\ \mathrm{dB}
\tag{5.2a}
$$

$$
PL_{\rm NLoS}(d,h) = PL_{\rm FS}(d) + 20\log_{10}\!\left(\frac{\sqrt{d^{2}+h^{2}}}{d}\right) + \eta_{\rm NLoS},
\qquad \eta_{\rm NLoS} = 20\ \mathrm{dB}
\tag{5.2b}
$$

$$
PL_{\rm avg}(d,h) = P_{\rm LoS}(\theta)\,PL_{\rm LoS}(d,h) + \big(1-P_{\rm LoS}(\theta)\big)\,PL_{\rm NLoS}(d,h)
\tag{5.2c}
$$

with $d = d_{2D}$ (horizontal), $h$ = UAV altitude, $PL_{\rm FS}(d)$ from (3.1b) **evaluated at the
horizontal distance**, and $\theta = \arctan(h/d)$.

**Numerical check at $h=100$ m, $f_c=2.4$ GHz, $20$ dB EIRP, $2$ dBi receive gain:**

| $d_{2D}$ (m) | $\theta$ | geometry term (dB) | $PL_{\rm LoS}$ (dB) | $PL_{\rm NLoS}$ (dB) | $P_r$ NLoS (dBm) |
|---|---|---|---|---|---|
| 100 | 45.00° | 3.010 | 84.06 | 103.06 | $-81.06$ |
| 200 | 26.57° | 0.969 | 88.04 | 107.04 | $-85.04$ |
| 500 | 11.31° | 0.170 | 95.20 | 114.20 | $-92.20$ |
| 1000 | 5.71° | 0.043 | 101.10 | 120.10 | $-98.10$ |
| 2000 | 2.86° | 0.011 | 107.08 | 126.08 | $-104.08$ |
| 3000 | 1.91° | 0.005 | 110.60 | 129.60 | $-107.60$ |

The geometry term is $20\log_{10}(\sqrt{d^2+h^2}/d) \to 0$ as $d \gg h$: at 100 m altitude it
costs 3 dB at 100 m range and is negligible beyond 500 m.

> **Big caveat for a report.** (5.2b) with $\eta_{\rm NLoS}=20$ dB is effectively a $20\times$
> free-space law, i.e. an *effective* PLE of 2.0 with a huge constant offset. Its coverage radius
> for a 100 kbit/s / 10 kHz link comes out **> 20 km** (the model is still monotone increasing at
> 20 km: $PL_{\rm NLoS}=146.07$ dB). [38.901] UMa NLOS for the same link budget gives
> $d_{2D,\max}=1179$ m. **The two models differ by an order of magnitude in coverage radius.**
> If your RL agent exploits the [AlH14] NLOS branch, you will report coverage areas that no
> measurement supports.

**A composite form widely used in the UAV-BS literature** (same structure as (5.2c) but with the
*slant* range in $PL_{\rm FS}$ and $\xi$ in dB):

$$
PL_k = P_{\rm LoS}\left(\xi_{\rm LoS} + PL_{{\rm FS},k}\right) + \left(1-P_{\rm LoS}\right)\left(\xi_{\rm NLoS} + PL_{{\rm FS},k}\right),
\quad \xi_{\rm LoS}=1\ \mathrm{dB},\ \xi_{\rm NLoS}=20\ \mathrm{dB}
\tag{5.2d}
$$

### 5.3 Al-Hourani LoS probability

[AlH20] gives a two-branch logistic fit in the elevation angle:

$$
P_{\rm LoS}(\theta) \;=\; \frac{a}{1 + b\,\exp\!\left(-c\,(\theta-a)\right)}
\tag{5.3a}
$$

with

$$
\theta_0 = \arctan\!\left(\frac{a_1}{b_1}\right),\qquad
a = a_1 - b_1\sin\theta_0,\qquad
b = \frac{(a_2-a_1)\,\sin\theta_0}{1.25-\sin\theta_0},\qquad
c = \frac{(b_2-b_1)\,\cos\theta_0}{1.25-\sin\theta_0}
\tag{5.3b}
$$

and per-environment $(a_1,b_1,a_2,b_2)$. **Reproduce (5.3b) from the primary source before use.**
Two practical warnings: (i) many secondary sources tabulate $b_1=b_2$, which makes $c=0$ and
collapses $P_{\rm LoS}$ to a constant; (ii) the widely-quoted "urban $a=9.61$, $b=0.16$" pair is
$(a_1,b_1)$, **not** $(a,b)$. Do not mix them. Because of this ambiguity, in a simulator it is
usually better to implement the elevation-angle LoS probability *directly* as

$$
P_{\rm LoS}(\theta) = \begin{cases} 1, & \theta \ge \theta_0 \\ \frac{1}{1+\big(b/\tan\theta_0\big)^2}, & \theta < \theta_0\end{cases}
$$

([AlH20] form 2) and calibrate $\theta_0$ and $b$ from your own city layout.

### 5.4 Coverage radius as a function of altitude and antenna pattern

**Isotropic / wide-beam.** For the [38.901] UMa NLOS branch (1.3e), the only altitude dependence
is via $d_{3D}=\sqrt{d_{2D}^2+(h-h_{UT})^2}$:

$$
d_{3D,\max} = 10^{\frac{PL_{\max}-13.54-20\log_{10}(f_c)+0.6(h_{UT}-1.5)}{39.08}},
\qquad
d_{2D,\max}(h) = \sqrt{d_{3D,\max}^{2}-(h-h_{UT})^{2}}
\tag{5.4a}
$$

Numerically, for $PL_{\max}=141.24$ dB ($B=10$ kHz, $R=100$ kbit/s, $\mathrm{EIRP}=20$ dBm,
$G_r=2$ dBi, $F=7$ dB, $f_c=2.4$ GHz, $h_{UT}=1.5$ m): $d_{3D,\max}=1183.5$ m and

| $h$ (m) | 30 | 50 | 100 | 150 | 200 | 300 |
|---|---|---|---|---|---|---|
| $d_{2D,\max}$ NLOS (m) | 1183.2 | 1182.5 | 1179.4 | 1174.1 | 1166.7 | 1145.2 |

**Pure NLOS gives no interior optimal altitude** — the coverage radius is monotonically decreasing
in $h$ (and collapses to zero as $h\to d_{3D,\max}\approx1183$ m). The optimum comes *only* from
the LoS-probability term. Combining (1.9c) with both branches and solving
$P_{\rm LoS}\,PL_{\rm LoS}+(1-P_{\rm LoS})\,PL_{\rm NLoS}=PL_{\max}$:

| $h$ (m) | 30 | 50 | 100 | 150 | 200 | 300 | 600 |
|---|---|---|---|---|---|---|---|
| composite $d_{2D,\max}$ (m) | 1222.5 | 1221.9 | 1219.0 | 1214.1 | 1207.1 | 1187.1 | 1072.7 |

i.e. also monotone, because with $h_{UT}=1.5$ m the [38.901] LoS probability is essentially zero at
the cell edge ($\Pr_{LOS}\approx0.0145$ there) and the NLOS term dominates. **This is the correct,
mathematically honest conclusion: with the [38.901] UMa model, higher is worse.** The
"optimal LAP altitude" result of [AlH14] only emerges when you plug in an altitude-dependent
$P_{\rm LoS}(\theta)$ — precisely the extra physics [38.901] does not provide.

**Directional antenna footprint.** A nadir-pointing antenna of azimuth 3 dB beamwidth $\alpha$
illuminates a ground disc of radius

$$
r_{fp} = h_{\rm eff}\,\tan\!\left(\frac{\alpha}{2}\right), \qquad h_{\rm eff} = h - h_{UT}
\tag{5.4b}
$$

| $\alpha$ | $r_{fp}/h$ | $r_{fp}$ @ 100 m | $r_{fp}$ @ 150 m |
|---|---|---|---|
| 30° | 0.2679 | 26.8 m | 40.2 m |
| **65°** (3GPP UMa) | **0.6371** | **63.7 m** | **95.6 m** |
| 90° | 1.0000 | 100.0 m | 150.0 m |
| 120° | 1.7321 | 173.2 m | 259.8 m |

The **coverage trade-off is then explicit**: the array factor limits the footprint to $r_{fp}$ no
matter how much power, while the path loss limits the propagation radius:

$$
r_{cov} = \min\!\left(r_{fp},\; r_{prop}\right),\qquad
r_{prop} \text{ from (5.4a) with the extra antenna-pattern penalty } +(-G(\theta(r)))
\tag{5.4c}
$$

where $G(\theta)$ comes from the `AxiallySymmetricAntenna` gain string. With a 65° beam at
$h=100$ m the footprint edge is $r_{fp}=63.7$ m, i.e. an off-nadir angle of $57.5^\circ$ —
comfortably inside the main lobe — giving a **63.7 m radius of genuinely good coverage**, plus a
long degraded ($-12$ to $-30$ dB) tail out to the propagation radius. **For a persistent-coverage
RL problem the antenna footprint, not the path-loss ceiling, is the binding constraint over most
of the useful range — and neither `UnitDiskRadio` nor the default isotropic INET antenna captures
that.** Use `AxiallySymmetricAntenna`.

### 5.5 Aerial-to-aerial

* **Free space, always.** There is no terrain; (3.1b) applies with $d=d_{3D}$.
* **Rician $K$ is high.** [38.901] does not cover A2A. Measured air-to-air $K$ values are typically
  10–20 dB; at 2.4 GHz with air-to-air LoS, $K=15$ dB with $\sigma_{SF}=2$ dB is a defensible
  starting point (cite your measurement).
* **Doppler is the dominant dynamic effect.** Two counter-rotating UAVs at 10 m/s each have a
  relative speed of 20 m/s: $f_{D,\max}=160$ Hz at 2.4 GHz, $T_c\approx1.12$ ms.
* **Multipath delay.** Air-to-air delay spreads are small (tens of ns), so a narrowband model is
  adequate. Set `numFadingPaths` in Simu5G to 3–6 and `delayRms` to 30–100 ns for A2A.
* **Three-ray (ground-bounce) model.** If you want a specular ground bounce, add a second
  propagation path with relative attenuation
  $4\sin^2\!\left(\frac{2\pi h_t h_r}{\lambda d}\right)$ and relative delay $\frac{2h_t h_r}{c}$.

### 5.6 Multihop relay and connectivity graph

Define the per-link success probability from §3 + §5.2/§5.4:

$$
p_{ij} \;=\; \Pr\!\left[\mathrm{SINR}_{ij} \ge \Gamma\right]
\;\simeq\; \mathcal N\!\left(\frac{P_{r,ij}-N_{\rm eff}-\gamma}{\sigma_{SF,ij}},\;1\right)
= \Phi\!\left(\frac{P_{r,ij}-N_{\rm eff}-\gamma}{\sigma_{SF,ij}}\right)
\tag{5.6a}
$$

with $P_{r,ij}=\mathrm{EIRP}_i+G_{r,j}(\theta_{ij})-PL_{ij}$ and $\theta_{ij}$ the elevation angle
between UAV $i$ and UAV $j$ (both airborne => $\theta_{ij}$ is the off-nadir angle of the antenna,
so **antenna pointing matters enormously for A2A**).

A standard surrogate for multi-hop connectivity is a correlated-outage / stochastic-geometry form:

$$
\Pr\!\left[\text{UAV }j \text{ not reachable from } i\right] = 1-p_{ij},
\qquad
\Pr[\text{network partitioned}] \approx \sum_{j} \prod_{k\in\mathcal{N}(j)}(1-p_{jk})^{\rho}
\tag{5.6b}
$$

or, for the classic relay model, the probability that the sink is unreachable after $n$ hops.
**However** — and this matters for a rigorous report — (5.6b) is a *model*, not a measurement, and
it rests on a homogeneous-Poisson assumption that breaks down badly for a small, deliberately
positioned UAV swarm (which is exactly what your RL agent produces). Since your simulator
evaluates every pair link-by-link anyway, **measure the empirical disconnection probability from
the simulation** rather than assuming (5.6b). Also note that INET's `ScalarRadioMedium` does not
route at the physical layer: multihop must come from the routing layer (`Ipv4Router` plus a
routing protocol), so the "relay" behaviour is a MAC/routing outcome, not a channel-model outcome.


---

## 6. Simu5G: what it models and what it does not

### 6.1 Channel-model family

[Simu5G] `src/simu5g/stack/phy/channelmodel/`:

```
ChannelModelBase            (abstract)
├── IdealChannelModel       no impairments; a configured PER only
└── StochasticChannelModel  the real one
    ├── Tr36873ChannelModel    pathLossType default "Tr36873"
    └── Tr38901ChannelModel    pathLossType default "Tr38901"   <-- default for gNodeB/NR UE
```

`pathLossType @enum("Tr36814","Tr36873","Tr38901")`, backed by `Tr36814PathLossModel.cc`,
`Tr36873PathLossModel.cc`, `Tr38901PathLossModel.cc`. From v1.7.0 the project notes: *"the 3GPP
propagation formulas audited, fixed and covered by unit tests"*.

`Tr38901PathLossModel.cc` implements exactly the formulas of §1.3/§1.4/§1.5 (verified in source):

```cpp
double pLoss_nlos = 13.54 + 39.08*log10(threeDimDistance) + 20*log10CarrierFrequencyGHz_ - 0.6*(hUe_-1.5);   // UMa
double pLoss_nlos = 35.3*log10(threeDimDistance) + 22.4 + 21.3*log10CarrierFrequencyGHz_ - 0.3*(hUe_-1.5);  // UMi
double pLoss_nlos = 161.04 - 7.1*log10(W) + 7.5*log10(h) ... ;                                               // RMa
```

and `getShadowingStdDev()` returns 4/6 (UMa), 4/7.82 (UMi), 3/8.03 (InH), 4/6/8 (RMa) by LOS
state and breakpoint. It also implements the O2I low/high-loss models of (1.8c).

### 6.2 `StochasticChannelModel` — the complete parameter set

Verbatim from `StochasticChannelModel.ned`:

```ned
string pathLossType @enum("Tr36814","Tr36873","Tr38901") = default("Tr36814");
bool   shadowing = default(true);
string scenario  @enum(INDOOR_HOTSPOT,URBAN_MICROCELL,URBAN_MACROCELL,RURAL_MACROCELL,SUBURBAN_MACROCELL,UNKNOWN_SCENARIO) = default("URBAN_MACROCELL");
double nodebHeight    @unit(m) = default(25m);
double buildingHeight @unit(m) = default(20m);
bool   insideBuilding = default(false);
bool   useBuildingPenetrationHighLossModel = default(false);
double streetWidth @unit(m) = default(20m);
double ueHeight    @unit(m) = default(1.5m);
bool   tolerateMaxDistViolation = default(false);
bool   useTorus = default(false);
double correlationDistance @unit(m) = default(50m);
double targetBler   = default(0.01);
double harqReduction = default(0.2);
double antennaGainUe @unit(dBi) = default(0dBi);
double antennGainEnB @unit(dBi) = default(18dBi);
double antennGainMicro @unit(dBi) = default(5dBi);
double thermalNoise  @unit(dBm) = default(-104.5dBm);   // "for 10 MHz of Bandwidth"
double ueNoiseFigure @unit(dBm) = default(7dBm);
double bsNoiseFigure @unit(dBm) = default(5dBm);
double cableLoss     @unit(dB)  = default(2dB);
bool   dynamicLos = default(false);
bool   fixedLos    = default(false);
bool   fading = default(true);
string fadingType @enum(RAYLEIGH,JAKES) = default("JAKES");
int    numFadingPaths = default(6);
double delayRms @unit(s) = default(363ns);
bool   bgCellInterference  = default(true);
bool   extCellInterference = default(true);
bool   downlinkInterference = default(false);
bool   uplinkInterference   = default(false);
bool   enableExtCellLos = default(true);
bool   collectSinrStatistics = default(true);
```

Key defaults you should override for a UAV-IoT study:

| Parameter | Simu5G default | What you likely want | Why |
|---|---|---|---|
| `scenario` | `URBAN_MACROCELL` | keep, or `SUBURBAN_MACROCELL` | suburban LoS persists further |
| `nodebHeight` | 25 m | **your UAV altitude** | see §1.12 — out of the [38.901] range, but Simu5G lets you set it |
| `ueHeight` | 1.5 m | 1.5 m | fine |
| `correlationDistance` | 50 m | **25 m** for exact [38.901] UMa-NLOS ($r_{SF}/2$, eq. 4.8b) | [38.901] $r_{SF}$(UMa NLOS) = 50 m |
| `thermalNoise` | $-104.5$ dBm | $-173.98 + 10\log_{10}(B) + F$ for your $B$ | Simu5G does not compute $kTB$ |
| `delayRms` | 363 ns (UMa LOS median) | 240 ns NLOS / 226 ns LOS | scenario-dependent |
| `fadingType` | `JAKES` | keep | |
| `numFadingPaths` | 6 | 3–6 | 6 taps $\approx$ 363 ns RMS spread |
| `downlinkInterference` / `uplinkInterference` | **false** | **true** | otherwise there is no inter-cell interference at all |
| `targetBler` | 0.01 | keep | Simu5G CQI computation targets 1 % BLER |
| `harqReduction` | 0.2 | keep | per-HARQ-transmission SNR offset |

### 6.3 What Simu5G models

* **Numerology** 0–4 (`ComponentCarrier.cc` throws if `numerologyIndex > 4`), FDD/TDD, TDD symbol
  split, carrier aggregation.
* **MCS/CQI/iTBS tables** exactly as in §3.7 ([Simu5G] `NrMcs.cc`; CQI from TS 38.214 Table
  7.2.3-1, MCS from Tables 5.1.3.1-1/-2, TBS from Table 5.1.3.2-1).
* **BLER-vs-SINR curves** in `src/simu5g/common/blerCurves/`:
  `BLERvsSINR_15CQI_TU.h` (TU, from TR 36.842) and `BLERvsSINR_15CQI_AWGN.h`, indexed by
  `(itxmode, cqi, snr)` via `binder_->phyPisaData.getBler(itxmode, cqi, snr)`.
* **Path loss / LoS probability / shadowing** per TR 36.814, 36.873 or 38.901 (§6.1).
* **Multipath fading**: Jakes (sum of sinusoids, per-band, per-TTI) or Rayleigh — (4.8a).
* **Interference**: DL intra/inter-cell, UL, external cells, background cells (large-scale).
* **Antenna pattern attenuation** per the 3GPP sector pattern, plus the full link budget (antenna
  gains, cable loss, noise figures, thermal noise).
* **HARQ** (up to 4 process IDs by default), CQI reporting with target BLER, schedulers
  (Max C/I, Proportional Fair, Deficit Round Robin, QoS-aware variants), random access, BSR,
  handover, RLF/RRC re-establishment, RLC TM/UM/AM per TS 38.322, PDCP, SDAP, QoS flows
  (QCI/5QI), 5GC, EN-DC/NE-DC split bearers, MEC, and D2D (optional package).

### 6.4 What Simu5G does **NOT** model

This list is essential for an honest report.

1. **No aerial/UAV channel model.** No A2G LoS probability, no altitude-dependent path loss, no
   elevation-angle antenna pointing. `nodebHeight` is just a scalar fed to the terrestrial
   formulas, and there is no check that it lies inside [38.901]'s validity envelope.
2. **No spatial consistency** in the sense of [38.901] §7.6.3. Shadowing is correlated in *time*
   via (4.8b) only; there are no LSP/SSP correlation distances, no cluster model, no 38.901 GSCM.
3. **No tap-delay-line / frequency-selective channel.** `delayRms` only sets the phase offsets in
   (4.8a); it is not used for any convolution, and there is one SINR per PRB, not per subcarrier.
   **No OFDM, no CP, no ICI, no MIMO** — the Simu5G v1.4.5 notes explicitly say the incomplete
   MIMO code was *removed*.
4. **No per-symbol processing.** All decoding is at BLER-curve granularity per TTI.
5. **No thermal-noise computation.** `thermalNoise` is a constant.
6. **No RRC signalling** (only bearer management, handover, RLF and re-establishment are modelled).
7. **No MAC detail beyond what is implemented**: no PHY preamble-detection model beyond
   "collisions", no explicit propagation of TX-power-control commands beyond the configured rules,
   no PHY ARQ other than HARQ.
8. **No UAV energy model**, no propulsion power, no flight dynamics coupled to the radio.
9. **No multi-UAV coordination.** Handover, scheduling and power control assume terrestrial
   topology; there is no inter-UAV beam coordination and no distributed interference management.
10. **No mmWave beam management or dynamic blockage** (no human blockage, no LoS/NLOS transitions
    over time), even though 38.901 covers them.

---

## 7. Latency, PDR and throughput metrics (ITU-T definitions)

### 7.1 Fundamental IP packet transfer performance parameters [Y.1540]

For IP packet $T$ in a packet flow from source to destination:

**One-way delay (IP packet transfer delay), [Y.1540] §5.1 / RFC 7679 §3.4:**

$$
t_T \;=\; t_2 - t_1
\tag{7.1a}
$$

where $t_1$ is the wire time at which the *first bit* of $T$ crosses the source network reference
point and $t_2$ the wire time at which the *last bit* of $T$ crosses the destination reference
point. It is **undefined (informally infinite)** if $T$ is not received within the loss-threshold
waiting time $T_{max}$.

**Packet delay variation (IPDV), 2-point, [Y.1540] / RFC 2680 §4.1:**

$$
\mathrm{IPDV}(T_1,T_2) \;=\; \left|\, t_{T_1} - t_{T_2} \,\right|,\quad T_1<T_2
\tag{7.1b}
$$

**Absolute packet delay variation (APDV) / inter-packet delay variation:**

$$
\mathrm{APDV}(T) \;=\; \left|\, t_T - t_{T-1} \,\right|
\tag{7.1c}
$$

**Jitter** is *not* a [Y.1540] metric; the term is overloaded. Use either APDV (7.1c), the **local
delay variation** $\mathrm{LDV}(T)=t_T-t_{T-1}$ signed, or the [RFC 3550] inter-arrival jitter

$$
J = \left|\,\left(t_{T_i}-t_{T_{i-1}}\right) - \left(\tau_{T_i}-\tau_{T_{i-1}}\right)\,\right|
\tag{7.1d}
$$

where $\tau$ is the timestamp *at the sender*. **State explicitly in your report which one you
use.** For packetised sensor data, APDV (7.1c) is the most defensible and is what "jitter" usually
means in IoT QoS contexts.

### 7.2 Aggregated parameters

$$
\mathrm{IPLR} \;=\; \frac{\text{number of packets lost}}{\text{total number of packets sent}},
\qquad
\mathrm{PDR} \;=\; 1-\mathrm{IPLR}
\tag{7.2a}
$$

$$
\mathrm{OWD}_{\rm mean} = \frac{1}{N}\sum_{T\in\mathcal{S}} t_T ,
\qquad
\mathrm{OWD}_{p} = \inf\big\{x : F(x)\ge p\big\}
\tag{7.2b}
$$

$$
\mathrm{ITR} \;\approx\; \frac{L}{p_1 - p_2}
\tag{7.2c}
$$

([Y.1540] §5.3: the information transfer rate for a file of $L$ octets and loss ratio $p$ is
$L/(1-p)$; with an $\mathrm{IPLR}=p_1$ and an $\mathrm{IPER}=p_2$ the usable rate is
$L/(p_1-p_2)$.) Throughput over a simulation window:

$$
\Throughput = \frac{8\cdot\sum_{k} L_k}{T_{\rm sim}\ \mathrm{[s]}}
\tag{7.2d}
$$

For a UAV-IoT report the clean metric set is:

| metric | definition | units |
|---|---|---|
| Coverage ratio | fraction of target sensors whose SINR to their serving UAV exceeded $\Gamma$ during the window | dimensionless |
| PDR | (7.2a), per sensor and network-wide | dimensionless |
| Mean / $p_{95}$ / $p_{99}$ OWD | (7.2b) on successfully delivered packets only | ms |
| APDV / $p_{95}$ APDV | (7.1c) | ms |
| Goodput | (7.2d) counting only delivered payload bytes | bit/s |
| Connectivity time | fraction of time each sensor has $\ge 1$ UAV with SINR $\ge \Gamma$ | dimensionless |
| Handover count / inter-UAV handover latency | simulator-native | — |


?[Y.1541] Table 3, provisional classes 6 and 7 (evaluation interval $\ge 1$ min, 1500-byte payloads):

| Parameter | Class 6 | Class 7 |
|---|---|---|
| IPTD (one-way delay) | 100 ms | 400 ms |
| IPDV ($1-10^{-5}$ quantile of IPTD minus the minimum IPTD) | 50 ms | 50 ms |
| IPLR (packet loss ratio) | $1\times10^{-5}$ | $1\times10^{-5}$ |
| IPER (error ratio) | $1\times10^{-6}$ | $1\times10^{-6}$ |
| IPRR (reserved-bit ratio) | $1\times10^{-6}$ | $1\times10^{-6}$ |

**Mapping UAV-IoT onto these classes.** A persistent-coverage UAV-IoT network delivering small
sensor reports every $\Delta$ seconds is best benchmarked against **Y.1541 Class 0 / Class 2**
($\mathrm{OWD}\le 100$ ms, $\mathrm{IPLR}\le 10^{-3}$). Two points that belong in your report:

* The propagation delay from a 100 m UAV is **negligible** ($100/3\times10^{8}=0.33\ \mu$s), but
  the LoS/NLOS state changes the usable radius by a factor of $\approx 5.5$ (§8.11), and a UAV
  moving at 10 m/s changes which UAV serves a sensor every few seconds.
* Y.1541's 1-minute evaluation interval and $10^{-3}$ loss budget are weak constraints for a
  *persistent* coverage problem. Report **per-sensor outage distribution** and **inter-UAV handover
  latency**, not only network-average PDR. Class 0's 50 ms IPDV objective maps directly onto
  "how much does packet delay jitter while the serving UAV changes?"

---

## 8. Worked numerical example — every arithmetic step

### 8.1 Scenario

| Item | Value |
|---|---|
| Aerial BS (UAV) altitude | $h_{BS} = 100$ m |
| Ground sensor antenna height | $h_{UT} = 1.5$ m |
| Carrier frequency | $f_c = 2.4$ GHz |
| UAV EIRP (isotropic downlink antenna) | $20$ dBm |
| Sensor antenna gain | $2$ dBi |
| Sensor noise figure | $7$ dB |
| Cable/feeder + body losses | $0$ dB (both ends) |
| Channel bandwidth | $B = 200$ kHz |
| Scenario | 3GPP TR 38.901 **UMa**, NLOS branch |
| Shadowing | $\sigma_{SF} = 6$ dB (UMa NLOS) |

> **Validity warning, restated.** $h_{BS}=100$ m is **outside** the [38.901] UMa envelope
> ($h_{BS}=25$ m nominal). Every number below is the [38.901] formula *evaluated* at
> $h_{BS}=100$ m, i.e. an extrapolation. §10 discusses what to do instead.

### 8.2 Step 1 — geometry

With $h_{BS}=100$ m and $h_{UT}=1.5$ m:

$$
h_{BS}-h_{UT} = 98.5\ \mathrm{m}, \qquad \Delta h^{2} = 9702.25\ \mathrm{m^{2}}
$$

$$
d_{3D} = \sqrt{d_{2D}^{2} + 9702.25}\ \mathrm{m}
$$

For the reference case $d_{2D}=500$ m:

$$
d_{3D} = \sqrt{500^{2}+9702.25} = \sqrt{259\,702.25} = 509.6099\ \mathrm{m}
$$

### 8.3 Step 2 — breakpoint (needed for the LOS branch)

$h_{UT}=1.5$ m $< 13$ m $\Rightarrow C(d_{2D},h_{UT})=0 \Rightarrow h_E = 1$ m is drawn with
probability $1/(1+0)=1$, i.e. deterministically. Hence

$$
h'_{BS}=100-1=99\ \mathrm{m}, \qquad h'_{UT}=1.5-1=0.5\ \mathrm{m}
$$

$$
d'_{\rm BP}=\frac{4\,h'_{BS}h'_{UT}f_c}{c}
=\frac{4\cdot 99\cdot 0.5\cdot 2.4\times10^{9}}{2.99792458\times10^{8}}
=\frac{4.752\times10^{11}}{2.99792458\times10^{8}}
=1585.0966\ \mathrm{m}
$$

Sanity checks: $h'_{BS}h'_{UT}=49.5\ \mathrm{m^{2}}$; $4f_c/c = 32.022153\ \mathrm{m^{-1}}$;
product $=1585.0966$ m. ✔

Also, for later use:

$$
9\log_{10}\!\left((d'_{\rm BP})^{2}+\Delta h^{2}\right)
=9\log_{10}\!\left(2\,512\,529.6+9702.25\right)
=9\log_{10}(2\,522\,233.4)=9\times 6.401790=57.6161\ \mathrm{dB}
$$


### 8.4 Step 3 — path loss, UMa LOS branch (for contrast)

$d_{2D}=500$ m $\le d'_{\rm BP}=1585.10$ m, so use $PL_1$ of (1.3b):

$$
PL_1 = 28.0 + 22\log_{10}(509.6099) + 20\log_{10}(2.4)
$$

$$
\log_{10}(509.6099) = 2.707121 \quad\Rightarrow\quad 22\times 2.707121 = 59.55666\ \mathrm{dB}
$$

$$
20\log_{10}(2.4) = 20\times 0.380211 = 7.60422\ \mathrm{dB}
$$

$$
\boxed{PL_{\rm UMa\text{-}LOS} = 28.0 + 59.5567 + 7.6042 = 95.161\ \mathrm{dB}}
$$

Above the breakpoint the $PL_2$ branch (1.3c) applies; at $d_{2D}=1585$ m,
$d_{3D}=1588.06$ m, $\log_{10}(1588.06)=3.200973$:

$$
PL_2 = 28.0 + 40(3.200973) + 7.6042 - 57.6161 = 28.0+128.0389+7.6042-57.6161 = 106.027\ \mathrm{dB}
$$

### 8.5 Step 4 — path loss, UMa NLOS branch (the model we use)

From (1.3e):

$$
PL'_{\rm UMa\text{-}NLOS} = 13.54 + 39.08\log_{10}(509.6099) + 20\log_{10}(2.4) - 0.6\,(1.5-1.5)
$$

$$
39.08 \times 2.707121 = 105.79830\ \mathrm{dB}, \qquad -0.6\times 0 = 0
$$

$$
\boxed{PL'_{\rm UMa\text{-}NLOS} = 13.54 + 105.7983 + 7.6042 + 0 = 126.9425\ \mathrm{dB}}
$$

Apply the $\max$ of (1.3d):

$$
PL_{\rm UMa\text{-}NLOS}=\max(95.161,\;126.9425)=126.9425\ \mathrm{dB}
$$

The branches cross where $13.54 + 39.08\log_{10}(d_{3D}) = 28.0 + 22\log_{10}(d_{3D})$, i.e.
$17.08\log_{10}(d_{3D})=14.46 \Rightarrow d_{3D}=10^{0.84660}=7.03$ m. So for every
$d_{2D}\ge 10$ m the NLOS branch is selected — the height question changes the *value*, not the
*branch*.

### 8.6 Step 5 — noise power

$$
N_0 = kT = 1.380649\times10^{-23}\times 290 = 4.003882\times10^{-21}\ \mathrm{W/Hz}
$$

$$
N_0[\mathrm{dBm/Hz}] = 10\log_{10}\!\left(\frac{4.003882\times10^{-21}}{10^{-3}}\right)
=10\log_{10}(4.003882\times10^{-18}) = -173.9752\ \mathrm{dBm/Hz}
$$

$$
N_{\rm th} = N_0 + 10\log_{10}\!\left(\frac{B}{1\ \mathrm{Hz}}\right)
= -173.9752 + 10\log_{10}(200\,000)
= -173.9752 + 53.0103 = -120.9649\ \mathrm{dBm}
$$

$$
N_{\rm eff} = N_{\rm th} + F = -120.9649 + 7 = -113.9649\ \mathrm{dBm}
\quad\left(=10^{-11.39649}\ \mathrm{mW}=4.01339\times10^{-12}\ \mathrm{mW}\right)
$$

### 8.7 Step 6 — received power and SINR

$$
P_r = \mathrm{EIRP}+G_r-L_{\rm sys}-PL = 20 + 2 - 0 - 126.9425 = -104.9425\ \mathrm{dBm}
$$

$$
\mathrm{SINR}[\mathrm{dB}] = P_r - N_{\rm eff} = -104.9425 - (-113.9649) = +9.0224\ \mathrm{dB}
$$

$$
\mathrm{SINR}_{\rm linear} = 10^{0.90224} = 7.9873
$$

### 8.8 Step 7 — Shannon rate

$$
R = B\log_{2}\!\left(1+\mathrm{SINR}\right)
=200\,000\times\log_{2}(8.9873) = 200\,000\times 3.16736
$$

$$
\boxed{R = 633\,473\ \mathrm{bit/s}\;\approx\;0.633\ \mathrm{Mbit/s}}
$$

Spectral efficiency $\eta = R/B = 3.167$ bit/s/Hz — far beyond what any real radio achieves.
This is why Shannon is an upper bound and not a design number.

### 8.9 Step 7b — what a real radio gives at the same SINR

Using [38.214] MCS index 7 (QPSK, $R=526/1024$, $\eta = 2\times526/1024 = 1.0273$ bit/s/Hz):

$$
R_{\rm real} = B\times\eta = 200\,000\times 1.0273 = 205\,469\ \mathrm{bit/s} \approx 0.205\ \mathrm{Mbit/s}
$$

64QAM (MCS 23, $\eta=4.213$) is **not** viable at $\mathrm{SINR}=9.02$ dB. From (3.6c)/(3.6e),
64QAM at BLER $<10^{-3}$ needs $E_b/N_0 \approx 18{-}21$ dB, i.e.
$\gamma = 18 - 10\log_{10}(4.213) = 18-6.244 = 11.76$ dB at best and $\approx15{-}18$ dB in
practice. **An RL agent that optimises position must be given the modulation schedule, not
Shannon capacity.**


### 8.10 Step 8 — path loss vs distance (same link, full table)

| $d_{2D}$ (m) | $d_{3D}$ (m) | $PL_{\rm LOS}$ (dB) | $PL'_{\rm NLOS}$ (dB) | $PL$ used (dB) | $P_r$ (dBm) | SINR (dB) | $R$ Shannon (Mbit/s) |
|---|---|---|---|---|---|---|---|
| 200 | 222.940 | 87.26 | 112.91 | 112.91 | $-90.91$ | 23.05 | 1.5331 |
| 500 | 509.610 | 95.16 | 126.94 | 126.94 | $-104.94$ | 9.02 | 0.6334 |
| 1000 | 1004.839 | 101.65 | 138.47 | 138.47 | $-116.47$ | $-2.50$ | 0.1287 |
| 1585 | 1588.058 | 106.03 | 146.23 | 146.23 | $-124.23$ | $-10.27$ | 0.0259 |
| 2000 | 2002.424 | 110.05 | 150.17 | 150.17 | $-128.17$ | $-14.20$ | 0.0108 |
| 3000 | 3001.617 | 117.08 | 157.04 | 157.04 | $-135.04$ | $-21.07$ | 0.0022 |
| 5000 | 5000.970 | 125.95 | 165.70 | 165.70 | $-143.70$ | $-29.74$ | 0.0003 |

The LOS/NLOS gap is 17.7 dB at 200 m and 39.7 dB at 5 km, and it **grows** with distance because
the NLOS slope (39.08) exceeds the LOS slope (22). Altitude therefore buys you *branch switching*,
not a slope change.

### 8.11 Step 9 — required distance for a target rate

**Required SINR** for target rate $R$ in bandwidth $B$:

$$
\gamma_{\rm req}=10\log_{10}\!\left(\frac{R}{B}\ln 2 - 1\right)
\tag{8.11a}
$$

derived from $R=B\log_2(1+\gamma)\Rightarrow\gamma=2^{R/B}-1$. Note that $\gamma_{\rm req}$ is
undefined for $R<B\ln 2$: **you cannot hit 100 kbit/s in a 200 kHz channel at all**, because the
zero-SINR rate is exactly $B\log_2 2 = B$.

**Maximum tolerable path loss**, from $P_r=\mathrm{EIRP}+G_r-PL$ and
$\mathrm{SINR}=P_r-N_{\rm eff}\ge\gamma$:

$$
PL_{\max} = \mathrm{EIRP}+G_r-N_{\rm eff}-\gamma_{\rm req}
=20+2-(-113.9649)-\gamma_{\rm req}=135.9649-\gamma_{\rm req}
\tag{8.11b}
$$

**Invert the NLOS branch (1.3e):**

$$
d_{3D,\max}=10^{\frac{PL_{\max}-13.54-20\log_{10}(f_c)+0.6(h_{UT}-1.5)}{39.08}},
\qquad
d_{2D,\max}=\sqrt{d_{3D,\max}^{2}-(h_{BS}-h_{UT})^{2}}
\tag{8.11c}
$$

**NLOS results** (recomputed per row, since $N_{\rm eff}$ depends on $B$):

| $B$ | $R$ (bit/s) | $N_{\rm eff}$ (dBm) | $\gamma_{\rm req}$ (dB) | $PL_{\max}$ (dB) | $d_{3D,\max}$ (m) | $d_{2D,\max}$ (m) |
|---|---|---|---|---|---|---|
| 10 kHz | 100 000 | $-123.975$ | 7.7316 | 141.2436 | 1183.5 | **1179.4** |
| 10 kHz | 1 000 000 | $-123.975$ | 18.3505 | 130.6247 | 633.3 | 625.6 |
| 10 kHz | 10 000 000 | $-123.975$ | 28.4000 | 120.5649 | 350.1 | 336.0 |
| 10 kHz | 100 000 000 | $-123.975$ | 38.4108 | 110.5541 | 194.2 | 167.3 |
| 200 kHz | 1 000 000 | $-113.965$ | 3.9242 | 132.0407 | 688.3 | 681.3 |
| 200 kHz | 10 000 000 | $-113.965$ | 15.2713 | 120.6936 | 352.6 | 338.6 |
| 200 kHz | 100 000 000 | $-113.965$ | 25.3902 | 110.5747 | 194.3 | 167.5 |
| 1 MHz | 10 000 000 | $-106.975$ | 7.7316 | 128.2333 | 364.2 | 350.7 |

**LOS branch ($PL_2$, eq. 1.3c) for contrast** — inverting
$d_{3D}=10^{(\,PL_{\max}-28.0-20\log_{10}f_c+9\log_{10}C\,)/40}$ with
$C=(d'_{\rm BP})^2+\Delta h^2 = 2\,522\,233.4$:

| $B$ | $R$ (bit/s) | $PL_{\max}$ (dB) | $d_{3D,\max}$ (m) | $d_{2D,\max}$ (m) |
|---|---|---|---|---|
| 10 kHz | 100 000 | 141.2436 | 6547.1 | 6546.3 |
| 10 kHz | 1 000 000 | 130.6247 | 3694.0 | 3693.6 |
| 200 kHz | 1 000 000 | 132.0407 | 7102.8 | 7102.2 |
| 200 kHz | 10 000 000 | 120.6936 | 3695.3 | 3694.0 |

**Interpretation.** In LoS the same power budget buys a **5.5× larger radius** (6546 m vs 1179 m).
A UAV swarm therefore does not "extend coverage" in the NLOS sense — it *keeps its own users in
LoS*, which is far more valuable. An RL reward built on pure coverage area under an NLOS-only
assumption undervalues LoS maintenance by roughly 5× in radius, i.e. $\approx 30\times$ in area.

**Sensitivity to the two most-overlooked terms:**

* Forgetting the $7$ dB noise figure: $PL_{\max}$ rises by 7 dB, so
  $d_{3D,\max} \times 10^{7/39.08} = 1.514\times$ — a **51 % larger coverage radius from a pure
  bookkeeping omission.**
* EIRP error of $\pm3$ dB $\Rightarrow$ radius error $\pm 7.7\,\%$.

### 8.12 Step 10 — shadowing margin and outage

With $\sigma_{SF}=6$ dB, from (2.1d):

$$
M_{\rm SF}(p)=6\,\Phi^{-1}\!\left(1-\frac{p}{2}\right)\ \mathrm{dB}
$$

| $p$ | 0.20 | 0.10 | 0.05 | 0.01 |
|---|---|---|---|---|
| $M_{\rm SF}$ (dB) | 7.689 | 9.869 | 11.760 | 15.455 |

To keep $P_{\rm out}\le 1\,\%$ at $B=10$ kHz, $R=100$ kbit/s:
$PL_{\max}=141.2436-15.455=125.789$ dB, so

$$
d_{3D,\max}=10^{\frac{125.789-13.54-7.6042}{39.08}}=724.3\ \mathrm{m},
\qquad
d_{2D,\max}=\sqrt{724.3^{2}-9702.25}=717.6\ \mathrm{m}
$$

**A 1 % outage target cuts the NLOS coverage radius by 39 %** (1179 m → 718 m). Shadowing is the
second-largest lever after the path-loss exponent. If it is modelled as i.i.d. per packet (which is
what plain `LogNormalShadowing` does), the *marginal* outage probability is right but the
*temporal* structure is wrong: real shadowing produces correlated outage bursts, which is exactly
what an RL policy needs to learn to avoid.


### 8.13 Step 11 — cross-check against [AlH14] and against Simu5G

**[AlH14] A2G NLoS (5.2b)** at the same geometry, with
$PL_{\rm FS}(d)=32.4478+20\log_{10}f_c+20\log_{10}d$ evaluated at the **horizontal** distance and
$\eta_{\rm NLoS}=20$ dB:

| $d_{2D}$ (m) | $PL_{\rm LoS}$ (dB) | $PL_{\rm NLoS}$ (dB) | [38.901] UMa NLOS (dB) | difference |
|---|---|---|---|---|
| 100 | 84.06 | 103.06 | 105.06 | $-2.0$ dB |
| 200 | 88.04 | 107.04 | 112.91 | $-5.9$ dB |
| 500 | 95.20 | 114.20 | 126.94 | $-12.7$ dB |
| 1000 | 101.10 | 120.10 | 138.47 | $-18.4$ dB |
| 2000 | 107.08 | 126.08 | 150.17 | $-24.1$ dB |
| 3000 | 110.60 | 129.60 | 157.04 | $-27.4$ dB |

**The discrepancy grows without bound** because [AlH14] NLoS is essentially free space
(PLE 2.0) plus a 20 dB constant, whereas [38.901] UMa NLOS is PLE 3.908. Converting [AlH14] NLoS
into a coverage radius for the §8.11 link budget ($PL_{\max}=141.24$ dB) gives $d_{2D}>20$ km —
**more than an order of magnitude more coverage than [38.901]**, and still growing at the edge of
any realistic scenario. Never mix the two in the same study without a stated cross-calibration.

**Simu5G.** With its defaults (`antennGainEnB = 18` dBi, `cableLoss = 2` dB,
`bsNoiseFigure = 5` dB, `thermalNoise = -104.5` dBm):

```
EIRP        = TxPower - cableLoss + antennaGainEnB = TxPower + 16 dB
N_dBm       = thermalNoise + noiseFigure          = -104.5 + 5 = -99.5 dBm
```

At $d_{2D}=500$ m, $PL=126.9425$ dB and $\mathrm{TxPower}=0$ dBm:
$P_r = 16-126.9425 = -110.9425$ dBm, $\mathrm{SINR}=-110.9425-(-99.5)=-11.44$ dB — unusable.
To match §8.7 exactly in Simu5G you must set

```
TxPower  = 0 dBm
antennGainEnB  = 2 dBi            // so that EIRP = 20 dBm with cableLoss = 2 dB
bsNoiseFigure  = 7 dB
thermalNoise   = -120.965 dBm     // = -173.975 + 10*log10(200e3), NF folded into thermalNoise or kept separate
```

Simu5G additionally applies its 3GPP sector antenna pattern; with an azimuth beamwidth of 65° and
maximum gain set to `antennGainEnB`, a UAV at 500 m range sees an off-nadir angle of
$\theta = \arctan(98.5/500)=11.15°$, i.e. inside the main lobe, so the full gain applies.

### 8.14 Step 12 — the same link in a `UnitDiskRadio` run

If instead you use `UnitDiskRadio` with `UnitDiskTransmitter`, the only physics is

$$
\mathrm{receive} \iff d < \texttt{communicationRange}
\;\wedge\;\big(\text{no interfering tx within } \texttt{interferenceRange}\big)
\tag{8.14a}
$$

so the whole §8.2–8.13 analysis is replaced by a single number in the `.ned` file. You would set it
from (5.4a): $d_{2D,\max}=1179$ m for $B=10$ kHz/$R=100$ kbit/s, or $681$ m for
$B=200$ kHz/$R=1$ Mbit/s. **This is the correct value to use, and the reason §4.6 argues for the
scalar radio model is that this number is invisible when you write it into a NED file but has to be
*derived* with the analysis above.**

---

## 9. Corrections and caveats — a consolidated list

### 9.1 "UAV altitude above 22.5 m is not covered by TR 38.901" — what is actually true

**Restated precisely (see §1.12):**

1. $22.5$ m is the **upper bound on $h_{UT}$**, the *ground terminal* height, for UMa and UMi.
   It arises because $C(d_{2D},h_{UT})$ and $C'(h_{UT})$ are only calibrated to 23 m. A ground
   sensor at 1.5 m is well inside it.
2. The genuine exclusion is **$h_{BS}$**: UMa is calibrated at $h_{BS}=25$ m, UMi at 10 m. Setting
   $h_{BS}$ to a UAV altitude of 20–300 m is an **extrapolation**, and the LoS-probability
   derivation (Table 7.4.2-1 Note: *"antenna heights of ... 25 m for UMa"*) is invalidated.
3. You cannot avoid the extrapolation by labelling the UAV a "UT" — then $h_{UT}=100$ m violates
   $h_{UT}\le22.5$ m.
4. **[38.901] contains no aerial-communication scenario at all.** Its scope clause (V19.1.0 §4)
   lists only urban micro street canyon, urban macro, indoor office, rural macro, indoor factory and
   suburban macro. A full-text search of V19.1.0 finds "UAV" only in the ISAC **sensing-target**
   clause (7.9, radar cross-section) — never in a propagation model.
5. **The 3GPP non-terrestrial models do not cover 20–200 m either.** [38.811] and [38.821] target
   NTN platforms in the **8–50 km** band (the 3GPP portal describes UAS as *"operating typically
   between 8 and 50 km altitudes, including High Altitude Platforms"*), plus LEO/GEO satellites
   (600 km, 1 200 km, 35 786 km in the ns-3 calibration). Low-altitude UAV operation (200 m–1 km) is
   described as "below 1 km" / "a few hundred metres" in the NTN literature but has **no 3GPP path
   loss model calibrated for it**.
6. Rel-19 did add a **"UAV sensing scenario"** to the ISAC clause (7.9) with an aerial-UE height
   applicability range of $22.5\ \mathrm{m} < h \le 100$ m mapped onto UMi/UMa LOS probability — but
   this is for *radar sensing targets*, not for a UAV acting as a base station. Do not repurpose it.

**Therefore the statement "TR 38.901 does not cover UAV altitudes above 22.5 m" is *directionally
right but mechanistically wrong*.** The correct statement is: *TR 38.901's terrestrial path-loss
and LoS-probability models are calibrated for a terrestrial BS at 10–35 m and a terrestrial UT at
1.5–22.5 m, and contain no aerial-BS scenario at all.*

### 9.2 What to do instead — four defensible options

**(a) 3GPP extension: use TR 38.811/38.821 NTN models.**
Correct for HAPs (8–50 km) and LEO/GEO satellites. Scenarios: Dense Urban, Urban, Suburban, Rural;
path loss, shadow fading, clutter loss and fast fading all specified; atmospheric absorption and
tropospheric/ionospheric scintillation included. **Not calibrated for 20–300 m UAVs**, and its
flat-fading model requires $\theta\ge 20°$ elevation, quasi-LoS, S-band, $B\le5$ MHz.

**(b) Elevation-angle LoS probability + terrestrial slope (recommended for 20–300 m).**
Use the [38.901] **UMa LOS branch** (1.3b/1.3c) whenever LoS and the **UMa NLOS branch** (1.3e)
otherwise, but replace $\Pr_{LOS}^{\rm UMa}(1.9c)$ with an **altitude/elevation-dependent** LoS
probability $P_{LOS}(h,d_{2D})$ — e.g. (5.3a) from [AlH20], or a logistic fit calibrated against
your own building-height distribution. This is what almost every serious UAV-coverage paper does,
and it makes the UAV's altitude an explicit, controllable design variable.

**(c) Sub-band $\sigma_{SF}$ and slope correction.** Empirically, A2G measurements show the NLOS
slope *decreasing* with altitude (fewer obstructions at higher $h$): PLE values from $\approx4.2$
at 30 m down to $\approx2.8$–$3.2$ at 100–200 m in urban environments. Model

$$
PL_{\rm NLoS}(d_{3D},h)=\mathrm{FSPL}(d_{3D})+10\,n(h)\log_{10}\!\left(\frac{d_{3D}}{1\ \mathrm{m}}\right)+B(h),
$$

with $n(h)$ and $B(h)$ interpolated from your own measurements, or from published A2G fits.

**(d) Geometric / ray-tracing.** For a small deployment (tens of UAVs, hundreds of sensors) the most
defensible choice is a **deterministic 3-D urban model** with ray tracing (Raymobtime, Sionna RT,
QuaDRiGa) or, inside OMNeT++, INET's `TTracingObstacleLoss` / `DielectricObstacleLoss` over a
`TiledBuildingEnvironment`. You then export a *lookup* of $PL$ and shadowing onto a grid and feed it
to INET through a custom `IPathLoss`. This removes the scenario-selection problem entirely, at the
cost of no longer being "standard".

### 9.3 Ten modelling errors that will silently invalidate a UAV-IoT report

| # | Error | Consequence |
|---|---|---|
| 1 | Not folding the receiver noise figure into `IsotropicScalarBackgroundNoise.power` | 7 dB ⇒ **51 % overestimated coverage radius** (§8.11) |
| 2 | Using INET's `LogNormalShadowing` for shadowing | i.i.d. per packet ⇒ no outage bursts ⇒ PDR far too high, jitter far too low (§4.8) |
| 3 | Using Simu5G's `thermalNoise` default of $-104.5$ dBm with a bandwidth other than 10 MHz | wrong noise floor by $10\log_{10}(B/10\ \mathrm{MHz})$ dB |
| 4 | Using Simu5G's `correlationDistance` = 50 m as the [38.901] $d_{cor}$ | effective correlation is **100 m**, twice [38.901] (eq. 4.8b) |
| 5 | `downlinkInterference = false` (the Simu5G default) | no inter-cell interference at all |
| 6 | Leaving `UnitDiskRadio` as the main model | no path-loss law, no shadowing, no LoS/NLOS state |
| 7 | Isotropic antennas everywhere | ignores the 63.7 m footprint at 100 m / 65° beam (§5.4) |
| 8 | Shannon capacity as the rate in the reward function | 5–10 dB optimistic vs a real MCS schedule (§8.9) |
| 9 | Calling the UAV a "UT" to stay "inside" the 22.5 m bound | violates the bound and breaks the $C'(h_{UT})$ second LoS branch |
| 10 | Reporting network-average PDR only | hides per-sensor persistent outages — the entire point of the problem |

### 9.4 Frequency caveats

* **2.4 GHz (ISM) is outside 3GPP NR FR1 bands.** NR FR1 is 410 MHz–7.125 GHz but banded; 2.4 GHz
  is Wi-Fi/Bluetooth territory. Simu5G will happily model it, but "3GPP TR 38.901 + Simu5G at
  2.4 GHz" is a modelling choice, not a conformance scenario. If you need a real NR band, use
  n1 (2.11–2.17 GHz DL) or n3 (1.815–1.875 GHz) with a 20 MHz carrier, or n28/n8/n20 at 700–900 MHz
  for LPWAN IoT — and recompute $N_0+10\log_{10}B+F$ for the real bandwidth.
* **[38.901]'s frequency range is $0.5 < f_c < f_H$ GHz** with $f_H=30$ GHz for RMa and 100 GHz
  elsewhere. 2.4 GHz is inside all of them.
* **mmWave (28 GHz, 39 GHz)**: add oxygen absorption ($\approx 0.02$ dB/km at 28 GHz excluding the
  60 GHz band; $\approx 15$ dB/km peak at 60 GHz), rain attenuation from ITU-R P.838, and the
  explicit LoS/NLOS state switching of §5.1. Not modelled by INET or Simu5G.

### 9.5 Other caveats worth stating in a report

* **$\sigma_{SF}$ is a *marginal* statistic.** Correlating shadowing across sensors (§2.2) changes
  the coverage-probability distribution but not the marginal. If you only ever look at marginal
  PDR, implementing spatial correlation changes nothing — which is precisely why it is easy to skip
  and why doing so is defensible, provided you say so.
* **Small-scale fading barely matters for packet-level PDR at these rates.** With $T_c\approx2.2$ ms
  at 10 m/s and 2.4 GHz, and packets of 0.8–2 ms, the fast fade is essentially independent between
  packets; the *marginal* BER/PER is what matters and $R(\Delta x)$ of §2.2 does not enter. It
  *does* matter for (i) sub-$\mu$s delay-critical metrics, and (ii) the *burstiness* of failures
  at the packet level — hence per-TTI fading rather than per-transmission fading.
* **TR 38.901 §7.4.1 Table 7.4.1-1 footnote 6** — the "Optional" rows
  ($32.4+20\log_{10}f_c+30\log_{10}d_{3D}$ etc.) are *alternative* models with different $\sigma_{SF}$
  (7.8, 8.2, 8.29 dB). Do not average the main and optional models.
* **RMa LOS $\sigma_{SF}$ is distance-dependent** (4 dB below $d_{\rm BP}$, 6 dB above) — an
  implementation that hard-codes 4 dB for all RMa LOS is wrong above the breakpoint.
* **The `max(LOS, NLOS)` in (1.3d), (1.4d), (1.5e), (1.6b) is not a no-op.** For UMa/UMi it is
  redundant above $\approx7$ m but matters for the smallest cells; for InF-DL it selects the
  InF-SL floor and is mandatory.
* **In [38.901], $h_E$ must be drawn per link**, not per node — a detail that changes $d'_{\rm BP}$
  by hundreds of metres between adjacent users.
* **INET's `ApskErrorModel` has no FEC.** Its BER/PER are *uncoded*. Adding RLC/PDCP in the stack
  does not change them. Use `ApskLayeredErrorModel` (bilevel) or Simu5G's HARQ + BLER curves if you
  want coding gains.

---

## 10. Recommended configuration for a UAV-IoT persistent-coverage study

A defensible, internally consistent configuration:

| Component | Choice | Rationale |
|---|---|---|
| Scenario | UMa, `URBAN_MACROCELL` | 3GPP-calibrated PLE 2.2 / 3.908, $\sigma_{SF}$ 4 / 6 dB |
| Carrier | 2.4 GHz (or n3/n1 at 2.1 GHz) | inside [38.901] validity; ISM IoT realism |
| Bandwidth | 200 kHz ($N_{\rm RB}\approx13$ at $\mu=0$) | IoT-appropriate; forces $N_0 = -121$ dBm |
| Height | $h_{BS}\in[20,200]$ m, $h_{UT}=1.5$ m | document the [38.901] $h_{BS}$ extrapolation |
| LoS state | **custom $P_{LOS}(h,d_{2D})$** from [AlH20] | the one thing [38.901] cannot supply |
| Path loss | UMa NLOS (1.3e) for NLOS; **UMa LOS (1.3b)** for LoS; (5.2a) as a cross-check | |
| Antenna | `AxiallySymmetricAntenna`, `gains = "0 18 32.5 15 65 -12 180 -30"`, nadir-pointing | real footprint, §5.4b |
| Shadowing | $\sigma_{SF}=6$ dB (NLOS) / 4 dB (LoS), **spatially correlated**, $d_{cor}=37/50$ m | §2.2 |
| Fast fading | Rician $K=9\pm3.5$ dB (LoS), Rayleigh (NLOS); per-TTI or per-`correlationDistance` | §2.4, §4.8 |
| Receiver | `snirThreshold` derived from (8.11a) or `ApskErrorModel` + MCS schedule | not a magic number |
| Noise | `IsotropicScalarBackgroundNoise.power = -173.98 + 10log10(B) + F` | §4.9 |
| Propagation | `ConstantSpeedPropagation`, `propagationSpeed = 299792458mps` | |
| Error metric | SINR-threshold (fast) **and** PER-based (accurate) | §4.6 |
| Baselines | `UnitDiskRadio` (speed) + a LoS-only ideal radio (upper bound) | ablation |

---

## 11. Formula index (quick reference)

| Quantity | Formula | Source |
|---|---|---|
| 3-D slant range | $d_{3D}=\sqrt{d_{2D}^2+(h_{BS}-h_{UT})^2}$ | [38.901] (7.4-1) |
| Breakpoint (UMa/UMi) | $d'_{\rm BP}=4h'_{BS}h'_{UT}f_c/c$ | [38.901] Note 1 |
| Breakpoint (RMa/SMa) | $d_{\rm BP}=2\pi h_{BS}h_{UT}f_c/c$ | [38.901] Note 5 |
| UMa LOS | $28.0+22\log_{10}d_{3D}+20\log_{10}f_c$ (below BP) | [38.901] T7.4.1-1 |
| UMa NLOS | $13.54+39.08\log_{10}d_{3D}+20\log_{10}f_c-0.6(h_{UT}-1.5)$ | [38.901] T7.4.1-1 |
| UMi NLOS | $35.3\log_{10}d_{3D}+22.4+21.3\log_{10}f_c-0.3(h_{UT}-1.5)$ | [38.901] T7.4.1-1 |
| RMa LOS | $20\log_{10}(40\pi d_{3D}f_c/3)+\min(0.03h^{1.72},10)\log_{10}d_{3D}-\min(0.044h^{1.72},14.77)+0.002\log_{10}(h)d_{3D}$ | [38.901] T7.4.1-1 |
| RMa NLOS | $161.04-7.1\log_{10}W+7.5\log_{10}h-(24.37-3.7(h/h_{BS})^2)\log_{10}h_{BS}+(43.42-3.1\log_{10}h_{BS})(\log_{10}d_{3D}-3)+20\log_{10}f_c-(3.2(\log_{10}(11.75h_{UT}))^2-4.97)$ | [38.901] T7.4.1-1 |
| SF correlation | $R(\Delta x)=\exp(-\Delta x/d_{cor})$ | [38.901] (7.4-5), [P.1816] |
| Doppler | $f_{D,\max}=vf_c/c$ | [Rappaport] |
| Coherence time | $T_c=9/(16\pi f_{D,\max})$ | [Rappaport] |
| Thermal noise | $N=kTB$, $N_0=-173.98$ dBm/Hz @290 K | SI / [Rappaport] |
| SINR | $\mathrm{SINR}=P_r/(N+\sum P_i)$ | — |
| Shannon | $R=B\log_2(1+\mathrm{SINR})$ | Shannon 1948 |
| BPSK/QPSK BER | $\frac12\operatorname{erfc}(\sqrt{E_b/N_0})$ | [INET45] `BpskModulation.cc` |
| M-QAM BER (INET) | $\frac{4}{k}(1-1/\sqrt M)\frac12\operatorname{erfc}(\frac{1}{\sqrt2}\sqrt{\frac{3k}{M-1}E_b/N_0})$ | [INET45] `MqamModulationBase.cc` |
| PER (INET) | $1-(1-P_b)^{L_H}(1-P_b)^{L_D}$ | [INET45] `ApskErrorModel.cc` |
| A2G path loss | $PL_{\rm FS}(d)+20\log_{10}(\sqrt{d^2+h^2}/d)+\eta$ | [AlH14] |
| Antenna footprint | $r_{fp}=h\tan(\alpha/2)$ | geometry |
| One-way delay | $t_T=t_2-t_1$ | [Y.1540], [RFC7679] |
| Delay variation | $\mathrm{IPDV}(T_1,T_2)=\|t_{T_1}-t_{T_2}\|$ | [Y.1540], [RFC2680] |
| PDR | $1-\frac{N_{\rm lost}}{N_{\rm sent}}$ | [Y.1540] |

---

## 12. References

1. **3GPP TR 38.901**, *Study on channel model for frequencies from 0.5 to 100 GHz*.
   ETSI TR 138 901 V16.1.0 (2020-11); ETSI TR 138 901 V19.1.0 (2025-10).
   <https://www.etsi.org/deliver/etsi_tr/138900_138999/138901/19.01.00_60/tr_138901v190100p.pdf>
2. **3GPP TS 38.214**, *NR; Physical layer; Physical layer procedures for control* (Release 16/17).
3. **3GPP TS 38.211**, *NR; Physical channels and modulation*.
4. **3GPP TS 38.104**, *NR; Base station (BS) radio transmission and reception*.
5. **3GPP TR 36.814**, *Further advancements for E-UTRA physical layer aspect*.
6. **3GPP TR 36.873**, *Study on spatial channel model for frequencies from 2 to 6 GHz*.
7. **3GPP TR 36.842**, *Study on performance of 3GPP LTE radio interface*.
8. **3GPP TR 38.811**, *Study on NR to support non-terrestrial networks* (Release 15/16).
9. **3GPP TR 38.821**, *Solutions for NR to support Non-Terrestrial Networks (NTN)* (Release 16).
   <https://www.3gpp.org/dynareport/38821.htm>
10. **3GPP**, *Non-Terrestrial Networks (NTN)* technology overview.
    <https://www.3gpp.org/technologies/ntn-overview>
11. **ITU-R Recommendation P.1816** (cited by [38.901] §7.4.4).
12. **ITU-T Recommendation Y.1540**, *Internet protocol data communication service — IP packet
    transfer and availability performance parameters* (Dec. 2007; 2011 revision).
13. **ITU-T Recommendation Y.1541** (12/2011), *Network performance objectives for IP-based
    services*. <https://www.itu.int/rec/T-REC-Y.1541/en>
14. **IETF RFC 7679**, *A One-Way Delay Metric for IP Performance Metrics (IPPM)*.
    <https://datatracker.ietf.org/doc/html/rfc7679>
15. **IETF RFC 2680**, *An IP Packet Delay Variation Metric for IPPM*.
16. **IETF RFC 5976**, *A Model for Networks Using Y.1541 Quality-of-Service Classes*
    (summarises the Y.1541 classes).
17. **IETF RFC 3550**, *RTP: A Transport Protocol for Real-Time Applications* (inter-arrival jitter).
18. **T. S. Rappaport**, *Wireless Communications: Principles and Practice*, 2nd ed.,
    Prentice Hall, 2002.
19. **R. H. Clarke**, "A statistical theory of coverage in a randomly dispersed radio system,"
    *IRE Transactions on Communications*, vol. 6, no. 2, pp. 389–397, April 1958.
20. **W. C. Jakes (ed.)**, *IEEE 802.11 Standard*, IEEE, 1997.
21. **A. Al-Hourani, S. Kandeepan, S. Lardner**, "Optimal LAP altitude for maximum coverage,"
    *IEEE Wireless Communications Letters*, vol. 3, no. 6, pp. 569–572, Dec. 2014.
    doi:10.1109/LWC.2014.2342736
22. **A. Al-Hourani**, "On the probability of line-of-sight in urban environments,"
    *IEEE Wireless Communications Letters*, vol. 9, no. 8, pp. 1178–1181, Aug. 2020.
    doi:10.1109/LWC.2020.2985316
23. **A. Al-Hourani, S. Kandeepan, A. Jamalipour**, "Modeling air-to-ground path loss for low
    altitude platforms in urban environments," *IEEE GLOBECOM*, pp. 2898–2904, 2014.
24. **Li Chunjian**, "Efficient Antenna Patterns for Three-Sector WCDMA Systems," 2001
    (cited by [INET45] `CosineAntenna.ned`, eq. B.1–B.2).
25. **INET Framework v4.5.0**, <https://github.com/inet-framework/inet/tree/v4.5.0>.
    Key files: `src/inet/physicallayer/wireless/common/pathloss/{FreeSpacePathLoss,LogNormalShadowing,RicianFading,TwoRayGroundReflection,BreakpointPathLoss}.cc`;
    `src/inet/physicallayer/wireless/common/base/packetlevel/SnirReceiverBase.cc`;
    `src/inet/physicallayer/wireless/apsk/packetlevel/errormodel/ApskErrorModel.cc`;
    `src/inet/physicallayer/wireless/common/base/packetlevel/MqamModulationBase.cc`;
    `src/inet/physicallayer/wireless/common/modulation/BpskModulation.cc`.
26. **Simu5G v1.7.0**, <https://github.com/inet-framework/Simu5G/tree/v1.7.0>; documentation
    <https://simu5g.org/>. Key files:
    `src/simu5g/stack/phy/channelmodel/{StochasticChannelModel,Tr38901PathLossModel}.{cc,ned}`;
    `src/simu5g/stack/mac/amc/NrMcs.cc`;
    `src/simu5g/common/blerCurves/{BLERvsSINR_15CQI_TU.h,BLERvsSINR_15CQI_AWGN.h}`;
    `src/simu5g/common/carrierAggregation/ComponentCarrier.cc`.
27. **A. Radius et al.**, "Implementation of a Channel Model for Non-Terrestrial Networks in ns-3,"
    *Proc. 12th ACM Conference on Systems and Networks (SenSys/NSDI companion)*, 2023.
    doi:10.1145/3592149.3592158
28. **H. Poddar, A. …**, "Validation of 3GPP TR 38.901 Indoor Hotspot Path Loss Model Based on
    Measurements Conducted at 6.75, 16.95, 28, and 73 GHz," arXiv:2504.15589, 2025.
29. **T. Bai, P. Varshney, Z. Wu, A. Alshamleh, R. W. Heath Jr., D. Xu, H. K. Mehrpoust,**
    "Propagation Path Loss Models for 5G Urban Micro- and Macro-Cellular Scenarios,"
    arXiv:1511.07311.
30. **Shannon, C. E.**, "A Mathematical Theory of Communication," *Bell System Technical Journal*,
    vol. 27, pp. 379–423 and 623–656, 1948.

---

*All numeric values in this document were computed or verified against primary sources during
compilation on 29 September 2026. Where a formula has more than one published parameterisation, the
discrepancy is flagged in place rather than silently resolved.*

