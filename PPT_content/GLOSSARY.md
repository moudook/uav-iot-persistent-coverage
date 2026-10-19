# UAV Communications — Atomic Glossary
# Source: PPT.pptx extracted text

# ============================================================
# 1. UAV & DRONE FUNDAMENTALS
# ============================================================
UAV (Unmanned Aerial Vehicle): An aircraft without a human pilot on board, controlled autonomously or remotely; the core subject of the survey.
Drone: Colloquial synonym for UAV; emphasizes low cost, easy deployment, and minimal risk in civilian/military domains.
UAS (Unmanned Aerial System): The complete operational system comprising 5 components: (1) UAV air vehicle, (2) Ground Control Station, (3) Payload/data processing, (4) Control & data links, (5) Support system.
GCS (Ground Control Station): The ground-based control hub that manages UAV operations, telemetry, and command links.
Payload: The mission-specific equipment carried by a UAV (e.g., sensors, cameras, communication relays).
Control & Data Links: The communication channels between the UAV and GCS for command transmission and data reception.

# ============================================================
# 2. NETWORK TYPES & ARCHITECTURES
# ============================================================
FANET (Flying Ad-hoc Network): An infrastructure-less, self-organizing network of flying UAV nodes; used to automate aerial swarm communications.
MANET (Mobile Ad-hoc Network): A decentralized wireless network of mobile nodes without fixed infrastructure; early policies failed for aerial use due to 3D mobility.
VANET (Vehicular Ad-hoc Network): A MANET variant for vehicles; shares similar dynamic-topology challenges but operates on the ground.
SAGSIN (Space-Air-Ground-Sea Integrated Network): A future 6G vision integrating aerial nodes with space, ground, and sea segments for seamless global coverage.
IoD (Internet of Drones): A framework treating low-altitude airspace as a limited resource, coordinated by Zone Service Providers (ZSPs) with middleware for unified control.
ZSP (Zone Service Provider): An entity that coordinates local UAV operations within a designated airspace zone.
Backbone UAV: In a FANET, the node connected to the Ground Control Station or satellite, serving as the network gateway.
SWaP: Acronym for Size, Weight, and Power — key constraints for UAV platform design and payload selection.
C1 (Star Topology): A single-layered gateway view where all UAVs communicate through one central leader/gateway.
C2 (Leader Gateway): A multi-layered architecture with a designated leader UAV acting as the gateway for the network.
C3 (Mesh Topology): A fully connected or partially connected multi-layered architecture where UAVs relay among themselves without a single gateway.
Hierarchical Mesh: A scalable multi-UAV architecture combining star clusters within a larger mesh structure for survivability.
Physical Coupling: A multi-UAV cooperation scheme where UAVs are physically connected, causing motion of one to affect others.
Formation: UAVs flying in a predefined geometric pattern (e.g., star, rectangle) while maintaining relative distance, speed, and acceleration.
Swarm: A homogeneous team of UAVs using decentralized communication to achieve robust global behavior without central control.
Intentional Cooperation: Task allocation with predefined trajectories, implemented via centralized or decentralized coordination.
Regime-Switching System: A hybrid mission mode where UAVs switch between cooperation schemes (e.g., formation to swarm) per mission phase.
Fixed-wing UAV: An aircraft with rigid wings; efficient for long-range, high-altitude missions but requires runways or catapults.
Rotary-wing UAV: A helicopter-style aircraft; capable of vertical takeoff/landing and hovering, but limited in endurance.
Hybrid/VTOL UAV: A Vertical Takeoff and Landing aircraft that combines fixed-wing efficiency with rotary-wing flexibility.
Small/Mini UAV: Lightweight drones with limited range and payload; often used for surveillance and agile reconnaissance.
Medium UAV: Mid-size drones with moderate endurance and payload capacity; suitable for regional coverage missions.
Large UAV: Heavy, long-endurance aircraft capable of carrying substantial payloads and operating at high altitudes.
Mobility Model: A mathematical description of how UAVs move through 3D space, including speed, direction, and acceleration patterns.
Node Density: The number of UAV nodes per unit volume; affects routing complexity, interference, and network scalability.
Localization: The process of determining UAV positions in 3D space, critical for formation maintenance and coverage planning.
Hierarchical FANET: A clustered aerial network organized into tiers for improved scalability and survivability.
Cluster-based FANET: A FANET where UAVs are grouped into clusters with cluster heads managing intra-cluster communication.

