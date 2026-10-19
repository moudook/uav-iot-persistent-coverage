from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_AUTO_SIZE

# ---------------- Design system (topic: sky / aerial networks) ----------------
DARK    = RGBColor(0x0B, 0x1F, 0x3A)   # deep navy (title / conclusion)
PRIMARY = RGBColor(0x12, 0x4E, 0x89)   # sky blue (headings)
TEAL    = RGBColor(0x2A, 0x9D, 0x8F)   # accent for quotes
ACCENT  = RGBColor(0xE8, 0x8A, 0x2B)   # warm accent (dark-slide headings)
CARD    = RGBColor(0xEE, 0xF2, 0xF7)   # light card fill
DCARD   = RGBColor(0x16, 0x30, 0x55)   # dark card fill
LINE    = RGBColor(0xD5, 0xDD, 0xE5)   # card border
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
TEXT    = RGBColor(0x20, 0x24, 0x28)
MUTED   = RGBColor(0x5A, 0x63, 0x70)

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

def bg(slide, color):
    f = slide.background.fill
    f.solid(); f.fore_color.rgb = color

def add_text(slide, x, y, w, h):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.text_frame.word_wrap = True
    return tb, tb.text_frame

# item tuple: (text, level, bold, color, size, italic)
def H(t, color=PRIMARY, size=17): return (t, 0, True, color, size, False)
def B(t, color=TEXT, size=13):     return ("\u2022  " + t, 1, False, color, size, False)
def Q(t, size=12.5):               return ("\u201c" + t + "\u201d", 1, False, TEAL, size, True)
def HD(t):                         return (t, 0, True, ACCENT, 17, False)
def BD(t):                         return ("\u2022  " + t, 1, False, WHITE, 13, False)
def QD(t):                         return ("\u201c" + t + "\u201d", 1, False, TEAL, 12.5, True)

def render(tf, items):
    tf.clear()
    first = True
    for spec in items:
        text, lvl, bold, color, size, ital = spec
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = text
        p.level = lvl
        p.space_after = Pt(4)
        p.space_before = Pt(0)
        for r in p.runs:
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.italic = ital
            r.font.name = "Arial"
            r.font.color.rgb = color

def card(slide, x, y, w, h, items, dark=False):
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                Inches(x), Inches(y), Inches(w), Inches(h))
    sp.fill.solid()
    sp.fill.fore_color.rgb = DCARD if dark else CARD
    sp.line.color.rgb = LINE
    sp.line.width = Pt(0.75)
    sp.shadow.inherit = False
    tf = sp.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.18); tf.margin_right = Inches(0.18)
    tf.margin_top = Inches(0.14);  tf.margin_bottom = Inches(0.14)
    render(tf, items)
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE   # shrink-to-fit, never overflow
    return sp

def content_slide(title, columns, dark=False):
    s = prs.slides.add_slide(BLANK)
    bg(s, DARK if dark else WHITE)
    tb, tf = add_text(s, 0.6, 0.32, 12.1, 1.0)
    p = tf.paragraphs[0]; p.text = title
    p.font.size = Pt(27); p.font.bold = True
    p.font.name = "Arial"; p.font.color.rgb = (WHITE if dark else PRIMARY)
    n = len(columns)
    if n == 1:
        card(s, 0.6, 1.5, 12.1, 5.4, columns[0], dark=dark)
    else:
        cw = 5.9
        for i, col in enumerate(columns):
            card(s, 0.6 + i * 6.23, 1.5, cw, 5.4, col, dark=dark)
    return s

