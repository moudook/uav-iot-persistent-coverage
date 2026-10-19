# TECHNICAL BACKING — THE ACTUAL PAPER CONTENT BEHIND EACH SLIDE
# This is not a summary of summaries. This is the technical substance.
# For each slide: the specific formulations, algorithm mechanics, contrasts, and analysis from the paper.

# ============================================================
# SLIDE 1 — Title
# ============================================================
# PPT: "A Survey on Unmanned Aerial Vehicles (UAVs) Communications", "first to integrate academic + 3GPP", "13-area taxonomy"
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# The paper's core thesis is that prior UAV surveys are siloed — they cover either academic research OR 3GPP standards OR specific technical areas. This survey is the first to connect all three.
#
# Market numbers (Abstract): $17.31B in 2024 → $32.95B by 2030. This is not just growth — it's the specific CAGR that justifies why this survey matters NOW. The market is doubling in 6 years, and 3GPP is actively standardizing (R15 done, R18 in progress).
#
# The 13-area taxonomy (Figure 1) is the paper's MAIN contribution, not an outline. The paper explicitly says: "The paper introduces a unified taxonomy that incorporates emerging paradigms such as Digital Twins (DT), Reconfigurable Intelligent Surfaces (RIS), and Integrated Sensing and Communications (ISAC)." These are not buzzwords — they are specific technologies with specific 3GPP alignment (DT: Rel-15/16/17, RIS: 6G, ISAC: 6G).
#
# The cross-layer claim: "holistic, cross-layer analysis of UAV communication and networking, encompassing physical, data link, network, and transport layers—unlike prior surveys that focus on isolated layers or specific use cases." This means the paper connects:
# - PHY: channel models (TR 38.901, TTS-CGAN)
# - MAC: protocols (full-duplex, MPR, directional antennas)
# - Network: routing (AODV, DSR, Q-learning-based)
# - Transport: protocols (PRRT, LRT, MPTCP)
# And shows how they interact — a systems view that prior surveys lacked.
#
# The 6G/SAGSIN positioning: "UAVs have the potential to boost coverage and dependability and enable energy efficient 6G wireless networks as a vertical component." The paper explicitly frames UAVs as a 6G vertical, not a 5G add-on. SAGSIN = Space-Air-Ground-Sea Integrated Network.
#
# THE DEEP INSIGHT: The paper is not a literature review — it's a systems paper that argues UAV communications is a single coherent problem spanning physics → protocols → standards → applications. The 13-area taxonomy is the proof that this problem can be organized and understood systematically.

# ============================================================
# SLIDE 2 — Agenda
# ============================================================
# PPT: 6 sections
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# The agenda mirrors the paper's section structure, which is a DEPENDENCY CHAIN, not just an outline:
#
# I (Intro) → II (Contributions) → III (Background) → IV (Architecture) → V (Design) → VI (Standardization) → VII (Testbeds) → VIII (Open Issues) → IX (Conclusion)
#
# Why this order matters:
# - Section III provides the PHYSICAL CONSTRAINTS: 3D mobility, LoS dependency, battery limits
# - Section IV uses those constraints to define 13 DESIGN AREAS
# - Section V dives into TECHNICAL DETAILS of each area (protocols, algorithms, security)
# - Section VI shows what 3GPP ACTUALLY RATIFIED (vs. what's just research)
# - Section VII validates which designs WORK IN PRACTICE (testbeds)
# - Section VIII identifies where THEORY and PRACTICE DIVERGE (open issues)
#
# THE DEEP INSIGHT: The paper's structure is a thesis argument: physics constrains architecture, architecture constrains protocols, protocols get standardized, testbeds validate, gaps remain. Our project must navigate this entire chain.

# ============================================================
# SLIDE 3 — Motivation & Contributions
# ============================================================
# PPT: MANET failed, 3D mobility, reliable links essential, 3 contributions
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# The fundamental break from ground networking (Section I, exact quote):
# "In the early phases, Mobile Ad-hoc Network (MANET) wireless policies were adopted in aerial networking but failed due to rapidly changing topology, fast mobility, and three-dimensional free space movements. Indeed, UAVs are characterized by greater degrees of mobility and freedom in the 3D space, which makes a big difference in the context of aerial networks in comparison to ground networks and results in a more dynamic and rapidly changing network topology."
#
# This is NOT a qualitative statement — it invalidates specific MANET/VANET protocol assumptions:
# 1. Routing convergence time: MANET protocols assume topology changes are slower than routing convergence. In FANETs, the graph can reconfigure completely in seconds — faster than AODV/DSR can discover new routes.
# 2. Link lifetime: MANET links last minutes. FANET links at aerial speeds last seconds. This breaks distance-vector protocols that rely on stable next-hop assumptions.
# 3. MAC backoff: 802.11 DCF backoff intervals tuned for ground mobility cause excessive collisions at aerial speeds because the channel state changes between backoff and transmission.
# 4. 3D asymmetry: MANET/VANET assume 2D movement. FANETs have vertical dimension, creating asymmetric link directions that invalidate bidirectional link assumptions in routing protocols.
#
# Communication prerequisite (exact quote): "A reliable wireless communication link between swarms of drones and ground base stations (BS) is essential to automate the aerial network, e.g., Flying Ad-hoc Networks (FANETs)."
# "Essential" = prerequisite, not feature. Without reliable links, UAVs are just expensive flying cameras. Communication is the enabler of autonomy.
#
# Three contributions with SPECIFIC gaps filled:
# 1. Holistic cross-layer: "encompassing physical, data link, network, and transport layers—unlike prior surveys that focus on isolated layers or specific use cases." Prior surveys ([5], [6], [7], [8]) covered: 5G/6G-enabled UAVs, channel modeling, routing/handover. This one covers ALL of them AND connects them across layers.
# 2. First to integrate academic + 3GPP: "first to systematically integrate both academic research and industry perspectives, with a strong emphasis on 3GPP standardization (Releases 15 to 18)." "Systematically" means each of the 13 areas has explicit 3GPP cross-references — not just a standards appendix.
# 3. Unified taxonomy with DT/RIS/ISAC: "incorporates emerging paradigms such as Digital Twins (DT), Reconfigurable Intelligent Surfaces (RIS), and Integrated Sensing and Communications (ISAC)." These are positioned as the future directions with specific 3GPP alignment, not afterthoughts.
#
# THE DEEP INSIGHT: The MANET failure is not historical trivia — it's the reason EVERY protocol in this course must be designed for 3D mobility from first principles. You cannot use AODV or DSR "out of the box"; they need modification for FANET dynamics. The cross-layer claim means our placement algorithm (PHY layer) must consider routing constraints (network layer) and energy constraints (system layer) simultaneously — this is a non-convex optimization problem, not sequential optimization.

