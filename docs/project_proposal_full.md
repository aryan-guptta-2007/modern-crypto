# Legacy Cipher Migration Framework for Industrial Control Systems

**Project proposal — Milestone 2 (Problem Analysis)**

| Item | Value |
|---|---|
| Project topic | No. 8, Legacy Cipher Migration Framework for Industrial Control Systems (ICS) |
| Course and code | `TODO(team)` |
| Team members | Aryan Gupta, Yug Chaturvedi, Yuvraj Pathak |
| Instructor | `TODO(team)` |
| Submission format | Markdown, converted to PDF |
| Date | 8 October 2026 |

## Abstract

Legacy field devices in electricity distribution networks were installed before
communication security was a design requirement, and many cannot be upgraded to run
modern cryptography. A common industrial response is to place a translation gateway
beside the old device: the gateway accepts the weakly protected legacy frame and
forwards it under AES. This project builds a software simulation of such a gateway,
implements the classical ciphers and AES named in the course problem statement, and
studies which vulnerabilities persist or are introduced while a network is partly
migrated. The gateway concept is established industrial practice and is not claimed
here as novel; the contribution of the project is a reproducible simulation, a set of
working attacks, and measurements of what gateway-side checks do and do not catch. A
feasibility prototype already runs the full pipeline end to end, recovers a legacy key
by exhaustive search in under a millisecond, and delivers a forged reading to the
control centre inside a cryptographically valid AES envelope.

## How this document maps to the evaluation criteria

| # | Criterion | Marks | Part |
|---|---|---|---|
| 1 | Problem domain identification and analysis | 3 | Part A |
| 2 | Review of existing systems and project feasibility | 3 | Part B |
| 3 | Objectives and methodology of the proposed work | 3 | Part C |
| 4 | Relevance of algorithms and techniques | 3 | Part D |

Every source cited in this document was opened and read during preparation. Sources
that could not be retrieved were left out, and the omissions are recorded in the
`TODO(team)` list at the end.

---

# Part A — Problem domain identification and analysis

## A.1 Domain background

### A.1.1 ICS and SCADA architecture

An industrial control system (ICS) is a combination of programmable devices that
interact with a physical process. NIST groups these systems under the broader term
operational technology, defined as "programmable systems and devices that interact with
the physical environment" [1]. In electricity distribution the relevant arrangement is
a supervisory control and data acquisition (SCADA) system, which has three layers:

| Layer | Contents | Function |
|---|---|---|
| Field level | Remote terminal unit (RTU), programmable logic controller (PLC), intelligent electronic device (IED), meter | Measures the process and operates plant |
| Communication link | Serial line, leased line, radio, or an IP network | Carries measurements up and commands down |
| Control centre | Control server, operator HMI, historian | Supervises the network and issues commands |

In the master–slave arrangement typical of these systems, master devices control the
operation of slave devices, and a slave such as an RTU "can be a sensor, an actuator,
or both" [3]. Large installations with hundreds of RTUs commonly add an intermediate
sub-control server to reduce load on the primary server [1].

### A.1.2 The smart-grid telemetry and control loop

The control centre "polls field devices for data at defined intervals (e.g., 5 seconds,
60 seconds) and can send new set points to field devices as required", while also
watching for priority interrupts from field alarm systems [1]. Two flows therefore
exist. Upward telemetry carries measurements such as voltage, current, frequency and
breaker position. Downward commands carry set points and switching instructions. A
SCADA system in a power grid monitors transformers, circuit breakers, protective relays
and re-closers while acquiring measurements that describe loading conditions across the
network [2].

**This project models the upward telemetry flow only.** Downward commands are out of
scope, for the reason given in A.7.

### A.1.3 Why field devices are called legacy

Three properties recur across the literature.

| Property | Evidence |
|---|---|
| Very long service life | "The lifespan of an OT system can exceed 20 years", so many legacy systems run hardware and software no longer supported by the vendor and cannot be patched [1]. The expected lifetime of SCADA equipment is given elsewhere as 20 to 50 years [3]. |
| Severe resource limits | Operational technology is "often resource-constrained" and may "lack desired features, including encryption capabilities, error logging, and password protection" [1]. Implementing cryptographic defence on old-generation devices is described as impossible on resource grounds, forcing protection into an add-on [2]. |
| Designed before security was a requirement | Serial SCADA systems were "deployed decades ago with availability and personnel safety as the primary concerns, rather than security" [3]. Very few systems in active use "were originally designed with security in mind" [2]. |

Replacement is not a short-term option. Legacy devices are "so highly integrated with
the power equipment they monitor" that phasing them out will take decades [2], and
retrofitting is frequently blocked by the cost of re-certification [4].

### A.1.4 Legacy protocols

The protocols in common use on these links are Modbus and DNP3 [3]; DNP3 is published
as IEEE Std 1815 [1], [7]. Messages are deliberately compact, because the links are
narrow: traditional SCADA links are low bandwidth, with typical baud rates from 9600 to
115200, and slave devices transmit only when polled [3]. In their original forms these
protocols carry no source authentication: most legacy SCADA systems "could have little
defense to this kind of attacks as no source authentication or command verification
mechanism is in place" [2].

`TODO(team)`: a direct citation to the Modbus specification itself would strengthen
A.1.4. The claim is currently supported by three secondary sources [1], [2], [3] rather
than by the protocol document.

### A.1.5 Why isolation no longer protects the grid

The original security strategy was obscurity and physical isolation [2]. That strategy
has eroded. NIST records that operational technology was initially isolated and ran
proprietary protocols, but as these systems adopted IT solutions "to enable corporate
business systems connectivity and remote access capabilities", the result "provides
significantly less isolation for OT from the outside world than predecessor systems"
[1]. The same source notes that low-cost Ethernet, IP and wireless devices are
replacing older proprietary technologies, which "increases the likelihood of
cybersecurity vulnerabilities and incidents" [1]. Increasing connectivity between
legacy SCADA systems and more open smart-grid systems enlarges the attack surface and
allows forged data or commands to be sent from outside [2].

The problem addressed by this project is therefore the consequence of a change in the
environment, not of a fault in the original engineering.

## A.2 Problem statement

> Legacy field devices in electricity distribution networks transmit telemetry without
> confidentiality, integrity or source authentication, and a large installed base cannot
> be upgraded to run modern cryptography because of resource limits, service life and
> re-certification cost. The established industrial response is to place a translation
> gateway between the legacy device and the network, so that data leaves the gateway
> under AES. This arrangement moves the trust boundary rather than removing it. This
> project builds a simulation of such a gateway, implements the classical ciphers and
> AES named in the course problem statement as a graded scale of legacy protection, and
> determines which vulnerabilities persist or are newly introduced while the network is
> partly migrated.

### A.2.1 What the statement does and does not claim

| The statement claims | The statement does not claim |
|---|---|
| The migration problem is real and documented | That this project discovered it |
| A gateway is the common response | That the gateway design here is new; it is not (Part B) |
| Residual vulnerabilities can be demonstrated and measured | That the project proposes a complete fix |
| Classical ciphers usefully model graded weakness for study | That real legacy devices use Caesar or Vigenère; they generally do not (A.7) |

## A.3 Root-cause analysis

| # | Root cause | Effect | Why it cannot simply be fixed |
|---|---|---|---|
| R1 | Protocols specified without confidentiality or authentication [2], [3] | Frames can be read, altered and injected in transit | Changing the protocol breaks interoperability with the installed base, and modification is needed at both protocol and device level [2] |
| R2 | Constrained field hardware [1], [2] | The device cannot perform AES or run a TLS stack | Cryptographic defence on these devices is infeasible on resource grounds, so protection must be an add-on [2] |
| R3 | Service life of 20 years and beyond [1], [3] | Old and new equipment coexist for years | Replacement is capital-intensive and needs planned outages; phase-out will take decades [2] |
| R4 | Re-certification and amortisation cost [4] | Even technically possible retrofits are rejected | High acquisition cost and long amortisation periods make replacement impractical, and re-certification makes retrofit infeasible [4] |
| R5 | Loss of the isolation the design assumed [1], [2] | Threats the design never anticipated now reach the device | Connectivity is required by the business; it cannot be withdrawn |

R1 to R4 explain why a gateway is used at all. R5 explains why the matter is urgent.
The analysis in this project concentrates on what R1 and R2 leave exposed once a
gateway is in place.

## A.4 Threat model

### A.4.1 Attacker positions and capabilities

The attacker is assumed to have gained access to the substation cabinet or the local
wiring between the legacy device and the gateway, which is the position the literature
identifies as unaddressed [4]. No cryptographic break of AES is assumed, and no
attacker with unlimited resources is assumed.

| Position | Attacker capability | Security property lost |
|---|---|---|
| P1 Legacy link, device to gateway | Read, alter, inject and replay frames | Confidentiality, integrity, source authentication |
| P2 Inside the gateway | Observe plaintext between decryption and re-encryption; potentially read both key sets | All properties, for every device behind that gateway |
| P3 AES link, gateway to control centre | Read and replay ciphertext | None, provided AES-GCM, sequence numbers and timestamps are used correctly |
| P4 Configuration and management | Enable a passthrough or fallback mode | Reduces protection to the legacy level |

A diagram of these positions is given in `docs/figures/threat_model.svg`, with a text
description in `docs/figures/threat_model.md`.

### A.4.2 Trust boundaries

The gateway creates two boundaries where there was one. The segment from the gateway to
the control centre becomes a protected channel. The segment from the device to the
gateway does not. Kaniewski et al. name this remaining segment the *legacy link* and
state the position directly: the gateway "secures only the communication on the network
side but does not mitigate the absence of security features in the legacy device", so
the link connecting the legacy device to the gateway "remains vulnerable and
unaddressed" [4]. That sentence is the starting point for this project.

### A.4.3 What is not modelled

Side-channel and fault attacks on AES; compromise of the control centre itself; supply
chain attacks on gateway firmware; denial of service by physical destruction of plant;
and the stolen-credential and remote-access route that characterised the 2015 Ukraine
incident described in A.6.1. These are excluded to keep the study small enough to
complete and to measure, not because they are unimportant.

## A.5 Transition vulnerabilities

These eight items are the substance of the "study of transition vulnerabilities" that
the problem statement requires. Items marked *demonstrated* are already reproduced in
the feasibility prototype; see `docs/prototype_run.txt` and Part B.

| # | Vulnerability | Status |
|---|---|---|
| V1 | The legacy link remains exposed | Demonstrated |
| V2 | Authenticated false data | Demonstrated |
| V3 | Plaintext exposure inside the gateway | By design, argued |
| V4 | Two key sets on one device | Argued |
| V5 | Incorrect AES mode selection | Planned |
| V6 | Replay on the legacy link | Demonstrated |
| V7 | Downgrade to passthrough | Planned |
| V8 | Added latency and a single point of failure | Partly measured |

**V1 — The legacy link remains exposed.** AES protects only the half of the path beyond
the gateway. Anything readable or writable on the device-to-gateway segment stays so.
This is the vulnerability the reviewed literature explicitly leaves open [4]. In the
prototype, a 36-key additive cipher on this segment was broken by exhaustive search in
0.20 ms and the reading recovered in full.

**V2 — Authenticated false data.** The gateway cannot distinguish a genuine frame from a
forged one, because the legacy protocol provides no source authentication [2]. It
therefore wraps a tampered reading in a valid AES envelope, and the control centre sees
a correctly authenticated message. Chan and Zhou describe the consequence: false
readings from compromised instrumentation devices "could present a distorted picture of
the system status to the master station, thus possibly triggering a false alarm and
disruptive actions" [2]. This is the most serious finding of the prototype, because
cryptography on the protected half performs exactly as specified while the data it
protects is false. Authentication of the channel is not authentication of the
measurement.

