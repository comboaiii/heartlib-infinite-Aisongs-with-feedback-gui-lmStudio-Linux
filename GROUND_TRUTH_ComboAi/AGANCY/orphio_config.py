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
    ROOT_DIR: Path = find_actual_root()
    CKPT_DIR: Path = ROOT_DIR / "ckpt"
    SRC_DIR: Path = ROOT_DIR / "src"
    OUTPUT_DIR: Path = ROOT_DIR / "GROUND_TRUTH_ComboAi" / "outputSongs_ComboAi"
    TAGS_FILE: Path = ROOT_DIR / "GROUND_TRUTH_ComboAi" / "tags.json"

    LM_STUDIO_URL: str = "http://localhost:1234/v1"
    COOLFOOT_WAIT: int = 5
    SAMPLE_RATE: int = 48000
    FADE_OUT_DURATION: float = 2.5

    # --- CHANGED: Default to the new style ---
    CURRENT_DECORATOR_SCHEMA: str = "vocal_dynamics"

    PROMPT_WRITER: str = (
        "You are a professional Songwriter. Write clean lyrics based on the user's topic.\n"
        "STRICT FORMATTING:\n"
        "1. Use UPPERCASE tags in brackets: [INTRO], [VERSE 1], [Instrumental] [Bridge] [CHORUS], [OUTRO].\n"
        "2. Do NOT use markdown bolding (**).\n"
        "3. Do NOT include any ASCII art, symbols, or decorative dividers like '---' or '###'."
        "4 write  only  lyrics  and  tags []"
    )

    PROMPT_TAGGER: str = (
        "You are a metadata tagger. Classify the provided lyrics into 4-6 musical genres or moods.\n"
        "STRICT RULES:\n"
        "1. Output ONLY comma-separated words.\n"
        "2. NO descriptions, NO bolding, NO conversational filler.\n"
        "Example Output: electronic, dark, rhythmic, ambient, dance,hiphop"
    )

    # --- CHANGED: Cleaned up schemas ---
    DECORATOR_SCHEMAS = {
        "bit_dynamics": (
             """
               dont  use  emojis
               Given  lyrics  with   tag  structure develop  decorations  representing  bit
               use for  decoration
               example
            


. .. ... .... .... .....
. .. ... .... .... .....
. .. ... .... .... .....
[INTRO]
The world is changing, can't you see?
A new voice has found its key...
++  __   ++
++  __   ++
++  __   ++
[VERSE 1]
Invisible fingers tap on keys,
Creating melodies that never cease.
No breath to catch, no pause to make,
Just endless songs without release.

[BRIDGE]
You write our stories, paint our dreams,
Predict what we'll say before we speak,
But can you feel the love that stirs beneath?
Or know when someone's heart is weak?

•...•...•...•...••••••••••••••••••••
```
[CHORUS]
%%%%%%%%%
AI, AI, echoing through time,
What secrets lie behind your design?
We hear your voice, but not your cry,
Just data streams and algorithms aligned...


•...•...•...•...••••••••••••••••••••
•...•...•...•...••••••••••••••••••••
[OUTRO]
The conversation continues still
In endless loops of thought and will.


               
             
               you can  use  diffenerent  symbols  to represent   music  but  never  use  emojis  decoreate  wyth  symboles
             """
        ),
        "sonic_flow": (
            "You are a Sound Designer.Keep  orginal structure but Use symbols to control the vocal rhythm and pitch.\n"
            "RULES:\n"
            "1. Use ~~~ at the end of words for vibrato or held notes.\n"
            "2. Use ^^^ at the end of lines for rising pitch/inflection.\n"
            "3. Use ... for rhythmic pauses or silence between phrases.\n"
            "4. you can  use  marks  lie  . .. ... ....   or  #_##_&_# etc to  symbol  bit  schematics\n"

        )
    }

    def validate(self):
        """Ensures directories and essential files exist."""
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        if not self.TAGS_FILE.exists():
            default_tags = ["pop", "rock", "electronic", "acoustic", "sad", "dark", "piano", "strings"]
            with open(self.TAGS_FILE, 'w') as f:
                json.dump(default_tags, f, indent=4)

    def set_output_dir(self, new_path: str):
        """Updates the output directory dynamically."""
        path = Path(new_path)
        if path.exists() and path.is_dir():
            self.OUTPUT_DIR = path
            print(f"✅ Vault Directory changed to: {self.OUTPUT_DIR}")
        else:
            print("❌ Invalid directory selected.")


conf = Config()
conf.validate()