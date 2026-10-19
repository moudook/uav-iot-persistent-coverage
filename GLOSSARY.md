# UAV Communications — Hinglish Glossary
**Paper:** Granelli et al., *A Survey on UAV Communications*, IEEE OJ-COMS 2026

**How to use this:** Har entry mein teen cheezein hain — **Kya hai** (scene imagine kar), **Kaise kaam karta hai** (mechanism), **Kyun important hai paper mein**. Jab kuch confusing lage, pehle "scene" wala part padh, math baad mein aayega.

---

## PART 1 — Core Standards & Big Picture

---

### 3GPP — 3rd Generation Partnership Project
**Kya hai:** Ek global "rules committee" hai jo 4G/5G/6G ke technical standards banata hai. Jaise BIS (Bureau of Indian Standards) electronic products ke liye hota hai, 3GPP wireless networks ke liye hai. Releases nikalta hai — Release 15, 16, 17, 18...

**Kaise kaam karta hai:** Har Release mein nayi capabilities add hoti hain. UAVs ke liye detailed timeline:
- **Rel-15 (2017):** Pehli baar 4G LTE pe aerial users recognize hue — signaling protocols for aerial user identification based on subscriptions, location/altitude/flight trajectory reporting, new measurement reports.
- **Rel-16:** UAV connectivity, identification, aur tracking (TR 23.754) — UTM se communications, unauthorized aerial end-devices detect/report.
- **Rel-17:** 5G enhancements for UAVs (TS 22.125, TS 22.829) — new UAV KPIs, connectivity requirements, command & control link, data payload, radio access node onboard UAV (**UxNB**), UAV service constraints. Application layer support (TR 23.755) — tracking/identification, UAv-UTM service interactions for location/route authorization, group communication.
- **Rel-18:** 5G-Advanced mein UAVs officially supported.

**Kyun important hai paper mein:** Poora survey academic research aur 3GPP standards ke beech bridge hai. Agar 3GPP ne kuch specify nahi kiya, wo commercially viable nahi hoga.

> **Yaad rakh:** 3GPP = rules banane wali body. Har Release = nayi capabilities ka package. Rel-17 mein UxNB (UAV as base station) officially introduced.

---

### UAV — Unmanned Aerial Vehicle
**Kya hai:** Simple — hawa mein udne wala vehicle bina pilot ke (drone). UAS ka ek component hai sirf.

**Classification:**
- **Type se:** Fixed-wing (fast, zyada range, hover nahi kar sakta) · Rotary-wing (helicopter style, hover karta hai, slow) · Hybrid (dono ka mix — VTOL + forward flight)
- **Size se:** Small/mini · Medium · Large (large mostly military/govt; small = delivery, agriculture, inspection)

> **Yaad rakh:** UAV = sirf hawa wala vehicle. UAS = full system (vehicle + control + links + support).

---

### UAS — Unmanned Aerial System
**Kya hai:** Poora system — sirf drone nahi. Ek UAV + yeh 4 cheezein:
1. GCS (Ground Control Station) — zameen pe human interface
2. Payload & data processing — camera, radar, sensors
3. Control & data transmission links — radio hardware/software
4. Support system — flight speed/data provide karta hai

**Kyun important hai:** 3GPP standardization mein, safe airspace integration ke liye poora system design karna hota hai — sirf vehicle nahi.

> **Yaad rakh:** UAS = UAV + uske control ka poora ecosystem.

---

### GCS — Ground Control Station
**Kya hai:** Zameen pe rakha terminal jahan se human operator drone ko command karta hai aur monitor karta hai.

**Security risk:** GCS ek single point of failure hai — agar GCS pe attack ho, to puri fleet ka control ja sakta hai.

> **Yaad rakh:** GCS = drone ka "cockpit" zameen pe.

---

### SAGSIN / SAGIN
**Full form:** Space-Air-Ground-Sea Integrated Network

**Kya hai:** 6G ka vision — ek giant wireless network jo space (satellites), air (UAVs/HAPS), ground (cellular towers), aur sea (maritime ships) sab ek saath connect kare. Abhi yeh sirf research vision hai.

**Scene:** Imagine kar ek single network jismein satellite se ocean mein ship bhi connect ho, aur zaroorat parne pe UAV relay kare traffic — sab seamlessly.

**Challenges:** Cross-domain routing (kaise data satellite se UAV pe aur phir tower pe jaaye), handover management, heterogeneity handle karna.

> **Yaad rakh:** SAGSIN = 6G ka "sab ek hi network" ka dream.

---

### IEEE P1920.1 / P1920.2 — Aerial Ad-hoc Network Standards
**P1920.1:** IEEE ka working group jo 2016 mein first standard for aerial ad-hoc networks (self-organized) banane ke liye bana. Draft standard December 2022 mein complete hua. Defines air-to-air communications for self-organized ad-hoc aerial networks [159].

**P1920.2:** Vehicle-to-Vehicle Communications ke liye currently under development.

**Kyun important:** Ye 3GPP ke alawa aerial networking ke liye dedicated IEEE standards hain — FANETs/IoD ka formal standardization track.

> **Exam tip:** 3GPP = cellular/UAV integration. IEEE P1920 = aerial ad-hoc network (FANET) standardization. Dono parallel tracks hain.

---

### Cross-layer Analysis (Survey's Holistic Approach)
**Kya hai:** Paper ka unique contribution — UAV communications ko sirf ek layer mein nahi, balki **cross-layer** analyse karna: physical → data link → network → transport layers sab cover kiye gaye hain.

**Kyun unique:** Previous surveys ek layer (jaise sirf 5G, ya sirf channel modeling, ya sirf routing) pe focus karte the. Ye survey "holistic, cross-layer analysis" deta hai.

**Paper contribution:** "encompassing physical, data link, network, and transport layers — unlike prior surveys that focus on isolated layers or specific use cases."

**Kyun important:** UAV problems (mobility, spectrum, security) ek layer tak limited nahi hote — cross-layer optimize karna padta hai. Isliye survey bhi cross-layer approach leta hai.

---

## PART 2 — UAV Network Types & Architectures

---

### Communication Architectures — 6 Types (Survey ka core)
Paper kehta hai: koi ek architecture sab ke liye fit nahi hoti. 6 main types hain:

| # | Type | Simple analogy | Main problem |
|---|------|----------------|--------------|
| 1 | **Direct links** | Walkie-talkie | LoS chahiye, urban mein block hota hai |
| 2 | **Satellite comms** | GPS/DTH | Latency zyada (120ms), heavy antenna |
| 3 | **Cellular (3GPP/5G)** | Apna mobile network | Best balance, interference issue |
| 4 | **IoD** | Smart city drone network | ZSP chahiye, complex |
| 5 | **FANETs** | Drone se drone relay | High mobility = topology changes |
| 6 | **Multi-UAV** | Fleet coordination | Star vs mesh tradeoffs |

**Solution:** Hybrid architectures — different link types ko combine karo.

---

### LoS / NLoS — Line-of-Sight / Non-Line-of-Sight
**Kya hai:**
- **LoS:** Transmitter aur receiver ke beech seedha rasta hai — koi obstacle nahi. *Jaise jugnu ko seedha dekh sako.*
- **NLoS:** Beech mein kuch hai — building, tree, pahad. Signal ko bounce/diffract karna padta hai.

**UAVs ke liye impact:**
- Direct links sirf LoS mein kaam karte hain — urban mein building block kar deti hain
- Satellite zyada NLoS coverage deta hai (upar se dekh raha hai)
- mmWave channels mein NLoS mein performance bahut kharab hoti hai

> **Yaad rakh:** LoS = seedha rasta. NLoS = kuch beech mein hai, signal ka chakkar lagana padega.

---

### FANET — Flying Ad-hoc Network
**Kya hai:** UAVs ka wireless network jismein koi fixed infrastructure nahi hai — UAVs directly ek dusre se baat karte hain. Ek "backbone UAV" hota hai jo GCS se connected hota hai, baaki sab usse connect hote hain.

**MANET/VANET se alag kyon:** MANET = ground pe mobile nodes. VANET = vehicles on roads. FANET = 3D space mein, bahut fast speed pe — topology bahut zyada dynamic hai.

**6 design parameters:**
1. **Network topology** — kaise connected hain sablog
2. **Mobility model** — har UAV ka 3D path kaise evolve hota hai
3. **Node density** — kitne UAVs per area (FANET mein bahut kam)
4. **Radio propagation model** — link quality predict karna LoS/NLoS mein
5. **Power consumption** — battery drain (payload bhi drains battery)
6. **Localisation** — har UAV ka precise position track karna zaroori

> **Yaad rakh:** FANET = infrastructure-free flying mesh network. 3D mein fast movement = biggest challenge.

---

### MANET / VANET
**Kya hai:** FANET ke "zameen wale cousins"
- **MANET** = Mobile Ad-hoc Network (pedestrians/general mobile devices)
- **VANET** = Vehicular Ad-hoc Network (cars on roads)

**Paper mein role:** Comparison baseline — FANET inse zyada hard hai kyunki 3D space mein aur bahut fast move karte hain.

---

### Cluster-based / Hierarchical FANET
**Kya hai:** Flat FANET se evolution — kuch UAVs "cluster leaders" ban jaate hain jo baaki UAVs ka traffic relay karte hain. Jaise class mein ek monitor hota hai jo teacher ko report karta hai, sabka nahi.

**Benefits:** Better coverage, energy efficiency, scalability.

**Techniques:** Distributed gateway selection, bio-inspired routing, load balancing.

---

### Bio-inspired Routing
**Kya hai:** Routing algorithms jo nature se inspired hain — bird flocking (boids), insect swarms, ant colonies. Simple local rules → global intelligent behavior emerge hota hai.

**UAVs mein use:** Cluster-based FANETs mein inter-cluster coordination ke liye. Decentralized, self-organizing — 3D dynamic environments mein robust.

> **Scene:** Murmuration dekha hai starlings ka? Thousands of birds, ek leader nahi, fir bhi perfectly coordinated move karte hain. Yahi bio-inspired routing hai.

---

