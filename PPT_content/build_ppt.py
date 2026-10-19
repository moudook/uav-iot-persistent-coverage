import shutil
from pptx import Presentation
from pptx.util import Pt

SRC = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\PPT_content\PPT.pptx"
BAK = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\PPT_content\PPT_backup.pptx"
DST = SRC

# Backup original template
shutil.copyfile(SRC, BAK)

# Fresh presentation (clean, valid default theme, standard layouts)
prs = Presentation()

# Default layout indices: 0=Title Slide, 1=Title & Content, 2=Section Header,
# 3=Two Content, 5=Title Only, 6=Blank
L_TITLE = 0
L_BODY  = 1
L_SECT  = 2
L_TWOC  = 3

def add(layout_idx):
    return prs.slides.add_slide(prs.slide_layouts[layout_idx])

def set_ph(slide, idx, text, size=None, bold=None):
    ph = None
    for p in slide.placeholders:
        if p.placeholder_format.idx == idx:
            ph = p
            break
    if ph is None:
        return
    tf = ph.text_frame
    tf.word_wrap = True
    for para in list(tf.paragraphs):
        para.clear()
    tf.paragraphs[0].text = text
    for r in tf.paragraphs[0].runs:
        if size: r.font.size = Pt(size)
        if bold is not None: r.font.bold = bold

def set_bullets(slide, idx, items, base=15):
    ph = None
    for p in slide.placeholders:
        if p.placeholder_format.idx == idx:
            ph = p
            break
    if ph is None:
        return
    tf = ph.text_frame
    tf.word_wrap = True
    first = True
    for text, lvl in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = text
        p.level = lvl
        for r in p.runs:
            r.font.size = Pt(base - lvl*2)
            r.font.name = 'Calibri'

def slide_title(title, subtitle):
    s = add(L_TITLE)
    set_ph(s, 0, title, size=36, bold=True)
    set_ph(s, 1, subtitle, size=18)
    return s

def slide_section(text):
    s = add(L_SECT)
    set_ph(s, 0, text, size=40, bold=True)
    return s

def slide_body(title, items, size=16):
    s = add(L_BODY)
    set_ph(s, 0, title, size=26, bold=True)
    set_bullets(s, 1, items, base=size)
    return s

def slide_two(title, col1, col2):
    s = add(L_TWOC)
    set_ph(s, 0, title, size=24, bold=True)
    set_bullets(s, 1, col1, base=14)
    set_bullets(s, 2, col2, base=14)
    return s

# ============================================================
# DECK
# ============================================================
slide_title(
    "A Survey on Unmanned Aerial Vehicles (UAVs) Communications\nState-of-the-Art, Existing Standards and Future Directions",
    "Full-paper reading & content summary  •  Week 1  •  ML in Wireless Networks"
)

slide_body("Agenda — Whole-Paper Walkthrough", [
    ("1. Introduction & Contributions", 0),
    ("2. Background: UAS, FANET, Cooperation schemes", 0),
    ("3. UAV-Based Network Architecture (roles, AI/ML, RIS, ISAC, MIMO, DT, self-org, spectrum, protocols, security, optimization)", 0),
    ("4. Standardization (3GPP Releases 15-18) & Real Testbeds", 0),
    ("5. Open Issues, Recommendations & Conclusion", 0),
    ("6. Course Problem Statement & mapping to the paper", 0),
])

# I. INTRODUCTION
slide_section("I. Introduction")
slide_body("Motivation & Scope", [
    ("UAVs (drones): surging demand in civilian & military domains \u2014 low cost, easy deployment, minimal risk.", 0),
    ("\u201cA reliable wireless communication link between swarms of drones and ground base stations (BS) is essential to automate the aerial network, e.g., Flying Ad-hoc Networks (FANETs).\u201d", 0),
    ("Early MANET policies failed for aerial networking: \u201crapidly changing topology, fast mobility, and three-dimensional free space movements.\u201d", 0),
    ("\u201cUAVs are characterized by greater degrees of mobility and freedom in the 3D space\u2026 in comparison to ground networks.\u201d", 0),
    ("Goal: \u201cprovides a holistic view about the current state-of-the-art on UAV communications, identifying challenges and outlining research topics.\u201d", 0),
    ("Future \u2192 6G + SAGSIN (Space-Air-Ground-Sea Integrated Network); enablers: AI/ML, edge, blockchain, RIS, Digital Twins, ISAC.", 0),
])

