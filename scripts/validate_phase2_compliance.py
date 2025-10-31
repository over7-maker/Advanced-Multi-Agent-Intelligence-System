#!/usr/bin/env python3
"""
Phase 2 Compliance Validator
Validates that core Phase 2 requirements are met across K8s manifests.
"""
import glob
import sys
from pathlib import Path
from typing import List

import yaml


class Phase2Validator:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_security_hardening(self, k8s_path: str) -> None:
        deployment_files = glob.glob(str(Path(k8s_path) / "*deployment*.yaml"))
        for file_path in deployment_files:
            with open(file_path, "r") as f:
                docs = list(yaml.safe_load_all(f))
            for doc in docs:
                if not doc or doc.get("kind") != "Deployment":
                    continue
                spec = (
                    doc.get("spec", {})
                    .get("template", {})
                    .get("spec", {})
                )
                # Pod security context
                if not spec.get("securityContext") and not spec.get("seccompProfile"):
                    self.errors.append(f"{file_path}: Missing pod-level securityContext/seccompProfile")
                containers = spec.get("containers", [])
                if not containers:
                    self.errors.append(f"{file_path}: No containers defined")
                    continue
                for c in containers:
                    sc = c.get("securityContext")
                    if not sc:
                        self.errors.append(f"{file_path}: Missing container securityContext for {c.get('name')}")
                    image = c.get("image", "")
                    if image.endswith(":latest"):
                        self.errors.append(f"{file_path}: Floating image tag ':latest' for {c.get('name')}")
                    # TLS envs
                    for env in c.get("env", []):
                        if env.get("name") == "DATABASE_URL" and "sslmode=require" not in env.get("value", ""):
                            self.errors.append(f"{file_path}: DATABASE_URL missing sslmode=require")
                        if env.get("name") == "REDIS_URL" and not env.get("value", "").startswith("rediss://"):
                            self.errors.append(f"{file_path}: REDIS_URL not using rediss://")
                        if env.get("name") == "NEO4J_URI" and "+s://" not in env.get("value", ""):
                            self.errors.append(f"{file_path}: NEO4J_URI not using TLS")

    def validate_observability(self, k8s_path: str) -> None:
        # ServiceMonitor or prometheus annotations
        sm_files = glob.glob(str(Path(k8s_path) / "*servicemonitor*.yaml")) + glob.glob(
            str(Path(k8s_path) / "*ServiceMonitor*.yaml")
        )
        if not sm_files:
            self.warnings.append("No ServiceMonitor found (ensure Prometheus Operator present or use annotations)")

    def validate_performance(self, k8s_path: str) -> None:
        deployment_files = glob.glob(str(Path(k8s_path) / "*deployment*.yaml"))
        for file_path in deployment_files:
            with open(file_path, "r") as f:
                docs = list(yaml.safe_load_all(f))
            for doc in docs:
                if not doc or doc.get("kind") != "Deployment":
                    continue
                containers = (
                    doc.get("spec", {})
                    .get("template", {})
                    .get("spec", {})
                    .get("containers", [])
                )
                for c in containers:
                    if not c.get("resources"):
                        self.errors.append(f"{file_path}: Missing resources for {c.get('name')}")

    def validate_reliability(self, k8s_path: str) -> None:
        hpa_files = glob.glob(str(Path(k8s_path) / "*hpa*.yaml"))
        if not hpa_files:
            self.errors.append("No HPA configuration found")
        pdb_files = glob.glob(str(Path(k8s_path) / "*pdb*.yaml")) + glob.glob(
            str(Path(k8s_path) / "*disruption*.yaml")
        )
        if not pdb_files:
            self.errors.append("No PodDisruptionBudget found")

    def run(self, k8s_path: str) -> bool:
        print("Running Phase 2 Compliance Validation...")
        self.validate_security_hardening(k8s_path)
        self.validate_observability(k8s_path)
        self.validate_performance(k8s_path)
        self.validate_reliability(k8s_path)

        if self.errors:
            print("\nErrors:")
            for e in self.errors:
                print(f"  - {e}")
        if self.warnings:
            print("\nWarnings:")
            for w in self.warnings:
                print(f"  - {w}")
        passed = not self.errors
        print("\nResult:", "PASS" if passed else "FAIL")
        return passed


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: validate_phase2_compliance.py <k8s_path>")
        return 2
    validator = Phase2Validator()
    ok = validator.run(sys.argv[1])
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
