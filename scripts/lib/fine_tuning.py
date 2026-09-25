#!/usr/bin/env python3
"""
Ars Arcanum Sovereign Local AI Fine-Tuning & Dataset Synthesizer
(scripts/lib/fine_tuning.py)
================================================================================
Zero-dependency, 100% offline instruction dataset compiler transforming Obsidian
World Bibles, character profiles, dialogue exchanges, and manuscript chapters into
high-quality instruction tuning datasets for local LLM fine-tuning (LoRA / QLoRA
with Unsloth, Ollama, LLaMA-Factory, Axolotl).

Supported Output Formats:
1. Alpaca Format: {"instruction": "...", "input": "...", "output": "..."}
2. ShareGPT Multi-Turn Format: {"conversations": [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]}
3. ChatML / OpenAI Messages Format: {"messages": [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}]}
4. Ollama Modelfile: Tailored Modelfile with custom SYSTEM prompt, parameter settings (temperature, top_p, repeat_penalty), and stop tokens.

Synthesis Generators:
- Character Persona Roleplay & Voice Tuning
- World Lore & Taxonomy Inquisitor Q&A
- Scene Continuation & Prose Rhythm Tuning
- Arcane Rule Compliance & Magic Constraint Auditing

Zero external dependencies; 100% offline privacy.
"""

import argparse
import json
import logging
import os
import random
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import PROJECT_ROOT, atomic_write
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    try:
        from _bootstrap import PROJECT_ROOT, atomic_write
        from frontmatter import parse_yaml_frontmatter
    except ImportError:
        PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

        def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(content, encoding=encoding)
            os.replace(tmp, path)

        def parse_yaml_frontmatter(text: str) -> dict[str, Any]:
            fm_match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", text, re.DOTALL)
            if not fm_match:
                return {}
            meta: dict[str, Any] = {}
            for line in fm_match.group(1).splitlines():
                if ":" in line and not line.strip().startswith("#"):
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip("\"'")
            return meta

logger = logging.getLogger("arcanum.fine_tuning")

CLEAN_TAG_REGEX = re.compile(r"^@([a-zA-Z0-9_-]+):\s*.*$", re.MULTILINE)
WIKILINK_REGEX = re.compile(r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]")


def clean_prose(text: str) -> str:
    """Strips scene tags and normalizes Obsidian wikilinks to clean text."""
    # Remove @tag directives
    cleaned = CLEAN_TAG_REGEX.sub("", text)
    # Replace [[Link|Alias]] with Alias or Link
    cleaned = WIKILINK_REGEX.sub(lambda m: m.group(2) if m.group(2) else m.group(1), cleaned)
    # Normalize multiple newlines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


@dataclass
class InstructionExample:
    """Represents a single canonical prompt-completion training instance."""
    category: str  # "persona", "lore", "prose", "magic"
    system_prompt: str
    instruction: str
    input_text: str
    output_text: str
    source_doc: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_alpaca(self) -> dict[str, Any]:
        return {
            "instruction": self.instruction,
            "input": self.input_text,
            "output": self.output_text,
            "category": self.category,
            "source": self.source_doc,
        }

    def to_sharegpt(self) -> dict[str, Any]:
        convs = []
        if self.system_prompt:
            convs.append({"from": "system", "value": self.system_prompt})

        user_content = self.instruction
        if self.input_text:
            user_content = f"{self.instruction}\n\nContext:\n{self.input_text}"

        convs.append({"from": "human", "value": user_content})
        convs.append({"from": "gpt", "value": self.output_text})
        return {"conversations": convs}

    def to_chatml(self) -> dict[str, Any]:
        msgs = []
        if self.system_prompt:
            msgs.append({"role": "system", "content": self.system_prompt})

        user_content = self.instruction
        if self.input_text:
            user_content = f"{self.instruction}\n\nContext:\n{self.input_text}"

        msgs.append({"role": "user", "content": user_content})
        msgs.append({"role": "assistant", "content": self.output_text})
        return {"messages": msgs}


