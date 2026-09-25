#!/usr/bin/env python3
"""
Unit tests for the Manuscript Importer Engine (tests/test_importer.py).
"""

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LIB_DIR = REPO_ROOT / "scripts" / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from importer import extract_docx_text, import_manuscript_batch


class TestManuscriptImporter(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.work_path = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_extract_docx_text(self):
        docx_file = self.work_path / "sample.docx"
        doc_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading 1"/></w:pPr>
      <w:r><w:t>The Beginning</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>The cold wind howled across the plains.</w:t></w:r>
    </w:p>
  </w:body>
</w:document>"""
        with zipfile.ZipFile(docx_file, "w") as zf:
            zf.writestr("word/document.xml", doc_xml)

        text = extract_docx_text(docx_file)
        self.assertIn("# The Beginning", text)
        self.assertIn("The cold wind howled across the plains.", text)

    def test_import_manuscript_batch_from_md_folder(self):
        source_dir = self.work_path / "scrivener_export"
        source_dir.mkdir()
        (source_dir / "01_Prologue.md").write_text("Long ago in the first age.", encoding="utf-8")
        (source_dir / "02_The_Call.md").write_text("A hero stood by the gate.", encoding="utf-8")

        dest_dir = self.work_path / "Target_Manuscript"
        res = import_manuscript_batch(
            source_dir,
            dest_dir,
            title="The Chronicles of Eldoria",
            author="Test Author",
        )

        self.assertEqual(res["chapters_imported"], 2)
        self.assertTrue((dest_dir / "manuscript.yaml").is_file())
        self.assertTrue((dest_dir / "nwProject.nwx").is_file())
        self.assertTrue((dest_dir / ".gitignore").is_file())
        self.assertTrue((dest_dir / "Book-01" / "Draft-01" / "01_Prologue.md").is_file())
        self.assertTrue((dest_dir / "Book-01" / "Draft-01" / "02_The_Call.md").is_file())

        yaml_content = (dest_dir / "manuscript.yaml").read_text(encoding="utf-8")
        self.assertIn('title: "The Chronicles of Eldoria"', yaml_content)
        self.assertIn('author: "Test Author"', yaml_content)


if __name__ == "__main__":
    unittest.main()