# ---------------- Slide 1: Title (dark) ----------------
s = prs.slides.add_slide(BLANK)
bg(s, DARK)
tb, tf = add_text(s, 0.8, 1.9, 11.7, 2.4)
p = tf.paragraphs[0]; p.text = "A Survey on Unmanned Aerial Vehicles (UAVs) Communications"
p.font.size = Pt(34); p.font.bold = True; p.font.name = "Arial"; p.font.color.rgb = WHITE
p2 = tf.add_paragraph(); p2.text = "State-of-the-Art, Existing Standards, and Future Directions"
p2.font.size = Pt(20); p2.font.color.rgb = TEAL; p2.font.name = "Arial"; p2.space_before = Pt(8)
tb2, tf2 = add_text(s, 0.8, 6.4, 11.7, 0.8)
p3 = tf2.paragraphs[0]; p3.text = "Full-paper reading & content summary   \u2022   Week 1   \u2022   ML in Wireless Networks"
p3.font.size = Pt(13); p3.font.color.rgb = RGBColor(0xB8, 0xC4, 0xD4); p3.font.name = "Arial"

# ---------------- Slide 2: Agenda ----------------
content_slide("Agenda \u2014 Whole-Paper Walkthrough", [[
    H("Roadmap", size=18),
    B("1. Introduction & Contributions"),
    B("2. Background: UAS, FANET, Cooperation schemes"),
    B("3. UAV-Based Network Architecture \u2014 roles, AI/ML, RIS, ISAC, MIMO, DT, self-org, spectrum, protocols, security, optimization"),
    B("4. Standardization (3GPP Releases 15\u201318) & Real Testbeds"),
    B("5. Open Issues, Recommendations & Conclusion"),
    B("6. Course Problem Statement & mapping to the paper"),
]])

# ---------------- Slide 3: I + II ----------------
content_slide("I. Introduction & II. Contributions", [
    [H("I. Motivation & Scope"),
     B("UAVs (drones): surging demand in civilian & military domains \u2014 low cost, easy deployment, minimal risk."),
     Q("A reliable wireless communication link between swarms of drones and ground base stations (BS) is essential to automate the aerial network, e.g., Flying Ad-hoc Networks (FANETs)."),
     B("Early MANET policies failed for aerial networking: rapidly changing topology, fast mobility, and three-dimensional free space movements."),
     Q("UAVs are characterized by greater degrees of mobility and freedom in the 3D space\u2026 in comparison to ground networks."),
     Q("This survey provides a holistic view about the current state-of-the-art on UAV communications, identifying challenges and outlining research topics."),
     B("Future \u2192 6G + SAGSIN (Space-Air-Ground-Sea Integrated Network); enablers: AI/ML, edge, blockchain, RIS, Digital Twins, ISAC.")],
    [H("II. Contributions (what's new)"),
     Q("It is the first to systematically integrate both academic research and industry perspectives, with a strong emphasis on 3GPP standardization (Releases 15 to 18)."),
     Q("The paper introduces a unified taxonomy that incorporates emerging paradigms such as Digital Twins (DT), Reconfigurable Intelligent Surfaces (RIS), and Integrated Sensing and Communications (ISAC)."),
     B("Holistic cross-layer analysis: physical \u2192 data link \u2192 network \u2192 transport layers (prior surveys focused on isolated layers)."),
     B("Contextualizes UAV networking within future 6G and SAGSIN roadmaps."),
     B("Organization: I Intro \u2192 II Contributions \u2192 III Background \u2192 IV Architecture \u2192 V Design Aspects \u2192 VI Standardization \u2192 VII Testbeds \u2192 VIII Open Issues \u2192 IX Conclusion.")],
])

# ---------------- Slide 4: III Background ----------------
content_slide("III. Background of Aerial Networking", [
    [H("UAS & FANET"),
     B("UAS = 5 components: (1) UAV (air vehicle), (2) Ground Control Station, (3) Payload/data processing, (4) Control & data links, (5) Support system."),
     B("FANET = infrastructure-less network of flying UAV nodes."),
     B("One node acts as backbone UAV (connected to GCS/satellite)."),
     B("Building blocks: topology, mobility model, node density, radio propagation, power, localization."),
     B("Key challenge: high-speed 3D mobility vs MANETs/VANETs."),
     B("Hierarchical / cluster-based FANETs for scalability & survivability.")],
    [H("Cooperation Schemes for Multi-UAV"),
     B("Physical coupling: UAVs physically connected; motion of one depends on others."),
     B("Formations: UAVs fly a pattern (star/rectangle), maintain distance/speed/acceleration."),
     B("Swarms: homogeneous teams, decentralized communication \u2192 robust global behaviour."),
     B("Intentional cooperation: tasks allocated, predefined trajectories (centralized/decentralized)."),
     B("Modern missions = hybrid / regime-switching systems (switch modes per mission phase)."),
     B("UAV classification: by type (fixed-wing, rotary-wing, hybrid/VTOL); by size (small/mini, medium, large).")],
])