# ============================================================
# SLIDE 4 — Background
# ============================================================
# PPT: UAS 5 components, FANET backbone UAV, 6 building blocks, cooperation schemes, UAV types
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# UAS 5 components (Section III-A, exact definitions):
# 1. UAV: "air vehicles that satisfy the requirements of flight air vehicles. The operation theater, capacity and performance of the UASs affect UAVs' abilities, including endurance, range, altitude, payload, etc."
# 2. GCS: "a portable ground control terminal or air traffic control station that facilitates the interaction between UAVs and humans."
# 3. Payload: "equipment is added to UAVs to fulfill specific mission objectives, including camera, radar, sensor, and communications equipment."
# 4. Control & data links: "all the equipment including hardware (HW) and software (SW) that contributes to sending and receiving any type of information both from and to the system itself and other external actors, as well as the UAVs and GCS."
# 5. Support system: "provides flight speed to UAVs (and potentially other data, if needed) within a very short space of time."
#
# The GCS is explicitly a single point of failure (Table 8 security analysis). The control and data links are the security perimeter — "the equipment... that contributes to sending and receiving any type of information."
#
# FANET backbone UAV: "one of the UAVs, a.k.a. the backbone UAV, must be connected to a ground control station (GCS), a satellite, or any other core command and control station. With such a mechanism, the geographical coverage grows extensively, but such advantages come with a price and challenges."
# The backbone UAV is the gateway — if it fails, the entire network loses connectivity to the internet. Single point of failure at the network layer.
#
# FANET building blocks with specific interdependencies:
# - Network Topology: "critical parameter... ensure mutual connectivity among and with the command control station. However, the geographical position of each flying node in a FANET changes rapidly at high speed compared to its peers from MANETs, VANETs or nodes in any ground network, causing major communication problems."
# - Mobility Model: "3D trajectories of each UAV—including its position, velocity and acceleration—evolve dynamically over time." This is fundamentally different from ground mobility models which are 2D.
# - Node Density: "nodes in a FANET are scattered in the sky, and thus node density is much lower than in MANETs and VANETs." Lower density means sparser connectivity, different routing dynamics.
# - Radio Propagation: "predict link quality and reliability among different flying nodes with varying speeds, velocities, and positions, as well as with the command and control station, either in LoS or NLoS."
# - Power: "extra payloads attached to UAVs also contribute to battery drainage... recommended by industrial experts to avoid such practices."
# - Localization: "the loss of a flying node may expose the entire mission to information to any unwanted entity."
#
# Cooperation schemes — hierarchy of constraint tightness:
# - Physical coupling: "UAVs are physically connected and the motions of each UAV highly depend on the movement of other UAVs." Mechanical linkage — if one moves, all must compensate.
# - Formations: "flying in a specific pattern and make a particular shape e.g. star shape, rectangle, also these UAVs maintain the distance, speed and acceleration from each other." 500-drone show example: works because of "reliable coordination among pre-programmed UAVs."
# - Swarms: "homogeneous teams of many UAVs interact with each other to generate collective global behaviors. The global behaviour of UAVs create more adoptable, robust and reliable to the dynamic environment, this is mainly because of its decentralized communication approach."
# - Intentional cooperation: "each UAV in a team is allocated a set of tasks of a global mission, and then the movements of UAVs of the team follows predefined trajectories of individual tasks where two types of control architectures are applicable either centralized or decentralized."
# - Regime-switching: "modern UAV missions increasingly operate in hybrid and adaptive modes, where a fleet may dynamically transition between these regimes during different mission phases. The taxonomy adopted in this work should therefore be interpreted as a classification of dominant control and coordination structures at a given time-scale, rather than as rigid mission categories. In this sense, hybrid UAV operations can be formally modeled as regime-switching systems."
#
# UAV type trade-offs:
# - Fixed-wing: "high speed, longer endurance, greater stability and heavy payload, mostly used for large scale applications e.g. border surveillance. Unfortunately, these UAVs can only fly forward and require ample space to execute large, sweeping turns when changing direction for instance 360° turn. Hence, this category of UAVs is not suitable for stationary mission such as close inspection."
# - Rotary-wing: "able to change direction quickly, as well as to hover, take off and land vertically. However, rotary-wing UAVs also have limitations such as low speed, limited mobility and reduced payload."
# - Hybrid/VTOL: "combination of both fixed and wing rotary-wings which provide the facility of vertical Takeoff and Landing (VTOL)."
#
# THE DEEP INSIGHT: The 5 UAS components define the system boundary and attack surface. The FANET building blocks are NOT independent — they form a coupled system where node density affects routing complexity, mobility affects topology change rate, and radio propagation affects link reliability. Regime-switching means our project must support dynamic transitions between cooperation modes, not just static formations. The UAV type selection is a fundamental engineering trade-off: endurance vs hover capability vs complexity.

# ============================================================
# SLIDE 5 — Taxonomy Overview
# ============================================================
# PPT: 13 areas A-M
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# The taxonomy (Figure 1) is a layered dependency DAG. Each area depends on the areas below it:
#
# Layer 1 — Foundation: A (Communication Architectures)
# Three architectures with specific failure modes:
# - Direct links: LoS-dependent, ISM band, safety/interference sensitive
# - Satellite: 0.12s latency, heavy antennas, weather-affected, bandwidth-limited
# - Cellular-connected: only architecture with 3GPP alignment, but creates uplink interference to ground UEs
#
# Layer 2 — Roles & Intelligence: B (Roles), C (AI/ML)
# B depends on A: cannot define roles (BS, relay, sensor) without communication architecture.
# C depends on A and B: "Optimize trajectories and radio resources jointly (e.g., transmit power, spectrum allocation, user association) under complex and often non-convex constraints." NOT sequential optimization — joint optimization because variables are coupled.
#
# Layer 3 — Channel & Environment: D (GenAI), E (IoD), G (RIS/ISAC), H (MIMO/DT)
# D depends on A and C: channel models feed into ML-based PHY algorithms. 3GPP TR 38.901 is "terrestrial-calibrated" — fails for aerial uptilt paths. TTS-CGAN/MTS-CGAN generate p(x|u,c) for spatially consistent RSS sequences.
# E depends on A and B: airspace management requires communication and defined roles. ZSP coordinates local UAVs; cyber-physical environment divided into zones with airways and intersections.
# G depends on C, D, H: "RIS–UAV co-design introduces high-dimensional coupling between mobility and beamforming, requiring real-time trajectory updates." Six scenarios: data collection, ubiquitous coverage, relaying, PHY security, SWIPT, cellular-connected.
# H depends on A, C, D: MIMO pilot contamination worse for aerial users because "aerial users see many more base stations as LoS interferers." DT aligns with 3GPP Rel-15/16/17 because those releases introduced data models and edge computing.
#
# Layer 4 — Network Intelligence: I (Self-Org), J (Spectrum), K (Protocols)
# I depends on F (multi-UAV): cannot self-organize without multi-UAV architecture. Reynolds' boids: separation, alignment, cohesion. But "this similarity is limited by wireless link qualities, which are related to factors such as channel fading, communication delay, and protocol overhead."
# J depends on A and G: spectrum access constrained by physical layer and RIS. "A major issue is the lack of a dedicated spectrum for commercial drones… especially for C2." RTCA allocated for medium/large UAVs, but NO band for small commercial UAVs.
# K depends on A, I, J: protocols implement communication, self-organization, spectrum management. "The protocols of FANET need to adopt the dynamic topology, changing link qualities, the high mobility of UAVs and their limited power issues."
#
# Layer 5 — Security & Optimization: L (Security), M (Optimization)
# L depends on J, K, F: 7 security requirements (C, I, Non-repudiation, Auth, Access Control, Availability, Privacy). "GCS and Backbone UAV each have a single point of failure, resulting in reduced availability."
# M depends on everything: mathematical synthesis layer. "3D placement: altitude ↑ LoS but ↑ path loss; solved via PSO, Genetic Algorithm, CVX, convex hull."
#
# THE DEEP INSIGHT: The taxonomy is a dependency DAG, not a list. Understanding the dependencies tells you what to design first. For our project: need A before B, B before C, all before M. The spectrum gap (no dedicated C2 band) is a hard constraint forcing ISM band usage. The optimization layer (M) is the mathematical synthesis of everything below it.

