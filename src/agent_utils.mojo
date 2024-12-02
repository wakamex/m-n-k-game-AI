from collections.vector import InlinedFixedVector

alias EMPTY = 0

fn print_board(board: InlinedFixedVector[Int, 1024], board_size_x: Int, board_size_y: Int):
    """Print the current state of the board."""
    for y in range(board_size_y):
        for x in range(board_size_x):
            var pos = y * board_size_x + x
            var value = board[pos]
            if value == EMPTY:
                print(" .", end="")
            elif value == 1:
                print(" X", end="")
            elif value == 2:
                print(" O", end="")
            else:
                print(" ?", end="")  # For any unexpected values
        print("")  # New line after each row
    print("")  # Extra line after board