# ---------------- Slide 5: IV Overview (dark) ----------------
content_slide("IV. UAV-Based Network Architecture", [
    [HD("Taxonomy \u2014 13 sub-areas"),
     BD("A. Communication Architectures"),
     BD("B. Roles of UAVs in Networks"),
     BD("C. AI/ML in UAV Communications"),
     BD("D. Generative AI for A2G Channel Modeling"),
     BD("E. Internet of Drones (IoD) & Middleware"),
     BD("F. Multi-UAV Architectures"),
     BD("G. RIS-assisted & ISAC UAV Communications")],
    [HD("Taxonomy (cont.)"),
     BD("H. MIMO & Digital Twin for UAVs"),
     BD("I. Self-Organization"),
     BD("J. Spectrum Management"),
     BD("K. Channel Modeling & Communication Protocols"),
     BD("L. Communication & Security Requirements"),
     BD("M. Resource Optimization"),
     QD("A unified taxonomy bridging academic research, 3GPP standardization, and practical deployment.")],
], dark=True)

# ---------------- Slide 6: A-D ----------------
content_slide("IV. Communication, Roles, AI/ML, GenAI (A\u2013D)", [
    [H("A. Communication Architectures"),
     B("1. Direct links (ISM 2.4/5.8 GHz): simplest, consumer-grade, but limited by LoS & range; safety/interference sensitive."),
     B("2. Satellite-based: wide coverage, good for NLoS/remote; but high latency (~0.12 s), heavy antennas, cost, weather."),
     Q("Cellular-connected UAVs offer several appealing advantages\u2026 a win-win case not only for UAVs, but also for cellular networks."),
     B("UAV roles in cellular: (a) aerial BS / flying relay = UAV-Assisted Cellular; (b) aerial user = Cellular-Connected UAV."),
     B("Choice: direct = point-to-point; satellite = rural/remote; cellular = urban/dense."),
     H("B. Roles of UAVs in Networks"),
     Q("UAVs as base stations enables continuity of communications by expanding the communication coverage and acting as protocol converters."),
     B("Challenges: energy optimization, coverage, bandwidth, trajectory/path planning, WPT, security."),
     B("UAV as Relay Station: extends range of existing infrastructure (disaster response, on-demand coverage)."),
     B("UAV as Sensor/Actuator: surveillance, agriculture, forestry; low bandwidth; often onboard processing; can act as data mule.")],
    [H("C. AI/ML in UAV Communications"),
     B("Optimize trajectories + radio resources jointly (power, spectrum, user association) under non-convex constraints."),
     B("Enhance PHY/MAC: channel estimation, beam/antenna mgmt, interference handling in 3D channels."),
     B("Automate network functions: mobility mgmt, routing, load balancing (single & swarm)."),
     B("Improve security: intrusion/anomaly detection, jamming identification in multi-hop aerial networks."),
     H("D. Generative AI for Air-to-Ground Channel Modeling"),
     Q("The development and examination of UAV communications critically depend on precise models of electromagnetic propagation."),
     B("Standardized models (3GPP TR 38.901) are terrestrial-calibrated \u2192 inadequate for aerial uptilt paths."),
     B("Data-driven (site-specific) & generative (non-site-specific): TTS-CGAN, MTS-CGAN for spatially consistent modeling."),
     B("Open challenge: spatio-temporal consistency + capturing small-scale fading in generated samples.")],
])

