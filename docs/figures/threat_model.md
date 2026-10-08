# Figure A.1 — Threat model

Text description of `threat_model.svg`, for accessibility and for any conversion step
that drops the image.

## What the figure shows

A single telemetry path runs left to right in three components:

`Legacy device (RTU / PLC / IED / meter, cannot run AES)` → **legacy link** →
`GATEWAY (decrypt legacy, validate, re-encrypt AES)` → **AES link** →
`Control centre (verify tag, sequence and timestamp, display reading)`

The path is divided into two zones by the gateway:

| Zone | Extent | Properties |
|---|---|---|
| Unprotected | Legacy device up to the gateway | No confidentiality, no integrity, no source authentication. Carries plaintext or a classical cipher |
| Protected | Gateway to control centre | AES-256-GCM with a sequence number and a timestamp |

The gateway sits on the boundary and belongs to both zones, which is the point of the
figure: deploying it creates two trust boundaries where there was previously one.

## Attacker positions

| Position | Where | Capability | Security property lost | Vulnerabilities |
|---|---|---|---|---|
| P1 | On the legacy link | Read, alter, inject and replay frames | Confidentiality, integrity, source authentication | V1, V2, V6 |
| P2 | Inside the gateway | Observes plaintext between decryption and re-encryption; may read either key set | All properties, for every device behind that gateway | V3, V4 |
| P3 | On the AES link | Read and replay ciphertext only | None, provided GCM, sequence numbers and timestamps are used correctly | Resists V5, V6 |
| P4 | Configuration and management interface | Enable a passthrough or fallback mode | Protection drops to the legacy level | V7 |

P1, P2 and P4 are drawn in red as positions where protection fails. P3 is drawn in
green because a correctly configured AES link denies the attacker anything useful.

## Central finding

The figure carries one conclusion in a separate panel:

> The gateway authenticates the channel. It cannot authenticate the measurement. A frame
> forged at P1 arrives at the control centre under a valid AES tag and is believed.

This is vulnerability V2, and it is the finding that distinguishes this project from a
straightforward "add encryption" exercise. The cryptography on the protected half
performs exactly as specified while the data it protects is false.

## Explicitly out of scope

AES side-channel and fault attacks; compromise of the control centre itself; supply
chain attacks on gateway firmware; denial of service by physical destruction of plant;
and the stolen-credential remote-access route that characterised the 2015 Ukraine
incident.
