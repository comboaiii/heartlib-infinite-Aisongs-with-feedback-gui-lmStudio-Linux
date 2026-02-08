import json
import re
import time
from pathlib import Path
from colorama import Fore, Style, init

# IMPORT YOUR STACK
from orphio_config import conf
from lmstudio_controler import LMStudioController
from orphio_engine import OrphioEngine

init(autoreset=True)


class ProducerBlueprintEngine:
    def __init__(self):
        self.lms = LMStudioController(conf.LM_STUDIO_URL)
        self.engine = OrphioEngine(log_callback=print)

        # Absolute pathing to avoid "No blueprints found"
        self.strategies_path = Path(__file__).parent / "PRODUCER_STRATEGIES"
        self.strategies_path.mkdir(parents=True, exist_ok=True)

    def list_producers(self):
        """Returns a list of dictionaries containing producer info"""
        files = list(self.strategies_path.glob("*.json"))
        producers_data = []

        for f in files:
            try:
                # Specify encoding='utf-8' to handle Windows text issues
                with open(f, 'r', encoding='utf-8') as j:
                    data = json.load(j)
                    producers_data.append({
                        "path": f,
                        "name": data.get("name", f.name),
                        "desc": data.get("description", "Standard Strategy")
                    })
            except Exception as e:
                # If it's not a valid blueprint, skip it
                print(f"{Fore.RED}⚠️ Skipped invalid strategy file: {f.name} ({e})")
                continue
        return producers_data

    def load_blueprint(self, filepath):
        """Loads the JSON strategy into memory"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _extract_json_from_response(self, text):
        """
        Robustly extracts JSON object from LLM response.
        """
        # 1. Attempt strict clean
        try:
            clean_text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except json.JSONDecodeError:
            pass

        # 2. Regex Search
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                json_candidate = match.group(0)
                return json.loads(json_candidate)
        except (AttributeError, json.JSONDecodeError):
            pass

        return None

    def execute_album(self, blueprint, user_topic, user_duration=120, user_track_count=None):
        """
        Executes the album generation.
        :param user_duration: Length of songs in seconds.
        :param user_track_count: Override the blueprint's default track count.
        """
        print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════╗")
        print(f"{Fore.CYAN}║  🧢 ACTIVE PRODUCER: {blueprint['name'].upper()}")
        print(f"{Fore.CYAN}║  📜 STRATEGY: {blueprint['propagation_logic']['type']}")
        print(f"{Fore.CYAN}╚════════════════════════════════════════════════╝")

        # 1. DETERMINE TRACK COUNT
        # If user provided a count, override the blueprint
        target_count = blueprint['executive_strategy'].get('track_count', 3)
        if user_track_count and user_track_count > 0:
            target_count = user_track_count
            print(
                f"{Fore.YELLOW}🔧 OVERRIDE: Producing {target_count} tracks (Blueprint default was {blueprint['executive_strategy'].get('track_count')})")

        # --- PRINT FULL PRODUCER SCHEMA ---
        print(f"\n{Fore.LIGHTBLACK_EX}--- [PRODUCER BLUEPRINT SCHEMA] ---")
        print(f"{Fore.LIGHTBLACK_EX}{json.dumps(blueprint, indent=4)}")
        print(f"{Fore.LIGHTBLACK_EX}-----------------------------------")

        # 2. EXECUTIVE PHASE (Planning)
        print(f"\n{Fore.YELLOW}🧠 Planning Album Strategy...")

        # Construct prompt with EXPLICIT track count requirement
        exec_prompt = (
            f"{blueprint['executive_strategy']['system_prompt']}\n"
            f"USER REQUEST: {user_topic}\n"
            f"MANDATORY REQUIREMENT: Generate a tracklist with exactly {target_count} songs.\n"
            "OUTPUT FORMAT: Return ONLY a valid JSON object with 'album_title', 'album_theme', and 'tracklist' (array).\n"
            "Do not include conversational text."
        )

        # Call LLM
        plan_raw = self.lms.chat(exec_prompt, "Generate the plan.")
        plan = self._extract_json_from_response(plan_raw)

        if not plan:
            print(f"{Fore.RED}❌ Executive Producer failed to output valid JSON.")
            print(f"{Fore.LIGHTBLACK_EX}Raw Output:\n{plan_raw}")
            return

        # Double check if the LLM respected the count (optional warning)
        generated_count = len(plan.get('tracklist', []))
        if generated_count != target_count:
            print(
                f"{Fore.MAGENTA}⚠️  Producer generated {generated_count} tracks instead of {target_count}. Proceeding with generated list.")

        # --- PRINT FULL ALBUM PLAN ---
        print(f"\n{Fore.CYAN}--- [GENERATED ALBUM MANIFEST] ---")
        print(f"{Fore.CYAN}{json.dumps(plan, indent=4)}")
        print(f"{Fore.CYAN}----------------------------------")

        # Setup Album Folder
        safe_album_title = "".join(
            [c for c in plan.get('album_title', 'Untitled') if c.isalnum() or c in " _-"]).strip().replace(" ", "_")
        album_dir = conf.OUTPUT_DIR / f"ALBUM_{safe_album_title}"
        album_dir.mkdir(parents=True, exist_ok=True)

        print(f"{Fore.GREEN}✅ Plan Accepted. Starting Production Loop...")

        # 3. PRODUCTION LOOP
        context_history = []
        track_list = plan.get('tracklist', [])

        for i, track in enumerate(track_list):
            t_title = track.get('title', f"Track {i + 1}")
            t_desc = track.get('description', track.get('plot_point', track.get('hook_concept', '')))
            t_mood = track.get('mood', track.get('energy_level', track.get('atmosphere', '')))

            print(f"\n{Fore.MAGENTA}▶ TRACK {i + 1}/{len(track_list)}: {t_title}")
            print(f"{Fore.MAGENTA}  ⏱️ Duration: {user_duration}s")

            # --- DYNAMIC PROMPT CONSTRUCTION ---
            template = blueprint['propagation_logic']['lyric_instruction_template']
            prev_context = context_history[-1]['summary'] if context_history else "None (First Track)"
            prev_mood = context_history[-1]['mood'] if context_history else "Neutral"

            try:
                smart_prompt = template.replace("{prev_context}", prev_context) \
                    .replace("{track_title}", t_title) \
                    .replace("{track_description}", t_desc) \
                    .replace("{album_theme}", plan.get('album_theme', '')) \
                    .replace("{album_title}", plan.get('album_title', 'Untitled')) \
                    .replace("{prev_mood}", prev_mood) \
                    .replace("{track_mood}", t_mood)
            except Exception:
                smart_prompt = f"Topic: {t_title}"

            print(f"{Fore.WHITE}   📝 PROMPT SENT TO LYRICIST:\n   \"{smart_prompt}\"")

            # Write Lyrics & Tags
            lyrics = self.lms.chat(conf.PROMPT_WRITER, smart_prompt)
            lyrics = self.engine._enforce_tag_schema(lyrics)
            tags_raw = self.lms.chat(conf.PROMPT_TAGGER, lyrics, temp=0.2)
            tags = self.engine._clean_tags_list(tags_raw)
            print(f"{Fore.LIGHTBLUE_EX}   🏷️  TAGS: {tags}")

            # Render Audio
            try:
                wav_path, _ = self.engine.render_audio_stage(
                    topic=t_title,
                    lyrics=lyrics,
                    tags=tags,
                    duration_s=user_duration,
                    cfg=1.5,
                    temp=1.0
                )

                # Move files
                final_filename = f"{i + 1:02d}_{t_title.replace(' ', '_')}.wav"
                final_filename = "".join([c for c in final_filename if c.isalnum() or c in " ._-"])
                final_path = album_dir / final_filename
                Path(wav_path).rename(final_path)

                json_src = Path(wav_path).with_suffix('.json')
                if json_src.exists():
                    json_src.rename(final_path.with_suffix('.json'))

                # Update History
                context_history.append({
                    "title": t_title,
                    "summary": lyrics[:50] + "...",
                    "mood": t_mood
                })

            except Exception as e:
                print(f"{Fore.RED}❌ Audio Error: {e}")

            self.engine.free_memory()
            time.sleep(2)

        print(f"\n{Fore.GREEN}✅ Production Complete using blueprint: {blueprint['name']}")


if __name__ == "__main__":
    system = ProducerBlueprintEngine()
    blueprints = system.list_producers()

    if not blueprints:
        print(f"{Fore.RED}No blueprints found in AGANCY/PRODUCER_STRATEGIES/")
    else:
        print(f"\n{Fore.WHITE}Available Producers:")
        for idx, bp in enumerate(blueprints):
            print(f"[{idx + 1}] {bp['name']}")

        try:
            selection = int(input("\nSelect Producer (Number): ")) - 1
            selected_bp_path = blueprints[selection]['path']
            bp_data = system.load_blueprint(selected_bp_path)

            topic = input("Enter Album Idea: ")

            d_in = input("Duration (sec, default 120): ")
            dur = int(d_in) if d_in.strip() else 120

            c_in = input("Track Count (default: blueprint): ")
            count = int(c_in) if c_in.strip() else None

            system.execute_album(bp_data, topic, dur, count)
        except Exception as e:
            print(f"{Fore.RED}Error: {e}")