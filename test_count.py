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
    winning_size = 3
    agent = Agent(player_number=1, board_size=board_size, winning_size=winning_size, scoring_array=[0, 1, 2, 3], circle_of_two=[(1, 0), (0, 1)])
    board_state = np.array([1, 1, 1, -1, -1, -1, -1, -1, -1], dtype=np.int32)
    counts = agent.count_sequences(board_state)
    # For Player 1 (agent, piece '1'):
    # counts[1][0] = 6 (empty cells)
    # counts[1][1] = 5 (five 3-cell lines like [1,-1,-1])
    # counts[1][2] = 0
    # counts[1][3] = 1 (the [1,1,1] line)
    # For Player 0 (piece '0'): No pieces.
    expected_counts = np.array([[6, 0, 0, 0], [6, 5, 0, 1]], dtype=np.int32)
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
    # P0 (piece '0') has 1 piece at center. It forms part of 3 valid 3-cell lines (1 hor, 1 vert, 1 diag TR-BL).
    # P1 (piece '1') has 2 pieces at corners. Each forms part of 2 valid 3-cell lines (1 hor, 1 vert for each).
    expected_counts = np.array([[6, 3, 0, 0], [6, 4, 0, 0]], dtype=np.int32)
    np.testing.assert_array_equal(counts, expected_counts)

def test_board_with_line():
    agent = Agent(player_number=1, board_size=[3, 3], winning_size=3, scoring_array=[0, 1, 2, 3], circle_of_two=[(1, 0), (0, 1)])
    board_state = np.array([1, -1, 0, 1, 0, -1, 1, -1, 0], dtype=np.int32)
    print_board([3,3], board_state)
    counts = agent.count_sequences(board_state)
    # P1 (piece '1') has a winning vertical line [1,1,1] at col 0 -> counts[1][3]=1. No other "P1-only" lines.
    # P0 (piece '0') has:
    #   - one line with one '0' and two EMPTY: board[[1,4,7]] is [-1,0,-1] -> counts[0][1]=1
    #   - one line with two '0's and one EMPTY: board[[2,5,8]] is [0,-1,0] -> counts[0][2]=1
    expected_counts = np.array([[3, 1, 1, 0], [3, 0, 0, 1]], dtype=np.int32)
    np.testing.assert_array_equal(counts, expected_counts)

def test_single_token_player_one(): # Agent is P1, board has one P0 token
    agent = Agent(player_number=1, board_size=[3, 3], winning_size=3, scoring_array=[0, 1, 2, 3], circle_of_two=[(1, 0), (0, 1)])
    board_state = np.array([-1, -1, -1, -1, 0, -1, -1, -1, -1], dtype=np.int32)
    counts = agent.count_sequences(board_state)
    # P0 (piece '0') at center. Forms part of 4 valid 3-cell lines (1 hor, 1 vert, 2 diag).
    # P1 (piece '1') has no pieces.
    expected_counts = np.array([[8, 4, 0, 0], [8, 0, 0, 0]], dtype=np.int32)
    np.testing.assert_array_equal(counts, expected_counts)

def test_single_token_player_two(): # Agent is P1, board has one P1 token
    agent = Agent(player_number=1, board_size=[3, 3], winning_size=3, scoring_array=[0, 1, 2, 3], circle_of_two=[(1, 0), (0, 1)])
    board_state = np.array([-1, -1, -1, -1, 1, -1, -1, -1, -1], dtype=np.int32)
    counts = agent.count_sequences(board_state)
    # P1 (piece '1') at center. Forms part of 4 valid 3-cell lines.
    # P0 (piece '0') has no pieces.
    expected_counts = np.array([[8, 0, 0, 0], [8, 4, 0, 0]], dtype=np.int32)
    np.testing.assert_array_equal(counts, expected_counts)

# Add these new tests to your test.py

def test_evaluate_p0_has_more_two_threats():
    board_size = [3, 3]
    winning_size = 3
    agent_p0 = Agent(player_number=0, board_size=board_size, winning_size=winning_size, scoring_array=[], circle_of_two=[]) # P0 is maximizing

    # P0: X X .  => counts[0][2] = 1 (horizontally)
    # P1: . O .  => counts[1][2] = 0
    #       . . .
    board_state = np.array([
        0, 0, EMPTY,
        EMPTY, 1, EMPTY,
        EMPTY, EMPTY, EMPTY
    ], dtype=np.int32)
    game_state = {"board_state": board_state}
    
    # counts[0][2] = 1 (for [0,0,E] from 0,0,E)
    # +1 for [0,E,0] (from 0,E,0), if it considers non-contiguous as part of a line
    # The current count_sequences logic for row 0:
    # idx=0, seg=[0,0,E]. P0_len=2. counts[0][2]++
    # For P1:
    # idx=0, seg=[E,1,E]. P1_len=1. counts[1][1]++
    
    # Let's trace counts for board [0,0,E, E,1,E, E,E,E]
    # P0:
    # Hor: [0,0,E] -> P0 len 2. counts[0][2]+=1
    # Vert: [0,E,E] -> P0 len 1. counts[0][1]+=1
    # Vert: [0,E,E] (col 1) -> P0 len 1. counts[0][1]+=1
    # Diag TLBR: [0,1,E] -> Invalid for P0.
    # Diag TRBL: [E,1,E] -> Invalid for P0.
    # So, counts[0] = [5, 2, 1, 0]
    # P1:
    # Hor: [E,1,E] -> P1 len 1. counts[1][1]+=1
    # Vert: [0,1,E] -> Invalid for P1
    # Vert: [0,1,E] (col 1) -> Invalid for P1
    # Vert: [E,1,E] (col 2) -> P1 len 1. counts[1][1]+=1
    # Diag TLBR: [0,1,E] -> Invalid for P1
    # Diag TRBL: [E,1,E] -> P1 len 1. counts[1][1]+=1
    # So, counts[1] = [5, 3, 0, 0]

    # score = (counts[0][2] - counts[1][2]) * 0.1 = (1 - 0) * 0.1 = 0.1
    expected_eval = 0.1
    actual_eval = agent_p0.evaluate(game_state, winner=EMPTY)
    np.testing.assert_almost_equal(actual_eval, expected_eval, decimal=5)