# ============================================================
# SLIDE 6 — A-D: Communication, Roles, AI/ML, GenAI
# ============================================================
# PPT: 3 architectures, 3 roles, AI/ML for joint optimization, GenAI for channel
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# Section A — Communication Architectures with SPECIFIC failure modes:
# 1. Direct links (ISM 2.4/5.8 GHz): "limited by LoS & range; safety/interference sensitive." Paper: "this simple architecture is typically sensitive to safety and interference issues, which may make it difficult to legitimately monitor and manage." Extending beyond LoS "introduces complexities related to delays, data rates, safety, and interference concerns."
# 2. Satellite: latency ~0.12s (specific from Inmarsat Swiftbroadand), heavy antennas, high cost. "this solution is often associated with an excessive operation cost and introduces constraints during large-scale deployment on consumer-scale applications. Finally, satellite transmissions are often affected by rain, snow, and other precipitations and their scalability... may be questionable since there is short supply of bandwidth resources."
# 3. Cellular-connected: "Cellular-connected UAVs offer several appealing advantages… a win-win case not only for UAVs, but also for cellular networks." The win-win is NOT obvious — UAVs at altitude create uplink interference to ground UEs directly below. Benefit to cellular: new revenue streams and use cases (events, disaster response). Two variants: UAV-Assisted Cellular (UAV as BS/relay) vs Cellular-Connected UAV (UAV as UE).
#
# Section B — Roles of UAVs with SPECIFIC challenges:
# 1. Base Station: "enables continuity of communications by expanding the communication coverage and acting as protocol converters (whenever required)." Challenges: energy optimization, communication coverage, bandwidth optimization, trajectory and path planning, WPT, wireless security.
# 2. Relay Station: "primarily to extend the communication range of an already available communication infrastructure." In contrast to base stations, this "aims only to extend communication from an already available communication infrastructure." Challenges: communication relaying, relay positioning, throughput maximization, trajectory or power optimization.
# 3. Sensor/Actuator: "most of the typical applications... are not bandwidth-intensive, rather they rely on enhanced communication range and prolonged duration of operations." "Sometimes, the UAVs may be enablers for ground-based sensor and actuator networks, or may act as data mules."
#
# KEY INSIGHT — Maturity Assessment with SPECIFIC gaps:
# "From a technological maturity perspective, we distinguish between challenges that are relatively mature at the algorithmic level and those that remain open from a system and deployment perspective."
# - Energy optimization: MATURE — "supported by numerous analytical models and optimization frameworks for UAV base stations and relaying systems. These contributions provide robust theoretical tools for addressing energy-aware deployment, mobility control, and power management. However, important gaps remain in terms of real-world implementation, particularly with respect to real-time decision making, uncertainty in energy profiles, battery behavior, and integration with onboard control systems."
# - Trajectory/path planning: INTERMEDIATE — "significant body of deterministic and learning-based approaches for UAV mobility and coverage optimization. Nonetheless, their effectiveness in complex, large-scale, and safety-critical operational scenarios is still not fully established."
# - Security and trust: EARLY STAGE — "Existing efforts mainly build upon traditional communication security paradigms, while comprehensive defenses against spoofing, jamming, coordinated attacks, and adversarial swarm behaviors are still largely open research problems."
#
# Section C — AI/ML with SPECIFIC application domains:
# 1. "Optimize trajectories and radio resources jointly (e.g., transmit power, spectrum allocation, user association) under complex and often non-convex constraints"
# 2. "Enhance physical and medium access control layer performance, including channel estimation, beam/antenna management, and interference handling in dynamic 3D channels"
# 3. "Automate network-level functions such as mobility management, routing, and load balancing for single UAVs and UAV swarms"
# 4. "Improve security and resilience (e.g., intrusion and anomaly detection, jamming identification) in vulnerable multi-hop aerial networks"
#
# Section D — GenAI for Channel Modeling with SPECIFIC gap:
# Core problem: "The development and examination of UAV communications critically depend on precise models of electromagnetic propagation." 3GPP TR 38.901 is "terrestrial-calibrated" — designed for ground users looking up at base stations. Aerial users look down at steep uptilt angles. "3GPP channel models, partly rooted in terrestrial measurements which significantly differ from aerial contexts, especially in the mmWave bands, are not adequately calibrated. Additionally, these models, originally designed for BSs targeting ground users, fail to replicate the characteristics of specialized uptilted deployments aimed at UAV pathways, such as those on rooftops."
# TTS-CGAN/MTS-CGAN: "specifically depicts the large-scale channel behavior as the local-average received signal strength (RSS) of a UAV navigating typical urban trajectories." Conditional distribution p(x|u,c) where xk is channel parameters for trajectory k, uk is distance evolution. "additional efforts are needed to incorporate small-scale fading and thereby deliver a complete multipath channel response, including path gains, delays, and angles, which are essential for crafting site-specific deployments and for the development and validation of AI/ML-based multi-antenna PHY algorithms."
#
# THE DEEP INSIGHT: The three architectures have specific failure modes — not interchangeable. For our project, cellular-connected is the only 3GPP-aligned option. Maturity assessment tells us: use existing energy algorithms, use trajectory planning with caution (intermediate maturity), expect to contribute new security solutions (early stage). AI/ML demands joint optimization, not sequential — our placement and movement algorithms must be coupled, not independent. Channel modeling gap means we cannot use 3GPP TR 38.901 directly for aerial users — we need site-specific or generative models for PHY validation.

