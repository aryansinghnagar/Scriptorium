#!/usr/bin/env python3
"""
Unit test for WCAG 2.1 AA color contrast compliance in generated HTML reports (tests/test_wcag_contrast.py).
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DIFF_PY = REPO_ROOT / "scripts" / "lib" / "manuscript_diff.py"


def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    hex_code = hex_code.lstrip("#")
    if len(hex_code) == 3:
        hex_code = "".join(2 * c for c in hex_code)
    return int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    def channel_lum(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4

    r, g, b = (channel_lum(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex1: str, hex2: str) -> float:
    l1 = relative_luminance(hex_to_rgb(hex1))
    l2 = relative_luminance(hex_to_rgb(hex2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


class TestWcagContrastCompliance(unittest.TestCase):
    """Verifies that color palettes used in HTML diffs meet WCAG 2.1 AA standards (ratio >= 4.5:1 for normal text)."""

    def test_manuscript_diff_palette_contrast(self):
        self.assertTrue(DIFF_PY.is_file())
        content = DIFF_PY.read_text(encoding="utf-8")

        # Extract light mode variables
        light_match = re.search(r":root\s*\{\{(.*?)\}\}", content, re.DOTALL)
        self.assertIsNotNone(light_match, "Could not find :root theme block in manuscript_diff.py")
        light_css = light_match.group(1)

        del_bg = re.search(r"--del-bg:\s*(#[0-9a-fA-F]+);", light_css).group(1)
        del_fg = re.search(r"--del-color:\s*(#[0-9a-fA-F]+);", light_css).group(1)
        ins_bg = re.search(r"--ins-bg:\s*(#[0-9a-fA-F]+);", light_css).group(1)
        ins_fg = re.search(r"--ins-color:\s*(#[0-9a-fA-F]+);", light_css).group(1)

        del_ratio = contrast_ratio(del_fg, del_bg)
        ins_ratio = contrast_ratio(ins_fg, ins_bg)

        self.assertGreaterEqual(
            del_ratio,
            4.5,
            f"Light mode deletion contrast {del_ratio:.2f}:1 fails WCAG AA (>= 4.5:1) for fg {del_fg} on bg {del_bg}"
        )
        self.assertGreaterEqual(
            ins_ratio,
            4.5,
            f"Light mode insertion contrast {ins_ratio:.2f}:1 fails WCAG AA (>= 4.5:1) for fg {ins_fg} on bg {ins_bg}"
        )

        # Extract dark mode variables
        dark_match = re.search(r'\[data-theme="dark"\]\s*\{\{(.*?)\}\}', content, re.DOTALL)
        self.assertIsNotNone(dark_match, "Could not find dark mode theme block in manuscript_diff.py")
        dark_css = dark_match.group(1)

        dark_del_bg = re.search(r"--del-bg:\s*(#[0-9a-fA-F]+);", dark_css).group(1)
        dark_del_fg = re.search(r"--del-color:\s*(#[0-9a-fA-F]+);", dark_css).group(1)
        dark_ins_bg = re.search(r"--ins-bg:\s*(#[0-9a-fA-F]+);", dark_css).group(1)
        dark_ins_fg = re.search(r"--ins-color:\s*(#[0-9a-fA-F]+);", dark_css).group(1)

        dark_del_ratio = contrast_ratio(dark_del_fg, dark_del_bg)
        dark_ins_ratio = contrast_ratio(dark_ins_fg, dark_ins_bg)

        self.assertGreaterEqual(
            dark_del_ratio,
            4.5,
            f"Dark mode deletion contrast {dark_del_ratio:.2f}:1 fails WCAG AA (>= 4.5:1) for fg {dark_del_fg} on bg {dark_del_bg}"
        )
        self.assertGreaterEqual(
            dark_ins_ratio,
            4.5,
            f"Dark mode insertion contrast {dark_ins_ratio:.2f}:1 fails WCAG AA (>= 4.5:1) for fg {dark_ins_fg} on bg {dark_ins_bg}"
        )


if __name__ == "__main__":
    unittest.main()
