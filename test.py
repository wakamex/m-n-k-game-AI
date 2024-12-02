from src.Agent import Agent
import numpy as np

EMPTY = -1

def print_board(board_size, board):
    print("---------")
    for i in range(board_size[1]):
        print_row = []
        for j in range(board_size[0]):
            if board[i * board_size[0] + j] == 0:
                print_row.append("X")
            if board[i * board_size[0] + j] == 1:
                print_row.append("O")
            if board[i * board_size[0] + j] == EMPTY:
                print_row.append("-")
        print(print_row)
    print("---------")

def test_horizontal_sequence():
    board_size = [3, 3]
    agent = Agent(player_number=1, board_size=board_size, winning_size=3, scoring_array=[0, 1, 2, 3], circle_of_two=[(1, 0), (0, 1)])
    board_state = np.array([1, 1, 1, -1, -1, -1, -1, -1, -1], dtype=np.int32)
    counts = agent.count_sequences(board_state)
    # 6 empty spaces, 3 singles, 2 doubles, 1 triple for player 1
    expected_counts = np.array([[6, 0, 0, 0], [6, 3, 2, 1]], dtype=np.int32)
    np.testing.assert_array_equal(counts, expected_counts)

def test_count_on_empty_board():
    agent = Agent(player_number=1, board_size=[3, 3], winning_size=3, scoring_array=[0, 1, 2, 3], circle_of_two=[(1, 0), (0, 1)])
    board_state = np.full(9, EMPTY, dtype=np.int32)  # Empty board
    counts = agent.count_sequences(board_state)
    expected_counts = np.array([[9, 0, 0, 0], [9, 0, 0, 0]], dtype=np.int32)  # Only empty spaces, no sequences
    np.testing.assert_array_equal(counts, expected_counts)

def test_memory_update_after_move():
    agent = Agent(player_number=1, board_size=[3, 3], winning_size=3, scoring_array=[0, 1, 2, 3], circle_of_two=[(1, 0), (0, 1)])
    initial_board_state = np.full(9, EMPTY, dtype=np.int32)
    agent.new_move_played(initial_board_state)
    new_board_state = initial_board_state.copy()
    new_board_state[4] = agent.player_number
    agent.new_move_played(new_board_state)
    expected_last_move_played = np.array([1, 1], dtype=np.int32)
    np.testing.assert_array_equal(agent.memory["last_move_played"], expected_last_move_played)

def test_board_with_tokens():
    agent = Agent(player_number=1, board_size=[3, 3], winning_size=3, scoring_array=[0, 1, 2, 3], circle_of_two=[(1, 0), (0, 1)])
    board_state = np.array([1, -1, -1, -1, 0, -1, -1, -1, 1], dtype=np.int32)
    print_board([3,3], board_state)
    counts = agent.count_sequences(board_state)
    # 6 empty spaces, 1 single for player 0, 2 singles for player 1
    expected_counts = np.array([[6, 1, 0, 0], [6, 2, 0, 0]], dtype=np.int32)
    np.testing.assert_array_equal(counts, expected_counts)

def test_board_with_line():
    agent = Agent(player_number=1, board_size=[3, 3], winning_size=3, scoring_array=[0, 1, 2, 3], circle_of_two=[(1, 0), (0, 1)])
    board_state = np.array([1, -1, 0, 1, 0, -1, 1, -1, 0], dtype=np.int32)
    print_board([3,3], board_state)
    counts = agent.count_sequences(board_state)
    # 3 empty spaces, 3 singles, 2 doubles, 1 triple for player 1 (vertical line)
    # 3 empty spaces, 3 singles, 2 doubles, 0 triples for player 0 (diagonal X's)
    expected_counts = np.array([[3, 3, 2, 0], [3, 3, 2, 1]], dtype=np.int32)
    np.testing.assert_array_equal(counts, expected_counts)

def test_single_token_player_one():
    agent = Agent(player_number=1, board_size=[3, 3], winning_size=3, scoring_array=[0, 1, 2, 3], circle_of_two=[(1, 0), (0, 1)])
    board_state = np.array([-1, -1, -1, -1, 0, -1, -1, -1, -1], dtype=np.int32)
    counts = agent.count_sequences(board_state)
    expected_counts = np.array([[8, 1, 0, 0], [8, 0, 0, 0]], dtype=np.int32)
    np.testing.assert_array_equal(counts, expected_counts)

def test_single_token_player_two():
    agent = Agent(player_number=1, board_size=[3, 3], winning_size=3, scoring_array=[0, 1, 2, 3], circle_of_two=[(1, 0), (0, 1)])
    board_state = np.array([-1, -1, -1, -1, 1, -1, -1, -1, -1], dtype=np.int32)
    counts = agent.count_sequences(board_state)
    expected_counts = np.array([[8, 0, 0, 0], [8, 1, 0, 0]], dtype=np.int32)
    np.testing.assert_array_equal(counts, expected_counts)
