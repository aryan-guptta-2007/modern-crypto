# Legacy Cipher Migration Framework for Industrial Control Systems (ICS)

Build plan and working brief for an AI coding agent.
Course: Cybersecurity / Modern Cryptography. Project topic no. 8.

---

## 0. How to use this file

You are an AI agent building this project for a student team. Read the whole file before writing anything.

Work in this order:

1. **Milestone 2 documents (Section 3 and 4).** Due tomorrow. This is the priority.
2. **Feasibility prototype (Section 5).** Small, working, end to end. It is evidence for the feasibility marks.
3. **Full system (Section 6 onwards).** Later milestones. Do not start this until 1 and 2 are complete.

Rules that apply to everything you produce:

| Rule | Detail |
|---|---|
| No invented sources | Every paper, standard, product or incident you cite must be opened and checked. If you cannot verify it, leave it out. Section 4.2 lists starting sources; verify each one before use. |
| No invented numbers | Costs, latencies and device counts must come from a cited source or from the team's own measurements. Mark estimates as estimates. |
| No novelty claims | The gateway idea already exists in industry. Present the project as a simulation and comparative study, not an invention. |
| Honest limits | State openly that classical ciphers are a teaching stand-in. Real legacy devices mostly send plaintext, not Caesar or Vigenère. |
| Plain writing | Short sentences, tables where content is comparable, no filler. Write as a student team would, in a natural academic voice. |
| Ask, do not guess | Items marked `TODO(team)` need input from the team. Leave the marker in place and list all of them at the end of your run. |

---

## 1. Problem statement (as given by the course)

> **8. Legacy Cipher Migration Framework for Industrial Control Systems (ICS)**
>
> **Cryptographic Concepts:** Monoalphabetic ciphers (Caesar, Affine, Additive), Polyalphabetic ciphers (Playfair, Vigenère), Advanced Encryption Standards (AES).
>
> **Smart Grid Application:** Construct a protocol-translation gateway that wraps legacy, unencrypted or classically encrypted telemetry data (simulating historical substitution/transposition ciphers) into modern AES-encrypted payloads, studying the transition vulnerabilities of upgrading legacy grid hardware.

### 1.1 What it means in plain words

Old grid devices send readings with no protection or very weak protection. They cannot all be replaced. A gateway placed next to the old device takes its data in and sends it onward under AES. The project builds a simulation of that gateway and studies what remains unsafe during the changeover.

```
Legacy device ──(weak "legacy link")──► GATEWAY ──(AES link)──► Control centre
 plaintext or classical cipher           decrypt, check,          decrypt, verify,
                                         re-encrypt               display
```

### 1.2 The three things the statement asks for

| # | Requirement | Where it is met |
|---|---|---|
| 1 | Implement the named classical ciphers and AES | `ciphers/`, `gateway/aes_envelope.py` |
| 2 | Construct the protocol-translation gateway | `gateway/` |
| 3 | Study the transition vulnerabilities | `attacks/`, `experiments/`, report |

---

## 2. Milestone 2 rubric

Milestone 2 is **Problem Analysis, 6 marks**, in two parts of 3 marks each.

| Band | Problem domain identification and analysis (3) | Review of existing systems and project feasibility (3) |
|---|---|---|
| Top | Clearly identified with in-depth analysis and strong justifications | Comprehensive review with clear feasibility analysis |
| Second | Clearly identified with adequate analysis | Adequate review and basic feasibility |
| Third | Identified but analysis is superficial | Limited review; weak feasibility |
| Bottom | Unclear or incorrectly identified | No meaningful review or feasibility |

### 2.1 What separates the top band from the second

| Top-band phrase | What the document must therefore contain |
|---|---|
| "Clearly identified" | One precise problem statement, a stated scope, and what is out of scope |
| "In-depth analysis" | Root causes, a threat model, and a breakdown of where exactly the system is weak |
| "Strong justifications" | Evidence for every major claim: a standard, a paper, or a documented incident |
| "Comprehensive review" | Standards, research and commercial products all covered, compared on the same criteria, ending in a gap statement |
| "Clear feasibility analysis" | Technical, economic, operational and schedule feasibility each assessed, plus risks, backed by a working prototype |

