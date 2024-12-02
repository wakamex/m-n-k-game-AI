EMPTY = -1
NOONE = -1

class Game:
    def __init__(self, board_size_x, board_size_y, winning_size, total_games, agent1, agent2, end_turn_print):
        self.board = [EMPTY] * board_size_x * board_size_y
        self.board_size = [board_size_x, board_size_y]
        self.played_games = 0
        self.total_games = total_games
        self.player_turn = 0
        self.agents = [agent1, agent2]
        self.winning_size = winning_size
        self.scores = [0, 0]
        self.end_turn_print = end_turn_print

    def play_agent_move(self):
        move = self.agents[self.player_turn].get_next_move()
        self.play_move(move[0], move[1])

    def play_move(self, x, y):
        if self.board[y * self.board_size[1] + x] == EMPTY:
            self.board[y * self.board_size[1] + x] = self.player_turn
            print(f"{self.board=}")
            for agent in self.agents:
                agent.new_move_played(self.board)
            self.print_board()
            self.end_turn()

    def end_turn(self):
        self.check_for_win()
        self.player_turn = 1 - self.player_turn

    def handle_win(self, player_win):
        self.played_games += 1
        self.scores[player_win] += 1
        if self.played_games < self.total_games:
            self.board = [EMPTY] * self.board_size[0] * self.board_size[1]
            self.player_turn = 0
            self.agents[0].forget()
            self.agents[1].forget()
        else:
            print(f"Played {self.played_games} games, with scores: {self.scores[0]}:{self.scores[1]}")

    def check_for_win(self):
        # We trust agent in order to save time checking board, this could be handled by "referee" agent
        for player in range(2):
            print(f"{player=} {self.agents[player].memory['counts'][player]=}")
            if self.agents[player].memory["counts"][player][self.winning_size] >= 1:
                self.print_board()
                self.handle_win(player)
                return

        board_is_full = all(place != EMPTY for place in self.board)
        if board_is_full:
            self.handle_win(NOONE)

    def print_board(self):
        print("---------")
        for i in range(self.board_size[1]):
            print_row = []
            for j in range(self.board_size[0]):
                if self.board[i * self.board_size[0] + j] == 0:
                    print_row.append("X")
                if self.board[i * self.board_size[0] + j] == 1:
                    print_row.append("O")
                if self.board[i * self.board_size[0] + j] == EMPTY:
                    print_row.append("-")
            print(print_row)
        print("---------")
