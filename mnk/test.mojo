from python import Python
from collections.vector import InlinedFixedVector

from Agent import AgentState, count_sequences, Sequences
from Game import GameState

alias EMPTY = 0

fn create_test_agent() -> AgentState:
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

fn create_board_vector(values: InlinedFixedVector[Int, 1024]) -> InlinedFixedVector[Int, 1024]:
    """Create a board vector from a list of values."""
    var board = InlinedFixedVector[Int, 1024](len(values))
    for i in range(len(values)):
        board[i] = values[i]
    return board

fn assert_sequences_equal(actual: Sequences, expected_count: Int, expected_win: Bool, message: String) raises:
    """Assert that a Sequences value matches expected count and win status."""
    if actual.count != expected_count or actual.win != expected_win:
        print("Assertion failed:", message)
        print("Expected count:", expected_count, "win:", expected_win)
        print("Actual count:", actual.count, "win:", actual.win)
        raise Error("Assertion failed: " + message)

fn test_horizontal_sequence() raises:
    """Test counting horizontal sequences."""
    print("Running test_horizontal_sequence...")
    var agent = create_test_agent()
    
    # Test horizontal sequence
    var board = create_board_vector(InlinedFixedVector[Int, 1024](9))
    board[0] = 1  # X
    board[1] = 1  # X
    board[2] = 1  # X
    
    var counts = count_sequences(agent, board)
    
    # Expect:
    # - count = 6 (3 singles + 2 doubles + 1 triple)
    # - win = True (three in a row wins)
    assert_sequences_equal(counts, 6, True, "Horizontal sequence count mismatch")

fn test_vertical_sequence() raises:
    """Test counting vertical sequences."""
    print("Running test_vertical_sequence...")
    var agent = create_test_agent()
    
    # Create board with vertical line of player 1
    var board = create_board_vector(InlinedFixedVector[Int, 1024](9))
    board[0] = 1  # X
    board[3] = 1  # X
    board[6] = 1  # X
    
    var counts = count_sequences(agent, board)
    
    # Expect:
    # - count = 6 (3 singles + 2 doubles + 1 triple)
    # - win = True (three in a column wins)
    assert_sequences_equal(counts, 6, True, "Vertical sequence count mismatch")

fn test_diagonal_sequence() raises:
    """Test counting diagonal sequences."""
    print("Running test_diagonal_sequence...")
    var agent = create_test_agent()
    
    # Create board with diagonal line of player 1
    var board = create_board_vector(InlinedFixedVector[Int, 1024](9))
    board[0] = 1  # X
    board[4] = 1  # X
    board[8] = 1  # X
    
    var counts = count_sequences(agent, board)
    
    # Expect:
    # - count = 6 (3 singles + 2 doubles + 1 triple)
    # - win = True (three in diagonal wins)
    assert_sequences_equal(counts, 6, True, "Diagonal sequence count mismatch")

fn test_empty_board() raises:
    """Test counting sequences on an empty board."""
    print("Running test_empty_board...")
    var agent = create_test_agent()
    var board = create_board_vector(InlinedFixedVector[Int, 1024](9))
    
    var counts = count_sequences(agent, board)
    
    # Expect:
    # - count = 0 (no pieces)
    # - win = False (no winning sequence)
    assert_sequences_equal(counts, 0, False, "Empty board should have no pieces and no win")

fn test_board_with_tokens() raises:
    """Test counting sequences with scattered tokens."""
    print("Running test_board_with_tokens...")
    var agent = create_test_agent()
    
    # Create board with scattered tokens
    var board = create_board_vector(InlinedFixedVector[Int, 1024](9))
    board[0] = 1  # X
    board[4] = 0  # O
    board[8] = 1  # X
    
    var counts = count_sequences(agent, board)
    
    # Expect:
    # - count = 2 (2 singles, no sequences)
    # - win = False (no winning sequence)
    assert_sequences_equal(counts, 2, False, "Board with scattered tokens should count singles correctly")

fn test_board_with_line() raises:
    """Test counting sequences with a winning line."""
    print("Running test_board_with_line...")
    var agent = create_test_agent()
    
    # Create board with diagonal line
    var board = create_board_vector(InlinedFixedVector[Int, 1024](9))
    board[0] = 1  # X
    board[4] = 1  # X
    board[8] = 1  # X
    
    var counts = count_sequences(agent, board)
    
    # Expect:
    # - count = 6 (3 singles + 2 doubles + 1 triple)
    # - win = True (winning diagonal)
    assert_sequences_equal(counts, 6, True, "Board with diagonal line should count sequences correctly")

fn test_single_token() raises:
    """Test counting sequences with a single token."""
    print("Running test_single_token...")
    var agent = create_test_agent()
    
    # Create board with single token
    var board = create_board_vector(InlinedFixedVector[Int, 1024](9))
    board[4] = 1  # X in center
    
    var counts = count_sequences(agent, board)
    
    # Expect:
    # - count = 1 (one single)
    # - win = False (no winning sequence)
    assert_sequences_equal(counts, 1, False, "Board with single token should count singles correctly")

fn main() raises:
    test_horizontal_sequence()
    test_vertical_sequence()
    test_diagonal_sequence()
    test_empty_board()
    test_board_with_tokens()
    test_board_with_line()
    test_single_token()
    print("All tests passed!")
