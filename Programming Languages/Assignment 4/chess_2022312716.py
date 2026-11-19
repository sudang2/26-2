"""Chess Assignment STEP 5: castling, en passant, promotion, and king safety checks."""


FILES = "abcdefgh"
RANKS = "12345678"
DIGITS = "0123456789"


class ChessBoard:

    def __init__(self):
        self._rows = [
            list("RNBQKBNR"),
            list("PPPPPPPP"),
            list("........"),
            list("........"),
            list("........"),
            list("........"),
            list("pppppppp"),
            list("rnbqkbnr"),
        ]

    def inside_board(self, square):
        x, y = square
        return 0 <= x < 8 and 0 <= y < 8

    def get_piece(self, square):
        if not self.inside_board(square):
            raise IndexError("Square is outside the board")
        x, y = square
        return self._rows[y][x]

    def set_piece(self, square, piece):
        if not self.inside_board(square):
            raise IndexError("Square is outside the board")
        x, y = square
        self._rows[y][x] = piece

    def copy(self):
        board = ChessBoard()
        for y in range(8):
            for x in range(8):
                board._rows[y][x] = self._rows[y][x]
        return board


    def trace_path(self, source, destination, directions):
        source_x, source_y = source
        for step_x, step_y in directions:
            x = source_x + step_x
            y = source_y + step_y
            while self.inside_board((x, y)):
                if (x, y) == destination:
                    return True
                if self.get_piece((x, y)) != ".":
                    break
                x += step_x
                y += step_y
        return False

    def can_move(self, command):
        source_x, source_y = command.source
        destination_x, destination_y = command.destination
        dx = destination_x - source_x
        dy = destination_y - source_y
        piece = self.get_piece(command.source)
        target = self.get_piece(command.destination)
        kind = piece.lower()

        if kind == "p":
            direction = 1
            starting_rank = 1
            if piece.islower():
                direction = -1
                starting_rank = 6
            if dx == 0 and target == ".":
                if dy == direction:
                    return True
                if source_y == starting_rank and dy == 2 * direction:
                    middle = (source_x, source_y + direction)
                    return self.get_piece(middle) == "."
            return abs(dx) == 1 and dy == direction and target != "."

        if kind == "n":
            return (abs(dx) == 1 and abs(dy) == 2) or (abs(dx) == 2 and abs(dy) == 1)
        if kind == "k":
            return abs(dx) <= 1 and abs(dy) <= 1

        rook_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        bishop_directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        if kind == "r":
            return self.trace_path(command.source, command.destination, rook_directions)
        if kind == "b":
            return self.trace_path(command.source, command.destination, bishop_directions)
        if kind == "q":
            directions = rook_directions + bishop_directions
            return self.trace_path(command.source, command.destination, directions)
        return False


    def is_attacked(self, square, attacker):
        for y in range(8):
            for x in range(8):
                piece = self.get_piece((x, y))
                if piece == ".":
                    continue
                if attacker == "white" and piece.islower():
                    continue
                if attacker == "black" and piece.isupper():
                    continue

                dx = square[0] - x
                dy = square[1] - y
                if dx == 0 and dy == 0:
                    continue

                if piece.lower() == "p":
                    direction = 1
                    if piece.islower():
                        direction = -1
                    if abs(dx) == 1 and dy == direction:
                        return True
                else:
                    command = MoveCommand((x, y), square)
                    if self.can_move(command):
                        return True
        return False

    def king_is_safe(self, player):
        king = "K"
        opponent = "black"
        if player == "black":
            king = "k"
            opponent = "white"
        for y in range(8):
            for x in range(8):
                if self.get_piece((x, y)) == king:
                    return not self.is_attacked((x, y), opponent)
        return False

    def render(self):
        lines = []
        for y in range(7, -1, -1):
            line = "".join(self._rows[y])
            lines.append(line)
        return "\n".join(lines)


class MoveCommand:

    def __init__(self, source, destination, promotion=None):
        self.source = source
        self.destination = destination
        self.promotion = promotion



class MoveEffect:

    def __init__(self, moving_piece, captured_piece):
        self.changes = []
        self.moving_piece = moving_piece
        self.captured_piece = captured_piece
        self.move_type = "normal"
        if captured_piece != ".":
            self.move_type = "capture"

    def add_change(self, square, piece):
        self.changes.append((square, piece))

    def apply(self, board):
        for square, piece in self.changes:
            board.set_piece(square, piece)


def parse_square(file, rank):
    x = FILES.index(file)
    y = RANKS.index(rank)
    return (x, y)


def parse_move(line):
    command = line.replace(" ", "")
    if len(command) != 4 and len(command) != 5:
        return None

    if command[0] not in FILES or command[1] not in RANKS:
        return None
    if command[2] not in FILES or command[3] not in RANKS:
        return None

    promotion = None
    if len(command) == 5:
        promotion = command[4]
        if promotion not in "qrbn":
            return None

    source = parse_square(command[0], command[1])
    destination = parse_square(command[2], command[3])
    return MoveCommand(source, destination, promotion)


def is_case_id(line):
    if len(line) < 2 or line[0] != "#":
        return False

    has_nonzero_digit = False
    for digit in line[1:]:
        if digit not in DIGITS:
            return False
        if digit != "0":
            has_nonzero_digit = True
    return has_nonzero_digit


