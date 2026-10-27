#!/usr/bin/env python3
"""
6185 Inheritance Rule — Void Memory Artefacts
Every layer must inherit from the database when a memory artefact is in the void pool.
"""

from dataclasses import dataclass
from typing import Optional
import sqlite3

@dataclass
class MemoryArtefact:
    artefact_id: str
    pool_status: str          # 'void' or other
    content_hash: Optional[str]
    canonical: bool = False

class Layer:
    """Base class. Every concrete layer inherits its view from the database."""
    def __init__(self, db_path: str):
        self.db_path = db_path

    def load(self, artefact_id: str) -> MemoryArtefact:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        row = c.execute(
            "SELECT protocol_name, content_hash, pool_status FROM protocol_hashes WHERE hash_id = ?",
            (artefact_id,)
        ).fetchone()
        conn.close()
        if row is None:
            raise KeyError(f"Artefact {artefact_id} not in database")
        name, content_hash, pool_status = row
        # Inheritance rule INH-VOID-001
        if pool_status == "void":
            return MemoryArtefact(
                artefact_id=artefact_id,
                pool_status="void",
                content_hash=content_hash,
                canonical=False,          # never promoted
            )
        return MemoryArtefact(
            artefact_id=artefact_id,
            pool_status=pool_status,
            content_hash=content_hash,
            canonical=False,
        )

# Example layers — all inherit the same load behaviour
class IdentityRailLayer(Layer):
    pass

class CompileEngineLayer(Layer):
    pass

class GovernanceKernelLayer(Layer):
    pass

class DescriptorLayer(Layer):
    pass

if __name__ == "__main__":
    db = "6185-Code-Construct-Hash-Pool.db"
    layers = [
        IdentityRailLayer(db),
        CompileEngineLayer(db),
        GovernanceKernelLayer(db),
        DescriptorLayer(db),
    ]
    # Demonstrate inheritance for a void artefact
    sample_id = "PROTO-EXEC"
    for layer in layers:
        art = layer.load(sample_id)
        print(f"{layer.__class__.__name__:25} → {art.artefact_id} pool={art.pool_status} canonical={art.canonical}")