**V3 — Plaintext exposure inside the gateway.** Translation requires decryption, so the
cleartext reading necessarily exists inside the gateway. One gateway typically serves
several devices, which concentrates risk at a single point. The 2015 Ukraine incident is
relevant here in a narrow and specific way: the attackers rendered serial-to-Ethernet
devices at substations inoperable by corrupting their firmware [5], which shows that
devices of exactly this class are reachable and are treated as targets.

**V4 — Two key sets on one device.** The gateway holds the legacy key for each device it
serves and the AES key for the uplink. Field sites are remote and visited rarely, which
makes rotation difficult. This project does not attempt to solve key distribution
(A.7); it records the exposure.

**V5 — Incorrect AES mode selection.** Choosing AES is not sufficient. ECB reveals
repeating structure, and telemetry is highly repetitive. CBC without a separate
authentication step provides no integrity. The project will demonstrate the difference
rather than assert it.

**V6 — Replay on the legacy link.** Legacy frames carry no freshness information, so a
captured frame can be re-presented and the gateway will accept it. The prototype shows
the asymmetry plainly: a replayed AES envelope is rejected on its sequence number, while
a replayed legacy frame is accepted and faithfully forwarded.

**V7 — Downgrade to passthrough.** Gateways commonly provide a bypass mode for
commissioning and fault-finding. If that mode can be triggered, or is simply left
enabled after maintenance, protection returns to the legacy level while the system
continues to appear operational.

**V8 — Added latency and a single point of failure.** Encryption "adds latency and may
not be suitable for all OT devices" [1], and latency is the constraint that dominates
retrofit design for time-critical serial links [3]. A gateway also becomes a component
whose failure removes visibility of every device behind it.

## A.6 Justification of significance

### A.6.1 Documented incidents

On 23 December 2015, three Ukrainian regional electricity distribution companies
experienced outages affecting approximately 225,000 customers, which an interagency
team assessed were caused by external cyber-attackers [5]. The attacks at each company
occurred within 30 minutes of each other. Breakers were operated remotely by "multiple
external humans using either existing remote administration tools at the operating
system level or remote industrial control system (ICS) client software via virtual
private network (VPN) connections", and the companies believe the actors had acquired
legitimate credentials beforehand [5].

Two honest qualifications matter. First, this intrusion route was stolen credentials
and remote access, not interception of a legacy link, so a gateway of the kind studied
here would not have prevented it. Second, CISA states that BlackEnergy malware was
present on the networks but that its role in the attack is not established [5]. The
incident is cited to establish that manipulation of field equipment in a distribution
network produces real and large consequences, and that substation communication devices
are attacked in practice [5]. It is not cited as evidence for the specific attack this
project simulates.

An earlier and more directly comparable case is the 2001 incident in which an
attacker interfered with a computerised sewage management system in Australia and
released untreated waste into parks and rivers, reported as an example of attacks on
critical infrastructure control systems [3].

`TODO(team)`: Stuxnet (2010) is named in the project brief but is **not** cited here.
No primary source for it was retrievable during preparation, and its mechanism —
manipulation of PLC logic via engineering workstations — differs from the telemetry
interception problem this project studies. Add it only with a verified source and an
explicit statement of relevance.

### A.6.2 Standards that exist in response to this problem

The existence of dedicated standards is itself evidence that the problem is recognised
as serious.

| Standard | Scope | Note for this project |
|---|---|---|
| NIST SP 800-82 Rev. 3 (September 2023) | Guidance on securing operational technology, including compensating controls where legacy systems cannot support a control [1] | The compensating-control concept is the formal justification for gateway-side validation in this project |
| IEC TS 62351-1:2007 | "Information security for power system control operations", developing security for the communication protocols defined by IEC TC 57 [6] | Note the boundary: the series targets IEC TC 57 protocols such as the IEC 60870-5 and IEC 61850 series, not Modbus directly [6] |
| IEEE Std 1815 (DNP3) | Electric power systems communications [1], [7] | The protocol family in which Secure Authentication was added |
| IEEE Std 1711.1 (SSPP) | "Cryptographic Protocol for Cyber Security of Substation Serial Links" [1] | A standardised cryptographic protocol for precisely the serial link this project models |
| IEEE Std 1711.2-2019 (SSCP) | "Secure SCADA Communications Protocol" [1] | Reviewed in Part B |

### A.6.3 Research statements of the gap

The reviewed research states the residual weakness in its own words. Kaniewski et al.
identify the legacy link as remaining "vulnerable and unaddressed" even where a security
gateway is correctly deployed [4]. Chan and Zhou state that protection for legacy
devices must be an add-on, and that the bump-in-the-wire approach it forces "is
generally regarded as very inefficient" [2]. Tsang and Smith frame the retrofit problem
as one of achieving security without exceeding the timing constraints of the link [3].

A general 2020 survey of ICS cybersecurity reaches the same conclusion from a wider
vantage point: industrial control systems were kept isolated from the Internet for a
long time, business benefits are now driving convergence with IT environments, and as a
result these systems "have been exposed to the attack vectors used in the majority of
cyber-attacks" while remaining "inherently much less secure against such advanced attack
scenarios" [13].

## A.7 Scope, exclusions and assumptions

| Item | Content |
|---|---|
| In scope | Software simulation on one machine; upward telemetry only; one gateway; several simulated legacy devices; the classical ciphers and AES named in the problem statement; attacks on the legacy link; gateway-side validation and its measurement |
| Out of scope | Real hardware and real field deployment; genuine Modbus or DNP3 framing; downward control commands; key distribution infrastructure; post-quantum cryptography; the stolen-credential and remote-access attack route |
| Assumptions | The gateway sits physically adjacent to the device; the AES key is provisioned securely in advance; clocks are synchronised closely enough for a 30-second acceptance window; the frame layout is public knowledge, as a published protocol would be |

**Stated limitation, carried through the whole project.** Real legacy devices
overwhelmingly transmit plaintext or use proprietary encodings; they do not use Caesar,
Affine, Playfair, Vigenère or Rail Fence. These ciphers are used here as a deliberate
teaching device: they provide a graded scale of weak protection, from a key space of one
up to a polyalphabetic cipher, against which attack techniques from the course can be
demonstrated and timed. Where the literature describes the legacy link it describes it
as unprotected [4], which corresponds to the weakest point on that scale. Any conclusion
in this project that depends on a specific classical cipher is a statement about that
cipher, not about field practice.

## A.8 Summary of Part A

The problem is precisely located: not that AES is unavailable, but that a partly
migrated network has a protected half and an unprotected half, and that the gateway
joining them authenticates the channel without being able to authenticate the
measurement. The causes are documented and structural — protocol design, device
resources, service life, re-certification cost, and the loss of assumed isolation [1],
[2], [3], [4]. The consequences of field-equipment manipulation in a distribution
network are documented [5]. Standards bodies have responded with protocols aimed
specifically at substation serial links [1], [6], [7]. The residual weakness this
project studies is one that the reviewed research names and leaves open [4].

---

# Part B — Review of existing systems and project feasibility

## B.1 Review method and comparison criteria

Three categories are reviewed: standards, research, and commercial products. Each entry
is described in terms of what it does, how it works, and what it does not do. Every
entry is then placed in a single comparison table (B.5) using identical columns, so that
the categories can be read against each other rather than in isolation.

Two rules were applied while compiling this review.

1. **Only sources that were opened are cited.** Several works named in the project brief
   could not be retrieved and have been dropped rather than cited from their titles. The
   omissions are listed in B.9 and in `docs/references.md`.
2. **Unverified cells are marked, not guessed.** Where a source does not state a
   property, the table says "not reported". Where only the title of a standard could be
   confirmed, the table says "not verified in this review". This keeps the comparison
   honest at the cost of leaving visible gaps.

## B.2 Standards

### B.2.1 NIST SP 800-82 Rev. 3

NIST SP 800-82 Rev. 3 is guidance rather than a protocol. It addresses how to secure
operational technology while respecting performance, reliability and safety constraints
[1]. Its relevance to this project is the concept of the compensating control: where a
legacy system cannot support a required security control, the guidance directs the
organisation to consider an alternative that achieves part of the objective, giving the
example that anti-malware cannot be installed on a PLC [1]. It also records the
cost side of the trade-off, noting that encryption "adds latency and may not be suitable
for all OT devices" [1]. It does not specify a cryptographic protocol, so it cannot be
compared on confidentiality or replay protection; it is the source of the
*justification* for gateway-side validation in this project rather than a design to
imitate.

### B.2.2 IEC TS 62351-1:2007

The IEC 62351 series addresses "information security for power system control
operations", and its stated objective is to develop security standards for the
communication protocols defined by IEC TC 57 [6]. Part 1 is an introduction to the
security issues covered by the remaining parts [6]. The scope statement names the
protocol families it targets: the IEC 60870-5 series, the IEC 60870-6 series, the IEC
61850 series, the IEC 61970 series and the IEC 61968 series [6]. **This boundary matters
for the present project: Modbus is not within that list.** A utility running Modbus on
its legacy links therefore cannot simply adopt IEC 62351 to solve the problem, which is
part of why bump-in-the-wire products exist. Chan and Zhou describe what one part of the
series does and why it is hard to adopt: authentication and authorization frameworks
such as IEC 62351-8 are "increasingly applied for authentication and access policy
enforcement in distributed smart grid and newer SCADA systems" and "can avoid or
minimize false command injection", but remain challenging to deploy on some legacy
systems and protocols because of the computational and communication overheads involved
and the need for modifications at both the protocol and the device level [2]. Two things
follow for the comparison in B.5. The guarantee offered by that part is authentication
and authorization rather than confidentiality, which again places authenticity ahead of
secrecy. And the obstacle to adoption is the same one that defines this project: the
legacy device cannot be changed.

### B.2.3 IEEE Std 1711.1 (Substation Serial Protection Protocol)

IEEE Std 1711.1 is a "Standard for a Cryptographic Protocol for Cyber Security of
Substation Serial Links: Substation Serial Protection Protocol (SSPP)" [1], [8]. Its
subject is precisely the link this project models: the serial connection into a
substation device. Its existence as a dedicated standard is strong evidence that the
problem identified in Part A is recognised at standards level and not merely academic.
Only the designation and title could be confirmed, from the standards list in NIST SP
800-82 Rev. 3 Appendix D [1]; the IEEE pages are JavaScript-rendered and returned no
readable content, and the standard itself is paywalled. Because no verified source
supports any property beyond the title, it is **not given a row of its own** in B.5,
where an all-empty row would mislead; it appears there as a note attached to the IEEE
Std 1711.2 row instead.

### B.2.4 IEEE Std 1711.2-2019 (Secure SCADA Communications Protocol)

IEEE Std 1711.2-2019 is the "Standard for Secure SCADA Communications Protocol (SSCP)"
[1], [8]. More detail about SSCP is available from the government project that developed
it (B.4.1): the protocol "ensures control system data integrity through message
authentication and optional encryption", marking each original message with a unique
identifier and an authenticator that the receiving device validates, so that the
receiver can establish that a message came from a trusted source and was not altered in
transit, with unauthenticated commands logged and reported as errors [10]. Two features
are notable. First, **encryption is optional and authentication is the primary
guarantee**, which is the opposite emphasis to a naive "add AES" approach and matches
the argument in B.6. Second, the protocol is described as protocol-independent, so it
secures "all legacy and new control systems designs" [10].

### B.2.5 IEEE Std 1815 (DNP3) and Secure Authentication