### 2.2 Milestone 2 deliverables

| File | Purpose |
|---|---|
| `docs/milestone2_problem_analysis.md` | Main document, Sections 3 and 4 of this README turned into full prose and tables |
| `docs/figures/` | Architecture diagram, threat model diagram, comparison chart |
| `prototype/` | Feasibility prototype from Section 5 |
| `docs/milestone2_summary.md` | One-page summary for presenting, mapped to the two rubric columns |

`TODO(team)`: confirm the required submission format (Word, PDF or slides) and page limit. Default is a Markdown document of about 6 to 8 pages that converts cleanly to Word or PDF.

---

## 3. Part A: Problem domain identification and analysis (3 marks)

Write this as Part A of `docs/milestone2_problem_analysis.md`. Use the sub-sections below as headings.

### 3.1 Domain background

Explain briefly, with a source for each point:

| Point to cover | Guidance |
|---|---|
| What an ICS / SCADA system is | Field devices (RTU, PLC, IED, meter), communication link, control centre |
| How a smart grid uses it | Telemetry upward (voltage, current, frequency, breaker state), commands downward |
| Why field devices are "legacy" | Service life of decades, limited processor and memory, designed for isolated networks |
| Which protocols they use | Modbus and DNP3 in their original forms carry no encryption or authentication |
| Why this became a problem | Grids are now connected to IP networks and remote access, so isolation no longer protects them |

### 3.2 Problem statement

Draft to refine, not to copy unchanged:

> Legacy field devices in power grids transmit telemetry without confidentiality, integrity or authenticity, and cannot be upgraded to run modern cryptography. Utilities therefore place a translation gateway between the legacy device and the network. This project examines how such a gateway can migrate weakly protected telemetry to AES, and which vulnerabilities persist or are introduced during that migration.

### 3.3 Root-cause analysis

Present as a table with one row per cause.

| Root cause | Effect | Why it cannot simply be fixed |
|---|---|---|
| Protocols designed without security | Data readable and modifiable in transit | Changing the protocol breaks compatibility with installed devices |
| Constrained hardware | Device cannot run AES or TLS | Replacement is costly and needs outages |
| Long replacement cycles | Old and new equipment coexist for years | Migration is gradual, so a mixed state is unavoidable |
| Weak or absent key management | Shared, static or hard-coded keys | Field sites are remote and rarely visited |

### 3.4 Mapping the course concepts to the problem

This table justifies why classical ciphers appear in a smart-grid project. Include it.

| Course concept | Role in this project | What it demonstrates |
|---|---|---|
| Caesar, Additive | Weakest legacy protection | Key space small enough to try every key |
| Affine | Slightly stronger monoalphabetic | Still a fixed substitution, broken by known plaintext |
| Playfair | Digram substitution | Hides single-letter frequencies, not digram patterns |
| Vigenère | Polyalphabetic | Broken once the key length is found |
| Transposition (Rail Fence) | Rearrangement only | Content unchanged, so character counts leak |
| AES | Modern target | Confidentiality, and with GCM also integrity |

### 3.5 Threat model

State the attacker, their position and their goal. Add a diagram to `docs/figures/threat_model.*`.

| Position | Attacker capability | Security property lost |
|---|---|---|
| Legacy link (device to gateway) | Read, alter, inject and replay frames | Confidentiality, integrity, authenticity |
| Inside the gateway | Sees plaintext between decrypt and re-encrypt; may read keys | All three, for every device behind it |
| AES link (gateway to control centre) | Read and replay ciphertext only | None, if GCM, sequence numbers and timestamps are used correctly |
| Configuration | Force a fallback to plaintext mode | Downgrade to the legacy level |

### 3.6 Transition vulnerabilities

