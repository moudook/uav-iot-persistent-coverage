from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_AUTO_SIZE, PP_ALIGN, MSO_ANCHOR

# ---------------- Design tokens (60-30-10, aerial/sky theme) ----------------
NAVY     = RGBColor(0x0E, 0x1B, 0x2A)   # dominant dark
PAPER    = RGBColor(0xF4, 0xF6, 0xF8)   # light bg
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
BLUE     = RGBColor(0x2E, 0x6F, 0x9E)   # secondary
AMBER    = RGBColor(0xF2, 0xA9, 0x00)   # accent (sparse)
INK      = RGBColor(0x1B, 0x26, 0x32)   # body text on light
MUTED    = RGBColor(0x5A, 0x66, 0x72)
CARDFILL = RGBColor(0xFF, 0xFF, 0xFF)
CARDLINE = RGBColor(0xD9, 0xE0, 0xE6)
QUOTEFILL= RGBColor(0xEA, 0xF1, 0xF7)
DARKCARD = RGBColor(0x16, 0x2B, 0x42)
TITLE_FONT = "Cambria"
BODY_FONT  = "Calibri"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

def bg(slide, color):
    f = slide.background.fill; f.solid(); f.fore_color.rgb = color

def add_text(slide, x, y, w, h):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.text_frame.word_wrap = True
    return tb, tb.text_frame

# item tuple: (text, lvl, bold, color, size, italic)
def H(t, color=BLUE, size=15):   return (t, 0, True, color, size, False)
def B(t, color=INK, size=12.5):  return ("\u2022  " + t, 1, False, color, size, False)
def Q(t, size=12):               return ("\u201c" + t + "\u201d", 1, False, BLUE, size, True)
def HD(t):                       return (t, 0, True, AMBER, 15, False)
def BD(t):                       return ("\u2022  " + t, 1, False, WHITE, 12.5, False)
def QD(t):                       return ("\u201c" + t + "\u201d", 1, False, BLUE, 12, True)

def render(tf, items):
    tf.clear(); first = True
    for spec in items:
        text, lvl, bold, color, size, ital = spec
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = text; p.level = lvl
        p.space_after = Pt(3); p.space_before = Pt(0)
        for r in p.runs:
            r.font.size = Pt(size); r.font.bold = bold; r.font.italic = ital
            r.font.name = BODY_FONT; r.font.color.rgb = color

def card(slide, x, y, w, h, items, fill=None, line=None, dark=False, autofit=True):
    if fill is None: fill = DARKCARD if dark else CARDFILL
    if line is None: line = (RGBColor(0x3A, 0x55, 0x72) if dark else CARDLINE)
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                Inches(x), Inches(y), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = fill
    sp.line.color.rgb = line; sp.line.width = Pt(0.75)
    sp.shadow.inherit = False
    tf = sp.text_frame; tf.word_wrap = True
    tf.margin_left = Inches(0.16); tf.margin_right = Inches(0.16)
    tf.margin_top = Inches(0.12);  tf.margin_bottom = Inches(0.12)
    render(tf, items)
    if autofit: tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    return sp