# II. CONTRIBUTIONS
slide_section("II. Contributions of this Survey")
slide_body("What makes this survey different", [
    ("\u201cIt is the first to systematically integrate both academic research and industry perspectives, with a strong emphasis on 3GPP standardization (Releases 15 to 18).\u201d", 0),
    ("\u201cThe paper introduces a unified taxonomy that incorporates emerging paradigms such as Digital Twins (DT), Reconfigurable Intelligent Surfaces (RIS), and Integrated Sensing and Communications (ISAC).\u201d", 0),
    ("Holistic cross-layer analysis: physical \u2192 data link \u2192 network \u2192 transport layers (prior surveys focused on isolated layers).", 0),
    ("Contextualizes UAV networking within future 6G and SAGSIN roadmaps.", 0),
    ("Organization: I Intro \u2192 II Contributions \u2192 III Background \u2192 IV Architecture \u2192 V Design Aspects \u2192 VI Standardization \u2192 VII Testbeds \u2192 VIII Open Issues \u2192 IX Conclusion.", 0),
])

# III. BACKGROUND
slide_section("III. Background of Aerial Networking")
slide_two("UAS & FANET",
    [("UAS = 5 components:", 0),
     ("1. UAV (air vehicle)", 1),
     ("2. Ground Control Station (GCS)", 1),
     ("3. Payload / data processing", 1),
     ("4. Control & data links (HW+SW)", 1),
     ("5. Support system", 1)],
    [("FANET = infrastructure-less network of flying UAV nodes", 0),
     ("One node = backbone UAV (connected to GCS/satellite)", 1),
     ("Building blocks: topology, mobility model, node density, radio propagation, power, localization", 1),
     ("Key challenge: high-speed 3D mobility vs MANETs/VANETs", 1),
     ("Hierarchical / cluster-based FANETs for scalability & survivability", 1)])
slide_body("Cooperation Schemes for Multi-UAV", [
    ("Physical coupling: UAVs physically connected; motion of one depends on others.", 0),
    ("Formations: UAVs fly a pattern (star/rectangle), maintain distance/speed/acceleration.", 0),
    ("Swarms: homogeneous teams, decentralized communication \u2192 robust global behaviour.", 0),
    ("Intentional cooperation: tasks allocated, predefined trajectories (centralized/decentralized).", 0),
    ("Modern missions = hybrid / regime-switching systems (switch modes per mission phase).", 0),
    ("UAV classification: by type (fixed-wing, rotary-wing, hybrid/VTOL); by size (small/mini, medium, large).", 0),
])