def test_evaluate_p1_has_more_two_threats():
    board_size = [3, 3]
    winning_size = 3
    agent_p0 = Agent(player_number=0, board_size=board_size, winning_size=winning_size, scoring_array=[], circle_of_two=[]) # P0 is maximizing

    # P0: X . .
    # P1: O O .
    #       . . .
    board_state = np.array([
        0, EMPTY, EMPTY,
        1, 1, EMPTY,
        EMPTY, EMPTY, EMPTY
    ], dtype=np.int32)
    game_state = {"board_state": board_state}

    # P0: counts[0][2] = 0. (Line [0,E,E] gives counts[0][1]=1)
    # P1: counts[1][2] = 1 (for [1,1,E])
    # score = (0 - 1) * 0.1 = -0.1
    expected_eval = -0.1
    actual_eval = agent_p0.evaluate(game_state, winner=EMPTY)
    np.testing.assert_almost_equal(actual_eval, expected_eval, decimal=5)

def test_evaluate_equal_two_threats():
    board_size = [3, 3]
    winning_size = 3
    agent_p0 = Agent(player_number=0, board_size=board_size, winning_size=winning_size, scoring_array=[], circle_of_two=[])

    # P0: X X .
    # P1: O O .
    #       . . .
    board_state = np.array([
        0, 0, EMPTY,
        1, 1, EMPTY,
        EMPTY, EMPTY, EMPTY
    ], dtype=np.int32)
    game_state = {"board_state": board_state}
    
    # P0: counts[0][2] = 1
    # P1: counts[1][2] = 1
    # score = (1 - 1) * 0.1 = 0.0
    expected_eval = 0.0
    actual_eval = agent_p0.evaluate(game_state, winner=EMPTY)
    np.testing.assert_almost_equal(actual_eval, expected_eval, decimal=5)

def test_evaluate_p0_wins_overrides_heuristic():
    board_size = [3, 3]
    winning_size = 3
    agent_p0 = Agent(player_number=0, board_size=board_size, winning_size=winning_size, scoring_array=[], circle_of_two=[])
    
    # P0 wins, P1 might have some 2-threats but P0 win score should dominate.
    # P0: X X X
    # P1: O O .
    #       . . .
    board_state = np.array([
        0, 0, 0,
        1, 1, EMPTY,
        EMPTY, EMPTY, EMPTY
    ], dtype=np.int32)
    game_state = {"board_state": board_state}
    
    # P0 wins, evaluate should return 1.0
    expected_eval = 1.0
    actual_eval = agent_p0.evaluate(game_state, winner=0) # winner=0 for P0 win
    np.testing.assert_almost_equal(actual_eval, expected_eval, decimal=5)

def test_evaluate_p1_wins_overrides_heuristic():
    board_size = [3, 3]
    winning_size = 3
    agent_p0 = Agent(player_number=0, board_size=board_size, winning_size=winning_size, scoring_array=[], circle_of_two=[])
    
    # P1 wins, P0 might have some 2-threats but P1 win score should dominate.
    # P0: X X .
    # P1: O O O
    #       . . .
    board_state = np.array([
        0, 0, EMPTY,
        1, 1, 1,
        EMPTY, EMPTY, EMPTY
    ], dtype=np.int32)
    game_state = {"board_state": board_state}
    
    # P1 wins, evaluate for P0 should return -1.0
    expected_eval = -1.0
    actual_eval = agent_p0.evaluate(game_state, winner=1) # winner=1 for P1 win
    np.testing.assert_almost_equal(actual_eval, expected_eval, decimal=5)

def test_evaluate_draw_overrides_heuristic():
    board_size = [3, 3]
    winning_size = 3
    agent_p0 = Agent(player_number=0, board_size=board_size, winning_size=winning_size, scoring_array=[], circle_of_two=[])
    
    # A draw state, heuristic value might be non-zero but draw score (0.0) should be returned.
    board_state = np.array([ # Example draw
        0, 1, 0,
        1, 1, 0,
        0, 0, 1 
    ], dtype=np.int32)
    game_state = {"board_state": board_state}
    
    expected_eval = 0.0
    actual_eval = agent_p0.evaluate(game_state, winner=-2) # winner=-2 for draw
    np.testing.assert_almost_equal(actual_eval, expected_eval, decimal=5)