# ============================================================
# SLIDE 7 — E-H: IoD, Multi-UAV, RIS/ISAC, MIMO/DT
# ============================================================
# PPT: IoD with ZSP, multi-UAV architectures, RIS/ISAC, MIMO/DT
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# Section E — Internet of Drones (exact technical content):
# "Coordination of access to UAVs in a regulated airspace is made possible by the emerging Internet of Drones (IoD). Among other aspects, IoD encompasses protocols that introduce the idea of treating the airspace, especially the low-altitude one, as a limited resource." This is airspace management, not just networking.
# ZSP: "the former ensures coordination between local UAVs, while the latter characterizes the backbone of the IoD ground communication infrastructure." Cyber-physical environment divided into zones with airways and intersections. "By leveraging regulated flight paths, drones are capable of accessing nodes, which represent specific points of interest. These nodes allow drones to perform various actions such as takeoff, landing, recharging, or engaging in missions."
# Critical safety requirements: "the drone is able to continuously broadcast its coordinates in order to be led by ZSP and guarantee that its intended trajectory and actions follow the mission plan. On the contrary, the ZSP is responsible for relaying control information from remote services, as well as ATC and weather updates. Furthermore, the ZSP must be capable of dealing with emergency situations, including the possibility that a drone would be unable to continue its journey due to hardware and/or software faults, sudden power loss, or uncontrolled flight."
# Middleware: "propose middleware solutions to provide a unified control structure that are vendor-independent. In this way, the entire software stack becomes predictable by UAV providers and operators to ease drone provisioning, their remote control, and ensure that all relevant mission-critical algorithms are provided."
#
# Section F — Multi-UAV Architectures (exact technical content):
# Architectures (Fig. 3):
# - A1: single-layered, A2: multi-layered 3D deployment
# - C1: star topology (central leader/gateway) — single point of failure at leader
# - C2: leader gateway (designated leader UAV) — leader is communication gateway to external entities
# - C3: mesh topology (no single gateway, fully/partially connected) — resilient to single node failure
# Leader selection: "static leader-follower [119], [120] and distributed leadership [121]." "for the sake of ensuring architectural stability and to primarily maintain the physical formation of the UAVs, ideally a leader UAV is selected as shown by configuration C2. The leader acts as the communication gateway of each layer with external entities (outside the layer) as well as decides formation controls and UAV placements."
#
# Maturity assessment with SPECIFIC gaps:
# - Energy optimization: MATURE — analytical models exist, but "important gaps remain in terms of real-world implementation, particularly with respect to real-time decision making, uncertainty in energy profiles, battery behavior, and integration with onboard control systems."
# - Trajectory/path planning: INTERMEDIATE — "deterministic and learning-based approaches exist, but their effectiveness in complex, large-scale, and safety-critical operational scenarios is still not fully established."
# - Security and trust: EARLY STAGE — "comprehensive defenses against spoofing, jamming, coordinated attacks, and adversarial swarm behaviors are still largely open research problems."
#
# Section G — RIS/ISAC (exact technical content):
# RIS: "electronically controllable EM materials that can be electronically controlled. By controlling how radio waves interact with objects that are coated with reconfigurable EM layers, telecommunication operators are able to provide continuous connectivity and high quality of service (QoS) for users. The mounting of RIS on UAVs has the great potential to improve UAV communication performance."
# Six scenarios (You et al. [135]) with SPECIFIC mechanisms:
# 1. Data collection: more RIS elements → higher data collection rates, less hovering time
# 2. Ubiquitous coverage: extend reachability to ground users not covered by UAVs
# 3. Data relaying: near terrestrial gateway → increases backhaul capacity of air-ground channels
# 4. PHY security: mitigate eavesdropping attack from malicious ground users
# 5. SWIPT: low energy consumption, improve efficiency of information-and-power transfer
# 6. Cellular-connected: alleviate interference between UAVs and non-associated base stations
# Key technical challenge: "trajectory planning must increasingly account for fast-varying channel geometry and learning-driven adaptation; for example, the multi-threaded federated optimization framework in [137] shows that RIS–UAV co-design introduces high-dimensional coupling between mobility and beamforming, requiring real-time trajectory updates."
#
# ISAC: "On one hand, sensory data of a UAV's location, velocity and channel environment can be used to mitigate interference, reduce the delay of beam tracking, and improve the communication performance. On the other hand, wireless signals of UAVs can be used to detect and avoid obstacles, reconstruct the environment 3D map and improve positioning accuracy."
# Key challenge: "continuous sensing and communication can consume a lot of battery power, and co-channel interference may occur when UAVs provide both communication services and radar sensing." Chang et al. [140]: "joint scheduling method for sensing, communication and control for UAV communications with mmWave/THz interfaces."
# Paper's conclusion: "By using ISAC technology, we can push the physical limits of UAVs and enable them to adapt reliably, agilely, and efficiently to complex as well as extreme environments."
#
# Section H — MIMO/DT (exact technical content):
# MIMO challenges: "pilot contamination and 3D beam tracking." Huang et al. [147]: "interference-cancellation-based pilot decontamination and Kalman-filter-based channel tracking, to maintain reliable aerial links." Why worse for UAVs: "aerial users see many more base stations as LoS interferers" — more interferers than ground users.
# Digital Twins: "virtual replicas of physical systems that use data from sources like Internet of Things (IoT) to model, monitor and improve network performance in real time. Their operation involves three primary steps: data acquisition, data processing, and data application."
# 3GPP alignment: "Release 15 marked the first substantial efforts to connect UAVs via 3GPP networks... Release 16 built upon these advancements by introducing further support for UAV communication, including network slicing and edge computing capabilities... Release 17 introduced enhancements for non-terrestrial networks (NTNs)."
#
# THE DEEP INSIGHT: IoD is not just networking — it's airspace management with safety-critical requirements. The ZSP is both a network entity and an air traffic controller. The middleware requirement is critical: without vendor-independent control, we cannot integrate heterogeneous UAVs. RIS/ISAC represent the cutting edge — our project should be designed to accommodate these future enhancements. MIMO pilot contamination is a real problem for aerial base stations. Digital Twins are on the 3GPP roadmap — our system should be designed with DT data interfaces in mind.

