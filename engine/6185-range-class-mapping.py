#!/usr/bin/env python3
"""
6185 Range Class Mapping — Reference Implementation
Maps content volume (byte length) to the high-nibble range class
used by the modified SHA-255 descriptor.
"""

from typing import Tuple

# Range class constants (high nibble)
RANGE_EMPTY     = 0x0  # 0 bytes
RANGE_TOKEN     = 0x1  # < 64 bytes
RANGE_SHORT     = 0x2  # 64 B – 1 KiB
RANGE_DOCUMENT  = 0x3  # 1 KiB – 64 KiB
RANGE_ARCHIVE   = 0x4  # > 64 KiB
RANGE_RESERVED  = 0xF  # unknown / reserved

RANGE_NAMES = {
    RANGE_EMPTY:    "empty/void",
    RANGE_TOKEN:    "token/identity",
    RANGE_SHORT:    "short construct",
    RANGE_DOCUMENT: "document",
    RANGE_ARCHIVE:  "archive",
    RANGE_RESERVED: "reserved/unknown",
}

def volume_to_range_class(volume_bytes: int) -> int:
    """
    Deterministic mapping from content volume (bytes) to range class nibble.
    Returns an integer 0x0–0x4 or 0xF.
    """
    if volume_bytes < 0:
        return RANGE_RESERVED
    if volume_bytes == 0:
        return RANGE_EMPTY
    if volume_bytes < 64:
        return RANGE_TOKEN
    if volume_bytes < 1024:
        return RANGE_SHORT
    if volume_bytes <= 64 * 1024:
        return RANGE_DOCUMENT
    return RANGE_ARCHIVE

def apply_range_nibble(sha256_digest: bytes, range_class: int) -> bytes:
    """
    Construct the modified SHA-255:
    - Take the 32-byte SHA-256 digest
    - Replace the high nibble of the first byte with range_class
    - Return the resulting 32-byte value (255 bits of original + 4-bit range)
    """
    if len(sha256_digest) != 32:
        raise ValueError("SHA-256 digest must be 32 bytes")
    if not (0 <= range_class <= 0xF):
        raise ValueError("range_class must be a single nibble")

    result = bytearray(sha256_digest)
    # Clear high nibble, insert range class
    result[0] = (result[0] & 0x0F) | (range_class << 4)
    return bytes(result)

def describe_range(volume_bytes: int) -> Tuple[int, str]:
    """Convenience: returns (range_class, human name)."""
    rc = volume_to_range_class(volume_bytes)
    return rc, RANGE_NAMES.get(rc, "unknown")

# ------------------------------------------------------------------
# Demonstration
# ------------------------------------------------------------------
if __name__ == "__main__":
    import hashlib

    samples = [
        ("empty", b""),
        ("identity-token", b"HRS:MT:GEN:001:001:L00:W03:C05"),
        ("short-construct", ("σ6185 { Bound=true }" * 4).encode("utf-8")),
        ("document", b"X" * 2048),
        ("archive", b"Y" * 100_000),
    ]

    print("Volume → Range Class Mapping")
    print("-" * 60)
    for name, data in samples:
        vol = len(data)
        rc, label = describe_range(vol)
        digest = hashlib.sha256(data).digest()
        modified = apply_range_nibble(digest, rc)
        print(f"{name:20} {vol:8d} B  →  0x{rc:X} ({label})")
        print(f"  SHA-256[:4] : {digest[:4].hex()}")
        print(f"  SHA-255[:4] : {modified[:4].hex()}  (range nibble inserted)")
        print()