def test_count_horizontal_win_k4_on_4x4():
    board_size = [4, 4]
    winning_size = 4
    agent = Agent(player_number=1, board_size=board_size, winning_size=winning_size, scoring_array=[], circle_of_two=[])
    board_state = np.array([
        1, 1, 1, 1,
        -1,-1,-1,-1,
        -1,-1,-1,-1,
        -1,-1,-1,-1
    ], dtype=np.int32)
    counts = agent.count_sequences(board_state)

    # For Player 1 (piece '1'):
    # Empty cells = 12.
    # counts[1][4] = 1 (for OOOO line).
    # counts[1][1] = 6 (4 vertical [O...] lines, 1 TL-BR diag [O...] line, 1 TR-BL diag [O...] line).
    expected_counts = np.array([[12,0,0,0,0], [12,6,0,0,1]], dtype=np.int32) # Changed 5 to 6
    np.testing.assert_array_equal(counts, expected_counts)

def test_count_p0_two_pieces_k4_on_4x4():
    board_size = [4, 4]
    winning_size = 4
    # Agent is Player 0 (maximizer, piece '0')
    agent = Agent(player_number=0, board_size=board_size, winning_size=winning_size, scoring_array=[], circle_of_two=[])
    # Board: P0 (X) at (0,0) and (0,2). P1 (O) at (2,1).
    # X . X .
    # . . . .
    # . O . .
    # . . . .
    board_state = np.array([
        0,-1, 0,-1,
        -1,-1,-1,-1,
        -1, 1,-1,-1,
        -1,-1,-1,-1
    ], dtype=np.int32)
    counts = agent.count_sequences(board_state)

    # For Player 0 (piece '0'):
    # Empty cells = 13.
    # Horizontal line [X,.,X,.] starting at (0,0) -> counts[0][2]=1.
    # Vertical line [X,.,.,.] starting at (0,0) -> counts[0][1]=1.
    # Vertical line [X,.,.,.] starting at (0,2) -> counts[0][1]=1.
    # Diagonal TL-BR [X,.,.,.] starting at (0,0) -> counts[0][1]=1.
    # So, counts[0] = [13, 3, 1, 0, 0]

    # For Player 1 (piece '1'):
    # Empty cells = 13.
    # Piece 'O' at (2,1) (index 9).
    # Horizontal line [.,O,.,.] (board[8:12]) -> counts[1][1]=1.
    # Vertical line [.,.,O,.] (board[[1,5,9,13]]) -> counts[1][1]=1.
    # Diagonal TL-BR [.,O,.,.] (board[[4,9,14,X]]) -> counts[1][1]=1.
    # Diagonal TR-BL [.,.,O,.] (board[[3,6,9,12]]) -> counts[1][1]=1.
    # So, counts[1] = [13, 4, 0, 0, 0]
    expected_counts = np.array([[13,3,1,0,0], [13,4,0,0,0]], dtype=np.int32)
    np.testing.assert_array_equal(counts, expected_counts)

def test_count_p0_two_pieces_k4_on_4x4():
    board_size = [4, 4]
    winning_size = 4
    agent = Agent(player_number=0, board_size=board_size, winning_size=winning_size, scoring_array=[], circle_of_two=[])
    board_state = np.array([
        0,-1, 0,-1,
        -1,-1,-1,-1,
        -1, 1,-1,-1,
        -1,-1,-1,-1
    ], dtype=np.int32)
    counts = agent.count_sequences(board_state)

    # For Player 0 (piece '0'):
    # Horizontal line [X,.,X,.] (board[0:4]) -> counts[0][2]=1.
    # Vertical line [X,.,.,.] (col 0) -> counts[0][1]=1.
    # Vertical line [X,.,.,.] (col 2) -> counts[0][1]=1.
    # Diagonal TL-BR [X,.,.,.] (main) -> counts[0][1]=1.
    # So, counts[0] = [13, 3, 1, 0, 0]

    # For Player 1 (piece '1'):
    # Piece 'O' at (2,1) (index 9).
    # Horizontal: board[8:12] is [-1,1,-1,-1] -> counts[1][1]=1.
    # Vertical: board[[1,5,9,13]] is [-1,-1,1,-1] -> counts[1][1]=1.
    # Diagonal TL-BR: Main diag [0,-1,-1,-1] (contains P0), not valid for P1.
    # Diagonal TR-BL: Segment from idx=12 (board[12,9,6,3]) is [-1,1,-1,-1] -> counts[1][1]=1.
    # So, counts[1] = [13, 3, 0, 0, 0]
    expected_counts = np.array([[13,3,1,0,0], [13,3,0,0,0]], dtype=np.int32) # Changed P1 counts[1][1] from 4 to 3
    np.testing.assert_array_equal(counts, expected_counts)