# IV. ARCHITECTURE
slide_section("IV. UAV-Based Network Architecture")
slide_body("A. Communication Architectures", [
    ("1. Direct links (ISM 2.4/5.8 GHz): simplest, consumer-grade, but limited by LoS & range; safety/interference sensitive.", 0),
    ("2. Satellite-based: wide coverage, good for NLoS/remote; but high latency (~0.12 s), heavy antennas, cost, weather.", 0),
    ("3. Cellular-supported: leverage existing 4G/5G; \u201cCellular-connected UAVs offer several appealing advantages\u2026 a win-win case not only for UAVs, but also for cellular networks.\u201d", 0),
    ("UAV roles in cellular: (a) aerial BS / flying relay = UAV-Assisted Cellular; (b) aerial user = Cellular-Connected UAV.", 0),
    ("Choice: direct = point-to-point; satellite = rural/remote; cellular = urban/dense.", 0),
])
slide_body("B. Roles of UAVs in Networks", [
    ("UAV as Base Station: \u201cUAVs as base stations [95] enables continuity of communications by expanding the communication coverage and acting as protocol converters.\u201d", 0),
    ("Challenges: energy optimization, coverage, bandwidth, trajectory/path planning, WPT, security.", 0),
    ("UAV as Relay Station: extends range of existing infrastructure (disaster response, on-demand coverage).", 0),
    ("UAV as Sensor/Actuator: surveillance, agriculture, forestry; low bandwidth; often onboard processing; can act as data mule.", 0),
])
slide_body("C. AI/ML in UAV Communications", [
    ("Optimize trajectories + radio resources jointly (power, spectrum, user association) under non-convex constraints.", 0),
    ("Enhance PHY/MAC: channel estimation, beam/antenna mgmt, interference handling in 3D channels.", 0),
    ("Automate network functions: mobility mgmt, routing, load balancing (single & swarm).", 0),
    ("Improve security: intrusion/anomaly detection, jamming identification in multi-hop aerial networks.", 0),
])
slide_body("D. Generative AI for Air-to-Ground Channel Modeling", [
    ("\u201cThe development and examination of UAV communications critically depend on precise models of electromagnetic propagation.\u201d", 0),
    ("Standardized models (3GPP TR 38.901) are terrestrial-calibrated \u2192 inadequate for aerial uptilt paths.", 0),
    ("Data-driven (site-specific) & generative (non-site-specific): TTS-CGAN, MTS-CGAN for spatially consistent modeling.", 0),
    ("Open challenge: spatio-temporal consistency + capturing small-scale fading in generated samples.", 0),
])
slide_body("E. Internet of Drones (IoD) & Middleware", [
    ("IoD treats low-altitude airspace as a limited resource; ZSP (Zone Service Provider) coordinates local UAVs.", 0),
    ("Airspace divided into zones with airways (flight paths) & intersections; nodes for takeoff/land/recharge.", 0),
    ("Middleware gives vendor-independent unified control; simulation env. for resilient protocols.", 0),
])
slide_body("F. Multi-UAV Architectures", [
    ("Single-layered vs multi-layered (3D). Gateway view: C1 (star), C2 (leader gateway), C3 (mesh).", 0),
    ("Leader UAV selected for stability (static leader-follower or distributed leadership).", 0),
    ("Scalability: star \u2192 mesh \u2192 multi-star / hierarchical mesh.", 0),
    ("Tech maturity: energy optimization = mature; trajectory/path planning = intermediate; security & trust = early stage.", 0),
])
slide_body("G. RIS-assisted & ISAC UAV Communications", [
    ("RIS: electronically controllable EM surfaces reflect/enhance signals; mounted on UAVs boosts A2G links.", 0),
    ("6 RIS integration scenarios: data collection, ubiquitous coverage, relaying, PHY security, SWIPT, cellular-connected.", 0),
    ("ISAC: joint sensing + communication \u2014 sensing aids beam tracking/interference; comms aids mapping/positioning.", 0),
    ("Challenge: joint design of sensing+computing+communication; co-channel interference; battery for continuous sensing.", 0),
])
slide_body("H. MIMO & Digital Twin for UAVs", [
    ("MIMO: spectral efficiency via spatial diversity/multiplexing; challenges: pilot contamination, 3D beam tracking.", 0),
    ("Solutions: interference-cancellation pilot decontamination, Kalman-filter channel tracking, dual-functional MIMO.", 0),
    ("Digital Twin: virtual replica (data acquisition \u2192 processing \u2192 application); aligns with 3GPP Rel-15/16/17.", 0),
    ("DT benefit: real-time monitoring, predictive maintenance, path/task adaptation, operator training.", 0),
])
slide_body("I. Self-Organization", [
    ("Self-organization = ad-hoc network formation in the sky; akin to natural flocking (Reynolds' boids: separation, alignment, cohesion).", 0),
    ("Recipe: (1) aerial node addressing (unicast/multicast/broadcast), (2) neighbor discovery, (3) network formation, (4) path planning/routing.", 0),
    ("Real-world UAV nets usually augmented with partial infrastructure (satellite/cellular) due to high mobility.", 0),
])
slide_body("J. Spectrum Management", [
    ("\u201cA major issue is the lack of a dedicated spectrum for commercial drones\u2026 especially for command and control communication.\u201d", 0),
    ("Current: ISM bands (900 MHz, 2.4, 5.8 GHz); FCC considering 5030\u20135091 MHz & 60\u201364 GHz.", 0),
    ("3 sharing schemes: Opportunistic (sense spectrum holes), Competitive (spectrum auction), Cooperative (primary-UAV coordination, interference-free).", 0),
])
slide_body("K. Channel Modeling & Communication Protocols", [
    ("Channel = large-scale (LoS/NLoS, path loss, shadowing) + small-scale (multipath, Doppler, polarization).", 0),
    ("GPU ray-tracing (Sionna RT) enables site-specific calibration at scale.", 0),
    ("Protocols (OSI): Physical (directional antennas, Doppler), Data Link (MAC, full-duplex, MPR, clustering),", 0),
    ("Network (AODV/DSR/TSAODV, EE-Hello, JTCR, k-means+black-hole clustering),", 0),
    ("Transport (PRRT, LRT, multipath TCP, QUAD/CUBIC congestion control).", 0),
])
slide_body("L. Communication & Security Requirements", [
    ("C2 modes (3GPP TS 22.125): steering to waypoints, direct stick steering, automatic flight by UTM, autonomous navigation.", 0),
    ("Video feedback KPIs (Table 5/6): 8K @100 Mbps uplink; HD control min 25 Mbps uplink / 300 kbps downlink.", 0),
    ("7 Security requirements: Confidentiality, Integrity, Non-repudiation, Authentication, Access Control, Availability, Privacy.", 0),
    ("Threats by connection/node vectors & OSI layers; mitigations: HECC, DLSMR, blockchain key mgmt, BFT/ACBFT, Sybil detection.", 0),
])
slide_body("M. Resource Optimization", [
    ("Scarce on-board batteries/compute \u2192 efficient resource use essential.", 0),
    ("3D UAV placement: trade-off altitude \u2191 LoS but \u2191 path loss; solved via PSO, Genetic Algorithm, CVX, branch-and-bound, convex hull.", 0),
    ("NOMA for UAV-ground; Decode-and-Forward relay; water-filling power; Successive Convex Approximation; alternating minimization.", 0),
    ("Graph-based: Dijkstra+Pareto, dual ascent, hypergraphs / fuzzy-graphs for modeling.", 0),
])

