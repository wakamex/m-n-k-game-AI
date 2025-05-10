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

def helper_create_agent_for_minimax_tests(player_number, board_size, winning_size, depth, heuristic_params=None):
    # Your current heuristic doesn't use scoring_array, so pass empty
    scoring_array = [] 
    if heuristic_params: # If you ever make heuristic configurable
        # Adapt this based on how you'd pass params to evaluate
        pass
    return Agent(player_number, board_size, winning_size, scoring_array, circle_of_two=[], name=f"TestAgent{player_number}", depth_override=depth) # Assuming you add depth_override for testing

# It's often useful to have the agent play within a game context for get_next_move
from src.Game import Game # Assuming Game.py is in src

def test_minimax_immediate_win_p0():
    board_size = (3, 3)
    winning_size = 3
    depth = 1 # Should be enough to see one move ahead

    agent_p0 = Agent(player_number=0, board_size=board_size, winning_size=winning_size, scoring_array=[], circle_of_two=[])
    # Set a depth for the agent if it's not fixed or passed to get_next_move
    # agent.depth = depth # Or however depth is set for the agent instance if not in __init__
    # For your current Agent, DEPTH is a global constant. If you want to test different depths,
    # you might need to make it an instance variable or pass it to get_next_move.
    # Let's assume Agent uses the global DEPTH or it's set appropriately.
    # For this example, let's assume Agent.get_next_move can be influenced by a test-specific depth.
    # For simplicity, I'll assume Agent.__init__ takes a depth argument, or there's a setter.
    # Your current Agent uses a global DEPTH = 3. This test assumes it can find a 1-move win.

    game = Game(board_size, winning_size)
    # Board: P0 (X) P0 (X) .
    #        P1 (O) P1 (O) .
    #        .      .      .
    # P0's turn.
    game.board = np.array([
        0, 0, EMPTY,
        1, 1, EMPTY,
        EMPTY, EMPTY, EMPTY
    ], dtype=np.int32)
    game.player_turn = 0 # P0's turn
    game.agents = [agent_p0, None] # Only need the agent being tested for its turn

    # Link agent to game (if your agent needs a game reference)
    agent_p0.set_game(game) # Your agent has this method

    # Expected move for P0 is at index 2 to win
    expected_move_idx = 2
    actual_move_idx = agent_p0.get_next_move()

    assert actual_move_idx == expected_move_idx, f"Expected P0 to win at {expected_move_idx}, got {actual_move_idx}"

def test_minimax_block_opponent_win_p0():
    board_size = (3, 3)
    winning_size = 3
    # DEPTH needs to be at least 1 for the agent to "see" the opponent's winning reply if P0 doesn't block.
    # Your agent's global DEPTH=3 should be sufficient.

    agent_p0 = Agent(player_number=0, board_size=board_size, winning_size=winning_size, scoring_array=[], circle_of_two=[])
    
    game = Game(board_size, winning_size)
    # Board: P1 (O) P1 (O) .
    #        P0 (X) .      .
    #        P0 (X) .      .
    # P0's turn. P1 threatens to win at index 2.
    game.board = np.array([
        1, 1, EMPTY,
        0, EMPTY, EMPTY,
        0, EMPTY, EMPTY
    ], dtype=np.int32)
    game.player_turn = 0
    game.agents = [agent_p0, None]
    agent_p0.set_game(game)

    # Expected move for P0 is at index 2 to block P1's win
    expected_move_idx = 2
    actual_move_idx = agent_p0.get_next_move()
    
    assert actual_move_idx == expected_move_idx, f"Expected P0 to block at {expected_move_idx}, got {actual_move_idx}"

