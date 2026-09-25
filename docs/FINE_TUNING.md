# Sovereign Local AI Fine-Tuning & Dataset Synthesizer
> **Ars Arcanum Module**: `scripts/lib/fine_tuning.py` | **CLI**: `arcanum train-data` (alias: `lora-dataset`)

---

## 1. Executive Summary & Sovereignty Guarantees

The **Ars Arcanum Local AI Fine-Tuning Synthesizer** transforms unpublished World Bibles, character sheets, and manuscripts into high-quality instruction tuning datasets for local LLMs (Llama 3, Mistral, Gemma, Phi) without sending private intellectual property to third-party cloud platforms.

### Core Guarantees
- **100% Offline Privacy**: Zero telemetry, zero cloud dependencies.
- **Multi-Format Instruction Schemas**: Exports directly to **Alpaca**, **ShareGPT**, **ChatML**, and **Ollama Modelfiles**.
- **Craft-Specific Dataset Synthesis**:
  - `persona`: Roleplay instructions grounded in character speech patterns, allegiances, and personality traits.
  - `lore`: Canonical worldbuilding Q&A pairs from headings, wikilinks, and taxonomy notes.
  - `prose`: Scene continuation pairs capturing authorial rhythm and voice.
  - `magic`: Hard magic system constraint enforcement and paradox mitigation.

---

## 2. CLI Usage Reference

### 2.1 Generating Fine-Tuning Datasets
```bash
# Generate Alpaca-format dataset from an Obsidian world vault
arcanum train-data ~/Universes/Cosmos/Worlds/Eldoria/ -f alpaca -o dist/lora_dataset/

# Generate ShareGPT multi-turn dataset with 15% validation split
arcanum train-data ~/Manuscript/ -f sharegpt -s 0.15 -o dist/sharegpt_dataset/

# Generate ChatML dataset without generating an Ollama Modelfile
arcanum train-data ~/Universes/Cosmos/ -f chatml --no-modelfile
```

### 2.2 Dataset Schema Formats

| Format | Flag | Structure | Compatible Frameworks |
| :--- | :--- | :--- | :--- |
| **Alpaca** | `-f alpaca` *(default)* | `{"instruction": "...", "input": "...", "output": "..."}` | Unsloth, LLaMA-Factory, Alpaca-LoRA |
| **ShareGPT** | `-f sharegpt` | `{"conversations": [{"from": "human", ...}, {"from": "gpt", ...}]}` | Axolotl, FastChat, vLLM |
| **ChatML** | `-f chatml` | `{"messages": [{"role": "system", ...}, {"role": "user", ...}]}` | Hugging Face TRL, SFTTrainer |

---

## 3. Training with Local Tools (Unsloth / Ollama)

### 3.1 Custom Ollama Lore Model
The synthesizer generates a custom `Modelfile` in the output directory. You can create a specialized lore model with one command:

```bash
cd dist/lora_dataset
ollama create my-lore-assistant -f Modelfile
ollama run my-lore-assistant "Who holds the Iron Scribe's ledger?"
```

### 3.2 Fine-Tuning with Unsloth / LoRA
Load `dist/lora_dataset/train.jsonl` and `val.jsonl` directly into your offline Unsloth or Axolotl training script:

```python
from datasets import load_dataset
dataset = load_dataset("json", data_files={"train": "dist/lora_dataset/train.jsonl", "validation": "dist/lora_dataset/val.jsonl"})
```