DNP3 is published as IEEE Std 1815 [1], [7]. The protocol was developed by Harris,
Distributed Automation Products, and responsibility passed to the DNP Users Group in
November 1993; it was first adopted as IEEE Std 1815 in 2010 and has been updated
periodically since [14]. The user group's documentation covers subset levels and "how to
implement secure authentication" [14], which confirms that DNP3 Secure Authentication
exists as part of the DNP3 documentation set and that implementing it is a task for the
devices at both ends. The publicly readable feature list names output options, secure
configuration and file transfers, addressing, time synchronisation and time-stamped
events, broadcast messages, and data link and application layer confirmation; **message
encryption is not among the listed features** [14]. One phrase on that page needs care:
DNP3 is described as "very efficient for a layered protocol while ensuring high data
integrity" [14], which refers to the error-detection properties of a layered protocol,
not to cryptographic integrity, and it should not be read as a security guarantee. What
is independently confirmed is that DNP3 in its original form was deployed without
protection: Solomakhin et al. describe substations communicating over microwave radio
using "unsecured Distributed Network Protocol v3 (DNP3)" [9].

## B.3 Research

### B.3.1 YASIR (bump-in-the-wire retrofit)

YASIR is a bump-in-the-wire design that retrofits security into time-critical
communication over bandwidth-limited serial links, without modifying the legacy devices
at either end [3]. A pair of modules is inserted into the link; the transmitter-side
module transforms outgoing frames and the receiver-side module reverses the
transformation and checks an authentication tag. The paper's central contribution is the
treatment of latency as a first-class design constraint, and it quantifies the problem:
at 9600 baud one byte takes roughly 1 ms, so two modules that each buffer a 20-byte
message before processing it add 40 ms from buffering alone, rising to about 0.5 s for a
250-byte message [3]. This is measured against real requirements — event notification
between IEDs for bus and transformer protection must complete within 10 ms, and the
maximum delivery time for a data poll response or phasor measurement is up to 0.2 s [3].
YASIR reduces this by processing as a stream: the transmitter adds at most 4 byte times
and the receiver 14 byte times [3]. Its limitation is inherent to the approach — latency
grows with frame length, and the design targets serial links specifically.

One observation in this paper deserves particular emphasis, because it shapes Part D of
this proposal: "retrofitting data privacy to the communications in serial-based SCADA
systems, even the time-critical ones, is a relatively trivial task; the real challenge
lies in retrofitting data authenticity and freshness in a timely manner" [3].
Confidentiality is the easy half. Integrity and freshness are the hard half.

### B.3.2 Predictive YASIR

Predictive YASIR extends the same line of work to reduce latency further [9]. Instead of
treating each message independently, the device predicts the incoming plaintext from
previous observations, compresses, encrypts and authenticates online, and pre-sends part
of the ciphertext before the whole plaintext has arrived [9]. It was implemented in the
Scalable Simulation Framework and tested on Modbus/ASCII, which the authors describe as
widely used in power grid, oil and gas, manufacturing and water treatment control
networks [9]. The reported result is a 15.32 ± 0.27 % improvement in latency [9]. The
limitations are that the evaluation is a simulation rather than a field deployment, and
that the gain depends on the traffic being predictable — periodic polled telemetry is
predictable, but the benefit would not transfer to irregular traffic.

### B.3.3 In-device AES on PLCs

Nguyen et al. implement AES-128 encryption for Modbus TCP/IP directly inside the PLC,
using structured control programming on Siemens S7-1200 and Rockwell CompactLogix
controllers [12]. Because the cryptography runs on the device, there is no unprotected
legacy link at all, which makes this the architectural opposite of the gateway approach.
The reported measurements are an average encryption latency of 41.08 µs with end-to-end
communication delays between 5 and 35 ms, consistent timing across more than 12,000 test
cycles with a standard deviation below 3 µs, and full interoperability with unmodified
Modbus TCP devices [12]. The decisive limitation for this project is the premise: the
method requires a PLC with enough capability and programmability to run AES. The devices
described in Part A cannot do this — NIST records that such systems may lack encryption
capabilities entirely [1], and Chan and Zhou state that implementing cryptographic
defence on old-generation devices is infeasible on resource grounds [2]. In-device AES
is the correct answer where it is possible, and it is unavailable exactly where the
problem is hardest.

### B.3.4 Compensating measures for the legacy link

Kaniewski et al. address the gap left by every gateway design above [4]. They name the
device-to-gateway segment the *legacy link* and state that a security gateway "secures
only the communication on the network side but does not mitigate the absence of security
features in the legacy device", leaving that link "vulnerable and unaddressed" [4]. The
work is a systematic analysis rather than a new protocol: it examines physical,
technical and operational compensating measures, assessing each for its ability to
prevent or detect physical tampering and unauthorised access, and introduces an
evaluation framework covering detection properties, applicability, costs, attack
mitigation and adherence to controls from ISO/IEC 27002 and IEC 62443 [4]. Its own
framing of the obstacle matches Part A: replacement is impractical because of
acquisition cost and amortisation periods, and retrofitting is often infeasible because
of re-certification [4]. It is the closest work to this project's subject, and it is the
source of the gap statement in B.6.

### B.3.5 Surveys

Chan and Zhou survey protection strategies for legacy SCADA in the smart grid and
discuss two add-on defences, the data diode and a detect-and-respond approach [2]. The
survey is useful here for three statements established in Part A: that few systems in
active use were designed with security in mind, that most legacy systems have no source
authentication or command verification mechanism in place, and that false readings from
compromised instrumentation can present a distorted picture of system status to the
master station and trigger disruptive actions [2]. It also judges that protection must
be an add-on and that the bump-in-the-wire approach this forces "is generally regarded
as very inefficient" [2]. Bhamare et al. provide a broader 2020 survey of ICS
cybersecurity, covering the shift from stand-alone systems to cloud-based environments
and the application of machine learning to ICS security [13]; it corroborates the
convergence and exposure trend used in A.1.5, though its focus on machine-learning
defence is adjacent to, rather than part of, the retrofit question studied here.

## B.4 Commercial and government systems

### B.4.1 Hallmark: SEL-3025 link module and SEL-3045 cryptographic card

Hallmark is a cost-shared project of the US Department of Energy's Cybersecurity for
Energy Delivery Systems programme, led by Schweitzer Engineering Laboratories with
Pacific Northwest National Laboratory and CenterPoint Energy Houston Electric [10]. PNNL
developed the Secure SCADA Communications Protocol described in B.2.4, and the project
commercialised two products: the SEL-3045 cryptographic card, aimed at original
equipment manufacturers and carrying FIPS 140-2 Level 2 validated cryptography, and the
SEL-3025 bump-in-the-wire link module for asset owners [10]. The fact sheet states that
the SEL-3025 "adds only minimal latency while securing existing equipment and serial
communication links, including dial up, radios, leased line, or most any serial
communication network", and makes the migration argument explicitly: as SSCP-capable
products appear, "a forklift upgrade of all equipment is unnecessary", because the link
module translates secure serial communications on behalf of the legacy device [10]. Two
limitations are relevant. No latency figure is given, only the word "minimal", so the
comparison table records "not reported". And the module necessarily sits beside the
legacy device, so the segment between them is the same unprotected legacy link that
Kaniewski et al. identify [4].

This product line is the clearest demonstration that the architecture this project
simulates is established engineering practice, standardised as IEEE 1711.2 and sold as
hardware, not a new idea.

### B.4.2 Thales Datacryptor SCADA module

A trade report from January 2005 describes a Thales e-Security encryption appliance for
legacy process control systems, to be marketed in the Datacryptor product line [11]. It
is characterised as "a bulk encryptor in a hardened box that uses the Advanced
Encryption Standard algorithm", supporting Modbus and DNP3, and additionally
authenticating administrators who access maintenance ports using a password and a token
[11]. The distinguishing feature claimed is the combination of data encryption with
encrypted access to maintenance ports [11]. Three cautions apply to this source and are
carried into the comparison table. It is a journalistic announcement, not a datasheet or
a specification. It was forward-looking at the time of writing, describing a product in
"the final stages of development", and the current status of the product was not
verified. And the authentication it describes is for administrative access rather than
per-message authentication of telemetry, so it should not be read as providing message
integrity.

## B.5 Comparison of reviewed systems

Columns are identical for every row. "Legacy link protected?" asks specifically whether
the segment between the legacy device and the protecting element is covered.

| System | Approach | Legacy device modified? | Confidentiality | Integrity and authentication | Replay protection | Legacy link protected? | Reported latency | Limitation |
|---|---|---|---|---|---|---|---|---|
| NIST SP 800-82 Rev. 3 [1] | Guidance, compensating controls | No | Not a protocol | Not a protocol | Not a protocol | Not addressed as a protocol | Not applicable; notes encryption adds latency | Guidance only; prescribes no mechanism |
| IEC 62351 series [6] | Protocol security for IEC TC 57 families | Yes — changes required at both protocol and device level [2] | Series covers "data and communications security"; the part named in the reviewed literature, IEC 62351-8, provides authentication and authorization rather than confidentiality [2], [6] | Yes — authentication and access policy enforcement; can avoid or minimise false command injection [2] | Not stated by the verified sources | **No — scope excludes Modbus; the series targets IEC 60870-5/-6, 61850, 61970, 61968** [6] | No figure given; [2] reports computational and communication overheads as the deployment obstacle | Challenging to deploy on legacy systems and protocols because of overheads and the need for protocol and device changes [2] |
| IEEE Std 1711.2-2019, SSCP (see note on IEEE Std 1711.1 below) [1], [8], [10] | Protocol-independent secure serial protocol | No | **Optional** [10] | Yes — message authentication with a per-message authenticator; unauthenticated commands are logged and reported as errors [10] | Not stated explicitly; each message carries a unique identifier [10] | No — protects the link beyond the module, not device-to-module | Not reported | Encryption is optional, so confidentiality is not guaranteed by adoption alone |
| IEEE Std 1815, DNP3 with Secure Authentication [7], [14] | Protocol extension | Yes — both endpoints must implement it [14] | Not listed among the publicly documented DNP3 features [14] | Yes — secure authentication is part of the DNP3 document set [14] | Not stated in the openly readable DNP3 documentation [14] | No — endpoint-to-endpoint; both ends must support it | Not reported | Original DNP3 was deployed unsecured [9]. DNP3's documented "high data integrity" refers to layered-protocol error detection, not cryptographic protection [14] |
| YASIR [3] | Bump-in-the-wire, serial | No | Yes | Yes, authentication tag | Yes, sequence number | No — device-to-module segment uncovered | Transmitter ≤ 4 byte times, receiver 14 byte times; ≈ 1 ms per byte time at 9600 baud [3] | Latency grows with frame length; serial links only |
| Predictive YASIR [9] | Bump-in-the-wire with traffic prediction | No | Yes | Yes | Not reported | No — same architecture as YASIR | 15.32 ± 0.27 % latency improvement over the prior approach [9] | Simulation only; gain depends on predictable traffic |
| In-device AES-128 on PLCs [12] | In-device cryptography | **Yes — program change on the PLC** | Yes, AES-128 | Not reported | Not reported | Not applicable — no legacy link exists | Encryption 41.08 µs; end-to-end 5–35 ms [12] | Requires a capable, programmable PLC, so unavailable on the constrained devices that define the problem [1], [2] |
| Compensating measures for the legacy link [4] | Analysis of physical, technical and operational measures | No | Partly, depending on measure | Partly, depending on measure | Not addressed | **Yes — this is its explicit subject** | Not reported | An evaluation framework, not an implemented system |
| Hallmark SEL-3025 / SEL-3045 [10] | Commercial bump-in-the-wire module and OEM card | No | Optional, per SSCP [10] | Yes [10] | Not stated explicitly; unique identifier per message [10] | No — device-to-module segment uncovered | "Minimal", no figure given → not reported [10] | Proprietary hardware purchase; legacy link remains |
| Thales Datacryptor SCADA module [11] | Commercial bulk encryptor | No | Yes, AES [11] | Administrative access only, not per-message [11] | Not reported | No | Not reported | 2005 trade announcement of a product then in development; current status not verified |
| **This project** | Simulated protocol-translation gateway | No (devices are simulated) | Yes, AES-256-GCM on the uplink | Yes on the uplink, GCM tag over header and payload | Yes on the AES link (sequence number and 30 s timestamp window); **no on the legacy link, by design** | **No — studied as the object of the work, not fixed** | Gateway path 10.69 µs total, measured; see B.7.1 | Simulation only; classical ciphers are a teaching stand-in; no real Modbus or DNP3 framing |

