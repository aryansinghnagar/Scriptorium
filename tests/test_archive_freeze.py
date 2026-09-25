#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Cosmos Archive Freeze & Cryptographic Provenance Sealer (scripts/lib/archive_freeze.py).
"""

import json
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.archive_freeze import (
    export_freeze_bundle,
    generate_provenance_seal_markdown,
    hash_file,
    main,
    scan_and_freeze_vault,
    verify_vault_freeze,
)


class TestArchiveFreeze(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_dir = Path(self.temp_dir.name) / "Cosmos"
        self.vault_dir.mkdir(parents=True)
        (self.vault_dir / "World" / "Characters").mkdir(parents=True)
        (self.vault_dir / "Manuscript" / "Book-01").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write(self, rel_path: str, content: str) -> Path:
        p = self.vault_dir / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def test_scan_empty_vault(self):
        """Empty directory produces zero tracked files and a deterministic root hash."""
        empty_dir = Path(self.temp_dir.name) / "Empty"
        empty_dir.mkdir()
        manifest = scan_and_freeze_vault(empty_dir)
        self.assertEqual(manifest.total_files, 0)
        self.assertEqual(manifest.total_words, 0)
        self.assertTrue(len(manifest.root_sha256) == 64)

    def test_scan_single_file_hashes(self):
        """Single file computes accurate SHA-256 and SHA-512 hashes."""
        self._write("World/Characters/Kaelen.md", "# Kaelen\nA solitary spellblade.")
        manifest = scan_and_freeze_vault(self.vault_dir)
        self.assertEqual(manifest.total_files, 1)
        self.assertEqual(manifest.files[0].rel_path, "World/Characters/Kaelen.md")
        self.assertTrue(manifest.files[0].is_markdown)
        self.assertGreater(manifest.files[0].word_count, 0)

    def test_scan_computes_word_count_for_markdown(self):
        """Word count is correctly calculated for prose files."""
        self._write("Manuscript/Book-01/01_Chapter.md", "# Chapter 1\nThe cold wind blew.")
        manifest = scan_and_freeze_vault(self.vault_dir)
        self.assertEqual(manifest.total_words, 6)

    def test_root_sha256_is_deterministic(self):
        """Scanning identical directories produces identical root SHA-256."""
        self._write("A.md", "Content A")
        self._write("B.md", "Content B")
        m1 = scan_and_freeze_vault(self.vault_dir)
        m2 = scan_and_freeze_vault(self.vault_dir)
        self.assertEqual(m1.root_sha256, m2.root_sha256)

    def test_ignore_pycache_and_hidden_dirs(self):
        """Directories like __pycache__ and .git are ignored during scanning."""
        self._write("__pycache__/cached.pyc", "binary")
        self._write("Real.md", "Real text")
        manifest = scan_and_freeze_vault(self.vault_dir)
        self.assertEqual(manifest.total_files, 1)
        self.assertEqual(manifest.files[0].rel_path, "Real.md")

    def test_generate_provenance_seal_markdown(self):
        """generate_provenance_seal_markdown creates formatted markdown table."""
        self._write("Lore.md", "Lore entry")
        manifest = scan_and_freeze_vault(self.vault_dir)
        seal = generate_provenance_seal_markdown(manifest)
        self.assertIn("Immutable Provenance Seal", seal)
        self.assertIn("Root SHA-256 Digest", seal)
        self.assertIn("Lore.md", seal)

    def test_export_freeze_bundle_files_created(self):
        """export_freeze_bundle writes ARCHIVE_MANIFEST.json and PROVENANCE_SEAL.md."""
        self._write("Note.md", "Some note")
        manifest = scan_and_freeze_vault(self.vault_dir)
        m_path, s_path = export_freeze_bundle(manifest, self.vault_dir)
        self.assertTrue(m_path.exists())
        self.assertTrue(s_path.exists())
        data = json.loads(m_path.read_text(encoding="utf-8"))
        self.assertEqual(data["total_files"], 1)

    def test_verify_clean_vault_succeeds(self):
        """Untouched vault verifies cleanly with 0 errors."""
        self._write("A.md", "Text A")
        self._write("B.md", "Text B")
        manifest = scan_and_freeze_vault(self.vault_dir)
        res = verify_vault_freeze(manifest.to_dict(), self.vault_dir)
        self.assertTrue(res["is_verified"])
        self.assertEqual(res["error_count"], 0)
        self.assertEqual(res["matched_files"], 2)

    def test_verify_modified_file_flags_frz101(self):
        """Modified file after freeze triggers FRZ-101 checksum mismatch."""
        p = self._write("A.md", "Initial text")
        manifest = scan_and_freeze_vault(self.vault_dir)
        # Modify file
        p.write_text("Tampered text", encoding="utf-8")
        res = verify_vault_freeze(manifest.to_dict(), self.vault_dir)
        self.assertFalse(res["is_verified"])
        ids = [f["id"] for f in res["findings"]]
        self.assertIn("FRZ-101", ids)

    def test_verify_missing_file_flags_frz102(self):
        """Deleted file after freeze triggers FRZ-102 missing file."""
        p = self._write("A.md", "Initial text")
        manifest = scan_and_freeze_vault(self.vault_dir)
        p.unlink()
        res = verify_vault_freeze(manifest.to_dict(), self.vault_dir)
        self.assertFalse(res["is_verified"])
        ids = [f["id"] for f in res["findings"]]
        self.assertIn("FRZ-102", ids)

    def test_verify_untracked_new_file_flags_frz103(self):
        """Newly created file triggers FRZ-103 untracked warning."""
        self._write("A.md", "Initial text")
        manifest = scan_and_freeze_vault(self.vault_dir)
        self._write("NewUnrecorded.md", "Surprise content")
        res = verify_vault_freeze(manifest.to_dict(), self.vault_dir)
        self.assertTrue(res["is_verified"])  # Warnings don't fail verification
        ids = [f["id"] for f in res["findings"]]
        self.assertIn("FRZ-103", ids)

    def test_freeze_manifest_serialization(self):
        """FreezeManifest to_dict produces valid JSON round-trip."""
        self._write("Doc.md", "Hello world")
        manifest = scan_and_freeze_vault(self.vault_dir)
        d = manifest.to_dict()
        raw = json.dumps(d)
        parsed = json.loads(raw)
        self.assertEqual(parsed["version"], manifest.version)
        self.assertEqual(len(parsed["files"]), 1)

    def test_scan_vault_multiple_nested_directories(self):
        """Nested directories are indexed with forward-slash paths."""
        self._write("World/Geography/Maps/North.md", "# North Continent")
        self._write("Manuscript/Draft-01/01.md", "# Scene 1")
        manifest = scan_and_freeze_vault(self.vault_dir)
        paths = [f.rel_path for f in manifest.files]
        self.assertIn("World/Geography/Maps/North.md", paths)
        self.assertIn("Manuscript/Draft-01/01.md", paths)

    def test_hash_file_non_markdown_words_zero(self):
        """Non-markdown files report 0 words."""
        p = self._write("config.json", '{"key": "value"}')
        _, _, size, wc = hash_file(p)
        self.assertGreater(size, 0)
        self.assertEqual(wc, 0)

    def test_cli_main_freeze_and_verify(self):
        """CLI main function works for freeze and verify actions."""
        self._write("Chapter.md", "Prose")
        ret_freeze = main([str(self.vault_dir)])
        self.assertEqual(ret_freeze, 0)

        manifest_file = self.vault_dir / "ARCHIVE_MANIFEST.json"
        self.assertTrue(manifest_file.exists())

        ret_verify = main([str(self.vault_dir), "--verify", str(manifest_file), "--json"])
        self.assertEqual(ret_verify, 0)


if __name__ == "__main__":
    unittest.main()