class ChessGame:

    def __init__(self, case_id):
        self.case_id = case_id
        self.board = ChessBoard()
        self.commands = []
        self.current_player = "white"
        self.castling_rights = [(0, 0), (7, 0), (0, 7), (7, 7)]
        self.en_passant_target = None
        self.invalid_input = False

    def read_move(self, line):
        if self.invalid_input:
            return
        command = parse_move(line)
        if command is None:
            self.invalid_input = True
            return
        if not self.play_move(command):
            self.invalid_input = True

    def validate_move(self, command):
        if not self.board.inside_board(command.source):
            return None
        if not self.board.inside_board(command.destination):
            return None
        if command.source == command.destination:
            return None

        piece = self.board.get_piece(command.source)
        target = self.board.get_piece(command.destination)
        if piece == ".":
            return None
        if self.current_player == "white" and piece.islower():
            return None
        if self.current_player == "black" and piece.isupper():
            return None
        if target != "." and piece.isupper() == target.isupper():
            return None
        if target.lower() == "k":
            return None

        source_x, source_y = command.source
        destination_x, destination_y = command.destination

        if piece.lower() == "k" and abs(destination_x - source_x) == 2:
            if command.promotion is not None:
                return None
            effect = self.validate_castling(command)
        else:
            placed_piece = piece
            if piece.lower() == "p" and destination_y in (0, 7):
                if command.promotion not in ("q", "r", "b", "n"):
                    return None
                placed_piece = command.promotion
                if piece.isupper():
                    placed_piece = placed_piece.upper()
            elif command.promotion is not None:
                return None

            if piece.lower() == "p" and source_x != destination_x and target == ".":
                effect = self.validate_en_passant(command)
            else:
                if not self.board.can_move(command):
                    return None
                effect = MoveEffect(piece, target)
                effect.add_change(command.source, ".")
                effect.add_change(command.destination, placed_piece)
                if placed_piece != piece:
                    effect.move_type = "promotion"

        if effect is None:
            return None
        temporary_board = self.board.copy()
        effect.apply(temporary_board)
        if not temporary_board.king_is_safe(self.current_player):
            return None
        return effect

    def validate_castling(self, command):
        rank = 0
        king = "K"
        rook = "R"
        opponent = "black"
        if self.current_player == "black":
            rank = 7
            king = "k"
            rook = "r"
            opponent = "white"

        if command.source != (4, rank):
            return None
        if command.destination not in ((2, rank), (6, rank)):
            return None

        rook_x = 7
        crossing_x = 5
        between = [5, 6]
        if command.destination[0] == 2:
            rook_x = 0
            crossing_x = 3
            between = [1, 2, 3]

        rook_square = (rook_x, rank)
        if rook_square not in self.castling_rights:
            return None
        if self.board.get_piece(command.source) != king:
            return None
        if self.board.get_piece(rook_square) != rook:
            return None
        for x in between:
            if self.board.get_piece((x, rank)) != ".":
                return None

        if self.board.is_attacked(command.source, opponent):
            return None
        temporary_board = self.board.copy()
        temporary_board.set_piece(command.source, ".")
        temporary_board.set_piece((crossing_x, rank), king)
        if temporary_board.is_attacked((crossing_x, rank), opponent):
            return None

        effect = MoveEffect(king, ".")
        effect.move_type = "castling"
        effect.add_change(command.source, ".")
        effect.add_change(command.destination, king)
        effect.add_change(rook_square, ".")
        effect.add_change((crossing_x, rank), rook)
        return effect

    def validate_en_passant(self, command):
        source_x, source_y = command.source
        destination_x, destination_y = command.destination
        direction = 1
        required_rank = 4
        opponent_pawn = "p"
        if self.current_player == "black":
            direction = -1
            required_rank = 3
            opponent_pawn = "P"

        if source_y != required_rank:
            return None
        if command.destination != self.en_passant_target:
            return None
        if abs(destination_x - source_x) != 1 or destination_y - source_y != direction:
            return None
        if self.board.get_piece(command.destination) != ".":
            return None
        captured_square = (destination_x, source_y)
        if self.board.get_piece(captured_square) != opponent_pawn:
            return None

        piece = self.board.get_piece(command.source)
        effect = MoveEffect(piece, opponent_pawn)
        effect.move_type = "en_passant"
        effect.add_change(command.source, ".")
        effect.add_change(command.destination, piece)
        effect.add_change(captured_square, ".")
        return effect

    def remove_castling_right(self, square):
        if square in self.castling_rights:
            self.castling_rights.remove(square)

    def update_rights(self, command, effect):
        source_x, source_y = command.source
        if effect.moving_piece.lower() == "k":
            self.remove_castling_right((0, source_y))
            self.remove_castling_right((7, source_y))
        elif effect.moving_piece.lower() == "r":
            self.remove_castling_right(command.source)
        if effect.captured_piece.lower() == "r":
            self.remove_castling_right(command.destination)

    def update_en_passant(self, command, effect):
        self.en_passant_target = None
        source_x, source_y = command.source
        destination_x, destination_y = command.destination
        if effect.moving_piece.lower() == "p" and abs(destination_y - source_y) == 2:
            self.en_passant_target = (source_x, (source_y + destination_y) // 2)

    def play_move(self, command):
        effect = self.validate_move(command)
        if effect is None:
            return False
        effect.apply(self.board)
        self.update_rights(command, effect)
        self.update_en_passant(command, effect)
        self.commands.append(command)
        self.switch_player()
        return True

    def switch_player(self):
        if self.current_player == "white":
            self.current_player = "black"
        else:
            self.current_player = "white"

    def render(self):
        result = self.case_id + "\n" + self.board.render()
        if self.invalid_input:
            result += "\ninvalid input"
        return result


def main():
    game = None
    while True:
        try:
            line = input()
        except EOFError:
            break
        line = line.rstrip("\r\n")

        if is_case_id(line):
            if game is not None:
                print(game.render())
            game = ChessGame(line)
        elif game is None:
            print("invalid input")
            return
        else:
            game.read_move(line)

    if game is None:
        print("invalid input")
    else:
        print(game.render())


if __name__ == "__main__":
    main()
