from python import Python
from collections.vector import InlinedFixedVector
from Game import GameState, print_board
from Agent import AgentState
from time import now
from sys import argv

alias EMPTY = 0

fn main() raises:
    # Get parameters from command line arguments
    var board_size_x = 3  # Default width
    var board_size_y = 3  # Default height
    var depth = 1        # Default depth
    
    if len(argv()) > 1:
        board_size_x = atol(argv()[1])
    if len(argv()) > 2:
        board_size_y = atol(argv()[2])
    if len(argv()) > 3:
        depth = atol(argv()[3])
    
    var winning_size = min(board_size_x, board_size_y)  # Set winning size to minimum dimension
    
    print("Game initialized with:")
    print("Board size:", board_size_x, "x", board_size_y)
    print("Winning size:", winning_size)
    print("Search depth:", depth)
    
    var game = GameState(board_size_x, board_size_y)
    
    # Initialize agents with depth parameter
    var agent1_state = AgentState(1, board_size_x, board_size_y, winning_size, depth=depth)
    var agent2_state = AgentState(2, board_size_x, board_size_y, winning_size, depth=depth)
    
    # Play the game
    var current_player = 1
    var game_start_time = now()
    var move_count = 0
    var total_move_time = 0.0
    
    while not game.is_game_over():
        print_board(game.board, game.board_size_x, game.board_size_y)
        print("Player", current_player, "'s turn")
        
        var move_start_time = now()
        var move: Tuple[Int, Int]
        if current_player == 1:
            move = agent1_state.get_next_move(game.board)
        else:
            move = agent2_state.get_next_move(game.board)
        
        var move_end_time = now()
        var move_duration = Float64(move_end_time - move_start_time) / 1_000_000.0  # Convert to milliseconds
        total_move_time += move_duration
        move_count += 1
        print("Move took:", move_duration, "ms")
        
        if not game.make_move(move[0], move[1], current_player):
            print("Invalid move!")
            continue
        
        # Switch players
        current_player = 3 - current_player  # Switch between 1 and 2
    
    var game_end_time = now()
    var total_game_time = Float64(game_end_time - game_start_time) / 1_000_000.0  # Convert to milliseconds
    
    print_board(game.board, game.board_size_x, game.board_size_y)
    if game.winner != EMPTY:
        print("Player", game.winner, "wins!")
    else:
        print("Game is a draw!")
        
    print("\nGame Statistics:")
    print("Total game time:", total_game_time, "ms")
    print("Total moves:", move_count)
    print("Average time per move:", total_move_time / Float64(move_count), "ms")
