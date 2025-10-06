import importlib

class FormatManager:
    """
    A unified manager for loading and saving game stages.
    It dynamically imports the correct format handler based on game_config.json.
    """
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.handlers = {}

    def _get_handler(self):
        """
        Dynamically imports and returns the format handler module for the current game.
        """
        game = self.game_manager.get_current_game()
        handler_name = game.get('format_handler')
        
        if not handler_name:
            raise NotImplementedError(f"No 'format_handler' specified in game_config.json for game '{game.name}'.")

        # Import the handler module if it hasn't been imported yet
        if handler_name not in self.handlers:
            self.handlers[handler_name] = importlib.import_module(handler_name)
            
        return self.handlers[handler_name]

    def load_stage(self, stage_name):
        """
        Loads a stage by dispatching to the current game's format handler.
        """
        handler = self._get_handler()
        return handler.load_stage(self.game_manager, stage_name)

    def save_stage(self, stage):
        """
        Saves a stage by dispatching to the current game's format handler.
        """
        handler = self._get_handler()
        return handler.save_stage(self.game_manager, stage)