**Note on IEEE Std 1711.1 (SSPP).** This standard has no row of its own because no
verified source supports any cell beyond its title, and a row of empty cells would
mislead rather than inform. What is established is its designation and subject: a
"Standard for a Cryptographic Protocol for Cyber Security of Substation Serial Links:
Substation Serial Protection Protocol (SSPP)" [1], [8]. Its subject is exactly the link
this project models, so its existence is evidence that the problem in Part A is
recognised at standards level, and it is discussed on that basis in B.2.3. The standard
is paywalled and the IEEE pages are JavaScript-rendered, so its properties could not be
read (`TODO(team)` T8).

## B.6 Gap statement

| Finding from the review | Position of this project |
|---|---|
| Gateway-based retrofit is established and commercially available, standardised as IEEE 1711.2 and sold as the SEL-3025 link module [8], [10] | Reproduced in simulation. No part of the architecture is claimed as new |
| Existing work assumes the legacy protocol carries plaintext [3], [4], [9] | This project adds classical ciphers as a graded scale of weak legacy protection, for teaching and comparison, while stating that this is not field practice |
| The legacy link is acknowledged as the remaining weakness and is left unaddressed by gateway designs [4] | This project demonstrates the consequence with working attacks and measures what simple gateway-side checks do and do not catch |

The gateway described in this proposal is not novel. It is a software reproduction of an
architecture that has existed in commercial hardware for close to two decades [10], [11]
and is standardised [8]. What the project contributes is not a mechanism but evidence:
a reproducible simulation in which the residual vulnerabilities named in Part A can be
exercised, measured and shown to an audience, together with an honest account of the
limits of the mitigations. The specific question it answers — what proportion of
tampered and replayed frames a plausibility check catches, and what it misses — is a
measurement question, and the prototype already shows the answer is not "all" (B.7.1).

One further point sharpens the project's focus. Tsang and Smith observe that retrofitting
confidentiality to these links is comparatively easy, and that the difficulty lies in
authenticity and freshness [3]. The Hallmark programme reaches the same conclusion from
the engineering side, making authentication the primary guarantee of SSCP and encryption
optional [10]. Both support the central finding of Part A: wrapping telemetry in AES is
the straightforward half of the problem, and establishing that the reading was true is
the hard half.

## B.7 Feasibility analysis

### B.7.1 Technical feasibility

The feasibility prototype (`prototype/demo.py`, output in `docs/prototype_run.txt`) runs
the entire pipeline on one machine with a single command and no arguments. It implements
Caesar and Vigenère over a 36-character alphabet, an AES-256-GCM envelope whose header is
authenticated as associated data, and a control centre that checks the tag, the sequence
number and a timestamp window. All of the behaviour the full system depends on is
already demonstrated.

Measured per-stage cost, mean of 2000 runs per stage (Stage 6 of the run log):

| Stage | Mean |
|---|---|
| Caesar encrypt / decrypt | 4.16 µs / 3.97 µs |
| Vigenère encrypt / decrypt | 5.44 µs / 5.81 µs |
| Parse | 1.60 µs |
| Validate | 1.97 µs |
| AES-256-GCM seal / open | 3.15 µs / 3.08 µs |

The gateway path is the sum of the four stages a frame actually passes through inside
the gateway, taken from the table above:

```
legacy decrypt (Caesar)   3.97 µs
parse                     1.60 µs
validate                  1.97 µs
AES-256-GCM seal          3.15 µs
                        ---------
gateway path             10.69 µs
```

The device-side encryption and the control centre's `open` are excluded because they
happen on other machines in the modelled architecture. Using Vigenère rather than Caesar
as the legacy cipher replaces 3.97 µs with 5.81 µs and gives 12.53 µs. For context, YASIR
cites a 10 ms requirement for IED protection messages and up to 0.2 s for a data poll
response [3]. Our measured cryptographic and parsing cost on a laptop is roughly three
orders of magnitude below the tighter of those figures. **This is not a claim that the
design meets that requirement.** It suggests only that cryptography is unlikely to be the
bottleneck in this architecture, and that processing cost is not an obstacle to the
experiments planned in Part C. It is not a prediction of latency on real gateway hardware,
where transmission dominates: at 9600 baud a single byte takes about 1 ms [3], which alone
exceeds the whole measured processing path.

Two qualifications are stated in the run log itself and are repeated here rather than
buried. First, "the classical ciphers are pure Python, while AES runs in the
cryptography library's compiled backend with AES-NI hardware support, so the absolute
figures compare implementations, not the algorithms themselves". Second, the figures are
for one machine, include Python interpreter overhead, and "are not a prediction of
latency on real gateway hardware". The 10.69 µs figure is also computation only and
excludes serial transmission, which is the dominant term in YASIR's analysis [3].

Three results confirm that the vulnerabilities of Part A are reproducible, not merely
asserted:

- **Stage 2, V1.** All 36 additive keys were tried in 0.2039 ms by ciphertext-only
  exhaustive search with a plaintext-recognition test; exactly one candidate passed, and
  both the key (k = 3) and the reading were recovered.
- **Stage 3, V2.** With validation off, a frame edited on the legacy link was delivered
  to the control centre as `290.1 V` against a true value of `230.1 V`, and the log
  records: "GCM tag verified, yet the voltage is false". With validation on, the gross
  edit was rejected — "V=2901 outside plausible range [2000, 2600]" — but a small edit to
  `231.1 V` was still accepted. The run log's own conclusion is the honest one:
  "Validation reduces the problem. It does not remove it."
- **Stage 4, envelope integrity.** One flipped bit in the ciphertext and one flipped bit
  in the header were each rejected with "InvalidTag: GCM tag check failed". This is the
  necessary contrast with Stage 3: the envelope is cryptographically sound, which is
  precisely why a forged reading inside it is believed.

**Verdict: feasible.** Every mechanism the full system requires already runs end to end,
and the measured processing cost is far below the timing constraints reported in the
literature.

### B.7.2 Economic feasibility

The project requires no hardware purchase and no licence. The complete dependency set
for the prototype is one library, `cryptography`, pinned in `requirements.txt`; the
remaining tools planned in Part C — `pytest` and `matplotlib` — are likewise free and
open source. The work runs on the team's own laptops, and the prototype has been
executed on more than one machine already. There is no cloud, storage or data
acquisition cost, because all telemetry is generated by the simulator.

**Verdict: feasible.** Total monetary cost is zero; the only resource consumed is team
time.

### B.7.3 Operational feasibility

The prototype runs with `python prototype/demo.py` and no arguments, and prints a
labelled log in which each stage names what it is demonstrating and which vulnerability
it corresponds to. A reader who is not a cryptographer can follow it, because every
reading is printed in engineering units alongside the raw frame — for example
`device 07  230.1 V  15.2 A  49.98 Hz  breaker closed  seq 123`. The demonstration
planned in Part C extends the same pattern to a scripted scenario list. The main
operational risk is a failure on an unfamiliar machine during the presentation, which is
addressed in the risk register (B.8) by pinned dependencies, a single run script and a
recorded backup run.

**Verdict: feasible.** One command, readable output, and a rehearsal path that does not
depend on live execution.

### B.7.4 Schedule feasibility

The deliverable for this milestone is this document plus the prototype, and both exist.
The remaining work is the full cipher set, the gateway and control centre as separate
processes, the attack suite and the measurement experiments, in the sequence set out in
Part C. The architecture is already proven end to end, so the remaining tasks are
extensions of working code rather than unresolved design problems. The classical ciphers
are individually small and independently testable, which makes the work easy to divide
among three team members.

**Verdict: feasible, subject to dates.** `TODO(team)`: insert the actual milestone dates
and marks so that this assessment can be stated against a calendar rather than a
sequence.

### B.7.5 Legal and ethical feasibility

The entire project is a simulation. No real grid equipment, utility network, vendor
product or third-party system is touched at any point; the telemetry is synthetic, the
devices are software objects, and all communication is local to one machine. The attacks
implemented are executed only against the project's own simulated components. No
vulnerability in any real product is investigated or disclosed. The cryptographic
material used is generated at run time or read from an environment variable, and no key
appears in the source code. The ciphers implemented from scratch are historical and are
used for teaching purposes; AES is used through a maintained library rather than
reimplemented, which is also the responsible engineering choice.

**Verdict: feasible.** Nothing in the project requires access to, or testing against,
any system the team does not own.

### B.7.6 Feasibility verdicts

| Dimension | Verdict | One-line reason |
|---|---|---|
| Technical | Feasible | The full pipeline already runs; measured gateway path is 10.69 µs against a 10 ms constraint in the literature [3] |
| Economic | Feasible | Zero cost: one free library, free tooling, existing laptops |
| Operational | Feasible | One command, output readable by a non-specialist, recorded backup run planned |
| Schedule | Feasible, subject to dates | Remaining work extends proven code; dates to be confirmed by the team |
| Legal and ethical | Feasible | Entirely simulated; no real equipment, network or third-party product involved |

## B.8 Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| K1 | Classical ciphers cannot handle numeric telemetry | High | High | A single 36-character alphabet, `A–Z` then `0–9`, with arithmetic modulo 36. Already implemented and verified in the prototype |
| K2 | Playfair padding corrupts readings | Medium | High | `X` reserved as the filler and excluded from readings; the parser strips it after decryption. To be covered by round-trip tests |
| K3 | AES misuse, such as nonce reuse or a weak mode | Medium | High | GCM only, a fresh random 96-bit nonce per message, library primitives rather than hand-written crypto, header authenticated as associated data. Verified by Stage 4 of the prototype |
| K4 | Frequency analysis is weak on short structured messages | Medium | Medium | Use the fixed field tags at known positions as the basis for known-plaintext attacks, and use exhaustive search with a recognition test where the key space is small, as demonstrated in Stage 2 |
| K5 | Scope creep | Medium | Medium | The out-of-scope list in A.7 is explicit and is treated as binding |
| K6 | Demo fails on another machine | Low | High | Pinned dependency versions, a single run script with no arguments, and a recorded backup run. The prototype has already been executed successfully on a second machine |
| K7 | A cited source becomes unreachable before submission | Low | Medium | Every source was opened during preparation, and the verification status of each is recorded in `docs/references.md` |

## B.9 Summary of Part B

The review covers five standards, five research works and two commercial systems, all
compared on identical criteria in B.5. The architecture this project simulates is
standardised and commercially available, which is stated plainly rather than obscured.
The consistent finding across categories is that protection stops at the gateway: YASIR
and the SEL-3025 protect the link beyond the module, in-device AES avoids the problem
only where the device is capable enough to run cryptography, and Kaniewski et al. name
the uncovered segment and leave it as an open question [3], [4], [10], [12]. Feasibility
is established on all five dimensions, with the technical case resting on a prototype
that already runs end to end and reproduces three of the eight transition
vulnerabilities.