def icon_circle(slide, x, y, d, letter, fill=BLUE, txt=WHITE, fs=16):
    c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    c.fill.solid(); c.fill.fore_color.rgb = fill
    c.line.fill.background(); c.shadow.inherit = False
    tf = c.text_frame; tf.word_wrap = False
    tf.margin_top = Inches(0); tf.margin_bottom = Inches(0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p.text = letter
    p.font.size = Pt(fs); p.font.bold = True; p.font.name = BODY_FONT; p.font.color.rgb = txt
    return c

def title_band(slide, icon, title, dark=False):
    icon_circle(slide, 0.55, 0.40, 0.64, icon,
                fill=(AMBER if not dark else BLUE), fs=18)
    tb, tf = add_text(slide, 1.38, 0.34, 11.4, 0.9)
    p = tf.paragraphs[0]; p.text = title
    p.font.size = Pt(24); p.font.bold = True; p.font.name = TITLE_FONT
    p.font.color.rgb = (WHITE if dark else BLUE)

def std_slide(icon, title, left, right, dark=False):
    s = prs.slides.add_slide(BLANK); bg(s, NAVY if dark else PAPER)
    title_band(s, icon, title, dark)
    card(s, 0.60, 1.50, 5.90, 5.40, left, dark=dark)
    card(s, 6.83, 1.50, 5.90, 5.40, right, dark=dark)
    return s

def single_slide(icon, title, items, dark=False):
    s = prs.slides.add_slide(BLANK); bg(s, NAVY if dark else PAPER)
    title_band(s, icon, title, dark)
    card(s, 0.60, 1.50, 12.13, 5.40, items, dark=dark)
    return s

# ============================================================ 1. TITLE (dark)
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
tb, tf = add_text(s, 0.9, 1.7, 11.5, 2.6)
p = tf.paragraphs[0]; p.text = "A Survey on Unmanned Aerial Vehicles (UAVs) Communications"
p.font.size = Pt(33); p.font.bold = True; p.font.name = TITLE_FONT; p.font.color.rgb = WHITE
p2 = tf.add_paragraph(); p2.text = "State-of-the-Art, Existing Standards, and Future Directions"
p2.font.size = Pt(19); p2.font.color.rgb = AMBER; p2.font.name = TITLE_FONT; p2.space_before = Pt(10)
p3 = tf.add_paragraph(); p3.text = "A whole-paper reading & content map for the course project"
p3.font.size = Pt(14); p3.font.color.rgb = RGBColor(0xBF,0xCB,0xD8); p3.font.name = BODY_FONT; p3.space_before = Pt(8)
tb2, tf2 = add_text(s, 0.9, 6.5, 11.5, 0.6)
pp = tf2.paragraphs[0]; pp.text = "ML in Wireless Networks  \u2022  Project 1  \u2022  Week 1"
pp.font.size = Pt(13); pp.font.color.rgb = RGBColor(0x9F,0xB0,0xC2); pp.font.name = BODY_FONT

# ============================================================ 2. AGENDA
single_slide("=", "Agenda \u2014 Whole-Paper Walkthrough", [
    H("Roadmap", size=16),
    B("1. Introduction & Contributions"),
    B("2. Background: UAS, FANET, Cooperation schemes"),
    B("3. UAV-Based Network Architecture \u2014 roles, AI/ML, RIS, ISAC, MIMO, DT, self-org, spectrum, protocols, security, optimization"),
    B("4. Standardization (3GPP Releases 15\u201318) & Real Testbeds"),
    B("5. Open Issues, Recommendations & Conclusion"),
    B("6. Course Problem Statement & mapping to the paper"),
])

# ============================================================ 3. I + II
std_slide("I", "I\u2013II. Motivation & a 3GPP-Anchored, Cross-Layer Taxonomy",
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
)

# ============================================================ 4. III Background
std_slide("III", "III. Background of Aerial Networking",
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
)

# ============================================================ 5. IV OVERVIEW (dark, node-grid)
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
title_band(s, "IV", "IV. UAV-Based Network Architecture \u2014 13-Area Taxonomy", dark=True)
tax = ["A \u2014 Communication Architectures","B \u2014 Roles of UAVs in Networks",
       "C \u2014 AI/ML in UAV Communications","D \u2014 Generative AI for A2G Channel",
       "E \u2014 Internet of Drones (IoD)","F \u2014 Multi-UAV Architectures",
       "G \u2014 RIS & ISAC UAV Comms","H \u2014 MIMO & Digital Twin",
       "I \u2014 Self-Organization","J \u2014 Spectrum Management",
       "K \u2014 Channel & Protocols","L \u2014 Security & C2",
       "M \u2014 Resource Optimization"]
cw, ch, gx, gy = 1.62, 1.65, 0.22, 0.30
x0, y0 = 0.60, 1.55
for i, t in enumerate(tax):
    r, c = divmod(i, 7)
    cx = x0 + c*(cw+gx); cy = y0 + r*(ch+gy)
    sp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(cx), Inches(cy), Inches(cw), Inches(ch))
    sp.fill.solid(); sp.fill.fore_color.rgb = DARKCARD; sp.line.color.rgb = BLUE; sp.line.width = Pt(1)
    sp.shadow.inherit = False
    tf = sp.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.08); tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.04); tf.margin_bottom = Inches(0.04)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p.text = t
    p.font.size = Pt(11); p.font.bold = True; p.font.name = BODY_FONT; p.font.color.rgb = WHITE
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
tb, tf = add_text(s, 0.6, 6.55, 12.1, 0.6)
p = tf.paragraphs[0]; p.text = "A unified taxonomy bridging academic research, 3GPP standardization, and practical deployment."
p.font.size = Pt(12.5); p.font.italic = True; p.font.color.rgb = AMBER; p.font.name = BODY_FONT

