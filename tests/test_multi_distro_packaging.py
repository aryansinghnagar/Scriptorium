#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Multi-Distribution Packaging & Systemd Units (tests/test_multi_distro_packaging.py).
Validates:
- P5-M3: Systemd user service and timer definitions.
- P5-M5: Arch Linux PKGBUILD and RPM spec file syntax and file mappings.
- setup_arcanum.sh multi-distro mapping and flags.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestMultiDistroPackaging(unittest.TestCase):

    def test_systemd_units_exist_and_valid(self):
        service_file = REPO_ROOT / "configs" / "systemd" / "arcanum-backup.service"
        timer_file = REPO_ROOT / "configs" / "systemd" / "arcanum-backup.timer"

        self.assertTrue(service_file.is_file(), "arcanum-backup.service must exist")
        self.assertTrue(timer_file.is_file(), "arcanum-backup.timer must exist")

        service_content = service_file.read_text(encoding="utf-8")
        self.assertIn("[Unit]", service_content)
        self.assertIn("[Service]", service_content)
        self.assertIn("ExecStart=/usr/bin/arcanum backup --all", service_content)
        self.assertIn("IOSchedulingClass=idle", service_content)

        timer_content = timer_file.read_text(encoding="utf-8")
        self.assertIn("[Unit]", timer_content)
        self.assertIn("[Timer]", timer_content)
        self.assertIn("OnCalendar=", timer_content)
        self.assertIn("Persistent=true", timer_content)

    def test_arch_pkgbuild_exists_and_valid(self):
        pkgbuild = REPO_ROOT / "pkg" / "arch" / "PKGBUILD"
        self.assertTrue(pkgbuild.is_file(), "PKGBUILD must exist")

        content = pkgbuild.read_text(encoding="utf-8")
        self.assertIn("pkgname=ars-arcanum", content)
        self.assertIn("pkgver=1.6.1", content)
        self.assertIn("python-gobject", content)
        self.assertIn("package()", content)
        self.assertIn("arcanum-backup.service", content)

    def test_rpm_spec_exists_and_valid(self):
        spec_file = REPO_ROOT / "pkg" / "rpm" / "ars-arcanum.spec"
        self.assertTrue(spec_file.is_file(), "ars-arcanum.spec must exist")

        content = spec_file.read_text(encoding="utf-8")
        self.assertIn("Name:           ars-arcanum", content)
        self.assertIn("Version:        1.6.1", content)
        self.assertIn("Requires:       python3-gobject", content)
        self.assertIn("%install", content)
        self.assertIn("%files", content)
        self.assertIn("arcanum-backup.timer", content)

    def test_setup_arcanum_script_multi_distro_support(self):
        setup_script = REPO_ROOT / "scripts" / "setup_arcanum.sh"
        self.assertTrue(setup_script.is_file())

        content = setup_script.read_text(encoding="utf-8")
        self.assertIn("--enable-timer", content)
        self.assertIn("dnf", content)
        self.assertIn("pacman", content)
        self.assertIn("zypper", content)
        self.assertIn("arcanum-backup.timer", content)


if __name__ == "__main__":
    unittest.main()