**Sources dropped from this review.** Two works named in the project brief could not be
opened and are therefore not cited anywhere in this document: the University of Messina
proxy paper, whose repository returned HTTP 403, and the Modbus/TCP Security
specification, whose published URL returned HTTP 404 while the specification index page
is JavaScript-rendered and exposed no retrievable document. Their absence weakens two
specific points — the proxy-based category in B.3 rests on a single analysis [4] rather
than an implementation, and the claim in A.1.4 that Modbus carries no security is
supported by secondary sources [1], [2], [3] rather than by the protocol specification
itself. Both gaps are recorded as `TODO(team)` items.

# Part C — Objectives and methodology of the proposed work

## C.1 Aim

To build a reproducible software simulation of a legacy-to-AES protocol translation
gateway, and to use it to demonstrate and measure which security weaknesses persist, and
which are newly introduced, while an industrial control network is partly migrated.

## C.2 Objectives

### C.2.1 Objective table

No objective sets a numeric performance target. Targets of that kind would have to be
invented, because no source states what a simulated gateway on a laptop should achieve,
and inventing one would also presuppose the answer to the questions in C.3. Where a
timing reference is needed, the figures reported by Tsang and Smith are used as external
reference points rather than as project targets: 10 ms for IED protection messages and
up to 0.2 s for a data poll response [3].

| # | Objective | Rationale | Deliverable | Measurable success criterion |
|---|---|---|---|---|
| **O1** | Implement the six classical ciphers and the AES-256-GCM envelope | The problem statement names these concepts; they are also the graded scale of weak protection defined in A.7 | `ciphers/`, `gateway/aes_envelope.py` | Every cipher satisfies `Decrypt(Encrypt(m)) = m` for the full test vector set including edge cases; invalid Affine keys are rejected; an altered envelope, header or tag is rejected in every case |
| **O2** | Build the gateway, device simulator and control centre as separate communicating processes | The architecture under study must exist before its weaknesses can be measured | `telemetry/`, `gateway/`, `control_centre/` | A reading sent by the device arrives byte-identical at the control centre across all six ciphers; the gateway logs a reason for every accept and reject decision |
| **O3** | Implement the attacks on the legacy link | V1 and V6 are claims about the legacy link; they must be shown working, not asserted | `attacks/` | Each classical cipher's key is recovered by the stated technique, and the time to recover is recorded for each; a replayed legacy frame is accepted by an unprotected gateway |
| **O4** | Demonstrate and measure the transition vulnerabilities V1 to V8 | This is the "study of transition vulnerabilities" the problem statement requires | `attacks/`, `experiments/` | Each of V1 to V8 has either a scripted demonstration that produces the predicted outcome, or a written statement of why it is argued rather than demonstrated |
| **O5** | Evaluate gateway-side mitigations and state their limits | A study that shows only the problem is incomplete; a study that claims the problem is solved would be false | `gateway/validator.py`, `experiments/detection_rate.py` | The detection rate against tampered and replayed frames is reported for validation off and on, together with a characterisation of the frames that pass undetected and the rate of legitimate readings wrongly rejected |

Note on O5: the criterion deliberately does not say "detection rate above X %". The
prototype has already shown the answer is below 100 % — a small in-range edit passed with
validation on — so the measurement of interest is *which* frames escape, not whether a
threshold is met.

### C.2.2 Traceability

Each objective traces to the vulnerabilities it addresses, the modules that implement it,
the experiment that measures it, and the metric reported.

| Objective | Vulnerability | Module (C.5.2) | Experiment (C.6.3) | Metric | Success criterion |
|---|---|---|---|---|---|
| O1 | V5 | `ciphers/*`, `gateway/aes_envelope.py` | E3 Overhead; E2 Latency | Payload bytes before and after wrapping; µs per primitive | Round trip exact for every cipher; ECB and GCM outputs distinguishable in E5 |
| O2 | V3, V4, V8 | `telemetry/device_sim.py`, `gateway/gateway.py`, `gateway/profiles.py`, `control_centre/centre.py` | E2 Latency; E3 Overhead | µs per gateway stage; envelope size | End-to-end identity holds; per-stage cost reported alongside the 10 ms figure from [3] as context, not as a claim of meeting it |
| O3 | V1 | `attacks/brute_force.py`, `known_plaintext.py`, `frequency.py`, `kasiski.py` | E1 Break time | Seconds to recover each key | Key recovered for every classical cipher, with time recorded |
| O3 | V6 | `attacks/mitm_proxy.py` | E4 Detection rate | Share of replays accepted | Legacy replay accepted without sequence checks; AES replay rejected |
| O4 | V2 | `attacks/mitm_proxy.py`, `gateway/validator.py` | E4 Detection rate | Share of tampered frames reaching the centre | Reported for validation off and on; undetected frames characterised by edit size |
| O4 | V5 | `attacks/ecb_demo.py` | E5 ECB against GCM | Repeated ciphertext blocks observed | Repetition visible under ECB and absent under GCM |
| O4 | V7 | `gateway/gateway.py` passthrough mode | E4 Detection rate | Frames accepted while in passthrough | Downgrade reduces protection to the legacy level, shown and logged |
| O4 | V8 | `experiments/timing.py` | E2 Latency | µs added per frame | Added cost reported with its implementation caveat (C.10) |
| O5 | V2, V6 | `gateway/validator.py` | E4 Detection rate; E6 False alarms | Detection rate; legitimate readings rejected | Both states reported; misses characterised; false alarm rate stated |

V3 and V4 appear against O2 because they are properties of the architecture rather than
behaviours that can be triggered: the gateway necessarily holds plaintext and two key
sets. They are argued from the design and recorded as such in A.5, not demonstrated by a
script. Stating this openly is preferable to staging a demonstration that proves only
that the code was written to fail.

## C.3 Research questions

Each question is answerable by a named experiment, and none is rhetorical — the prototype
has already shown that the answers are not all favourable to the design.

| # | Question | Answered by |
|---|---|---|
| **Q1** | How long does it take to recover the key for each classical cipher at this frame length, and does a 27-character structured frame give enough material for frequency analysis and Kasiski examination to work at all? | E1 Break time |
| **Q2** | What share of tampered legacy frames does gateway validation detect, and which kinds pass undetected? | E4 Detection rate |
| **Q3** | What does validation cost in false alarms — how many legitimate readings are rejected, and under what conditions? | E6 False alarms |
| **Q4** | What processing cost does the gateway add per frame, and how does it compare with the latency constraints reported for real SCADA links [3]? | E2 Latency |
| **Q5** | What size overhead does the AES envelope impose on a short telemetry frame, and does that matter on a link of the bandwidth described in [3]? | E3 Overhead |
| **Q6** | Does the choice of AES mode change what an observer can learn from repetitive telemetry? | E5 ECB against GCM |

Q1 contains a genuine uncertainty worth stating in advance. Classical cryptanalysis
normally assumes a long passage of natural language; a 27-character frame over a
36-character alphabet is short and highly structured. It is possible that frequency
analysis and Kasiski examination will perform poorly on a single frame and will need many
frames accumulated under one key. That outcome is itself a finding and will be reported
as one, not hidden by switching to an easier technique.

## C.4 Methodology

### C.4.1 Overall approach

The approach is simulation and controlled comparison, not invention. An architecture that
already exists in standards and products (Part B) is reproduced in software, instrumented
so that every stage can be timed and every decision logged, and then subjected to attacks
under two configurations — validation off and validation on — so that the effect of the
mitigation can be isolated. The figure in `docs/figures/methodology.svg` shows the five
phases and the verification gate between them.

### C.4.2 Phase table

| Phase | Inputs | Activities | Outputs | How it is verified |
|---|---|---|---|---|
| **P1** Ciphers and AES | Cipher definitions; the 36-character alphabet; frame format C.5.3 | Implement Caesar, Additive, Affine, Playfair, Vigenère, Rail Fence from scratch; implement the AES-256-GCM envelope with the header as associated data | `ciphers/`, `gateway/aes_envelope.py`, unit tests | Round-trip property for every cipher over the full test vector set; invalid Affine keys rejected; altered envelope, header or tag rejected |
| **P2** Gateway and centre | P1 output; device profiles | Build the device simulator, profile lookup, parser, switchable validator, logger and control centre; split into three processes over local TCP sockets | `telemetry/`, `gateway/`, `control_centre/`, `run_demo.py` | End-to-end test: a reading sent by the device arrives unchanged at the centre, for every cipher |
| **P3** Attacks | P2 output | Implement exhaustive search, known-plaintext, frequency analysis, Kasiski and index of coincidence, the MITM proxy for tamper, inject and replay, the ECB demonstration and the downgrade trigger | `attacks/` | Each attack produces its predicted outcome: a recovered key, an accepted forgery, or an observable pattern |
| **P4** Mitigations | P3 output | Implement range, rate-of-change and sequence checks; re-run every Phase 3 attack with validation off and then on, holding everything else constant | `gateway/validator.py`, paired result sets | Detection counted for both validator states over the same attack set and the same seed |
| **P5** Experiments and analysis | P4 output | Run E1 to E6, write CSV and charts, analyse and answer Q1 to Q6 | `experiments/results/*.csv`, `*.png`, Part D and the final report | Every figure in the report traceable to a CSV produced by a re-runnable script |

### C.4.3 Work already complete

The feasibility prototype discharges part of P1 and P2 and some of P3, which is why the
schedule assessment in B.7.4 treats the remaining work as extension rather than
exploration.

| Phase | Already done in `prototype/demo.py` | Still to do |
|---|---|---|
| P1 | Caesar and Vigenère over the 36-character alphabet; AES-256-GCM envelope with authenticated header, fresh nonce per message, key from environment or generated | Additive, Affine, Playfair, Rail Fence; formal test suite |
| P2 | Device reading, profile-free single-device path, parser, switchable validator, control centre with tag, sequence and timestamp checks | Per-device profiles, three-process split over sockets, logger, multiple devices |
| P3 | Exhaustive key search with recognition test; tamper on the legacy link; replay on both links; envelope bit-flip rejection | Known-plaintext, frequency, Kasiski and IoC; ECB demonstration; downgrade |
| P4 | Validator toggling demonstrated manually for one attack | Systematic paired runs across the whole attack set |
| P5 | Per-stage timing harness, mean of 2000 runs | E1 and E3 to E6; CSV and chart output |

## C.5 System design

### C.5.1 Architecture

See `docs/figures/architecture.svg`. Telemetry flows from the device simulator across the
unprotected legacy link, through the six stages of the gateway, across the AES link, to
the control centre. A man-in-the-middle sits on the legacy link; a passive attacker sits
on the AES link.

### C.5.2 Component responsibilities

| Module | Responsibility |
|---|---|
| `ciphers/alphabet.py` | The 36-character alphabet and modulo-36 helpers shared by every classical cipher |
| `ciphers/*.py` | One cipher each, written from scratch, no cipher libraries |
| `telemetry/reading.py` | Format and parse readings; reject malformed frames |
| `telemetry/device_sim.py` | Generate readings and encrypt with the device's own legacy cipher and key |
| `gateway/profiles.py` | Per-device cipher and key; reject unknown devices |
| `gateway/validator.py` | Range, rate-of-change and sequence checks; switchable on and off |
| `gateway/aes_envelope.py` | AES-256-GCM pack and unpack, header as associated data |
| `gateway/gateway.py` | Orchestrate the pipeline and log every decision with a reason |
| `control_centre/centre.py` | Verify tag, sequence and timestamp; display or reject |
| `attacks/*.py` | One attack technique each |
| `experiments/*.py` | One experiment each, writing a CSV and a chart |

### C.5.3 Telemetry frame format

Fixed width, no separators, letters as field tags, every character drawn from the
36-character alphabet. Example: `D07V2301I0152F4998B1Q000123`, 27 characters.

