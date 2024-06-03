import pygame
pygame.init()  # inicijalizujemo
from dame.game import Game
from dame.algorithm import Minimax
from dame.constants import WIDTH, HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, SQUARE_SIZE, WHITE, BLACK, BEIGE, BROWN, DARK_BROWN, ORANGE, YELLOW
from time import time

FPS = 60
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')

def draw_start_menu(window, game_state):
    font = pygame.font.Font(None, 44)
    button_x = (WIDTH - BUTTON_WIDTH) // 2
    button_y = (HEIGHT - BUTTON_HEIGHT) // 2

    window.fill(BEIGE)

    title = font.render("Welcome to Checkers!", True, DARK_BROWN)
    title_rect = title.get_rect(center=(WIDTH // 2, 170))
    window.blit(title, title_rect)

    title = font.render("Please, select a game mode:", True, DARK_BROWN)
    title_rect = title.get_rect(center=(WIDTH // 2, 230))
    window.blit(title, title_rect)

    pygame.draw.rect(window, BROWN, (button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT))
    pygame.draw.rect(window, DARK_BROWN, (button_x, button_y + BUTTON_HEIGHT + 40, BUTTON_WIDTH, BUTTON_HEIGHT))

    text = font.render("Classic", True, (255, 255, 255))
    text_rect = text.get_rect(center=(button_x + BUTTON_WIDTH // 2, button_y + BUTTON_HEIGHT // 2))
    window.blit(text, text_rect)

    text = font.render("Forced jumps", True, (255, 255, 255))
    text_rect = text.get_rect(center=(button_x + BUTTON_WIDTH // 2, button_y + BUTTON_HEIGHT + 40 + BUTTON_HEIGHT // 2))
    window.blit(text, text_rect)

    pygame.display.update()
    forced_jumps = False
    while game_state == "start_menu":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = "exit"
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                if button_x <= position[0] <= button_x + BUTTON_WIDTH and button_y <= position[1] <= button_y + BUTTON_HEIGHT:
                    game_state = "classic"
                    forced_jumps = False
                elif button_x <= position[0] <= button_x + BUTTON_WIDTH and button_y + BUTTON_HEIGHT + 20 <= position[1] <= button_y + BUTTON_HEIGHT + 20 + BUTTON_HEIGHT:
                    game_state = "forced_jumps"
                    print("Forced jumps selected. If there are any jumps, you must play them!")
                    forced_jumps = True

        if game_state == "exit":
            break
    return game_state, forced_jumps
    # bira se game mode, da li mora da se jede ili ne

def get_row_col_from_mouse(position):
    x, y = position
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def load_previous_states(file_path):
    board_states = {} # koristimo recnik gde je kljuc stanje table, a vrednost je potez koji treba da se odigra
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip("\n")
            board_state, move = line.split(":")
            old_pos, new_pos = move.split("->")
            board_states[board_state] = (old_pos, new_pos)
    return board_states

def save_new_states(file_path, dictionary_of_boards_and_moves):
    for board_state in dictionary_of_boards_and_moves.keys():
        with open(file_path, "a") as file:
            file.write(f"{board_state}:{dictionary_of_boards_and_moves[board_state]}\n")
    return

# main.py
def main(previous_moves):
    run = True
    clock = pygame.time.Clock()
    game = Game(window)
    inital_game_state = "start_menu"
    game_state, forced_jumps = draw_start_menu(window, inital_game_state)
    depth = 4  # pocetna dubina
    saved_moves = {}

    while run:
        clock.tick(FPS)

        if game.board.winner() is not None:
            game.announce_winner(window)
            run = False
            break

        if game_state == "exit":
            print("Exiting...")
            run = False
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.turn == WHITE:
                    position = pygame.mouse.get_pos()
                    row, col = get_row_col_from_mouse(position)
                    game.select(row, col, forced_jumps)  # selektuje se figura
                    if game.selected is not None:
                        selected_x, selected_y = game.selected.x, game.selected.y  
                        if forced_jumps:
                            jumps = game.get_possible_jumps(game.board.get_piece(selected_x, selected_y))
                            print(f"row: {row}, col: {col}")
                            game.highlight_move(window, (selected_x, selected_y), jumps, YELLOW, forced_jumps)

                        game.highlight_move(window, (selected_x, selected_y), (row, col), YELLOW, forced_jumps)
                        pygame.display.update()  
                        pygame.time.delay(500)  
                        game.board.draw(window) 
                        pygame.time.delay(100)  

        # AI na potezu
        if game.turn == BLACK:
            t1 = time()
            minimax = Minimax(game.board, depth, True, previous_moves)
            best_move = minimax.get_best_move(BLACK, forced_jumps)
            
            if best_move:
                piece, move = best_move
                if piece != 0:
                    saved_moves[str(game.board)] = str((piece.row, piece.col)) + "->" + str(move) # best_move je oblika (piece, move) zato je ovakva struktura
                    print(f"AI selected: ({piece.row}, {piece.col}) --> ({move[0]}, {move[1]})")
                    game.highlight_move(window, (piece.row, piece.col), move, ORANGE, forced_jumps)
                    skipped = game.board.move(piece, move[0], move[1])
                    if skipped:
                        game.board.remove(skipped)
                    t2 = time()
                    thinking_time = t2 - t1
                    print(f"Time taken: {t2 - t1} seconds for depth {depth}.")
                    game.highlight_move(window, (piece.row, piece.col), move, ORANGE, forced_jumps)  
                    game.board.move(piece, move[0], move[1])
                    pygame.display.update()  
                    game.board.draw(window) 
                    
                    if thinking_time < 0.1:
                        depth += 2
                    elif thinking_time < 0.5:
                        depth += 1
                    elif thinking_time > 1.2:
                        depth -= 1
                    elif thinking_time > 3:
                        depth -= 3
                    elif thinking_time > 2  :
                        depth -= 2

                    if depth > 7:
                        depth = 7
                    pygame.time.delay(500)  
                    game.switch_turn()
            else:
                print("No valid moves found by AI.")
                game.board.winner()

        game.update(window)

    pygame.quit()
    return saved_moves



if __name__ == "__main__":
    previous_moves = load_previous_states("previous_states.txt")
    saved_moves = main(previous_moves)
    save_new_states("previous_states.txt", saved_moves)
