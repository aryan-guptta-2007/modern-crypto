# Viva questions and answers

25 likely examiner questions with short answers. Section references point to
`docs/project_proposal.md`; deeper detail is in `docs/project_proposal_full.md`.

---

## Scope and framing

**Q1. Why are classical ciphers in a smart-grid project at all? Real devices do not use
Caesar.**
Correct, and we say so explicitly in A.6. Real legacy devices transmit plaintext or
proprietary encodings. We use the classical ciphers as a deliberate teaching device: they give
a *graded* scale of weak protection, from a key space of one up to polyalphabetic, against
which the course's attack techniques can be demonstrated and timed. The unprotected case that
the literature actually describes [4] is the zero point of that same scale.

**Q2. Why not just replace the legacy devices?**
Three documented reasons. Operational technology lifespan "can exceed 20 years" [1], so the
installed base is enormous and long-lived. Replacement is capital-intensive and needs planned
outages, with phase-out taking decades [2]. And even where it is technically possible,
re-certification cost makes it impractical [4]. That is precisely why gateways exist.

**Q3. What is actually new here, if gateways already exist?**
Nothing about the architecture, and we state that in the gap statement (B.3). It is
standardised as IEEE 1711.2 and sold as the SEL-3025 [8], [10]. Our contribution is evidence,
not mechanism: a reproducible simulation in which the residual vulnerabilities can be
exercised and measured, with an honest account of what the mitigations miss.

**Q4. How does this differ from the SEL-3025 or IEEE 1711.2?**
Those are the real thing; ours is a simulation of the same idea, so we can instrument it. Two
substantive differences. SSCP makes authentication primary and encryption *optional* [10],
whereas we always encrypt with AES-256-GCM. And we deliberately study the segment the SEL-3025
does not cover — the link between the legacy device and the module — which is the subject of
the project rather than a gap in their product.

**Q5. Why only telemetry, and not control commands?**
Scope control (A.6). Commands going downward raise a different and larger problem — command
authentication and authorisation — which would roughly double the system and the attack
surface. We would rather measure one direction properly than describe two superficially.

---

## The central finding

**Q6. What can the gateway not fix?**
V2, authenticated false data. The legacy protocol has no source authentication [2], so the
gateway cannot tell a genuine frame from a forged one; it faithfully re-encrypts whatever it
receives. The control centre then sees a correctly authenticated message containing a false
reading. **The gateway authenticates the channel, not the measurement.**

**Q7. Can you prove that, or is it an argument?**
It is demonstrated. In Stage 3 of our prototype, with validation off, an edit on the legacy
link delivered `290.1 V` to the control centre when the true value was `230.1 V`, and the log
records "GCM tag verified, yet the voltage is false". The cryptography worked perfectly; the
data was false.

**Q8. So does your validator solve it?**
No, and we report that. With validation on, the gross edit to 290.1 V was rejected as "V=2901
outside plausible range [2000, 2600]", but a smaller edit to 231.1 V was still accepted. The
run log's own conclusion is "Validation reduces the problem. It does not remove it." A
plausible-looking lie still passes.

**Q9. Why can the gateway's sequence check not stop forged frames?**
Because the sequence number travels inside the legacy frame, which has no authentication. An
attacker who can edit the voltage field can edit the sequence field in the same way. The
sequence check catches *naive* replay — re-sending an identical captured frame — but not an
attacker who increments the counter. Freshness without authentication is not a defence.

**Q10. If AES cannot stop this, what would?**
Authentication at the device, which is the one thing the device cannot do — that is the whole
problem. Realistically: compensating controls, which is how NIST frames it [1]. Physical
protection of the legacy link, plausibility and rate-of-change checks, and cross-validation
against other measurements. Kaniewski et al. analyse exactly this space [4].

---

## Cryptographic choices

**Q11. Why GCM rather than ECB or CBC?**
ECB is unusable here: identical plaintext blocks give identical ciphertext, and telemetry is
highly repetitive, so patterns leak directly. CBC gives confidentiality but *no integrity on
its own*, so an altered envelope would not be detected. GCM is authenticated encryption with
associated data [16] — one primitive giving both, with a tag covering payload and header.

**Q12. What happens if a nonce repeats?**
It is catastrophic, and NIST says so directly. SP 800-38D states that breaching IV uniqueness
"may compromise the security assurance almost entirely" and that GCM "should not be deployed
unless compliance with this uniqueness requirement is ensured"; if even one IV repeats under a
given key, the implementation "may be vulnerable to the forgery attacks" [16]. That is why we
draw a fresh random 96-bit nonce per message rather than a counter that a gateway restart
could reset.

**Q13. Why 96 bits for the nonce?**
SP 800-38D recommends restricting IV support to 96 bits "to promote interoperability,
efficiency, and simplicity of design" [16]. It is also the length GCM uses directly without
additional derivation, which removes a step where implementations differ.

