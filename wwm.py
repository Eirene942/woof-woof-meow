import pygame
import sys
import random

# Basic
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 600
BOARD_WIDTH = WINDOW_WIDTH // 2
LINE_WIDTH = 1
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = BOARD_WIDTH // BOARD_COLS
SPACE = SQUARE_SIZE // 4

# Colors
BG_COLOR = (255,255,255)
LINE_COLOR = (23, 145, 135)
WIN_LINE_COLOR = (255, 255, 255)
TEXT_COLOR = (0,0,0)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (100, 100, 100)

# Rectangles for start screen
dog_rect = pygame.Rect(WINDOW_WIDTH // 4 - 125, 150, 250, 250)
cat_rect = pygame.Rect(WINDOW_WIDTH * 3 // 4 - 125, 150, 250, 250)

#  Window 
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Woof-Woof-Meow")

#  Fonts 
font = pygame.font.Font(None, 80)
button_font = pygame.font.Font(None, 50)
symbol_font = pygame.font.Font(None, 60)

#  Load images (start screen) 
try:
    dog_img = pygame.image.load("dog.jpg").convert()
    cat_img = pygame.image.load("cat.jpeg").convert()
    dog_img = pygame.transform.scale(dog_img, (250, 250))
    cat_img = pygame.transform.scale(cat_img, (250, 250))
except:
    dog_img = cat_img = None

#  Right-side background image 
try:
    background_img = pygame.image.load("background.jpg").convert()
    background_img = pygame.transform.scale(background_img, (BOARD_WIDTH, WINDOW_HEIGHT))
except:
    background_img = None


#  Button 
button_rect = pygame.Rect(BOARD_WIDTH + 150, 400, 200, 60)

#  Game state 
board = [["." for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)] #board list of three liste .=""
game_over = False
winner_text = ""
current_player = None
PLAYER = None
AI = None
player_word = None
ai_word = None

#  Start screen status 
show_start_screen = True


#  Functions 
def draw_lines():
    for i in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, i * SQUARE_SIZE), (BOARD_WIDTH, i * SQUARE_SIZE), LINE_WIDTH)
    for j in range(1, BOARD_COLS):
        pygame.draw.line(screen, LINE_COLOR, (j * SQUARE_SIZE, 0), (j * SQUARE_SIZE, WINDOW_HEIGHT), LINE_WIDTH)