This is the core of the "study" in the problem statement. Give each a short paragraph.

| # | Vulnerability | Explanation |
|---|---|---|
| V1 | Legacy link stays exposed | AES protects only the gateway-to-centre half |
| V2 | Authenticated false data | The gateway wraps tampered readings in valid AES, so the centre trusts them |
| V3 | Plaintext exposure in the gateway | Translation requires decrypting, so the gateway is a high-value target |
| V4 | Key management | Legacy keys and AES keys both sit on one device |
| V5 | Wrong AES mode | ECB reveals repeating telemetry; CBC without a MAC gives no integrity |
| V6 | Replay | Legacy frames carry no freshness information |
| V7 | Downgrade | A passthrough or fallback mode can be triggered or left enabled |
| V8 | Latency and availability | Added delay and a single point of failure in a real-time system |

### 3.7 Justification

Support the importance of the problem with:

| Type of evidence | Examples to verify and cite |
|---|---|
| Documented incidents | 2015 Ukraine power grid attack; Stuxnet (2010) |
| Standards that exist because of this problem | IEC 62351; IEEE 1711; NIST SP 800-82; DNP3 Secure Authentication; Modbus/TCP Security |
| Research stating the gap | The legacy-link paper in Section 4.2 |

`TODO(team)`: if the course expects an Indian context, add one verified paragraph on smart-meter rollout or grid modernisation in India.

### 3.8 Objectives, scope and assumptions

| Item | Content |
|---|---|
| Objectives | (1) Implement the classical ciphers and AES. (2) Build the gateway. (3) Demonstrate attacks on the legacy side. (4) Demonstrate and measure the transition vulnerabilities. (5) Evaluate gateway-side mitigations. |
| In scope | Software simulation, telemetry direction only, one gateway, several simulated devices |
| Out of scope | Real hardware, real Modbus or DNP3 framing, control commands, key distribution infrastructure, post-quantum cryptography |
| Assumptions | Gateway is physically near the device; AES key is provisioned securely beforehand; clocks are roughly synchronised |

---

## 4. Part B: Review of existing systems and project feasibility (3 marks)

Write this as Part B of the same document.

### 4.1 Review structure

Cover three categories, then compare, then state the gap.

| Category | What to review |
|---|---|
| Standards | IEC 62351, IEEE 1711, DNP3 Secure Authentication, Modbus/TCP Security, NIST SP 800-82 |
| Research | Bump-in-the-wire retrofits, proxy-based approaches, in-device AES, legacy-link studies |
| Commercial products | Serial encryptors and secure protocol gateways |

### 4.2 Starting sources (verify each before citing)

| Work | Type | Relevance | Link |
|---|---|---|---|
| YASIR: A Low-Latency, High-Integrity Security Retrofit for Legacy SCADA Systems (Dartmouth, 2008) | Research | Early bump-in-the-wire design; latency as the main constraint | https://www.cs.dartmouth.edu/~sws/pubs/yasir-sec08.pdf |
| Predictive YASIR | Research | Reducing retrofit latency on Modbus/ASCII | https://cs.dartmouth.edu/~sws/pubs/sts10-draft.pdf |
| Hallmark Project and SEL-3025 link module (US Dept. of Energy, SEL, PNNL) | Government and commercial | Protocol-independent secure SCADA protocol in a bump-in-the-wire module | https://www.energy.gov/documents/hallmark-cryptographic-serial-communication-schweitzer-engineering-laboratories |
| Thales Datacryptor SCADA module | Commercial | AES encryptor box for Modbus and DNP3 | https://washingtontechnology.com/2005/01/encryption-device-planned-for-legacy-scada-installations/328769 |
| Toward Safe Integration of Legacy SCADA Systems in the Smart Grid (Chan) | Survey | Compares protection strategies; reviews the field | https://ar5iv.arxiv.org/html/2107.05863 |
| Securing Modbus in legacy ICS using proxies (Univ. of Messina) | Research | Proxies doing cryptography for legacy devices | https://iris.unime.it/handle/11570/3339492 |
| Embedding Real-Time AES-128 into PLCs for Secure Modbus TCP/IP | Research | Measured AES latency on real PLCs | https://journal.uthm.edu.my/index.php/ijie/article/view/22589 |
| Evaluating Compensating Security Measures for Legacy Device Integration Paths (Univ. of Tübingen) | Research | Directly addresses the unprotected legacy link | https://atlas.cs.uni-tuebingen.de/~menth/papers/Menth26i.pdf |