# ============================================================
# 3. COMMUNICATION TECHNOLOGIES
# ============================================================
Direct Link: A point-to-point wireless connection (typically ISM 2.4/5.8 GHz) between UAVs or between UAV and ground; simplest but limited by LoS and range.
LoS (Line of Sight): A direct, unobstructed radio path between transmitter and receiver; essential for high-quality UAV links.
NLoS (Non-Line of Sight): A radio path blocked by obstacles; causes signal degradation and requires alternative routing or relay nodes.
ISM Bands: Industrial, Scientific, and Medical radio bands (900 MHz, 2.4 GHz, 5.8 GHz) used for unlicensed UAV communications.
Satellite-based Communication: Wide-area coverage via satellite links; high latency (~0.12 s), heavy antennas, and high cost, but effective for remote/NLoS areas.
UAV-Assisted Cellular: A deployment model where UAVs act as flying relays or aerial base stations to augment terrestrial cellular networks.
Cellular-Connected UAV: A deployment model where UAVs function as aerial users (UEs) connected to terrestrial 5G/4G base stations.
Aerial BS (Base Station): A UAV-mounted base station providing temporary, on-demand wireless coverage in disaster or event scenarios.
Flying Relay: A UAV that extends the range of existing terrestrial infrastructure by retransmitting signals.
Data Mule: A UAV that physically carries data between nodes, useful in low-bandwidth or disconnected environments.
A2G (Air-to-Ground): Communication link between an aerial node and a ground-based station; subject to unique propagation challenges.
UAV-to-UAV Connectivity: Direct or mesh-based communication links between aerial nodes; essential for formation control and swarm coordination.
WPT (Wireless Power Transfer): Technology for charging UAV batteries via RF or laser energy beaming, extending mission endurance.
Beam Management: Dynamic control of antenna beam direction, width, and power to maintain links with moving UAVs.
Beamforming: A MIMO technique using multiple antennas to focus signal energy in specific directions, improving SNR and range.
Dual-functional MIMO: A MIMO system that simultaneously performs communication and sensing/radar functions.

# ============================================================
# 4. CHANNEL MODELING & PROTOCOLS
# ============================================================
Channel Model: A mathematical representation of signal propagation between transmitter and receiver, including path loss, fading, and interference.
3GPP TR 38.901: A 3GPP technical report defining channel models for 5G; terrestrial-calibrated, inadequate for aerial uptilt paths.
Large-scale Fading: Slow signal strength variations due to path loss and shadowing from obstacles; determines coverage range.
Small-scale Fading: Rapid signal fluctuations due to multipath propagation; characterized by Doppler shift and delay spread.
Multipath: The phenomenon where signals arrive at the receiver via multiple reflecting paths, causing interference and fading.
Doppler Shift: Frequency change caused by relative motion between transmitter and receiver; critical for high-speed UAV links.
TTS-CGAN: A time-series conditional GAN for generating spatially consistent A2G channel samples in a site-specific manner.
MTS-CGAN: A multi-time-step conditional GAN for generating temporally consistent A2G channel samples.
Spatio-temporal Consistency: The requirement that generated channel samples preserve both spatial and temporal correlations found in real measurements.
Sionna RT: A GPU-accelerated ray-tracing simulator for site-specific radio channel calibration in 3D environments.
PHY (Physical Layer): The OSI layer responsible for raw bit transmission over the wireless medium; handles modulation, coding, and channel estimation.
MAC (Medium Access Control): The OSI layer managing channel access, scheduling, and collision avoidance among multiple UAVs.
MPR (Multi-Packet Reception): A MAC capability allowing simultaneous reception of multiple packets, improving throughput in dense UAV networks.
Full-duplex: A communication mode enabling simultaneous transmission and reception on the same frequency, doubling spectral efficiency.
AODV (Ad-hoc On-demand Distance Vector): A reactive network-layer routing protocol for MANETs/FANETs that discovers paths only when needed.
DSR (Dynamic Source Routing): A source-routing protocol for ad-hoc networks where the complete path is embedded in each packet header.
PRRT (Partial Reliable Real-Time Transport): A transport protocol balancing reliability and latency for real-time UAV telemetry.
LRT (Lightweight Reliable Transport): A low-overhead transport protocol designed for resource-constrained UAV nodes.