| Tag | Field | Width | Meaning | Example |
|---|---|---|---|---|
| `D` | Device ID | 2 | Identifies the device behind the gateway | `07` |
| `V` | Voltage | 4 | Tenths of a volt | `2301` = 230.1 V |
| `I` | Current | 4 | Tenths of an ampere | `0152` = 15.2 A |
| `F` | Frequency | 4 | Hundredths of a hertz | `4998` = 49.98 Hz |
| `B` | Breaker | 1 | 0 open, 1 closed | `1` = closed |
| `Q` | Sequence | 6 | Device counter | `000123` |

`X` is reserved as the Playfair filler and never appears in a reading, so the parser can
strip it after Playfair decryption without ambiguity.

### C.5.4 Gateway processing pipeline

| Step | Action | On failure |
|---|---|---|
| 1 | Receive a frame from a legacy device | Log and drop |
| 2 | Look up the device profile for cipher and key | Reject unknown device, with reason |
| 3 | Decrypt with that device's legacy cipher | Log and drop |
| 4 | Parse the frame | Reject malformed reading, with reason |
| 5 | Validate: plausible ranges, rate-of-change limit, increasing sequence | Reject, with the failing check named |
| 6 | Build the AES envelope and send | Log the error |
| 7 | Log the decision and its reason | — |

Step 5 must be switchable at run time, because the comparison in P4 depends on running
the identical attack set in both states.

### C.5.5 AES envelope structure

| Field | Size | Content | Authenticated |
|---|---|---|---|
| `version` | 1 byte | Envelope format version | Yes, as associated data |
| `gateway_id` | 2 bytes | Identifies the gateway | Yes, as associated data |
| `gateway_seq` | 8 bytes | Strictly increasing per gateway | Yes, as associated data |
| `timestamp` | 8 bytes | Milliseconds since epoch | Yes, as associated data |
| `nonce` | 12 bytes | Fresh random value per message | Not authenticated; it is an input to GCM |
| `ciphertext + tag` | 27 bytes + 16 bytes | AES-256-GCM output over the frame | Yes, by construction |

Total 74 bytes for a 27-byte frame, a 47-byte overhead, as measured in the prototype.
The key is read from a file or environment variable and never appears in source code. The
control centre rejects a bad tag, a repeated or lower sequence number, and a timestamp
outside a 30-second window. Because the header is passed as associated data, editing it
fails the tag check exactly as editing the ciphertext does, which the prototype
confirms.

## C.6 Experimental design

### C.6.1 Controls held constant

Across every experiment: the same frame format and alphabet, the same device identity and
starting sequence number, the same machine, a fixed random seed for attack frame
selection so that paired runs are comparable, and a warmed AES backend so that first-call
initialisation does not contaminate timings. The only variable that changes between
paired runs in E4 and E6 is the validator state.

### C.6.2 Metrics

| Metric | Definition | Unit |
|---|---|---|
| Break time | Wall-clock time from receiving ciphertext to recovering the key | seconds |
| Stage latency | Mean processing time per gateway stage over repeated runs | µs |
| Overhead | Envelope size minus frame size | bytes |
| Detection rate | Tampered or replayed frames rejected, divided by tampered or replayed frames sent | share |
| False alarm rate | Legitimate readings rejected, divided by legitimate readings sent | share |

### C.6.3 Experiment plan

| # | Experiment | Independent variable | Dependent variable | Controls | Runs | Output |
|---|---|---|---|---|---|---|
| **E1** | Break time | Cipher (Caesar, Additive, Affine, Playfair, Vigenère, Rail Fence) and attack technique | Time to recover the key; whether recovery succeeds at all | Same plaintext frame set, same machine, same key-generation procedure | Repeated per cipher, count fixed in advance and reported with the result | CSV + bar chart |
| **E2** | Latency | Gateway stage (legacy decrypt, parse, validate, AES seal, AES open) and legacy cipher | Mean processing time | Warmed backend, single process, no network, same frame | 2000 per stage, matching the prototype harness | CSV + table + chart |
| **E3** | Overhead | Frame length | Envelope size and absolute overhead | Same envelope structure throughout | One per frame length tested | CSV + table |
| **E4** | Detection rate | **Validation OFF / ON**, and attack type (tamper gross, tamper small, inject, replay legacy, replay AES, downgrade) | Share of malicious frames rejected; where each was rejected | Identical attack set and seed in both states | Same attack set run twice, once per validator state | CSV + table |
| **E5** | ECB against GCM | AES mode | Count of repeated ciphertext blocks across repetitive telemetry | Same plaintext sequence and key | One run per mode | CSV + side-by-side figure |
| **E6** | False alarms | **Validation OFF / ON**, and reading profile (steady, ramping, step change at a breaker event) | Share of legitimate readings rejected; which check fired | Same generated reading stream in both states | Same stream run twice, once per validator state | CSV + table |

E4 and E6 are the core of the study and share a design: the same inputs are presented to
the same system twice, differing only in the validator state, so that any difference in
outcome is attributable to validation alone. E6 exists because E4 alone would be
misleading — a validator can be made to catch more attacks simply by tightening its
limits, at the cost of rejecting genuine readings, and a breaker event produces exactly
the sudden change that a rate-of-change check is designed to suppress.

### C.6.4 Reporting

Every experiment writes a CSV and a chart to `experiments/results/`. Every figure in the
final report is traceable to one of those CSVs, and every CSV is reproducible by
re-running its script. Results that contradict the project's expectations are reported as
found; the prototype's demonstration that validation does not stop a small in-range edit
is the model for this.

## C.7 Testing strategy

| Test | Requirement | Covers |
|---|---|---|
| Round trip | `Decrypt(Encrypt(m)) = m` for every cipher, including empty input, single character, maximum length, repeated characters and all-digit frames | O1 |
| Affine key validation | Every `a` not coprime to 36 is rejected; all 12 valid values accepted | O1 |
| Playfair edge cases | Doubled characters and odd lengths handled; the `X` filler is inserted and stripped correctly without corrupting a reading | O1, risk K2 |
| AES envelope integrity | An altered ciphertext, an altered header and an altered tag are each rejected | O1, K3 |
| Replay rejection | A second copy of an envelope is rejected on its sequence number | O3, V6 |
| End to end | A reading sent by the device arrives unchanged at the control centre, for every cipher | O2 |
| Validator behaviour | Each check fires on a crafted input and stays silent on a valid one | O5 |

Tests are run with `pytest`. The round-trip and envelope tests are the regression barrier
for every later change.

## C.8 Tools, environment and reproducibility

| Need | Choice | One-line justification |
|---|---|---|
| Language | Python 3.11 or newer | Available on all team machines; prototype verified on 3.11.9 |
| Classical ciphers | Written from scratch, no cipher libraries | The implementation is the coursework; a library would remove the learning and the ability to instrument it |
| AES | `cryptography` library, AES-256-GCM | Hand-rolled AES would be the single largest correctness risk in the project; a maintained library is the responsible choice |
| Communication | Standard `socket` module, TCP on localhost | No dependency, and it makes the three components genuinely separate processes |
| Tests | `pytest` | Standard, already a dependency-free habit for the team |
| Charts | `matplotlib` | Produces the CSV-backed figures required in C.6.4 |
| Dashboard (optional, last) | Streamlit | Only if time remains after all experiments are complete; not on the critical path |

Reproducibility rests on four things: pinned dependency versions in `requirements.txt`, a
single entry point that takes no arguments, a fixed random seed for attack frame
selection, and the rule that every reported figure comes from a committed CSV.

`TODO(team)`: confirm Python 3.11 is permitted by the course (T6).

## C.9 Work plan

| Stage | Content | Owner | Dates |
|---|---|---|---|
| Milestone 2 | This proposal, the feasibility prototype, run log and figures | All three | Complete |
| Next | Phase 1 and Phase 2: full cipher set, device simulator, gateway, control centre, three-process split | `TODO(team)` | `TODO(team)` |
| After that | Phase 3 and Phase 4: attack suite, validator, paired runs | `TODO(team)` | `TODO(team)` |
| Final | Phase 5: experiments, charts, report, demo rehearsal, optional dashboard | `TODO(team)` | `TODO(team)` |

`TODO(team)`: insert the actual milestone dates and marks, and assign an owner per stage
(T7). The cipher implementations in Phase 1 are independent of one another and are the
natural unit of division among three members.

## C.10 Threats to validity and limitations of the method

Stating these in advance is part of the method, not an apology for it.

| # | Threat | Effect on conclusions | How it is handled |
|---|---|---|---|
| L1 | Classical ciphers are not what legacy devices use | Cipher-specific results do not transfer to field practice | Stated in A.7 and repeated wherever a cipher-specific result is reported; the unprotected case corresponds to the documented reality [4] |
| L2 | Timings mix a pure-Python implementation with a compiled, AES-NI accelerated library | Absolute comparisons between classical ciphers and AES measure implementations, not algorithms | The caveat is printed in the run log itself and repeated beside every timing in this document |
| L3 | Measurements are taken on one laptop, in one process, with no network | Figures are not predictions of gateway hardware performance | Stated in the run log and in B.7.1; external reference figures are cited from [3] rather than produced here |
| L4 | The validator's plausibility ranges are chosen by the team | Detection and false-alarm rates depend on a parameter we set | The ranges are declared as modelling assumptions in the code and in A.7; E6 measures the cost of the choice rather than hiding it |
| L5 | Frames are short and highly structured | Classical cryptanalysis may underperform compared with textbook results | Treated as a finding to report (Q1), not a problem to engineer around |
| L6 | The simulation omits real protocol framing, timing and error behaviour | Conclusions apply to the model, not to a Modbus or DNP3 deployment | Declared out of scope in A.7; no claim is made about real deployments |
| L7 | The attack set is written by the same team that writes the defence | Risk of testing only what the validator already catches | E4 includes attack types chosen to defeat the validator by design, in particular the small in-range edit already shown to pass |

L7 is the most serious of these for a project of this shape, and the prototype shows the
intended discipline: the small-edit case was included precisely because it defeats the
mitigation, and its success is reported rather than omitted.

## C.11 Summary of Part C

The aim is a measurement, not a mechanism. Five objectives run from implementing the
named algorithms to evaluating mitigations, each with a success criterion that can be
checked rather than asserted, and each traced in C.2.2 to the vulnerability it addresses,
the module that implements it and the experiment that measures it. The method is five
phases with a verification gate between them, two of which are already partly discharged
by the feasibility prototype. The experimental design turns on a single controlled
comparison — the same attacks against the same system with validation off and on — and is
accompanied by a false-alarm experiment so that the cost of the mitigation is reported
alongside its benefit.

# Part D — Relevance of algorithms and techniques

## D.1 Selection criteria

Every algorithm in this project was chosen against four criteria, in order.

| # | Criterion | Consequence |
|---|---|---|
| 1 | Named by the problem statement | The classical ciphers and AES are fixed by the course brief; they are not free choices |
| 2 | Able to operate on the telemetry alphabet | A reading contains digits, so a 26-letter alphabet is unusable. All classical ciphers work over the 36-character set `A–Z` then `0–9`, modulo 36 |
| 3 | Models something real about legacy protection | Each classical cipher must correspond to a recognisable grade of weakness, from "none" upward (A.7) |
| 4 | Correct by construction where correctness matters | AES is used through a maintained library; the classical ciphers are written from scratch because implementing them is the coursework and because they must be instrumentable |

The classical ciphers are included because the brief names them and because they give a
*graded* scale of weakness that a single plaintext case cannot. Their relevance is
pedagogical and comparative, not descriptive of field practice — the literature describes
the real legacy link as unprotected [4], which is the zero point of the scale.

### D.1.1 Course concepts mapped to the problem

