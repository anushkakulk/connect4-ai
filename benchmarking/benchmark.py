import time
import random
from connect4 import minimax, get_valid_locations, get_next_open_row, set_piece, winning_move, create_board, PLAYER, AI
import matplotlib.pyplot as plt

def benchmark_speed(board, max_depth):
    speeds = []
    
    for depth in range(1, max_depth + 1):
        start_time = time.time()
        col, _ = minimax(board, depth, -float('inf'), float('inf'), True)  # AI move
        end_time = time.time()
        
        speeds.append(end_time - start_time)
        print(f"Depth {depth}: {end_time - start_time:.4f} seconds")

    plt.plot(range(1, max_depth + 1), speeds, label="AI Speed", marker='o')
    plt.xlabel("Depth")
    plt.ylabel("Time (seconds)")
    plt.title("AI Speed Benchmark vs. Depth")
    plt.grid(True)
    plt.show()


def random_player_move(board):
    """Pick a random valid column."""
    valid_moves = get_valid_locations(board)
    col = random.choice(valid_moves)
    row = get_next_open_row(board, col)
    return row, col


def play_game(depth):
    """
    Simulate a game between the AI and a random player.
    Returns:
    - 1 if AI wins
    - -1 if Random player wins
    - 0 if draw
    """
    board = create_board()
    game_over = False
    turn = random.choice(['PLAYER', 'AI'])
    ai_move_times = []  # List to track the time of each AI move

    while not game_over:
        if turn == 'AI':
            start_time = time.time()  
            col, _ = minimax(board, depth, -float('inf'), float('inf'), True)
            row = get_next_open_row(board, col)
            set_piece(board, row, col, 'X')  # AI's piece is 'X'
            end_time = time.time()  # End measuring time after AI's move

            ai_move_times.append(end_time - start_time)  # Time taken by the AI to decide its move
            if winning_move(board, 'X'):
                return 1, ai_move_times  # Return AI's win and the move time

            turn = 'PLAYER'

        else:  # Random player's turn
            row, col = random_player_move(board)
            set_piece(board, row, col, 'O')  # Random player's piece is 'O'
            if winning_move(board, 'O'):
                return -1, ai_move_times  # Return random player's win, no AI move time for player's turn
            turn = 'AI'

        if len(get_valid_locations(board)) == 0:
            return 0, 0  # It's a draw


def benchmark_win_rate(depth, games=10):
    """
    Benchmark AI win rate against a random player and track AI move time.

    Parameters:
    - depth: AI search depth.
    - games: Number of games to simulate.

    Returns:
    - Win rate percentage.
    """
    results = {1: 0, -1: 0, 0: 0}  # 1 -> AI win, -1 -> Player win, 0 -> Draw
    all_ai_move_times = []  #  track all AI move times across games

    for _ in range(games):
        print("Simulating game %d/%d..." % (_ + 1, games))
        result, ai_move_times = play_game(depth)  
        results[result] += 1
        all_ai_move_times.extend(ai_move_times)  # save timing data from game

    win_rate = (results[1] / games) * 100  # win rate percentage
    print(f"AI Win Rate: {win_rate:.2f}%")
    print(f"Results: {results}")

    # Plotting AI Move Times
    plt.plot(all_ai_move_times, label=f"AI Move Time (Depth {depth})", marker='o')
    plt.xlabel("Move #")
    plt.ylabel("Time (seconds)")
    plt.title(f"AI Move Times Across {games} Games (Depth {depth})")
    plt.grid(True)
    plt.show()

    return win_rate


if __name__ == "__main__":
    DEPTH = 7  

    print("Running AI speed benchmark...")
    benchmark_speed(create_board(), DEPTH)

    print("\nRunning AI win rate benchmark vs random player...")
    benchmark_win_rate(DEPTH)