# ============================================================
# 5. AI/ML & OPTIMIZATION METHODS
# ============================================================
AI/ML in UAV Communications: The application of artificial intelligence and machine learning to optimize trajectories, resources, and network functions under non-convex constraints.
Non-convex Constraints: Optimization constraints where the feasible region is not a convex set; common in 3D placement and joint resource problems.
Channel Estimation: The process of inferring the channel state information (CSI) from pilot signals; enhanced by ML for 3D aerial channels.
Beam/Antenna Management: Dynamic selection and steering of antenna beams to maintain connectivity with moving UAVs; optimized by ML.
Intrusion Detection: Security technique using ML to identify unauthorized access or malicious behavior in aerial networks.
Anomaly Detection: ML-based identification of abnormal network patterns, such as jamming or spoofing attacks.
Jamming Identification: Detection of intentional RF interference aimed at disrupting UAV communications.
Multi-hop Aerial Network: A network where data traverses multiple UAV relays before reaching the destination or ground station.
Generative AI: AI models (e.g., GANs) that generate synthetic data; used here for A2G channel modeling where real measurements are scarce.
Deep RL (Deep Reinforcement Learning): ML approach combining deep neural networks with reinforcement learning; used for routing and dynamic UAV control.
Hybrid-learning: A combination of learning paradigms (e.g., supervised + reinforcement) for predicting topology dynamics in FANETs.
PSO (Particle Swarm Optimization): A bio-inspired optimization algorithm simulating swarm behavior; used for 3D UAV placement.
Genetic Algorithm: An evolutionary optimization technique using selection, crossover, and mutation; applied to UAV placement and trajectory planning.
CVX (Convex Optimization): A mathematical framework for problems with convex objectives and constraints; used as a baseline for 3D placement.
Convex Hull: The smallest convex polygon enclosing a set of points; used in geometric formulations of UAV coverage problems.
NOMA (Non-Orthogonal Multiple Access): A multiple-access technique allowing multiple users to share the same time/frequency resource with successive interference cancellation.
Decode-and-Forward: A relaying strategy where the relay node decodes the message before retransmitting; used in multi-UAV networks.
Water-filling: A power allocation strategy that distributes power across subcarriers to maximize capacity, proportional to the inverse of channel gain.
SCA (Successive Convex Approximation): An iterative optimization technique that approximates non-convex problems with convex surrogates.
Alternating Minimization: An optimization method that minimizes a multi-variable objective by solving for one variable at a time while fixing others.
Pareto Optimization: A multi-objective approach finding solutions where no objective can be improved without degrading another.
Dual-ascent: A constrained optimization method using Lagrange multipliers to decompose complex problems into manageable subproblems.
Multi-Agent Q-Learning: A reinforcement learning variant where multiple agents learn policies simultaneously; used for dynamic UAV formation control.

# ============================================================
# 6. ADVANCED TECHNOLOGIES
# ============================================================
RIS (Reconfigurable Intelligent Surface): An electronically controllable electromagnetic surface that reflects and enhances signals to improve A2G link quality.
ISAC (Integrated Sensing and Communications): A paradigm combining radar sensing and wireless communication on the same hardware/platform; sensing aids beam tracking, communications aids mapping.
Digital Twin (DT): A virtual replica of a physical UAV system that mirrors real-time state via data acquisition, processing, and application; aligns with 3GPP Rel-15/16/17.
MIMO (Multiple-Input Multiple-Output): A communication technology using multiple antennas at transmitter and receiver to achieve spatial diversity/multiplexing, improving spectral efficiency.
Spatial Diversity: MIMO technique using multiple antennas to combat fading by transmitting/receiving redundant signal copies.
Spatial Multiplexing: MIMO technique transmitting independent data streams on multiple antennas to increase throughput.
Pilot Contamination: A MIMO impairment where pilot signals from neighboring cells interfere with channel estimation, degrading performance.
Kalman-filter Channel Tracking: An estimation technique using Kalman filters to track time-varying 3D channel states for moving UAVs.
SWIPT (Simultaneous Wireless Information and Power Transfer): A technique enabling simultaneous energy harvesting and data reception from the same RF signal.