| Course concept | Role in this project | What it demonstrates |
|---|---|---|
| Caesar, Additive | Weakest legacy protection | Key space small enough to try every key |
| Affine | Slightly stronger monoalphabetic | Still a fixed substitution, broken by known plaintext |
| Playfair | Digram substitution | Hides single-letter frequencies, not digram patterns |
| Vigenère | Polyalphabetic | Broken once the key length is found |
| Rail Fence | Rearrangement only | Content unchanged, so character counts leak |
| AES | Modern target | Confidentiality, and with GCM also integrity |

## D.2 Classical ciphers as a graded model of weak legacy protection

All operate on `x ∈ Z₃₆`, the index of a character in `A–Z` followed by `0–9`.

The table in D.2.1 carries the formula, key space, weakness modelled and attack for each.
The notes below give only what the table cannot: why each earns its place.

**Caesar** is the zero-key case — protection that carries no secret at all, broken in
0.2039 ms in the prototype. **Additive** adds a real but tiny key, modelling a realistic
failure mode: a key short enough for a technician to type is short enough to enumerate.
**Affine** looks cleverer but is still a fixed substitution, and it is the cipher that
best exposes the arithmetic of a composite modulus (D.5.2).

**Playfair** is the first to defeat naive single-character frequency analysis, and its
nominal key space of `36!` is the lesson: a keyword-derived grid occupies a tiny region of
that space, so the headline figure overstates the real one. It is also the only cipher
here that changes message length, because a doubled pair forces a filler (D.2.2).

**Vigenère** is the strongest legacy case studied — the same plaintext character maps
differently by position — but collapses into `L` independent additive ciphers once the key
length is known. **Rail Fence** substitutes nothing at all, so the character multiset is
unchanged; for a fixed-format frame the leaked character counts are nearly enough to
reconstruct the reading, which makes it the cleanest demonstration that rearrangement is
not concealment.

All six support V1 and feed E1.

### D.2.1 Comparison

| Cipher | Formula over Z₃₆ | Key space (36 chars) | Legacy weakness modelled | Attack that breaks it | Supports |
|---|---|---|---|---|---|
| Caesar | `x + 3` | 1 | Obfuscation with no secret | Exhaustive search + recognition | V1, E1 |
| Additive | `x + k` | 36 | Key too small to matter | Exhaustive search + recognition | V1, E1 |
| Affine | `a·x + b`, `gcd(a,36)=1` | 12 × 36 = 432 | Fixed substitution dressed up | Known plaintext on two tags; exhaustive search | V1, E1 |
| Playfair | Digram map on a 6 × 6 grid | `36!` nominal, far less in practice | Hides letter frequency, not digram structure | Known plaintext on fixed tags | V1, E1 |
| Vigenère | `xᵢ + k₍ᵢ mod L₎` | `36ᴸ` | Strongest legacy case studied | Kasiski / IoC for `L`, then per-position additive | V1, E1 |
| Rail Fence | Permutation over `r` rails | ≈ 25 usable values | Rearrangement without substitution | Exhaustive search; character counts leak | V1, E1 |

Read down the key-space column and the point of the exercise appears: every value is
either tiny or illusory. None of these schemes is a defence. They are a measuring stick
for how fast a defence fails.

### D.2.2 Worked example

The same frame `D07V2301I0152F4998B1Q000123` encrypted with each cipher. **All outputs
below are produced by executed code, not hand calculation**, and the Caesar and Vigenère
rows match `docs/prototype_run.txt` exactly.

| Cipher | Sample key | Ciphertext | Round trip |
|---|---|---|---|
| Caesar | shift 3 (fixed) | `G3AY5634L3485I7CCBE4T333456` | yes |
| Additive | k = 11 | `OBI6DEBCTBCGDQFKKJMC1BBBCDE` | yes |
| Affine | a = 5, b = 8 | `X43FEJ49M49TE7ODD8N9Q4449EJ` | yes |
| Playfair | keyword `GRID` | `I1D13Y12F6Z70J5449D3N33U123Y` | yes |
| Vigenère | keyword `GRIDKEY` | `JHFYC7O7Z84F63AQHBL5E6H84C7` | yes |
| Rail Fence | 3 rails | `D2I29Q10V3105F9810027014B03` | yes |

Two observations that only appear once real output is inspected. The Playfair ciphertext
is **28 characters, not 27**: the digram split is `D0 7V 23 01 I0 15 2F 49 98 B1 Q0 0X 01
23`, where the doubled `00` in the sequence field forces the reserved filler `X`. The
filler lands *inside* the frame, not at the end, so the parser must strip every `X` rather
than trimming trailing ones — a detail that silently corrupts readings if missed, and the
reason K2 appears in the risk register. The Rail Fence output contains exactly the same
characters as the plaintext in a different order, which is visible by inspection and is
the whole of its weakness.

## D.3 AES-256-GCM as the migration target

**Why AES.** AES is the published US federal standard for symmetric encryption, selected
from the Rijndael family through open competition [15]. It is specified in an open
standard, implemented in maintained libraries with hardware acceleration, and already the
algorithm named by the commercial systems reviewed in Part B [11], which makes the
simulation comparable to the practice it models.

**Why 256-bit.** The measured cost of the larger key is negligible here — seal 3.15 µs and
open 3.08 µs, against a pure-Python Caesar decrypt at 3.97 µs. Where the stronger option
costs nothing measurable, taking it is the correct default.

**Why GCM rather than encryption alone.** SP 800-38D specifies GCM as "an algorithm for
authenticated encryption with associated data" [16]. Confidentiality alone would not
address the problem in Part A, where the hard half is authenticity and freshness rather
than secrecy [3].

| Mode | Confidentiality | Integrity | Pattern leakage | IV / nonce requirement |
|---|---|---|---|---|
| ECB | Weak in practice | None | **Severe** — identical plaintext blocks give identical ciphertext, and telemetry is highly repetitive | None, which is part of the problem |
| CBC | Yes | None by itself | Low | Unpredictable IV per message |
| CTR | Yes | None by itself | Low | Unique nonce per message |
| **GCM** | Yes | **Yes, with a tag over ciphertext and associated data** | Low | **Unique IV per key, 96 bits recommended** [16] |

ECB is included in the project not as a candidate but as a demonstration (E5): repeated
voltage readings produce repeated ciphertext blocks, which is V5 made visible. CBC and CTR
are both acceptable for confidentiality but provide no integrity on their own, which is
precisely the gap that allows an altered envelope to pass unnoticed.

**The 96-bit nonce, and why reuse is catastrophic.** SP 800-38D recommends that
implementations restrict IV support to 96 bits "to promote interoperability, efficiency,
and simplicity of design" [16]. The uniqueness requirement is stated as a hard bound: the
probability of invoking authenticated encryption with the same IV and key on two distinct
sets of input "shall be no greater than 2⁻³²" [16]. The standard's own caution is blunt —
a breach of that requirement "may compromise the security assurance almost entirely", and
GCM "should not be deployed unless compliance with this uniqueness requirement is
ensured"; if even one IV repeats under a given key, the implementation "may be vulnerable
to the forgery attacks" described in the supporting reference [16]. This is why the
envelope draws a fresh random 96-bit nonce per message rather than using a counter that
could be reset by a gateway restart, and why K3 in the risk register treats nonce reuse as
a high-impact risk.

**Associated data and the tag.** The envelope's header — version, gateway identifier,
gateway sequence number and timestamp — is passed to GCM as associated data. It is
authenticated but not encrypted, which is correct: the control centre needs to read the
sequence number and timestamp in order to reject replays before attempting decryption, yet
must be certain they were not altered. Stage 4 of the prototype confirms the construction
works in both directions. One flipped bit in the ciphertext and one flipped bit inside the
header's `gateway_id` field were each rejected with `InvalidTag: GCM tag check failed`.
The header enjoys exactly the same protection as the payload despite travelling in clear.

The necessary contrast is with Stage 3. The envelope is cryptographically sound, and that
is precisely why a reading forged before it reaches the gateway is believed. GCM proves
the envelope was not altered in transit; it cannot prove the measurement was true.

## D.4 Alternatives considered and not chosen

Being fair about the alternatives matters, because three of the four would also work.

| Alternative | Would it work here? | Why not chosen |
|---|---|---|
| ChaCha20-Poly1305 | **Yes.** An equally sound AEAD, and usually faster where AES-NI is absent — which is exactly the constrained-device case this project is about | The problem statement names AES. On the measurement machine AES-NI is present, so the usual argument for ChaCha20 does not apply. A genuine alternative, excluded by the brief rather than on merit |
| AES-CCM | **Yes.** AEAD built from CTR and CBC-MAC, widely used in constrained environments | GCM is better supported in the chosen library and parallelises better. CCM would be the stronger choice on a small microcontroller, which is worth stating since that is the hardware the problem concerns |
| AES-CBC + HMAC | **Yes, if assembled correctly.** Encrypt-then-MAC with separate keys gives confidentiality and integrity | Two primitives, two keys and an ordering that is easy to get wrong. A single AEAD call removes a class of implementation error. Rejected on safety of construction, not on cryptographic grounds |
| TLS or DTLS | Yes for the uplink, no for the problem | It would solve the gateway-to-centre link well, and real deployments use it. But it presumes a session, a handshake, certificates and a PKI — and key distribution is explicitly out of scope (A.7). It also does nothing for the legacy link, which is the subject of the study |

The honest summary is that the uplink is the easy part and several options would secure
it. The project's subject is the half that none of them reaches.

## D.5 Cryptanalytic techniques

### D.5.1 Exhaustive key search with a recognition test

Where the key space is small, the attacker decrypts under every candidate key and needs a
test to recognise the right one. Here the test is structural: does the candidate parse as
a well-formed reading, with `D` at position 0, `V` at 3, `I` at 8, `F` at 13, `B` at 18,
`Q` at 20 and digits elsewhere? This is a **ciphertext-only** attack — no matching
plaintext is required, only knowledge of the public frame layout. In the prototype all 36
additive keys were tried in 0.2039 ms and exactly one candidate passed, recovering both
`k = 3` and the reading. Applicable to Caesar, Additive, Affine and Rail Fence.

### D.5.2 Known plaintext using the fixed field tags

Known plaintext is a different and stronger technique, and Affine shows why. The attacker
knows that specific plaintext characters sit at specific positions. Each known pair gives
one equation `c ≡ a·p + b (mod 36)`, and two pairs give a solvable system — *sometimes*.

Taking tags `D` (index 3) at position 0 and `I` (index 8) at position 8, and subtracting
to eliminate `b`:

```
c_I − c_D ≡ a·(8 − 3)  ≡ 5a   (mod 36)
gcd(5, 36) = 1, so 5 is invertible:  5⁻¹ ≡ 29 (mod 36)
a ≡ 29·(c_I − c_D) (mod 36),   then   b ≡ c_D − 3a (mod 36)
```

With the worked example (`a = 5, b = 8`, ciphertext `X43FEJ49M…`), the differences give
`a ≡ 29 × 25 ≡ 5` and `b ≡ 23 − 15 ≡ 8`, recovering the key uniquely.

**The failure case matters more.** Take instead `D` (3) at position 0 and `V` (21) at
position 3:

```
c_V − c_D ≡ a·(21 − 3) ≡ 18a (mod 36)
gcd(18, 36) = 18, so 18 is not invertible
```

Executed against the same ciphertext, this system is satisfied by **all twelve** valid
multipliers `{1, 5, 7, 11, 13, 17, 19, 23, 25, 29, 31, 35}`, and recovers nothing. The
cause is that 36 is composite: differences sharing a factor with 36 collapse the equation.
An attacker must choose tag pairs whose index difference is coprime to 36, and a student
who picks the pair carelessly concludes the cipher is strong when it is not. This is a
direct consequence of the 36-character alphabet chosen in D.1 and is worth demonstrating
rather than stating.

### D.5.3 Frequency analysis, and why it is weak here