# ---------------- Slide 7: E-H ----------------
content_slide("IV. IoD, Multi-UAV, RIS/ISAC, MIMO/DT (E\u2013H)", [
    [H("E. Internet of Drones (IoD) & Middleware"),
     B("IoD treats low-altitude airspace as a limited resource; ZSP (Zone Service Provider) coordinates local UAVs."),
     B("Airspace divided into zones with airways (flight paths) & intersections; nodes for takeoff/land/recharge."),
     B("Middleware gives vendor-independent unified control; simulation env. for resilient protocols."),
     H("F. Multi-UAV Architectures"),
     B("Single-layered vs multi-layered (3D). Gateway view: C1 (star), C2 (leader gateway), C3 (mesh)."),
     B("Leader UAV selected for stability (static leader-follower or distributed leadership)."),
     B("Scalability: star \u2192 mesh \u2192 multi-star / hierarchical mesh."),
     B("Tech maturity: energy optimization = mature; trajectory/path planning = intermediate; security & trust = early stage.")],
    [H("G. RIS-assisted & ISAC UAV Communications"),
     B("RIS: electronically controllable EM surfaces reflect/enhance signals; mounted on UAVs boosts A2G links."),
     B("6 RIS integration scenarios: data collection, ubiquitous coverage, relaying, PHY security, SWIPT, cellular-connected."),
     B("ISAC: joint sensing + communication \u2014 sensing aids beam tracking/interference; comms aids mapping/positioning."),
     B("Challenge: joint design of sensing+computing+communication; co-channel interference; battery for continuous sensing."),
     H("H. MIMO & Digital Twin for UAVs"),
     B("MIMO: spectral efficiency via spatial diversity/multiplexing; challenges: pilot contamination, 3D beam tracking."),
     B("Solutions: interference-cancellation pilot decontamination, Kalman-filter channel tracking, dual-functional MIMO."),
     B("Digital Twin: virtual replica (data acquisition \u2192 processing \u2192 application); aligns with 3GPP Rel-15/16/17."),
     B("DT benefit: real-time monitoring, predictive maintenance, path/task adaptation, operator training.")],
])

# ---------------- Slide 8: I-M ----------------
content_slide("IV. Self-Org, Spectrum, Channels/Protocols, Security, Optimization (I\u2013M)", [
    [H("I. Self-Organization"),
     B("Self-organization = ad-hoc network formation in the sky; akin to natural flocking (Reynolds' boids: separation, alignment, cohesion)."),
     B("Recipe: (1) aerial node addressing, (2) neighbor discovery, (3) network formation, (4) path planning/routing."),
     B("Real-world UAV nets usually augmented with partial infrastructure (satellite/cellular) due to high mobility."),
     H("J. Spectrum Management"),
     Q("A major issue is the lack of a dedicated spectrum for commercial drones\u2026 especially for command and control communication."),
     B("Current: ISM bands (900 MHz, 2.4, 5.8 GHz); FCC considering 5030\u20135091 MHz & 60\u201364 GHz."),
     B("3 sharing schemes: Opportunistic (sense spectrum holes), Competitive (spectrum auction), Cooperative (primary-UAV coordination)."),
     H("K. Channel Modeling & Protocols"),
     B("Channel = large-scale (LoS/NLoS, path loss, shadowing) + small-scale (multipath, Doppler, polarization)."),
     B("GPU ray-tracing (Sionna RT) enables site-specific calibration at scale.")],
    [H("K. Protocols (OSI) (cont.)"),
     B("Physical: directional antennas, Doppler. Data Link: MAC, full-duplex, MPR, clustering."),
     B("Network: AODV/DSR/TSAODV, EE-Hello, JTCR, k-means+black-hole clustering."),
     B("Transport: PRRT, LRT, multipath TCP, QUAD/CUBIC congestion control."),
     H("L. Communication & Security Requirements"),
     B("C2 modes (3GPP TS 22.125): steering to waypoints, direct stick steering, automatic flight by UTM, autonomous navigation."),
     B("Video KPIs: 8K @100 Mbps uplink; HD control min 25 Mbps uplink / 300 kbps downlink."),
     B("7 Security requirements: Confidentiality, Integrity, Non-repudiation, Authentication, Access Control, Availability, Privacy."),
     B("Mitigations: HECC, DLSMR, blockchain key mgmt, BFT/ACBFT, Sybil detection."),
     H("M. Resource Optimization"),
     B("Scarce on-board batteries/compute \u2192 efficient resource use essential."),
     B("3D UAV placement: trade-off altitude \u2191 LoS but \u2191 path loss; solved via PSO, Genetic Algorithm, CVX, branch-and-bound, convex hull."),
     B("NOMA for UAV-ground; Decode-and-Forward relay; water-filling power; Successive Convex Approximation; alternating minimization."),
     B("Graph-based: Dijkstra+Pareto, dual ascent, hypergraphs / fuzzy-graphs for modeling.")],
])