# ============================================================
# 7. SELF-ORGANIZATION & COORDINATION
# ============================================================
Self-Organization: The ability of UAV networks to autonomously form, configure, and maintain connectivity without central control.
Reynolds' Boids: A computational model of flocking behavior (separation, alignment, cohesion) used as inspiration for UAV self-organization.
Addressing: The process of assigning unique identifiers to UAV nodes for network identification and routing.
Neighbor Discovery: The mechanism by which UAVs detect and identify nearby nodes to establish local connectivity.
Routing: The process of selecting paths for data packets from source to destination across a dynamic aerial network.
Formation Control: The coordination mechanism ensuring UAVs maintain specified geometric patterns during flight.

# ============================================================
# 8. SPECTRUM & SECURITY
# ============================================================
Spectrum Management: The planning, allocation, and utilization of radio frequencies for UAV communications, addressing scarcity and interference.
Spectrum Sharing: The practice of multiple users/services coexisting in the same frequency band via Opportunistic, Competitive, or Cooperative schemes.
Opportunistic Sharing: A spectrum strategy where secondary users transmit when primary users are inactive.
Competitive Sharing: A spectrum strategy where users compete for channel access, often via game-theoretic mechanisms.
Cooperative Sharing: A spectrum strategy where users coordinate to maximize overall system efficiency and fairness.
C2 (Command and Control): The real-time communication link between a human operator and a UAV for commanding missions and receiving telemetry.
C2 Modes (TS 22.125): The standardized control modalities: waypoints (predefined path), stick (manual joystick), UTM-auto (traffic-management automation), autonomous (full AI control).
UTM (UAV Traffic Management): An air-traffic-control framework for low-altitude airspace, managing flight plans, conflict resolution, and surveillance.
Confidentiality: A security requirement ensuring that UAV communication data is accessible only to authorized parties.
Integrity: A security requirement guaranteeing that transmitted data has not been tampered with in transit.
Non-repudiation: A security property preventing the sender from denying having sent a message.
Authentication: A security process verifying the identity of communicating parties to prevent spoofing.
Access Control: A security mechanism restricting resource access to authorized UAVs and operators.
Availability: A security requirement ensuring that UAV communication services are accessible and operational when needed.
Privacy: A security requirement protecting sensitive UAV data (e.g., location, imagery) from unauthorized disclosure.
Jamming: An attack that deliberately interferes with UAV communication signals to disrupt operations.
Spoofing: An attack that transmits false signals to deceive UAV navigation or communication systems.
UUAA (UAV Authentication & Authorization): A 3GPP standard mechanism for authenticating and authorizing UAVs via the UAV Service System (USS).
USS (UAV Service System): The 3GPP network entity responsible for managing UAV authentication, authorization, and registration.

