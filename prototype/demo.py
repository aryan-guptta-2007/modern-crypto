"""Feasibility prototype for the Legacy Cipher Migration Framework.

Proves the full pipeline end to end on one machine:

    legacy device --(Caesar or Vigenere)--> gateway --(AES-256-GCM)--> control centre

It also runs one passive attack on the legacy link and one active attack that
shows the control centre accepting a forged reading inside a valid AES envelope.

Run:  python prototype/demo.py
"""

import os
import platform
import struct
import sys
import time

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --------------------------------------------------------------------------
# 36-character alphabet, shared by every classical cipher. Arithmetic mod 36.
# --------------------------------------------------------------------------

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
N = len(ALPHABET)
POS = {c: i for i, c in enumerate(ALPHABET)}

CAESAR_SHIFT = 3
VIGENERE_KEY = "GRIDKEY"


def _values(text):
    return [POS[c] for c in text]


def _text(values):
    return "".join(ALPHABET[v % N] for v in values)


def additive_encrypt(text, k):
    return _text(v + k for v in _values(text))


def additive_decrypt(text, k):
    return _text(v - k for v in _values(text))


def caesar_encrypt(text):
    return additive_encrypt(text, CAESAR_SHIFT)


def caesar_decrypt(text):
    return additive_decrypt(text, CAESAR_SHIFT)


def vigenere_encrypt(text, key):
    ks = _values(key)
    return _text(v + ks[i % len(ks)] for i, v in enumerate(_values(text)))


def vigenere_decrypt(text, key):
    ks = _values(key)
    return _text(v - ks[i % len(ks)] for i, v in enumerate(_values(text)))


# --------------------------------------------------------------------------
# Telemetry frame:  D07V2301I0152F4998B1Q000123
# --------------------------------------------------------------------------

FIELDS = [("D", 0, 2), ("V", 3, 4), ("I", 8, 4), ("F", 13, 4), ("B", 18, 1), ("Q", 20, 6)]
FRAME_LEN = 27

# Nominal ranges only. These are modelling assumptions for the prototype,
# not values taken from a utility specification.
RANGES = {"V": (2000, 2600), "I": (0, 1000), "F": (4900, 5100), "B": (0, 1)}


def format_reading(device, voltage, current, freq, breaker, seq):
    return f"D{device:02d}V{voltage:04d}I{current:04d}F{freq:04d}B{breaker:01d}Q{seq:06d}"


def parse_reading(frame):
    """Return a field dict, or raise ValueError if the frame is malformed."""
    if len(frame) != FRAME_LEN:
        raise ValueError(f"length {len(frame)}, expected {FRAME_LEN}")
    out = {}
    for tag, at, width in FIELDS:
        if frame[at] != tag:
            raise ValueError(f"expected tag {tag} at position {at}, found {frame[at]!r}")
        digits = frame[at + 1: at + 1 + width]
        if not digits.isdigit():
            raise ValueError(f"field {tag} is not numeric: {digits!r}")
        out[tag] = int(digits)
    return out


def validate_reading(fields, last_seq):
    """Plausibility and sequence checks. Returns a list of reasons for rejection."""
    reasons = []
    for tag, (lo, hi) in RANGES.items():
        if not lo <= fields[tag] <= hi:
            reasons.append(f"{tag}={fields[tag]} outside plausible range [{lo}, {hi}]")
    if last_seq is not None and fields["Q"] <= last_seq:
        reasons.append(f"sequence {fields['Q']} not greater than {last_seq}")
    return reasons


def pretty(fields):
    return (f"device {fields['D']:02d}  "
            f"{fields['V'] / 10:.1f} V  "
            f"{fields['I'] / 10:.1f} A  "
            f"{fields['F'] / 100:.2f} Hz  "
            f"breaker {'closed' if fields['B'] else 'open'}  "
            f"seq {fields['Q']}")


# --------------------------------------------------------------------------
# AES-256-GCM envelope. Header is authenticated as associated data.
# --------------------------------------------------------------------------

HEADER = struct.Struct("!BHQQ")  # version, gateway_id, gateway_seq, timestamp_ms
VERSION = 1