# ---------------- Slide 9: VI Standardization ----------------
content_slide("VI. Standardization (3GPP Releases 15\u201318)", [
    [H("3GPP Releases for UAV Cellular"),
     B("Rel-15: 4G LTE support tailored for UAVs; aerial user identification, location/altitude/trajectory reporting, new measurement events H1/H2."),
     B("Rel-16: remote UAV identification (TR 23.754); UTM interaction; unauthorized device detection."),
     B("Rel-17: 5G enhancements (TS 22.125/22.829) new KPIs, UxNB (UAV as gNB), application-layer tracking (TR 23.755)."),
     B("Rel-18: NR support, conditional handover, beam management, multi-antenna beamforming, dedicated BS uptilt.")],
    [H("Slicing, UUAA & C2"),
     B("UAV Authentication & Authorization (UUAA) via USS."),
     B("C2 comms: direct / network-assisted / UTM-navigated."),
     B("Network Slicing for UAV: NetSliA/B/C per eMBB/URLLC/mMTC."),
     B("AirSlice framework; SLA-driven slices for aerial services.")],
])

# ---------------- Slide 10: VII Testbeds ----------------
content_slide("VII. Real Testbeds, Deployments & Experiments", [
    [H("Representative Testbeds"),
     B("AERPAW (NSF PAWR): large-scale SDR platform; RF/I-Q/packet-level emulation; E-VMs as UE/gNB/core; digital twins."),
     B("SkyRAN / SkyCore / SkyHAUL (NEC): flying LTE RAN, EPC core, self-organizing gigabit multi-UAV network.")],
    [H("Testbeds (cont.)"),
     B("EuroDRONE: V2I/V2V UTM testbed with autonomous small UAVs (2.4/5 GHz LTE + Sub-GHz)."),
     B("HITL (Hardware-in-the-Loop) & SITL (Software-in-the-Loop) emulators; OMNeT++/ns-3/X-Plane (AVENS, CUSCUS, FlyNetSim)."),
     B("Aerial BS testbeds: 60 GHz mmWave UAV-BS channel model; LoRa/NB-IoT LPWAN relay; USRP-based beamforming.")],
])

# ---------------- Slide 11: VIII Open Issues ----------------
content_slide("VIII. Open Research Issues (14)", [
    [H("Open Issues (1\u20137)"),
     B("Energy constraint"), B("UAV platform & mobility model"), B("Routing (dynamic topology)"),
     B("Path planning"), B("QoS provisioning"), B("Fault handling"),
     B("Data processing (edge/fog)")],
    [H("Open Issues (8\u201314)"),
     B("Data sharing & security"), B("FANET standardization"), B("Distributed optimization algorithms"),
     B("Spectrum management"), B("Network formation/topology control"), B("Testing & simulation fidelity"),
     B("Airspace integration & regulation")],
])