# VI. STANDARDIZATION
slide_section("VI. Standardization (3GPP)")
slide_body("3GPP Releases for UAV Cellular Communications", [
    ("Rel-15: 4G LTE support tailored for UAVs; aerial user identification, location/altitude/trajectory reporting, new measurement events H1/H2.", 0),
    ("Rel-16: remote UAV identification (TR 23.754); UTM interaction; unauthorized device detection.", 0),
    ("Rel-17: 5G enhancements (TS 22.125/22.829) new KPIs, UxNB (UAV as gNB), application-layer tracking (TR 23.755).", 0),
    ("Rel-18: NR support, conditional handover, beam management, multi-antenna beamforming, dedicated BS uptilt.", 0),
    ("UAV Authentication & Authorization (UUAA) via USS; C2 comms: direct / network-assisted / UTM-navigated.", 0),
    ("Network Slicing for UAV: NetSliA/B/C per eMBB/URLLC/mMTC; AirSlice framework; SLA-driven slices.", 0),
])

# VII. TESTBEDS
slide_section("VII. Real Testbeds, Deployments & Experiments")
slide_body("Representative UAV Communication Testbeds", [
    ("AERPAW (NSF PAWR): large-scale SDR platform; RF/I-Q/packet-level emulation; E-VMs as UE/gNB/core; digital twins.", 0),
    ("SkyRAN / SkyCore / SkyHAUL (NEC): flying LTE RAN, EPC core, self-organizing gigabit multi-UAV network.", 0),
    ("EuroDRONE: V2I/V2V UTM testbed with autonomous small UAVs (2.4/5 GHz LTE + Sub-GHz).", 0),
    ("HITL (Hardware-in-the-Loop) & SITL (Software-in-the-Loop) emulators; OMNeT++/ns-3/X-Plane (AVENS, CUSCUS, FlyNetSim).", 0),
    ("Aerial BS testbeds: 60 GHz mmWave UAV-BS channel model; LoRa/NB-IoT LPWAN relay; USRP-based beamforming.", 0),
])