Add at least two more verified sources of your own, preferably one standard document and one recent survey.

### 4.3 Comparison table to produce

One row per reviewed system, same columns for all.

| Column | Meaning |
|---|---|
| Approach | Bump-in-the-wire, proxy, in-device, protocol extension |
| Legacy device modified? | Yes or no |
| Confidentiality | Provided or not |
| Integrity and authentication | Provided or not |
| Replay protection | Provided or not |
| Legacy link protected? | Usually no; record what each says |
| Reported latency | Figure from the source, or "not reported" |
| Limitation | As stated by the authors or evident from the design |

Add a final row for **this project** so the reader sees where it sits.

### 4.4 Gap statement

Conclude the review with a short, honest paragraph on these lines:

| Finding from the review | Position of this project |
|---|---|
| Gateway-based retrofit is established and commercially available | Reproduced in simulation, not claimed as new |
| Existing work assumes plaintext legacy protocols | This project adds classical ciphers as a graded scale of "weak legacy protection" for teaching and comparison |
| The legacy link is acknowledged as the remaining weakness | This project demonstrates it with working attacks and tests simple gateway-side checks |

### 4.5 Feasibility analysis

Give each dimension its own short sub-section and a verdict.

| Dimension | Points to make | Evidence |
|---|---|---|
| Technical | All ciphers are well documented; AES is available in a maintained library; three processes over local sockets are enough | Working prototype (Section 5) |
| Economic | Free software, no hardware purchase, runs on student laptops | Tool list in Section 6.1 |
| Operational | One command to run; output readable by a non-specialist; clear demo flow | Prototype run log |
| Schedule | Work fits the remaining milestones | Timeline in Section 10 |
| Legal and ethical | Fully simulated on localhost; no real grid equipment or networks touched | Statement in the document |

### 4.6 Risk table

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Classical ciphers do not handle numeric telemetry | High | High | 36-character alphabet, fixed in Section 6.3 |
| Playfair padding corrupts readings | Medium | High | Reserved filler character, Section 6.4 |
| AES misuse (nonce reuse, wrong mode) | Medium | High | GCM only, random 96-bit nonce per message, library primitives |
| Frequency analysis weak on short structured messages | Medium | Medium | Use known-plaintext attacks on the fixed field letters as the main method |
| Scope creep | Medium | Medium | Out-of-scope list in Section 3.8 |
| Demo fails on another machine | Low | High | Pinned dependencies, single run script, recorded backup run |

---

## 5. Feasibility prototype (build for Milestone 2)

A deliberately small version that proves the pipeline works. Target: under 300 lines, one file acceptable.

| Requirement | Detail |
|---|---|
| Ciphers | Caesar and Vigenère only |
| Flow | Generate one reading, encrypt with the legacy cipher, gateway decrypts, re-encrypts with AES-256-GCM, control centre decrypts and prints |
| One attack | Brute-force the Caesar ciphertext and print the recovered reading |
| One vulnerability | Alter a digit on the legacy side and show the control centre accepting it |
| Output | Clear console log of every stage, plus per-stage timing in milliseconds |
| Run | `python prototype/demo.py` with no arguments |

Save the console output to `docs/prototype_run.txt` and quote it in the feasibility section.

---

## 6. Full system specification (later milestones)

### 6.1 Technology

