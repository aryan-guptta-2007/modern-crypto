# Legacy Cipher Migration Framework for Industrial Control Systems

A simulation and comparative study of a protocol-translation gateway that wraps weakly
protected legacy telemetry into modern AES-encrypted payloads, and a study of the
vulnerabilities that persist or appear during that migration.

Coursework project (Cybersecurity / Modern Cryptography, CSET357) — Milestone 2, Problem
Analysis.

> **This is not a new idea, and the project does not claim it is.** Gateway-based retrofit for
> legacy SCADA is established practice: it is standardised as IEEE Std 1711.2 and sold as
> commercial hardware. What this project contributes is evidence — a reproducible simulation in
> which the residual vulnerabilities can be exercised, measured and shown, with an honest
> account of what the mitigations do not catch.

## The problem in one picture

```
Legacy device ──(weak "legacy link")──► GATEWAY ──(AES-256-GCM)──► Control centre
 plaintext or classical cipher          decrypt, validate,         verify tag, sequence,
                                        re-encrypt                 timestamp
```

Old grid devices send readings with no protection or very weak protection, and a large
installed base cannot be upgraded. A gateway placed beside the device takes that data in and
sends it onward under AES. The gateway moves the trust boundary rather than removing it, and
the segment between the device and the gateway stays exposed.

**The central finding:** the gateway authenticates the *channel*. It cannot authenticate the
*measurement*. A reading forged on the legacy link arrives at the control centre inside a
cryptographically valid AES envelope and is believed.

## Feasibility prototype

```bash
python prototype/demo.py
```

No arguments. Requires Python 3.11+ and `cryptography` (see `requirements.txt`). The AES key is
read from `AES_KEY_HEX` or generated per run — never hard-coded.

The run demonstrates, end to end:

| Stage | What it shows |
|---|---|
| 1 | Normal operation — Caesar and Vigenère frames arrive byte-identical at the control centre |
| 2 | **V1** — ciphertext-only exhaustive key search with a plaintext-recognition test recovers the key and reading in ~0.2 ms |
| 3 | **V2** — a forged reading is delivered under a valid GCM tag; validation catches a gross edit but *not* a small in-range one |
| 4 | Envelope integrity — one flipped bit in the ciphertext, and one in the authenticated header, are both rejected with `InvalidTag` |
| 5 | **V6** — an AES envelope replay is rejected on its sequence number; a legacy frame replay is accepted |
| 6 | Per-stage cost, mean of 2000 runs |

A saved run is in [`docs/prototype_run.txt`](docs/prototype_run.txt).

## Documents

| File | Contents |
|---|---|
| [`docs/project_proposal.pdf`](docs/project_proposal.pdf) | The submission document, 19 pages, figures embedded |
| [`docs/project_proposal.md`](docs/project_proposal.md) | Source of the above — Parts A to D, one per evaluation criterion |
| [`docs/project_proposal_full.md`](docs/project_proposal_full.md) | Full report with the complete review and extended justification |
| [`docs/references.md`](docs/references.md) | Every source with its link, type and a verification record |
| [`docs/presentation_summary.md`](docs/presentation_summary.md) | Talking points per criterion, with the figure or table to show |
| [`docs/viva_questions.md`](docs/viva_questions.md) | 25 likely examiner questions with short answers |
| [`docs/figures/`](docs/figures/) | Threat model, architecture and methodology diagrams (SVG) |
| `README_to snd.md` | The original project brief |

## Sourcing policy

Every source cited was opened and read during preparation; nothing is cited from memory or from
a title alone, with one declared exception recorded in `docs/references.md`. Sources that could
not be retrieved were dropped rather than cited, and the resulting gaps are listed under
"Open items and limitations" in the proposal.

## Honest limits

- **The classical ciphers are a teaching stand-in.** Real legacy devices transmit plaintext or
  proprietary encodings; they do not use Caesar, Affine, Playfair, Vigenère or Rail Fence. They
  are used here as a graded scale of weak protection, and the unprotected case is the one the
  literature actually describes.
- **Timings compare implementations, not algorithms.** The classical ciphers are pure Python
  while AES runs in a compiled backend with AES-NI, so AES appearing "faster" than Caesar is an
  artefact of implementation.
- **Measurements are from one laptop**, single process, no network. They are not a prediction of
  latency on real gateway hardware.
- **Entirely simulated.** No real grid equipment, utility network or vendor product is touched.
  All attacks run only against this project's own components.

## Status

Milestone 2 complete: proposal, feasibility prototype, run log and figures. The full system —
remaining ciphers, three-process split, the attack suite and the measurement experiments — is
specified in Part C of the proposal and not yet built.

## Team

Aryan Gupta · Yug Chaturvedi · Yuvraj Pathak
