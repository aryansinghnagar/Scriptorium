#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Causal DAG & Time-Travel Consistency Validator (scripts/lib/causality.py).
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.causality import (
    extract_causal_nodes,
    audit_causality,
    generate_causality_mermaid,
    generate_causality_html_report,
)


class TestCausalityEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.world_dir.mkdir(parents=True)
        (self.world_dir / "History").mkdir(parents=True)
        self.ms_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write(self, base_dir: Path, rel_path: str, content: str) -> Path:
        target = base_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    # ------------------------------------------------------------------
    # 1. test_extract_clean_linear_events
    # ------------------------------------------------------------------
    def test_extract_clean_linear_events(self):
        """Two events with no causal loops -> events_dict has exactly 2 entries."""
        self._write(
            self.ms_dir,
            "scene-alpha.md",
            "---\nname: Alpha\ntimeline: prime\n---\n\nProse for alpha.\n",
        )
        self._write(
            self.ms_dir,
            "scene-beta.md",
            "---\nname: Beta\ntimeline: prime\n---\n\nProse for beta.\n",
        )

        events, _timelines = extract_causal_nodes(self.world_dir, self.ms_dir)

        self.assertEqual(len(events), 2)
        ids = set(events.keys())
        self.assertIn("scene-alpha", ids)
        self.assertIn("scene-beta", ids)

    # ------------------------------------------------------------------
    # 2. test_causal_origins_extracted
    # ------------------------------------------------------------------
    def test_causal_origins_extracted(self):
        """@causal-origin tag populates the causal_origins list."""
        self._write(
            self.ms_dir,
            "scene-child.md",
            "@timeline: prime\n@causal-origin: scene-parent\n",
        )
        self._write(self.ms_dir, "scene-parent.md", "@timeline: prime\n")

        events, _timelines = extract_causal_nodes(self.world_dir, self.ms_dir)

        self.assertIn("scene-child", events)
        self.assertIn("scene-parent", events["scene-child"]["causal_origins"])

    # ------------------------------------------------------------------
    # 3. test_causes_extracted
    # ------------------------------------------------------------------
    def test_causes_extracted(self):
        """@causes tag populates the causes list."""
        self._write(
            self.ms_dir,
            "scene-trigger.md",
            "@timeline: prime\n@causes: scene-result\n",
        )
        self._write(self.ms_dir, "scene-result.md", "@timeline: prime\n")

        events, _timelines = extract_causal_nodes(self.world_dir, self.ms_dir)

        self.assertIn("scene-trigger", events)
        self.assertIn("scene-result", events["scene-trigger"]["causes"])

    # ------------------------------------------------------------------
    # 4. test_unregistered_bootstrap_cau102
    # ------------------------------------------------------------------
    def test_unregistered_bootstrap_cau102(self):
        """Mutual causation without paradox_type -> CAU-102 (unregistered bootstrap)."""
        self._write(
            self.ms_dir,
            "scene-a.md",
            "---\ncauses: [scene-b]\n---\n\n@timeline: prime\n",
        )
        self._write(
            self.ms_dir,
            "scene-b.md",
            "---\ncauses: [scene-a]\n---\n\n@timeline: prime\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        codes = [f["id"] for f in findings]
        self.assertIn("CAU-102", codes)

    # ------------------------------------------------------------------
    # 5. test_grandfather_paradox_cau101
    # ------------------------------------------------------------------
    def test_grandfather_paradox_cau101(self):
        """Cycle with paradox_type=grandfather -> CAU-101."""
        self._write(
            self.ms_dir,
            "event-gramps.md",
            "---\ncauses: [event-killer]\nparadox_type: grandfather\n---\n\n@timeline: prime\n",
        )
        self._write(
            self.ms_dir,
            "event-killer.md",
            "---\ncauses: [event-gramps]\nparadox_type: grandfather\n---\n\n@timeline: prime\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        codes = [f["id"] for f in findings]
        self.assertIn("CAU-101", codes)

    # ------------------------------------------------------------------
    # 6. test_novikov_violation_cau103
    # ------------------------------------------------------------------
    def test_novikov_violation_cau103(self):
        """Cycle with paradox_type=novikov-violation -> CAU-103."""
        self._write(
            self.ms_dir,
            "event-nova.md",
            "---\ncauses: [event-anti]\nparadox_type: novikov-violation\n---\n\n@timeline: prime\n",
        )
        self._write(
            self.ms_dir,
            "event-anti.md",
            "---\ncauses: [event-nova]\nparadox_type: novikov-violation\n---\n\n@timeline: prime\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        codes = [f["id"] for f in findings]
        self.assertIn("CAU-103", codes)

    # ------------------------------------------------------------------
    # 7. test_intentional_bootstrap_no_violation
    # ------------------------------------------------------------------
    def test_intentional_bootstrap_no_violation(self):
        """Cycle tagged paradox_type=bootstrap is self-consistent -> no CAU-101/102/103."""
        self._write(
            self.ms_dir,
            "event-loop-x.md",
            "---\ncauses: [event-loop-y]\nparadox_type: bootstrap\n---\n\n@timeline: prime\n",
        )
        self._write(
            self.ms_dir,
            "event-loop-y.md",
            "---\ncauses: [event-loop-x]\nparadox_type: bootstrap\n---\n\n@timeline: prime\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        violation_codes = {"CAU-101", "CAU-102", "CAU-103"}
        raised = {f["id"] for f in findings}
        self.assertTrue(
            raised.isdisjoint(violation_codes),
            f"Unexpected violation codes for intentional bootstrap: {raised & violation_codes}",
        )

    # ------------------------------------------------------------------
    # 8. test_no_cau104_for_prime_only_manuscript
    # ------------------------------------------------------------------
    def test_no_cau104_for_prime_only_manuscript(self):
        """All events on the prime timeline -> no CAU-104 orphan-branch finding."""
        self._write(
            self.ms_dir,
            "scene-one.md",
            "@timeline: prime\n",
        )
        self._write(
            self.ms_dir,
            "scene-two.md",
            "@timeline: prime\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        codes = [f["id"] for f in findings]
        self.assertNotIn("CAU-104", codes)

    # ------------------------------------------------------------------
    # 9. test_dangling_causal_origin_cau105
    # ------------------------------------------------------------------
    def test_dangling_causal_origin_cau105(self):
        """Event referencing a nonexistent causal origin -> CAU-105."""
        self._write(
            self.ms_dir,
            "scene-orphan.md",
            "@timeline: prime\n@causal-origin: ghost-event-xyz\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        codes = [f["id"] for f in findings]
        self.assertIn("CAU-105", codes)

    # ------------------------------------------------------------------
    # 10. test_generate_causality_mermaid
    # ------------------------------------------------------------------
    def test_generate_causality_mermaid(self):
        """generate_causality_mermaid returns a string with 'graph TD' and 'mermaid'."""
        self._write(self.ms_dir, "scene-x.md", "@timeline: prime\n")
        self._write(
            self.ms_dir,
            "scene-y.md",
            "@timeline: prime\n@causes: scene-x\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        output = generate_causality_mermaid(events, timelines)

        self.assertIsInstance(output, str)
        self.assertIn("mermaid", output)
        self.assertIn("graph TD", output)

    # ------------------------------------------------------------------
    # 11. test_generate_causality_html_report
    # ------------------------------------------------------------------
    def test_generate_causality_html_report(self):
        """HTML report is written, has CSP header, and contains 'Causal DAG'."""
        self._write(self.ms_dir, "scene-p.md", "@timeline: prime\n")
        self._write(
            self.ms_dir,
            "scene-q.md",
            "@timeline: prime\n@causes: scene-p\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        report_path = Path(self.temp_dir.name) / "causality_report.html"
        audit_data = {
            "events": events,
            "timelines": timelines,
            "findings": findings,
            "world": "TestWorld",
        }
        generate_causality_html_report(audit_data, report_path)

        self.assertTrue(report_path.exists(), "HTML report file was not created")
        html = report_path.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", html)
        self.assertIn("Causal DAG", html)

    # ------------------------------------------------------------------
    # 12. test_clean_world_zero_findings
    # ------------------------------------------------------------------
    def test_clean_world_zero_findings(self):
        """Linear chain A->B->C with no cycles -> 0 audit findings."""
        self._write(self.ms_dir, "event-aaa.md", "@timeline: prime\n")
        self._write(
            self.ms_dir,
            "event-bbb.md",
            "@timeline: prime\n@causal-origin: event-aaa\n",
        )
        self._write(
            self.ms_dir,
            "event-ccc.md",
            "@timeline: prime\n@causal-origin: event-bbb\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        self.assertEqual(
            len(findings),
            0,
            f"Expected zero findings for clean linear chain, got: {findings}",
        )



    def test_dynamic_butterfly(self):
        self._write(self.ms_dir, "event-1.md", "---\ncauses: [event-2]\nparadox_type: dynamic\n---\n@timeline: prime\n")
        self._write(self.ms_dir, "event-2.md", "---\ncauses: [event-1]\nparadox_type: dynamic\n---\n@timeline: prime\n")
        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)
        self.assertTrue(any(f["id"] == "CAU-201" for f in findings))

if __name__ == "__main__":
    unittest.main()
