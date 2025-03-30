import sys
import pygame
from game_logic import TicTacToeGame, BOARD_SIZE, WIN_LENGTH # Import the game logic
from ai_player import RandomAIPlayer # Import the AI player

# --- Constants ---
# BOARD_SIZE and WIN_LENGTH are now imported from game_logic
SQUARE_SIZE = 50  # Size of each square in pixels
MARGIN_TOP = 70  # Increased top margin for turn indicator
MARGIN_LEFT = 50  # Margin for row legends
MARGIN_BOTTOM = 50  # Margin for messages/reset info
MARGIN_RIGHT = 20
GRID_WIDTH = BOARD_SIZE * SQUARE_SIZE
GRID_HEIGHT = BOARD_SIZE * SQUARE_SIZE
WIDTH = GRID_WIDTH + MARGIN_LEFT + MARGIN_RIGHT
HEIGHT = GRID_HEIGHT + MARGIN_TOP + MARGIN_BOTTOM
CIRCLE_RADIUS = SQUARE_SIZE // 2 - 10
CROSS_WIDTH = 15
SPACE = SQUARE_SIZE // 4
ANIMATION_SPEED = 0.05  # Controls how fast the winning line draws

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LINE_COLOR = (200, 200, 200)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
BG_COLOR = (28, 170, 156)
MESSAGE_COLOR = (255, 255, 0)  # Yellow for messages
WIN_LINE_COLOR = (255, 0, 0)
LEGEND_COLOR = (200, 200, 255)  # Light blue for legends
TURN_COLOR = (255, 255, 255)  # White for turn indicator
HOVER_COLOR = (200, 200, 200, 100)  # Semi-transparent light grey for hover
BUTTON_COLOR = (0, 100, 200)
BUTTON_HOVER_COLOR = (0, 150, 255)
BUTTON_TEXT_COLOR = WHITE

# --- Game Setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(
    f"{WIN_LENGTH}-in-a-Row Tic Tac Toe ({BOARD_SIZE}x{BOARD_SIZE})",
)
font = pygame.font.Font(None, 40)  # For messages
legend_font = pygame.font.Font(None, 25)  # Smaller font for legends
turn_font = pygame.font.Font(None, 35)  # Font for turn indicator
button_font = pygame.font.Font(None, 50) # Font for mode selection buttons

# --- Drawing Functions ---

def draw_lines():
    # Draw grid lines offset by margins
    # Horizontal
    for i in range(BOARD_SIZE + 1):
        y = MARGIN_TOP + i * SQUARE_SIZE
        pygame.draw.line(screen, LINE_COLOR, (MARGIN_LEFT, y), (MARGIN_LEFT + GRID_WIDTH, y), 2 if i == 0 or i == BOARD_SIZE else 1)
    # Vertical
    for i in range(BOARD_SIZE + 1):
        x = MARGIN_LEFT + i * SQUARE_SIZE
        pygame.draw.line(screen, LINE_COLOR, (x, MARGIN_TOP), (x, MARGIN_TOP + GRID_HEIGHT), 2 if i == 0 or i == BOARD_SIZE else 1)