# ---------------- Slide 12: VIII Recommendations ----------------
content_slide("VIII. Recommendations & Further Work", [
    [H("Recommendations"),
     B("Multi-UAV systems: steady comms, remote C2, unlimited coverage, adaptive beamforming/directional antennas."),
     B("Routing via Deep RL / hybrid-learning predicting topology dynamics."),
     B("Blockchain-based device lifecycle registration (manufacture\u2192repair\u2192scrap).")],
    [H("Further Work"),
     B("Realistic UAV simulators (energy + flight dynamics); full security frameworks (jamming/spoofing); cognitive-radio spectrum sharing."),
     B("ISAC-enhanced situational awareness; network-slicing-assisted cross-domain architectures."),
     B("Toward 6G / SAGSIN-ready UAV networks.")],
])

# ---------------- Slide 13: IX Conclusion ----------------
content_slide("IX. Conclusion", [
    [H("Summary"),
     B("UAVs enable cooperative, self-organizing missions in unreachable areas."),
     B("Coverage: communication architecture, protocols, requirements, security; network formation & state-of-the-art solutions."),
     B("3GPP standardization (Rel-15\u201318) bridges research & commercial deployment; network slicing for UAV."),
     B("FANET addresses scalability of direct-link networking; communication remains the key constraint.")],
    [H("Outlook"),
     B("Open issues + future directions encourage researchers toward 6G / SAGSIN-ready UAV networks."),
     B("Convergence of AI/ML, RIS, ISAC, Digital Twins reshapes UAV networking."),
     B("Standardization (3GPP) + real testbeds (AERPAW, SkyRAN) turn theory into deployable aerial networks."),
     Q("UAV communications has evolved from a niche topic to a key enabler of future wireless connectivity.")],
])

# ---------------- Slide 14: Problem Statement (dark) ----------------
content_slide("Course Problem Statement (Week 1)", [[
    H("Course Problem Statement (verbatim)", ACCENT, 18),
    BD("Develop an AI-based system for deploying multiple UAVs as temporary aerial base stations."),
    BD("The system should determine where UAVs should be positioned and how they should move as users move,"),
    BD("while maintaining UAV-to-UAV connectivity, maximizing coverage, and minimizing energy consumption."),
    BD("Input: User locations/density, UAV positions, battery levels, communication range, channel quality."),
    BD("Output: UAV positions/movement decisions and resulting coverage/connectivity."),
    BD("AI/ML: PSO / Genetic Algorithm for placement + Multi-Agent Q-Learning for dynamic formation."),
]], dark=True)

# ---------------- Slide 15: Mapping ----------------
content_slide("How the Survey Maps to the Problem", [
    [H("Paper content \u2192 Problem"),
     B("UAV as Base Station (Sec IV-B) \u2192 aerial base stations."),
     B("3D placement optimization (Sec IV-M/K) \u2192 where UAVs are positioned."),
     B("PSO & Genetic Algorithm (Sec IV-M) \u2192 placement AI/ML."),
     B("Multi-UAV architectures & leader (Sec IV-F) \u2192 how they move as a formation."),
     B("Energy optimization (Sec IV-M, Open Issues) \u2192 minimizing energy."),
     B("UAV-to-UAV connectivity = mesh / C1\u2013C3 (Sec IV-F) \u2192 maintain connectivity."),
     B("Coverage maximization (Sec IV-B/M) \u2192 maximize coverage.")],
    [H("Our course approach"),
     B("Placement: PSO/GA over 3D coordinates (CVX baseline)."),
     B("Movement: Multi-Agent Q-Learning for dynamic formation."),
     B("Constraint 1: maintain UAV-UAV links (mesh/graph)."),
     B("Constraint 2: maximize coverage (user density map)."),
     B("Constraint 3: minimize energy (battery-aware)."),
     B("Input/Output matches the paper's resource-optimization loop.")],
])

DST = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\PPT_content\PPT.pptx"
prs.save(DST)
print("Saved. Total slides:", len(prs.slides._sldIdLst))
