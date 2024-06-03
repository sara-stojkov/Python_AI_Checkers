import pygame
from .constants import ROWS, COLS, SQUARE_SIZE, WHITE, BLACK, BROWN, BEIGE, GREEN, RED, WIDTH, HEIGHT, YELLOW, ORANGE, BUTTON_WIDTH, BUTTON_HEIGHT, DARK_BROWN
from .board import Board

class Game:
    def __init__(self, window):
        self.window = window
        self._init()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = WHITE
        self.valid_moves = {}

    def update(self, window):
        self.board.draw(window)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def reset(self):
        self._init()

    def select(self, row, col, forced_jumps):
        piece = self.board.get_piece(row, col)
        if piece and piece.color == self.turn:
            self.selected = piece
            self.all_valid_moves = self.board.get_valid_moves(piece)
            jump_moves = self.only_jump_moves(self.all_valid_moves)
            if forced_jumps and jump_moves:
                self.valid_moves = jump_moves
            else:
                self.valid_moves = self.all_valid_moves

            print(f"Valid moves for {piece}: {self.valid_moves}")
            return True

        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.valid_moves = {}  # Clear valid moves if the move was not successful
            else:
                return True

        return False
    
    def only_jump_moves(self, moves):
        jumps = []
        for move in moves:
            if moves[move]:
                jumps.append(move)
        return jumps

    def _move(self, row, col):
        if self.selected and (row, col) in self.valid_moves:
            skipped = self.board.move(self.selected, row, col, )  # pomera se odabrana figura
            if skipped:
                self.board.remove(skipped)  # sklanjaju se preskocene figure
            self.switch_turn()  # ako je uspesno, menja se potez
            return True
        return False

    def switch_turn(self):
        self.valid_moves = {}
        if self.turn == BLACK:
            self.turn = WHITE 
        else: 
            self.turn = BLACK
        print(f"\n_____________________\nSwitched turn to {'WHITE' if self.turn == WHITE else 'BLACK'}\n____________________\n")


    def draw_board(self):
        self.window.fill(BROWN)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(self.window, BEIGE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            if moves[move]:
                pygame.draw.rect(self.window, RED, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            else:
                pygame.draw.rect(self.window, GREEN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    
    def highlight_move(self, window, start, end, color, jumps_forced):
        thickness = 10
        start_x = start[1] * SQUARE_SIZE
        start_y = start[0] * SQUARE_SIZE
        pygame.draw.rect(window, color, (start_x, start_y, SQUARE_SIZE, SQUARE_SIZE), thickness)
        self.board.highlighted_squares = [start]

        if jumps_forced:
            for end in end:
                end_x = end[1] * SQUARE_SIZE
                end_y = end[0] * SQUARE_SIZE
                pygame.draw.rect(window, color, (end_x, end_y, SQUARE_SIZE, SQUARE_SIZE), thickness)
                self.board.highlighted_squares.append(end)
        else:
            end_x = end[1] * SQUARE_SIZE
            end_y = end[0] * SQUARE_SIZE
            pygame.draw.rect(window, color, (end_x, end_y, SQUARE_SIZE, SQUARE_SIZE), thickness)
            self.board.highlighted_squares.append(end)

        pygame.display.update()

    def get_possible_jumps(self, piece):
        jumps = []
        for move in self.valid_moves:
            if self.valid_moves[move]:
                jumps.append(move)
        return jumps

    def announce_winner(self, window):
        winner = self.board.winner()
        if winner == WHITE:
            print("Game over - White wins!")
        else:
            print("Game over - Black wins!")

        if winner:
            font = pygame.font.Font(None, 60)
            
            window.fill(BEIGE)
            title = font.render("Game finished!", True, DARK_BROWN)
            title_rect = title.get_rect(center=(WIDTH // 2, 200))
            window.blit(title, title_rect)
            
            if winner == BLACK:
                text = font.render("BLACK wins!", True, BROWN)
            elif winner == WHITE:
                text = font.render("WHITE wins!", True, BROWN)
            text_rect = text.get_rect(center=(WIDTH // 2, 320))
            self.window.blit(text, text_rect)
            pygame.display.update()
            pygame.time.wait(5000)
        return winner
    