def draw_legends():
    # Draw column numbers (0-11) above the grid
    for i in range(BOARD_SIZE):
        text = legend_font.render(str(i), True, LEGEND_COLOR)
        text_rect = text.get_rect(center=(MARGIN_LEFT + i * SQUARE_SIZE + SQUARE_SIZE // 2, MARGIN_TOP - 20))
        screen.blit(text, text_rect)
    # Draw row numbers (0-11) left of the grid
    for i in range(BOARD_SIZE):
        text = legend_font.render(str(i), True, LEGEND_COLOR)
        text_rect = text.get_rect(center=(MARGIN_LEFT - 25, MARGIN_TOP + i * SQUARE_SIZE + SQUARE_SIZE // 2))
        screen.blit(text, text_rect)

def draw_figures(board): # Takes the board state as argument
    # Draw X's and O's offset by margins
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            center_x = MARGIN_LEFT + col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = MARGIN_TOP + row * SQUARE_SIZE + SQUARE_SIZE // 2
            if board[row][col] == 'O':
                pygame.draw.circle(screen, CIRCLE_COLOR, (center_x, center_y), CIRCLE_RADIUS, CROSS_WIDTH // 2) # Thinner circle line
            elif board[row][col] == 'X':
                # Draw anti-aliased lines for X
                top_left = (center_x - (SQUARE_SIZE // 2 - SPACE), center_y - (SQUARE_SIZE // 2 - SPACE))
                top_right = (center_x + (SQUARE_SIZE // 2 - SPACE), center_y - (SQUARE_SIZE // 2 - SPACE))
                bottom_left = (center_x - (SQUARE_SIZE // 2 - SPACE), center_y + (SQUARE_SIZE // 2 - SPACE))
                bottom_right = (center_x + (SQUARE_SIZE // 2 - SPACE), center_y + (SQUARE_SIZE // 2 - SPACE))
                pygame.draw.aaline(screen, CROSS_COLOR, top_left, bottom_right, CROSS_WIDTH // 2)
                pygame.draw.aaline(screen, CROSS_COLOR, top_right, bottom_left, CROSS_WIDTH // 2)

def display_message(message):
    # Display message in the bottom margin
    # Clear the area first
    pygame.draw.rect(
        screen,
        BG_COLOR,
        (0, MARGIN_TOP + GRID_HEIGHT, WIDTH, MARGIN_BOTTOM),
    )  # Clear bottom margin
    # Display the main message (Win/Draw)
    text = font.render(message, True, MESSAGE_COLOR)
    text_rect = text.get_rect(
        center=(WIDTH // 2, MARGIN_TOP + GRID_HEIGHT + MARGIN_BOTTOM // 2 - 10),
    )  # Shift up slightly
    screen.blit(text, text_rect)
    # Always display restart instruction
    restart_text = legend_font.render("Press 'R' to Restart", True, WHITE)
    restart_rect = restart_text.get_rect(
        center=(WIDTH // 2, MARGIN_TOP + GRID_HEIGHT + MARGIN_BOTTOM // 2 + 15),
    )  # Shift down slightly
    screen.blit(restart_text, restart_rect)

def display_turn(player):
    # Display current player's turn in the top margin
    # Clear the area first
    pygame.draw.rect(screen, BG_COLOR, (0, 0, WIDTH, MARGIN_TOP))
    message = f"Player {player}'s Turn"
    text = turn_font.render(message, True, TURN_COLOR)
    text_rect = text.get_rect(center=(WIDTH // 2, MARGIN_TOP // 2))
    screen.blit(text, text_rect)

def draw_winning_line(start_pos, end_pos, progress):
    """Draws the winning line with animation progress (0.0 to 1.0)."""
    start_x = MARGIN_LEFT + start_pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2
    start_y = MARGIN_TOP + start_pos[0] * SQUARE_SIZE + SQUARE_SIZE // 2
    end_x = MARGIN_LEFT + end_pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2
    end_y = MARGIN_TOP + end_pos[0] * SQUARE_SIZE + SQUARE_SIZE // 2

    # Calculate current end point based on progress
    current_end_x = start_x + (end_x - start_x) * progress
    current_end_y = start_y + (end_y - start_y) * progress

    if progress > 0:  # Only draw if progress has started
        pygame.draw.line(
            screen,
            WIN_LINE_COLOR,
            (start_x, start_y),
            (current_end_x, current_end_y),
            7,
        )

def draw_button(text, rect, color, hover_color):
    """Draws a button and handles hover effect."""
    mouse_pos = pygame.mouse.get_pos()
    is_hovering = rect.collidepoint(mouse_pos)
    button_color = hover_color if is_hovering else color
    pygame.draw.rect(screen, button_color, rect, border_radius=10)
    text_surf = button_font.render(text, True, BUTTON_TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    return is_hovering # Return hover state for click detection

# --- Game Mode Selection ---
def select_game_mode():
    """Displays mode selection screen and returns the chosen mode ('pvp' or 'pve')."""
    button_width = 300
    button_height = 80
    spacing = 40
    total_height = button_height * 2 + spacing
    start_y = (HEIGHT - total_height) // 2

    pvp_rect = pygame.Rect((WIDTH - button_width) // 2, start_y, button_width, button_height)
    pve_rect = pygame.Rect((WIDTH - button_width) // 2, start_y + button_height + spacing, button_width, button_height)

    while True:
        screen.fill(BG_COLOR)
        pvp_hover = draw_button("Human vs Human", pvp_rect, BUTTON_COLOR, BUTTON_HOVER_COLOR)
        pve_hover = draw_button("Human vs AI", pve_rect, BUTTON_COLOR, BUTTON_HOVER_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pvp_hover:
                    return 'pvp' # Player vs Player
                if pve_hover:
                    return 'pve' # Player vs Environment (AI)

        pygame.display.update()
        pygame.time.Clock().tick(30) # Lower tick rate for selection screen


# --- Main Game Loop ---
def main():
    game_mode = select_game_mode() # Get game mode first
    print(f"Starting game in {game_mode} mode.") # Optional: Log mode

    game = TicTacToeGame() # Instantiate the game logic

    # Pygame specific state variables (remain the same)
    win_line_start_pos = None
    win_line_end_pos = None
    animating_win_line = False
    animation_progress = 0.0
    hover_row, hover_col = -1, -1 # Track hovered cell

    clock = pygame.time.Clock()  # For controlling animation frame rate

    # Placeholder for AI player logic if needed
    ai_player = None
    if game_mode == 'pve':
        ai_player = RandomAIPlayer('O') # Initialize AI as player 'O'
        print("Human (X) vs Random AI (O) mode selected.")
        pass

    while True:
        # --- Event Handling ---
        mouse_pos = pygame.mouse.get_pos()  # Get mouse position every frame for hover
        hover_row, hover_col = -1, -1  # Reset hover each frame

        # Calculate potential hover cell based on mouse position
        if (
            MARGIN_LEFT < mouse_pos[0] < MARGIN_LEFT + GRID_WIDTH
            and MARGIN_TOP < mouse_pos[1] < MARGIN_TOP + GRID_HEIGHT
        ):
            temp_col = int((mouse_pos[0] - MARGIN_LEFT) // SQUARE_SIZE)
            temp_row = int((mouse_pos[1] - MARGIN_TOP) // SQUARE_SIZE)
            # Check if the cell is empty and game not over using game object
            if game.is_valid_move(temp_row, temp_col) and not game.is_game_over():
                 hover_row, hover_col = temp_row, temp_col

        # Determine if it's the human's turn (always in pvp, only if current player is X in pve)
        is_human_turn = (game_mode == 'pvp' or (game_mode == 'pve' and game.get_current_player() == 'X'))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # Handle human click only if it's their turn
            if event.type == pygame.MOUSEBUTTONDOWN and not game.is_game_over() and is_human_turn:
                mouseX = event.pos[0]
                mouseY = event.pos[1]

                # Adjust click coordinates for margins
                if (
                    MARGIN_LEFT < mouseX < MARGIN_LEFT + GRID_WIDTH
                    and MARGIN_TOP < mouseY < MARGIN_TOP + GRID_HEIGHT
                ):
                    clicked_col = int((mouseX - MARGIN_LEFT) // SQUARE_SIZE)
                    clicked_row = int((mouseY - MARGIN_TOP) // SQUARE_SIZE)
                else:
                    clicked_row, clicked_col = -1, -1  # Click outside grid

                if 0 <= clicked_row < BOARD_SIZE and 0 <= clicked_col < BOARD_SIZE: # Check if click is within grid bounds
                    move_successful = game.make_move(clicked_row, clicked_col)
                    if move_successful:
                        if game.is_game_over():
                            winner = game.get_winner() # Get winner from game state
                            if winner: # If there's a winner, get coords and start animation
                                coords = game.get_winning_line_coords()
                                if coords:
                                    win_line_start_pos, win_line_end_pos = coords
                                    animating_win_line = True
                                    animation_progress = 0.0
                            # No need to explicitly handle draw case here for animation
                    else:
                         # Only print if the click was on the board but invalid (already taken)
                         if not game.is_game_over() and not game.is_valid_move(clicked_row, clicked_col):
                            print("Invalid move: Square already taken.")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reset game on 'R' key press ANYTIME
                    game.reset()
                    # Reset Pygame-specific animation/display variables
                    win_line_start_pos = None
                    win_line_end_pos = None
                    animating_win_line = False
                    animation_progress = 0.0
                    # If AI mode, potentially reset AI state if needed (depends on AI implementation)
                    if game_mode == 'pve':
                         print("Game reset. AI state might need reset depending on implementation.")


        # --- AI Turn Logic ---
        if game_mode == 'pve' and game.get_current_player() == 'O' and not game.is_game_over() and ai_player:
            pygame.time.wait(200) # Small delay to make AI move visible
            ai_move = ai_player.get_move(game)
            if ai_move:
                move_successful = game.make_move(ai_move[0], ai_move[1])
                if move_successful and game.is_game_over():
                    winner = game.get_winner()
                    if winner: # AI won
                        coords = game.get_winning_line_coords()
                        if coords:
                            win_line_start_pos, win_line_end_pos = coords
                            animating_win_line = True
                            animation_progress = 0.0
                    # No need to handle draw separately here, main loop does it
            else:
                print("AI Error: Could not find a valid move.") # Should not happen in normal play


        # --- Drawing Phase ---
        screen.fill(BG_COLOR)  # Clear screen first
        draw_lines()
        draw_legends()
        draw_figures(game.get_board_list()) # Draw current X's and O's from game state

        # Draw Hover Highlight
        if hover_row != -1 and hover_col != -1 and is_human_turn: # Only show hover on human turn
            # Create a surface for transparency
            hover_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            hover_surface.fill(HOVER_COLOR)
            screen.blit(
                hover_surface,
                (
                    MARGIN_LEFT + hover_col * SQUARE_SIZE,
                    MARGIN_TOP + hover_row * SQUARE_SIZE,
                ),
            )

        # Draw Winning Line Animation or Static Line
        if animating_win_line:
            animation_progress += ANIMATION_SPEED
            if win_line_start_pos and win_line_end_pos: # Ensure coords exist
                draw_winning_line(
                    win_line_start_pos,
                    win_line_end_pos,
                    min(1.0, animation_progress),
                )
            if animation_progress >= 1.0:
                animating_win_line = False  # Animation finished
        elif game.is_game_over() and game.get_winner(): # Draw full line after animation or if loaded into win state
             if win_line_start_pos and win_line_end_pos: # Ensure coords exist
                 draw_winning_line(win_line_start_pos, win_line_end_pos, 1.0)

        # Display Status (Turn or Game Over Message)
        if not game.is_game_over():
            display_turn(game.get_current_player())
        else:
            winner = game.get_winner()
            if winner:
                display_message(f"Player {winner} wins!") # Message function now adds restart text
            else:
                display_message("It's a Draw!") # Message function now adds restart text

        pygame.display.update()
        clock.tick(60)  # Limit frame rate to 60 FPS


if __name__ == "__main__":
    main()
