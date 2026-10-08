# Presentation summary

One section per evaluation criterion, 3 marks each. Each section is about two minutes.
Figures are in `docs/figures/`; tables are in `docs/project_proposal.md`.

**Opening line for the whole talk:** *"Old grid devices send readings that anyone on the wire
can read and change, and they cannot be upgraded. The industry answer is a gateway that
re-encrypts under AES. We simulated that gateway to find out what it still does not fix."*

---

## Criterion 1 — Problem domain identification and analysis

**Show: `docs/figures/threat_model.svg` (Figure A.1)**

1. **The setting.** Electricity distribution runs on SCADA: field devices measure voltage,
   current, frequency and breaker state, and the control centre polls them every 5 to 60
   seconds [1]. We model the telemetry direction only.

2. **Why the devices cannot be fixed.** Three documented causes: an operational technology
   lifespan that "can exceed 20 years" [1]; devices that "lack desired features, including
   encryption capabilities" [1]; and re-certification cost that makes even possible retrofits
   impractical [4]. Replacement is a decades-long process [2].

3. **What changed.** These systems were designed for isolation. As they adopted IT
   connectivity, the result "provides significantly less isolation for OT from the outside
   world than predecessor systems" [1]. *The problem is a change in environment, not bad
   original engineering.*

4. **The threat model — point at the figure.** The gateway creates two trust boundaries where
   there was one. P1 legacy link: read, alter, inject, replay. P2 inside the gateway: plaintext
   and both key sets. P3 AES link: nothing gained if GCM is used correctly. P4 configuration:
   force a downgrade.

5. **The eight transition vulnerabilities**, V1 to V8. Three are already demonstrated in our
   prototype, not just claimed: V1 legacy link exposed, V2 authenticated false data, V6 replay.

6. **The line to land.** *"The gateway authenticates the channel. It cannot authenticate the
   measurement."* That is V2, and it is the finding the whole project turns on.

**If asked to go deeper:** root-cause table R1–R5 in A.3.

---

## Criterion 2 — Review of existing systems and project feasibility

**Show: the comparison table, B.2 (the final row is this project)**

1. **We reviewed eleven systems in three categories** — standards, research, commercial — on
   identical criteria. Every source was opened and read; two we could not open were dropped
   rather than cited, and we say which (B.6).

2. **The architecture is not ours.** It is standardised as IEEE 1711.2 and sold as the
   SEL-3025 bump-in-the-wire link module, which "adds only minimal latency" and means "a
   forklift upgrade of all equipment is unnecessary" [10]. We claim no novelty.

3. **Two findings that reshaped our understanding.** IEC 62351's scope *excludes Modbus* — it
   targets IEC TC 57 protocols [6] — so a Modbus utility cannot simply adopt it. And in-device
   AES works well (41.08 µs on real PLCs [12]) but needs a PLC capable of running AES, which
   is exactly what the problem devices are not.

4. **The gap, stated honestly.** Every gateway design protects the link *beyond* the module.
   Kaniewski et al. name the remaining segment the legacy link and state it "remains vulnerable
   and unaddressed" [4]. That is what we study.

5. **Feasibility: five verdicts, all feasible.** Technical rests on a working prototype: the
   gateway path measures 10.69 µs on a laptop, about three orders of magnitude below the 10 ms
   latency YASIR cites [3]. *Say it carefully* — that suggests cryptography is unlikely to be
   the bottleneck, but it is not a prediction for real gateway hardware, where transmission
   dominates. Economic: zero cost. Operational: one command. Schedule: extends working code.
   Legal: entirely simulated.

6. **Risk register** K1–K7, with the two real ones: AES misuse (answered by GCM-only and a
   fresh nonce) and demo failure on another machine (pinned versions, recorded backup run).

**If asked to go deeper:** YASIR's latency arithmetic — at 9600 baud, two modules buffering a
20-byte message add 40 ms from buffering alone [3].

