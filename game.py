
import json

class Game:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.base_path = None

    def get(self, key, default=None):
        return self.config.get(key, default)

class GameManager:
    def __init__(self, config_path='game_config.json'):
        self.games = {}
        self.current_game = None
        self.load_games(config_path)

    def load_games(self, config_path):
        with open(config_path, 'r') as f:
            configs = json.load(f)
            for name, config in configs.items():
                self.games[name] = Game(name, config)

    def set_game(self, name):
        if name in self.games:
            self.current_game = self.games[name]
        else:
            raise ValueError(f"Game '{name}' not found in configuration.")

    def get_current_game(self):
        if not self.current_game:
            raise ValueError("No game has been set.")
        return self.current_game

    def set_game_path(self, path):
        if self.current_game:
            self.current_game.base_path = path
        else:
            raise ValueError("No game selected.")