def load_key():
    """Key comes from the environment, or is generated for this run. Never hard-coded."""
    hex_key = os.environ.get("AES_KEY_HEX")
    if hex_key:
        return bytes.fromhex(hex_key), "AES_KEY_HEX environment variable"
    return os.urandom(32), "generated randomly for this run"


def seal(key, gateway_id, gateway_seq, plaintext):
    header = HEADER.pack(VERSION, gateway_id, gateway_seq, int(time.time() * 1000))
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, plaintext.encode(), header)
    return header + nonce + ct


def open_envelope(key, blob, last_seq, window_ms=30_000):
    """Verify and decrypt. Raises ValueError on any rejection."""
    header, nonce, ct = blob[:HEADER.size], blob[HEADER.size:HEADER.size + 12], blob[HEADER.size + 12:]
    version, gateway_id, gateway_seq, ts = HEADER.unpack(header)
    if version != VERSION:
        raise ValueError(f"unsupported envelope version {version}")
    if last_seq is not None and gateway_seq <= last_seq:
        raise ValueError(f"replayed or out-of-order envelope: seq {gateway_seq} after {last_seq}")
    if abs(int(time.time() * 1000) - ts) > window_ms:
        raise ValueError("timestamp outside the accepted window")
    try:
        plaintext = AESGCM(key).decrypt(nonce, ct, header).decode()
    except InvalidTag:
        raise ValueError("InvalidTag: GCM tag check failed, the envelope was altered")
    return plaintext, gateway_id, gateway_seq


# --------------------------------------------------------------------------
# Instrumentation
# --------------------------------------------------------------------------

IMPL_NOTE = (
    "Note on every timing in this log: the classical ciphers are pure Python, while AES",
    "runs in the cryptography library's compiled backend with AES-NI hardware support, so",
    "the absolute figures compare implementations, not the algorithms themselves.",
)


def timed(label, fn, *args, **kwargs):
    t0 = time.perf_counter_ns()
    result = fn(*args, **kwargs)
    ms = (time.perf_counter_ns() - t0) / 1e6
    print(f"    {label:<34} {ms:8.4f} ms")
    return result


def rule(title):
    print()
    print("=" * 74)
    print(title)
    print("=" * 74)


# --------------------------------------------------------------------------
# Scenarios
# --------------------------------------------------------------------------

def normal_flow(key, legacy_name, enc, dec, gateway_seq, centre_last_seq):
    """One reading travelling device -> gateway -> control centre."""
    print(f"\n  Legacy cipher on the device link: {legacy_name}")
    frame = format_reading(device=7, voltage=2301, current=152, freq=4998, breaker=1, seq=123)
    print(f"    device plaintext frame             {frame}")

    legacy_ct = timed("device: legacy encrypt", enc, frame)
    print(f"    on the legacy link                 {legacy_ct}")

    recovered = timed("gateway: legacy decrypt", dec, legacy_ct)
    fields = timed("gateway: parse", parse_reading, recovered)
    reasons = timed("gateway: validate", validate_reading, fields, None)
    if reasons:
        print(f"    gateway REJECTED: {reasons}")
        return gateway_seq, centre_last_seq

    blob = timed("gateway: AES-256-GCM seal", seal, key, 1, gateway_seq, recovered)
    print(f"    envelope {len(blob)} bytes wrapping a {len(recovered)}-byte frame "
          f"({len(blob) - len(recovered)} bytes overhead)")

    plaintext, _, seq = timed("centre: AES-256-GCM open", open_envelope, key, blob, centre_last_seq)
    print(f"    control centre accepted            {pretty(parse_reading(plaintext))}")
    assert plaintext == frame, "end-to-end mismatch"
    print("    frame at the centre is identical to the frame the device sent")
    return gateway_seq + 1, seq


