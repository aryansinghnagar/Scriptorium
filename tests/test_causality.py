#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Causal DAGs & Multiverse Engine (scripts/lib/causality.py).
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
        self.ms_dir.mkdir(parents=True)
        (self.world_dir / "History").mkdir(parents=True)
        (self.ms_dir / "Book-01" / "01_Act_I").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_clean_linear_dag(self):
        (self.world_dir / "History" / "Event_1.md").write_text("""---
name: "The First Discovery"
id: event-1
causes:
  - event-2
---
""", encoding="utf-8")

        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Scene 1
@event: event-2
@timeline: prime
@time: 2050-01-01
@causal-origin: event-1
@causes: event-3
""", encoding="utf-8")

        (self.ms_dir / "Book-01" / "01_Act_I" / "02_Scene.md").write_text("""# Scene 2
@event: event-3
@timeline: prime
@time: 2050-02-01
@causal-origin: event-2
""", encoding="utf-8")

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        self.assertIn("event-1", events)
        self.assertIn("event-2", events)
        self.assertIn("event-3", events)

        findings = audit_causality(events, timelines)
        self.assertEqual(len(findings), 0)

        mermaid = generate_causality_mermaid(events, timelines)
        self.assertIn("graph TD", mermaid)
        self.assertIn("event-1", mermaid)

    def test_grandfather_and_bootstrap_paradoxes(self):
        # Create a loop: event-A -> event-B -> event-A
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_LoopA.md").write_text("""# Scene A
@event: loop-a
@causes: loop-b
@paradox-type: grandfather
""", encoding="utf-8")

        (self.ms_dir / "Book-01" / "01_Act_I" / "02_LoopB.md").write_text("""# Scene B
@event: loop-b
@causes: loop-a
""", encoding="utf-8")

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        ids = [f["id"] for f in findings]
        self.assertIn("CAU-101", ids) # Grandfather paradox detected

    def test_self_consistent_predestination_loop(self):
        # A loop marked with predestination should NOT raise an error
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_LoopA.md").write_text("""# Scene A
@event: loop-predestined-a
@causes: loop-predestined-b
@paradox-type: predestination
""", encoding="utf-8")

        (self.ms_dir / "Book-01" / "01_Act_I" / "02_LoopB.md").write_text("""# Scene B
@event: loop-predestined-b
@causes: loop-predestined-a
@paradox-type: predestination
""", encoding="utf-8")

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        # No errors for designated self-consistent predestination loop
        self.assertEqual(len(findings), 0)

    def test_dangling_origin(self):
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Dangling.md").write_text("""# Scene
@event: event-orphan
@causal-origin: non-existent-mythic-event
""", encoding="utf-8")

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        ids = [f["id"] for f in findings]
        self.assertIn("CAU-105", ids)

    def test_comma_separated_causal_origins(self):
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Origins.md").write_text("""# Scene
@event: merge-event
@causal-origin: origin-alpha, origin-beta
""", encoding="utf-8")
        events, _ = extract_causal_nodes(self.world_dir, self.ms_dir)
        self.assertIn("merge-event", events)
        self.assertEqual(events["merge-event"]["causal_origins"], ["origin-alpha", "origin-beta"])

    def test_novikov_violation_cau103(self):
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_NovikovA.md").write_text("""# Scene A
@event: novikov-a
@causes: novikov-b
@paradox-type: novikov-violation
""", encoding="utf-8")
        (self.ms_dir / "Book-01" / "01_Act_I" / "02_NovikovB.md").write_text("""# Scene B
@event: novikov-b
@causes: novikov-a
""", encoding="utf-8")
        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)
        ids = [f["id"] for f in findings]
        self.assertIn("CAU-103", ids)

    def test_temporal_inversion(self):
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_LateCause.md").write_text("""# Scene Late
@event: late-event
@timeline: prime
@time: Year 2050
@causes: early-event
""", encoding="utf-8")
        (self.ms_dir / "Book-01" / "01_Act_I" / "02_EarlyEffect.md").write_text("""# Scene Early
@event: early-event
@timeline: prime
@time: Year 2020
""", encoding="utf-8")
        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)
        self.assertTrue(any("Temporal Inversion" in f["message"] for f in findings))

    def test_generate_causality_html_report(self):
        (self.world_dir / "History" / "Event.md").write_text("""---
name: "Big Event"
id: big-event
---
""", encoding="utf-8")
        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        html_out = Path(self.temp_dir.name) / "causality.html"
        generate_causality_html_report({"world": "TestWorld", "events": events, "timelines": timelines, "findings": []}, html_out)
        self.assertTrue(html_out.is_file())
        self.assertIn("Big Event", html_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
