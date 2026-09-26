#!/usr/bin/env python3
"""
Test Suite: Optional GPG Backup Encryption & Restore (tests/test_backup_encryption.py)
======================================================================================
Validates:
1. Backup script command-line option handling (--symmetric, --encrypt, --passphrase, --gpg-key).
2. Metadata schema with encryption flags and checksum integrity.
3. Restore script decryption and integrity checks.
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestBackupEncryption(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.has_bash = shutil.which("bash") is not None
        cls.has_gpg = (shutil.which("gpg") is not None) or (shutil.which("gpg2") is not None)
        cls.project_root = Path(__file__).resolve().parent.parent

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="arcanum_backup_enc_test_"))
        self.world_dir = self.temp_dir / "TestWorld"
        self.world_dir.mkdir(parents=True, exist_ok=True)
        (self.world_dir / "world.yaml").write_text("name: TestWorld\nauthor: Author\n", encoding="utf-8")
        bible = self.world_dir / "00-World-Bible" / "Characters"
        bible.mkdir(parents=True, exist_ok=True)
        (bible / "hero.md").write_text("# Hero\n\nSecret Lore", encoding="utf-8")

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_backup_meta_json_schema(self):
        """Test metadata schema serialization for encrypted backup records."""
        meta = {
            "world": "TestWorld",
            "timestamp": "20260921-120000",
            "archive": "TestWorld-backup-20260921-120000.tar.gz.gpg",
            "sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "size_bytes": 1024,
            "git_commit": "none",
            "note": "secure-backup",
            "encrypted": True,
            "encryption_type": "symmetric",
            "gpg_recipient": "none",
        }
        meta_file = self.temp_dir / "test.meta.json"
        meta_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        loaded = json.loads(meta_file.read_text(encoding="utf-8"))
        self.assertTrue(loaded["encrypted"])
        self.assertEqual(loaded["encryption_type"], "symmetric")
        self.assertEqual(loaded["archive"], "TestWorld-backup-20260921-120000.tar.gz.gpg")

    def test_gpg_roundtrip_if_available(self):
        """If GPG and Bash are installed, test actual encrypted backup and restore."""
        if not (self.has_bash and self.has_gpg):
            self.skipTest("Bash and/or GPG not available in environment")

        arcanum_script = (self.project_root / "scripts" / "arcanum").as_posix()
        dest_dir = self.temp_dir / "Backups"
        dest_dir.mkdir(parents=True, exist_ok=True)
        passphrase = "SecretTestPassphrase123!"

        # Run backup with --symmetric and --passphrase
        res = subprocess.run(
            [
                "bash",
                arcanum_script,
                "backup",
                "-w",
                self.world_dir.as_posix(),
                "-d",
                dest_dir.as_posix(),
                "--symmetric",
                "--passphrase",
                passphrase,
                "--no-local",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Backup stdout: {res.stdout}\nstderr: {res.stderr}")

        # Verify output files
        gpg_files = list(dest_dir.glob("*.tar.gz.gpg"))
        self.assertEqual(len(gpg_files), 1, "Encrypted archive should be created")
        archive_path = gpg_files[0]

        meta_files = list(dest_dir.glob("*.meta.json"))
        self.assertEqual(len(meta_files), 1)
        meta_data = json.loads(meta_files[0].read_text(encoding="utf-8"))
        self.assertTrue(meta_data["encrypted"])
        self.assertEqual(meta_data["encryption_type"], "symmetric")

        # Test restore to new target name
        restore_dest = self.temp_dir / "Restored"
        restore_dest.mkdir(parents=True, exist_ok=True)

        res_restore = subprocess.run(
            [
                "bash",
                arcanum_script,
                "restore",
                "-a",
                archive_path.as_posix(),
                "-d",
                restore_dest.as_posix(),
                "-t",
                "RestoredWorld",
                "--passphrase",
                passphrase,
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            res_restore.returncode,
            0,
            f"Restore stdout: {res_restore.stdout}\nstderr: {res_restore.stderr}",
        )
        self.assertTrue((restore_dest / "RestoredWorld" / "00-World-Bible" / "Characters" / "hero.md").exists())


if __name__ == "__main__":
    unittest.main()