# ============================================================
# SLIDE 8 — I-M: Self-Org, Spectrum, Protocols, Security, Optimization
# ============================================================
# PPT: boids self-org, spectrum gap, protocol stack, 7 security reqs, optimization methods
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# Section I — Self-Organization:
# Reynolds' boids: "Craig Reynolds captured the essence of flocking. Later, he modelled and simulated flocking behavior with the help of agents which he named boids. Reynolds defined flocking as an interaction of individual agents, adhering to a set of three simple rules for separation, alignment, and cohesion."
# Paper's caveat: "this similarity is limited by wireless link qualities, which are related to factors such as channel fading, communication delay, and protocol overhead." The boids model assumes perfect sensing; in FANETs, links are lossy and delayed.
# Self-organization recipe (implementation sequence — NOT optional):
# 1. Aerial node addressing: "Leverage existing standards from IEEE, FAA remote drone identification... to establish an addressing scheme that supports unicast, multicast and broadcast schemes"
# 2. Neighbor discovery: "Develop a strategy for discovering neighboring UAVs that are within the communication range"
# 3. Network formation: "Enable mechanisms for aerial nodes to join and leave the network in a dynamic fashion"
# 4. Path planning and routing: "Provide support for efficient strategies for path planning and routing between any pair/group of UAVs interested in sharing real-time information."
# Critical note: "the creation and maintenance of ad-hoc networking of UAVs is an extremely challenging task, primarily due to the high mobility of UAVs. Hence, in the real-world, UAV networks are usually augmented through some form of partial infrastructure such as satellite or cellular networks."
#
# Section J — Spectrum Management (exact technical content):
# Spectrum gap: "A major issue is the lack of a dedicated spectrum for commercial drones, which would have helped, especially in a context where reliable operation, safety and security of drone operations highly rely on their spectrum access, in particular for command and control communication."
# Current allocation: "Commercial UAVs primarily operate on the ISM bands (900MHz, 2.4 GHz and 5.8GHz) for C2 and payload communications. While the 900MHz-band offers favorable propagation characteristics for aeronautical communications, it cannot support high data transmission rate for payload communications. On the other hand, the 2.4GHz and 5.8GHz bands suffer from spectrum congestion and short communication range, particularly in urban areas."
# What's being considered:
# - FCC 5030-5091 MHz: "FCC report published in August 2020 concluded the suitability of the 5030-5091 MHz band for UAV operations and recommended developing service and licensing rules"
# - FCC 60-64 GHz: "FCC is considering the use of 60-64 GHz band for drone operations with unlicensed field disturbance sensors to be used by collision avoidance systems"
# - RTCA: "allocated a dedicated spectrum for C2 communications to medium and large UAVs, however, no spectrum band has been yet allocated to small commercial UAVs"
# - 960-1164 MHz: raises concerns for AMS(R)S
#
# Three sharing schemes with SPECIFIC trade-offs:
# 1. Opportunistic: "UAVs are secondary unlicensed users... requires considerable energy consumption at the UAVs to search for the spectrum holes... Noting the rapid movement of UAVs, the spectrum sensing measurements may become quickly invalid as UAVs move to new locations." → Fast movement invalidates spectrum predictions.
# 2. Competitive: "unlicensed users placing bids for getting spectrum access from single or multiple competing sellers using one of existing spectrum auction mechanisms" → Requires market infrastructure.
# 3. Cooperative: "primary users coordinate with the spectrum seekers (e.g., UAVs) to share with them a portion of their spectrum access... can guarantee an orthogonal (interference-free) spectrum sharing mechanism. However, these schemes often involve an overhead signaling for coordination and require knowledge of users' locations and their instantaneous CSI levels." → Requires coordination overhead and CSI knowledge.
#
# Section K — Channel & Protocols (exact technical content):
# PHY layer: "The physical layer is related to hardware aspects of the network like voltage and power control for the network hardware devices, establishing their inter-linking, encoding, decoding, modulation, demodulation, accessing the physical medium and transmitting on it. In FANETs, the link characteristics are impacted by the form physical dimensions of UAVs and their onboard limited power batteries. Out of service UAVs might lead to session expiry and frequent network partitioning. Efficient algorithms bring the transmission power requirement to an optimum level to maintain the connectivity."
# Specific PHY solutions:
# - Directional antenna with lightweight woodpile reflector: "effectively addresses the co-channel interference between UAVs and the ground station. The lightweight woodpile reflector not only maintains the antenna radiation performance but also extends the flight time of the UAV, resulting in contributing to the widespread of long life UAV-aided wireless networks."
# - Energy harvesting from drone vibrations (ref [198])
# - Beaconing period scheduling via game theory (ref [199])
# - Sleep and Rate-adaptation: "power optimization by switching network interfaces to sleep mode during short idle timings"
#
# MAC layer: "The high mobility and varying distances and direction between UAV nodes continuously change the network architecture in a FANET system, which directly impacts on the design of the FANET media access control (MAC) layer." Key technologies: "Full-duplex radio and multi-packet reception (MPR) and directional antenna are promising technologies for improving the performance of the MAC protocols in FANET systems."
# Specific MAC protocols:
# - Multi-channel MAC for safety packets (ref [201])
# - Energy-efficient location-aware MAC (ref [202])
# - Cooperative MAC with relay mode selection (ref [203])
#
# Network layer: "The traditional route discovery process cannot fully explore the most connected and durable paths, which result in frequent link failure and high overhead seriously affect the data transmission." Specific solutions:
# - ECaD: energy-efficient routing (ref [214])
# - Cross-layer AODV with Glow Swarm Optimization CH selection (ref [215])
# - Adaptive Q-learning for topology change detection (ref [206])
# - EE-Hello: energy-efficient hello interval (ref [207])
# - Joint Topology Control and Routing (JTCR): two-phase topology control (ref [205])
#
# Transport layer: "A transport protocol for FANETs requires these features: reliability, congestion control and flow control. In a UAV network, congestion is commonly caused by the high speed motion of UAV nodes and varying traffic rates. If a transient link is possibly unstable, the TCP congestion control should not be run unless lower speed transmission is required."
# Specific solutions:
# - PRRT: "latency-aware and -predictable communication with open protocol stacks for remote drone control"
# - LRT: "low-latency reliable transport solution for network-connected UAV" using network coding
# - MPTCP adaptive offloading (ref [219])
# - MpQUAD: multipath QUAD congestion control (ref [220])
# - Adaptive TCP slow-start (ref [221])
#
# Section L — Security (exact technical content):
# "UAVs are cyber-physical systems (CPS) with unique natural characteristics such as small size, manoeuvrability and maintenance, which make them more vulnerable to cyber attacks. These attacks often target UAVs' physical and software components."
# 7 requirements with specific attack vectors:
# 1. Confidentiality: "UAV nodes in FANET systems require security mechanisms to mitigate information exposure. It is also important to hide the information exchange within the FANETs, for example, outside nodes should not know what a FANET is going to execute."
# 2. Integrity: "ensures that the FANET has adequate security mechanisms to guarantee that the transferred information has not been intentionally or unintentionally altered."
# 3. Availability: "The nodes in FANETs can be jammed, thereby bringing the network down. Further, most FANET nodes depend on GNSS; GNSS jamming poses a threat to availability. Denial-of-service attacks can be mitigated through frequency-hopping mechanisms. Further, the IMU based navigation is also used."
# 4. Privacy: "The nodes in FANET are required to keep the identification information and also the transactions... Data privacy – protecting sensitive information; Protection of Routing and/or protocol information – strategies to protect user privacy while enabling collaboration among flying nodes; Application and position privacy – where the exchange of information between nodes and their status/relative position is protected."
# Key insight: "GCS and Backbone UAV each have a single point of failure, resulting in reduced availability. Similarly, DoS, Flooding attacks, and Backdoor malware can result in a lack of availability."
# Specific mechanisms:
# - HECC for MAC layer access control (ref [228])
# - DLSMR: deep learning-based secure multicast routing (ref [229])
# - Blockchain-based key management for heterogeneous FANET (ref [234])
# - ACBFT: adaptive chained Byzantine fault-tolerant protocol (ref [237])
#
# Section M — Resource Optimization (exact technical content):
# Algorithm taxonomy:
# 1. Centralized/distributed: "algorithms addressing the various challenges associated with UAVs are evaluated on a small scale using a centralized approach. However, for scalability reasons it is more suitable to design distributed algorithms."
# 2. Convex/non-convex: "convex problems are simpler to analyze and solve than non-convex optimization problems, although they can be NP-hard. At last, the advantage of these tools is that they provide theoretical guarantees and optimality gaps."
# 3. Heuristic/Meta-heuristic: "heuristic approaches are related to the problem at hand, while meta-heuristics exploit different evolution mechanisms and operators providing a high level of abstraction."
# 4. Graph-theoretic-based: "interactions that occur in the investigated problems can be modeled by static or dynamic graphs. Furthermore, the vast majority of studies use (static) graph theory to represent and model them."
# 5. Online/offline: "Online algorithms arise in any situation in which decisions must be made and resources allocated without knowing the future requests. In contrast, an offline algorithm takes decisions and allocates resources based on a full knowledge of the requests."
#
# Specific 3D placement algorithms:
# - PSO (Alzenad et al. [95]): "3-D placement of an unmanned aerial vehicle base station (UAV-BS) for energy-efficient maximal coverage." Nonlinear integer problem, solved using CVX.
# - CVX baseline: "find the optimal 2D and 3D coordinates in a decoupled way"
# - 3D random geometric graphs + PSO (ref [245]): "effective iterative algorithm... placement of each AP to be a different optimization problem. As a result, they can be placed sequentially"
# - Genetic Algorithm (ref [246]): "genetic algorithm-based evolutionary optimization technique for a similar problem to maximize users' QoS requirements"
# - Branch-and-bound (ref [247]): "exact and realistic mathematical model... to increase user connectivity in a geographically designated area while deploying as few UAVs as possible... solved by leveraging the branch and bound solution method. A simple heuristic is also suggested... exhibiting linear complexity."
# - Spiral-based convex hull (ref [248]): "strategy for optimizing UAVs-MBs, utilizing the convex hull algorithm... for providing GUs wireless coverage."
# - Alternating minimization (ref [110]): "joint trajectory and power optimization for UAV relay networks was framed using a non-convex optimization framework to minimize the outage probability. A tractable decomposition gradient-descent algorithm was suggested... In this procedure, the path of UAVs is optimized first, and then the resulting power control is iterative until the convergence criteria are met."
# - Graph-based: Dijkstra with Pareto principle (ref [108]), dual-ascent bounded by UAV cardinality (ref [108])
# - Distributed first-order methods (ref [253]): "optimize the UAV swarm positions to achieve the highest gain under a line-of-sight MIMO backhaul"
#
# THE DEEP INSIGHT: The spectrum gap is a HARD CONSTRAINT: no dedicated C2 spectrum for small UAVs means we MUST use ISM bands. The protocol stack details (PHY → MAC → Network → Transport) are the specific technical challenges our system must address. The 7 security requirements map to specific attack vectors in FANETs. The optimization taxonomy tells us which algorithm to use for which problem: PSO for placement, GA for evolutionary adjustment, CVX for baseline, alternating minimization for non-convex joint optimization.

