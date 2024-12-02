from python import Python
from collections.vector import InlinedFixedVector

from Agent import AgentState, count_sequences, Sequences
from agent_utils import print_board

alias EMPTY = 0

def create_test_agent() -> AgentState:
    """Create a standard test agent configuration."""
    var scoring_array = InlinedFixedVector[Int, 1024](1024)
    for i in range(4):
        scoring_array[i] = i
    
    return AgentState(
        player_number=1,
        board_size_x=3,
        board_size_y=3,
        winning_size=3,
        scoring_array=scoring_array,
        restrict_moves=5
    )

def create_empty_board() -> InlinedFixedVector[Int, 1024]:
    """Create an empty 3x3 board."""
    var board = InlinedFixedVector[Int, 1024](9)
    # Initialize all cells to EMPTY
    for i in range(9):
        board[i] = EMPTY
    return board

fn assert_eval_equal(actual: Float64, expected: Float64, message: String) raises:
    """Assert that a Float64 evaluation value matches the expected value."""
    if actual != expected:
        print("Assertion failed:", message)
        print("Expected eval:", expected)
        print("Actual eval:", actual)
        raise Error("Assertion failed: " + message)

fn evaluate(state: AgentState, sequences: Sequences) -> Float64:
    """Evaluate a board position."""
    if sequences.win:
        return 1e6
    return Float64(sequences.count)

fn test_both_win() raises:
    """Test evaluating sequences for both players and calculate eval."""
    print("Running test_both_win...")
    var agent = create_test_agent()
    
    # Initialize board with sequences for both players
    var board = create_empty_board()
    board[0] = 1  # Player 1
    board[1] = 1  # Player 1
    board[2] = 1  # Player 1
    board[3] = 2  # Player 2
    board[4] = 2  # Player 2
    board[5] = 2  # Player 2
    
    # Print the board for debugging
    print_board(board, agent.board_size_x, agent.board_size_y)

    # Evaluate sequences and calculate eval for Player 1
    agent.player_number = 1
    var eval_player1 = evaluate(agent, count_sequences(agent, board))
    assert_eval_equal(eval_player1, 1000000.0, "Player 1 evaluation failed")
    
    # Evaluate sequences and calculate eval for Player 2
    agent.player_number = 2
    var eval_player2 = evaluate(agent, count_sequences(agent, board))
    assert_eval_equal(eval_player2, 1000000.0, "Player 2 evaluation failed")

fn test_empty_board() raises:
    """Test evaluating an empty board."""
    print("Running test_empty_board...")
    var agent = create_test_agent()
    var board = create_empty_board()
    
    var sequences = count_sequences(agent, board)
    var eval = evaluate(agent, sequences)
    assert_eval_equal(eval, 0.0, "Empty board should evaluate to 0")

fn test_single_sequence() raises:
    """Test evaluating a board with a single sequence."""
    print("Running test_single_sequence...")
    var agent = create_test_agent()
    var board = create_empty_board()
    board[0] = 1
    board[1] = 1
    
    print("Board state for single sequence:")
    print_board(board, agent.board_size_x, agent.board_size_y)
    
    var sequences = count_sequences(agent, board)
    var eval = evaluate(agent, sequences)
    assert_eval_equal(eval, 3.0, "Single sequence evaluation failed")

fn test_multiple_sequences() raises:
    """Test evaluating a board with multiple non-winning sequences."""
    print("Running test_multiple_sequences...")
    var agent = create_test_agent()
    var board = create_empty_board()
    board[0] = 1
    board[1] = 1
    board[3] = 1
    board[4] = 1
    
    print("Board state for multiple sequences:")
    print_board(board, agent.board_size_x, agent.board_size_y)
    
    var sequences = count_sequences(agent, board)
    var eval = evaluate(agent, sequences)
    assert_eval_equal(eval, 10.0, "Multiple sequences evaluation failed")

fn test_diagonal_win() raises:
    """Test evaluating a board with a diagonal winning sequence."""
    print("Running test_diagonal_win...")
    var agent = create_test_agent()
    var board = create_empty_board()
    board[0] = 1  # Top-left
    board[4] = 1  # Center
    board[8] = 1  # Bottom-right
    
    print_board(board, agent.board_size_x, agent.board_size_y)
    var sequences = count_sequences(agent, board)
    var eval = evaluate(agent, sequences)
    assert_eval_equal(eval, 1000000.0, "Diagonal win evaluation failed")

fn test_full_board() raises:
    """Test evaluating a completely filled board with no winner."""
    print("Running test_full_board...")
    var agent = create_test_agent()
    var board = create_empty_board()
    # Fill board in a way that prevents any winning sequence
    board[0] = 1; board[1] = 2; board[2] = 1
    board[3] = 2; board[4] = 1; board[5] = 2
    board[6] = 2; board[7] = 1; board[8] = 2
    
    print("Board state for full board:")
    print_board(board, agent.board_size_x, agent.board_size_y)
    
    agent.player_number = 1
    var sequences = count_sequences(agent, board)
    var eval = evaluate(agent, sequences)
    assert_eval_equal(eval, 7.0, "Full board evaluation failed")

fn main() raises:
    test_empty_board()
    test_single_sequence()
    test_multiple_sequences()
    test_diagonal_win()
    test_full_board()
    test_both_win()
    print("All tests passed!")
