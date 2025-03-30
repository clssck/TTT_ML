import random
from typing import Tuple, Optional
from game_logic import TicTacToeGame # Import the game logic class

class RandomAIPlayer:
    """An AI player that chooses a random valid move."""

    def __init__(self, player_symbol: str):
        """
        Initializes the AI player.
        Args:
            player_symbol (str): The symbol this AI uses ('X' or 'O').
        """
        self.player_symbol = player_symbol
        print(f"Random AI initialized as Player {player_symbol}")

    def get_move(self, game: TicTacToeGame) -> Optional[Tuple[int, int]]:
        """
        Chooses a random valid move from the available moves.
        Args:
            game (TicTacToeGame): The current game state object.
        Returns:
            Optional[Tuple[int, int]]: A tuple (row, col) representing the chosen move,
                                       or None if no valid moves are available (should not happen if called correctly).
        """
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None # No moves left

        chosen_move = random.choice(valid_moves)
        # print(f"AI ({self.player_symbol}) chose move: {chosen_move}") # Optional debug print
        return chosen_move
