
from game import GameManager
from loader import Loader
from saver import Saver

def main():
    # --- Config ---
    GAME_TO_LOAD = "kero_blaster" # or "cave_story"
    STAGE_NAME = "00boot-test"
    GAME_PATH = "/home/god/Documents/pxEditKeroTest/Kero Blaster" # Adjust as needed

    # --- Setup ---
    game_manager = GameManager()
    
    # --- Game Selection ---
    try:
        game_manager.set_game(GAME_TO_LOAD)
    except ValueError as e:
        print(e)
        return

    # --- Path Selection ---
    game_manager.set_game_path(GAME_PATH)

    print(f"Initialized for game: {game_manager.get_current_game().name}")
    print(f"Game data path: {GAME_PATH}")

    # --- Data Loading ---
    loader = Loader(game_manager)
    
    # Example of loading a stage
    try:
        stage = loader.load_stage(STAGE_NAME)
        print(f"Successfully loaded stage: {stage.name}")
    except (ValueError, FileNotFoundError) as e:
        print(f"Error loading stage: {e}")
        stage = None


    # --- Data Saving ---
    saver = Saver(game_manager)
    if stage:
        stage.name = '00boot-test'
        saver.save_stage(stage)

if __name__ == "__main__":
    main()