| Need | Choice |
|---|---|
| Language | Python 3.11 or newer |
| Classical ciphers | Written from scratch, no cipher libraries |
| AES | `cryptography` library, AES-256-GCM |
| Communication | Standard `socket` module, TCP on localhost |
| Tests | `pytest` |
| Charts | `matplotlib` |
| Dashboard (optional, last) | Streamlit |

`TODO(team)`: confirm Python is permitted by the course.

### 6.2 Repository layout

```
legacy-cipher-migration/
├── README.md
├── requirements.txt
├── run_demo.py                 # starts everything, runs the scenario list
├── ciphers/
│   ├── alphabet.py             # 36-character alphabet helpers
│   ├── caesar.py
│   ├── additive.py
│   ├── affine.py
│   ├── playfair.py
│   ├── vigenere.py
│   └── railfence.py
├── telemetry/
│   ├── reading.py              # format and parse readings
│   └── device_sim.py           # simulated legacy device
├── gateway/
│   ├── profiles.py             # per-device cipher and key
│   ├── validator.py            # range, rate-of-change, sequence checks
│   ├── aes_envelope.py         # AES-GCM pack and unpack
│   └── gateway.py
├── control_centre/
│   └── centre.py
├── attacks/
│   ├── brute_force.py
│   ├── known_plaintext.py
│   ├── frequency.py
│   ├── kasiski.py
│   ├── mitm_proxy.py           # tamper, inject, replay on the legacy link
│   └── ecb_demo.py
├── experiments/
│   ├── timing.py
│   ├── break_time.py
│   ├── detection_rate.py
│   └── results/
├── tests/
├── prototype/
│   └── demo.py
└── docs/
```

### 6.3 Alphabet

All classical ciphers use one 36-character alphabet: `A–Z` then `0–9`, indexed 0 to 35. Arithmetic is modulo 36.

| Cipher | Key | Key space | Note |
|---|---|---|---|
| Caesar | Fixed shift of 3 | 1 | Special case of Additive |
| Additive | Shift k | 36 | |
| Affine | (a, b), a coprime to 36 | 12 × 36 = 432 | Valid a: 1, 5, 7, 11, 13, 17, 19, 23, 25, 29, 31, 35 |
| Playfair | Keyword | Large | 6 × 6 grid holds all 36 characters, so no I/J merging |
| Vigenère | Keyword | 36^length | |
| Rail Fence | Number of rails | Small | Transposition |

### 6.4 Telemetry format

Fixed-width, no spaces, letters as field tags.

```
D07V2301I0152F4998B1Q000123
```

| Tag | Field | Width | Meaning |
|---|---|---|---|
| D | Device ID | 2 | |
| V | Voltage | 4 | Tenths of a volt (2301 = 230.1 V) |
| I | Current | 4 | Tenths of an ampere |
| F | Frequency | 4 | Hundredths of a hertz (4998 = 49.98 Hz) |
| B | Breaker | 1 | 0 open, 1 closed |
| Q | Sequence | 6 | Device counter |

The letter `X` is reserved as the Playfair filler and never appears in a reading. The parser strips `X` after Playfair decryption.

### 6.5 Gateway behaviour

| Step | Action |
|---|---|
| 1 | Receive a frame from a legacy device |
| 2 | Look up the device profile (cipher, key); reject unknown devices |
| 3 | Decrypt with the legacy cipher |
| 4 | Parse; reject malformed readings |
| 5 | Validate: plausible ranges, rate-of-change limit, sequence increasing |
| 6 | Build the AES envelope and send |
| 7 | Log every decision with a reason |

Validation must be switchable on and off, so experiments can compare both states.

### 6.6 AES envelope

| Field | Content |
|---|---|
| version | 1 byte |
| gateway_id | 2 bytes |
| gateway_seq | 8 bytes, increasing |
| timestamp | 8 bytes, milliseconds |
| nonce | 12 bytes, random per message |
| ciphertext + tag | AES-256-GCM output |

