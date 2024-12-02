from Agent import AgentState, count_sequences
from collections.vector import InlinedFixedVector

fn main():
    # Create a complex board state to benchmark
    var board = InlinedFixedVector[Int, 1024](36)  # 6x6 board
    
    # Match Python's board state:
    #  1, -1,  0,  1,  0, -1,  # First row
    #  1, -1,  0,  1,  0, -1,  # Second row
    #  1, -1,  0,  1,  0, -1,  # Third row
    #  1, -1,  0,  1,  0, -1,  # Fourth row
    #  1, -1,  0,  1,  0, -1,  # Fifth row
    #  1, -1,  0,  1,  0, -1,  # Sixth row
    for y in range(6):
        for x in range(6):
            var i = y * 6 + x
            if x % 3 == 0:
                board[i] = 1
            elif x % 3 == 1:
                board[i] = -1
            else:
                board[i] = 0
    
    var scoring_array = InlinedFixedVector[Int, 1024](1024)
    for i in range(4):
        scoring_array[i] = i
    
    var agent = AgentState(
        player_number=1,
        board_size_x=6,
        board_size_y=6,
        winning_size=3,
        scoring_array=scoring_array,
        restrict_moves=False
    )
    
    var `_` = count_sequences(agent, board)

fn test():
    main()