### Boids / Reynolds Flocking Rules (Self-organization Foundation)
**Kya hai:** Craig Reynolds ka famous model (1986) — "boids" naam ke simple agents follow 3 simple rules to create realistic flocking behavior:
1. **Separation:** Paas ke boids se dur rehna (collision avoid)
2. **Alignment:** Nearby boids ki direction follow karna
3. **Cohesion:** Group ke center of mass ke paas rehna (don't get lost)

**Paper mein relevance:** "Self-organization is akin to flocking" — paper explicitly draws this parallel. High-quality wireless links among UAVs se boids-like self-organization possible hai.

**Limitation:** Real UAVs birds se jyada rigid hain (communication range, spectrum constraints, antenna design). Wireless link quality (fading, delay, protocol overhead) flocking behavior limit karta hai.

> **Scene:** Starlings ki murmuration = boids algorithm. 1000 drones ki coordinated swarm = same 3 rules applied to UAVs with communication constraints.

---

### Self-organization Recipe (Aerial Network Formation — Section E)
**Paper ka 4-step framework** for establishing self-organized aerial networks:

1. **Aerial node addressing schemes:** Existing standards (IEEE, FAA remote drone identification) use karke addressing scheme banana — unicast, multicast, broadcast support kare.
2. **Neighbor discovery:** Nearby UAVs ko discover karne ki strategy — communication range ke andar kaun kaun hai.
3. **Network formation:** Aerial nodes dynamically join/leave karne ke liye mechanisms — ad-hoc networking ke liye essential.
4. **Path planning and routing:** Real-time information share karne ke liye efficient path planning aur routing strategies.

**Kyun hard:** High mobility se wireless links unstable hote hain — isliye real-world mein partial infrastructure (satellite/cellular) often augment karta hai.

> **Exam tip:** Self-organization = 4 steps: Addressing → Neighbor Discovery → Network Formation → Path Planning/Routing.

---

### Centralized vs Decentralized Control
**Centralized:** Ek boss (GCS ya leader UAV) sab decisions leta hai. Simple, but single point of failure aur scale nahi hota.

**Decentralized:** Peer-to-peer — koi central authority nahi. Adaptive, robust. Swarms isi se resilient hote hain.

**Regime-Switching Systems:** Real missions dono switch karte rehte hain — mission phase ke hisaab se. Ek hi architecture pe fix nahi rehte.

---

### Cooperation Schemes (Multi-UAV Taxonomy — Section III.A)
**Kya hai:** Paper UAVs ke cooperation ko 4 distinct regimes mein classify karta hai (based on how UAVs coordinate). Real missions inme se koi ek dominant mode rehta hai at a given time-scale:

1. **Physical coupling:** UAVs physically connected hain — ek ka motion doosre pe directly depend karta hai (jaise connected modules/joined airframes).
2. **Formations:** UAVs specific shape mein fly karte hain (star, rectangle) aur distance/speed/acceleration maintain karte hain cooperative task ke liye. Example: 500 UAVs ki formation demo [15].
3. **Swarms:** Homogeneous UAV teams interact karke collective global behaviour generate karti hain. Decentralized communication se dynamic environment mein robust aur reliable.
4. **Intentional cooperation:** Har UAV ko global mission ke subtasks allocate hote hain, predefined trajectories follow karte hain. Centralized ya decentralized dono ho sakta hai.

**Kyun important:** Har scheme ka alag communication/networking requirement hai — isliye taxonomy padhna zaroori hai.

> **Yaad rakh:** Physical coupling = connected. Formations = shape. Swarms = collective behaviour. Intentional = task allocation.

---

### Regime-Switching Systems (Expanded)
**Kya hai:** Modern UAV missions hybrid/adaptive hote hain — fleet different phases mein in schemes ke beech dynamically transition karta hai. Paper isse "regime-switching systems" bolta hai.

**Formal definition:** Taxonomy ko "classification of dominant control and coordination structures at a given time-scale" samjho — rigid mission categories nahi, dominant mode hai.

**Example:** Mission start = formation flight → phir swarm for area coverage → phir intentional cooperation for task completion.

**Related:** Centralized vs Decentralized control dono regimes mein use ho sakta hai. Hybrid operations = regime-switching.

---

### IoD — Internet of Drones
**Kya hai:** Bahut saare UAVs ka internet-jaisa ecosystem. Har UAV connected hai, ek dusre se baat kar sakta hai, ground se bhi, aur cloud se bhi.

**IoD kya karta hai:**
- **UAV Traffic Management (UTM):** Multiple UAVs ko ek airspace mein coordinate karna
- **Flight Control:** Individual UAV paths ko network through control karna
- **Resource Optimization:** Bandwidth, compute, battery efficiently allocate karna
- **Mission Planning:** Multi-UAV missions coordinate karna
- **Network Connectivity:** UAVs ko broader internet se connect karna
- **Protocols:** Safe operation ke liye communication rules

**Architecture:** 2 pillars hain:
1. **Ad-hoc networking** (local UAV-to-UAV)
2. **ZSP** (Zonal Service Provider — backbone coordinator)

> **Scene:** Imagine Zomato's delivery fleet — har rider GPS pe track ho, orders coordinate ho, traffic patterns optimize ho. IoD wahi hai but for drones in 3D airspace.

---

### Low-Altitude Airspace as a Limited Resource
**Kya hai:** Zameen ke paas wala airspace (roughly 400-500 feet neeche) infinite nahi hai. Kaafi saare drones delivery, surveillance, emergency ke liye ek saath use karna chahte hain.

**Scene:** Jaise Delhi mein highway ek limited resource hai — bina coordination ke sab ek hi lane mein ghusenge aur accident hoga. Airspace mein bhi yahi hoga.

**Solution:** IoD isse road jaise manage karta hai — lanes (airways), speed limits, traffic management.

---

### UAV Traffic Management (UTM)
**Kya hai:** Drones ke liye automated ATC (Air Traffic Control). Manage karta hai:
- **Deconfliction:** Do UAVs ek hi jagah ek hi time pe na ho
- **Geofencing:** Restricted areas se drones bahar rahein (airports, govt buildings)
- **Priority:** Emergency drone ko delivery drone se zyada priority
- **Communication coordination:** Kaun sa frequency koun use kare

**UTM vs IoD:** UTM = application layer (kya manage karna hai). IoD = network layer neeche (kaise manage karna hai infrastructure-wise).

---

### ZSP — Zonal Service Provider
**Kya hai:** Ek specific geographic zone ka "local network manager." Jaise ek city mein municipal corporation hoti hai, ek airspace zone mein ZSP hota hai.

**ZSP kya karta hai:**
- Zone mein sab UAVs ki communication manage karta hai
- Local resources allocate karta hai (channels, edge servers, charging stations)
- Local UAVs aur broader internet ke beech interface
- Local ATC/UTM coordination

**Architecture mein role:** Ad-hoc networking = local UAV-to-UAV. ZSP = uska backbone/controller.

**Zonal kyun:** IoD zones mein divided hai. Adjacent zones ke ZSPs coordinate karte hain jab UAV boundary cross kare.

> **Scene:** Cellular network cells jaisa — har cell ek base station manage karta hai, inter-cell handover hota hai. ZSP = airspace ka base station.

---

### Ad-hoc Networking (FANET Context)
**Kya hai:** UAVs bina central tower ke directly ek dusre se baat karte hain. Har UAV dono hai — user bhi aur relay bhi.

**"Ad-hoc" ka matlab:** "Is specific purpose ke liye, abhi." Koi pre-built infrastructure nahi chahiye.

**Kaise kaam karta hai:** UAV A → UAV B → UAV C → Ground (message hop hota hai jab direct link nahi hai)

**Advantage:** Remote areas mein kaam karta hai, ek node fail ho to reroute ho jaata hai.

**Limitation:** Large scale pe coordinate karna mushkil — isliye ZSP aata hai.

---

### Airways / Flight Corridors
**Kya hai:** Sky mein designated "roads" for drones. Jaise highway lanes hoti hain cars ke liye, waise hi 3D paths defined hote hain UAVs ke liye.

**Why:** ZSP ko pata hona chahiye UAVs kahan honge — regulated paths se collision avoidance simpler ho jaata hai.

**Intersection:** Jahan do airways milte hain — road junction jaisi — carefully managed.

---

### Waypoints / Nodes (Airspace)
**Kya hai:** Sky mein named specific points jahan UAVs navigate karte hain — GPS waypoints ki tarah. Ye points hain: takeoff nodes, landing nodes, recharging nodes, mission nodes.

**Why useful:** UAVs free roam nahi karte — they follow defined sequences of waypoints, making UTM simpler.

---

### Intrazone Flights
**Kya hai:** Flight jo ek hi ZSP ke zone ke andar complete hoti hai. Simplest case — sirf ek authority manage kar rahi hai.

---

### Interzone Flights
**Kya hai:** Flight jo ek ZSP zone se doosre zone mein cross karti hai. Complexity zyada:
- Outgoing ZSP → incoming ZSP ko UAV handoff karna padta hai
- Dono ko coordinate karna padta hai
- Spectrum allocation bhi change ho sakta hai

**Cellular handover jaisa** — but airspace management ke liye.

---

## PART 3 — Wireless Technology Concepts

---

### mmWave — Millimeter Wave
**Kya hai:** Radio frequency band — wavelength 1-10mm, frequency roughly 30-300 GHz. 5G mein "mmWave" = 24 GHz aur usse zyada (FR2 bands — 28 GHz, 39 GHz).

**Why attractive:** Bahut zyada spectrum available → extremely high data rates (multi-Gbps)

**Catch (aur yeh bada catch hai):**
- **Bahut short range** — signal fast weaken hota hai
- **Easily block hota hai** — buildings, trees, rain... even humans block karte hain
- **LoS dependent** — NLoS mein poor performance
- Shorter wavelength → smaller antenna (UAV ke liye good), but range kam

**UAVs ke liye unique problem:** 3GPP channel models mmWave ke liye terrestrial measurements se banaye gaye (zameen level users). UAV altitude pe scene alag hai — no ground clutter, different building geometry. Isliye terrestrial models UAVs ke liye inaccurate hain.

> **Scene:** mmWave = laser pointer. Bahut powerful, bahut focused, lekin haath se rok lo to kuch nahi pahunchta. Regular 4G = floodlight — kam powerful lekin obstacles ke around jaata hai.

---

### Doppler Effect (UAV Communications)
**Kya hai:** Jab transmitter ya receiver move karta hai, signal ki frequency shift ho jati hai — jaise ambulance ka siren aate waqt high, jaate waqt low. Same phenomenon radio signals pe bhi hota hai.

**UAVs ke liye problem:** UAVs fast move karte hain (50-100+ km/h) → significant Doppler shift → channel estimation aur synchronization difficult ho jaata hai.

**Paper mein:** "Nodes in FANET are usually far away from the ground... sensitive to the doppler effects, changes in communication distance." Doppler = major physical layer challenge in FANETs.

> **Scene:** Ambulance siren — approaching = high pitch (frequency increased), receding = low pitch (frequency decreased). Wahi radio signals ke saath hota hai jab UAV fast move karta hai.

---

### MIMO — Multiple-Input Multiple-Output
**Kya hai:** Transmitter aur receiver dono pe multiple antennas. Multiple data streams simultaneously same spectrum pe — throughput aur reliability badhta hai.

**UAVs ke liye challenge:** 3D rapid mobility mein channel conditions continuously change hoti hain — MIMO ke liye accurate channel estimation zaroori hai.

> **Scene:** Ek hi road pe multiple lanes — zyada cars simultaneously, but sab lanes independently manage karna padega.

---

### Pilot Contamination (Massive MIMO for Cellular-Connected UAVs)
**Kya hai:** Jab multiple UAVs simultaneously same pilot sequences use karte hain → interference hota hai → channel estimation corrupt ho jata hai. "Pilot contamination" ka naam hai is problem ka.

**Paper mein:** Massive MIMO cellular-connected UAVs ke liye major challenge [147]. Solutions: interference-cancellation-based pilot decontamination.

---

### 3D Beam Tracking (Massive MIMO for UAVs)
**Kya hai:** Massive MIMO base station ko UAV ke 3D movement ko track karna aur beam continuously adjust karna — traditional 2D beam tracking se alag because UAVs 3D space mein move karte hain.

**Kyun hard:** UAV fast move karta hai → beam lag jayega. Plus pilot contamination.

---

### Kalman-filter-based Channel Tracking
**Kya hai:** Kalman filter (estimation algorithm) se UAV channel track karna — predicts future channel state based on past measurements.

**Paper mein:** [147] proposes Kalman-filter-based channel tracking for massive MIMO cellular-connected UAVs to maintain reliable aerial links despite 3D mobility.

---

### Virtual MIMO Links for IoT Data Collection
**Kya hai:** Multiple UAVs ke antennas ko collectively MIMO link banane ke liye use karna — "virtual" MIMO. Single UAV ke physical antennas nahi, but multiple UAVs aapas mein coordinate karke MIMO-like gains lete hain.

**Paper mein:** [144] studies UAV-aided data collection for IoT via virtual MIMO links — iterative algorithm maximizes collection efficiency using only large-scale CSI.

---

### Dual-functional MIMO (Communication + Jamming)
**Kya hai:** MIMO system simultaneously two kaam karta hai: (1) legitimate users se communicate, (2) unauthorized UAVs ko jam. Same antennas, same frequency, two functions.

**Paper mein:** [145] designs joint beamforming for dual-functional MIMO — communicates with legitimate users while jamming unauthorized UAVs. Effective even when total devices > antenna count.

---

### URLLC — Ultra-Reliable Low-Latency Communication
**Full form:** Ultra-Reliable Low-Latency Communication (5G feature)

**Kya hai:** 5G ka ek "service class" — extremely low latency (1ms target) aur extremely high reliability (99.9999% uptime) ke saath.

**UAVs ke liye relevance:** C2 (command and control) links ke liye zaroori hai. Agar C2 link mein latency zyada ho to drone control lose hoga.

**Satellite ka problem:** GEO satellite latency ~120ms hai — URLLC standards ke liye unacceptable.

---

### Spectrum Allocation & Spectrum Efficiency
**Spectrum allocation:** Frequency bands/channels UAV links ko assign karna — radio resource management. AI se optimize hota hai trajectory aur power ke saath jointly.

**Spectrum efficiency:** KPI — kitna data transmit hota hai per unit bandwidth. UAVs terrestrial users ke saath spectrum share karte hain — competition hai.

---

### Interference Handling / Interference Mitigation
**Kya hai:** Multiple transmitters (UAVs, BSs) ek hi spectrum share karte hain → signals ek dusre ko disturb karte hain → interference.

**Problem:** Cellular mein aerial UAVs kai BSs ke antennas directly dekh sakte hain → zyada interference sources.

**Solutions:** ML-driven scheduling, power control, user association optimization.

---

### ISM Band (2.4 GHz)
**Full form:** Industrial, Scientific, and Medical band

**Kya hai:** Unlicensed frequency band — Wi-Fi, Bluetooth, aur consumer drones sab isi band mein operate karte hain. "Unlicensed" = koi license fee nahi, lekin iska matlab hai crowded bhi hai.

**UAVs ke liye:** Direct links consumer UAVs mein widely used hai ISM band pe. Simple, cheap, but LoS limited aur urban areas mein interference prone.

---

### Ku / Ka Band (Satellite-Drone Links)
**Kya hai:** Satellite communication frequency bands.
- **Ku band:** ~12-18 GHz — standard satellite TV aur older satellite comms
- **Ka band:** ~26.5-40 GHz — newer, more capacity, weather sensitive

**UAVs ke liye:** WRC-2015 ne drones ke liye satellite comms approve kiye. Wide coverage milti hai. Con: latency, heavy antenna, expensive.

---

### Beamforming / Beam Management
**Kya hai:** Multiple antennas ka use karke signal ek specific direction mein "focus" karna — jaise torch ka light ek jagah concentrate karna. Random direction mein broadcast nahi karte.

**Benefits:** More signal to intended receiver, less interference to others, longer range.

**UAVs ke liye challenge:** UAV move kar raha hai → beam continuously track karna padta hai → AI/ML se beam prediction.

> **Scene:** Spotlight vs floodlight. Beamforming = spotlight. Precisely follow karna kisi ko — spotlight automatically rotate karta hai uske saath.

---

### Cell Handover (Handover Management)
**Kya hai:** Jab cellular-connected UAV ek base station se doosre mein move karta hai, to connection seamlessly transfer hota hai. Jaise phone call chalti rehti hai jab tum ek 4G tower se doosre mein move karte ho.

**UAV ke liye extra hard kyun:** 3D movement, high speed, aur aerial UAVs multiple towers simultaneously dekh sakte hain — handover decisions complex ho jaate hain.

---

## PART 4 — AI/ML in UAV Communications

---

### AI & ML in UAV Communications (Overview)
Paper ki Section V mein 7 automated network-level functions hain jo AI/ML optimize karte hain:

1. **Channel Estimation** — link quality measure karna
2. **Beamforming / Beam Management** — signal direction optimize karna
3. **Spectrum Allocation** — frequency band assign karna
4. **Interference Handling** — interference minimize karna
5. **Mobility Management** — 3D movement track karna
6. **Routing Management** — packet paths decide karna
7. **Security** — intrusion detection, anomaly detection

**Plus additional tasks:** Channel modeling, multi-modal learning, computation offloading.

> **Key insight:** Terrestrial networks ke liye bane algorithms UAV ke 3D dynamic environment mein directly kaam nahi karte — retrain aur adapt karna padta hai.

---

### Solution Approaches Classification (Graph-Theoretic / Optimization / Heuristic)
**Kya hai:** Paper ke "lessons learnt" section mein UAV problems solve karne ke 4 main approach categories:

1. **Centralized/Distributed:** Small scale pe centralized (simple), large scale pe distributed (scalable).
2. **Optimization Framework:** Convex (easier, global optimum guaranteed) vs Non-convex (hard, multiple local minima). Provides theoretical guarantees aur optimality gaps.
3. **Heuristic/Meta-heuristic:** Problem-specific heuristics vs general meta-heuristics (genetic algorithms, particle swarm). High abstraction level.
4. **Graph-theoretic Models:** UAV networks ko static ya dynamic graphs se represent karna — nodes = UAVs, edges = communication links. Most studies use static graph theory.

**Kyun important:** Same problem ko different approaches se solve kiya ja sakta hai — approach choice depends on scale, accuracy requirement, and computational resources.

> **Exam tip:** UAV problems = 4 solution families: centralized/distributed, convex/non-convex optimization, heuristics, graph theory. Sab apne apne trade-offs hain.

---

### Channel Modeling / Propagation Modeling
**Kya hai:** Mathematical/statistical description of how radio signals travel between transmitter and receiver.

**UAV channels ke 3 key characteristics:**
1. **Path angles** — signal paths kis angle pe arrive/depart karte hain
2. **Gains** — propagation ke baad signal power kitna bachta hai
3. **Delays** — multipath components kitne time spread mein aate hain

**Models:**
- **3GPP TR 38.901** — terrestrial-rooted (zameen level measurements se bana), UAVs ke liye imperfect
- **Ray tracing** — physically simulate karna (accurate, expensive)
- **Deep generative models** — AI se synthetic channels banana (middle ground)

---

### 3GPP Channel Models — Limitations for Aerial UAVs
**Problem:** 3GPP TR 38.901 model terrestrial measurements se bana hai. UAV 100-500m altitude pe hai → completely different geometry:
- BS antenna zameen ki taraf face karta hai, UAV upar se dekh raha hai
- Aerial UAV: no ground clutter, different building heights, different sky clutter
- Non-site-specific: specific city/environment replicate nahi kar sakta

**Paper kya propose karta hai:**
- **Ray tracing** — 3D building blueprints chahiye (accurate but computationally expensive)
- **Deep generative AI** — faster, more environment-specific

---

### Generative AI for Channel Modeling
**Kya hai:** Deep generative neural networks (GANs, diffusion models) se synthetic but realistic channel realizations generate karna — measured data ki jagah ya complement ke roop mein.

**Kyon useful:** Real UAV channels measure karna expensive aur time-consuming hai. AI se synthetic channels banao → test karo → model improve karo.

---

### CVAE — Conditional Variational Autoencoder (Channel Generator)
**Kya hai:** Dual-stage architecture for channel modeling:
1. **Stage 1:** LoS vs NLoS classify karo (link condition predict karo)
2. **Stage 2:** CVAE uss condition pe conditional hoke path losses, delays, angles compute karta hai

**Why useful:** Full multipath description generate karta hai bina site-specific assumptions ke.

---

### DCGAN — Deep Convolutional Generative Network (for Channels)
**Kya hai:** Channel parameters ko images mein convert karo → DCGAN se image generation karo (edge detection, spatial correlations learn karta hai).

**Insight:** Channel generation = image generation problem. CNNs spatially consistent synthetic channels generate kar sakte hain.

---

### Synthetic Multipath Channel Realizations — Key Limitation
**Problem:** Most generative models independent channel "snapshots" generate karte hain — marginal distribution capture hoti hai. Lekin **time evolution** capture nahi hoti.

**Kab problem hoti hai:**
- Multi-antenna (MIMO/ISAC) PHY algorithms ke liye — signal fluctuations over time chahiye
- Mobility ke saath radio access networks ke liye

**Open challenge:** Trajectory-aware, time-consistent channel generation.

---

### Ray Tracing (Channel Modeling)
**Kya hai:** Physics-based simulation — electromagnetic rays trace karo transmitter se receiver tak through a 3D environment (buildings, materials, positions).

**Advantage:** Site-specific — exact city ka digital twin ban sakta hai.

**Limitation:** Needs exhaustive 3D blueprint. Computationally very expensive for large UAV networks.

---

### Data-Driven / Site-Specific Channel Modeling
**Kya hai:** Physical locations (3D coordinates, elevation) ko channel characteristics se correlate karna via regression. Altitude-aware — elevation change karne se LoS interferers bhi change hote hain.

**Limitation:** Extensive real measurements chahiye. UAV-specific propagation "intricacies" capture nahi ho sakti fully. Isliye generative methods complement karte hain.

---

### Channel Estimation
**Kya hai:** Actual link quality real-time mein measure karna — kaafi path loss ho rahi hai, kya fading hai, kya interference hai.

**UAVs ke liye challenge:** Continuous 3D movement se channel continuously change hota hai → estimation ko fast aur accurate hona chahiye.

---

### Large-Scale vs Small-Scale Fading
**Large-scale fading:** Average signal strength ka gradual change as UAV moves (path loss, shadowing from buildings). Distance se dominated.

**Small-scale fading (Multipath):** Rapid fluctuations from multiple signal paths arriving at slightly different times — can cause constructive or destructive interference over very short distances (centimeters!).

**Scene (small-scale):** Tu swimming pool mein 2 stones daalta hai — ripples interfere karte hain. Kahin waves add hoti hain, kahin cancel. Wahi signal mein hota hai multipath se.

---

### Spatial-Temporal Consistency (Channel)
**Kya hai:** Channel model ka property — jab UAV move karta hai, channel "smoothly" evolve hona chahiye, suddenly jump nahi karna chahiye (physically unrealistic hoga).

**Why matters:** Independent snapshots isko miss karte hain — is open research problem ka hissa hai.

---

### gNB / gNodeB
**Kya hai:** 5G NR ka base station — LTE ke eNB ka successor. "g" stands for "next generation NodeB" (gNB).

**Paper mein:** "BS" aur "gNB" interchangeable use hote hain. TTS-CGAN UAVs aur gNBs ke beech large-scale RSS model karta hai jab UAV urban trajectory navigate karta hai.

---

### Spectrum Management for UAVs (Section F)
**Kya hai:** UAV networks ke liye radio spectrum allocate, manage, aur share karna — currently biggest challenge for commercial deployment.

**Current state — no dedicated spectrum for small commercial drones:**
- Commercial UAVs primarily ISM bands use karte hain (900 MHz, 2.4 GHz, 5.8 GHz) — congestion, short range, interference problems.
- RTCA ne C2 communications ke liye dedicated spectrum allocate kiya hai medium/large UAVs ke liye, but NOT for small commercial UAVs.
- FCC investigating:
  - **960-1164 MHz band** — interference concerns with Aeronautical Mobile Satellite (Route) Service (AMS(R)S)
  - **5030-5091 MHz band** — FCC 2020 report recommended this for UAV C2
  - **60-64 GHz band** — considering for drone operations with unlicensed field disturbance sensors (collision avoidance)

**Kyun spectrum management critical hai:** Safe operation, tracking, traffic management sab spectrum access pe depend karta hai.

---

### Spectrum Sharing Schemes
**Kya hai:** Jab multiple users (UAVs + terrestrial networks) same spectrum ko use karna chahte hain — sharing schemes batate hain kaise manage karna hai.

**Tin main types:**
1. **Opportunistic Spectrum Access:** UAVs "secondary users" hain — licensed users (primary) ke spectrum "holes" pe temporarily access lete hain. Spectrum sensing chahiye (temporal/spatial). Problem: UAV fast move karta hai → holes quickly invalid ho jaate hain.
2. **Competitive Spectrum Access:** Spectrum ke liye auction/bidding — MNOs (mobile network operators) sellers hain, UAVs buyers. Decentralized open market solutions bhi exist.
3. **Cooperative Spectrum Sharing:** Primary users aur UAVs explicitly cooperate — primary users spectrum share karte hain exchange mein UAVs se relaying ya cooperative jamming. Guarantees interference-free access but coordination overhead chahiye.

**Paper mein:** "Several spectrum sharing schemes have been developed to enable dynamic spectrum sharing between UAV networks and terrestrial networks."

> **Exam tip:** Spectrum sharing = UAVs ke liye critical kyunki dedicated spectrum nahi hai. Teen schemes: opportunistic (free rider), competitive (auction), cooperative (explicit deal).

---

### RSS — Received Signal Strength
**Kya hai:** Receiver pe signal kitna strong arrive kiya — simple measurement. Higher RSS = stronger link.

**TTS-CGAN mein use:** UAV ka RSS multiple gNBs ke saath condition pe kaisa evolve hota hai jab vo urban trajectory pe fly karta hai.

---

### TTS-CGAN / MTS-CGAN (Time-Series Conditional GANs)
**Kya hai:** Time-series data ke liye conditional GANs — channel data sequentially generate karte hain (trajectory-aware). MTS = Multi-variate Time Series version.

**UAV use case:** UAV trajectory ke saath RSS evolution predict karna across multiple gNBs.

---

### Generalization Across Environments
**Kya hai:** Channel models ka requirement — urban, suburban, rural — sab mein kaam karna chahiye. Training environment se alag environment mein bhi.

**Kyon hard:** Scattering density, building morphology, elevation statistics sab alag hote hain different environments mein.

---

## PART 5 — Sensor Systems & Data Collection

---

### Sensor Deployment (UAV)
**3 phases:**
1. **Sensor selection:** Mission ke liye right sensor type choose karna
2. **Pre-flight calibration:** Accurate measurements ensure karna takeoff se pehle
3. **In-flight stabilization:** Data blurry ya crooked nahi hona chahiye

**Simple truth:** Best communication architecture bhi bechaar hai agar sensor data hi galat hai.

---

### Sensor Modalities (UAV Payload)
Mission ke hisaab se sensor choose hota hai:

- **RGB Camera (8K):** Standard visual imaging. Mapping, surveillance, inspection.
- **Multispectral/Hyperspectral:** Human eye se pare light capture — crop health, mineral detection.
- **LiDAR:** Laser pulse se 3D map banana. Topographic mapping, autonomous navigation.
- **Thermal Infrared:** Heat camera. Search & rescue (andheron mein bhi kaam karta hai), building inspection.
- **Gas Analyzers:** CO2, methane detect karna. Environmental monitoring, leak detection.

**Choose kaise karo:** Mission target + required spatial resolution + spectral resolution ke hisaab se.

---

### Spatial Resolution vs Spectral Resolution
**Spatial Resolution:** Kitna detail camera dekh sakta hai — smallest distinguishable object.
- *Higher spatial res = more data = more bandwidth*

**Spectral Resolution:** Kitne precisely different wavelengths (colors of light) distinguish kar sakta hai.
- Regular RGB = 3 bands. Hyperspectral = 200+ bands.
- *Higher spectral res = more data = more bandwidth*

**Key insight:** Resolution requirements directly drive communication architecture choice — high-res = cellular chahiye, low-res = direct link might work.

---

### Radiometric Calibration
**Kya hai:** Sensor ka brightness measurement scale accurate hai ya nahi — check aur correct karna. Jaise thermometer calibrate karna hota hai, sensor ke liye brightness calibrate hota hai.

**Kyon zaroori:** Uncalibrated sensor ek hi condition mein alag-alag brightness values de sakta hai — comparison impossible ho jaata hai.

---

### Geometric Calibration
**Kya hai:** Sensor geometry accurate hai ya nahi — har pixel real world mein correct location pe correspond kare.

**Correct karta hai:** Lens distortion (barrel/pincushion), focal length variations, sensor alignment errors.

---

### Dark Frame Removal / Vignetting Correction
**Dark Frame:** Sensor ka "background noise image" — lens cap laga ke liya gaya. Subtract karo → noise remove.

**Vignetting:** Image ke edges center se darker hote hain (lens se light unevenly aati hai). Mathematically correct karo.

---

### Gimbal
**Kya hai:** Mechanical stabilization platform jo sensor ko steady rakhta hai jab UAV vibrate ya tilt kare — jaise professional camera ke stabilizer.

**Types:** 2-axis (roll + pitch) ya 3-axis (roll + pitch + yaw). 3-axis better hai.

**Active stabilization:** Gyroscope-driven motors continuously compensate karte hain.

**Passive/Dampers:** Vibration-absorbing materials jo motor vibrations filter karte hain.

---

### GNSS / INS (Navigation)
**GNSS (Global Navigation Satellite System):** GPS, GLONASS, Galileo, BeiDou — satellite se position. Accurate (~1m) lekin buildings mein ya GPS dropout mein fail.

**INS (Inertial Navigation System):** Accelerometers + gyroscopes se position track karna — bina satellite ke. Drift karta hai over time (~10-100m error per minute).

**Combined use:** GNSS primary, INS backup. GPS dropout → INS only → accuracy degrade hoti hai.

---

### COFDM — Coded OFDM
**Kya hai:** OFDM (data ko many small sub-channels mein split karna) + error-correction codes.

**Scene:** Highway ek lane ke bajaye 100 tiny lanes — ek block ho to baaki continue. Yahi COFDM hai wirelessly.

**UAV video ke liye perfect:** Interference resist karta hai, multipath handle karta hai, HD video long range pe.

---

### ISR — Intelligence, Surveillance, Reconnaissance
**Kya hai:** Military/operational term — UAV ki core mission category:
- **Intelligence:** Collected data analyze karna (5 vehicles found in building)
- **Surveillance:** Area continuously monitor karna over time (border watch)
- **Reconnaissance:** Ek baar ya periodic scouting (road passable hai ya nahi)

**Communication ke liye impact:** ISR = high data rate (HD video) + low latency + high reliability + security. Basically sabse demanding use case.

---

## PART 6 — Safety, Control & Operational Concepts

---

### C2 Communication — Command and Control
**Kya hai:** UAV aur GCS ke beech critical control link. Do directions:
- **Uplink (GCS → UAV):** Commands, mission updates, waypoints
- **Downlink (UAV → GCS):** Telemetry, sensor data, video

**CNPC:** Control and Non-Payload Communication — specifically command link ke liye. 3GPP defines KPIs: data rate 100 Kbps (C2), payload rate 50 Mbps, latency 50 ms.

**Why critical:** C2 link = UAV ki lifeline. Fail → uncontrolled flight → crash.

---

### C2 Communication Modes (4 Types — Section I / Table 5)
**Kya hai:** 3GPP defines 4 distinct C2 (Command and Control) communication modes for UAVs:

1. **Waypoint Steering:** UAV predefined waypoints follow karta hai — autonomous flight mode.
2. **Direct Stick Steering:** Human operator direct stick/controller se manually steer karta hai — like RC plane.
3. **Automatic Flight by UTM:** UTM (UAS Traffic Management) automatically flight manage karta hai — coordinated airspace.
4. **Approaching Autonomous Navigation Infrastructure:** UAV khud autonomous navigation infrastructure ke towards move karta hai — highest autonomy level.

**Kyun modes matter:** Har mode ke alag prerequisites hain — packet timing, message size, end-to-end delay. Table 5 mein KPIs mapped hain. Switching between modes during operation possible hai if requirements meet hote hain.

**3GPP video feedback:** Direct stick steering ke liye video feedback recommended hai (Table 6: video transmission parameters).

---

### C2 Station (Expanded)
**Kya hai:** Full ground control setup jismein hota hai:
- Mission planning software
- Real-time flight control
- Open API/SDK for custom automation (e.g., ArduPilot, Mission Planner, QGroundControl)
- Fail-safe monitoring

---

### Fail-safe Behaviors
**Kya hai:** Pre-programmed automatic emergency responses — human command ka wait nahi karte.

**Types:**
1. **Return-to-Home (RTH):** Link lost → automatically ghar wapas
2. **Low battery auto-land:** Battery threshold par → nearest safe landing
3. **Light patterns:** LED indicators — status dikhate hain

**Kyon critical:** 100m altitude, 2 min battery, link lost — human react nahi kar sakta fast enough. UAV khud react karta hai.

---

### Dual/Redundant RF Links
**Kya hai:** Do alag radio links simultaneously use karna (e.g., 2.4 GHz + 900 MHz). Ek fail → doosra backup lele.

**Kyon 2 frequencies:** Alag frequencies alag obstacles aur interference se affected hote hain. Frequency diversity = better reliability.

---

### Fault Tolerance (UAV / IoD)
**Kya hai:** System ki ability to keep working even when some parts fail.

**Tactics:** Redundant links, alternative routing, graceful degradation (critical functions prioritize karna), automatic failover.

---

### Loss of Control / Uncontrolled Flight
**Kya hai:** UAV ka C2 link fail ho jaata hai ya software crash — koi command nahi milti, drone apne aap fly karta hai (or crashes).

**Prevention:** RTH fail-safe, redundant links, geofencing (boundary se bahar nahi jaayega).

---

### Emergency Situation Handling (ZSP / IoD)
**ZSP ka role:** Zone mein emergency detect karna → affected UAVs ko alert karna → safe landing ya reroute coordinate karna → priority traffic (emergency vehicles) ke liye airspace clear karna.

---

### Handover Re-evaluation for IoD
**Problem:** Terrestrial cellular handover algorithms UAVs ke liye kaam nahi karte — aerial UAVs multiple BSs simultaneously see karte hain → frequent unnecessary handovers.

**Solution needed:** Altitude-aware, 3D-mobility-aware handover algorithms specifically for aerial users.

---

### Congestion Control Re-evaluation for Aerial Networks
**Problem:** Ground-level TCP/QUIC congestion control assumes ground-level packet loss patterns (mostly congestion-caused). Aerial links mein loss mostly channel-caused — algorithms unnecessary slow down karte hain.

**Solution needed:** UAV-specific congestion control jo aerial channel characteristics samjhe.

---

### Remote ID
**Kya hai:** UAV continuously apni identity broadcast karta hai (registration number, position, operator info). Jaise car ki license plate — airspace mein "who is this drone?"

**Why:** Safety aur accountability. ATC aur authorities identify kar sakein drone ko.

---

### BLoS — Beyond Line-of-Sight Communication
**Kya hai:** UAV operator direct line-of-sight se bahar hai — drone bahut door ya obstacle ke peechhe hai.

**Kya chahiye:** Cellular ya satellite link (direct link LoS pe tha). Redundant RF links. Reliable C2 even without visual contact.

---

### Urban Canyon Effect / Urban LoS Challenges
**Kya hai:** Dense urban areas mein tall buildings GPS signals aur radio signals dono block karte hain — aisa lagta hai jaise tum ek deep canyon mein ho.

**Effects:**
- GPS dropout (buildings satellites block karte hain)
- Multipath fading (signals buildings se bounce karte hain)
- Direct link failures (LoS blocked)

---

## PART 7 — Emerging Technologies

---

### Digital Twin (DT)
**Kya hai:** Physical system ka virtual replica jo real-time mein mirror karta hai — IoT data use karke monitoring, analysis, aur decision-making ke liye.

**Scene:** Imagine IIT Dharwad ka ek perfect 3D computer model jisme sab real-time data hai — classes kahan chal rahi hain, crowd kahan hai, etc. Uski koi change real building mein hone se pehle simulate kar sako. Wahi DT hai.

**UAVs ke liye uses:**
- Real-time operation monitoring
- Operator training (simulated environments)
- Network optimization
- Channel modeling (ray tracing ka digital twin)

**3GPP alignment:** DT for UAVs Rel-15 enhancements se aligned, Rel-16 ne build kiya (high throughput, low latency).

---

### RIS — Reconfigurable Intelligent Surface
**Kya hai:** Electronically controllable EM surface/array jo wireless signals ko reflect aur shape karta hai via phase-shifts. Jaise ek programmable mirror for radio waves.

**UAV-mounted RIS:** UAV pe RIS lagao → air-to-ground signals enhance ho → achievable rate significantly badhti hai. UAV trajectory aur RIS phase-shift jointly optimize karte hain.

**Additional benefits:** PHY-layer security improve hoti hai, efficient information+power transfer.

**Scene:** Sunlight focus karne ke liye mirror use karna — usi tarah radio signal reflect karke exactly jahan chahiye wahan concentrate karo.

---

### ISAC — Integrated Sensing and Communication
**Full form:** Integrated Sensing and Communication

**Kya hai:** Ek hi platform/waveform pe dono kaam — sensing (radar/camera) + wireless communication — simultaneously. 6G ka emerging technology.

**UAV-assisted ISAC:** UAV mein communication array + radar (ISAC-enabled). Radar real-time environment sense karta hai → communication beams steer hote hain usse.

**Challenges:** Joint sensing-communication design complex hai. Performance UAV applications ke liye fully investigated nahi hua abhi tak.

**Scene:** Chhichhori mein "ultrasound se genders pata chalti hai" wala scene yaad hai? Ek hi signal se detect bhi karo aur communicate bhi — ISAC wahi hai.

---

### 6G
**Kya hai:** 5G ka successor — abhi research phase mein (2030 ke aaspaas expect karte hain). Key features: sub-ms latency, terabit speeds, AI-native, SAGSIN integration.

**UAV relevance:** 6G mein aerial users first-class citizens hone chahiye — not an afterthought.

---

### HAP / HAPS — High Altitude Platform Station
**Kya hai:** Stratosphere mein (20-50km altitude) stationed platforms (balloons ya aircraft). Ground aur satellite ke beech — satellite ki tarah wide coverage, ground BS ki tarah lower latency.

**UAV ke saath difference:** UAV = low altitude, short duration. HAPS = very high altitude, long duration (weeks/months).

---

### FSO — Free Space Optical
**Kya hai:** Data transmit karna light beams (laser/optical) se air ke through — wire nahi, radio nahi. Very high bandwidth possible.

**Con:** LoS strictly required. Rain, fog, dust se highly affected.

**UAV use case:** Short-range high-speed backhaul links jahan LoS guaranteed ho.

---

### Full-Duplex UAV-Assisted Wireless Powered Communication
**Kya hai:** UAV simultaneously dono kaam karta hai — ek side ke nodes ko power wirelessly transfer karta hai, aur doosre side se data receive karta hai. Full-duplex = ek saath transmit + receive.

**Challenge:** Self-interference — khud ka transmitted signal khud ke receiver ko interfere karta hai.

---

### Multi-modal Learning & Federated Learning
**Multi-modal learning:** Multiple types of data (sensor fusion — camera + LiDAR + radar) simultaneously ek model mein process karna.

**Federated Learning:** Multiple UAVs/devices local data pe train karte hain, sirf model updates share karte hain (raw data nahi) — privacy preserve, bandwidth save.

**UAV application:** Multi-task offloading aur resource optimization ke liye.

---

### Computation Offloading (Multi-task Offloading)
**Kya hai:** UAV ka heavy computation (image processing, ML inference) edge server ya cloud pe shift karna — UAV ki battery bachao, faster processing karo.

**Multi-task:** Multiple computation tasks simultaneously offload karna. Trade-off: offloading task ke liye communication overhead.

---

### Edge Computing / Edge Services
**Kya hai:** Computation power cloud se neeche lana — network ke "edge" pe (base station, ZSP server) — low latency ke liye.

**UAV ke liye:** Sensor data cloud tak jaane ki bajaye nearby edge server pe process — latency bahut kam.

---

## PART 8 — IoT & Age of Information

---

### IoT — Internet of Things
**Kya hai:** Physical objects mein embedded sensors + connectivity — internet se baat karte hain bina human intervention ke. Smart thermostats, fitness watches, industrial sensors.

**UAV + IoT connection:** Static IoT sensors hain duniya bhar mein. UAVs fly karke unka data collect karte hain rapidly — "mobile data collectors" as a service.

---

### Age of Information (AoI)
**Kya hai:** Data kitna "fresh" hai — source pe kab generate hua vs. recipient tak kab pahuncha. Lower AoI = fresher data.

**Formula:** AoI = current_time − generation_time_of_last_received_update

**Scene:** Milk carton ka "best before" date — except yeh seconds mein change hota hai. Traffic data 5 second purana = useless. UAV AoI minimize karta hai fresh data deliver karke.

**UAV AoI minimize kaise karta hai:**
- Directly sensor ke paas fly karo (delay reduce)
- Intelligent trajectory plan karo (stalest data wale sensors pehle visit karo)
- Multiple UAVs parallel mein collect karo

---

### Correlation-Aware AoI (CA-AoI)
**Extension:** Sensors ka data correlated hai (temperature sensors paas mein ek jaise readings denge). CA-AoI isko model karta hai — correlated sensors ko baar baar visit karna wasteful hai.

**Optimization:** CA-AoI minimize karo while accounting for correlations — different trajectories, different visit frequencies.

---

### Data Timeliness / Data Freshness
**Timeliness:** Data deliver hone ki speed after generation.
**Freshness:** Data use hone ke waqt kitna recent hai.

**ITS mein:** Traffic data 2-3 second purana = useless. Real-time chahiye.
**Textile IoT mein:** Worker safety sensor stale data = missed emergency.

---

### UAV as Data Mule / Data Ferry
**Kya hai:** UAV physically data carry karta hai — remote IoT sensors se collect karo, base station tak deliver karo. Jaise postal service — except digital data aur hawa mein.

**Kab useful:** Remote areas, no cell towers, sensors sirf short-range wireless support karte hain.

**Disadvantages:** Flying time = delay (instantaneous nahi). Battery/capacity limited.

---

### Data Aggregation & Dissemination (IoD)
**Aggregation:** 100 UAVs, 500 sensors — sab data ek useful summary mein compress karna. In-network: UAV locally summarize karo, raw data mat bhejo.

**Dissemination:** Aggregated data relevant parties ko send karna (ZSP, ATC, cloud, other UAVs).

**ZSP as hub:** Zone ke sab UAVs ka data collect karo, process karo, redistribute karo.

---

### UAV-Assisted Data Dissemination (Infrastructure-less IoT)
**Kya hai:** UAV ek "data disseminator" ki tarah kaam karta hai — data distribute karta hai widely dispersed IoT devices tak, un areas mein jahan koi fixed network infrastructure nahi hai (no cell towers, no WiFi). Jaise ek floating Wi-Fi router jo farms ya disaster zones mein data deliver karta hai.

**Kaise kaam karta hai:** UAV geographic area mein fly karta hai, sensor data collect karta hai, phir updates wapas IoT devices tak deliver karta hai — sab devices pe synchronized data maintain karke. Resource allocation + 3D mobility jointly optimize karta hai to reduce delay.

**Kyun important hai paper mein:** Infrastructure-less scenarios (remote farms, disaster zones) mein fixed network nahi hai — UAV hi single practical solution hai for synchronized data across all dispersed nodes.

> **Scene:** Jaise newspaper delivery boy jo har gaaon mein akhbaar pahunchata hai — UAV wahi hai for digital data across IoT sensors.

---

### Infrastructure-less IoT Scenarios
**Kya hai:** IoT deployments jahan koi fixed communication infrastructure nahi hai — no cell towers, no fiber backhaul, no WiFi.

**Examples:** Remote farms (precision agriculture), dense forests (environmental monitoring), disaster zones (collapsed cell towers), offshore platforms.

**Kyun UAVs critical:** Traditional IoT fixed infrastructure pe rely karta hai. Infrastructure-less mein UAV hi data mover hai — collect bhi karega, disseminate bhi karega. Bina UAV ke ye scenarios practically impossible hain.

---

### Precision Agriculture
**Kya hai:** Farming mein IoT + UAV use karna — soil sensors, crop-health cameras, weather stations. UAV fields ke upar se fly karta hai, data collect karta hai, farm ki IoT system tak deliver karta hai.

**UAV role:** High-res imagery + sensor data → crop stress, irrigation need, pest detection. Timely data = better yield, kam paani waste.

**Kyun paper mein:** Example of "data dissemination across widely dispersed IoT devices" — farm sensors kilometres apart hain, UAV unhein sync karta hai.

---

### Environmental Monitoring
**Kya hai:** Forests, rivers, air quality ko distributed sensors se monitor karna. UAV widely dispersed sensors se data collect karta hai (jo manually reach karna mehenga ya dangerous hai).

**Example:** Wildfire detection — forest mein temperature/humidity sensors, UAV rapidly readings collect karta hai, fire risk predict karta hai before it spreads.

---

### Emergency Services & Public Safety (Disaster Response)
**Kya hai:** Disaster areas (earthquake, flood, fire) mein cell towers down ho sakte hain. UAV rapidly data disseminate karta hai + real-time info emergency response teams tak pahunchata hai.

**UAV role:** Affected area ka map deliver karo, survivor locations relay karo, coordination data provide karo. "Timely decision making" aid karta hai → better disaster response.

**Kyun paper mein:** Explicitly listed as key application — UAV-assisted dissemination "plays a vital role in emergency services and public safety."

---

### Telemedicine Data Transport
**Kya hai:** UAV medical data (patient vitals, scans, ECG) transport karta hai remote location se healthcare facility tak.

**Kyun important:** Remote villages mein bandwidth low ya network down hai — UAV physically data carry karta hai, jo network se faster hai. Timely diagnosis lives save karta hai.

> **Yaad rakh:** "Data carrier" (data mule) ka yahi concept — bas yahan payload medical hai, not just sensor readings.

---

### Non-Convex Optimization (UAV Context)
**Kya hai:** Optimization problem jahan objective function "non-convex" hai — multiple local minima hote hain, global best find karna hard hai.

**UAV context:** Jointly optimize resource allocation + UAV 3D trajectory → non-convex ban jaata hai kyunki trajectory, power, aur scheduling non-linearly interact karte hain.

**Kyun hard:** Standard gradient descent global optimum guarantee nahi karta. Specialized algorithms chahiye (jaise jo neeche mention hai).

**Paper mein:** [92] ka problem "formulated as a non-convex optimisation task" for maximizing UAV-assisted data dissemination efficiency.

---

### Alternating Descent / Concave-Convex Procedures (CCCP)
**Kya hai:** Non-convex problems solve karne ki technique — problem ko sub-problems mein tod do, unke beech alternate karo.

**Concave-convex procedure (CCCP):** Non-convex function ko convex + concave parts mein decompose karo, iterate karo — har step pe solvable ban jaata hai.

**Paper mein:** [92] uses "combination of alternating descent and concave-convex procedures" to maximize efficiency of UAV-assisted data dissemination.

> **Yaad rakh:** Non-convex = tricky optimization (bohat saare local minima). CCCP = tod ke solve karo, phir doosra part solve karo, repeat.

---

### Ant Colony Optimization (ACO)
**Kya hai:** Bio-inspired optimization algorithm — ants ke foraging behaviour se inspired. Artificial "ants" pheromone trails deposit karke best path dhoondte hain.

**Paper mein:** [89] correlation-aware AoI problem solve karne ke liye ACO use karta hai (normalized weighted sum minimize karne ke liye).

**Why useful for UAV:** Trajectory planning aur routing mein ACO achha hai — UAVs ko best path/visit-order find karna (TSP-like problems). Bio-inspired routing se related hai (PART 2).

> **Exam tip:** Optimization toolbox: Non-convex (hard math), CCCP (decompose), ACO (bio-inspired search), PSO (swarm-based search). Sab different problems ke liye.

---

### Particle Swarm Optimization (PSO)
**Kya hai:** Bio-inspired optimization — birds ke flocking behaviour se inspired. "Particles" (candidate solutions) apne velocity update karte hain by blending: apna best-known position + swarm ka best-known position.

**Paper mein (K. Resource Optimization, line 1633):** [244] ne **PSO stepwise process** propose kiya to serve all users with few UAV-BSs while optimally calculating 3D spatial coordinates.

**Why useful for UAV:** 3D placement, trajectory, resource allocation — continuous optimization problems jahan gradient nahi milta. ACO ke saath compare: ACO discrete paths ke liye, PSO continuous coordinates ke liye.

> **Exam tip:** PSO = swarm search in continuous space. ACO = ant path search. Dono bio-inspired, dono UAV placement/routing ke liye.

---

### 3D UAV Placement Optimization
**Kya hai:** UAV-BS / UAV-relay / UAV-sensor ka **optimal 3D position** (x, y, altitude) find karna so user coverage maximize ho aur transmission power minimize ho.

**Paper mein (line 1628-1641):**
- 3D placement + coverage probability = main problems of interest.
- [244] PSO use karta hai 3D coordinates set karne ke liye.
- [95] (Alzenad et al.) UAV-energy-efficient BS placement — nonlinear integer problem, optimal 2D+3D coordinates decoupled way mein, **CVX solver** se solve.

**Kyun hard:** Altitude ↑ → LoS probability ↑ (better link) but path loss ↑ (distance ↑). Trade-off optimize karna padta hai.

> **Exam tip:** 3D placement = UAV-BS ko sahi jagah aur height pe rakhna. Altitude ka trade-off: zyada height = zyada LoS par zyada path loss. CVX = convex solver, PSO = heuristic solver.
---

### Intelligent Transportation Systems (ITS)
**Kya hai:** Smart traffic management — connected cars, real-time monitoring, autonomous vehicles.

**UAV + ITS:** Aerial perspective → bird's eye view of traffic. UAV can see entire intersection at once vs. ground cameras.

---

### Textile IoT / Smart Textiles
**Kya hai:** Sensors embedded in fabric/clothing. Worker safety monitoring, health tracking.

**UAV relevance:** Large construction sites mein workers ke smart uniforms se UAV fly karke sab data collect karta hai simultaneously.

---

### Tactile Internet
**Kya hai:** Internet jo **touch/feel** transmit karta hai real-time — ultra-low latency network for remote physical interaction (jaise remote surgery, haptic control).

**AoI connection:** Tactile internet mein data freshness CRITICAL hai — even 1ms delay = failed remote operation. Isliye paper ne isko AoI timeliness ka example diya hai (ITS aur command-control ke saath).

**Example:** Remote surgeon robot ko control karta hai — agar AoI high hai, surgery fail ho sakti hai.

> **Exam tip:** AoI applications ke 3 examples: ITS (traffic), Textile IoT (worker safety), Tactile Internet (remote touch/haptics).

---

### Cooperative UAV Systems / Swarm Coordination
**Kya hai:** Multiple UAVs ek team ki tarah kaam karte hain — individual actions nahi, coordinated strategy.

**Strategies:** Task allocation, data relaying, position sharing, load balancing.

**Mobility control in cooperative systems:** Sabki trajectories jointly optimize hoti hain fleet-wide AoI minimize karne ke liye — much harder than single UAV.

---

### Drone Light Shows / Swarm Shows
**Kya hai:** Coordinated swarms of drones with LEDs — programmable aerial displays. Thousands of drones precisely position maintain karte hain.

**Technical requirement:** Precise positioning, reliable C2, tight synchronization, collision avoidance.

**IoD application:** Example of cooperative UAV systems at scale.

---

## PART 9 — Security

---

### Security in UAV Networks
**Threats:**
- **Spoofed IDs:** Fake UAV identity broadcast karna
- **DoS attacks:** ZSP ya C2 link overwhelm karna
- **Flooding:** Network traffic se jam karna
- **Backdoors:** Compromised firmware
- **Location leakage:** Lost node ki position mission data reveal kar sakti hai

**Defense methods:**
- **ML-based anomaly detection:** Normal behavior se deviation detect karna
- **Jamming identification:** Intentional interference detect karna
- **PHY-layer security:** RIS use karke eavesdropping prevent karna
- **AES-256 encryption:** Data scramble karna
- **Authentication protocol:** Sender identity verify karna
- **Frequency hopping:** Rapidly switch frequencies — jamming resist karna

---

### AES-256 Encryption
**Kya hai:** Military-grade encryption. "256" = 256-bit key — practically unbreakable by brute force. C2 commands aur sensor data encrypt karta hai.

---

### Frequency Hopping
**Kya hai:** Transmission ke dauran rapidly between multiple frequencies switch karna. Jammer ek frequency jam kare → signal dusri pe hop kar jaata hai.

**Anti-jamming technique.** Also used in Bluetooth.

---

### Authentication Protocol
**Kya hai:** "Kya tum wo ho jo tum claim karte ho?" — identity verification. Prevents spoofing (impersonator ko C2 commands mat bhejo).

---

### Anti-Jamming Strategies
**Combined techniques:** Frequency hopping + spread spectrum + directional antennas + redundant links. Together jamming practically impossible banate hain.

---

### Blockchain in UAV Networks
**Kya hai:** Blockchain (distributed, tamper-proof ledger) ko UAV networks mein use karna for security, trust, aur decentralized coordination.

**Paper mention:** Intro mein listed as ek technology jo 6G ke through UAV networks ko support karta hai — "robust and more heterogeneous applications."

**UAV use cases:**
- **Decentralized trust:** Bina central authority ke UAVs ka trust establish karna (Sybil attack resist karna)
- **Secure logging:** Mission data immutable record (tamper-proof audit trail)
- **Smart contracts:** Automated coordination rules between UAVs/operators
- **Identity management:** UAV identities ki tamper-proof verification

**Kyun relevant:** Traditional security (AES, auth) centralized hai — blockchain decentralized alternative deta hai jo swarm/edge scenarios mein useful hai.

> **Exam tip:** Blockchain = decentralized security layer. PART 9 ke baaki methods (AES, auth, freq hopping) centralized ya pairwise hain; blockchain distributed trust add karta hai.

---

### BFT / Byzantine Fault Tolerance (aur ACBFT)
**Kya hai:** Blockchain consensus mechanism jo malicious/ faulty nodes ("Byzantine" nodes jo jhooth bolte hain) ke against tolerate karta hai — network tab bhi sahi chalta hai agar majority honest ho.

**UAV context (paper line 1529-1536):**
- Blockchain-enabled **zero-trust** UAV networking use karta hai **mobility-aware BFT** mechanisms.
- **ACBFT (Adaptive Chained Byzantine Fault-Tolerant):** UAV ad-hoc networks ke liye tailor kiya gaya — dynamic committee election + micro-block pipelining + mobility-aware fault handling. Traditional BFT se kam consensus latency aur overhead.

**Kyun important:** Swarm mein koi UAV compromise ho jaye (Sybil/internal attack) toh BFT ensure karta hai baaki swarm correct state maintain karein.

> **Exam tip:** BFT = tolerate malicious nodes. ACBFT = UAV-specific adaptive version (mobility-aware). Zero-trust + blockchain + BFT = paper ka advanced security stack.

---

### Security Requirements for UAV Networks (7 Requirements)
**Kya hai:** Paper defines 7 main security requirements for UAV/FANET systems (line 1608):

1. **Confidentiality:** Information exchange hide karna — outside nodes ko FANET ke plans/actions nahi pata chalne chahiye.
2. **Integrity:** Transferred information intentionally ya unintentionally alter nahi ho sakti — tampering detect karna.
3. **Availability:** Network down nahi hona chahiye — jamming, DoS, node failure se bachna. GNSS jamming bhi availability threat hai.
4. **Privacy:** Identification information aur transactions protect karna. Three types: Data privacy, Routing/protocol privacy, Application/position privacy.
5. **Authentication:** Verify karo ki node jo claim kar raha hai wahi hai (spoofed UAV reject).
6. **Access Control:** Sirf authorized nodes ko network resources/commands access milein.
7. **Non-repudiation:** Koi node apni bheji hui message ya action ko later deny nahi kar sakta — accountability ensure hoti hai.

**Paper mein:** Table 7, 8, 9 analyze threats according to connection vector, node vector, aur OSI layers. Table 10 summarizes mitigation mechanisms.

> **Exam tip:** Traditional CIA + Privacy = 4 (C.I.A.P.). Paper ka full list = 7: add Authentication, Access Control, Non-repudiation. Non-repudiation = "maine ye nahi bheja" claim nahi kar sakta.

---

## PART 10 — Quality Assurance & Post-Mission

---

### Health Monitoring / Ongoing Health Monitoring
**Kya hai:** Continuous real-time monitoring of UAV subsystems:
- Battery voltage aur current
- Motor performance aur temperature
- GPS signal strength
- Communication link quality

**Threshold violation:** Koi parameter safety limit cross kare → automatic response trigger.

---

### Automated Post-Mission Checks
**3 main checks after each mission:**
1. **Missing frames:** Video ya sensor data mein gaps (link drops se)
2. **SNR anomalies:** Signal quality ke problematic segments
3. **GPS dropouts:** Position data unavailable periods

**Purpose:** Patterns identify karo → future missions improve karo.

---

### Signal-to-Noise Ratio (SNR)
**Kya hai:** Useful signal / background noise ka ratio. Higher SNR = cleaner data.

**Scene:** Concert mein baat karna = low SNR (music = noise, voice = signal). Library mein = high SNR.

**SNR anomalies:** Sudden drops → interference ya NLoS transition. Intermittent → multipath ya weather.

---

### GPS Dropout
**Kya hai:** GPS signal lost ya severely degraded — UAV ko nahi pata kahan hai.

**Causes:** Urban canyon (buildings block satellites), indoor, RF jamming, solar weather, multipath.

**Effect:** INS-only mode → drift badhta hai over time. Sensor data ka position tag nahi hoga → mapping useless.

---

### Log File Analysis (Post-Mission)
**Kya hai:** Mission ke baad flight logs analyze karna — "black box" analysis for drones.

**Log mein hota hai:** GPS trail, sensor frames, battery history, communication signal strength, events/errors.

**Goal:** Efficiency identify karo, patterns nikalo, next mission better plan karo.

---

### Quality Assurance & Feedback Loop (Design Aspect 6)
**Closed loop:** Fly mission → collect data → automated post-mission checks → log analysis → identify issues → improve next mission → fly again.

**Why a "loop":** Improvements are continuous — each mission feeds the next.

---

## PART 11 — Network Architecture Details

---

### HAP-Assisted Architecture
**Kya hai:** High-altitude platform (stratosphere mein) ground BS ki tarah kaam karta hai — zyada area cover karta hai single BS se.

**Tradeoff:** Lower latency than satellite, larger coverage than terrestrial BS, but atmospheric effects.

---

### Satellite Constellations: LEOSat / OneWeb
**LEO (Low Earth Orbit):** ~550-2000 km altitude. OneWeb: 720 satellites, 50 Mbit/s throughput, latency under 50 ms — much better than GEO satellites.

**GEO:** 36,000 km altitude — 120ms+ latency. Not suitable for URLLC.

---

### FlyBS / Fly-RRH
**FlyBS (Flying Base Station):** UAV as aerial cellular base station — extends coverage on demand.

**Fly-RRH (Flying Remote Radio Head):** UAV as aerial radio unit connected to ground core.

**Performance:** 11x higher throughput than small cell, 5.3x energy efficiency improvement (FlyRRH numbers).

---

### Micro UAV Airborne Communication Relay
**Kya hai:** Small UAV physical communication relay ke roop mein — terrestrial nodes ko range extend karne ke liye bridge karta hai.

---

### Self-healing Communication Networks / Network Healing
**Kya hai:** Network khud apne aap ko repair karta hai jab koi link ya node fail ho jaye — bina human intervention ke.

**Paper mein:** Listed as relay challenge: "specialized communication network healing [111]" — UAV relay networks ko automatically reconfigure karna chahiye jab ek relay fail ho.

**BITS example:** Battlefield Information Transmission System (BITS) [106] — military relay scenario mein self-healing crucial hai (node destroyed ho to baaki network survive kare).

**Techniques:** Redundant paths, automatic rerouting, mesh recovery, relay re-positioning.

---

### UAV Roles in Networks (Taxonomy — Fig 12 / Fig 2)
**Kya hai:** Paper ek taxonomy deti hai — UAVs ek hi hardware pe alag-alag *roles* le sakte hain, depending on intended usage. Figure 12 (aur Fig 2) mein individual use cases dikhaye gaye hain. Teen primary roles allocate ho sakte hain:

1. **UAV as Base Station** → dekho `FlyBS / Fly-RRH` entry
2. **UAV as Relay Station** → dekho `Micro UAV Airborne Communication Relay` entry
3. **UAV as Sensor and/or Actuator** → neeche entry

**Kyun important hai:** Same UAV fleet different missions mein different roles play kar sakti hai — isliye "role allocation" ek optimization problem hai (kaunsa UAV kya karega).

---

### UAV as Sensor and/or Actuator
**Kya hai:** UAV sirf data collect (sensor) nahi karta — physically *act* bhi karta hai world pe via **actuators** (motors, sprayers, grippers, drop-mechanisms).

**Actuator kya hai:** Wo component jo signal ko physical action mein convert karta hai — jaise printer ka ink droplet, ya drone ka pesticide sprayer. Sensor = "dekhta hai", actuator = "karta hai".

**Examples:**
- **Sensor only:** Surveillance, mapping, environmental monitoring (camera/LiDAR collect karta hai)
- **Sensor + Actuator:** Precision agriculture (crop scan karega + fertilizer spray karega), package delivery (locate + drop), search-and-rescue (detect + supply drop)
- **Actuator heavy:** Cargo transport, emergency supply delivery

**Paper context:** Ye teesra role hai UAV taxonomy ka — base station aur relay se alag kyunki ye *physical world pe direct effect* daalta hai, sirf bits nahi bhejta.

> **Yaad rakh:** Sensor = eyes, Actuator = hands. UAV as Sensor/Actuator = dekhta bhi hai aur kaam bhi karta hai.

---

### Satellite-Ground Integrated Network
**Kya hai:** Satellite + ground cellular ki hybrid — SAGSIN ka subset. ML se resource optimization jointly terrestrial aur satellite mein.

---

### Multi-modal Learning (Channel Models)
**Kya hai:** Alag-alag data types simultaneously ek ML model mein — e.g., channel parameters + location + weather — better prediction.

---

### Mission Planning (UAV / IoD Context)
**Kya hai:** Mission se pehle: route plan, waypoints define, fuel/battery plan, sensor settings, contingencies.

**IoD-enabled:** Network se weather, airspace restrictions, other UAVs ki positions — sab real-time data available → better planning.

---

### Network Integration / Network Connectivity (UAV-to-Internet)
**Kya hai:** UAV ka connection broader internet se — cloud services, remote operators, database access.

**Why important:** Remote services enable karta hai — firmware updates, AI inference on cloud, real-time maps.

---

### Cloud Data Offloading / Sensor Data Streaming
**Cloud offloading:** UAV ka heavy data (video, LiDAR) cloud pe push karna real-time mein — onboard storage nahi chahiye.

**Sensor data streaming:** Continuous real-time data stream UAV se cloud/edge tak. Low latency aur reliable link zaroori.

---

### ATC Integration for UAVs
**Kya hai:** UAV systems ka integration with existing Air Traffic Control. Challenge: traditional ATC radar low-altitude mein kaam nahi karta aur drone density bahut zyada hai manned aircraft se.

**IoD provides:** Network layer jo ATC coordination ke liye connectivity deta hai.

---

### Ground Recharging Stations
**Kya hai:** Drone ke liye charging/battery-swap stations. Mission planning mein: location, availability, queue time, compatibility, weather — sab IoD network se real-time information.

---

### Aerial Vehicle Course Optimization Algorithms
**Kya hai:** UAV ke optimal flight path compute karna given mission objectives.

**Levels of autonomy:** Manual → semi-autonomous → fully autonomous. More autonomy = better optimization but harder to certify safely.

---

### Open API / SDK (UAV Mission Planning)
**Kya hai:** Programmable interface for UAV missions — custom scripts, third-party tool integration.

**Examples:** Mission Planner, QGroundControl, DroneKit (open source).

---

### KPIs for UAV Communication Architectures (Table 4)
**8 KPIs compared across architectures:**
1. Latency
2. Throughput
3. Spectrum efficiency
4. Interference level
5. Outage probability
6. Power efficiency
7. Reliability
8. Safety/Security

**Key numbers (from Table 4):**
- FlyRRH: 11x throughput improvement over small cell
- Cellular single UAV at 15m: DL 5 Mbps, UL 1.5 Mbps, ping 100ms
- CNPC: data rate 100 Kbps, payload 50 Mbps, latency 50 ms
- OneWeb: 50 Mbit/s, latency < 50 ms

---

### Middleware (UAV / IoD Context)
**Kya hai:** Software layer UAV aur network services ke beech — hardware/platform differences abstract karta hai. Different manufacturers ke UAVs ek hi IoD network pe kaam kar sakein.

**Vendor-Independent Control:** Middleware isliye important hai — ek manufacturer ke protocol doosre ke liye kaam nahi karta. Unified interface chahiye.

---

### Mission-Critical Algorithms
**Kya hai:** Algorithms jo fail hone pe physical damage ya injury ho sakti hai — collision avoidance, geofencing, fail-safe behaviors, loss-of-control recovery.

**Kyon "critical":** Movie recommendation algorithm fail → bad movie. Mission-critical algorithm fail → drone crashes into building ya person.

**IoD ki responsibility:** Ensure karna ki sab certified, up-to-date mission-critical algorithms sab UAVs pe available hain.

---

### Simulation Environment (UAV / IoD)
**Kya hai:** Virtual world jahan real deployment se pehle sab test karo — jaise flight simulator for drones lekin poore IoD ecosystem ke liye.

**Why essential:**
- Safety — 100 real UAVs pe test karna dangerous hai, simulation mein crashes free hain
- Cost — real flight tests expensive hain
- Repeatability — exact same scenario 1000 baar run karo
- Edge cases — 1000 UAVs ek zone mein → real mein impossible test

---

### Resilient Protocols (UAV / IoD)
**Kya hai:** Protocols jo problems ke bawajood kaam karte rehte hain. "Resilient" = bend but don't break.

**Tactics:** Redundant paths, graceful degradation (critical messages prioritize karo), fast recovery, error correction, jamming resistance.

**IoD mein kyon critical:** Protocol failure = UAV loses ZSP connection = uncontrolled hazard. Resilience = safety requirement, not just nice-to-have.

---

### UAV-Oriented Remote Services
**Kya hai:** Cloud/network-based services specifically for UAVs — remote flight control, mission planning, sensor data processing, firmware updates, monitoring, airspace management.

**"UAV-oriented" kyon:** Generic cloud nahi — aviation-specific needs: low latency, 3D spatial awareness, safety-critical operation.

---

### Regulated Flight Paths
**Kya hai:** Officially authorized routes UAVs ko follow karne chahiye. ZSP/aviation authority define karta hai airways, waypoints, altitudes, speed limits.

**Kyon regulation zaroori:** Bina regulation ke UAVs conflicting routes choose karein → collision hazards. Regulation se: collision avoidance simpler, spectrum planning easier, airspace capacity badhti hai.

---

### Mission Plan Enforcement (ZSP Role)
**ZSP ensures:** UAV apne approved mission plan se deviate nahi karta.

**Kaise:** Position broadcasting compare karo planned trajectory se → deviation detect karo → alert karo ya intervene karo.

---

### Control Information Relaying (ZSP Role)
**Kya hai:** ZSP C2 commands aur control information relay karta hai jab direct link possible nahi — especially BVLOS operations mein.

---

### Weather Updates (UAV Operations)
**IoD se available:** Wind speed, precipitation, visibility, temperature — real-time near UAV's planned route.

**Kyon crucial:** UAVs especially small ones wind se bahut affected hote hain. Mission plan adjust karo agar weather bad hai.

---

### Crucial Geographic Information (IoD-Accessible)
IoD-connected UAVs ko milti hai real-time:
- ATC data (other aircraft positions)
- No-fly zones (geofencing data)
- Ground recharging station locations + availability
- Building/obstacle maps
- Emergency event locations
- Weather data

---

### Cyber-Physical Environment (IoD Context)
**Kya hai:** Physical reality (buildings, weather) + cyber/digital systems (networks, software) ka combination jisme IoD operate karta hai.

**Why matters for design:** Har location ka alag cyber-physical environment hai — urban dense city ≠ open rural field. IoD architecture adaptive aur location-aware honi chahiye.

---

### Physical Obstacles and Service Restrictions
**Physical obstacles:** Buildings/mountains (LoS block), weather (communication + flight), power lines (collision hazard).

**Service restrictions:** No-fly zones, frequency licensing, network coverage gaps, privacy laws, altitude limits.

**ZSP must know:** Restricted areas se UAVs bahar rakho, obstacles ke around route karo.

---

## PART 12 — UAV Roles: Details, Challenges & Technology Maturity

---

### UAV as Base Station — Protocol Converter & GCU
**Protocol Converter:** UAV-BS alag-alag network protocols ke beech translate kar sakta hai — jaise ek device jo Bluetooth ko cellular mein convert kare. Disaster zone mein purane radios ko modern network se connect karne ke liye useful.

**Ground Communication Units (GCU):** Zameen pe rakhe communication devices jo UAV-BS ke through baat karte hain. UAV-BS unhein regular network se connect karta hai (Fig 12/N3 mein uv3, uv4 GCUs UAV-BS se communicate karte hain).

**Disaster example:** Earthquake/flood mein cell towers gir gaye → UAV-BS quickly reliable communication infrastructure establish karta hai. Pehle se uncovered zones mein extended infrastructure.

> **Yaad rakh:** UAV-BS = regular base station jo hawa mein hai. GCU = ground devices jo usse connect karte hain.

---

### UAV Placement Optimization
**Kya hai:** UAV-BS ya relay ko physically kahan rakhein (altitude + position) takki coverage aur throughput maximize ho.

**Kyun hard:** Coverage area altitude ke saath badalta hai (too low = chota area, too high = weak signal). Plus obstacles, interference, mobility constraints.

**Paper mein:** Listed as major challenge for both UAV-BS aur relay deployment.

---

### Communication Bandwidth Optimization
**Kya hai:** UAV ke limited spectrum ko efficiently allocate karna across users/backhaul.

**Challenge:** UAV-BS neeche bahut users serve karta hai but upar ka backhaul link limited hai — bottleneck ban sakta hai.

---

### Wireless Power Transfer (WPT)
**Kya hai:** RF signals se UAV ko charge karna — dedicated transmitter se energy harvest karna. ("Full-duplex wireless powered" systems mein covered tha.)

**Challenge:** UAV ki battery life biggest limitation hai. WPT se mission time badhana — but efficiency low hai (distance se rapid decay).

**Paper mein:** Listed as major challenge for UAV-BS deployment.

---

### Onboard Processing (Edge on UAV)
**Kya hai:** Sensor data ko UAV ke apne processors pe process karna — cloud ya ground pe bhejne ke bajaye.

**Kyun:** Sensor/actuator UAVs (agriculture, forest) mein most processing onboard hoti hai → robust processors chahiye UAV pe.

**Trade-off:** Onboard processing = kam bandwidth chahiye (raw data mat bhejo) but heavier UAV (compute power = weight = battery drain).

---

### UAV-enabled Ground Sensor/Actuator Networks
**Kya hai:** UAV ground-based sensor/actuator networks ka "enabler" ban sakta hai — unhein connect karke ya data relay karke.

**Example:** Forest mein ground sensors hain but no network → UAV fly karke unka data collect karta hai (data mule role) ya unhein temporarily network se jodta hai.

---

### Aerial Network Formation
**Kya hai:** Multiple UAVs milke apne aap ek network banate hain (self-organizing). Fig 12/N4 mein multiple search UAVs aerial network form karte hain.

**Kyun:** Large-area missions (search-and-rescue) mein ek UAV kafi nahi — fleet coordinate karta hai dynamic network banake.

**Related:** FANET + cooperative systems ka yahi concept.

---

### Technology Maturity Levels (Algorithmic vs System)
**Kya hai:** Paper ka "lessons learnt" framework — challenges ko do categories mein baatna:
- **Algorithmic maturity:** Theoretical models/optimization frameworks ready hain (paper/simulation level)
- **System maturity:** Real-world deployment mein gaps hain (hardware, integration, real-time)

**Kyun important:** Same section mein discuss hone wale challenges equal maturity nahi rakhte — kuch algorithmically solve hain, kuch abhi open hain.

---

### Energy Optimization — Maturity Level
**Maturity:** RELATIVELY ADVANCED (algorithmic level). Bohot analytical models + optimization frameworks hain UAV-BS aur relay ke liye.

**Provides:** Theoretical tools for energy-aware deployment, mobility control, power management.

**Gap (system level):** Real-world implementation mein problems — real-time decision making, uncertainty in battery/energy profile, onboard control system se integration.

> **Exam tip:** Energy optimization = algorithmic mature, BUT real-world immature.

---

### Trajectory & Path Planning — Maturity Level
**Maturity:** INTERMEDIATE. Significant body of deterministic + learning-based approaches hain UAV mobility aur coverage optimization ke liye.

**Gap:** Still open problems in dynamic environments, multi-UAV coordination, real-time re-planning.

> **Exam tip:** Trajectory planning = intermediate maturity (na fully solved, na fully open).

---

## PART 13 — Multi-UAV Architecture, Leadership & Trust

---

### Security & Trust Management (UAV) — Early Stage
**Kya hai:** UAV networks ki security sirf encryption/auth nahi — "trust" bhi hai (kaunsa UAV reliable hai, kaunsa compromised). Paper kehta hai ye abhi **early stage** mein hai.

**Traditional paradigm:** Existing efforts "traditional communication security paradigm" pe build hain (AES, auth, freq hopping — jo PART 9 cover kiya). But comprehensive defence nahi hai.

**Open problem:** Spoofing, jamming, coordinator attack, adversarial swarm behaviour ke against comprehensive defence abhi **research problem** hai.

**Kyun important:** Safety-critical operations (disaster, military) mein ek compromised UAV poora swarm crash kar sakta hai.

> **Exam tip:** Security = relatively mature (PART 9). Trust management = early stage. Dono alag hain.

---

### Adversarial Swarm Behaviour
**Kya hai:** Attack jahan multiple malicious actors coordinate karke swarm ko disrupt karte hain — real swarm jaise behave karte hain but hostile intent se.

**Example:** 1000 drones mein se kuch hijacked → sahi drones ko collide force karte hain ya false data flood karte hain.

**Kyun hard:** Normal anomaly detection ek drone pakad leta hai, but swarm-level coordinated attack pattern detect karna bohot hard hai.

---

### Coordinator / Sybil Attack
**Kya hai:** Attacker ek node se multiple fake identities banata hai (Sybil) ya network coordinator compromise karta hai.

**Effect:** Fake UAVs inject karke swarm decisions manipulate sakta hai (false leader election, wrong routing).

**Defense:** Continuous trust management + identity verification chahiye.

---

### Multi-layer vs Single-layer UAV Architecture (Fig 3)
**Kya hai:** Figure 3 mein UAV networks organize karne ke 2 ways:
- **Single-layer (flat):** Sab UAVs ek hi level pe, peer-to-peer (FANET jaise)
- **Multi-layer:** UAVs alag-alag layers mein organized (leadership hierarchy)

**Fig 3 notation:** A1, A2 = layer-wise view. C1, C3 = communication gateway between views. Top layer = network orchestration.

**Kyun important:** Architecture type decide karta hai communication challenges (routing, leader election, relay).

---

### Leader UAV (Configuration C2, Fig 3)
**Kya hai:** Multi-layer architecture mein stability ke liye ek "leader" UAV select hota hai (C2 config).

**Leader kya karta hai:**
- Har layer ka communication gateway (external agents se)
- Formation control decide karta hai
- UAV placement decide karta hai
- Layer-andar aur across-layer coordination

**Kyun:** Bina leader ke multi-layer swarm unstable ho sakta hai — physics formation maintain karna mushkil.

> **Yaad rakh:** Leader = swarm ka "captain". Gateway + controller dono.

---

### Star vs Mesh Topology (UAV Networks)
**Star:** Sab UAVs ek central node (leader/gateway) se connect. Simple, but single point of failure.

**Mesh:** Har UAV multiple neighbours se connect. Robust, but complex routing.

**Paper:** Multi-layer architecture mein star YA mesh use ho sakta hai.

---

### Multi-star / Hierarchical Mesh
**Kya hai:** Star aur mesh combine karke hierarchical banaya ja sakta hai — multiple stars jinke apne leaders hain, leaders aapas mein mesh.

**Benefit:** Scalability + robustness dono. Large swarms ke liye ideal.

---

### Leader Selection Approaches
**Static leader-follower:** Pehle se fix leader assign (predictable, but leader fail ho to problem).

**Distributed leadership:** Dynamic — leader role rotate hota hai ya situation ke hisaab se change (resilient, but coordination overhead).

**Challenge:** Optimal leader select karna (energy, position, reliability consider karke).

---

### Architecture Stability (UAV Formation)
**Kya hai:** Multi-UAV formation physically stable rehna chahiye — UAVs relative positions maintain karein despite wind/disturbances.

**Leader's role:** Formation control signals deta hai taaki swarm tight reh sake.

**Cross-cutting challenges (literature):** Communication relay minimization, routing protocols, power transfer, UAV traffic management, communication relay — ye sab multi-layer architectures mein open problems hain (PART 10/11 mein individual cover kiye gaye).

---



### Network Slicing (UAV Communications)
**Kya hai:** Ek shared physical 5G network ke upar multiple independent "logical networks" banane ki technique — har ek apna QoS, bandwidth, latency provide karta hai. Jaise ek apartment building mein har flat ka apna electricity/water connection hai, par sab ek hi building mein.

**Kaise kaam karta hai:**
- **NetSliA, NetSliB, NetSliC** = different slices for different service types (eMBB, URLLC, mMTC)
- Core Network (CN) + Access Network (AN) instances har slice ke liye dedicated
- UAV applications ke hisaab se slice allocate hota hai:
  - HD video streaming → eMBB slice
  - UTM data → mMTC slice
  - BVLoS control → URLLC slice

**Kyun important hai paper mein:** UAVs ke liye QoS guarantee karna without interfering with terrestrial users — network slicing hi woh mechanism hai jo different UAV applications ko unke specific requirements ke hisaab se serve karta hai.

> **Scene:** Ek shared highway pe different lanes — ambulance (URLLC) alag lane mein, truck (eMBB) alag, bicycle (mMTC) alag.
> **Exam tip:** eMBB = high bandwidth (video), URLLC = ultra-reliable low-latency (control), mMTC = massive IoT (sensor data).

---

### AirSlice
**Kya hai:** Yuan and Muntean [291] ka proposed 5G network slicing framework specifically designed for UAV communications — different QoS support for aerial users.

**Kaise kaam karta hai:** UAV applications ko unke bandwidth, latency, packet delivery requirements ke hisaab se classify karta hai, phir appropriate network slice allocate karta hai.

> **Exam tip:** AirSlice = UAV-specific slicing framework. Key contribution = QoS differentiation for aerial vs terrestrial traffic.

---

### SLA — Service Level Agreement (UAV Context)
**Kya hai:** Ek formal contract ya specification jo batata hai ki ek UAV application ko kitna bandwidth, throughput, latency, packet delivery ratio milega.

**Kaise kaam karta hai:** Har UAV use-case (HD video, UTM control, BVLoS command) ko ek predefined QoS level assign karta hai, jisse network operator uske liye dedicated slice/resources allocate kar sake.

**Challenge:** Existing 5G slice types (eMBB/URLLC/mMTC) se fully match nahi karte — new SLA frameworks chahiye.

> **Exam tip:** SLA = QoS guarantee ka contract. Paper mein problem = existing slice types UAV applications ke saath match nahi karte.

---

### Testbed (UAV Communications)
**Kya hai:** UAV communication systems ko real-world ya controlled lab environment mein test karne ka hardware/software platform. Real UAVs + radios + protocols = end-to-end testing.

**Kaise kaam karta hai:**
- **Real-world testbeds:** Actual UAVs + cellular/WiFi radios + sensors
- **Simulators:** OMNeT++, ns-3, X-Plane flight simulator
- **HITL (Hardware-in-the-Loop):** Real UAV flight controller + simulated network
- **SITL (Software-in-the-Loop):** Fully simulated UAV + network

**Examples:**
- Bouachir [301]: 802.11g WiFi, AODV routing, 200m range
- Callegaro [308]: 4G LTE + USRP + srsLTE on UAV
- AERPAW: NSF-funded large-scale SDR-based platform
- SkyRAN [326]: LTE RAN on flying UAV
- EuroDRONE [316]: V2I/V2V for UTM

> **Scene:** Car test track = testbed for cars. UAV testbed = controlled airspace + radios + measurement tools for UAV networks.
> **Exam tip:** Testbed types = real-world, simulator, HITL, SITL. AERPAW = largest US testbed.

---

### HITL — Hardware-in-the-Loop
**Kya hai:** Testbed ka ek type jahan real UAV hardware (flight controller, motors) use hota hai lekin network communication simulated ya emulated hota hai.

**Kaise kaam karta hai:** Real flight dynamics + simulated radio channel → cost-effective testing without actual flight risk.

> **Exam tip:** HITL = real hardware + fake network. Opposite = SITL (fully fake).

---

### SITL — Software-in-the-Loop
**Kya hai:** Fully software-based simulation — virtual UAV + virtual network + virtual channel models. No physical hardware needed.

---

### AERPAW
**Kya hai:** NSF (National Science Foundation) ka large-scale aerial wireless testbed platform — PAWR program ka part. Multi-level wireless emulation for UAVs (RF-level, I-Q level, packet-level) over SDR-based 5G.

**Kaise kaam karta hai:** Fixed + portable SDR nodes mounted on UAVs/UGVs. E-VMs (Experimenter Virtual Machines) configure as UE, gNB, or core network.

**Features:** USRPs, Keysight RF sensors, LoRa gateways, Ericsson 4G/5G base station.

> **Scene:** AERPAW = a "drone laboratory" where researchers test wireless protocols without building everything from scratch.
> **Exam tip:** AERPAW = US NSF's platform for aerial wireless experiments. Supports 4G/5G SDR + digital twins.

---

### SkyRAN / SkyCore / SkyHAUL
**Kya hai:** NEC Labs ke flying base station testbeds:
- **SkyRAN [326]:** LTE RAN on flying UAV — adaptive to terrain and ground UE mobility
- **SkyCore [327]:** EPC core on UAV supporting multiple flying base stations
- **SkyHAUL [328]:** Self-organizing gigabit network with multiple replay UAVs

---

### EuroDRONE
**Kya hai:** A testbed for unmanned traffic management (UTM) using V2I and V2V communication technologies. Autonomous small UAVs with 2.4/5GHz LTE and Sub-GHz communication.

---

### Open Issues (UAV Communications)
**Kya hai:** Paper ke Section VIII mein listed major unresolved research challenges in UAV networking.

**Key open issues:**
- **Energy constraint:** Limited battery power for computation + communication + flight
- **UAV platform:** Flight dynamics and orientation highly influence communication links
- **Mobility model:** Need realistic UAV motion models combining best features of existing models
- **Routing:** Protocols must dynamically adapt to changing network topology
- **Path planning:** Multi-UAV missions need coordination-aware dynamic replanning
- **QoS provisioning:** Heterogeneous/distributed nature makes QoS framework establishment difficult
- **Fault handling:** Hardware, software, communication link failures need deep exploration
- **Data processing:** Limited onboard computation — fog/edge computing needed
- **Security:** Authenticity of relaying information impacts overall network security
- **Standardization of FANET:** Need proper standards for civilian commercialization
- **Distributed optimization:** Most existing solutions are centralized — need scalable distributed algorithms
- **Spectrum management:** No dedicated spectrum for commercial UAVs — need new sharing techniques
- **Network formation:** 3D dynamic topology control is uniquely challenging
- **Testing/Simulation:** Current simulators don't capture realistic aerial network dynamics

> **Exam tip:** Open issues = "what still needs to be solved." 14 major categories listed in paper Section VIII-A.

---

### Recommendation and Further Work (UAV)
**Kya hai:** Paper ke Section VIII-B mein specific recommendations for future research and development in UAV communications.

**Key recommendations:**
- Multi-UAV systems with steady communication, remote control, unlimited coverage
- Adaptive beamforming + directional antennas for reliability
- Deep RL-based routing for high mobility and topology changes
- Blockchain-based registration for UAV device lifecycle management
- Realistic UAV simulators with energy models and flight dynamics
- Full security frameworks covering jamming, spoofing, unauthorized access
- Cognitive radio and dynamic spectrum access for spectrum sharing
- Network slicing-assisted architectures for cross-domain applications

---

### ACRONYMS AND NOMENCLATURE (Additional New Terms)

### CH — Cluster Head
**Kya hai:** Wireless sensor networks (WSNs) mein cluster-based routing mein ek leader node jo cluster ke andar ke data collect karke aggregation/transmission handle karta hai.

> **Exam tip:** CH = cluster ka leader. Data gathering/aggregation ka responsibility.

---

### CN — Core Network
**Kya hai:** Mobile communication ka central part — subscriber management, mobility management, session management, authentication sab yahan manage hota hai. 5G mein 5GC (5G Core).

---

### DAG — Directed Acyclic Graph
**Kya hai:** Networking topology jahan edges direction ke saath hote hain aur koi cycle nahi hota. Used in routing protocols where data flows in one direction without loops.

---

### DCR — Data Centric Routing
**Kya hai:** Routing approach jahan data packets ko destination address ke bajaye data content/name ke hisaab se route kiya jata hai. Interest-based forwarding.

---

### DOLSR — Directional OLSR
**Kya hai:** Optimized Link State Routing (OLSR) ka modified version jo directional antennas use karta hai instead of omnidirectional — improves spatial reuse and reduces interference.

---

### DSR — Dynamic Source Routing
**Kya hai:** On-demand routing protocol for MANETs/FANETs — source node entire route embed karta hai packet mein. Route discovery = RREQ/RREP mechanism.

---

### D2D — Device-to-Device
**Kya hai:** Two devices directly communicate without going through base station or network infrastructure. In UAV context: UAV-to-UAV direct communication for swarm coordination.

---

### EM — Electromagnetic
**Kya hai:** Electromagnetic waves — radio frequency (RF) signals jo wireless communication carry karte hain. UAV channel models electromagnetic propagation par based hote hain.

---

### ETSI — European Telecommunications Standards Institute
**Kya hai:** Europe ka standardization body — 3GPP ke saath mil kar 5G standards develop karta hai. UAV-related specs: TS 128530, TS 28.530.

---

### FAA — Federal Aviation Administration
**Kya hai:** United States ka aviation regulatory authority — civilian UAV operations ke liye airspace rules, safety standards, certification define karta hai.

---

### GPMOR — Geographic Position Mobility Oriented Routing
**Kya hai:** UAV-specific routing protocol jo UAVs ki current geographic position use karta hai forwarding decisions ke liye — suitable for 3D aerial networks with predictable mobility patterns.

---

### GPSR — Greedy Perimeter Stateless Routing
**Kya hai:** Geographic routing protocol — greedy forwarding (closest node to destination) use karta hai. Perimeter mode activates jab greedy forwarding fail ho (void hole).

---

### GS — Ground Station
**Kya hai:** UAV network ka terrestrial node — can be a GCS, relay point, or data collection center. GS UAVs se data receive karta hai aur network ko terrestrial infrastructure se connect karta hai.

---

### HW — Hardware
**Kya hai:** Physical components of UAV system — flight controller, sensors, radios, batteries, gimbal. Contrast with SW (software).

---

### ISAC — Integrated Sensing and Communication
**Kya hai:** Ek emerging technology jahan same waveform/spectrum simultaneously communication data transmit karta hai AND environmental sensing perform karta hai (radar-like). Future 6G UAV networks ke liye promising.

---

### LAROD — Location Aware Routing for Opportunistic Delay
**Kya hai:** Routing protocol combining geographic forwarding with delay-tolerant networking — suitable for intermittently connected UAV networks.

---

### LCAD — Load Carry And Deliver
**Kya hai:** UAV application use-case classification — UAV as cargo transport/delivery vehicle. Key communication requirement = reliable control + real-time telemetry.

---

### LLC — Logical Link Control
**Kya hai:** OSI model ka upper sublayer of Data Link layer — flow control, error control, multiplexing provide karta hai. In wireless UAV networks, LLC layer reliability mechanisms critical hote hain.

---

### MAC — Media Access Control
**Kya hai:** Data Link layer ka lower sublayer — channel access control karta hai (CSMA/CA in WiFi, scheduling in cellular). UAV networks mein dynamic topology ke karan MAC layer design challenging hai.

---

### MANET — Mobile Ad-hoc Network
**Kya hai:** Infrastructure-less wireless network where nodes dynamically form network and route packets multi-hop. UAV FANETs ka foundational concept — but FANETs have more extreme mobility than MANETs.

---

### MLHR — Multi Level Hierarchical Routing
**Kya hai:** Hierarchical routing protocol for FANETs — network multiple levels (clusters) mein divided hota hai, har level ka apna routing mechanism. Reduces routing overhead in large swarms.

---

### ML-OLSR — Mobility and Load aware OLSR
**Kya hai:** OLSR protocol ka modified version jo node mobility patterns aur network load consider karta hai routing decisions mein — better for high-mobility UAV networks.

---

### MNO — Mobile Network Operator
**Kya hai:** Cellular service provider (Jio, Airtel, Verizon, etc.) — owns spectrum licenses, base stations, core network infrastructure. UAVs as aerial users MNO networks ke through connect hote hain.

---

### MPGR — Mobility Prediction Geographic Routing
**Kya hai:** Geographic routing protocol jo future mobility predictions use karta hai — UAV position ko predict karke forwarding decisions optimize karta hai.

---

### MPR — Multi-Packet Reception
**Kya hai:** Wireless receiver ki capability simultaneously multiple packets receive karne ki — improves network throughput in dense UAV deployments where multiple UAVs might transmit together.

---

### MRPA — Mission Route Planning Agent
**Kya hai:** AI/software component jo multi-UAV mission ke liye optimal routes plan karta hai — coordinates path planning, collision avoidance, and coverage optimization.

---

### NAS — National Airspace System
**Kya hai:** United States ka complete airspace management framework — includes controlled/uncontrolled airspace, navigation aids, ATC procedures. UAV integration NAS mein critical challenge hai.

---

### NextG-RANs — Next Generation Radio Access Networks
**Kya hai:** 4G/5G/6G cellular base stations (gNBs) — RAN infrastructure jo aerial users (UAVs) ko cellular connectivity provide karta hai. 3GPP Rel-17/18 UAV-specific enhancements define kiye hain.

---

### NEF/SCEF — Network Exposure Function / Service Capability Exposure Function
**Kya hai:** 3GPP core network functions jo third-party applications (like UTM) ko network services expose karte hain — location reporting, QoS monitoring, etc.

---

### OLSR — Optimized Link State Routing
**Kya hai:** Proactive routing protocol for MANETs/FANETs — uses Hello messages for neighbor discovery and TC (Topology Control) messages for route calculation. MPR (Multi-Point Relay) concept se flooding overhead reduce karta hai.

---

### POLSR — Predictive OLSR
**Kya hai:** OLSR ka enhanced version jo link stability predictions use karta hai routing table update karne mein — better for high-mobility UAV networks where links break frequently.

---

### QFLR — Q-learning-based Fuzzy Logic Routing
**Kya hai:** AI-based routing protocol combining Q-learning (RL) with fuzzy logic — adapts to changing UAV network conditions autonomously without pre-programmed rules.

---

### QMR — Q-learning based Multiobjective optimisation Routing
**Kya hai:** Multi-objective routing protocol using Q-learning — simultaneously optimizes energy efficiency, latency, and reliability for UAV network communications.

---

### RIS — Reconfigurable Intelligent Surface
**Kya hai:** Programmable metasurface jo wireless propagation environment actively reshape karta hai — passive reflecting elements directional beamforming without active RF chains. UAV networks mein NLoS coverage improve karne ke liye promising.

> **Scene:** RIS = ek "smart mirror" jo radio signals ko bounce karke desired direction mein redirect karta hai.
> **Exam tip:** RIS = passive, reconfigurable, no power needed. UAV deployment = NLoS → LoS conversion.

---

### RF — Radio Frequency
**Kya hai:** Electromagnetic waves used for wireless communication — spectrum ranges from kHz to GHz. UAV communication channels RF propagation par based hote hain (TR 38.901 model).

---

### RL — Reinforcement Learning
**Kya hai:** ML paradigm jahan agent environment se learn karta hai actions lena — reward function optimize karta hai. UAV networking mein RL use hota hai dynamic routing, resource allocation, trajectory optimization ke liye.

---

### RPA — Remotely Piloted Aircraft
**Kya hai:** Official ICAO/EASA term for what civilians call "drone" — aircraft jo remote pilot se control hota hai. Regulation mein technical term hai.

---

### RPAS — Remotely Piloted Aircraft System
**Kya hai:** Complete system = RPA (aircraft) + remote control station + command & control links + support equipment. Equivalent to UAS (Unmanned Aerial System).

---

### RREQ / RREP — Route Request / Route Reply
**Kya hai:** AODV routing protocol ke messages — RREQ = source node route discovery ke liye broadcast karta hai, RREP = destination ya intermediate node reply karta hai with path information.

---

### RTCA — Radio Technical Commission for Aeronautics
**Kya hai:** US aviation standards organization — DO-360, DO-365 etc. documents publish karta hai for UAV communications spectrum allocation and safety standards.

---

### SAGSIN — Space Air Ground Sea Integrated Network
**Kya hai:** Next-generation communication architecture jo space, air, ground, sea domains integrate karta hai — seamless connectivity across all domains for global coverage. UAVs = aerial domain component.

---

### SWIPT — Simultaneous Wireless Information and Power Transfer
**Kya hai:** Technology jahan same RF signal simultaneously data transmit karta hai AND energy harvest karta hai — UAV receivers par deployed kar sakte hain for extended flight endurance.

---

### TBRPF — Topology Broadcast based on Reverse Path Forwarding
**Kya hai:** Proactive link-state routing protocol for MANETs — uses reverse path forwarding for efficient topology broadcast. Less common than OLSR but similar purpose.

---

### TORA — Temporally-Ordered Routing Algorithm
**Kya hai:** Distributed routing protocol for MANETs/FANETs — uses "height" metric based on temporal ordering of nodes. Loop-free on-demand routing with multiple route discovery.

---

### TSAODV — Time-Slotted AODV
**Kya hai:** AODV protocol ka time-slotted version — synchronized time slots reduce collisions and improve channel utilization in scheduled UAV network communications.

---

### USMP — UAV Search Mission Protocol
**Kya hai:** Specialized protocol for UAV search and rescue missions — coordinates area coverage, search patterns, and data collection among multiple UAVs in a swarm.

---

### UUAA — UAV Authentication and Authorization
**Kya hai:** 3GPP-defined security procedure jo UAV ko UTM/network se authenticate karta hai before granting access to communication services — USS (UAS Service Supplier) through.

**Process:** CAA-level UAV ID + GPSI + subscription verification → PDU session establishment.

---

### VANET — Vehicular Ad-hoc Network
**Kya hai:** V2X (Vehicle-to-Everything) communication network — vehicles as mobile nodes form ad-hoc network. Similar to FANET but ground-based. UAVs can integrate with VANETs for aerial relay/coordination.

---

### VTOL — Vertical TakeOff and Landing
**Kya hai:** Aircraft capability vertically take off and land without runway — includes multirotor drones, tilt-rotor aircraft. Most common UAV type (quadcopters = VTOL).

---

### WLAN — Wireless Local Area Network
**Kya hai:** Short-range wireless networking standard (IEEE 802.11) — WiFi. UAV testbeds often use WLAN for ad-hoc mesh communications between UAVs and GCS.

---

### WRC — World Radiocommunication Conference
**Kya hai:** ITU (International Telecommunication Union) ka periodic conference jo global radio spectrum allocation decisions leta hai — frequency bands for UAVs officially assigned here.

---

### ZRP — Zone Routing Protocol
**Kya hai:** Hybrid routing protocol combining proactive (intra-zone) and reactive (inter-zone) routing — network ko zones mein divide karta hai. Reduces routing overhead in large MANETs/FANETs.

---

### ZSP — Zone Service Provider
**Kya hai:** Cloud-based entity jo ek specific geographic zone ke liye UAV traffic management, communication services, and coordination provide karta hai — UTM architecture ka component.

> **Exam tip:** ZSP = zone-level "manager" (cloud). GCS = pilot's ground terminal. Dono different.

---

## Quick Reference: "Kya confusion hoga exam mein"

| Commonly confused | Difference |
|---|---|
| UAV vs UAS | UAV = just the vehicle. UAS = vehicle + control + links + support |
| IoD vs UTM | UTM = application layer (what to manage). IoD = network layer (how to manage) |
| ZSP vs GCS | ZSP = cloud-based zone coordinator. GCS = human's ground terminal |
| FANET vs IoD | FANET = flying ad-hoc network (lower layer). IoD = the full vision/architecture |
| LoS vs NLoS | LoS = clear path. NLoS = obstacle between TX and RX |
| AoI vs latency | Latency = transit delay. AoI = total staleness from source generation |
| CVAE vs DCGAN | CVAE = LoS/NLoS condition → multipath params. DCGAN = channel params as images |
| Intrazone vs Interzone | Intrazone = stays in one ZSP's zone. Interzone = crosses ZSP boundary |
| Large-scale vs small-scale fading | Large = gradual path loss over distance. Small = rapid fluctuations from multipath |
| mmWave vs sub-6GHz | mmWave = huge bandwidth but short range, LoS only. Sub-6 = less bandwidth, better range/NLoS |
| Network Slicing vs QoS | Slicing = mechanism to create dedicated logical networks. QoS = performance guarantee (throughput/latency). Slicing enables QoS. |
| HITL vs SITL | HITL = real hardware + simulated network. SITL = fully simulated. |
| SkyRAN vs SkyCore | SkyRAN = LTE base station on UAV. SkyCore = EPC core on UAV. |
| AirSlice vs generic slicing | AirSlice = UAV-specific. Generic = designed for general 5G users. |
| RPA vs RPAS | RPA = aircraft only. RPAS = aircraft + all support systems. |

---

*End of Hinglish Glossary — UAV Communications Survey*
