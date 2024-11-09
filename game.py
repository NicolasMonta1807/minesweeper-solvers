import math
import random
import itertools

ROWS = 10
COLUMNS = 10
MINE_COUNT = 20

BOARD = []
MINES = set()
EXTENDED = set()

MATRIX = [['?'] * COLUMNS for i in range(ROWS)]


class Colors(object):
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


def colorize(s, color):
    return '{}{}{}'.format(color, s, Colors.ENDC)


def get_index(i, j):
    if 0 > i or i >= COLUMNS or 0 > j or j >= ROWS:
        return None
    return i * ROWS + j


def create_board():
    global BOARD, MINES, EXTENDED, MATRIX
    BOARD = []
    MINES = set()
    EXTENDED = set()
    MATRIX = [['?'] * COLUMNS for _ in range(ROWS)]

    squares = ROWS * COLUMNS

    # Crear el tablero
    for _ in range(squares):
        BOARD.append('[ ]')

    # Crear minas
    while True:
        if len(MINES) >= MINE_COUNT:
            break
        MINES.add(int(math.floor(random.random() * squares)))


def draw_board():
    lines = []

    for j in range(ROWS):
        if j == 0:
            lines.append('   ' + ''.join(' {} '.format(x) for x in range(COLUMNS)))

        line = [' {} '.format(j)]
        for i in range(COLUMNS):
            line.append(BOARD[get_index(i, j)])
        lines.append(''.join(line))

    return '\n'.join(reversed(lines))


def parse_selection(raw_selection):
    try:
        return [int(x.strip(','), 10) for x in raw_selection.split(' ')]
    except Exception:
        return None


def adjacent_squares(i, j):
    num_mines = 0
    squares_to_check = []
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            # Skip current square
            if di == dj == 0:
                continue

            coordinates = i + di, j + dj

            # Skip squares off the board
            proposed_index = get_index(*coordinates)
            if not proposed_index:
                continue

            if proposed_index in MINES:
                num_mines += 1

            squares_to_check.append(coordinates)

    return num_mines, squares_to_check


def update_board(square, selected=True):
    i, j = square
    index = get_index(i, j)
    EXTENDED.add(index)

    if MINE_COUNT == 0:
        BOARD[index] = '   '
        return False

    if index in MINES:
        if not selected:
            return
        BOARD[index] = colorize(' X ', Colors.RED)
        return True
    else:
        num_mines, squares = adjacent_squares(i, j)
        MATRIX[i][j] = num_mines
        if num_mines:
            if num_mines == 1:
                text = colorize(num_mines, Colors.BLUE)
            elif num_mines == 2:
                text = colorize(num_mines, Colors.GREEN)
            else:
                text = colorize(num_mines, Colors.RED)

            BOARD[index] = ' {} '.format(text)
            return
        else:
            BOARD[index] = '   '

            for asquare in squares:
                aindex = get_index(*asquare)
                if aindex in EXTENDED:
                    continue
                EXTENDED.add(aindex)
                update_board(asquare, False)


def reveal_mines():
    for index in MINES:
        if index in EXTENDED:
            continue
        BOARD[index] = colorize(' X ', Colors.YELLOW)


def has_won():
    if MINE_COUNT == 0:
        return len(EXTENDED) == len(BOARD)
    return len(EXTENDED | MINES) == len(BOARD)


def brute_force_solve():
    numbered_squares = []
    restrictions = []
    unknown_squares = set()

    for i in range(ROWS):
        for j in range(COLUMNS):
            if MATRIX[i][j] != '?':
                numbered_squares.append((i, j))
            else:
                unknown_squares.add((i, j))

    for square in numbered_squares:
        i, j = square
        unknown_neighbours, num_mines = check_neighbours(i, j)
        if unknown_neighbours:
            restrictions.append((unknown_neighbours, MATRIX[i][j]))

    relevant_squares = set()
    for neighbours, _ in restrictions:
        relevant_squares.update(neighbours)

    if not restrictions:
        return random.choice(list(unknown_squares)), True

    for r in range(1, MINE_COUNT + 1):
        for possible_mines in itertools.combinations(relevant_squares, r):
            simulated_mines = set(get_index(i, j) for i, j in possible_mines)
            is_solution = True

            for neighbours, mine_count in restrictions:
                current_mines = sum(1 for square in neighbours if get_index(*square) in simulated_mines)
                if current_mines != mine_count:
                    is_solution = False
                    break

            if is_solution:
                for square in unknown_squares:
                    if get_index(*square) not in simulated_mines:
                        return square, False

    return random.choice(list(unknown_squares)), True


def check_neighbours(i, j):
    count = 0
    opts = []
    for k in range(i - 1, i + 2):
        for l in range(j - 1, j + 2):
            if -1 < k < ROWS and -1 < l < COLUMNS:
                if MATRIX[k][l] == '?':
                    opts.append((k, l))
                    count += 1
    return opts, count


def heuristic_solve():
    numbered_squares = []
    unknown_squares = set()

    for i in range(ROWS):
        for j in range(COLUMNS):
            if MATRIX[i][j] != '?':
                numbered_squares.append((i, j))
            else:
                unknown_squares.add((i, j))

    flagged_squares = set()
    safe_squares = set()

    for i, j in numbered_squares:
        unknown_neighbours, num_mines = check_neighbours(i, j)

        if len(unknown_neighbours) == num_mines:
            for square in unknown_neighbours:
                flagged_squares.add(get_index(*square))
        elif num_mines == 0:
            for square in unknown_neighbours:
                safe_squares.add(square)

    if safe_squares:
        square_to_reveal = random.choice(list(safe_squares))
        return square_to_reveal, False
    elif unknown_squares:
        square_to_reveal = random.choice(list(unknown_squares))
        return square_to_reveal, False

    return random.choice(list(unknown_squares)), True
