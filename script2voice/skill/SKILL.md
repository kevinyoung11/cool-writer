---
name: script2voice-cosyvoice
description: Convert a Chinese video script or口播稿 into complete audio using the local CosyVoice install. Use when the user wants script-to-voice, AI配音, 分段演绎, CosyVoice批量生成, or a final stitched wav/mp3 from a plain script.
---

# Script To Voice With CosyVoice

Use this project-local skill to turn a normal Markdown or text script into a complete voiceover audio file. Keep all created artifacts under `/Users/apulu/Documents/yy-article/script2voice`.

## Workflow

1. **Prepare input**
   - Accept `.md` or `.txt`.
   - Prefer the main口播正文; ignore title metadata, code blocks, prompt appendices, and production notes when obvious.
   - For B站口播, keep the language conversational and preserve useful punchlines.

2. **Segment**
   - Run `scripts/prepare_segments.py`.
   - Split into 10-20 second chunks, usually 45-95 Chinese characters.
   - Output a run folder:
     - `runs/<name>/cleaned_script.txt`
     - `runs/<name>/segments.json`
     - `runs/<name>/segments/seg_001.txt`
     - `runs/<name>/manifest.tsv`

3. **Synthesize**
   - Run `scripts/run_pipeline.py --input <script> --name <run-name>`.
   - The pipeline calls the local CosyVoice Python from `config/defaults.json`.
   - Per-segment wavs go to `runs/<name>/audio/parts/`.

4. **Assemble**
   - The pipeline joins wav chunks with short silence gaps.
   - Final files:
     - `runs/<name>/audio/final.wav`
     - `runs/<name>/audio/final.mp3`

5. **Review**
   - Listen for flat delivery, wrong pauses, clipped starts/ends, and misread English terms.
   - If needed, edit `segments.json` or individual `segments/seg_*.txt`, then rerun synthesis.

## Commands

Dry-run segmentation only:

```bash
python3 /Users/apulu/Documents/yy-article/script2voice/scripts/run_pipeline.py \
  --input /path/to/script.md \
  --name test-run \
  --dry-run
```

Generate full audio:

```bash
python3 /Users/apulu/Documents/yy-article/script2voice/scripts/run_pipeline.py \
  --input /path/to/script.md \
  --name vibe-coding-5min
```

Regenerate only selected segments:

```bash
python3 /Users/apulu/Documents/yy-article/script2voice/scripts/synthesize_cosyvoice.py \
  --run-dir /Users/apulu/Documents/yy-article/script2voice/runs/vibe-coding-5min \
  --only 3,4,5
```

## Quality Rules

- Do not synthesize a full script as one block.
- Keep chunk text natural; remove markdown syntax before TTS.
- Do not put private keys or unrelated project files in the run folder.
- Prefer several short retries for bad segments instead of regenerating the whole script.
- If a voice prompt is provided by the user, use only authorized self-owned or licensed voices.