# ============================================================
# SLIDE 9 — 3GPP Standardization
# ============================================================
# PPT: R15-R18 timeline, key features per release
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# R15 (TR 36.777): "Enhanced LTE support for aerial vehicles: suggested solutions at the user and network sides to mitigate interference both in the uplink and downlink, to address issues related to mobility, and enable identification of UAVs. Defined channel models building atop TR 38.901, taking into account the altitude of UAVs." Two additional reporting events: H1 (above) and H2 (below) user height thresholds. The interference problem: UAVs at low altitude are high-power uplink interference sources for ground UEs directly below. The H1/H2 events allow the network to identify aerial users and apply interference mitigation.
# Channel model: TR 38.901 with altitude adjustments — but the paper later notes this model is "terrestrial-calibrated" and "not adequately calibrated" for aerial uptilt paths.
#
# R16 (TS 22.825, TR 23.754): "UAV remote identification: explored the requirements and use-cases for remote UAV identification and the corresponding demands through the configuration of the PDN in EPS connections." "UAV connectivity, identification, and tracking: examined how 3GPP can support communications between the UTM and UAVs, and also enable to detect and report unauthorized aerial end-devices to the UTM." UTM integration enables authorization, enforcement, and regulation. The CAA-level UAV ID is provided within PDU session establishment and registration in UUAA procedures.
#
# R17 (TS 22.125, TS 22.829, TR 23.755): "5G enhancements for UAVs: defined new UAV key performance indicators (KPIs) and connectivity requirements in terms of command and control link, data payload, radio access node onboard the UAV (UxNB), as well as UAV constraints on services and network exposure." UxNB = UAV as gNodeB (5G base station). Architecturally significant — the UAV is no longer just a UE or relay, but a full RAN node.
#
# R18: "NR support for UAVs: Will investigate enhancements to measurement reports, signaling for UAV multicast and identification based on subscription, conditional handover and new triggering events, and beam management in FR1 (below 8 GHz), including the use of multi-antenna beamforming and dedicated BS antenna uptilt for UAVs." "Conditional handover" = for fast-moving UAVs. "Dedicated BS uptilt" = ground antennas are downtilted for ground users; uptilt required for UAVs at altitude.
#
# C2 Communications (TS 22.125): Four modes: steer to waypoints, direct stick steering, automatic flight by UTM, approaching autonomous navigation infrastructure. Three C2 link types:
# 1. Direct C2: authenticated cellular connection, tailored resource for C2
# 2. Network-assisted C2: unicast C2 links over RAN, bi-directional critical information
# 3. UTM-navigated C2: indirect via 3GPP network, UTM oversight of flight status
# "Properly acknowledging the receipt of all UAV-terminated C2 packets is crucial. This is because these transmissions may contain essential guidelines that are necessary for controlling the flight of the UAV."
#
# UUAA: "authentication and authorization via a UAS Service Supplier (USS) UAVAuthentication &Authorization (UUAA) prior to granting connectivity for UAS services. The UUAA is enabled either via the 5G core (5GC) connected to next-generation radio access network (NG-RAN) or via the enhanced packet core (EPC) connected to LTE system." Can be triggered during 5GS registration or PDU session establishment.
#
# Network Slicing: "logical networks are built over shared physical networks, in order to enable high-quality dedicated services. It provides a logical solution 'on demand' meant to satisfy individual service requirements and better utilize existing network resources." NetSliA (eMBB): high throughput video. NetSliB (URLLC): C2 and control, sub-millisecond latency. NetSliC (mMTC): UTM telemetry, massive devices. AirSlice framework: "designed to enable differentiated quality-of-service support in 5G networks."
#
# THE DEEP INSIGHT: The 3GPP evolution R15→R18 tells a clear story: from treating UAVs as high-altitude UEs to aerial-native RAN nodes. R15 solved interference and identification. R16 solved security and UTM integration. R17 introduced UxNB. R18 solved mobility (conditional handover) and beam management. For our project, C2 modes and UUAA are the security requirements we must implement. Network slicing is how we'll support both control (URLLC) and data (eMBB) on the same infrastructure.

# ============================================================
# SLIDE 10 — Testbeds
# ============================================================
# PPT: AERPAW, SkyRAN/SkyCore/SkyHAUL, EuroDRONE, HITL/SITL, Aerial BS testbeds
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# AERPAW: "AERRPAW emulation testbed is developed as a multi-level wireless emulation for UAVs, including the RF-level, I-Q level, and packet-level emulation over SDR-based 5G network." Lake Wheeler site: "five fixed nodes, each equipped to support canonical experiments using USRPs with custom RF front ends. In addition to USRPs, several of these nodes are provisioned with advanced instrumentation, including Keysight RF sensors, LoRa gateways, and an Ericsson 4G/5G base station, enabling heterogeneous wireless experimentation across multiple protocol stacks and frequency bands." Portable nodes: "small form-factor USRPs with a host computer and a custom RF front end, can be mounted on a variety of custom-built multirotor UAVs and unmanned ground vehicles." E-VMs: "can be configured to function as a 4G or 5G user equipment, a base station, a 4G/5G core network, or any other SDR software component or system offering full-stack flexibility." Experiments: "UAV handover experiments, radio performance measurements, aerial channel modeling, UAV-based RF source localization, spectrum awareness for radio dynamic zones, mmWave and Sub-THz propagation measurements, and O-RAN enabled aerial networking."
#
# SkyRAN/SkyCore/SkyHAUL: SkyRAN implemented LTE RAN on flying UAV, adaptive to terrain and UE mobility. SkyCore implements EPC core for multiple UAV base stations. SkyHAUL is self-organizing gigabit network with multiple replay UAVs. Key: these are flying RAN prototypes — the UAV carries the base station electronics.
#
# EuroDRONE: "testbed called EuroDRONE for unmanned traffic management using a composite of different V2I and V2V communication technologies. The UAVs used for the testbed are autonomous small UAVs and the wireless technologies include 2.4/5GHz LTE and Sub-GHz communication technology."
#
# HITL/SITL Emulators:
# AVENS: "integrated OMNET++ network simulator and X-Plane flight simulator"
# CUSCUS: "FL-AIR drone simulator with ns-3 over tap bridges and containers"
# FlyNetSim: "ns-3 and Ardupilot with zeromq based middleware... also support HITL based emulation, where real UAVs can be connected over simulated ns-3 network"
# UB-ANC: "simulated UAVs are combined with software-defined radio based emulator... channel models can be implemented over software-defined GNU Radio transceivers"
# SUN: "PX4-based software flight controller with radio-based communications over USRP hardware"
#
# Aerial BS Testbeds: 60 GHz mmWave: "Sanchez et al. developed a testbed for UAV base station with 60GHz mmWave band and developed a UAV-to-ground mmWave channel model though experiments. They also developed an optimal beam selection strategy through experimental insights with the UAV." LoRa/NB-IoT: "Sobot et al. developed a testbed to use LoRa and NB-IoT to create a low power wide area network (LPWAN)."
#
# THE DEEP INSIGHT: Testbeds validate not just protocol correctness but real-world physics — vibration-induced packet loss, wind effects, battery curves, aerodynamic constraints. AERPAW is most capable: supports RF/I-Q/packet emulation, fixed + portable nodes, configurable as UE/gNB/core. SkyRAN/SkyCore/SkyHAUL are unique: full LTE stack on flying UAVs. EuroDRONE shows multi-band operation (LTE + Sub-GHz). HITL/SITL exist because fully end-to-end testbeds are infeasible. 60 GHz testbed pushes bandwidth frontier but requires extremely precise beam tracking.