# ============================================================
# 9. STANDARDIZATION & 3GPP
# ============================================================
3GPP (3rd Generation Partnership Project): The global standards body defining cellular technologies (4G, 5G, 6G) and UAV-related specifications.
3GPP Release 15 (R15): Introduced 4G LTE support for UAVs, aerial-user identification, and location/altitude/trajectory reporting (events H1/H2).
3GPP Release 16 (R16): Added Remote ID (TR 23.754), UTM interaction, and unauthorized-device detection for enhanced UAV security.
3GPP Release 17 (R17): Defined 5G KPIs for UAVs, UxNB (UAV as gNB), and application-layer tracking (TR 23.755).
3GPP Release 18 (R18): Introduced New Radio enhancements, conditional handover, beam management, multi-antenna support, dedicated BS uptilt, slicing, and UUAA/C2.
TR (Technical Report): A 3GPP document type providing research-oriented guidance (e.g., TR 23.754 for Remote ID, TR 23.755 for app-layer tracking).
UAV as gNB (UxNB): A 3GPP concept enabling a UAV to function as a gNodeB (5G base station), providing aerial coverage.
Remote ID: A 3GPP standard for electronic identification and location broadcasting of UAVs to authorities and other airspace users.
Conditional Handover: A 5G mobility procedure allowing seamless transfer of UAV connections between base stations under specific conditions.
Network Slicing: A 5G technique partitioning the physical network into virtual, isolated slices (NetSliA/B/C) tailored for eMBB, URLLC, or mMTC services.
NetSliA/B/C: Three 5G network slice types for UAVs: A (eMBB — high throughput), B (URLLC — ultra-reliable low latency), C (mMTC — massive machine-type).
eMBB (enhanced Mobile Broadband): A 5G service class optimized for high data rates and capacity; used for video streaming and high-bandwidth UAV payloads.
URLLC (Ultra-Reliable Low Latency Communication): A 5G service class providing sub-millisecond latency and extreme reliability; critical for C2 and safety missions.
mMTC (massive Machine-Type Communications): A 5G service class supporting massive numbers of low-data-rate devices; relevant for large UAV swarms.
AirSlice Framework: A 3GPP reference architecture implementing network slicing specifically for UAV communication services.
SLA (Service Level Agreement): A contractual agreement defining the performance guarantees (throughput, latency, reliability) for a network slice.

# ============================================================
# 10. TESTBEDS & HARDWARE
# ============================================================
AERPAW (NSF PAWR): A large-scale NSF-funded wireless testbed supporting SDR platforms, RF/I-Q/packet-level emulation, and edge virtual machines for UAV research.
SDR (Software Defined Radio): A programmable radio platform enabling flexible waveform generation and signal processing for experimentation.
E-VMs (Edge Virtual Machines): Virtualized compute instances deployed at network edges to run UE, gNB, or core network functions in testbeds.
UE (User Equipment): The 3GPP term for end-user devices; in testbeds, simulated or real devices connecting to aerial or terrestrial base stations.
gNB (gNodeB): The 5G base station; in aerial contexts, can be ground-based or mounted on UAVs (UxNB).
EPC (Evolved Packet Core): The 4G LTE core network; used in SkyRAN/SkyCore testbeds for flying RAN deployments.
SkyRAN / SkyCore / SkyHAUL (NEC): NEC's flying LTE RAN testbeds demonstrating self-organizing gigabit multi-UAV networks with EPC core.
EuroDRONE: A European V2I/V2V UTM testbed using autonomous small UAVs operating in 2.4/5 GHz LTE and Sub-GHz bands.
HITL (Hardware-in-the-Loop): A testing method integrating physical UAV hardware with simulated environments for realistic validation.
SITL (Software-in-the-Loop): A testing method running complete UAV software stacks in simulation without physical hardware.
OMNeT++: A discrete-event network simulator widely used for FANET protocol research.
ns-3: A discrete-event network simulator commonly used for UAV communication protocol evaluation.
X-Plane: A flight dynamics simulator providing realistic 3D aircraft physics for HITL/SITL testing.
AVENS: A HITL/SITL emulator combining OMNeT++ or ns-3 with X-Plane for FANET research.
CUSCUS: A hardware-in-the-loop testbed for evaluating UAV communication protocols under realistic flight dynamics.
FlyNetSim: A network simulator integrating flight dynamics for end-to-end UAV communication evaluation.
60 GHz mmWave: A high-frequency band offering multi-Gbps throughput; used in aerial BS testbeds for ultra-high-speed backhaul.
LoRa: A low-power, long-range LPWAN technology; tested for UAV relay and IoT sensor networks.
NB-IoT (NarrowBand IoT): A 5G LPWAN technology for low-power, wide-area IoT connectivity; used in aerial relay testbeds.
LPWAN (Low-Power Wide-Area Network): A wireless network class designed for long-range, low-power IoT devices; relevant for ground sensor networks served by UAVs.
USRP (Universal Software Radio Peripheral): A flexible SDR hardware platform used for beamforming experiments and custom waveform generation in aerial testbeds.

