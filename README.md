# (m,n,k)-game AI with Configurable Strategy

**(Disclaimer: This README currently describes the Python implementation. The Mojo version is not actively being updated and may differ significantly in its current state.)**

## (m,n,k)-game
An m,n,k-game is an abstract board game in which two players take turns in placing a stone of their color on an m×n board, the winner being the player who first gets k stones of their own color in a row, horizontally, vertically, or diagonally.

Thus, tic-tac-toe is the 3,3,3-game and free-style gomoku is the 15,15,5-game.
An m,n,k-game is also called a k-in-a-row game on an m×n board.

**In this program, we consider any sequence of k or more stones of the same color in a row (horizontally, vertically, or diagonally) as a winning line.**

## Player Representation
*   Player 0: Represented by `0` (typically 'X' in printed output)
*   Player 1: Represented by `1` (typically 'O' in printed output)
*   Empty Cell: Represented by `-1`

## How to Use (Python Version)
Run a tournament between configured agents:

`python src/play.py`

## Agent Configuration (Python `src/play.py`)
Agent behaviors are primarily defined within `src/play.py` by initializing `Agent` objects. Key parameters during initialization:
*   `player_number`: 0 or 1.
*   `board_size`: Tuple `(width, height)`.
*   `winning_size`: Integer `k`.
*   `scoring_array`: **(Currently NOT USED by the Python agent's heuristic for move evaluation - see Heuristic Scoring below)**. Intended for future heuristic development.
*   `circle_of_two`: A list of (dx, dy) tuples defining a neighborhood around existing pieces. Moves are typically restricted to empty cells within this neighborhood of any existing piece to prune the search space.
*   `name`: String name for the agent.

The agent uses a Minimax algorithm with alpha-beta pruning to determine its next move. The search depth is currently a global constant `DEPTH` (defaulting to 3) within `src/Agent.py`.

## Heuristic Scoring (Python Agent - Current Implementation)

The current Python agent (`src/Agent.py`) uses a specific heuristic for evaluating non-terminal game states. This heuristic **does not currently use the `scoring_array`** passed during agent initialization.

1.  **`count_sequences(board_state)` Method:**
    *   This method calculates, for each player, a `counts` array.
    *   `counts[player_idx][L]` (where `L > 0`) stores the number of distinct `winning_size`-length line segments (horizontal, vertical, or diagonal) on the board that contain exactly `L` pieces of that `player_idx` and `winning_size - L` empty cells. No opponent pieces are allowed in such a segment for it to be counted for a player.
    *   `counts[player_idx][0]` stores the total number of empty cells on the board.
    *   For example, if `winning_size = 3`, `counts[player_idx][2]` is the number of 3-cell lines that have two of that player's pieces and one empty cell (e.g., XX. or X.X or .XX).

2.  **`evaluate(state, winner)` Method:**
    *   If the game state is terminal (`winner` is 0, 1, or -2 for a draw):
        *   Returns `1.0` if Player 0 (the maximizing player) wins.
        *   Returns `-1.0` if Player 1 (the minimizing player) wins.
        *   Returns `0.0` for a draw.
    *   If the game is ongoing:
        *   It retrieves the `counts` array from `count_sequences`.
        *   The heuristic score is calculated as: `(counts[0][2] - counts[1][2]) * 0.1`.
        *   This means the evaluation prioritizes having more "two-pieces-in-a-potential-winning-line-of-3" (or k) than the opponent.
        *   The score is then clamped between -0.9 and 0.9.

**Example:**
If `winning_size = 3`, and Player 0 has five 3-cell lines containing two 'X's and one empty cell (`counts[0][2] = 5`), and Player 1 has three 3-cell lines containing two 'O's and one empty cell (`counts[1][2] = 3`), the heuristic score (from Player 0's perspective) would be `(5 - 3) * 0.1 = 0.2`.

## Some Results (Illustrative based on `src/play.py` setup)
The `src/play.py` script runs a tournament between agents defined with different names but currently using the same underlying heuristic logic as described above (since `scoring_array` is not used by the heuristic). Differences in play would primarily arise from turn order or subtle tie-breaking in Minimax if multiple moves yield the same heuristic value.

*(The table from the original README showing different agent behaviors based on `scoring_array` is not applicable to the current Python implementation's heuristic.)*

## Next Steps for Development

*   **Refine Agent Depth Control:**
    *   Modify `Agent.__init__` in Python to accept a `depth` parameter, store it as `self.depth`, and use it in the Minimax search. This will allow for more flexible agent configuration and testing.
*   **Implement and Test the Configurable Heuristic (as originally envisioned):**
    *   Redesign `Agent.count_sequences` in Python to identify *open* sequences (extendable on at least one end) of varying lengths (1 to `winning_size-1`).
    *   Redesign `Agent.evaluate` in Python to use the `scoring_array` to score these open sequences for each player and calculate a net score.
    *   Add comprehensive tests for this new heuristic logic.
*   **Mojo Implementation Alignment & Testing:**
    *   Once the Python version's heuristic is finalized, align the `Agent.mojo` implementation (player representation, heuristic logic, use of `scoring_array`).
    *   Update Mojo tests to match the refined logic.
*   **Game Logic Tests:**
    *   Add dedicated unit tests for `Game.py` methods like `is_game_over`, `play_move`, and `reset_game`.
*   **Advanced Minimax/Pruning Verification (Optional):**
    *   Consider methods to more explicitly test the correctness and efficiency of alpha-beta pruning.