# VIII. OPEN ISSUES
slide_section("VIII. Open Issues & Recommendations")
slide_body("Open Research Issues (14)", [
    ("Energy constraint \u2022 UAV platform & mobility model \u2022 Routing (dynamic topology)", 0),
    ("Path planning \u2022 QoS provisioning \u2022 Fault handling \u2022 Data processing (edge/fog)", 0),
    ("Data sharing & security \u2022 FANET standardization \u2022 Distributed optimization algorithms", 0),
    ("Spectrum management \u2022 Network formation/topology control \u2022 Testing & simulation fidelity", 0),
])
slide_body("Recommendations & Further Work", [
    ("Multi-UAV systems: steady comms, remote C2, unlimited coverage, adaptive beamforming/directional antennas.", 0),
    ("Routing via Deep RL / hybrid-learning predicting topology dynamics.", 0),
    ("Blockchain-based device lifecycle registration (manufacture\u2192repair\u2192scrap).", 0),
    ("Realistic UAV simulators (energy + flight dynamics); full security frameworks (jamming/spoofing); cognitive-radio spectrum sharing.", 0),
    ("ISAC-enhanced situational awareness; network-slicing-assisted cross-domain architectures.", 0),
])

# IX. CONCLUSION
slide_section("IX. Conclusion")
slide_body("Summary", [
    ("UAVs enable cooperative, self-organizing missions in unreachable areas.", 0),
    ("Coverage: communication architecture, protocols, requirements, security; network formation & state-of-the-art solutions.", 0),
    ("3GPP standardization (Rel-15\u201318) bridges research & commercial deployment; network slicing for UAV.", 0),
    ("FANET addresses scalability of direct-link networking; communication remains the key constraint.", 0),
    ("Open issues + future directions encourage researchers toward 6G / SAGSIN-ready UAV networks.", 0),
])

# PROBLEM STATEMENT
slide_section("Course Problem Statement (Week 1)")
slide_body("Given Problem (verbatim)", [
    ("\u201cDevelop an AI-based system for deploying multiple UAVs as temporary aerial base stations. The system should", 0),
    ("determine where UAVs should be positioned and how they should move as users move, while maintaining", 0),
    ("UAV-to-UAV connectivity, maximizing coverage, and minimizing energy consumption.\u201d", 0),
    ("Input: User locations/density, UAV positions, battery levels, communication range, channel quality.", 0),
    ("Output: UAV positions/movement decisions and resulting coverage/connectivity.", 0),
    ("AI/ML: PSO / Genetic Algorithm for placement + Multi-Agent Q-Learning for dynamic formation.", 0),
])
slide_two("How the Survey Maps to the Problem",
    [("Paper content directly relevant:", 0),
     ("UAV as Base Station (Sec IV-B)", 1),
     ("3D placement optimization (Sec IV-M/K)", 1),
     ("PSO & Genetic Algorithm (Sec K)", 1),
     ("Multi-UAV architectures & leader (Sec IV-F)", 1),
     ("Energy optimization (Sec K, Open Issues)", 1),
     ("UAV-to-UAV connectivity = mesh/C1-C3 (Sec IV-F)", 1)],
    [("Our course approach:", 0),
     ("Placement: PSO/GA over 3D coordinates (CVX baseline)", 1),
     ("Movement: Multi-Agent Q-Learning for dynamic formation", 1),
     ("Constraint 1: maintain UAV-UAV links (mesh/graph)", 1),
     ("Constraint 2: maximize coverage (user density map)", 1),
     ("Constraint 3: minimize energy (battery-aware)", 1),
     ("Input/Output matches paper's resource-optimization loop", 1)])

prs.save(DST)
print("Saved. Total slides:", len(prs.slides._sldIdLst))
