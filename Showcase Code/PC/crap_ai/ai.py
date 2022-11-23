import chess
import chess.polyglot

import tables
import util
from uuid import uuid4

class AI_AlphaBeta:
    INFINITE = 10000000
    PIECE_VALUES = [0, 100, 300, 330, 500, 900, INFINITE]
    boards_evaluated = 0
    move_count = 0
    opening = True
    zobrist_hash = 0
    hash_values = []
    piece_hash_index = {'p': 0, 'r': 1} #UNFINISHED

    def __init__(self):
        # One number for each piece at each square
        # One number to indicate the side to move is black
        # Four numbers to indicate the castling rights, though usually 16 (2^4) are used for speed
        # Eight numbers to indicate the file of a valid En passant square, if any
        for i in range(12*64 + 1 + 4 + 8):
            self.hash_values.append((uuid4().int >> 64))

        #Squares are counted from bottom left to otop right
        #Order of hashes: W/B Pawns, W/B Knight, W/B Bishop, W/B Rook, W/B Queen, W/B King
        self.zobrist_hash = 0;
        for i in range(8): #Pawns
            self.zobrist_hash ^= self.hash_values[0 * 64 + 1 * 8 + i]
        for i in range(8): #Pawns
            self.zobrist_hash ^= self.hash_values[1 * 64 + 6 * 8 + i]

        self.zobrist_hash ^= self.hash_values[2 * 64 + 0 * 8 + 1] #Knights
        self.zobrist_hash ^= self.hash_values[2 * 64 + 0 * 8 + 6]
        self.zobrist_hash ^= self.hash_values[3 * 64 + 7 * 8 + 1]
        self.zobrist_hash ^= self.hash_values[3 * 64 + 7 * 8 + 6]

        self.zobrist_hash ^= self.hash_values[4 * 64 + 0 * 8 + 2]#Bishop
        self.zobrist_hash ^= self.hash_values[4 * 64 + 0 * 8 + 5]
        self.zobrist_hash ^= self.hash_values[5 * 64 + 7 * 8 + 2]
        self.zobrist_hash ^= self.hash_values[5 * 64 + 0 * 8 + 5]

        self.zobrist_hash ^= self.hash_values[6 * 64 + 0 * 8 + 0]#Rook
        self.zobrist_hash ^= self.hash_values[6 * 64 + 0 * 8 + 7]
        self.zobrist_hash ^= self.hash_values[7 * 64 + 7 * 8 + 0]
        self.zobrist_hash ^= self.hash_values[7 * 64 + 7 * 8 + 7]

        self.zobrist_hash ^= self.hash_values[8 * 64 + 0 * 8 + 3]#Queen
        self.zobrist_hash ^= self.hash_values[9 * 64 + 7 * 8 + 3]

        self.zobrist_hash ^= self.hash_values[10 * 64 + 0 * 8 + 4]#King
        self.zobrist_hash ^= self.hash_values[11 * 64 + 7 * 8 + 4]


        pass

    def update_hash(self, board, move):
        print(move.from_square)
        print(move.to_square)


    def get_move(self, board, depth):
        best_eval = -self.INFINITE
        self.boards_evaluated = 0

        moves = list(board.legal_moves)
        # print(moves)
        moves = self.order_moves(board, moves)
        # print(moves)
        best_move = None

        for move in board.legal_moves:
            board.push(move)

            eval = -self.alphabeta(board, depth-1, -self.INFINITE, self.INFINITE)

            if (eval > best_eval):
                best_eval = eval
                best_move = move

            board.pop()


        self.update_hash(board, move)
        return best_move

    def alphabeta(self, board, depth, alpha, beta):
        if depth == 0:
            self.boards_evaluated += 1
            return self.evaluate(board)

        moves = list(board.legal_moves)
        moves = self.order_moves(board, moves)

        if (len(moves) == 0):
            return 0

        for move in moves:
            board.push(move)
            eval = -self.alphabeta(board, depth-1, -beta, -alpha)
            board.pop()

            if (eval >= beta):
                return beta
            if (eval > alpha):
                alpha = eval

        return eval

    def evaluate(self, board):
        value = 0

        for i in range(64):
            piece = board.piece_at(i)
            if piece is not None:
                if piece.color == board.turn:
                    value += self.PIECE_VALUES[piece.piece_type]
                    value += tables.PIECE_TABLE[piece.piece_type][int(i/8)][i%8]
                else:
                    value -= self.PIECE_VALUES[piece.piece_type]
                    value -= tables.PIECE_TABLE[piece.piece_type][int(i/8)][i%8]

        return value

    def test_openings(self, board):
        with chess.polyglot.open_reader("data/polyglot/Perfect2017.bin") as reader:
            for entry in reader.find_all(board):
                print(entry.move, entry.weight, entry.learn)

    def order_moves(self, board, moves):
        move_scores = []

        for move in moves:
            score = 0

            if board.is_capture(move) and board.piece_at(move.to_square) is not None:
                score += 10 * self.PIECE_VALUES[board.piece_at(move.to_square).piece_type] - self.PIECE_VALUES[board.piece_at(move.from_square).piece_type]

            move_scores.append(score)

        return util.bubble_sort(moves, move_scores)