# ============================================================ 6. A-D (2x2 bento)
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
title_band(s, "IV", "IV. Communication, Roles, AI/ML, GenAI (A\u2013D)")
cw, ch, gx, gy = 5.90, 2.55, 0.30, 0.30
x0, y0 = 0.60, 1.50
card(s, x0,            y0,            cw, ch, [
    H("A. Communication Architectures"),
    B("1. Direct links (ISM 2.4/5.8 GHz): simplest, but limited by LoS & range; safety/interference sensitive."),
    B("2. Satellite-based: wide coverage, good for NLoS/remote; but high latency (~0.12 s), heavy antennas, cost."),
    Q("Cellular-connected UAVs offer several appealing advantages\u2026 a win-win case not only for UAVs, but also for cellular networks."),
    B("(a) aerial BS / flying relay = UAV-Assisted Cellular; (b) aerial user = Cellular-Connected UAV.")])
card(s, x0+cw+gx,      y0,            cw, ch, [
    H("B. Roles of UAVs in Networks"),
    Q("UAVs as base stations enables continuity of communications by expanding the communication coverage and acting as protocol converters."),
    B("Challenges: energy optimization, coverage, bandwidth, trajectory/path planning, WPT, security."),
    B("UAV as Relay Station: extends range of existing infrastructure (disaster response, on-demand coverage)."),
    B("UAV as Sensor/Actuator: surveillance, agriculture, forestry; low bandwidth; often onboard processing; can act as data mule.")])
card(s, x0,            y0+ch+gy,      cw, ch, [
    H("C. AI/ML in UAV Communications"),
    B("Optimize trajectories + radio resources jointly (power, spectrum, user association) under non-convex constraints."),
    B("Enhance PHY/MAC: channel estimation, beam/antenna mgmt, interference handling in 3D channels."),
    B("Automate network functions: mobility mgmt, routing, load balancing (single & swarm)."),
    B("Improve security: intrusion/anomaly detection, jamming identification in multi-hop aerial networks.")])
card(s, x0+cw+gx,      y0+ch+gy,      cw, ch, [
    H("D. Generative AI for A2G Channel Modeling"),
    Q("The development and examination of UAV communications critically depend on precise models of electromagnetic propagation."),
    B("Standardized models (3GPP TR 38.901) are terrestrial-calibrated \u2192 inadequate for aerial uptilt paths."),
    B("Data-driven (site-specific) & generative (non-site-specific): TTS-CGAN, MTS-CGAN for spatially consistent modeling."),
    B("Open challenge: spatio-temporal consistency + capturing small-scale fading in generated samples.")])

# ============================================================ 7. E-H (2x2 bento)
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
title_band(s, "IV", "IV. IoD, Multi-UAV, RIS/ISAC, MIMO/DT (E\u2013H)")
card(s, x0,            y0,            cw, ch, [
    H("E. Internet of Drones (IoD) & Middleware"),
    B("IoD treats low-altitude airspace as a limited resource; ZSP (Zone Service Provider) coordinates local UAVs."),
    B("Airspace divided into zones with airways (flight paths) & intersections; nodes for takeoff/land/recharge."),
    B("Middleware gives vendor-independent unified control; simulation env. for resilient protocols.")])
