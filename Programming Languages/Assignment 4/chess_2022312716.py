"""Chess Assignment STEP 3: board setup and input parsing."""


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
        self.invalid_input = False

    def read_move(self, line):
        if self.invalid_input:
            return

        command = parse_move(line)
        if command is None:
            self.invalid_input = True
        else:
            self.commands.append(command)

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
