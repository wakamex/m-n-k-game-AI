import random


class Agent:
    def __init__(self, player_number, board_size, winning_size, scoring_array, restrict_moves):
        # Agent remembers best found move for every beggining postion he ever evaluated
        self.memory = {
            "last_board_state": [0] * board_size[0] * board_size[1],
            "last_move_played": [-1, -1],  # x, y
            # To be counted as sequence it must be open atleast on one side e.g. -1,1,1,1,0 is three
            "last_board_state_sequence": {"player_one": [0] * (winning_size + 1), "player_two": [0] * (winning_size + 1)},  # e.g. count of fours is on index 4
        }
        self.player_number = player_number
        self.board_size = board_size
        self.winning_size = winning_size
        self.scoring_array = [0] + scoring_array
        self.restrict_moves = restrict_moves

    def forget(self):
        self.memory = {
            "last_board_state": [0] * self.board_size[0] * self.board_size[1],
            "last_move_played": [-1, -1],
            "last_board_state_sequence": {"player_one": [0] * (self.winning_size + 1), "player_two": [0] * (self.winning_size + 1)},
        }

    def get_next_move(self):
        if self.memory["last_move_played"] == [-1, -1]:
            return [random.randint(0, self.board_size[0] - 1), random.randint(0, self.board_size[1] - 1)]
        state = {
            "board_state": self.memory["last_board_state"],
            "lastMove": self.memory["last_move_played"],
            "sequences": (self.memory["last_board_state_sequence"]["player_one"], self.memory["last_board_state_sequence"]["player_two"]),
        }
        move = self.minimax(state, 5, float("-inf"), float("inf"), True)
        return move[0]

    def new_move_played(self, board_state):
        for i in range(self.board_size[0] * self.board_size[1]):
            if board_state[i] != self.memory["last_board_state"][i]:
                self.memory["last_move_played"] = [i % self.board_size[0], i // self.board_size[1]]
                break
        new_sequences = self.count_sequences(
            self.memory["last_board_state_sequence"]["player_one"],
            self.memory["last_board_state_sequence"]["player_two"],
            self.memory["last_board_state"],
            board_state,
            self.memory["last_move_played"],
        )
        self.memory["last_board_state_sequence"]["player_one"] = new_sequences[0]
        self.memory["last_board_state_sequence"]["player_two"] = new_sequences[1]
        self.memory["last_board_state"] = board_state.copy()

    def count_sequences(self, player_one_sequences, player_two_sequences, board_state_old, board_state_new, move):
        # Sequence counting is done by first counting incident sequences on old board, subtracting
        # them from total and then adding new sequences from new board.
        player_one = player_one_sequences.copy()
        player_two = player_two_sequences.copy()
        # Rows
        old_rows = self.count_rows(board_state_old, move)
        new_rows = self.count_rows(board_state_new, move)
        # Columns
        old_columns = self.count_columns(board_state_old, move)
        new_columns = self.count_columns(board_state_new, move)
        # Down diagonal
        old_down_diagonal = self.count_down_diagonal(board_state_old, move)
        new_down_diagonal = self.count_down_diagonal(board_state_new, move)
        # Up diagonal
        old_up_diagonal = self.count_up_diagonal(board_state_old, move)
        new_up_diagonal = self.count_up_diagonal(board_state_new, move)
        for i in range(1, self.winning_size + 1):
            player_one[i] = (
                player_one[i]
                - old_rows[0][i]
                + new_rows[0][i]
                - old_columns[0][i]
                + new_columns[0][i]
                - old_up_diagonal[0][i]
                + new_up_diagonal[0][i]
                - old_down_diagonal[0][i]
                + new_down_diagonal[0][i]
            )
            player_two[i] = (
                player_two[i]
                - old_rows[1][i]
                + new_rows[1][i]
                - old_columns[1][i]
                + new_columns[1][i]
                - old_up_diagonal[1][i]
                + new_up_diagonal[1][i]
                - old_down_diagonal[1][i]
                + new_down_diagonal[1][i]
            )
        return player_one, player_two

    def count_rows(self, board_state, move):
        player_one = [0] * (self.winning_size + 1)
        player_two = [0] * (self.winning_size + 1)
        # Cycle iterates over all possible starting points
        counting = 0
        current_sequence_is_valid = False
        length = 0
        for i in range(move[1] * self.board_size[0], move[1] * self.board_size[0] + self.board_size[0]):
            if board_state[i] != counting:
                length = min(length, self.winning_size)
                if counting == 0 or board_state[i] == 0:
                    # Sequence must start or end with empty space to be valid
                    current_sequence_is_valid = True
                if counting == 1 and current_sequence_is_valid:
                    player_one[length] += 1
                    current_sequence_is_valid = False
                if counting == -1 and current_sequence_is_valid:
                    player_two[length] += 1
                    current_sequence_is_valid = False
                length = 1
            else:
                length += 1
            counting = board_state[i]
        # Sequence could end on board end
        if counting != 0 and current_sequence_is_valid:
            length = min(length, self.winning_size)
            if counting == 1:
                player_one[length] += 1
            else:
                player_two[length] += 1
        return (player_one, player_two)

    def count_columns(self, board_state, move):
        player_one = [0] * (self.winning_size + 1)
        player_two = [0] * (self.winning_size + 1)
        # Cycle iterates over all possible starting points
        counting = 0
        current_sequence_is_valid = False
        length = 0
        for i in range(move[0], self.board_size[0] * self.board_size[1], self.board_size[1]):
            if board_state[i] != counting:
                length = min(length, self.winning_size)
                if counting == 0 or board_state[i] == 0:
                    # Sequence must start or end with empty space to be valid
                    current_sequence_is_valid = True
                if counting == 1 and current_sequence_is_valid:
                    player_one[length] += 1
                    current_sequence_is_valid = False
                if counting == -1 and current_sequence_is_valid:
                    player_two[length] += 1
                    current_sequence_is_valid = False
                length = 1
            else:
                length += 1
            counting = board_state[i]
        # Sequence could end on board end
        if counting != 0 and current_sequence_is_valid:
            length = min(length, self.winning_size)
            if counting == 1:
                player_one[length] += 1
            else:
                player_two[length] += 1
        return (player_one, player_two)

    def count_down_diagonal(self, board_state, move):
        player_one = [0] * (self.winning_size + 1)
        player_two = [0] * (self.winning_size + 1)
        # Cycle iterates over all possible starting points
        counting = 0
        current_sequence_is_valid = False
        length = 0
        # Math magic works as follows:
        # First element on diagonal can be calculated from move by modulo length of step
        # Every step is length of row + 1
        for i in range((move[0] + (move[1] * self.board_size[0])) % (self.board_size[0] + 1), self.board_size[0] * self.board_size[1], self.board_size[0] + 1):
            if board_state[i] != counting:
                length = min(length, self.winning_size)
                if counting == 0 or board_state[i] == 0:
                    # Sequence must start or end with empty space to be valid
                    current_sequence_is_valid = True
                if counting == 1 and current_sequence_is_valid:
                    player_one[length] += 1
                    current_sequence_is_valid = False
                if counting == -1 and current_sequence_is_valid:
                    player_two[length] += 1
                    current_sequence_is_valid = False
                length = 1
            else:
                length += 1
            counting = board_state[i]
            # Handle diagonal overflowing board by checking if we didn't skip a row by increasing index
            if i // self.board_size[1] + 1 != ((i + self.board_size[0] + 1) // self.board_size[1]):
                break
        # Sequence could end on board end
        if counting != 0 and current_sequence_is_valid:
            length = min(length, self.winning_size)
            if counting == 1:
                player_one[length] += 1
            else:
                player_two[length] += 1
        return (player_one, player_two)

    def count_up_diagonal(self, board_state, move):
        player_one = [0] * (self.winning_size + 1)
        player_two = [0] * (self.winning_size + 1)
        # Cycle iterates over all possible starting points
        counting = 0
        current_sequence_is_valid = False
        length = 0
        # Math magic works as follows:
        # First element on diagonal can be calculated from move by modulo length of step
        # Every step is length of row - 1
        for i in range((move[0] + (move[1] * self.board_size[0])) % (self.board_size[0] - 1), self.board_size[0] * self.board_size[1], self.board_size[0] - 1):
            if board_state[i] != counting:
                length = min(length, self.winning_size)
                if counting == 0 or board_state[i] == 0:
                    # Sequence must start or end with empty space to be valid
                    current_sequence_is_valid = True
                if counting == 1 and current_sequence_is_valid:
                    player_one[length] += 1
                    current_sequence_is_valid = False
                if counting == -1 and current_sequence_is_valid:
                    player_two[length] += 1
                    current_sequence_is_valid = False
                length = 1
            else:
                length += 1
            counting = board_state[i]
            # Handle diagonal overflowing board by checking if we didn't end on a same row by increasing index
            if i // self.board_size[1] == ((i + self.board_size[0] - 1) // self.board_size[1]):
                break
        # Sequence could end on board end
        if counting != 0 and current_sequence_is_valid:
            length = min(length, self.winning_size)
            if counting == 1:
                player_one[length] += 1
            else:
                player_two[length] += 1
        return (player_one, player_two)

    def is_move_too_far_from_action(self, board, move):
        # Move is considered too far if there is no other move in 2 wide circle
        parsed_move = move % self.board_size[0], move // self.board_size[1]
        # Search one sized cricle
        circle = [
            [2, 2],
            [1, 2],
            [0, 2],
            [-1, 2],
            [-2, 2],
            [2, 1],
            [1, 1],
            [0, 1],
            [-1, 1],
            [-2, 1],
            [2, 0],
            [1, 0],
            [-1, 0],
            [-2, 0],
            [2, -1],
            [1, -1],
            [0, -1],
            [-1, -1],
            [-2, -1],
            [2, -2],
            [1, -2],
            [0, -2],
            [-1, -2],
            [-2, -2],
        ]
        for circle_index in circle:
            if parsed_move[0] + circle_index[0] >= self.board_size[0] or parsed_move[0] + circle_index[0] < 0:
                continue
            if parsed_move[1] + circle_index[1] >= self.board_size[1] or parsed_move[1] + circle_index[1] < 0:
                continue

            if (board[parsed_move[0] + circle_index[0] + (parsed_move[1] + circle_index[1]) * self.board_size[1]]) != 0:
                return False
        return True

    def generate_next_moves(self, state, player):
        next_moves = []
        next_states = []

        for i in range(len(state["board_state"])):
            if state["board_state"][i] == 0 and not self.is_move_too_far_from_action(state["board_state"], i):
                next_moves.append(i)
        for idx, next_move in enumerate(next_moves):
            next_states.append({"board_state": state["board_state"].copy(), "lastMove": [next_move % self.board_size[0], next_move // self.board_size[1]], "sequences": None, "evaluation": None})
            next_states[idx]["board_state"][next_move] = player
            next_states[idx]["sequences"] = self.count_sequences(state["sequences"][0], state["sequences"][1], state["board_state"], next_states[idx]["board_state"], next_states[idx]["lastMove"])
            next_states[idx]["evaluation"] = self.evaluate(next_states[idx])
        # Make job of alpha-beta easier by ordering from best/worst move and restricing number of checked moves
        sorted_states = sorted(next_states, key=lambda k: k["evaluation"], reverse=(player == self.player_number))
        return sorted_states[: self.restrict_moves]

    def evaluate(self, state):
        if state["sequences"][0][self.winning_size] != 0:
            return float("inf") if (self.player_number == 1) else float("-inf")
        if state["sequences"][1][self.winning_size] != 0:
            return float("inf") if (self.player_number == -1) else float("-inf")
        return sum(
            (state["sequences"][0][i] - state["sequences"][1][i]) * self.scoring_array[i] if self.player_number == 1 else (state["sequences"][1][i] - state["sequences"][0][i]) * self.scoring_array[i]
            for i in range(1, self.winning_size)
        )

    def is_game_over(self, state):
        if state["sequences"][0][self.winning_size] != 0 or state["sequences"][1][self.winning_size] != 0:
            return True
        return all(state["board_state"][i] != 0 for i in range(len(state["board_state"])))

    def print_board(self, board):
        print("---------")
        for i in range(self.board_size[1]):
            print_row = []
            for j in range(self.board_size[0]):
                if board[i * self.board_size[0] + j] == 1:
                    print_row.append("X")
                if board[i * self.board_size[0] + j] == -1:
                    print_row.append("O")
                if board[i * self.board_size[0] + j] == 0:
                    print_row.append("-")
            print(print_row)
        print("---------")

    def minimax(self, state, depth, alpha, beta, maximizing):
        if depth == 0 or self.is_game_over(state):
            return (state["lastMove"], self.evaluate(state))
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
            next_moves = self.generate_next_moves(state, self.player_number * -1)
            for move in next_moves:
                node = self.minimax(move, depth - 1, alpha, beta, True)
                if node[1] <= value:
                    value = node[1]
                    best_move = node[0]
                beta = min(beta, value)
                if beta <= alpha:
                    break
        return best_move, value