card(s, x0+cw+gx,      y0,            cw, ch, [
    H("F. Multi-UAV Architectures"),
    B("Single-layered vs multi-layered (3D). Gateway view: C1 (star), C2 (leader gateway), C3 (mesh)."),
    B("Leader UAV selected for stability (static leader-follower or distributed leadership)."),
    B("Scalability: star \u2192 mesh \u2192 multi-star / hierarchical mesh."),
    B("Tech maturity: energy optimization = mature; trajectory/path planning = intermediate; security & trust = early stage.")])
card(s, x0,            y0+ch+gy,      cw, ch, [
    H("G. RIS-assisted & ISAC UAV Communications"),
    B("RIS: electronically controllable EM surfaces reflect/enhance signals; mounted on UAVs boosts A2G links."),
    B("6 RIS integration scenarios: data collection, ubiquitous coverage, relaying, PHY security, SWIPT, cellular-connected."),
    B("ISAC: joint sensing + communication \u2014 sensing aids beam tracking; comms aids mapping/positioning.")])
card(s, x0+cw+gx,      y0+ch+gy,      cw, ch, [
    H("H. MIMO & Digital Twin for UAVs"),
    B("MIMO: spectral efficiency via spatial diversity/multiplexing; challenges: pilot contamination, 3D beam tracking."),
    B("Solutions: interference-cancellation pilot decontamination, Kalman-filter channel tracking, dual-functional MIMO."),
    B("Digital Twin: virtual replica (data acquisition \u2192 processing \u2192 application); aligns with 3GPP Rel-15/16/17."),
    B("DT benefit: real-time monitoring, predictive maintenance, path/task adaptation, operator training.")])

# ============================================================ 8. I-M (3+2 bento)
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
title_band(s, "IV", "IV. Self-Org, Spectrum, Channels/Protocols, Security, Optimization (I\u2013M)")
cw3 = 3.84; ch3 = 2.55; gx3 = 0.30; x3 = 0.60; y3 = 1.50
def c3(x, y, items): return card(s, x, y, cw3, ch3, items)
c3(x3,                                   y3, [
    H("I. Self-Organization"),
    B("Ad-hoc network formation in the sky; akin to natural flocking (Reynolds' boids)."),
    B("Recipe: addressing \u2192 neighbor discovery \u2192 formation \u2192 routing.")])
c3(x3+cw3+gx3,                          y3, [
    H("J. Spectrum Management"),
    Q("A major issue is the lack of a dedicated spectrum for commercial drones\u2026 especially for C2."),
    B("ISM (900 MHz, 2.4, 5.8 GHz); FCC considering 5030\u20135091 & 60\u201364 GHz."),
    B("Sharing: Opportunistic / Competitive / Cooperative.")])
c3(x3+2*(cw3+gx3),                      y3, [
    H("K. Channel & Protocols"),
    B("Channel = large-scale (LoS/NLoS) + small-scale (multipath, Doppler)."),
    B("GPU ray-tracing (Sionna RT) for site-specific calibration."),
    B("OSI: PHY (directional), MAC (full-duplex, MPR), Network (AODV/DSR), Transport (PRRT/LRT).")])
cw2 = 4.30; x2 = (13.333 - (2*cw2+gx3))/2; y2 = y3+ch3+gx3
c3(x2,                                   y2, [
    H("L. Security & C2 Requirements"),
    B("C2 modes (TS 22.125): waypoints, stick, UTM-auto, autonomous."),
    B("7 requirements: Confidentiality, Integrity, Non-repudiation, Authentication, Access Control, Availability, Privacy.")])
c3(x2+cw2+gx3,                          y2, [
    H("M. Resource Optimization"),
    B("3D placement: altitude \u2191 LoS but \u2191 path loss; solved via PSO, Genetic Algorithm, CVX, convex hull."),
    B("NOMA, Decode-and-Forward, water-filling, SCA, alternating minimization; graph-based Pareto/dual-ascent.")])

