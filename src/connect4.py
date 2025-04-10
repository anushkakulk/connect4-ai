import random
import time


ROWS, COLS = 6, 7
PLAYER, AI = 'O', 'X'
EMPTY = '_'

# opening book (column preferences, prefer the middle columns)
OPENING_BOOK = [3, 2, 4, 1, 5, 0, 6]

# transposition table, to store previously evaluated board states for optimization
transposition_table = {}

def create_board() -> None:
    """Create a new Connect 4 board"""
    transposition_table.clear()
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def print_board(board: list) -> None:
    """Print the current state of the board.
    
    Args:
    -   board (list): The current state of the board.
    """
    for row in board:
        print(' '.join(row))
    print(' '.join(map(str, range(COLS))))

def is_valid(board: list, col: int) -> bool:
    """Check if a column is valid for a move.
    
    Args:
    -  board (list): The current state of the board.
    -  col (int): The column to check if topmost position is empty.

    Returns:
    -  bool: True if the column is valid, False otherwise.
    """
    return col >= 0 and col <= 6 and board[0][col] == EMPTY

def get_next_open_row(board: list , col: int) -> int:
    """Get the next open row in a column.
    
    Args:
    -  board (list): The current state of the board.
    -  col (int): The column to get the row number of the topmost empty pos.

    Returns:
    -  int: The row number of the topmost empty position in the column.
    """
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            return row

def set_piece(board: list, row: list, col:list, piece:str) -> None:
    """Places given piece on the board at row, col position.

    Args:
    -  board (list): The current state of the board.
    -  row (int): The row to place the piece in.
    -  col (int): The column to place the piece in.
    -  piece (str): The piece to place ('X' or 'O').
    """
    board[row][col] = piece

def winning_move(board, piece):
    """Check if the last move was a winning move."""
    for c in range(COLS - 3):
        for r in range(ROWS):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True

    return False

def is_terminal(board):
    """Check if the game is over (win or draw)."""
    return winning_move(board, PLAYER) or winning_move(board, AI) or len(get_valid_locations(board)) == 0

def get_valid_locations(board):
    """Get a list of valid columns for the next move."""
    return [col for col in range(COLS) if is_valid(board, col)]

def evaluation(window, piece):
    """Evaluate a window of 4 cells for scoring"""
    score = 0
    opp_piece = PLAYER if piece == AI else AI

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 10
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 4

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 8

    return score

def score_position(board, piece):
    """"Score the board from the perspective of the given piece."""
    score = 0

    center_array = [board[i][COLS // 2] for i in range(ROWS)]
    center_count = center_array.count(piece)
    score += center_count * 6

    for r in range(ROWS):
        row_array = [board[r][c] for c in range(COLS)]
        for c in range(COLS - 3):
            window = row_array[c:c + 4]
            score += evaluation(window, piece)

    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS - 3):
            window = col_array[r:r + 4]
            score += evaluation(window, piece)

    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluation(window, piece)

    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + 3 - i][c + i] for i in range(4)]
            score += evaluation(window, piece)

    return score

def hash_board(board, depth):
    """Generate a hash for the current board state and depth to save in transition table."""
    return ''.join([''.join(row) for row in board]) + str(depth)