# ============================================================
# SLIDE 11 — Open Issues
# ============================================================
# PPT: 14 open issues
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# The 14 issues (exact technical details):
# 1. Energy constraint: "On-board batteries of UAVs have limited power resource to support all the operational functions including computation, communication, and flying. Therefore, long-term deployment of UAV systems and power harvest still are key research issues."
# 2. UAV platform & mobility model: "The flight dynamics as well as the UAVs position and orientation highly influence the communication links of UAVs networks. UAV Mobility model: For better simulating of UAVs motions in a practical environment, it needs to combine the best movement features of the proposed mobility models."
# 3. Routing: "In UAVs networks, the routing protocols must dynamically adapt to the network topology changes."
# 4. Path planning: "In multi-UAV missions, UAV node often requires to dynamically re-compute new path in order to cooperate with other UAVs. Therefore, dynamic path planning requires new algorithms to improve the coordination between UAVs."
# 5. QoS provisioning: "Due to the heterogeneous and distributed nature of UAVs networks, establishment of framework for supporting QoS is difficult and challenge."
# 6. Fault handling: "The solutions of handling any types of faults including the problems occurred in hardware, embedded component, software, and communication links, need to be deeply explored."
# 7. Data processing: "Onboard unit of UAVs has limited computation power and is insufficient for data processing. Fog and edge computing offer a solution for data processing."
# 8. Data sharing & security: "The specific characteristics of UAVs networks impose new security requirements. The authenticity of relaying information directly impacts on the security of UAVs networks."
# 9. FANET standardization: "UAV systems require proper standards and guidelines to improve their commercialization for civilian application, and improve the performance in FANETs." IEEE P1920.1 is the first draft standard, completed December 2022.
# 10. Distributed optimization: "It is paramount to design and implement distributed optimization techniques given the distributed nature of the UAVs but also for scalability purposes. Indeed, most existing solutions are centralized algorithms that suffer from scalability aptitude. Another critical aspect of these techniques is the study of their theoretical properties and technology readiness level that need to be boosted to their highest through real-world testing or at least simulation with built-in features for distributed algorithms."
# 11. Spectrum management: "Radio spectrum management for commercial UAV operations in the absence of a dedicated spectrum requires significant attention. Current spectrum allocation techniques are insufficient to meet the growing demands of UAV communications and, therefore, require new spectrum-sharing techniques with reduced interference."
# 12. Network formation/topology: "Dynamic topology control in UAV networks introduces several unique challenges due to dynamic movement patterns in 3D space, varying channel quality levels, and energy limitations. Therefore, efficient clustering mechanisms are needed."
# 13. Testing & simulation: "Current UAV simulation environments often fail to fine-tune the complex dynamics of aerial networks. This requires more realistic simulation frameworks and testing methodologies that could capture the unique characteristics of complex near-real aerial deployments."
# 14. Airspace integration: "Combining UAV networks with existing terrestrial, satellite, and maritime networks to create harmonious space-air-ground-sea networks is highly complex, and challenges persist in cross-domain routing, handover management, and heterogeneous resource allocation."
#
# THE DEEP INSIGHT: These are the specific gaps our project must address. Energy (#1) is fundamental — no algorithm works if battery dies. Routing (#3) and path planning (#4) are the dynamic topology problems our Multi-Agent Q-Learning must solve. QoS (#5) is what our coverage/connectivity constraints enforce. Data processing (#7) is why we need edge computing. Spectrum (#11) is the hard constraint forcing ISM band usage. Testing (#13) is why we need realistic simulators. Our project is a concrete instantiation of issues #1, #3, #4, #5, #11, #12.

# ============================================================
# SLIDE 12 — Recommendations & Further Work
# ============================================================
# PPT: Multi-UV recommendations, Deep RL routing, blockchain, realistic simulators, ISAC, slicing, 6G/SAGSIN
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# Recommendations (exact technical content from Section VIII-B):
# "Multi-UAV systems that are able to maintain steady communication, remotely operate control and command with unlimited coverage, secure information exchange, and support the various coexistent wireless applications. These multi-UAV systems should include adaptive beamforming approaches and directional antenna technologies to improve communication reliability and coverage while minimizing interference in highly dynamic operational environments."
#
# "Routing mechanisms for UAV networks that are able to adapt to high mobility, network topology changes, and load balance of UAVs. These futuristic routing protocols should leverage deep reinforcement learning or hybrid-learning approaches to predict topology dynamics and optimize route selection based on channel quality, energy efficiency, and mission requirements."
# This is specific: not just "use Deep RL" but "predict topology dynamics and optimize route selection based on channel quality, energy efficiency, and mission requirements." This is EXACTLY what our Multi-Agent Q-Learning must do.
#
# "A regular registration procedure to manage identifications of UAV devices through the entire life-cycle of UAV, including manufacturing, marketing, repairing, and scrapping. The registration process should comprise blockchain technology to guarantee secure and immutable device identification and enable trusted authentication and authorization throughout the UAV lifecycle."
# Lifecycle: manufacture → marketing → repairing → scrapping. Blockchain provides immutable audit trail.
#
# "UAV simulators that are able to accurately simulate different types of UAVs according to their constraints. Next-generation UAV simulators should incorporate realistic communication models, energy consumption patterns, and flight dynamics with network simulation capabilities to provide comprehensive evaluation and testing environments for realistic UAV-oriented research."
# Three specific requirements: realistic communication models, energy consumption patterns, flight dynamics.
#
# "Innovative network architectures that could support cross-domain applications. In this context, the network slicing-assisted architecture could provide enhanced communication services for diverse UAV applications and deployments with varying QoS requirements, i.e., from low-latency control to real-time high-throughput data transmission."
# "Full security frameworks that cover all possible threats, such as jamming, spoofing, unauthorized access, and data interception, for resource-constrained aerial platforms."
# "Avenues to improve existing spectrum-sharing techniques for unmanned aerial communications, including cognitive radio approaches, dynamic spectrum access, and interference coordination mechanisms to improve overall resource utilization while ensuring easy deployments with incumbent systems."
# "Solutions to enhance UAV situational awareness by improving ISAC capabilities for aerial networks that utilize the optimized hardware and spectrum resources for communication and environmental sensing."
#
# THE DEEP INSIGHT: Each recommendation is a direct response to a specific gap in Section VIII. Our project addresses: steady communication (routing), Deep RL for topology prediction (Multi-Agent Q-Learning), realistic simulation (flight dynamics + communication), and network slicing (QoS differentiation). The blockchain recommendation is the security track.

# ============================================================
# SLIDE 13 — Conclusion
# ============================================================
# PPT: 3 findings, 3 future directions, final quote
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# The three findings (exact text):
# 1. "UAVs have gained prominence among the scientific community over the years. Multiple UAVs can cooperatively perform complex missions, especially in unreachable areas, with the help of self-organizing UAV networking. This paper presents a technological overview of networking UAVs, including communication architecture, communication protocols, communication requirements, and security requirements. Within that, the UAV network formation and state-of-the-art solutions are discussed. Furthermore, we surveyed the 3GPP standardization for UAV cellular communication."
# 2. "Cellular-connected UAV communication and network slicing for UAV communication are discussed. FANET offers a novel mechanism to address scalability issue present in direct link networking. However, communication remains one of the most serious constraints that surround FANETs."
# 3. "Thus, the paper also presents the open research issues and further research directions suggested in the literature to encourage researchers and professionals in this domain."
#
# The "where it is heading" section with SPECIFIC technologies:
# - AI/ML convergence: "Optimize trajectories and radio resources jointly under complex and often non-convex constraints" — paradigm shift from sequential to joint optimization.
# - RIS: "electronically controllable EM surfaces reflect/enhance signals" — radio environment becomes programmable.
# - ISAC: "joint sensing + communication — same hardware, dual function" — fundamental hardware-software co-design.
# - Digital Twins: "virtual replica... data acquisition → processing → application" — real-time monitoring and predictive maintenance.
# - 6G/SAGSIN: "Space-Air-Ground-Sea Integrated Network" — seamless global coverage across domains.
#
# Final quote context: "UAV communications has evolved from a niche topic to a key enabler of future wireless connectivity." Supported by market data ($17.31B → $32.95B) and 3GPP roadmap extending to 6G.
#
# THE DEEP INSIGHT: The three findings are evidence-based, not summaries. Finding 1 is validated by architecture, protocol, and optimization sections. Finding 2 is validated by standardization evolution R15→R18. Finding 3 IS the 14 open issues. The convergence (AI/ML + RIS + ISAC + DT) is a coherent vision where the radio environment is programmable, the network is self-managing, and every physical asset has a virtual twin. Our project is a concrete instantiation: we use AI/ML (PSO/GA + Multi-Agent Q-Learning) to optimize UAV placement and movement in a communication-constrained environment.