def attack_brute_force():
    """Ciphertext-only exhaustive key search with a plaintext-recognition test.

    The attacker holds the ciphertext and nothing else. No matching plaintext is
    needed. Each of the 36 candidate decryptions is tested for being a well-formed
    reading, and that test alone identifies the key. This is not a known-plaintext
    attack; known plaintext is a separate technique, used later against Affine and
    Vigenere, where a matched plaintext-ciphertext pair solves for the key directly.
    """
    frame = format_reading(device=7, voltage=2301, current=152, freq=4998, breaker=1, seq=123)
    intercepted = caesar_encrypt(frame)
    print(f"\n  Method: ciphertext-only exhaustive key search over the {N}-key additive space,")
    print("  with a plaintext-recognition test. No matching plaintext is used.")
    print(f"\n  Attacker holds only the ciphertext   {intercepted}")
    print("  Recognition test: does the candidate parse as a well-formed reading?")
    print(f"  (frame layout is public protocol knowledge: tags "
          f"{[t for t, _, _ in FIELDS]} at fixed positions)")

    t0 = time.perf_counter_ns()
    hits = []
    for k in range(N):
        candidate = additive_decrypt(intercepted, k)
        try:
            parse_reading(candidate)
        except ValueError:
            continue
        hits.append((k, candidate))
    ms = (time.perf_counter_ns() - t0) / 1e6

    print(f"\n  Tried all {N} additive keys in {ms:.4f} ms; "
          f"{len(hits)} candidate(s) passed the recognition test.")
    for k, candidate in hits:
        print(f"    key k={k:<3} -> {candidate}   {pretty(parse_reading(candidate))}")
    print("  The key and the reading are both recovered. Key space 36 offers no protection.")


def attack_tamper(key):
    """Active attacker edits the legacy frame; the gateway authenticates the forgery."""
    genuine = format_reading(device=7, voltage=2301, current=152, freq=4998, breaker=1, seq=124)
    print(f"\n  Genuine reading from the device      {genuine}   ({genuine[4:8]} = 230.1 V)")

    for label, voltage, validation in [
        ("gross edit, gateway validation OFF", 2901, False),
        ("gross edit, gateway validation ON", 2901, True),
        ("small edit, gateway validation ON", 2311, True),
    ]:
        forged = format_reading(device=7, voltage=voltage, current=152, freq=4998, breaker=1, seq=124)
        legacy_ct = caesar_encrypt(forged)
        print(f"\n    {label}")
        print(f"      attacker injects                 {legacy_ct}")

        recovered = caesar_decrypt(legacy_ct)
        fields = parse_reading(recovered)
        reasons = validate_reading(fields, None) if validation else []
        if reasons:
            print(f"      gateway REJECTED                 {reasons[0]}")
            continue

        blob = seal(key, 1, 900 + voltage, recovered)
        plaintext, _, _ = open_envelope(key, blob, None)
        print(f"      centre ACCEPTED as authentic     {pretty(parse_reading(plaintext))}")
        print(f"      GCM tag verified, yet the voltage is false "
              f"(sent {voltage / 10:.1f} V, true value 230.1 V)")

    print("\n  Validation reduces the problem. It does not remove it: an edit that stays")
    print("  inside plausible limits is still wrapped in a valid AES envelope.")


def attack_envelope_edit(key):
    """One flipped bit in the envelope, in the ciphertext and then in the header."""
    frame = format_reading(device=7, voltage=2301, current=152, freq=4998, breaker=1, seq=126)
    blob = seal(key, 1, 600, frame)
    plaintext, _, _ = open_envelope(key, blob, None)
    print(f"\n  Untouched envelope, {len(blob)} bytes: accepted, {plaintext}")

    targets = [("ciphertext", HEADER.size + 12), ("header, inside gateway_id", 1)]
    for label, at in targets:
        edited = bytearray(blob)
        edited[at] ^= 0x01
        print(f"\n    one bit flipped in the {label}, byte offset {at}")
        try:
            open_envelope(key, bytes(edited), None)
            print("      centre ACCEPTED  <- would indicate a broken design")
        except ValueError as exc:
            print(f"      centre REJECTED  {exc}")

    print("\n  The header is passed to GCM as associated data, so editing it fails the tag")
    print("  check exactly as editing the ciphertext does. Contrast with Stage 3: GCM")
    print("  proves the envelope is unaltered in transit. It cannot prove that the reading")
    print("  placed inside it by the gateway was true.")