class DatasetSynthesizer:
    """
    Traverses World Bibles and manuscripts to synthesize multi-domain instruction tuning datasets.
    """

    def __init__(self, target_dir: Path | str) -> None:
        self.target_dir = Path(target_dir).resolve()
        self.examples: list[InstructionExample] = []

    def scan_and_synthesize(self) -> int:
        """Executes full repository discovery and instruction generation."""
        self.examples = []
        if not self.target_dir.exists():
            raise FileNotFoundError(f"Target directory not found: {self.target_dir}")

        md_files: list[Path] = []
        if self.target_dir.is_file() and self.target_dir.suffix.lower() == ".md":
            md_files.append(self.target_dir)
        else:
            for p in sorted(self.target_dir.rglob("*.md")):
                if p.name.startswith((".", "_")) or "Backups" in p.parts:
                    continue
                md_files.append(p)

        for f in md_files:
            content = f.read_text(encoding="utf-8", errors="replace")
            fm = parse_yaml_frontmatter(content)
            body = re.sub(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", "", content, flags=re.DOTALL)
            clean_body = clean_prose(body)

            # Determine entity or manuscript type
            etype = str(fm.get("type", "")).lower()
            category = str(fm.get("category", "")).lower()
            name = str(fm.get("name", fm.get("title", f.stem.replace("_", " "))))

            # 1. Character Persona Generation
            if etype in ("character", "person", "npc") or "character" in category or "Characters" in f.parts:
                self._synthesize_character_persona(name, fm, clean_body, str(f))

            # 2. Magic System & Arcane Rules Generation
            elif etype in ("magicsystem", "magic", "spell") or "magic" in category or "MagicSystems" in f.parts:
                self._synthesize_magic_rules(name, fm, clean_body, str(f))

            # 3. Lore & Worldbuilding Inquisitor Generation
            elif etype in ("location", "faction", "religion", "history", "item", "artifact") or "World" in str(f):
                self._synthesize_lore_qa(name, fm, clean_body, str(f))

            # 4. Manuscript Prose Continuation Generation
            if "Manuscript" in f.parts or "Drafts" in f.parts or "Chapters" in f.parts or "01_Chapter" in f.name:
                self._synthesize_prose_continuation(name, clean_body, str(f))

        return len(self.examples)

    def _synthesize_character_persona(self, name: str, fm: dict[str, Any], body: str, source: str) -> None:
        """Synthesizes roleplay dialogue and character profile instructions."""
        system_prompt = f"You are roleplaying as {name}, a character in the Ars Arcanum universe. Maintain their voice, tone, knowledge, and convictions."
        aliases = fm.get("aliases", [])
        if isinstance(aliases, str):
            aliases = [aliases]
        traits = fm.get("traits", fm.get("personality", ""))
        faction = fm.get("faction", fm.get("allegiance", ""))

        # 1. Biography & identity summary
        if body.strip():
            first_para = body.strip().split("\n\n")[0]
            if len(first_para.split()) >= 15:
                self.examples.append(InstructionExample(
                    category="persona",
                    system_prompt=system_prompt,
                    instruction=f"Describe your background and allegiance in your own words, {name}.",
                    input_text="",
                    output_text=first_para,
                    source_doc=source,
                    metadata={"character": name, "faction": faction},
                ))

        # 2. Philosophical convictions & traits
        if traits:
            self.examples.append(InstructionExample(
                category="persona",
                system_prompt=system_prompt,
                instruction=f"What principles or personal traits define how you navigate conflict, {name}?",
                input_text="",
                output_text=f"I am defined by {traits}. In all things, I remain loyal to {faction or 'my own creed'}.",
                source_doc=source,
                metadata={"character": name},
            ))

        # 3. Fact checking about aliases
        if aliases:
            alias_str = ", ".join(str(a) for a in aliases)
            self.examples.append(InstructionExample(
                category="lore",
                system_prompt="You are the Ars Arcanum Canon Chronicler.",
                instruction=f"What other names or titles is {name} known by?",
                input_text="",
                output_text=f"{name} is canonically known by the following titles and aliases: {alias_str}.",
                source_doc=source,
                metadata={"character": name},
            ))

    def _synthesize_lore_qa(self, name: str, fm: dict[str, Any], body: str, source: str) -> None:
        """Synthesizes factual worldbuilding Q&A pairs from sections and frontmatter."""
        system_prompt = "You are the Ars Arcanum Lore Inquisitor. Answer questions accurately based on canonical lore records."

        sections = re.split(r"^#{1,3}\s+", body, flags=re.MULTILINE)
        for sec in sections:
            sec = sec.strip()
            if not sec:
                continue
            lines = sec.splitlines()
            header = lines[0].strip()
            sec_body = "\n".join(lines[1:]).strip()

            if len(sec_body.split()) >= 15:
                self.examples.append(InstructionExample(
                    category="lore",
                    system_prompt=system_prompt,
                    instruction=f"What is the canonical lore regarding '{header}' in the context of {name}?",
                    input_text="",
                    output_text=sec_body,
                    source_doc=source,
                    metadata={"topic": name, "section": header},
                ))

    def _synthesize_magic_rules(self, name: str, fm: dict[str, Any], body: str, source: str) -> None:
        """Synthesizes hard magic system constraints, costs, and casting limitations."""
        system_prompt = "You are the Ars Arcanum Arcane Inquisitor. Enforce strict magic system constraints and costs."

        cost = fm.get("cost", fm.get("drawback", ""))
        source_power = fm.get("source", fm.get("reagent", ""))

        if body.strip():
            self.examples.append(InstructionExample(
                category="magic",
                system_prompt=system_prompt,
                instruction=f"Explain the governing principles and casting mechanics of {name}.",
                input_text="",
                output_text=body.strip(),
                source_doc=source,
                metadata={"magic_system": name},
            ))

        if cost:
            self.examples.append(InstructionExample(
                category="magic",
                system_prompt=system_prompt,
                instruction=f"What are the physical costs, risks, and failure states when channeling {name}?",
                input_text="",
                output_text=f"Channeling {name} incurs the following costs and consequences: {cost}. Power originates from {source_power or 'atmospheric aether'}.",
                source_doc=source,
                metadata={"magic_system": name},
            ))

    def _synthesize_prose_continuation(self, title: str, body: str, source: str) -> None:
        """Synthesizes scene continuation and narrative voice pairs from manuscripts."""
        system_prompt = "You are a speculative fiction author drafting the next scene continuation in the author's narrative voice."

        paragraphs = [p.strip() for p in body.split("\n\n") if len(p.strip().split()) >= 20]
        # Pair adjacent paragraphs (Prompt paragraph -> Completion paragraph)
        for i in range(len(paragraphs) - 1):
            prompt_para = paragraphs[i]
            target_para = paragraphs[i + 1]

            self.examples.append(InstructionExample(
                category="prose",
                system_prompt=system_prompt,
                instruction=f"Continue the narrative scene from '{title}', maintaining atmospheric prose rhythm and pacing.",
                input_text=prompt_para,
                output_text=target_para,
                source_doc=source,
                metadata={"chapter": title, "scene_idx": i},
            ))


# ==============================================================================
# Export & Modelfile Generation Modules
# ==============================================================================

def generate_ollama_modelfile(
    model_base: str = "llama3:8b",
    system_prompt: str | None = None,
    temperature: float = 0.7,
    top_p: float = 0.9,
    repeat_penalty: float = 1.15,
) -> str:
    """Generates an Ollama Modelfile tailored for Ars Arcanum creative lore assistance."""
    default_system = (
        "You are the Ars Arcanum Sovereign Creative Intelligence, an offline authoring assistant\n"
        "grounded in the speculative canon, hard magic constraints, and character voices of\n"
        "the author's sovereign universe. Maintain atmospheric prose and zero cloud telemetry."
    )
    sys_str = system_prompt or default_system

    lines = [
        f"FROM {model_base}",
        "",
        "# Runtime Inference Parameters",
        f"PARAMETER temperature {temperature}",
        f"PARAMETER top_p {top_p}",
        f"PARAMETER repeat_penalty {repeat_penalty}",
        "PARAMETER stop \"<|end_of_text|>\"",
        "PARAMETER stop \"<|eot_id|>\"",
        "PARAMETER stop \"<|im_end|>\"",
        "",
        "# Canonical Sovereign System Instructions",
        "SYSTEM \"\"\"",
        sys_str.strip(),
        "\"\"\"",
        "",
        "# Template definition for ChatML / Llama 3 formatting",
        "TEMPLATE \"\"\"{{ if .System }}<|im_start|>system",
        "{{ .System }}<|im_end|>",
        "{{ end }}{{ if .Prompt }}<|im_start|>user",
        "{{ .Prompt }}<|im_end|>",
        "{{ end }}<|im_start|>assistant",
        "{{ .Response }}<|im_end|>\"\"\"",
    ]
    return "\n".join(lines)


def export_fine_tuning_dataset(
    examples: list[InstructionExample],
    output_dir: Path | str,
    output_format: str = "alpaca",
    val_split: float = 0.1,
    generate_modelfile: bool = True,
    seed: int = 42,
) -> dict[str, Any]:
    """
    Exports synthesized instruction examples to JSONL training/validation splits.
    Returns export summary dictionary.
    """
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Deterministic train/validation split
    shuffled = list(examples)
    rng = random.Random(seed)
    rng.shuffle(shuffled)

    val_count = int(len(shuffled) * val_split)
    val_examples = shuffled[:val_count]
    train_examples = shuffled[val_count:]

    def format_item(ex: InstructionExample) -> dict[str, Any]:
        if output_format == "alpaca":
            return ex.to_alpaca()
        elif output_format == "sharegpt":
            return ex.to_sharegpt()
        elif output_format in ("chatml", "openai"):
            return ex.to_chatml()
        return ex.to_alpaca()

    train_file = out_dir / "train.jsonl"
    val_file = out_dir / "val.jsonl"

    train_lines = [json.dumps(format_item(ex), ensure_ascii=False) for ex in train_examples]
    val_lines = [json.dumps(format_item(ex), ensure_ascii=False) for ex in val_examples]

    atomic_write(train_file, "\n".join(train_lines) + ("\n" if train_lines else ""))
    atomic_write(val_file, "\n".join(val_lines) + ("\n" if val_lines else ""))

    # Optional Modelfile
    modelfile_path = None
    if generate_modelfile:
        modelfile_path = out_dir / "Modelfile"
        atomic_write(modelfile_path, generate_ollama_modelfile())

    # Metadata Manifest
    categories: dict[str, int] = {}
    for ex in examples:
        categories[ex.category] = categories.get(ex.category, 0) + 1

    summary = {
        "dataset_name": "Ars Arcanum Sovereign Fine-Tuning Dataset",
        "format": output_format,
        "total_examples": len(examples),
        "train_count": len(train_examples),
        "val_count": len(val_examples),
        "val_split_ratio": val_split,
        "category_distribution": categories,
        "train_file": str(train_file),
        "val_file": str(val_file),
        "modelfile": str(modelfile_path) if modelfile_path else None,
    }

    manifest_file = out_dir / "dataset_manifest.json"
    atomic_write(manifest_file, json.dumps(summary, indent=2))

    return summary


# ==============================================================================
# CLI Entry Point
# ==============================================================================

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="arcanum train-data",
        description="Sovereign Local AI Fine-Tuning Dataset Synthesizer",
    )
    parser.add_argument("target", help="Path to World Bible vault or manuscript directory")
    parser.add_argument(
        "-f", "--format",
        choices=["alpaca", "sharegpt", "chatml", "openai"],
        default="alpaca",
        help="Fine-tuning dataset schema format (default: alpaca)",
    )
    parser.add_argument(
        "-o", "--output",
        default="dist/fine_tuning",
        help="Target output directory for dataset JSONL files (default: dist/fine_tuning)",
    )
    parser.add_argument(
        "-s", "--split",
        type=float,
        default=0.1,
        help="Validation split ratio between 0.0 and 0.5 (default: 0.1)",
    )
    parser.add_argument(
        "--no-modelfile",
        action="store_true",
        help="Skip generating Ollama Modelfile",
    )

    args = parser.parse_args(argv)

    target_path = Path(args.target).resolve()
    if not target_path.exists():
        print(f"Error: Target path '{target_path}' not found.", file=sys.stderr)
        return 1

    synthesizer = DatasetSynthesizer(target_path)
    count = synthesizer.scan_and_synthesize()

    if count == 0:
        print("Warning: No instruction examples could be synthesized from target path.", file=sys.stderr)
        return 0

    summary = export_fine_tuning_dataset(
        examples=synthesizer.examples,
        output_dir=args.output,
        output_format=args.format,
        val_split=args.split,
        generate_modelfile=not args.no_modelfile,
    )

    print(f"✓ Synthesized {summary['total_examples']} instruction examples for fine-tuning:")
    print(f"  - Training Set:   {summary['train_count']} examples -> {summary['train_file']}")
    print(f"  - Validation Set: {summary['val_count']} examples -> {summary['val_file']}")
    if summary["modelfile"]:
        print(f"  - Ollama Profile: {summary['modelfile']}")
    print(f"  - Category Breakdown: {summary['category_distribution']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