# ============================================================ 9. VI Standardization (timeline)
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
title_band(s, "VI", "VI. Standardization \u2014 3GPP Releases 15\u201318")
rail_y = 3.05
rail = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(rail_y-0.03), Inches(11.33), Inches(0.10))
rail.fill.solid(); rail.fill.fore_color.rgb = BLUE; rail.line.fill.background(); rail.shadow.inherit = False
ms = [("R15","4G LTE for UAVs; aerial-user ID; location/altitude/trajectory reporting; events H1/H2", False),
      ("R16","Remote ID (TR 23.754); UTM interaction; unauthorized-device detection", False),
      ("R17","5G KPIs; UxNB (UAV as gNB); app-layer tracking (TR 23.755)", False),
      ("R18","NR; conditional handover; beam mgmt; multi-antenna; dedicated BS uptilt", True)]
xs = [1.9, 5.1, 8.3, 11.5]
for (lab, desc, hot), x in zip(ms, xs):
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x-0.16), Inches(rail_y-0.16), Inches(0.32), Inches(0.32))
    dot.fill.solid(); dot.fill.fore_color.rgb = (AMBER if hot else BLUE); dot.line.color.rgb = WHITE; dot.line.width = Pt(1.5); dot.shadow.inherit = False
    tb, tf = add_text(s, x-1.35, 1.7, 2.7, 1.1)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p.text = lab
    p.font.size = Pt(18); p.font.bold = True; p.font.name = TITLE_FONT
    p.font.color.rgb = (AMBER if hot else BLUE)
    tb2, tf2 = add_text(s, x-1.35, rail_y+0.25, 2.7, 1.5)
    p2 = tf2.paragraphs[0]; p2.alignment = PP_ALIGN.CENTER; p2.text = desc
    p2.font.size = Pt(10.5); p2.font.name = BODY_FONT; p2.font.color.rgb = INK
    tf2.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
card(s, 0.60, 5.05, 12.13, 1.85, [
    H("Slicing, UUAA & C2"),
    B("UAV Authentication & Authorization (UUAA) via USS."),
    B("C2 comms: direct / network-assisted / UTM-navigated."),
    B("Network Slicing for UAV: NetSliA/B/C per eMBB/URLLC/mMTC; AirSlice framework; SLA-driven slices.")])

# ============================================================ 10. VII Testbeds (2x3 bento)
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
title_band(s, "VII", "VII. Real Testbeds, Deployments & Experiments")
cw_t, ch_t, gx_t, gy_t = 3.92, 2.55, 0.18, 0.30
x_t, y_t = 0.60, 1.50
def tb_card(x, y, items): return card(s, x, y, cw_t, ch_t, items)
tb_card(x_t,                      y_t, [
    H("AERPAW (NSF PAWR)"),
    B("Large-scale SDR platform; RF/I-Q/packet-level emulation; E-VMs as UE/gNB/core; digital twins.")])
tb_card(x_t+cw_t+gx_t,           y_t, [
    H("SkyRAN / SkyCore / SkyHAUL (NEC)"),
    B("Flying LTE RAN, EPC core, self-organizing gigabit multi-UAV network.")])
tb_card(x_t+2*(cw_t+gx_t),       y_t, [
    H("EuroDRONE"),
    B("V2I/V2V UTM testbed with autonomous small UAVs (2.4/5 GHz LTE + Sub-GHz).")])
tb_card(x_t,                      y_t+ch_t+gy_t, [
    H("HITL & SITL Emulators"),
    B("Hardware/Software-in-the-loop; OMNeT++/ns-3/X-Plane (AVENS, CUSCUS, FlyNetSim).")])
tb_card(x_t+cw_t+gx_t,           y_t+ch_t+gy_t, [
    H("Aerial BS Testbeds"),
    B("60 GHz mmWave UAV-BS channel model; LoRa/NB-IoT LPWAN relay; USRP beamforming.")])
tb_card(x_t+2*(cw_t+gx_t),       y_t+ch_t+gy_t, [
    H("Why testbeds matter"),
    B("Turn theory \u2192 deployable aerial networks; validate AI/ML, RIS, ISAC at scale.")])

# ============================================================ 11. VIII Open Issues (2x7 matrix)
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
title_band(s, "VIII", "VIII. Open Research Issues (14)")
issues = ["1 Energy constraint","2 UAV platform & mobility model","3 Routing (dynamic topology)",
          "4 Path planning","5 QoS provisioning","6 Fault handling","7 Data processing (edge/fog)",
          "8 Data sharing & security","9 FANET standardization","10 Distributed optimization",
          "11 Spectrum management","12 Network formation/topology","13 Testing & simulation fidelity","14 Airspace integration"]