Header fields before the nonce are passed as associated data so they are authenticated. The key is loaded from a file or environment variable, never written in source code. The control centre rejects a bad tag, a repeated or lower sequence number, and a timestamp outside a 30-second window.

### 6.7 Attacks to implement

| Attack | Target | Shows |
|---|---|---|
| Brute force | Caesar, Additive, Affine, Rail Fence | Key spaces of 1 to 432 fall instantly |
| Known plaintext | Affine, Vigenère, Playfair | Fixed field tags at known positions reveal the key |
| Frequency analysis | Monoalphabetic ciphers | Character distribution survives substitution |
| Kasiski and index of coincidence | Vigenère | Key length recovery |
| Tamper, inject, replay | Legacy link | V1, V2, V6 |
| ECB pattern demo | AES-ECB against AES-GCM | V5 |
| Downgrade | Gateway passthrough mode | V7 |

### 6.8 Experiments

| Experiment | Measurement | Output |
|---|---|---|
| Break time | Time to recover the key for each classical cipher | Bar chart |
| Latency | Time per stage: legacy decrypt, validate, AES encrypt, AES decrypt | Table and chart |
| Overhead | Payload size before and after wrapping | Table |
| Detection rate | Share of tampered and replayed frames caught, validation off against on | Table |
| False alarms | Legitimate readings rejected by validation | Table |

Each experiment writes a CSV and a PNG to `experiments/results/`.

---

## 7. Testing

| Test | Requirement |
|---|---|
| Round trip | Decrypt(Encrypt(m)) equals m for every cipher, including edge cases |
| Affine keys | Invalid `a` values are rejected |
| Playfair | Doubled characters and odd lengths handled; filler removed correctly |
| AES envelope | Altered ciphertext, header or tag is rejected |
| Replay | Second copy of an envelope is rejected |
| End to end | A reading sent by the device appears unchanged at the control centre |

---

## 8. Demo script

`run_demo.py` runs these scenarios in order and prints a labelled log.

| # | Scenario | Expected result |
|---|---|---|
| 1 | Normal operation with each cipher | Readings arrive correctly |
| 2 | Eavesdropper on the legacy link | Classical ciphers broken, key shown |
| 3 | Eavesdropper on the AES link | Nothing recovered |
| 4 | Tampering on the legacy link, validation off | False reading accepted by the centre |
| 5 | Same attack, validation on | Out-of-range and sudden changes rejected; small changes still pass |
| 6 | Replay on both links | Legacy replay passes without sequence checks; AES replay rejected |
| 7 | ECB against GCM | Repeating blocks visible in ECB only |

Scenario 5 must show that validation reduces the problem and does not remove it.

---

## 9. Acceptance checklist for Milestone 2

Before finishing, confirm each line.

| Check | Done |
|---|---|
| Problem statement is one clear paragraph with scope and exclusions | ☐ |
| Root causes, threat model and eight transition vulnerabilities are all present | ☐ |
| Every major claim has a verified source | ☐ |
| Review covers standards, research and products | ☐ |
| Comparison table uses identical columns for every system and includes this project | ☐ |
| Gap statement makes no novelty claim | ☐ |
| Five feasibility dimensions each have a verdict | ☐ |
| Risk table is included | ☐ |
| Prototype runs with one command and its output is quoted in the document | ☐ |
| One-page summary maps content to the two rubric columns | ☐ |
| All `TODO(team)` items are listed at the end of the run | ☐ |

---

## 10. Timeline

| Stage | Content |
|---|---|
| Milestone 2 (tomorrow) | Sections 3, 4 and 5 |
| Next | Full cipher set, telemetry simulator, gateway, control centre |
| After that | Attacks and experiments |
| Final | Report, charts, demo rehearsal, optional dashboard |

`TODO(team)`: insert the actual milestone dates and marks.

---

## 11. Team details

| Item | Value |
|---|---|
| Team members | `TODO(team)` |
| Course and code | `TODO(team)` |
| Instructor | `TODO(team)` |
| Submission format | `TODO(team)` |
