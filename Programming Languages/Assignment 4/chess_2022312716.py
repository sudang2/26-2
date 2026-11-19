"""Chess Assignment STEP 4: ordinary piece movement and captures."""


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

        # Promotion is added in STEP 5.
        if command.promotion is not None:
            return None
        destination_x, destination_y = command.destination
        if piece.lower() == "p" and destination_y in (0, 7):
            return None
        if not self.board.can_move(command):
            return None

        effect = MoveEffect(piece, target)
        effect.add_change(command.source, ".")
        effect.add_change(command.destination, piece)
        return effect

    def play_move(self, command):
        effect = self.validate_move(command)
        if effect is None:
            return False
        effect.apply(self.board)
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