cw_i, ch_i, gx_i, gy_i = 1.62, 1.30, 0.22, 0.30
x0i, y0i = 0.60, 1.60
for i, t in enumerate(issues):
    r, c = divmod(i, 7)
    cx = x0i + c*(cw_i+gx_i); cy = y0i + r*(ch_i+gy_i)
    sp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(cx), Inches(cy), Inches(cw_i), Inches(ch_i))
    sp.fill.solid(); sp.fill.fore_color.rgb = CARDFILL; sp.line.color.rgb = BLUE; sp.line.width = Pt(0.75); sp.shadow.inherit = False
    tf = sp.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.10); tf.margin_right = Inches(0.10)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p.text = t
    p.font.size = Pt(11); p.font.bold = True; p.font.name = BODY_FONT; p.font.color.rgb = INK
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE

# ============================================================ 12. VIII Recommendations
std_slide("VIII", "VIII. Recommendations & Further Work",
    [H("Recommendations"),
     B("Multi-UAV systems: steady comms, remote C2, unlimited coverage, adaptive beamforming/directional antennas."),
     B("Routing via Deep RL / hybrid-learning predicting topology dynamics."),
     B("Blockchain-based device lifecycle registration (manufacture\u2192repair\u2192scrap).")],
    [H("Further Work"),
     B("Realistic UAV simulators (energy + flight dynamics); full security frameworks (jamming/spoofing); cognitive-radio spectrum sharing."),
     B("ISAC-enhanced situational awareness; network-slicing-assisted cross-domain architectures."),
     B("Toward 6G / SAGSIN-ready UAV networks.")])

# ============================================================ 13. IX Conclusion (dark)
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
title_band(s, "IX", "IX. Conclusion", dark=True)
card(s, 0.60, 1.55, 12.13, 5.35, [
    HD("What the survey establishes"),
    BD("UAVs enable cooperative, self-organizing missions in unreachable areas."),
    BD("Coverage: communication architecture, protocols, requirements, security; network formation & state-of-the-art solutions."),
    BD("3GPP standardization (Rel-15\u201318) bridges research & commercial deployment; network slicing for UAV."),
    BD("FANET addresses scalability of direct-link networking; communication remains the key constraint."),
    HD("Where it is heading"),
    BD("Open issues + future directions push researchers toward 6G / SAGSIN-ready UAV networks."),
    BD("Convergence of AI/ML, RIS, ISAC, Digital Twins reshapes UAV networking."),
    BD("Standardization + real testbeds (AERPAW, SkyRAN) turn theory into deployable aerial networks."),
    QD("UAV communications has evolved from a niche topic to a key enabler of future wireless connectivity."),
], dark=True)

# ============================================================ 14. Problem Statement (dark)
s = prs.slides.add_slide(BLANK); bg(s, NAVY)
title_band(s, "P", "Course Problem Statement (Week 1)", dark=True)
card(s, 0.60, 1.55, 12.13, 5.35, [
    H("Given problem (verbatim)", AMBER, 15),
    BD("Develop an AI-based system for deploying multiple UAVs as temporary aerial base stations."),
    BD("The system should determine where UAVs should be positioned and how they should move as users move,"),
    BD("while maintaining UAV-to-UAV connectivity, maximizing coverage, and minimizing energy consumption."),
    BD("Input: User locations/density, UAV positions, battery levels, communication range, channel quality."),
    BD("Output: UAV positions/movement decisions and resulting coverage/connectivity."),
    BD("AI/ML: PSO / Genetic Algorithm for placement + Multi-Agent Q-Learning for dynamic formation."),
], dark=True)

# ============================================================ 15. Mapping
std_slide("M", "How the Survey Maps to the Problem",
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
     B("Input/Output matches the paper's resource-optimization loop.")])

DST = r"C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\PPT_content\PPT.pptx"
prs.save(DST)
print("Saved. Total slides:", len(prs.slides._sldIdLst))
