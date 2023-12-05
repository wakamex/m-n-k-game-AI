class Game:
    def __init__(self, board_size_x, board_size_y, winning_size, total_games, agent1, agent2, end_turn_print):
        self.board = [0] * board_size_x * board_size_y
        self.board_size = [board_size_x, board_size_y]
        self.played_games = 0
        self.total_games = total_games
        self.player_turn = 1
        self.agents = [agent1, agent2]
        self.winning_size = winning_size
        self.scores = [0, 0]
        self.end_turn_print = end_turn_print

    def play_agent_move(self):
        move = self.get_agent_move()
        self.play_move(move[0], move[1])

    def get_agent_move(self):
        if self.player_turn == 1:
            return self.agents[0].get_next_move()
        return self.agents[1].get_next_move()

    def play_move(self, x, y):
        if self.board[y * self.board_size[1] + x] == 0:
            self.board[y * self.board_size[1] + x] = self.player_turn
            for agent in self.agents:
                agent.new_move_played(self.board)
            if self.end_turn_print:
                self.print_board()
            self.end_turn()

    def end_turn(self):
        self.check_for_win()
        self.player_turn = -1 * self.player_turn

    def handle_win(self, player_win):
        self.played_games += 1
        if player_win == -1:
            self.scores[1] += 1
        elif player_win == 1:
            self.scores[0] += 1
        if self.played_games < self.total_games:
            self.board = [0] * self.board_size[0] * self.board_size[1]
            self.player_turn = 1
            self.agents[0].forget()
            self.agents[1].forget()
        else:
            print(f"Played {self.played_games} games, with scores: {str(self.scores[0])}:{str(self.scores[1])}")

    def check_for_win(self):
        # We trust agent in order to save time checking board, this could be handled by "referee" agent
        if self.agents[0].memory["last_board_state_sequence"]["player_one"][self.winning_size] >= 1:
            self.handle_win(1)
            return

        if self.agents[0].memory["last_board_state_sequence"]["player_two"][self.winning_size] >= 1:
            self.handle_win(-1)
            return

        board_is_full = all(place != 0 for place in self.board)
        if board_is_full:
            self.handle_win(0)

    def print_board(self):
        print("---------")
        for i in range(self.board_size[1]):
            print_row = []
            for j in range(self.board_size[0]):
                if self.board[i * self.board_size[0] + j] == 1:
                    print_row.append("X")
                if self.board[i * self.board_size[0] + j] == -1:
                    print_row.append("O")
                if self.board[i * self.board_size[0] + j] == 0:
                    print_row.append("-")
            print(print_row)
        print("---------")