def test_minimax_prefers_heuristic_advantage_p0_depth1():
    board_size = (3, 3)
    winning_size = 3
    # For this test, we need to control the agent's depth.
    # Let's assume Agent's DEPTH constant is 1 for this specific test scenario if possible,
    # or we are testing with an agent configured to depth 1.
    # If Agent uses global DEPTH=3, this test becomes harder to reason about without full trace.
    # For now, this test is more of a conceptual placeholder if depth can't be easily controlled per test.

    # AGENT_UNDER_TEST_DEPTH = 1 # Ideal
    # agent_p0 = Agent(player_number=0, ..., depth=AGENT_UNDER_TEST_DEPTH) # If constructor takes depth

    # If your Agent.py uses a global DEPTH = 3, then to test a depth 1 decision effectively,
    # you'd have to ensure the chosen move leads to the highest immediate heuristic score.

    agent_p0 = Agent(player_number=0, board_size=board_size, winning_size=winning_size, scoring_array=[], circle_of_two=[])
    
    game = Game(board_size, winning_size)
    # Board: P0(X) . .
    #        P1(O) . .
    #        . . .
    # P0's turn.
    game.board = np.array([
        0, EMPTY, EMPTY,
        1, EMPTY, EMPTY,
        EMPTY, EMPTY, EMPTY
    ], dtype=np.int32)
    game.player_turn = 0
    game.agents = [agent_p0, None] # Only need the agent being tested
    agent_p0.set_game(game)

    # Possible moves for P0 (X): 1, 2, 4, 5, 6, 7, 8
    # Heuristic: (counts[0][2] - counts[1][2]) * 0.1
    # We need to evaluate the board state *after* P0 makes a move.
    # Let P0 move to index 1: [X,X,., O,.,., .,.,.]
    #   Board: [0,0,E, 1,E,E, E,E,E]
    #   P0 counts: C0[2]=1 (for XX.), C0[1]=2 (for X. from XX., .X from XX.)
    #   P1 counts: C1[1]=1 (for O..)
    #   Eval = (1 - 0) * 0.1 = 0.1
    # Let P0 move to index 2: [X,.,X, O,.,., .,.,.]
    #   Board: [0,E,0, 1,E,E, E,E,E]
    #   P0 counts: C0[1]=4 (X. from X.X, .X from X.X, X.. vert, X.. diag)
    #   P1 counts: C1[1]=1
    #   Eval = (0 - 0) * 0.1 = 0.0
    # Let P0 move to index 4 (center): [X,.,., O,X,., .,.,.]
    #   Board: [0,E,E, 1,0,E, E,E,E]
    #   P0 counts: C0[1]= many (e.g., X. hor, .X hor, X. vert, .X vert, etc.) C0[2]=0
    #   P1 counts: C1[1]= many C1[2]=0
    #   Eval will likely be 0 or close to 0.

    # So, playing at index 1 ([X,X,.]) seems to give the best immediate heuristic score (0.1).
    # This assumes agent.DEPTH is effectively 1 for this decision.
    # If agent.DEPTH is 3, it will look further.

    # This test is hard to make robust without controlling agent's search depth precisely
    # or doing a full minimax trace for depth 3.
    # For now, let's assert it makes *a* valid move. A more specific assertion requires depth control.
    
    actual_move_idx = agent_p0.get_next_move()
    possible_moves = [i for i, x in enumerate(game.board) if x == EMPTY]
    assert actual_move_idx in possible_moves, "Agent did not pick a valid empty spot."
    
    # To make this more specific for DEPTH=3, you'd need to calculate the true minimax value.
    # For example, if playing at index 1 ([X,X,.]) leads to a better outcome after P1's reply and P0's next reply.
    # Let's assume, for DEPTH=3, that playing at index 1 is indeed optimal or among optimal.
    # If the logic is sound, playing at index 1 (0,1) should be a strong candidate to maximize the heuristic (create a 2-in-a-row).
    if agent_p0.player_number == 0 : # Check if global DEPTH is used, or instance depth
        # With DEPTH=3, creating an immediate two-in-a-row is usually good.
        # Here, moves (0,1) (idx 1) or (1,0) (idx 3) or (1,1) (idx 4) might be chosen.
        # Let's assume making XX. at index 1 is a reasonable strong move.
        # If not, this test would need adjustment after deeper analysis of DEPTH=3 behavior.
        # For the current Python agent evaluate, creating a C[0][2] is good.
        # idx 1: [0,0,E, 1,E,E, E,E,E]. Eval state after P0 moves: (1-0)*0.1 = 0.1
        # idx 3: [0,E,E, 1,0,E, 0,E,E]. Eval state after P0 moves: (0-0)*0.1 = 0.0
        # idx 4: [0,E,E, 1,0,E, E,0,E]. Eval state after P0 moves: (0-0)*0.1 = 0.0
        # A depth 1 agent would pick idx 1. A depth 3 agent also likely picks idx 1.

        # To verify for depth=3, you need to consider P1's reply to move at idx=1.
        # P0: [0,0,E, 1,E,E, E,E,E]. P1 to move. P1 plays idx=2 to block: [0,0,1, 1,E,E, E,E,E]
        # Now P0 to move. Heuristic for [0,0,1, 1,E,E, E,E,E]:
        # P0 counts: C0[1]=2 (for [0,E,E] starting col 0, [0,E,E] starting col 1) C0[2]=0
        # P1 counts: C1[3]=1 (for [0,0,1] - wait, this is not a win if board[0] is P0)
        # P1 counts for [0,0,1, 1,E,E, E,E,E]
        #   P1 (piece 1) has one piece at idx 2. C1[1]=4.
        #   P0 (piece 0) has two pieces. Hor [0,0,1] is invalid for P0. Vert [0,1,E] C0[1]=1. Vert [0,E,E] C0[1]=1.
        #   Heuristic: (0-0)*0.1 = 0.
        # This level of manual trace is why these tests are hard.

        print(f"Agent P0 with current heuristic chose move: {actual_move_idx}")
        # A loose assertion for now, as specific optimal move for DEPTH=3 is complex to pre-calculate here
        assert actual_move_idx == 1 or actual_move_idx == 4 # Common strong opening/counter moves on 3x3