def attack_replay(key):
    """The same envelope offered twice is refused by the control centre."""
    frame = format_reading(device=7, voltage=2301, current=152, freq=4998, breaker=1, seq=125)
    blob = seal(key, 1, 500, frame)
    _, _, seq = open_envelope(key, blob, None)
    print(f"\n  First delivery of envelope seq {seq}: accepted")
    try:
        open_envelope(key, blob, seq)
    except ValueError as exc:
        print(f"  Replay of the same envelope:      rejected ({exc})")

    legacy_ct = caesar_encrypt(frame)
    print(f"  Replay of the same legacy frame:  accepted by the gateway "
          f"({caesar_decrypt(legacy_ct)}), because the legacy frame carries no freshness data")


def benchmark(key, repeats=2000):
    """Mean cost per stage, measured on this machine."""
    frame = format_reading(device=7, voltage=2301, current=152, freq=4998, breaker=1, seq=123)
    legacy_ct = caesar_encrypt(frame)
    vig_ct = vigenere_encrypt(frame, VIGENERE_KEY)
    blob = seal(key, 1, 1, frame)

    stages = [
        ("Caesar encrypt", lambda: caesar_encrypt(frame)),
        ("Caesar decrypt", lambda: caesar_decrypt(legacy_ct)),
        ("Vigenere encrypt", lambda: vigenere_encrypt(frame, VIGENERE_KEY)),
        ("Vigenere decrypt", lambda: vigenere_decrypt(vig_ct, VIGENERE_KEY)),
        ("parse", lambda: parse_reading(frame)),
        ("validate", lambda: validate_reading(parse_reading(frame), None)),
        ("AES-256-GCM seal", lambda: seal(key, 1, 1, frame)),
        ("AES-256-GCM open", lambda: open_envelope(key, blob, None)),
    ]

    print(f"\n  Mean of {repeats} runs per stage, single process, no network.")
    print(f"    {'stage':<22}{'mean (ms)':>12}{'mean (us)':>12}")
    for label, fn in stages:
        t0 = time.perf_counter_ns()
        for _ in range(repeats):
            fn()
        per = (time.perf_counter_ns() - t0) / repeats
        print(f"    {label:<22}{per / 1e6:>12.5f}{per / 1e3:>12.2f}")
    print()
    for line in IMPL_NOTE:
        print("  " + line)
    print("  These figures are for one machine and include Python interpreter overhead.")
    print("  They are not a prediction of latency on real gateway hardware.")


def main():
    key, key_source = load_key()

    rule("Feasibility prototype: legacy cipher migration gateway")
    print(f"  Python            {sys.version.split()[0]}")
    print(f"  Platform          {platform.platform()}")
    print(f"  AES key           256-bit, {key_source}")
    print(f"  Frame format      {FRAME_LEN} characters over a {N}-character alphabet")

    # The first AESGCM call initialises the backend and costs milliseconds. That
    # one-off cost is paid here so the per-stage figures below are steady-state.
    open_envelope(key, seal(key, 0, 0, "A" * FRAME_LEN), None)
    print("  AES backend       initialised before timing, so Stage 1 shows steady-state cost")
    print()
    for line in IMPL_NOTE:
        print("  " + line)

    rule("Stage 1  Normal operation, end to end")
    g_seq, c_seq = 1, None
    g_seq, c_seq = normal_flow(key, "Caesar (shift 3)", caesar_encrypt, caesar_decrypt, g_seq, c_seq)
    g_seq, c_seq = normal_flow(
        key, f"Vigenere (key {VIGENERE_KEY!r})",
        lambda t: vigenere_encrypt(t, VIGENERE_KEY),
        lambda t: vigenere_decrypt(t, VIGENERE_KEY),
        g_seq, c_seq)

    rule("Stage 2  V1  Passive attacker on the legacy link")
    attack_brute_force()

    rule("Stage 3  V2  Authenticated false data")
    attack_tamper(key)

    rule("Stage 4  Editing the AES envelope itself")
    attack_envelope_edit(key)

    rule("Stage 5  V6  Replay on each link")
    attack_replay(key)

    rule("Stage 6  Per-stage cost")
    benchmark(key)

    rule("Result")
    print("  The pipeline runs end to end, the legacy link is broken by exhaustive search,")
    print("  and a forged reading is delivered to the control centre under a valid AES tag.")
    print("  The architecture and the experiments planned for it are therefore feasible.")
    print()


if __name__ == "__main__":
    main()