# ============================================================
# SLIDE 14 — Course Problem Statement
# ============================================================
# PPT: Develop AI-based system for multiple UAVs as aerial BS, determine position/movement, maintain connectivity, maximize coverage, minimize energy, PSO/Genetic + Multi-Agent Q-Learning
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# Placement problem (Section IV-M, exact algorithms):
# "3-D placement of an unmanned aerial vehicle base station (UAV-BS) for energy-efficient maximal coverage" (Alzenad et al. [95]). Problem: "find the optimal 2D and 3D coordinates in a decoupled way and is solved using the CVX solver."
# "Particle swarm optimization stepwise process was proposed to serve all the users with few UAV-BSs while optimally calculating and setting their 3D spatial coordinates" (ref [244]).
# "genetic algorithm-based evolutionary optimization technique for a similar problem to maximize users' QoS requirements" (ref [246]).
# "branch and bound solution method... to increase user connectivity in a geographically designated area while deploying as few UAVs as possible" (ref [247]).
# "spiral-based strategy for optimizing UAVs-MBs, utilizing the convex hull algorithm" (ref [248]).
#
# Fundamental trade-off: "altitude ↑ LoS but ↑ path loss." Higher altitude increases LoS probability but increases path loss. Multi-objective optimization.
#
# Movement problem (Section IV-F, IV-C):
# Multi-UAV architectures: C1 (star), C2 (leader gateway), C3 (mesh). Our mesh connectivity constraint maps to C3.
# "Distributed sliding control for time-varying formation tracking of multi-UAV system with a dynamic leader" (ref [121]).
# "Deep reinforcement learning for UAV navigation through massive MIMO technique" (ref [143]).
# "Joint trajectory and communication design for multi-UAV enabled wireless networks" (ref [102]).
#
# Constraints are NOT independent:
# - Connectivity (mesh/graph) constrains placement: candidate positions must preserve graph connectivity
# - Coverage constrains movement: UAVs must remain over user density regions
# - Energy constrains both: battery depletion terminates mission
#
# AI/ML choice is specific:
# - PSO and GA: population-based meta-heuristics that handle non-convex, mixed-integer problems. Offline/slow-time.
# - Multi-Agent Q-Learning: sequential decision under partial observability, real-time. Each UAV learns policy conditioned on local observations (neighbors, battery, channel quality).
# - CVX: provides optimal solutions for convex relaxations, allowing measurement of sub-optimality gap.
#
# THE DEEP INSIGHT: The problem is a hierarchical optimization system with conflicting objectives. Placement is combinatorial search over 3D coordinates (offline). Movement is sequential decision under partial observability (real-time). The constraints interact: connectivity constrains placement, coverage constrains movement, energy constrains both. The AI/ML choices map directly to validated algorithms from the paper.

# ============================================================
# SLIDE 15 — Survey-to-Problem Mapping
# ============================================================
# PPT: Paper content → problem requirements
#
# THE ACTUAL TECHNICAL SUBSTANCE:
# This slide proves we've read the paper, not just the abstract. Each mapping is to a specific section with specific algorithms:
#
# UAV as Base Station (Sec IV-B) → aerial base stations:
# "UAVs as base stations enables continuity of communications by expanding the communication coverage and acting as protocol converters." Challenges: energy optimization, coverage, bandwidth, trajectory/path planning, WPT, wireless security.
# This gives us the coverage model and challenge set.
#
# 3D placement optimization (Sec IV-M/K) → where UAVs are positioned:
# Section IV-M gives the full optimization toolkit: PSO, GA, CVX, convex hull, branch-and-bound, alternating minimization, graph-based methods.
# Section IV-K gives channel models: LoS probability, path loss, directional antennas.
# Together: optimize (x,y,z) using PSO/GA, subject to channel quality constraints from IV-K.
#
# PSO & Genetic Algorithm (Sec IV-M) → placement AI/ML:
# Alzenad et al. [95]: PSO for 3D placement with energy-efficient maximal coverage.
# Ref [246]: Genetic Algorithm for multi-criteria placement maximizing QoS.
# These are our primary placement algorithms.
#
# Multi-UAV architectures & leader (Sec IV-F) → how they move as a formation:
# C1 (star), C2 (leader gateway), C3 (mesh). Our mesh connectivity constraint maps to C3.
# "Distributed sliding control for time-varying formation tracking" (ref [121]).
# This gives us the formation control mechanism.
#
# Energy optimization (Sec IV-M, Open Issues) → minimizing energy:
# "Energy tradeoff in ground-to-UAV communication via trajectory design" (ref [97]).
# Open Issue #1: "On-board batteries of UAVs have limited power resource to support all the operational functions including computation, communication, and flying."
# This is our battery-aware constraint.
#
# UAV-to-UAV connectivity = mesh / C1–C3 (Sec IV-F) → maintain connectivity:
# C3 mesh topology is our baseline. "Joint topology control and routing in a UAV swarm for crowd surveillance" (ref [205]).
# Open Issue #12: "Dynamic topology control in UAV networks... efficient clustering mechanisms are needed."
# This is our graph connectivity constraint.
#
# Coverage maximization (Sec IV-B/M) → maximize coverage:
# "3-D placement of an unmanned aerial vehicle base station (UAV-BS) for energy-efficient maximal coverage" (ref [95]).
# Open Issue #5: "QoS provisioning... establishment of framework for supporting QoS is difficult and challenge."
# This is our coverage objective function.
#
# Our course approach:
# - Placement: PSO/GA over 3D coordinates (CVX baseline)
# - Movement: Multi-Agent Q-Learning for dynamic formation
# - Constraint 1: maintain UAV-UAV links (mesh/graph)
# - Constraint 2: maximize coverage (user density map)
# - Constraint 3: minimize energy (battery-aware)
# - Input/Output matches the paper's resource-optimization loop
#
# Resource-optimization loop:
# "sense the environment → compute optimal actions → execute → repeat" — this is the paper's central metaphor for Section IV-M. Our system is an instantiation where:
# - Environment = user density map + UAV states + channel conditions
# - Compute = PSO/GA (slow-time placement) + Multi-Agent Q-Learning (fast-time movement)
# - Execute = UAV position/movement commands
#
# THE DEEP INSIGHT: This slide is the proof of concept. We are not building a generic UAV system — we are building a specific instantiation of the paper's architecture, using the paper's algorithms, addressing the paper's open issues, and aligned with the paper's 3GPP standardization. The mapping shows we understand the paper's dependency structure and have chosen the right algorithms for each requirement.
