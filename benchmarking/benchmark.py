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

def optimal_player_move(board):
    """Simulate Optimal Player Move."""
    col, _ = minimax(board, 3, -float('inf'), float('inf'), False)
    row = get_next_open_row(board, col)
    return row, col

def play_game(depth, optimal_opponent=False):
    """
    Simulate a game between the AI and a random player.
    Returns:
    - 1 if AI wins
    - -1 if Random player wins
    - 0 if draw
    """
    board = create_board()
    game_over = False
    turn = 'AI'
    ai_move_times = []  # list to track the time of each AI move
    move_count = 0
    while not game_over:
        if turn == 'AI':
            start_time = time.time()  
            col, _ = minimax(board, depth, -float('inf'), float('inf'), True)
            row = get_next_open_row(board, col)
            set_piece(board, row, col, 'X')  
            end_time = time.time()  
            time_taken = end_time - start_time
            ai_move_times.append(time_taken)  # save AI move time
            if winning_move(board, 'X'):
                return 1, ai_move_times, move_count  

            turn = 'PLAYER'

        else:  # Random player's turn
            row, col = optimal_player_move(board) if optimal_opponent else random_player_move(board)
            set_piece(board, row, col, 'O') 
            if winning_move(board, 'O'):
                return -1, ai_move_times, move_count
            turn = 'AI'
        move_count += 1
        if len(get_valid_locations(board)) == 0:
            return 0, ai_move_times, move_count  # It's a draw


def benchmark_win_rate(depth, games=10, optimal_opponent=False):
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
        result, ai_move_times, move_count = play_game(depth, optimal_opponent)  
        results[result] += 1
        print("Move count for game %d is %d" % (_+1, move_count))
        all_ai_move_times.extend(ai_move_times)  # save timing data from game

    win_rate = (results[1] / games) * 100  # win rate percentage
    print(f"AI Win Rate: {win_rate:.2f}%")
    print(f"Results: {results}")

    print("Average Time per AI Move: %.4f seconds" % (sum(all_ai_move_times) / len(all_ai_move_times) if all_ai_move_times else 0))
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
    benchmark_win_rate(DEPTH, optimal_opponent=False)
