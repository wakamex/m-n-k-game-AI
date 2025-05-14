from Agent import AgentState, count_sequences
from collections.vector import InlinedFixedVector

fn create_board(pattern: Int, size: Int) -> InlinedFixedVector[Int, 1024]:
    var board = InlinedFixedVector[Int, 1024](size * size)
    # Initialize with -1
    for i in range(size * size):
        board[i] = -1
        
    if pattern == 0:  # Diagonal pattern
        for i in range(size):
            board[i * size + i] = 1
            if i > 0:
                board[i * size + (i-1)] = 0
    elif pattern == 1:  # Vertical lines
        for i in range(size):
            for j in range(size):
                if j % 3 == 0:
                    board[i * size + j] = 1
                elif j % 3 == 1:
                    board[i * size + j] = 0
    elif pattern == 2:  # Horizontal lines
        for i in range(size):
            for j in range(size):
                if i % 3 == 0:
                    board[i * size + j] = 1
                elif i % 3 == 1:
                    board[i * size + j] = 0
    elif pattern == 3:  # Scattered pieces
        for i in range(size * size):
            if i % 7 == 0:
                board[i] = 1
            elif i % 5 == 0:
                board[i] = 0
    return board

fn create_agent(size: Int) -> AgentState:
    var scoring_array = InlinedFixedVector[Int, 1024](1024)
    for i in range(4):
        scoring_array[i] = i
    
    return AgentState(
        player_number=1,
        board_size_x=size,
        board_size_y=size,
        winning_size=3,
        scoring_array=scoring_array,
        restrict_moves=False
    )

fn main():
    # Create boards of different sizes with different patterns
    var sizes = InlinedFixedVector[Int, 10](6)
    sizes[0] = 3
    sizes[1] = 4
    sizes[2] = 5
    sizes[3] = 6
    sizes[4] = 8
    sizes[5] = 10
    
    # Process all boards
    for s in range(len(sizes)):
        var size = sizes[s]
        var agent = create_agent(size)
        for pattern in range(4):
            var board = create_board(pattern, size)
            var `_` = count_sequences(agent, board)

fn test():
    main()