**Q14. Why AES-256 rather than AES-128?**
Because the cost is not measurable in our setting: seal 3.15 µs and open 3.08 µs, against a
pure-Python Caesar decrypt at 3.97 µs. Where the stronger option costs nothing measurable,
taking it is the correct default. We would revisit this on constrained hardware.

**Q15. Why is the header authenticated but not encrypted?**
The control centre must read the gateway sequence number and timestamp to reject replays
*before* it attempts decryption, so those fields have to be in clear. Passing them as
associated data means they are still covered by the GCM tag. Stage 4 confirms it: flipping one
bit inside `gateway_id` was rejected with `InvalidTag`, exactly as flipping a ciphertext bit
was.

**Q16. Would ChaCha20-Poly1305 have worked?**
Yes, and we say so in D.3. It is an equally sound AEAD and is usually faster where AES-NI is
absent — which is exactly the constrained-device case this project is about. We use AES because
the problem statement names it, not because ChaCha20 is inferior. AES-CCM would also work and
would be the better choice on a small microcontroller.

**Q17. Why not just use TLS for the uplink?**
It would work well for that link, and real deployments use it. But it presumes a session
handshake, certificates and a PKI, and key distribution is explicitly out of scope (A.6). More
importantly it does nothing for the legacy link, which is the part we are studying. The uplink
is the easy half.

---

## Cryptanalysis and the worked example

**Q18. Why does AES appear faster than Caesar in your timings?**
It is an artefact of implementation, not of algorithms, and the run log says so on every
timing page. Our classical ciphers are pure Python loops; AES runs in the `cryptography`
library's compiled backend with AES-NI hardware acceleration. The figures compare
implementations. Nothing in our data suggests AES is intrinsically cheaper than a shift
cipher.

**Q19. Your brute-force attack knows the frame layout. Isn't that a known-plaintext attack?**
No. It is ciphertext-only with a plaintext-*recognition* test. The attacker holds only the
ciphertext and uses public protocol knowledge — the field tags sit at fixed positions — to
recognise which of the 36 candidate decryptions is well-formed. No matching plaintext-ciphertext
pair is used. Known plaintext is a separate, stronger technique we apply to Affine and
Vigenère.

**Q20. Why does Affine known-plaintext recovery fail with the D and V tag pair?**
Because 36 is composite. Two known pairs give `c ≡ a·p + b (mod 36)`; subtracting eliminates
`b` and leaves `a` multiplied by the difference of the plaintext indices. For D (3) and V (21)
that difference is 18, and `gcd(18, 36) = 18`, so 18 is not invertible — executed against our
ciphertext, all twelve valid multipliers satisfy the equation and nothing is recovered. Using
D (3) and I (8) instead gives a difference of 5, which is coprime to 36, and `a` comes out
uniquely as 5.

**Q21. Why does Playfair need a filler, and why is X reserved?**
Playfair encrypts in digrams, so it cannot process a repeated pair or an odd-length message
without inserting a filler character. Our frame contains `...Q000123`, whose doubled `00`
forces one. We reserve `X` and exclude it from every reading so the parser can strip it
unambiguously after decryption. The important detail is that the filler lands *inside* the
frame, not at the end, so the parser must remove every `X`, not just trailing ones — our first
implementation got this wrong and the round-trip test caught it.

**Q22. Will frequency analysis actually work on a 27-character frame?**
Possibly not, and we have committed in advance to reporting that honestly (Q1 in C.3). A
telemetry frame is not natural language: mostly near-uniform digits with six fixed tags, so a
single frame gives very little distributional signal. If the technique needs many frames
accumulated under one key, that is a finding about short structured messages, not a reason to
switch to an easier method.

---

## Method and evidence

**Q23. How do you know your validator results are not just an artefact of the ranges you
chose?**
We do not claim otherwise — it is declared as limitation L4. The plausibility ranges are our
modelling assumption, not a utility specification, and we label them as such in the code. That
is precisely why E6 measures false alarms: tightening the ranges would raise the detection rate
while rejecting genuine readings, so the two numbers only mean something reported together.

**Q24. You write both the attacks and the defence. How is that a fair test?**
It is the most serious threat to validity in the project, listed as L7. Our safeguard is to
include attacks chosen specifically to defeat our own validator — the small in-range edit is in
the set precisely because it passes — and to report its success rather than omit it. The
prototype already demonstrates that discipline.

**Q25. What would make you abandon or change the approach?**
If the measured detection rate with validation on turned out to be indistinguishable from
validation off, the mitigation would not be worth presenting as one, and we would report that
negative result. Equally, if the per-frame cost approached the 10 ms IED constraint cited in
[3], the latency story would become the finding instead of a footnote. Neither looks likely
from the prototype, but both are outcomes we would publish rather than hide.
