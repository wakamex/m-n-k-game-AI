from src.Agent import Agent
import numpy as np

def main():
    # Create a complex board state to benchmark
    board_state = np.array([
        1, -1, 0, 1, 0, -1,  # First row
        1, -1, 0, 1, 0, -1,  # Second row
        1, -1, 0, 1, 0, -1,  # Third row
        1, -1, 0, 1, 0, -1,  # Fourth row
        1, -1, 0, 1, 0, -1,  # Fifth row
        1, -1, 0, 1, 0, -1,  # Sixth row
    ], dtype=np.int32)
    
    agent = Agent(
        player_number=1,
        board_size=[6, 6],
        winning_size=3,
        scoring_array=[0, 1, 2, 3],
        circle_of_two=[(1, 0), (0, 1)]
    )
    
    # Run sequence counting once
    agent.count_sequences(board_state)

if __name__ == "__main__":
    main()