Frequency analysis exploits the uneven letter distribution of natural language, and a
telemetry frame is not natural language: 27 characters, mostly digits close to uniform
within each field, with six fixed tags. A single frame therefore gives almost no
distributional signal. The technique is included because it is on the syllabus and
because the honest result — that it underperforms on short structured frames and needs
many frames accumulated under one key — is itself a finding (Q1), reported as measured
rather than quietly replaced by an easier method.

### D.5.4 Kasiski examination and the index of coincidence

Both recover the Vigenère key length `L`, after which the ciphertext splits into `L`
additive ciphers that fall to D.5.1. Kasiski takes the greatest common divisor of the
separations between repeated substrings; the index of coincidence measures how often two
characters drawn from the text coincide, which is higher for a monoalphabetic stream than
a polyalphabetic one. The caution of D.5.3 applies again — on short frames repeats are
scarce — so both will likely need many frames under one key. Whether the recurring fixed
tags supply enough structure is an experimental question (E1).

## D.6 Gateway validation techniques

These are not cryptographic. They exist because cryptography cannot solve V2: the gateway
can verify that a frame decrypted correctly, but not that the measurement was true.

| Check | What it catches | What it misses |
|---|---|---|
| Range | Values outside plausible limits — the gross edit to 290.1 V was rejected as "V=2901 outside plausible range [2000, 2600]" | **Any edit that stays inside the range.** The 231.1 V edit was accepted and sealed into a valid envelope |
| Rate of change | Implausible jumps between consecutive readings | Slow drift applied over many frames; and it risks rejecting genuine step changes at a breaker event (E6) |
| Sequence | Replayed or out-of-order frames, once the gateway tracks the device counter | A replay that also rewrites the sequence field, since the legacy frame carries no authentication |

The run log states the conclusion plainly: "Validation reduces the problem. It does not
remove it: an edit that stays inside plausible limits is still wrapped in a valid AES
envelope." These checks are compensating controls in the sense of NIST SP 800-82 Rev. 3,
which directs that where a legacy system cannot support a required control an alternative
should be considered [1]. They narrow the attack surface; they do not close it, and E6
measures what they cost in false alarms.

## D.7 Mapping of techniques to the project

| Algorithm / technique | Problem it addresses | V# | O# | E# |
|---|---|---|---|---|
| Caesar, Additive | Model the weakest legacy protection | V1 | O1, O3 | E1 |
| Affine | Model a fixed substitution with a larger key | V1 | O1, O3 | E1 |
| Playfair | Model digram-level protection | V1 | O1, O3 | E1 |
| Vigenère | Model polyalphabetic legacy protection | V1 | O1, O3 | E1 |
| Rail Fence | Model transposition without substitution | V1 | O1, O3 | E1 |
| AES-256-GCM | Provide confidentiality and integrity on the uplink | V5 | O1, O2 | E2, E3, E5 |
| 96-bit random nonce per message | Prevent catastrophic IV reuse [16] | V5 | O1 | argued from [16], no experiment |
| Associated data over the header | Authenticate sequence and timestamp while leaving them readable | V6 | O1, O2 | E4 |
| Exhaustive search + recognition | Break small key spaces from ciphertext alone | V1 | O3 | E1 |
| Known plaintext on fixed tags | Break Affine, Vigenère and Playfair using frame structure | V1 | O3 | E1 |
| Frequency analysis | Test whether substitution survives on short frames | V1 | O3 | E1 |
| Kasiski, index of coincidence | Recover Vigenère key length | V1 | O3 | E1 |
| Tamper, inject, replay on the legacy link | Demonstrate authenticated false data and replay | V2, V6 | O4 | E4 |
| ECB demonstration | Show that mode choice changes what leaks | V5 | O4 | E5 |
| Downgrade to passthrough | Show protection collapsing to the legacy level | V7 | O4 | E4 |
| Range, rate-of-change, sequence validation | Compensating control for V2 and V6 | V2, V6 | O5 | E4, E6 |

V3, V4 and V8 are properties of the architecture rather than of any algorithm, and are
addressed in A.5 and C.2.2.

## D.8 Honest limits of the chosen techniques

**The classical ciphers are a teaching stand-in.** Real legacy devices transmit plaintext
or proprietary encodings; they do not use Caesar or Vigenère. Every cipher-specific result
in this project is a statement about that cipher, not about field practice. The
unprotected case at the zero point of the scale is the one the literature describes [4].

**The attacks exploit a known frame layout.** Recognition tests and known-plaintext
recovery both depend on the format being public. For a published protocol this is a
reasonable assumption, but it should not be mistaken for a general result about the
ciphers on arbitrary data.

**Timings compare implementations, not algorithms.** The classical ciphers are pure
Python; AES runs in a compiled backend with AES-NI. That AES "outperforms" Caesar in the
measurements is an artefact of implementation, stated in the run log and repeated here.

**AES-GCM is used, not analysed.** The project takes GCM's security as given from [15]
and [16] and studies how it is deployed. No claim is made about AES itself, and
side-channel and fault attacks are out of scope (A.4.3).

**Deliberately excluded:** TLS and DTLS, PKI and key distribution, post-quantum
cryptography, and hardware security modules. Each is either out of scope by A.7 or
belongs to the key-management problem the project does not attempt to solve.

---

## References

Every item below was opened and read during preparation of this document. Full
verification notes are kept in `docs/references.md`.

[1] K. Stouffer, M. Pease, C. Tang, T. Zimmerman, V. Pillitteri, S. Lightman, A. Hahn,
S. Saravia, A. Sherule, and M. Thompson, *Guide to Operational Technology (OT)
Security*, NIST Special Publication 800-82 Rev. 3, National Institute of Standards and
Technology, September 2023. doi: 10.6028/NIST.SP.800-82r3.
https://csrc.nist.gov/pubs/sp/800/82/r3/final

[2] A. C-F. Chan and J. Zhou, "Toward Safe Integration of Legacy SCADA Systems in the
Smart Grid," arXiv:2107.05863. https://ar5iv.arxiv.org/html/2107.05863

[3] P. P. Tsang and S. W. Smith, "YASIR: A Low-Latency, High-Integrity Security Retrofit
for Legacy SCADA Systems," in *Proc. IFIP TC 11 23rd International Information Security
Conference*, IFIP International Federation for Information Processing, vol. 278, Boston:
Springer, 2008, pp. 445–459.
https://www.cs.dartmouth.edu/~sws/pubs/yasir-sec08.pdf

[4] S. Kaniewski, N. Lohmiller, M. Menth, and T. Heer, "Securing The Forgotten Link:
Selecting and Evaluating Compensating Security Measures for Legacy Device Integration
Paths," accepted for *Proc. International Conference on Availability, Reliability and
Security (ARES)*, Linköping, Sweden. Accepted manuscript.
https://atlas.cs.uni-tuebingen.de/~menth/papers/Menth26i.pdf

[5] Cybersecurity and Infrastructure Security Agency, *Cyber-Attack Against Ukrainian
Critical Infrastructure*, Alert IR-ALERT-H-16-056-01, updated 20 July 2021.
https://www.cisa.gov/news-events/ics-alerts/ir-alert-h-16-056-01

[6] International Electrotechnical Commission, *Power systems management and associated
information exchange — Data and communications security — Part 1: Communication network
and system security — Introduction to security issues*, IEC TS 62351-1:2007.
https://webstore.iec.ch/publication/6903

[7] IEEE, *IEEE Standard for Electric Power Systems Communications — Distributed Network
Protocol (DNP3)*, IEEE Std 1815-2012.
https://standards.ieee.org/ieee/1815/5414/

[8] IEEE Std 1711.1, *Standard for a Cryptographic Protocol for Cyber Security of
Substation Serial Links: Substation Serial Protection Protocol (SSPP)*, and IEEE Std
1711.2-2019, *Standard for Secure SCADA Communications Protocol (SSCP)*. Titles and
designations as listed in NIST SP 800-82 Rev. 3, Appendix D [1].

[9] R. V. Solomakhin, P. P. Tsang, and S. W. Smith, "Predictive YASIR: High Security
with Lower Latency in Legacy SCADA," book chapter, Dartmouth College.
https://cs.dartmouth.edu/~sws/pubs/sts10-draft.pdf

[10] U.S. Department of Energy, Office of Cybersecurity, Energy Security, and Emergency
Response, *Hallmark Cryptographic Serial Communication*, Cyber Security for Energy
Delivery Systems fact sheet. Project lead: Schweitzer Engineering Laboratories; partners:
Pacific Northwest National Laboratory, CenterPoint Energy Houston Electric.
https://www.energy.gov/documents/hallmark-cryptographic-serial-communication-schweitzer-engineering-laboratories

[11] W. Jackson, "Encryption device planned for legacy SCADA installations," *Washington
Technology*, January 2005.
https://washingtontechnology.com/2005/01/encryption-device-planned-for-legacy-scada-installations/328769

[12] H.-D. Nguyen, T.-T. Dai, H.-D. Le, T.-H. Huynh, and P.-C. Pham, "Embedding the
Real-Time AES-128 Encryption into Programmable Logic Controllers for Secure Modbus
TCP/IP Communications in Industrial Control Systems," *International Journal of
Integrated Engineering*, vol. 17, no. 9, pp. 45–57, 2025.
https://journal.uthm.edu.my/index.php/ijie/article/view/22589

[13] D. Bhamare, M. Zolanvari, A. Erbad, R. Jain, K. Khan, and N. Meskin, "Cybersecurity
for Industrial Control Systems: A Survey," arXiv:2002.04124, submitted 10 February 2020.
https://arxiv.org/abs/2002.04124

[14] DNP Users Group, *Overview of DNP3 Protocol* and *Features of DNP3*.
https://www.dnp.org/About/Overview-of-DNP3-Protocol

[15] National Institute of Standards and Technology, *Advanced Encryption Standard
(AES)*, FIPS 197, published 26 November 2001, updated 9 May 2023.
https://csrc.nist.gov/pubs/fips/197/final

[16] M. Dworkin, *Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode
(GCM) and GMAC*, NIST Special Publication 800-38D, November 2007.
https://csrc.nist.gov/pubs/sp/800/38/d/final

---

## TODO(team) — outstanding items after Step 3

| # | Item | Where |
|---|---|---|
| T1 | Confirm course code and instructor name | Title block |
| T3 | Add a direct citation to the Modbus specification. The published security-specification URL returns HTTP 404 and the index page is JavaScript-rendered; a member with access should retrieve it | A.1.4, B.9 |
| T4 | Decide on Stuxnet: cite with a verified source and stated relevance, or omit | A.6.1 |
| T6 | Confirm Python 3.11 is permitted by the course | Part C |
| T7 | Insert actual milestone dates and marks | B.7.4, Part C |
| T8 | IEEE 1711.1 and 1711.2 titles are cited via NIST SP 800-82r3; the IEEE pages are JavaScript-rendered and could not be read directly. Confirm from the standards themselves if the course requires primary citation | A.6.2, B.2.3, B.2.4, [8] |
| T9 | Reference [4] states its venue as ARES, Linköping, Sweden; the file name suggests a 2026 publication year. Confirm the final year and volume before submission | [4] |
| T10 | The University of Messina proxy paper returned HTTP 403 and is not cited. If a member can obtain it, add a proxy-based implementation to B.3 | B.3, B.9 |
| T11 | Reference [11] is a 2005 trade announcement of a product then in development. If the Datacryptor SCADA module's current status matters to the review, obtain a vendor datasheet | B.4.2 |
| T12 | DNP3 Secure Authentication's specific guarantees could not be confirmed from an openly readable source. Confirm from IEEE Std 1815 if a stronger claim is needed in B.5 | B.2.5, B.5 |
| T13 | Reference [9] is a draft PDF hosted by the author. Confirm the final published venue, volume and page numbers | [9] |
