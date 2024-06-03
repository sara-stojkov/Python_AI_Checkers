from .constants import BLACK, WHITE

class Minimax:
    piece_value = 100
    queen_value = 150
    edge_value = 30  
    back_row_piece = 10
    vulnerable_piece = -45
    center_piece = 8
    almost_queen = 7

    def __init__(self, board, depth, maximizing_player, previous_moves_dictionary):
        self.board = board
        self.depth = depth
        self.maximizing_player = maximizing_player
        self.minimizing_player = not maximizing_player
        self.previous_moves = previous_moves_dictionary

    def evaluate_board(self):
        value = 0
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece != 0:
                    piece_value = self.piece_value
                    if piece.queen:
                        piece_value += self.queen_value
                    else:
                        if (piece.color == BLACK and row == 6) or (piece.color == WHITE and row == 1):
                            piece_value += self.almost_queen
                    if row == 0:
                        piece_value += self.back_row_piece
                    if row == 0 or row == 7 or col == 0 or col == 7:
                        piece_value += self.edge_value
                    if (col == 3 or col == 4) and (row == 2 or row == 3 or row == 4 or row == 5):
                        piece_value += self.center_piece
                    if self.is_piece_vulnerable(row, col):
                        piece_value += self.vulnerable_piece

                    if piece.color == BLACK:  # maximizing player
                        value += piece_value
                    elif piece.color == WHITE:  # minimizing player
                        value -= piece_value
        return value
    
    def is_piece_vulnerable(self, row, col):
        piece = self.board.get_piece(row, col)
        if piece is None:
            return False
        opponent_color = BLACK if piece.color == WHITE else WHITE
        opponent_moves = self.board.get_all_valid_moves(opponent_color)  # imaju oblik (figura, (potez, preskocene figure tokom poteza))
        for move in opponent_moves:
            if (row, col) in move[1][1]:
                return True
        return False
    
    def minimax_alpha_beta(self, board, depth, maximizing_player, alpha, beta):
        if depth == 0 or board.winner() is not None:
            eval_value = self.evaluate_board()
            return eval_value

        if maximizing_player:
            max_eval = float('-inf')
            for child, _ in board.generate_children(BLACK):
                eval = self.minimax_alpha_beta(child, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for child, _ in board.generate_children(WHITE):
                eval = self.minimax_alpha_beta(child, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
        

    def get_best_move(self, color, jumps_forced):
        best_move = None
        max_eval = float('-inf')  # AI je maximizing igrac
        piece_and_move = None
        if jumps_forced:  # this is a bool value, true or false depending on the choice at the start menu
            jump_moves = self.filter_jumps(self.board.get_all_valid_moves(color))
            if jump_moves:  # if there are jumps, play them
                for jump_move in jump_moves:  # where jump_move is in the form (piece, move)
                    new_board = self.board.make_move(jump_move[0], jump_move[1])  # make the jump move on a new board
                    eval = self.minimax_alpha_beta(new_board, self.depth - 1, False, float('-inf'), float('inf'))  # evaluate the new board state
                    if eval > max_eval:  # maximizing player
                        max_eval = eval
                        best_move = jump_move  # in the form(piece, move)
                return best_move
        
            for key, value in self.previous_moves.items():
                if key == str(self.board):
                    piece_and_move = value
                    return piece_and_move


        for child, piece_and_move in self.board.generate_children(BLACK):  # jer je (child, (figurica, potez)) gde je child novi board objekat
            eval = self.minimax_alpha_beta(child, self.depth - 1, False, float('-inf'), float('inf'))
            if eval > max_eval:  # maximizing player
                max_eval = eval
                best_move = piece_and_move  # in the form (piece, move)
        
        if best_move is None or best_move[0] == 0:
            return (0, (0, 0))
        else:
            # print(f"\nBest move selected: ({best_move[0].row}, {best_move[0].col}) --> ({best_move[1][0]}, {best_move[1][1]}) with evaluation: {max_eval}\n")
            pass
        return best_move
    
    def filter_jumps(self, moves):
        jump_moves = []
        for move in moves:
            if len(move) > 1:
                if len(move[1][1]) > 0:  # da li ima preskocenih figura
                    jump_moves.append(move)
        print(f"Jump moves: {jump_moves}")
        return jump_moves
