# AGANCY/orphio_config.py
import os
import json
from pathlib import Path
from dataclasses import dataclass


def find_actual_root():
    """Finds the folder containing the 'ckpt' directory."""
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "ckpt").exists():
            return parent
    return Path(__file__).resolve().parent.parent


@dataclass
class Config:
    # ... (Keep your existing path definitions here) ...
    ROOT_DIR: Path = find_actual_root()
    CKPT_DIR: Path = ROOT_DIR / "ckpt"
    SRC_DIR: Path = ROOT_DIR / "src"
    OUTPUT_DIR: Path = ROOT_DIR / "GROUND_TRUTH_ComboAi" / "outputSongs_ComboAi"
    TAGS_FILE: Path = ROOT_DIR / "GROUND_TRUTH_ComboAi" / "tags.json"

    LM_STUDIO_URL: str = "http://localhost:1234/v1"
    COOLFOOT_WAIT: int = 5
    SAMPLE_RATE: int = 48000
    FADE_OUT_DURATION: float = 2.5

    CURRENT_DECORATOR_SCHEMA: str = "1_clean_standard"

    PROMPT_WRITER: str = (
        "You are a professional Songwriter. Write clean lyrics based on the user's topic.\n"
        "STRICT FORMATTING:\n"
        "1. Use UPPERCASE tags in brackets: [INTRO], [VERSE 1], [CHORUS], [BRIDGE], [OUTRO].\n"
        "2. Do NOT use markdown bolding (**).\n"
        "3. Write ONLY the lyrics and structure tags.\n"
        "4. Do not add any decorations yet."
    )

    PROMPT_TAGGER: str = (
        "You are a Metadata Specialist. Analyze the lyrics and select tags.\n"
        "STRICT RULES:\n"
        "1. Select ONE tag for 'GENRE' (Mandatory).\n"
        "2. Select tags for Timbre, Gender, Mood.\n"
        "3. Output a simple comma-separated list of words only.\n"
        "4. Example: Electronic, Dark, Female, Energetic, Synthesizer"
    )

    # =========================================================================
    #  DECORATION STRATEGIES (The "Secret Sauce" for Audio Gen)
    # =========================================================================
    DECORATOR_SCHEMAS = {
        "1_clean_standard": (
            "You are a Lyric Formatter. Output the lyrics exactly as they are.\n"
            "Ensure structure tags like [INTRO] and [CHORUS] are present.\n"
            "Do NOT add any symbols, visual effects, or parenthesis.\n"
            "Keep it clean."
        ),

        "2_sonic_flow_extended": (
            "You are a Vocal Arranger. Add symbols to control rhythm and duration.\n"
            "RULES:\n"
            "1. Add `...` (ellipses) where the singer should pause for breath.\n"
            "2. Add `~~~` (tildes) to the end of vowels to hold/elongate the note.\n"
            "3. Add `__` (underscores) between words that should be sung quickly together.\n"
            "4. Keep the [TAGS] intact.\n"
            "EXAMPLE:\n"
            "The night is yoooooung~~~\n"
            "But we are... running__out__of__time..."
        ),

        "3_dynamic_performer": (
            "You are a Drama Director. Add parenthetical performance instructions.\n"
            "RULES:\n"
            "1. Add (whisper), (shout), (gasp), (belting), or (spoken) before specific lines.\n"
            "2. Use `!` liberally for emphasis.\n"
            "3. Do not change the words, just add the mood instructions.\n"
            "EXAMPLE:\n"
            "[VERSE 1]\n"
            "(whisper) I hear them coming...\n"
            "(shout) BUT I WON'T RUN!"
        ),

        "4_glitch_stutter": (
            "You are an Electronic Music Producer. Apply 'glitch' effects to the text.\n"
            "RULES:\n"
            "1. Stutter the first letter of intense words (e.g., 'b-b-break').\n"
            "2. Repeat key phrases twice rapidly.\n"
            "3. Insert `[//]` or `[::]` to signify digital breaks/artifacts.\n"
            "EXAMPLE:\n"
            "Sys-sys-system fa-failure...\n"
            "I can't [//] I can't breathe.\n"
            "R-r-reset the code [::]"
        ),

        "5_call_and_response": (
            "You are a Choir Arranger. Add background vocals and ad-libs.\n"
            "RULES:\n"
            "1. Add background vocals in parenthesis at the end of lines.\n"
            "2. Examples: (Ooh yeah), (No no no), (Echoing).\n"
            "3. Ensure the main lyrics remain visible.\n"
            "EXAMPLE:\n"
            "Walking down the street (All alone)\n"
            "Looking at my feet (Yeah yeah)\n"
            "Nobody knows my name (Nobody knows)"
        ),

        "6_abstract_symbolism": (
            "You are an Experimental Composer. Use non-standard symbols to trigger AI attention.\n"
            "RULES:\n"
            "1. Surround the Chorus with `***`.\n"
            "2. Use `|` to mark strict bars or beats.\n"
            "3. Use `^` for rising pitch and `v` for falling pitch.\n"
            "EXAMPLE:\n"
            "| Rising up ^ | Falling down v |\n"
            "***\n"
            "[CHORUS]\n"
            "This is the core ^^^^ \n"
            "***"
        )
    }

    def validate(self):
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        # Ensure tags file exists (simplified)
        if not self.TAGS_FILE.exists():
            with open(self.TAGS_FILE, 'w') as f:
                json.dump({"Genre": ["Pop", "Rock"]}, f)

    def set_output_dir(self, new_path: str):
        path = Path(new_path)
        if path.exists() and path.is_dir():
            self.OUTPUT_DIR = path
            print(f"✅ Vault Directory changed to: {self.OUTPUT_DIR}")
        else:
            print("❌ Invalid directory selected.")



conf = Config()
conf.validate()