# ============================================================
# 11. OPEN ISSUES & RESEARCH CHALLENGES
# ============================================================
Energy Constraint: The fundamental limitation of UAV battery capacity, affecting flight time, payload, and communication endurance.
UAV Platform & Mobility Model: The need for realistic models of UAV motion, aerodynamics, and platform constraints in simulation and design.
Routing (Dynamic Topology): The challenge of maintaining efficient data paths in networks where nodes move rapidly in 3D space.
Path Planning: The computation of collision-free, energy-efficient trajectories for single or multiple UAVs in complex environments.
QoS Provisioning: Ensuring required quality-of-service metrics (latency, throughput, reliability) for diverse UAV applications.
Fault Handling: Detecting, isolating, and recovering from hardware/software failures in autonomous UAV networks.
Data Processing (Edge/Fog): The challenge of processing UAV-generated data at the network edge or fog nodes to reduce latency and backhaul load.
Data Sharing & Security: Protecting sensitive UAV data during multi-node sharing while maintaining accessibility for authorized users.
FANET Standardization: The need for unified protocols and standards specifically designed for aerial ad-hoc networks.
Distributed Optimization: Solving complex resource allocation problems across multiple UAVs without central coordination.
Spectrum Management: Efficiently allocating and sharing limited radio spectrum among competing UAV applications and services.
Network Formation/Topology: The challenge of dynamically organizing UAV nodes into efficient, resilient network structures.
Testing & Simulation Fidelity: The gap between simulated UAV networks and real-world deployments, including energy models and flight dynamics.
Airspace Integration: The challenge of safely integrating large numbers of UAVs into shared low-altitude airspace with manned aircraft.

# ============================================================
# 12. SECURITY & TRUST
# ============================================================
Blockchain-based Device Lifecycle Registration: A distributed ledger system tracking UAV provenance from manufacture through repair to decommissioning, enhancing trust and accountability.
Security Framework: A comprehensive set of policies, protocols, and technologies protecting UAV networks from jamming, spoofing, and data breaches.
Cognitive-radio Spectrum Sharing: An intelligent spectrum access technique where UAVs sense and opportunistically use available frequencies without interfering with primary users.

# ============================================================
# 13. COURSE PROJECT CONCEPTS
# ============================================================
Course Problem Statement: The Week 1 project requiring an AI-based system for deploying multiple UAVs as temporary aerial base stations with dynamic positioning and movement.
Temporary Aerial Base Station: A UAV-mounted base station providing on-demand wireless coverage for a limited duration and geographic area.
3D Placement Optimization: The computational problem of determining optimal (x, y, z) coordinates for UAVs to maximize coverage while minimizing energy.
User Density Map: A spatial representation of user distribution used as input for UAV placement and coverage optimization algorithms.
Communication Range: The maximum distance over which a UAV can maintain reliable communication links with ground users or other UAVs.
Channel Quality: A measure of the radio link condition (e.g., SINR, SNR) between UAVs and ground users, influencing placement and power decisions.
Battery-aware Optimization: Resource allocation strategies that account for remaining UAV battery levels to ensure mission completion.
Resource-optimization Loop: The iterative cycle of sensing the environment, computing optimal UAV actions (placement/movement), and executing them to maximize system objectives.
Survey-to-Problem Mapping: The alignment between survey paper concepts (Sections IV-B, IV-F, IV-M, etc.) and the specific requirements of the course project.
Coverage Maximization: The objective of maximizing the number of served users or geographic area covered by aerial base stations.
Mesh/Graph Connectivity: Maintaining a connected network topology among UAVs using graph-theoretic connectivity constraints.
Battery-aware Constraint: A requirement that UAV movement and communication decisions consider remaining battery to prevent premature mission termination.
Aerial Base Station (Course Context): A UAV deployed specifically to provide wireless coverage and connectivity to ground users in a target area.