def minimax(board:list, depth:int, alpha:float, beta:float, maximizingPlayer:bool) -> tuple:
    """ Minimax algorithm with alpha-beta pruning to determine the optimal move.

    Recursively explores possible future game states up to a given depth,
    evaluating moves to select the best possible outcome for the AI, assuming that both 
    the AI and the human player play optimally.

    Args:
    - board: The current game state, represented as a 2D list.
    - depth: The maximum depth to explore in the game tree (limits recursion for efficiency).
    - alpha: The best value that the maximizer (AI) currently can guarantee.
    - beta: The best value that the minimizer (human player) currently can guarantee.
    - maximizingPlayer: Boolean flag indicating if the current move is by the maximizing player (AI).

    Returns:
    - tuple: (best_column, score)
        - best_column: The column index (0-6) of the best move found at this node.
        - score: The score associated with this move (high positive for good AI positions,
                 high negative for good player positions).

    Algorithm Explanation:
    - If the current board state is already terminal (win/loss/draw) or if depth == 0:
        -> Return an evaluation of the board (score).
    - If maximizingPlayer is True:
        -> The AI's turn. Aim to maximize the score.
        -> Iterate through all valid moves, simulate the move, recursively call minimax,
           and track the move with the highest score.
        -> Use alpha-beta pruning:
            - Update alpha with the best score found so far.
            - If alpha >= beta, prune the branch (no need to explore further).
    - If maximizingPlayer is False:
        -> The human player's turn. Aim to minimize the score.
        -> Iterate through all valid moves, simulate the move, recursively call minimax,
           and track the move with the lowest score.
        -> Use alpha-beta pruning:
            - Update beta with the lowest score found so far.
            - If alpha >= beta, prune the branch.

    Optimization:
    - Uses a transposition table (board state hashing) to cache evaluated positions
      and avoid redundant calculations.
    - Prefers center column moves (strategy: control the center for higher chances of winning).

    Notes:
    - Higher depth increases AI strength but slows down decision-making.
    - Alpha-beta pruning significantly reduces the number of nodes evaluated,
      speeding up the decision process.
    """

    board_hash = hash_board(board, depth)
    if board_hash in transposition_table:
        return transposition_table[board_hash]

    valid_locations = get_valid_locations(board)
    valid_locations.sort(key=lambda c: abs(COLS // 2 - c))  # Center-first move ordering
    terminal_pos = is_terminal(board)

    if depth == 0 or terminal_pos:
        if terminal_pos:
            if winning_move(board, AI):
                return (None, float('inf'))
            elif winning_move(board, PLAYER):
                return (None, -float('inf'))
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI))

    if maximizingPlayer:
        value = -float('inf')
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = [r[:] for r in board]
            set_piece(temp_board, row, col, AI)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        transposition_table[board_hash] = (column, value)
        return column, value

    else:
        value = float('inf')
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = [r[:] for r in board]
            set_piece(temp_board, row, col, PLAYER)
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        transposition_table[board_hash] = (column, value)
        return column, value

def get_ai_move(board):
    if sum(row.count(AI) + row.count(PLAYER) for row in board) < 2:
        for col in OPENING_BOOK:
            if is_valid(board, col):
                return col

    start = time.time()
    col, _ = minimax(board, 7, -float('inf'), float('inf'), True)
    end = time.time()
    print(f"AI move calculated in {end - start:.4f} seconds")
    return col

def play_game():
    board = create_board()
    game_over = False
    print("\nWelcome to Connect 4!")
    print("You are 'O' and the AI is 'X'.")
    print("The board columns are numbered from 0 to 6.\n")

    print_board(board)
    print('-------------\n')

    turn = random.choice(['PLAYER', 'AI'])
    print(f"{turn} goes first!")

    while not game_over:
        if turn == 'PLAYER':
            try:
                col = int(input("Your turn (0-6): \n"))
                if is_valid(board, col):
                    row = get_next_open_row(board, col)
                    set_piece(board, row, col, PLAYER)

                    if winning_move(board, PLAYER):
                        print_board(board)
                        print("You win!\n")
                        game_over = True
                    turn = 'AI'
                    print_board(board)
                    print('-------------\n')
                else:
                    print("Invalid move, try again.")
            except ValueError:
                print("Please enter a valid integer between 0 and 6.")

        else:  # AI Turn
            print("AI's turn...")
            col = get_ai_move(board)
            if is_valid(board, col):
                row = get_next_open_row(board, col)
                set_piece(board, row, col, AI)

                if winning_move(board, AI):
                    print_board(board)
                    print("AI wins!\n")
                    game_over = True
                turn = 'PLAYER'
                print_board(board)
                print('-------------\n')

        if not game_over and len(get_valid_locations(board)) == 0:
            print("Game is a draw!\n")
            game_over = True

if __name__ == "__main__":
    play_game()
