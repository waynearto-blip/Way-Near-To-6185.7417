#!/usr/bin/env python3
"""
6185 Compile Engine — Skill Registration and Refinement
Registers self-learning skills and compiles them into the fixed pipeline.
Skills remain non-canonical; they produce derived descriptors and evidence only.
"""

from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json

# ---------------------------------------------------------------------------
# Skill registration model
# ---------------------------------------------------------------------------

@dataclass
class Skill:
    skill_id: str
    name: str
    version: str
    description: str
    stage: str                          # LEX, BIND, CONSTRUCT, etc.
    function: Callable[..., Any]
    learned_parameters: Dict[str, Any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    version_history: List[Dict[str, Any]] = field(default_factory=list)
    registered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    canonical: bool = False             # always False — skills never become identity

    def refine(self, new_params: Dict[str, Any], evidence_note: str) -> str:
        """
        Self-learning refinement: update parameters, record evidence,
        and append an immutable version-history entry.
        Returns the new version string.
        """
        old_version = self.version
        self.learned_parameters.update(new_params)
        self.evidence.append(f"{datetime.utcnow().isoformat()}Z: {evidence_note}")
        # Semantic version bump (minor)
        if "." in self.version:
            major, minor = self.version.split(".", 1)
            try:
                self.version = f"{major}.{int(minor) + 1}"
            except ValueError:
                self.version = f"{self.version}.1"
        else:
            self.version = f"{self.version}.1"

        self.version_history.append({
            "from_version": old_version,
            "to_version": self.version,
            "parameters": dict(self.learned_parameters),
            "evidence_note": evidence_note,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": "refine",
        })
        return self.version

    def rollback(self, target_version: str) -> str:
        """
        Roll back to a previous version recorded in version_history.
        Restores parameters from that version and records the rollback as a new history entry.
        Returns the version after rollback.
        """
        # Find the most recent history entry that produced target_version
        target_entry = None
        for entry in reversed(self.version_history):
            if entry["to_version"] == target_version:
                target_entry = entry
                break
        if target_entry is None:
            # Also allow rollback to the original registered version if no history yet
            if target_version == self.version and not self.version_history:
                return self.version
            raise ValueError(f"Version {target_version} not found in history")

        old_version = self.version
        self.learned_parameters = dict(target_entry["parameters"])
        self.version = target_version
        self.evidence.append(
            f"{datetime.utcnow().isoformat()}Z: rollback from {old_version} to {target_version}"
        )
        self.version_history.append({
            "from_version": old_version,
            "to_version": target_version,
            "parameters": dict(self.learned_parameters),
            "evidence_note": f"rollback to {target_version}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": "rollback",
        })
        return self.version

# ---------------------------------------------------------------------------
# Compile Engine
# ---------------------------------------------------------------------------

class CompileEngine:
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.pipeline_order = [
            "RECEIVE", "LEX", "BIND", "TRANSLITERATE",
            "ESCAPE_BOUND", "CONSTRUCT", "EXECUTE",
            "VERIFY", "REGISTER", "HALT"
        ]

    def register(self, skill: Skill) -> str:
        """Register a skill. Returns skill_id. Skills are never canonical."""
        if skill.skill_id in self.skills:
            raise ValueError(f"Skill {skill.skill_id} already registered")
        skill.canonical = False
        self.skills[skill.skill_id] = skill
        return skill.skill_id

    def refine(self, skill_id: str, new_params: Dict[str, Any], evidence_note: str) -> None:
        """Refine an existing skill (self-learning step)."""
        if skill_id not in self.skills:
            raise KeyError(f"Skill {skill_id} not registered")
        self.skills[skill_id].refine(new_params, evidence_note)

    def compile(self, stage: str, input_data: Any) -> Any:
        """
        Apply all skills registered for the given pipeline stage.
        Returns derived output only — never mutates identity.
        """
        if stage not in self.pipeline_order:
            raise ValueError(f"Unknown stage: {stage}")

        result = input_data
        applied = []
        for skill in self.skills.values():
            if skill.stage == stage:
                result = skill.function(result, skill.learned_parameters)
                applied.append(skill.skill_id)

        return {
            "stage": stage,
            "input": input_data,
            "output": result,
            "skills_applied": applied,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "canonical": False,
        }

    def list_skills(self) -> List[Dict[str, Any]]:
        return [
            {
                "skill_id": s.skill_id,
                "name": s.name,
                "version": s.version,
                "stage": s.stage,
                "learned_parameters": s.learned_parameters,
                "evidence_count": len(s.evidence),
                "version_history_length": len(s.version_history),
                "canonical": s.canonical,
            }
            for s in self.skills.values()
        ]

    def get_version_history(self, skill_id: str) -> List[Dict[str, Any]]:
        """Return the immutable version history of a skill."""
        if skill_id not in self.skills:
            raise KeyError(f"Skill {skill_id} not registered")
        return list(self.skills[skill_id].version_history)

    def rollback(self, skill_id: str, target_version: str) -> str:
        """
        Roll a skill back to a previously recorded version.
        Returns the version after rollback.
        """
        if skill_id not in self.skills:
            raise KeyError(f"Skill {skill_id} not registered")
        return self.skills[skill_id].rollback(target_version)

    def learning_loop(
        self,
        stage: str,
        samples: List[Any],
        skill_id: str,
        refine_fn: Callable[[Any, Dict], Dict[str, Any]],
        max_iterations: int = 5,
        convergence_note: str = "learning loop iteration",
    ) -> List[Dict[str, Any]]:
        """
        Dynamic learning loop.
        Runs compile → observe → refine for up to max_iterations.
        refine_fn receives (compile_result, current_params) and returns new_params dict.
        Returns the list of iteration records.
        Skills remain non-canonical throughout.
        """
        if skill_id not in self.skills:
            raise KeyError(f"Skill {skill_id} not registered")
        if stage not in self.pipeline_order:
            raise ValueError(f"Unknown stage: {stage}")

        history = []
        for i in range(max_iterations):
            iteration_results = []
            for sample in samples:
                result = self.compile(stage, sample)
                iteration_results.append(result)

            # Derive refinement from the batch
            current_params = self.skills[skill_id].learned_parameters.copy()
            new_params = refine_fn(iteration_results, current_params)

            if new_params == current_params:
                history.append({
                    "iteration": i + 1,
                    "converged": True,
                    "note": "No parameter change",
                    "results_count": len(iteration_results),
                })
                break

            self.refine(
                skill_id,
                new_params,
                f"{convergence_note} #{i + 1}",
            )
            history.append({
                "iteration": i + 1,
                "converged": False,
                "from_version": self.skills[skill_id].version_history[-1]["from_version"],
                "to_version": self.skills[skill_id].version,
                "new_params": new_params,
                "results_count": len(iteration_results),
            })

        return history

    def audit_blanket(self) -> Dict[str, Any]:
        """Security blanket: audited names of all registered skills."""
        return {
            "engine": "6185-CompileEngine",
            "skill_count": len(self.skills),
            "skills": [
                {
                    "audited_name": f"hrs.skill.{s.skill_id}.v{s.version}",
                    "stage": s.stage,
                    "canonical": False,
                    "pool_status": "void",
                }
                for s in self.skills.values()
            ],
            "generated": datetime.utcnow().isoformat() + "Z",
        }

# ---------------------------------------------------------------------------
# Example self-learning skills
# ---------------------------------------------------------------------------

def skill_token_range_predictor(token_stream: Any, params: Dict) -> Dict:
    """Predicts range class from token volume (self-refining)."""
    volume = len(str(token_stream).encode()) if token_stream else 0
    threshold = params.get("short_threshold", 64)
    predicted = "token" if volume < threshold else "short"
    return {"volume": volume, "predicted_range": predicted, "threshold_used": threshold}

def skill_identity_normaliser(identity: str, params: Dict) -> str:
    """Normalises identity string (example skill)."""
    return identity.strip().upper() if isinstance(identity, str) else identity

# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    engine = CompileEngine()

    # Register skills
    s1 = Skill(
        skill_id="range-predictor",
        name="Token Range Predictor",
        version="1.0",
        description="Predicts range class from token volume",
        stage="LEX",
        function=skill_token_range_predictor,
        learned_parameters={"short_threshold": 64},
    )
    s2 = Skill(
        skill_id="id-normaliser",
        name="Identity Normaliser",
        version="1.0",
        description="Normalises identity strings",
        stage="BIND",
        function=skill_identity_normaliser,
    )
    engine.register(s1)
    engine.register(s2)

    # Self-learning refinement
    engine.refine("range-predictor", {"short_threshold": 48}, "Lowered threshold after sample analysis")

    # Compile
    sample_input = "HRS:MT:GEN:001:001:L00:W03:C05"
    result = engine.compile("LEX", sample_input)
    print("Compile result (LEX):")
    print(json.dumps(result, indent=2, default=str))

    print("\nRegistered skills:")
    print(json.dumps(engine.list_skills(), indent=2))

    print("\n--- Dynamic Learning Loop ---")
    samples = [
        "HRS:MT:GEN:001:001:L00:W03:C05",
        "HRS:YID:EX:001:001:L00:W01:C01",
        "short",
    ]

    def refine_threshold(results, current_params):
        # Simple heuristic: if average volume < current threshold, lower it
        volumes = [r["output"].get("volume", 0) for r in results if isinstance(r.get("output"), dict)]
        if not volumes:
            return current_params
        avg = sum(volumes) / len(volumes)
        threshold = current_params.get("short_threshold", 64)
        if avg < threshold * 0.8:
            return {"short_threshold": max(16, int(threshold * 0.75))}
        return current_params

    loop_history = engine.learning_loop(
        stage="LEX",
        samples=samples,
        skill_id="range-predictor",
        refine_fn=refine_threshold,
        max_iterations=4,
    )
    print(json.dumps(loop_history, indent=2))

    print("\nVersion history (range-predictor):")
    print(json.dumps(engine.get_version_history("range-predictor"), indent=2))

    print("\n--- Version Rollback ---")
    rolled = engine.rollback("range-predictor", "1.1")
    print(f"Rolled back to: {rolled}")
    print("Current parameters:", engine.skills["range-predictor"].learned_parameters)
    print("Version history after rollback:")
    print(json.dumps(engine.get_version_history("range-predictor"), indent=2))

    print("\nFinal audit blanket:")
    print(json.dumps(engine.audit_blanket(), indent=2))