---

## Criterion 3 — Objectives and methodology

**Show: `docs/figures/methodology.svg` (Figure C.2), then `docs/figures/architecture.svg`
(Figure C.1)**

1. **Aim in one sentence.** Build a reproducible simulation of a legacy-to-AES gateway and
   measure which weaknesses persist and which are introduced during partial migration.

2. **Five objectives, O1–O5**, each with a success criterion that can be checked, not asserted.
   O1 implement the ciphers and AES; O2 build the gateway; O3 attack the legacy link; O4
   demonstrate V1–V8; O5 evaluate mitigations and state their limits.

3. **We deliberately set no performance target.** Any number would be invented, and it would
   presuppose the answer. The only timing references are external: 10 ms for IED protection
   messages, 0.2 s for a poll response [3].

4. **Five phases with a verification gate** — point at the figure. A phase is not complete
   until its check passes, and a failed check sends the phase back, not forward. Phases 1 and 2
   are already partly discharged by the prototype.

5. **The core of the design is one controlled comparison.** The same attacks against the same
   system, twice, differing only in whether the gateway validator is on. That isolates the
   effect of the mitigation.

6. **E6 exists to keep us honest.** A validator catches more attacks simply by tightening its
   limits, at the cost of rejecting genuine readings — and a breaker event produces exactly the
   step change a rate-of-change check suppresses. So we measure false alarms alongside
   detection.

**If asked to go deeper:** the traceability table C.2.1 maps every objective to a
vulnerability, a module, an experiment and a metric.

---

## Criterion 4 — Relevance of algorithms and techniques

**Show: the cipher comparison table D.2, then the worked example D.2.1**

1. **Why classical ciphers at all.** They give a *graded* scale of weak protection that a
   single plaintext case cannot — from a key space of 1 up to polyalphabetic. We state plainly
   that real devices do not use them; the literature describes the real legacy link as
   unprotected [4], which is the zero point of our scale.

2. **Read down the key-space column.** 1, 36, 432, then `36!` for Playfair which is illusory
   because a keyword grid occupies a tiny part of that space, then `36ᴸ`, then about 25 for
   Rail Fence. *Every value is either tiny or illusory. These are not defences; they are a
   measuring stick for how fast a defence fails.*

3. **The worked example is real output, not hand calculation** — Caesar and Vigenère match our
   run log byte for byte. Two things only visible by running it: Playfair output is 28
   characters because a doubled `00` forces a filler *inside* the frame, and Rail Fence output
   contains exactly the plaintext characters reordered.

4. **Why AES-256-GCM, not just AES.** GCM is "authenticated encryption with associated data"
   [16]. ECB leaks repeating structure and telemetry is repetitive; CBC and CTR give no
   integrity alone. The header is authenticated as associated data so the centre can read the
   sequence number to reject replays *before* decrypting, yet be certain it was not altered.

5. **Nonce discipline is not optional.** NIST states a breach of IV uniqueness "may compromise
   the security assurance almost entirely", and if even one IV repeats under a key the
   implementation "may be vulnerable to the forgery attacks" [16]. Hence a fresh random 96-bit
   nonce per message, never a counter a restart could reset.

6. **The techniques have limits we report.** Frequency analysis is weak on a 27-character
   numeric frame; Affine known-plaintext recovery *fails* for tag pairs whose index difference
   shares a factor with 36. We treat both as findings, not obstacles to route around.

**If asked to go deeper:** the D.6 mapping table ties every algorithm to a vulnerability, an
objective and an experiment.

---

## Closing (30 seconds)

> *"Our prototype already shows the uncomfortable result. With validation off, a forged reading
> of 290 volts arrives at the control centre under a perfectly valid AES tag. With validation
> on, that one is caught — but a smaller edit to 231 volts still gets through. Validation
> reduces the problem. It does not remove it. That is what we set out to measure, and that is
> what the full system will quantify."*
