from typing import List, Literal, Optional, Tuple

from pydantic import BaseModel, Field, validator

BOARD_SIZE = 12
WIN_LENGTH = 5
Player = Literal["X", "O"]
CellValue = Literal["X", "O", " "]


class GameState(BaseModel):
    """Pydantic model to hold the state of the Tic Tac Toe game."""

    board: List[List[CellValue]] = Field(
        default_factory=lambda: [
            [" " for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)
        ],
    )
    current_player: Player = "X"
    winner: Optional[Player] = None
    game_over: bool = False

    @validator("board")
    def check_board_dimensions(cls, board):
        if len(board) != BOARD_SIZE:
            raise ValueError(f"Board must have {BOARD_SIZE} rows")
        if not all(len(row) == BOARD_SIZE for row in board):
            raise ValueError(f"Each row must have {BOARD_SIZE} columns")
        return board


class TicTacToeGame:
    def __init__(self):
        self.board_size = BOARD_SIZE
        self.win_length = WIN_LENGTH
        self.state = GameState()  # Initialize with default state

    def reset(self):
        """Resets the game to the initial state by creating a new GameState."""
        self.state = GameState()
        return self.get_state_tuple()  # Return initial state tuple

    def get_state_tuple(self) -> Tuple[str, ...]:
        """Returns a hashable tuple representation of the current board state."""
        return tuple("".join(row) for row in self.state.board)

    def get_board_list(self) -> List[List[CellValue]]:
        """Returns the board as a mutable list of lists (e.g., for Pygame drawing)."""
        # Return a copy to prevent external modification of the Pydantic state directly
        return [row[:] for row in self.state.board]

    def get_current_player(self) -> Player:
        return self.state.current_player

    def is_game_over(self) -> bool:
        return self.state.game_over

    def get_winner(self) -> Optional[Player]:
        return self.state.winner

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Returns a list of valid moves as (row, col) tuples."""
        moves = []
        if not self.state.game_over:
            for r in range(self.board_size):
                for c in range(self.board_size):
                    if self.state.board[r][c] == " ":
                        moves.append((r, c))
        return moves

    def is_valid_move(self, row: int, col: int) -> bool:
        """Checks if a move is valid (within bounds and on an empty square)."""
        return (
            0 <= row < self.board_size
            and 0 <= col < self.board_size
            and self.state.board[row][col] == " "
        )

    def make_move(self, row: int, col: int) -> bool:
        """
        Attempts to make a move for the current player.
        Updates the game state (board, current_player, game_over, winner).
        Returns True if the move was successful, False otherwise.
        """
        if self.state.game_over or not self.is_valid_move(row, col):
            return False  # Move is invalid or game already finished

        # Directly modify the list within the Pydantic model
        self.state.board[row][col] = self.state.current_player

        # Check for win
        if self._check_win(self.state.current_player):
            self.state.winner = self.state.current_player
            self.state.game_over = True
            return True  # Move successful, game ended in a win

        # Check for draw
        if self._is_board_full():
            self.state.winner = None  # Draw
            self.state.game_over = True
            return True  # Move successful, game ended in a draw

        # Game continues, switch player
        self.state.current_player = "O" if self.state.current_player == "X" else "X"
        return True  # Move successful, game continues

    def _check_win(self, player: Player) -> bool:
        """Internal method to check if the specified player has won."""
        board = self.state.board
        # Check horizontal
        for r in range(self.board_size):
            for c in range(self.board_size - self.win_length + 1):
                if all(board[r][c + i] == player for i in range(self.win_length)):
                    return True
        # Check vertical
        for r in range(self.board_size - self.win_length + 1):
            for c in range(self.board_size):
                if all(board[r + i][c] == player for i in range(self.win_length)):
                    return True
        # Check positive diagonal
        for r in range(self.board_size - self.win_length + 1):
            for c in range(self.board_size - self.win_length + 1):
                if all(board[r + i][c + i] == player for i in range(self.win_length)):
                    return True
        # Check negative diagonal
        for r in range(self.board_size - self.win_length + 1):
            for c in range(self.win_length - 1, self.board_size):
                if all(board[r + i][c - i] == player for i in range(self.win_length)):
                    return True
        return False

    def _is_board_full(self) -> bool:
        """Internal method to check if the board is full."""
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.state.board[r][c] == " ":
                    return False
        return True

    # Helper specifically for the Pygame version to get line coords for drawing
    def get_winning_line_coords(
        self,
    ) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Checks for a win and returns (start_pos, end_pos) if found, else None."""
        if not self.state.winner:
            return None

        player = self.state.winner
        board = self.state.board
        # Check horizontal
        for r in range(self.board_size):
            for c in range(self.board_size - self.win_length + 1):
                if all(board[r][c + i] == player for i in range(self.win_length)):
                    return (r, c), (r, c + self.win_length - 1)
        # Check vertical
        for r in range(self.board_size - self.win_length + 1):
            for c in range(self.board_size):
                if all(board[r + i][c] == player for i in range(self.win_length)):
                    return (r, c), (r + self.win_length - 1, c)
        # Check positive diagonal
        for r in range(self.board_size - self.win_length + 1):
            for c in range(self.board_size - self.win_length + 1):
                if all(board[r + i][c + i] == player for i in range(self.win_length)):
                    return (r, c), (r + self.win_length - 1, c + self.win_length - 1)
        # Check negative diagonal
        for r in range(self.board_size - self.win_length + 1):
            for c in range(self.win_length - 1, self.board_size):
                if all(board[r + i][c - i] == player for i in range(self.win_length)):
                    return (r, c), (r + self.win_length - 1, c - self.win_length + 1)
        return None  # Should not happen if self.winner is set correctly
