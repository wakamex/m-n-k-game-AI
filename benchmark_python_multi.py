from src.Agent import Agent
import numpy as np

def create_board(pattern: int, size: int) -> np.ndarray:
    board = np.full(size * size, -1, dtype=np.int32)
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

def main():
    # Create boards of different sizes with different patterns
    boards = []
    sizes = [3, 4, 5, 6, 8, 10]
    for size in sizes:
        for pattern in range(4):  # 4 different patterns
            boards.append((size, create_board(pattern, size)))
    
    # Create agents for each board size
    agents = {}
    for size in sizes:
        agents[size] = Agent(
            player_number=1,
            board_size=[size, size],
            winning_size=3,
            scoring_array=[0, 1, 2, 3],
            circle_of_two=[(1, 0), (0, 1)]
        )
    
    # Process all boards
    for size, board in boards:
        agents[size].count_sequences(board)

if __name__ == "__main__":
    main()
