import pygame
from .constants import BROWN, BEIGE, SQUARE_SIZE, ROWS, COLS, WHITE, BLACK, DARK_BEIGE, DARK_BROWN, CROWN, YELLOW
import copy

class Piece:

    PADDING = 14
    OUTLINE = 4

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.queen = False
        self.x = 0
        self.y = 0


    def calculate_position(self):
        self.x = self.col * SQUARE_SIZE + SQUARE_SIZE // 2
        self.y = self.row * SQUARE_SIZE + SQUARE_SIZE // 2

    def make_queen(self):
        self.queen = True

    def draw(self, window):
        radius = SQUARE_SIZE // 2 - self.PADDING
        if self.color == WHITE:
            pygame.draw.circle(window, DARK_BEIGE, (self.x, self.y), radius + self.OUTLINE)
        else:
            pygame.draw.circle(window, DARK_BROWN, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(window, self.color, (self.x, self.y), radius)

        if self.queen:
            window.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calculate_position()

    def __repr__(self):
        return f"Piece at ({self.row}, {self.col}) with color {self.color})"



class Board:
    def __init__(self):
        self.board = []
        self.black_left = 12
        self.white_left = 12
        self.black_queens = 0
        self.white_queens = 0
        self.highlighted_squares = []
        self.create_board()

    def __str__(self):
        final_string = ""
        for row in self.board:
            for piece in row:
                if piece == 0:
                    final_string += ("0")
                elif piece.color == WHITE and not piece.queen:
                    final_string += ("w")
                elif piece.color == WHITE and piece.queen:
                    final_string += ("W")
                elif piece.color == BLACK and not piece.queen:
                    final_string += ("b")
                elif piece.color == BLACK and piece.queen:
                    final_string += ("B")
            final_string += ("|")
        return final_string

    def draw_squares(self, window):
        window.fill(BROWN)
        for row in range(ROWS):
            for col in range(row % 2, ROWS, 2):
                if (row, col) in self.highlighted_squares:
                    color = YELLOW
                else:
                    color = BEIGE
                pygame.draw.rect(window, color, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, BLACK))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, WHITE))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, window):
        self.draw_squares(window)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.calculate_position()
                    piece.draw(window)

    def move(self, piece, row, col):
        if piece is None or piece == 0:
            print(f"Error: Trying to move a non-existent piece.")
            return
        # Check if the move is a jump
        if not isinstance(row, int):
            col = row[1]
            row = row[0]
        if abs(row - piece.row) >= 2:
            jump_distance = abs(row - piece.row)
            if jump_distance >= 2:
                # Calculate the direction of the jump
                row_direction = (row - piece.row) // jump_distance
                col_direction = (col - piece.col) // jump_distance

                # Remove all jumped pieces
                for i in range(1, jump_distance):
                    jumped_row = piece.row + i * row_direction
                    jumped_col = piece.col + i * col_direction
                    jumped_piece = self.board[jumped_row][jumped_col]
                    if jumped_piece != 0:
                        self.board[jumped_row][jumped_col] = 0
                        if jumped_piece.color == WHITE:
                            self.white_left -= 1
                        else:
                            self.black_left -= 1

        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            piece.make_queen()
            if piece.color == WHITE:
                self.white_queens += 1
            else:
                self.black_queens += 1



    def get_piece(self, row, col):
        if row < 0 or row >= ROWS or col < 0 or col >= COLS:
            print(f"Error: Invalid position ({row}, {col}).")
            return None
        piece = self.board[row][col]
        return piece
    
    def get_all_pieces(self, color):
            pieces = []
            for row in self.board:
                for piece in row:
                    if piece != 0 and piece.color == color:
                        pieces.append(piece)
            return pieces

    def get_valid_moves(self, piece):
        moves = {}

        if piece.queen:
            moves.update(self._move_explore(piece.row, piece.col, 1, piece.color, 1))
            moves.update(self._move_explore(piece.row, piece.col, 1, piece.color, -1))
            moves.update(self._move_explore(piece.row, piece.col, -1, piece.color, 1))
            moves.update(self._move_explore(piece.row, piece.col, -1, piece.color, -1))
        else:
            step = -1 if piece.color == WHITE else 1
            moves.update(self._move_explore(piece.row, piece.col, step, piece.color, -1))
            moves.update(self._move_explore(piece.row, piece.col, step, piece.color, 1))

        return moves

    def _move_explore(self, row, col, step, color, direction, jumped=[]):
        moves = {}

        if not (0 <= row + step < ROWS and 0 <= col + direction < COLS):  # da ta nova pozicija ne izadje van table
            return moves

        next_piece = self.get_piece(row + step, col + direction)

        if next_piece == 0 and not jumped:
            moves[(row + step, col + direction)] = []
        elif next_piece != 0 and next_piece.color != color and 0 <= row + 2*step < ROWS and 0 <= col + 2*direction < COLS and self.get_piece(row + 2*step, col + 2*direction) == 0:
            moves[(row + 2*step, col + 2*direction)] = jumped + [next_piece]
            # Check if further jumps are possible before recursing
            if self._can_jump(row + 2*step, col + 2*direction, step, color, direction):
                further_moves = self._move_explore(row + 2*step, col + 2*direction, step, color, direction, jumped + [next_piece])
                for key, value in further_moves.items():
                    if key in moves:
                        moves[key].extend(value)
                    else:
                        moves[key] = value
            # Always explore other directions after a jump
            for new_direction in [-1, 1]:
                if new_direction != direction:
                    further_moves = self._move_explore(row + 2*step, col + 2*direction, step, color, new_direction, jumped + [next_piece])
                    for key, value in further_moves.items():
                        if key in moves:
                            moves[key].extend(value)
                        else:
                            moves[key] = value

        return moves

    def _can_jump(self, row, col, step, color, direction):
        if 0 <= row + 2*step < ROWS and 0 <= col + 2*direction < COLS:
            next_piece = self.get_piece(row + step, col + direction)
            if next_piece != 0 and next_piece.color != color and self.get_piece(row + 2*step, col + 2*direction) == 0:
                return True
        return False


    def remove(self, pieces):
        for piece in pieces:
            for row in range(ROWS):
                for col in range(COLS):
                    if self.board[row][col] == piece:
                        self.board[row][col] = 0
                        if piece.color == WHITE:
                            self.white_left -= 1
                        else:
                            self.black_left -= 1

    def can_move(self, color):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0 and piece.color == color:
                    valid_moves = self.get_valid_moves(piece)
                    if valid_moves:
                        return True
        return False

    def get_all_valid_moves(self, color):
        all_moves = []  # lista u kojoj ce se naci moguci potezi svih figura na trenutnoj tabli
        for row in range(ROWS):  
            for col in range(COLS):
                piece = self.get_piece(row, col)
                if piece != 0 and piece.color == color:  # ako polje nije prazno i ako je boja figure jednaka trenutnoj boji
                    valid_moves = self.get_valid_moves(piece) # dobijamo sve moguce poteze za tu figuru
                    for move in valid_moves.keys(): # prolazimo kroz sve moguce poteze
                        all_moves.append((piece, (move, valid_moves[move])))  # ovde se appenduje (figura, (potez, preskocene figure tokom poteza))
        return all_moves

    def generate_children(self, color):
        children = []
        all_valid_moves = self.get_all_valid_moves(color)
        for piece, move in all_valid_moves:
            new_board = copy.deepcopy(self)
            moved_piece = new_board.get_piece(piece.row, piece.col)
            old_piece = self.get_piece(piece.row, piece.col)  # ovo pristupa 'original' figurici
            if moved_piece is None or moved_piece == 0:
                print(f"Error: No piece found at {piece.row}, {piece.col} in new_board after deepcopy.")
                continue
            
            new_board.move(moved_piece, move[0][0], move[0][1])
            skipped = new_board.get_valid_moves(moved_piece).get(move[0])
            if skipped:
                print(f"Skipped: {skipped}")
                new_board.remove([skipped])
            children.append((new_board, (old_piece, move[0])))
        
        return children
    
    def make_move(self, piece, move):
        new_board = copy.deepcopy(self)
        new_piece = new_board.get_piece(piece.row, piece.col)

        new_board.move(new_piece, move[0], move[1])
        skipped = new_board.get_valid_moves(piece).get(move[0])
        if skipped:
            new_board.remove([skipped])

        return new_board
    
    def winner(self):
        if self.black_left <= 0 or (not self.can_move(BLACK)):
            return WHITE
        elif self.white_left <=0 or (not self.can_move(WHITE)):
            return BLACK
        return None