def draw_figures(): #woof and meow positions
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] in ("woof", "meow"):
                # Different colors
                color = (0,0,0) if board[row][col] == "meow" else TEXT_COLOR
                text_surface = symbol_font.render(board[row][col], True, color)
                text_rect = text_surface.get_rect(center=(
                    col * SQUARE_SIZE + SQUARE_SIZE // 2,
                    row * SQUARE_SIZE + SQUARE_SIZE // 2))
                screen.blit(text_surface, text_rect)


def draw_win_line(start_pos, end_pos):
    pygame.draw.line(screen, WIN_LINE_COLOR, start_pos, end_pos, 10)


def draw_text_centered(text): #text on right side 
    text_surface = font.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(BOARD_WIDTH + BOARD_WIDTH // 2, 250))
    screen.blit(text_surface, text_rect)


def draw_button(mouse_pos): #button new on right side 
    color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, button_rect, border_radius=10)
    text_surface = button_font.render("New", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)


def check_winner():
    # Rows
    for r in range(3):
        if board[r][0] == board[r][1] == board[r][2] != ".":
            y = r * SQUARE_SIZE + SQUARE_SIZE // 2
            draw_win_line((15, y), (BOARD_WIDTH - 15, y))
            return board[r][0]
    # Columns
    for c in range(3):
        if board[0][c] == board[1][c] == board[2][c] != ".":
            x = c * SQUARE_SIZE + SQUARE_SIZE // 2
            draw_win_line((x, 15), (x, WINDOW_HEIGHT - 15))
            return board[0][c]
    # Diagonals
    if board[0][0] == board[1][1] == board[2][2] != ".":
        draw_win_line((15, 15), (BOARD_WIDTH - 15, WINDOW_HEIGHT - 15))
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != ".":
        draw_win_line((BOARD_WIDTH - 15, 15), (15, WINDOW_HEIGHT - 15))
        return board[0][2]
    # Draw
    if all(cell != "." for row in board for cell in row):
        return "Draw"
    return None


def restart(): #restart "New"Button or R
    global board, game_over, winner_text, current_player, show_start_screen
    board = [["." for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
    game_over = False
    winner_text = ""
    current_player = None
    show_start_screen = True


#  AI 
def empty_squares(b): #returns empty squares
    return [(r, c) for r in range(3) for c in range(3) if b[r][c] == "."]


def is_full(b):
    return all(cell != "." for row in b for cell in row)


def minimax(b, is_maximizing): #evaluates possible AI moves 
    result = check_winner()
    if result == ai_word:
        return 1
    elif result == player_word:
        return -1
    elif result == "Draw" or is_full(b):
        return 0

    if is_maximizing:
        best_score = -float("inf")
        for (r, c) in empty_squares(b):
            b[r][c] = ai_word
            score = minimax(b, False)
            b[r][c] = "."
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = float("inf")
        for (r, c) in empty_squares(b):
            b[r][c] = player_word
            score = minimax(b, True)
            b[r][c] = "."
            best_score = min(best_score, score)
        return best_score


def ai_move(): #AI: 50% minimax 50% random move
    if random.random() < 0.5:
        move = random.choice(empty_squares(board))
        board[move[0]][move[1]] = ai_word
        return
    best_score = -float("inf")
    best_move = None
    for (r, c) in empty_squares(board):
        board[r][c] = ai_word
        score = minimax(board, False)
        board[r][c] = "."
        if score > best_score:
            best_score = score
            best_move = (r, c)
    if best_move:
        board[best_move[0]][best_move[1]] = ai_word


#  Start screen 
def draw_start_screen(mouse_pos):
    screen.fill(BG_COLOR)
    title_surface = font.render("cat person or dog person?", True, TEXT_COLOR)
    title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 80))
    screen.blit(title_surface, title_rect)

    dog_rect = pygame.Rect(WINDOW_WIDTH // 4 - 125, 150, 250, 250)
    cat_rect = pygame.Rect(WINDOW_WIDTH * 3 // 4 - 125, 150, 250, 250)

    if dog_img:
        screen.blit(dog_img, dog_rect)
    else:
        pygame.draw.rect(screen, (200, 180, 150), dog_rect)
    if cat_img:
        screen.blit(cat_img, cat_rect)
    else:
        pygame.draw.rect(screen, (180, 150, 200), cat_rect)

    # Hover effect
    if dog_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (255, 255, 255), dog_rect, 5)
    if cat_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (255, 255, 255), cat_rect, 5)

    text_dog = button_font.render("Dog", True, TEXT_COLOR)
    text_cat = button_font.render("Cat", True, TEXT_COLOR)
    screen.blit(text_dog, (dog_rect.centerx - text_dog.get_width() // 2, 420))
    screen.blit(text_cat, (cat_rect.centerx - text_cat.get_width() // 2, 420))

    return dog_rect, cat_rect


#  Main loop 
while True:
    mouse_pos = pygame.mouse.get_pos() #stores current mouse position on board
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #clean quit if window closed
            pygame.quit()
            sys.exit()

        if show_start_screen and event.type == pygame.MOUSEBUTTONDOWN:
            if dog_rect.collidepoint(mouse_pos):
                PLAYER, AI = "Dog", "Cat"
                player_word, ai_word = "woof", "meow"
                current_player = PLAYER
                show_start_screen = False
            elif cat_rect.collidepoint(mouse_pos):
                PLAYER, AI = "Cat", "Dog"
                player_word, ai_word = "meow", "woof"
                current_player = PLAYER
                show_start_screen = False

        elif not show_start_screen:
            #  Game events 
            if event.type == pygame.MOUSEBUTTONDOWN: #detects where player clicked on board
                mouseX, mouseY = event.pos
                # Board click (player)
                if not game_over and mouseX < BOARD_WIDTH and current_player == PLAYER:
                    clicked_row = mouseY // SQUARE_SIZE
                    clicked_col = mouseX // SQUARE_SIZE
                    if board[clicked_row][clicked_col] == ".": #if space empty player word "woof"/"meow" is played
                        board[clicked_row][clicked_col] = player_word
                        winner = check_winner() #checks winner, no winner turn goes back to player
                        if winner:
                            game_over = True
                            winner_text = "DRAW!" if winner == "Draw" else "Cat wins!" if winner == "meow" else "Dog wins!"
                        else:
                            current_player = AI
                            ai_move()
                            winner = check_winner()
                            if winner:
                                game_over = True
                                winner_text = "DRAW!" if winner == "Draw" else "Cat wins!" if winner == "meow" else "Dog wins!"
                            else:
                                current_player = PLAYER
                # Restart button
                if button_rect.collidepoint(mouse_pos):
                    restart()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                restart()

    #  Drawing start screen
    if show_start_screen:
        screen.fill(BG_COLOR)
        draw_start_screen(mouse_pos)

    else:
        # or Game area background
        pygame.draw.rect(screen, BG_COLOR, (0, 0, BOARD_WIDTH, WINDOW_HEIGHT))
        if background_img:
            screen.blit(background_img, (BOARD_WIDTH, 0))
        else:
            pygame.draw.rect(screen, (50, 50, 50), (BOARD_WIDTH, 0, BOARD_WIDTH, WINDOW_HEIGHT))

        # Draw game
        draw_lines()
        draw_figures()
        if game_over and winner_text:
            draw_text_centered(winner_text)

        # Draw button
        draw_button(mouse_pos)

    pygame.display.update()
    #update makes all drawn elements appear
