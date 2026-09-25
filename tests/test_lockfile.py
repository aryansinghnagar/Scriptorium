#!/usr/bin/env python3
"""
Unit Tests for Ars Arcanum Lockfile & Concurrency Control (tests/test_lockfile.py)
================================================================================
Validates:
1. Lock acquisition, re-entrance/exclusive blocking, and timeout handling.
2. Context manager cleanup and descriptor release.
3. Metadata recording into lockfile.
4. World and manuscript lock helpers.
"""

import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.lockfile import (
    ArcanumLock,
    LockTimeoutError,
    acquire_world_lock,
    acquire_manuscript_lock,
)


class TestLockfile(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_basic_lock_acquisition_and_release(self):
        lock_file = self.work_dir / ".arcanum.lock"
        with ArcanumLock(lock_file, op_name="test_op") as lock:
            self.assertTrue(lock._is_locked)
            self.assertTrue(lock_file.is_file())

        self.assertFalse(lock._is_locked)
        content = lock_file.read_text(encoding="utf-8")
        self.assertIn("test_op", content)
        self.assertIn("pid", content)

    def test_nested_lock_timeout(self):
        lock_file = self.work_dir / ".arcanum.lock"
        with ArcanumLock(lock_file, op_name="outer"):
            # Second lock attempt on same file with very short timeout should time out (if exclusive locking active)
            t0 = time.monotonic()
            try:
                with ArcanumLock(lock_file, timeout=0.2, op_name="inner"):
                    pass
            except LockTimeoutError as e:
                self.assertIn("Timed out", str(e))
            elapsed = time.monotonic() - t0
            self.assertGreaterEqual(elapsed, 0.15)

    def test_world_and_manuscript_helpers(self):
        world_dir = self.work_dir / "TestWorld"
        world_dir.mkdir()
        with acquire_world_lock(world_dir, op_name="lore_update"):
            self.assertTrue((world_dir / ".arcanum.lock").is_file())

        ms_dir = self.work_dir / "TestManuscript"
        ms_dir.mkdir()
        with acquire_manuscript_lock(ms_dir, op_name="draft_edit"):
            self.assertTrue((ms_dir / ".arcanum.lock").is_file())


if __name__ == "__main__":
    unittest.main()
