#!/usr/bin/env python3
"""
Unit and Integration Tests for Ars Arcanum Local AI Fine-Tuning Synthesizer
(tests/test_fine_tuning.py)
"""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.lib.fine_tuning import (
    DatasetSynthesizer,
    InstructionExample,
    clean_prose,
    export_fine_tuning_dataset,
    generate_ollama_modelfile,
    main as fine_tuning_main,
)


class TestFineTuningDatasetSynthesizer(unittest.TestCase):
    """Validates multi-domain instruction dataset generation, formatting, and splitting."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # 1. Create sample Character note
        char_dir = self.root / "Characters"
        char_dir.mkdir(parents=True, exist_ok=True)
        char_file = char_dir / "Vaelor.md"
        char_file.write_text(
            "---\n"
            "name: Inquisitor Vaelor\n"
            "type: Character\n"
            "aliases: [The Iron Scribe, Hand of Judgement]\n"
            "traits: uncompromising rigor, devotion to canon, ascetic discipline\n"
            "faction: The Obsidian Concord\n"
            "---\n"
            "# Inquisitor Vaelor\n\n"
            "Inquisitor Vaelor stands as the senior chronicler of the Obsidian Concord. "
            "He was born in the ash wastes of Khem and dedicated his youth to the study of ancient glyphs. "
            "His word carries absolute judicial authority across the frontier provinces.\n",
            encoding="utf-8",
        )

        # 2. Create sample Magic System note
        magic_dir = self.root / "MagicSystems"
        magic_dir.mkdir(parents=True, exist_ok=True)
        magic_file = magic_dir / "Glyph_Weaving.md"
        magic_file.write_text(
            "---\n"
            "name: Glyph Weaving\n"
            "type: MagicSystem\n"
            "cost: severe sensory exhaustion and temporal distortion of short-term memory\n"
            "source: atmospheric aetheric resonance\n"
            "---\n"
            "# Glyph Weaving\n\n"
            "Glyph weaving requires tracing incandescent geometric formulas into the air using focused silver needles. "
            "The complexity of the geometric symmetry directly dictates the magnitude of the resulting kinetic ward.\n",
            encoding="utf-8",
        )

        # 3. Create sample Manuscript Chapter note
        ms_dir = self.root / "Manuscript" / "Chapters"
        ms_dir.mkdir(parents=True, exist_ok=True)
        ms_file = ms_dir / "01_Chapter_01.md"
        ms_file.write_text(
            "---\n"
            "title: Chapter 1: The Ash Gate\n"
            "---\n"
            "@pov: Vaelor\n"
            "@thread: Main-Investigation\n\n"
            "The iron gates of the citadel groaned against the howling northern gale as Vaelor stepped into the courtyard. "
            "Snow drifted in spiraling pale eddies across the dark basalt cobblestones, catching the amber light of the torch sconces.\n\n"
            "He reached into his heavy wool cloak and withdrew the sealed ledger of the Concord, feeling the cold leaden seal press against his fingertips. "
            "Every page inside held confessions that could shatter the fragile truce between the eastern houses and the High Council.\n\n"
            "A solitary figure stepped out from the archway shadows, the silhouette etched against the flickering braziers with a drawn silver rapier.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_clean_prose_strips_tags_and_wikilinks(self) -> None:
        """Verifies tag stripping and link normalization."""
        raw = "@pov: Kaelen\n@status: Draft\n\nHe visited [[Sunfire_Citadel|The Citadel]] to find [[Valerius]]."
        cleaned = clean_prose(raw)
        self.assertNotIn("@pov:", cleaned)
        self.assertNotIn("@status:", cleaned)
        self.assertIn("The Citadel", cleaned)
        self.assertIn("Valerius", cleaned)

    def test_synthesize_instruction_examples(self) -> None:
        """Verifies multi-category instruction pair generation from vault files."""
        synthesizer = DatasetSynthesizer(self.root)
        count = synthesizer.scan_and_synthesize()
        self.assertGreater(count, 0)

        categories = {ex.category for ex in synthesizer.examples}
        self.assertIn("persona", categories)
        self.assertIn("magic", categories)
        self.assertIn("prose", categories)

        # Check character persona example
        persona_ex = next(ex for ex in synthesizer.examples if ex.category == "persona")
        self.assertIn("Vaelor", persona_ex.instruction)
        self.assertIn("Obsidian Concord", persona_ex.output_text)

        # Check magic example
        magic_ex = next(ex for ex in synthesizer.examples if ex.category == "magic" and "costs and consequences" in ex.output_text)
        self.assertIn("Glyph Weaving", magic_ex.instruction)
        self.assertIn("sensory exhaustion", magic_ex.output_text)

        # Check prose continuation example
        prose_ex = next(ex for ex in synthesizer.examples if ex.category == "prose")
        self.assertIn("Chapter 1", prose_ex.instruction)
        self.assertIn("iron gates", prose_ex.input_text)
        self.assertIn("sealed ledger", prose_ex.output_text)

    def test_export_formats_alpaca_sharegpt_chatml(self) -> None:
        """Verifies conversion to standard LLM instruction schemas."""
        ex = InstructionExample(
            category="persona",
            system_prompt="You are Inquisitor Vaelor.",
            instruction="Who are you?",
            input_text="",
            output_text="I am the Iron Scribe.",
            source_doc="Characters/Vaelor.md",
        )

        # Alpaca
        alpaca = ex.to_alpaca()
        self.assertIn("instruction", alpaca)
        self.assertIn("output", alpaca)
        self.assertEqual(alpaca["output"], "I am the Iron Scribe.")

        # ShareGPT
        sharegpt = ex.to_sharegpt()
        self.assertIn("conversations", sharegpt)
        self.assertEqual(len(sharegpt["conversations"]), 3)
        self.assertEqual(sharegpt["conversations"][0]["from"], "system")
        self.assertEqual(sharegpt["conversations"][1]["from"], "human")
        self.assertEqual(sharegpt["conversations"][2]["from"], "gpt")

        # ChatML
        chatml = ex.to_chatml()
        self.assertIn("messages", chatml)
        self.assertEqual(len(chatml["messages"]), 3)
        self.assertEqual(chatml["messages"][0]["role"], "system")
        self.assertEqual(chatml["messages"][1]["role"], "user")
        self.assertEqual(chatml["messages"][2]["role"], "assistant")

    def test_dataset_export_and_splits(self) -> None:
        """Verifies writing dataset splits and metadata manifest."""
        synthesizer = DatasetSynthesizer(self.root)
        synthesizer.scan_and_synthesize()

        out_dir = self.root / "dist_ft"
        summary = export_fine_tuning_dataset(
            examples=synthesizer.examples,
            output_dir=out_dir,
            output_format="alpaca",
            val_split=0.2,
            generate_modelfile=True,
        )

        self.assertTrue((out_dir / "train.jsonl").is_file())
        self.assertTrue((out_dir / "val.jsonl").is_file())
        self.assertTrue((out_dir / "Modelfile").is_file())
        self.assertTrue((out_dir / "dataset_manifest.json").is_file())
        self.assertGreater(summary["total_examples"], 0)

    def test_ollama_modelfile_generation(self) -> None:
        """Verifies Ollama Modelfile text synthesis."""
        mf = generate_ollama_modelfile(
            model_base="mistral:7b",
            temperature=0.8,
        )
        self.assertIn("FROM mistral:7b", mf)
        self.assertIn("PARAMETER temperature 0.8", mf)
        self.assertIn("SYSTEM \"\"\"", mf)
        self.assertIn("TEMPLATE \"\"\"", mf)

    def test_cli_execution(self) -> None:
        """Verifies CLI execution of dataset synthesis."""
        out_dir = self.root / "cli_ft"
        code = fine_tuning_main([
            str(self.root),
            "-f", "sharegpt",
            "-o", str(out_dir),
            "-s", "0.25",
        ])
        self.assertEqual(code, 0)
        self.assertTrue((out_dir / "train.jsonl").is_file())

    def test_empty_vault_synthesis_returns_zero(self) -> None:
        """Verifies empty directory produces 0 examples without crashing."""
        empty_dir = self.root / "Empty"
        empty_dir.mkdir(parents=True, exist_ok=True)
        synthesizer = DatasetSynthesizer(empty_dir)
        count = synthesizer.scan_and_synthesize()
        self.assertEqual(count, 0)
        self.assertEqual(len(synthesizer.examples), 0)

    def test_nonexistent_directory_raises_error(self) -> None:
        """Verifies FileNotFoundError on nonexistent target directory."""
        nonexistent = self.root / "Ghost_Directory"
        synthesizer = DatasetSynthesizer(nonexistent)
        with self.assertRaises(FileNotFoundError):
            synthesizer.scan_and_synthesize()

    def test_system_prompt_customization_in_modelfile(self) -> None:
        """Verifies custom parameters in generated Modelfile."""
        mf = generate_ollama_modelfile(
            model_base="llama3:8b",
            system_prompt="You are the Chronicler of the Sunfire Citadel.",
            temperature=0.7,
            top_p=0.9,
            repeat_penalty=1.1,
        )
        self.assertIn("FROM llama3:8b", mf)
        self.assertIn("PARAMETER temperature 0.7", mf)
        self.assertIn("PARAMETER top_p 0.9", mf)
        self.assertIn("PARAMETER repeat_penalty 1.1", mf)
        self.assertIn("Chronicler of the Sunfire Citadel", mf)

    def test_sharegpt_without_system_prompt(self) -> None:
        """Verifies ShareGPT format when system_prompt is empty."""
        ex = InstructionExample(
            category="magic",
            system_prompt="",
            instruction="What is Glyph Weaving?",
            input_text="",
            output_text="A hard magic system.",
            source_doc="MagicSystems/Glyph_Weaving.md",
        )
        sg = ex.to_sharegpt()
        self.assertEqual(len(sg["conversations"]), 2)
        self.assertEqual(sg["conversations"][0]["from"], "human")
        self.assertEqual(sg["conversations"][1]["from"], "gpt")

    def test_export_all_three_formats_jsonl(self) -> None:
        """Verifies writing dataset splits across alpaca, sharegpt, and chatml formats."""
        synthesizer = DatasetSynthesizer(self.root)
        synthesizer.scan_and_synthesize()

        for fmt in ("alpaca", "sharegpt", "chatml"):
            out_dir = self.root / f"dist_{fmt}"
            export_fine_tuning_dataset(
                examples=synthesizer.examples,
                output_dir=out_dir,
                output_format=fmt,
                val_split=0.2,
                generate_modelfile=False,
            )
            train_file = out_dir / "train.jsonl"
            self.assertTrue(train_file.is_file())
            first_line = json.loads(train_file.read_text(encoding="utf-8").strip().splitlines()[0])
            if fmt == "alpaca":
                self.assertIn("instruction", first_line)
            elif fmt == "sharegpt":
                self.assertIn("conversations", first_line)
            elif fmt == "chatml":
                self.assertIn("messages", first_line)

    def test_cli_custom_val_split_and_modelfile(self) -> None:
        """Verifies CLI execution with -f chatml and custom split."""
        out_dir = self.root / "cli_chatml"
        code = fine_tuning_main([
            str(self.root),
            "-f", "chatml",
            "-o", str(out_dir),
            "-s", "0.3",
        ])
        self.assertEqual(code, 0)
        self.assertTrue((out_dir / "train.jsonl").is_file())
        self.assertTrue((out_dir / "Modelfile").is_file())
        mf_content = (out_dir / "Modelfile").read_text(encoding="utf-8")
        self.assertIn("FROM", mf_content)


if __name__ == "__main__":
    unittest.main()
