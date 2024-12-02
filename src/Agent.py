import random
import numpy as np

EMPTY = -1
NOONE = -1
DEPTH = 2

def ewadd(list_a, list_b):
    if isinstance(list_b, np.ndarray) and isinstance(list_a, np.ndarray):
        # Ensure the lengths are the same
        if len(list_a) != len(list_b):
            raise ValueError("Lists must be of the same length for element-wise addition")

        return list_a + list_b
    raise ValueError("Can only add lists")

class Agent:
    def __init__(self, player_number, board_size, winning_size, scoring_array, restrict_moves, circle_of_two):
        # Initialize with numpy arrays for better performance
        board_size_flat = board_size[0] * board_size[1]
        self.starting_state = {
            "last_board_state": np.full(board_size_flat, EMPTY, dtype=np.int32),
            "last_move_played": np.array([EMPTY, EMPTY], dtype=np.int32),
            "counts": np.zeros(2 * (winning_size + 1), dtype=np.int32),
        }
        self.memory = {k: v.copy() for k, v in self.starting_state.items()}
        self.player_number = player_number
        self.board_size = board_size
        self.winning_size = winning_size
        self.scoring_array = np.array([0] + scoring_array, dtype=np.int32)
        self.restrict_moves = restrict_moves
        
        # Store directions as flattened array like in Mojo
        self.directions = np.array([
            1, 0,   # right
            0, 1,   # down
            1, 1,   # down-right
            1, -1,  # up-right
        ], dtype=np.int32)
        self.circle_of_two = circle_of_two

    def forget(self):
        self.memory = {k: v.copy() for k, v in self.starting_state.items()}

    def get_next_move(self):
        if np.all(self.memory["last_move_played"] == EMPTY):
            return [random.randint(0, self.board_size[0] - 1), random.randint(0, self.board_size[1] - 1)]
            # return [0, 0]
        state = {
            "board_state": self.memory["last_board_state"],
            "last_move": self.memory["last_move_played"],
            "counts": self.memory["counts"],
        }
        move = self.minimax(state, DEPTH, float("-inf"), float("inf"), True)
        return move[0]

    def new_move_played(self, board_state):
        for i in range(self.board_size[0] * self.board_size[1]):
            if board_state[i] != self.memory["last_board_state"][i]:
                self.memory["last_move_played"] = np.array([i % self.board_size[0], i // self.board_size[0]], dtype=np.int32)
                break
        new_counts = self.count_sequences(board_state)
        self.memory["counts"] = ewadd(self.memory["counts"], new_counts.flatten())
        self.memory["last_board_state"] = board_state.copy()

    def count_sequences(self, board_state):
        if isinstance(board_state, list):
            board_state = np.array(board_state, dtype=np.int32)
            
        # Initialize counts array [2 players][winning_size + 1]
        counts = np.zeros(2 * (self.winning_size + 1), dtype=np.int32)
        
        # First count empty spaces
        empty_count = np.sum(board_state == EMPTY)
        counts[0] = empty_count  # Player 0's empty spaces
        counts[self.winning_size + 1] = empty_count  # Player 1's empty spaces
        
        # Count all tokens as singles first
        for pos in range(len(board_state)):
            player = board_state[pos]
            if player != EMPTY:
                player_idx = (1 if player == 1 else 0)
                counts[player_idx * (self.winning_size + 1) + 1] += 1
        
        # Then find all sequences (length > 1)
        for y in range(self.board_size[1]):
            for x in range(self.board_size[0]):
                pos = y * self.board_size[0] + x
                player = board_state[pos]
                
                if player == EMPTY:
                    continue
                    
                player_idx = (1 if player == 1 else 0)
                
                # For each direction
                for i in range(0, len(self.directions), 2):
                    dx, dy = self.directions[i:i+2]
                    
                    # Only start sequence from leftmost/topmost position
                    prev_x = x - dx
                    prev_y = y - dy
                    if (0 <= prev_x < self.board_size[0] and 
                        0 <= prev_y < self.board_size[1] and 
                        board_state[prev_y * self.board_size[0] + prev_x] == player):
                        continue
                    
                    # Count sequence length
                    length = 1
                    curr_x = x + dx
                    curr_y = y + dy
                    while (0 <= curr_x < self.board_size[0] and 
                           0 <= curr_y < self.board_size[1]):
                        curr_pos = curr_y * self.board_size[0] + curr_x
                        if board_state[curr_pos] != player:
                            break
                        length += 1
                        curr_x += dx
                        curr_y += dy
                    
                    # Record sequence if longer than 1
                    if length > 1:
                        # For a sequence of length N, count:
                        # - One sequence of length N
                        # - N-1 sequences of length 2
                        # - N-2 sequences of length 3
                        # etc.
                        for seq_len in range(2, length + 1):
                            if seq_len <= self.winning_size:
                                counts[player_idx * (self.winning_size + 1) + seq_len] += length - seq_len + 1
        
        # Reshape to match expected format
        return counts.reshape(2, -1)

    def is_move_too_far_from_action(self, board, move, circle_of_two):
        parsed_move = move % self.board_size[0], move // self.board_size[0]
        for dx, dy in circle_of_two:
            x, y = parsed_move[0] + dx, parsed_move[1] + dy
            if 0 <= x < self.board_size[0] and 0 <= y < self.board_size[1] and board[x + y * self.board_size[0]] != 0:
                return False
        return True

    def generate_next_moves(self, state, player):
        next_moves = []
        next_states = []

        for i in range(len(state["board_state"])):
            if state["board_state"][i] == EMPTY and not self.is_move_too_far_from_action(state["board_state"], i, self.circle_of_two):
                next_moves.append(i)
        for idx, next_move in enumerate(next_moves):
            next_states.append({"board_state": state["board_state"].copy(), "last_move": np.array([next_move % self.board_size[0], next_move // self.board_size[0]], dtype=np.int32), "counts": None, "evaluation": None})
            next_states[idx]["board_state"][next_move] = player
            next_states[idx]["counts"] = self.count_sequences(next_states[idx]["board_state"])
            next_states[idx]["evaluation"] = self.evaluate(next_states[idx])
        # Make job of alpha-beta easier by ordering from best/worst move and restricing number of checked moves
        sorted_states = sorted(next_states, key=lambda k: k["evaluation"], reverse=(player == self.player_number))
        return sorted_states[: self.restrict_moves]

    def evaluate(self, state):
        for player in range(2):
            if state["counts"][player][self.winning_size] != 0:
                return float("inf") if (self.player_number == player) else float("-inf")
        return np.sum(
            (state["counts"][0][1:self.winning_size] - state["counts"][1][1:self.winning_size]) * self.scoring_array[1:self.winning_size] if self.player_number == 1 else (state["counts"][1][1:self.winning_size] - state["counts"][0][1:self.winning_size]) * self.scoring_array[1:self.winning_size]
        )

    def is_game_over(self, state):
        if state["counts"][0][self.winning_size] != 0 or state["counts"][1][self.winning_size] != 0:
            return True
        return np.all(state["board_state"] != EMPTY)

    def print_board(self, board):
        print("---------")
        for i in range(self.board_size[1]):
            print_row = []
            for j in range(self.board_size[0]):
                if board[i * self.board_size[0] + j] == 0:
                    print_row.append("X")
                if board[i * self.board_size[0] + j] == 1:
                    print_row.append("O")
                if board[i * self.board_size[0] + j] == EMPTY:
                    print_row.append("-")
            print(print_row)
        print("---------")

    def minimax(self, state, depth, alpha, beta, maximizing):
        if depth == 0 or self.is_game_over(state):
            return (state["last_move"], self.evaluate(state))
        best_move = None
        if maximizing:
            value = float("-inf")
            next_moves = self.generate_next_moves(state, self.player_number)
            for move in next_moves:
                node = self.minimax(move, depth - 1, alpha, beta, False)
                # print(node[1], value)
                if node[1] >= value:
                    value = node[1]
                    best_move = node[0]
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        else:
            value = float("inf")
            next_moves = self.generate_next_moves(state, 1 - self.player_number)
            for move in next_moves:
                node = self.minimax(move, depth - 1, alpha, beta, True)
                if node[1] <= value:
                    value = node[1]
                    best_move = node[0]
                beta = min(beta, value)
                if beta <= alpha:
                    break
        return best_move, value
