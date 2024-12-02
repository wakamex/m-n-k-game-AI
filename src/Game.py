EMPTY = -1
NOONE = -1

class Game:
    def __init__(self, board_size, winning_size, end_turn_print=True):
        """Initialize a new game"""
        self.board_size = board_size if isinstance(board_size, tuple) else (board_size, board_size)
        self.winning_size = winning_size
        self.end_turn_print = end_turn_print
        self.board = [EMPTY] * (self.board_size[0] * self.board_size[1])
        self.agents = []
        self.player_turn = 0
        self.played_games = 0
        self.scores = [0, 0]
        self.winner = None

    def play_agent_move(self):
        """Play a move from the current agent"""
        move = self.agents[self.player_turn].get_next_move()
        
        # Validate move
        if self.board[move] != EMPTY:
            raise ValueError(f"Invalid move {move} - space already occupied")
            
        # Make move
        self.board[move] = self.player_turn
        
        # Notify agents
        for agent in self.agents:
            agent.new_move_played(self.board)
            
        # Check for win before switching turns
        if self.is_game_over():
            self.handle_win()
            return  # Don't switch turns after game is over
        
        # Switch turns if game is not over
        self.player_turn = 1 - self.player_turn

    def play_move(self, move):
        if move < 0 or move >= len(self.board):
            return
            
        if self.board[move] == EMPTY:
            self.board[move] = self.player_turn
            for agent in self.agents:
                agent.new_move_played(self.board)
            if self.end_turn_print:
                self.print_board()
            self.end_turn()
        else:
            return

    def end_turn(self):
        if self.is_game_over():
            self.handle_win()
        self.player_turn = 1 - self.player_turn

    def handle_win(self):
        """Handle end of game scoring"""
        self.played_games += 1
        if self.winner == NOONE:  # Tie game
            self.scores[0] += 0.5
            self.scores[1] += 0.5
        else:
            self.scores[self.winner] += 1.0
            
        if self.end_turn_print:
            print(f"Game over! Winner: {'Tie' if self.winner == NOONE else f'Player {self.winner}'}")
            print(f"Scores: {self.scores[0]}:{self.scores[1]}")
            
        # Reset for next game
        self.reset_game()

    def check_for_win(self):
        # We trust agent in order to save time checking board, this could be handled by "referee" agent
        for player in range(2):
            counts = self.agents[player].memory["counts"]
            player_offset = player * (self.winning_size + 1)
            if counts[player_offset + self.winning_size] >= 1:
                if self.end_turn_print:
                    self.print_board()
                self.handle_win()
                return

        board_is_full = all(place != EMPTY for place in self.board)
        if board_is_full:
            self.handle_win(NOONE)

    def is_game_over(self):
        """Check if the game is over"""
        # Check for winning sequences
        for i in range(len(self.board)):
            if self.board[i] == EMPTY:
                continue
                
            player = self.board[i]
            
            # Check horizontal
            if i % self.board_size[0] < self.board_size[0] - self.winning_size + 1:
                if all(self.board[i+j] == player for j in range(self.winning_size)):
                    self.winner = player
                    return True
                    
            # Check vertical
            if i < self.board_size[0] * (self.board_size[1] - self.winning_size + 1):
                if all(self.board[i+j*self.board_size[0]] == player for j in range(self.winning_size)):
                    self.winner = player
                    return True
                    
            # Check diagonal
            if i < self.board_size[0] * (self.board_size[1] - self.winning_size + 1) and i % self.board_size[0] < self.board_size[0] - self.winning_size + 1:
                if all(self.board[i+j*(self.board_size[0]+1)] == player for j in range(self.winning_size)):
                    self.winner = player
                    return True
                    
            if i < self.board_size[0] * (self.board_size[1] - self.winning_size + 1) and i % self.board_size[0] >= self.winning_size - 1:
                if all(self.board[i+j*(self.board_size[0]-1)] == player for j in range(self.winning_size)):
                    self.winner = player
                    return True
                    
        # Check for tie
        if all(x != EMPTY for x in self.board):
            self.winner = NOONE
            return True
            
        return False

    def reset_game(self):
        """Reset the game state for a new game"""
        self.board = [EMPTY] * (self.board_size[0] * self.board_size[1])
        self.player_turn = 0
        self.winner = None
        # Reset agent states
        for agent in self.agents:
            agent.forget()

    def print_board(self):
        print("---------")
        for i in range(self.board_size[1]):
            print_row = []
            for j in range(self.board_size[0]):
                idx = i * self.board_size[0] + j
                if self.board[idx] == 0:
                    print_row.append("X")
                elif self.board[idx] == 1:
                    print_row.append("O")
                else:
                    print_row.append("-")
            print(print_row)
        print("---------")
