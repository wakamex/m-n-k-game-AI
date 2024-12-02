import random
import numpy as np
import time

EMPTY = -1
NOONE = -1
DEPTH = 3
MAX_TIME = 0.5  # Keep timeout at 0.5 seconds

def ewadd(list_a, list_b):
    if isinstance(list_b, np.ndarray) and isinstance(list_a, np.ndarray):
        # Ensure the lengths are the same
        if len(list_a) != len(list_b):
            raise ValueError("Lists must be of the same length for element-wise addition")

        return list_a + list_b
    raise ValueError("Can only add lists")

class Agent:
    def __init__(self, player_number, board_size, winning_size, scoring_array, circle_of_two, name="Agent"):
        """Initialize the agent with game parameters"""
        self.player_number = player_number
        self.board_size = tuple(board_size) if isinstance(board_size, list) else board_size if isinstance(board_size, tuple) else (board_size, board_size)
        self.winning_size = winning_size
        self.scoring_array = scoring_array
        self.name = name
        self.circle_of_two = circle_of_two
        
        # Initialize memory
        self.memory = {
            "board_state": [EMPTY] * (self.board_size[0] * self.board_size[1]),
            "last_move": None,
            "counts": None,
            "last_move_played": None
        }
        self.game = None  # Will be set when added to a game
        
        # Store directions as flattened array like in Mojo
        self.directions = np.array([
            1, 0,   # right
            0, 1,   # down
            1, 1,   # down-right
            1, -1,  # up-right
        ], dtype=np.int32)
        
        # Debug counters
        self.states_evaluated = 0
        self.max_depth_reached = 0
        self.start_time = None

    def set_game(self, game):
        """Set the game instance for this agent"""
        self.game = game

    def forget(self):
        """Reset agent state for a new game"""
        self.memory = {
            "board_state": [EMPTY] * (self.board_size[0] * self.board_size[1]),
            "last_move": None,
            "counts": None,
            "last_move_played": None
        }

    def get_next_move(self):
        """Get the next move for this agent"""
        # Reset debug counters
        self.states_evaluated = 0
        self.max_depth_reached = 0
        self.start_time = time.time()
        
        print(f"\n{self.name} thinking...")
        
        start_time = time.time()
        best_move = None
        best_value = float("-inf") if self.player_number == 0 else float("inf")
        
        state = {
            "board_state": self.game.board.copy(),
            "last_move": None
        }
        
        next_moves = self.generate_next_moves(state, self.player_number)
        
        for move in next_moves:
            # Check if we've exceeded time limit
            if time.time() - start_time > MAX_TIME:
                if best_move is None and next_moves:
                    return next_moves[0]["last_move"]  # Return first valid move if out of time
                break
                
            # Start minimax with the OPPOSITE of our player number (since we're evaluating opponent's response)
            value = self.minimax(move, DEPTH, float("-inf"), float("inf"), self.player_number == 1)
            
            if self.player_number == 0:  # Maximizing player
                if value > best_value:
                    best_value = value
                    best_move = move
            else:  # Minimizing player
                if value < best_value:
                    best_value = value
                    best_move = move
                    
        if best_move is None:
            # If no moves found or out of time, take first available move
            empty_spaces = [i for i, x in enumerate(self.game.board) if x == EMPTY]
            if empty_spaces:
                return empty_spaces[0]
            raise ValueError("No valid moves found")
            
        return best_move["last_move"]

    def new_move_played(self, board_state):
        """Update our memory with the new board state"""
        # Find the last move by comparing with previous state
        last_move = None
        for i in range(len(board_state)):
            if self.memory["board_state"][i] != board_state[i]:
                last_move = i
                break
        
        # Update memory
        self.memory["board_state"] = board_state.copy()
        self.memory["last_move"] = last_move
        self.memory["counts"] = None  # Reset counts when board changes
        
        # Update last_move_played coordinates
        if last_move is not None:
            self.memory["last_move_played"] = np.array([last_move % self.board_size[0], last_move // self.board_size[0]], dtype=np.int32)

    def count_sequences(self, board_state):
        """Count sequences of pieces for each player"""
        counts = np.zeros((2, self.winning_size + 1), dtype=np.int32)
        
        # Count empty spaces first
        empty_count = np.sum(board_state == EMPTY)
        counts[0][0] = empty_count
        counts[1][0] = empty_count
        
        # Check horizontal sequences
        for row in range(self.board_size[1]):
            for col in range(self.board_size[0] - self.winning_size + 1):
                idx = row * self.board_size[0] + col
                for player in range(2):
                    length = 0
                    valid = True
                    for i in range(self.winning_size):
                        if board_state[idx + i] == player:
                            length += 1
                        elif board_state[idx + i] != EMPTY:
                            valid = False
                            break
                    if valid and length > 0:
                        counts[player][length] += 1
                        
        # Check vertical sequences
        for col in range(self.board_size[0]):
            for row in range(self.board_size[1] - self.winning_size + 1):
                idx = row * self.board_size[0] + col
                for player in range(2):
                    length = 0
                    valid = True
                    for i in range(self.winning_size):
                        if board_state[idx + i * self.board_size[0]] == player:
                            length += 1
                        elif board_state[idx + i * self.board_size[0]] != EMPTY:
                            valid = False
                            break
                    if valid and length > 0:
                        counts[player][length] += 1
                        
        # Check diagonal sequences (down-right)
        for row in range(self.board_size[1] - self.winning_size + 1):
            for col in range(self.board_size[0] - self.winning_size + 1):
                idx = row * self.board_size[0] + col
                for player in range(2):
                    length = 0
                    valid = True
                    for i in range(self.winning_size):
                        if board_state[idx + i * (self.board_size[0] + 1)] == player:
                            length += 1
                        elif board_state[idx + i * (self.board_size[0] + 1)] != EMPTY:
                            valid = False
                            break
                    if valid and length > 0:
                        counts[player][length] += 1
                        
        # Check diagonal sequences (up-right)
        for row in range(self.winning_size - 1, self.board_size[1]):
            for col in range(self.board_size[0] - self.winning_size + 1):
                idx = row * self.board_size[0] + col
                for player in range(2):
                    length = 0
                    valid = True
                    for i in range(self.winning_size):
                        if board_state[idx - i * (self.board_size[0] - 1)] == player:
                            length += 1
                        elif board_state[idx - i * (self.board_size[0] - 1)] != EMPTY:
                            valid = False
                            break
                    if valid and length > 0:
                        counts[player][length] += 1
                        
        return counts

    def is_move_too_far_from_action(self, board, move, circle_of_two):
        x, y = move  # Unpack the move coordinates directly
        for dx, dy in circle_of_two:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.board_size[0] and 0 <= new_y < self.board_size[1]:
                if board[new_y * self.board_size[0] + new_x] != EMPTY:
                    return False
        return True

    def generate_next_moves(self, state, current_player):
        """Generate all possible next moves from current state"""
        next_moves = []
        board = state["board_state"]
        
        # Count existing moves to validate
        p0_count = sum(1 for x in board if x == 0)
        p1_count = sum(1 for x in board if x == 1)
        
        # Validate it's the correct player's turn
        if current_player == 0 and p0_count > p1_count:
            return []  # Invalid - player 0 has more moves
        if current_player == 1 and p1_count > p0_count:
            return []  # Invalid - player 1 has more moves

        # Generate moves for empty spaces
        for i in range(len(board)):
            if board[i] == EMPTY:
                new_state = {
                    "board_state": board.copy(),
                    "last_move": i
                }
                new_state["board_state"][i] = current_player
                
                # Only add move if it's not too far from action
                if len([x for x in board if x != EMPTY]) == 0 or not self.is_move_too_far_from_action(board, (i % self.board_size[0], i // self.board_size[0]), self.circle_of_two):
                    next_moves.append(new_state)

        return next_moves

    def is_game_over(self, state):
        """Check if the current state is a terminal state"""
        board = state["board_state"]
        
        # Quick check - if not enough moves played, game can't be over
        moves_played = sum(1 for cell in board if cell != EMPTY)
        if moves_played < self.winning_size * 2 - 1:
            return False, -1
            
        # Debug - track long-running checks
        check_start = time.time()
        
        for i in range(len(board)):
            if time.time() - check_start > 0.1:  # Alert if taking too long
                print(f"Warning: Long game state check at position {i}/{len(board)}")
                
            if board[i] == EMPTY:
                continue
                
            player = board[i]
            
            # Check horizontal
            if i % self.board_size[0] < self.board_size[0] - self.winning_size + 1:
                if all(board[i+j] == player for j in range(self.winning_size)):
                    return True, player
                    
            # Check vertical
            if i < self.board_size[0] * (self.board_size[1] - self.winning_size + 1):
                if all(board[i+j*self.board_size[0]] == player for j in range(self.winning_size)):
                    return True, player
                    
            # Check diagonal
            if i < self.board_size[0] * (self.board_size[1] - self.winning_size + 1) and i % self.board_size[0] < self.board_size[0] - self.winning_size + 1:
                if all(board[i+j*(self.board_size[0]+1)] == player for j in range(self.winning_size)):
                    return True, player
                    
            if i < self.board_size[0] * (self.board_size[1] - self.winning_size + 1) and i % self.board_size[0] >= self.winning_size - 1:
                if all(board[i+j*(self.board_size[0]-1)] == player for j in range(self.winning_size)):
                    return True, player
                    
        # Check for tie
        if all(x != EMPTY for x in state["board_state"]):
            return True, -2
            
        return False, -1

    def evaluate(self, state, winner):
        """Evaluate the state from perspective of maximizing player (player 0)"""
        # If game is over, return appropriate score
        if winner == 0:  # Max player won
            return 1.0
        elif winner == 1:  # Min player won
            return -1.0
        elif winner == -2:  # Draw
            return 0.0
            
        # Game is ongoing - use simple heuristic based on 2-sequences
        counts = self.count_sequences(state["board_state"])
        
        # Simple heuristic: difference in number of 2-sequences
        score = (counts[0][2] - counts[1][2]) * 0.1
        return max(min(score, 0.9), -0.9)  # Bound between winning scores

    def minimax(self, state, depth, alpha, beta, maximizing_player):
        """Minimax implementation with alpha-beta pruning"""
        self.states_evaluated += 1
        self.max_depth_reached = max(self.max_depth_reached, depth)
        
        # Create a new state copy to avoid state pollution
        state = {
            "board_state": state["board_state"].copy(),
            "last_move": state["last_move"]
        }
        
        # Check if we're at a terminal state first
        game_over, winner = self.is_game_over(state)
        if game_over:
            return self.evaluate(state, winner)
            
        # Then check depth limit
        if depth <= 0:
            return self.evaluate(state, -1)  # -1 means game not over
            
        current_player = 0 if maximizing_player else 1
        next_moves = self.generate_next_moves(state, current_player)
        
        if not next_moves:  # No valid moves available
            return self.evaluate(state, -2)  # -2 means draw
            
        if maximizing_player:
            max_eval = float("-inf")
            for move in next_moves:
                eval = self.minimax(move, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf") 
            for move in next_moves:
                eval = self.minimax(move, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
