from python import Python
from collections.vector import InlinedFixedVector
from agent_utils import print_board

alias EMPTY = 0
alias SIMD_WIDTH = 8  # Process 8 elements at a time

struct AgentState:
    var memory: InlinedFixedVector[Int, 1024]
    
    fn __init__(inout self):
        self.memory = InlinedFixedVector[Int, 1024](1024)
    
    fn forget(inout self):
        self.memory.clear()

struct GameState:
    """State for a game."""
    var board_size_x: Int
    var board_size_y: Int
    var played_games: Int
    var total_games: Int
    var player_turn: Int
    var winning_size: Int
    var scores: InlinedFixedVector[Int, 2]
    var end_turn_print: Bool
    var board: InlinedFixedVector[Int, 1024]
    var winner: Int
    var current_player: Int
    var agent1: AgentState
    var agent2: AgentState

    fn __init__(inout self, board_size_x: Int, board_size_y: Int, winning_size: Int = 3, total_games: Int = 1, end_turn_print: Bool = True) raises:
        if board_size_x <= 0 or board_size_y <= 0 or winning_size <= 0:
            raise Error("Invalid board or winning size")
            
        var board_size = board_size_x * board_size_y
        if board_size > 1024:
            raise Error("Board size too large")
            
        self.board_size_x = board_size_x
        self.board_size_y = board_size_y
        self.board = InlinedFixedVector[Int, 1024](board_size)
        # Initialize board to empty
        for i in range(board_size):
            self.board.append(EMPTY)
            
        self.played_games = 0
        self.total_games = total_games
        self.player_turn = 0
        self.winning_size = winning_size
        self.scores = InlinedFixedVector[Int, 2](2)
        self.scores.append(0)
        self.scores.append(0)
        self.end_turn_print = end_turn_print
        self.winner = EMPTY
        self.current_player = 1
        self.agent1 = AgentState()
        self.agent2 = AgentState()
        
        print("GameState initialized with:")
        print("Board size:", board_size_x, "x", board_size_y)
        print("Board length:", len(self.board))
        print("Winning size:", winning_size)
        print("Total games:", total_games)

    fn is_valid_move(self, x: Int, y: Int) -> Bool:
        if x < 0 or x >= self.board_size_x:
            return False
        if y < 0 or y >= self.board_size_y:
            return False
        var idx = y * self.board_size_x + x
        return idx < len(self.board) and self.board[idx] == EMPTY

    fn play_move(inout self, x: Int, y: Int) raises:
        print("Attempting to play move at:", x, ",", y)
        if not self.is_valid_move(x, y):
            print("Invalid move at position:", x, ",", y)
            print("Board state:")
            self.print_board()
            raise Error("Invalid move")
        
        var idx = y * self.board_size_x + x
        if idx >= len(self.board):
            print("Index out of bounds:", idx, ">=", len(self.board))
            print("Board dimensions:", self.board_size_x, "x", self.board_size_y)
            print("Move position:", x, ",", y)
            raise Error("Invalid move: index out of bounds")
            
        print("Playing move for player", self.player_turn, "at position", x, ",", y)
        self.board[idx] = self.player_turn
        
        # Notify agents
        for i in range(2):
            # In real implementation, this would update agent state
            pass
        
        if self.end_turn_print:
            self.print_board()
        print("Ending turn")
        self.end_turn()

    fn end_turn(inout self):
        print("Checking for win")
        self.check_for_win()
        print("Switching player turn from", self.player_turn, "to", 1 - self.player_turn)
        self.player_turn = 1 - self.player_turn

    fn check_for_win(inout self):
        print("Checking rows for win")
        # Check rows
        for y in range(self.board_size_y):
            var count = 1
            var last_value = self.board[y * self.board_size_x]
            for x in range(1, self.board_size_x):
                var current = self.board[y * self.board_size_x + x]
                if current == last_value and current != EMPTY:
                    count += 1
                    if count >= self.winning_size:
                        self.handle_win(last_value)
                        return
                else:
                    count = 1
                last_value = current

        # Check columns
        for x in range(self.board_size_x):
            var count = 1
            var last_value = self.board[x]  # First row, column x
            for y in range(1, self.board_size_y):
                var current = self.board[y * self.board_size_x + x]
                if current == last_value and current != EMPTY:
                    count += 1
                    if count >= self.winning_size:
                        self.handle_win(last_value)
                        return
                else:
                    count = 1
                    last_value = current

        # Check diagonals
        # Main diagonals
        for y in range(self.board_size_y - self.winning_size + 1):
            for x in range(self.board_size_x - self.winning_size + 1):
                var count = 1
                var last_value = self.board[y * self.board_size_x + x]
                for i in range(1, min(self.board_size_x - x, self.board_size_y - y)):
                    var current = self.board[(y + i) * self.board_size_x + (x + i)]
                    if current == last_value and current != EMPTY:
                        count += 1
                        if count >= self.winning_size:
                            self.handle_win(last_value)
                            return
                    else:
                        count = 1
                        last_value = current

        # Anti-diagonals
        for y in range(self.board_size_y - self.winning_size + 1):
            for x in range(self.winning_size - 1, self.board_size_x):
                var count = 1
                var last_value = self.board[y * self.board_size_x + x]
                for i in range(1, min(x + 1, self.board_size_y - y)):
                    var current = self.board[(y + i) * self.board_size_x + (x - i)]
                    if current == last_value and current != EMPTY:
                        count += 1
                        if count >= self.winning_size:
                            self.handle_win(last_value)
                            return
                    else:
                        count = 1
                        last_value = current

    fn handle_win(inout self, player_win: Int):
        self.played_games += 1
        if player_win != NOONE:
            self.scores[player_win] += 1
        
        if self.played_games < self.total_games:
            self.reset_board()
        else:
            print("Game Over! Final scores after", self.played_games, "games:")
            print("Player 1:", self.scores[0])
            print("Player 2:", self.scores[1])

    fn reset_board(inout self):
        for i in range(len(self.board)):
            self.board[i] = EMPTY
        self.player_turn = 0
        self.winner = EMPTY
        self.current_player = 1
        self.agent1.forget()
        self.agent2.forget()

    fn play_agent_move(inout self) raises:
        # For now, just play in the first available spot
        for y in range(self.board_size_y):
            for x in range(self.board_size_x):
                if self.is_valid_move(x, y):
                    self.play_move(x, y)
                    return
        raise Error("No valid moves available")

    fn make_move(inout self, x: Int, y: Int, player: Int) -> Bool:
        """Make a move at the specified position."""
        if x < 0 or x >= self.board_size_x or y < 0 or y >= self.board_size_y:
            return False
            
        var pos = y * self.board_size_x + x
        if self.board[pos] != EMPTY:
            return False
            
        self.board[pos] = player
        self.player_turn = 3 - player  # Switch between 1 and 2
        self.current_player = 3 - player
        
        # Check if this move wins the game
        if self.check_win(x, y, player):
            self.winner = player
            
        return True
        
    fn check_win(self, x: Int, y: Int, player: Int) -> Bool:
        """Check if the last move at (x,y) wins the game."""
        # Check horizontal
        var count = 0
        for i in range(self.board_size_x):
            if self.board[y * self.board_size_x + i] == player:
                count += 1
                if count == 3:  # Win condition
                    return True
            else:
                count = 0
                
        # Check vertical
        count = 0
        for i in range(self.board_size_y):
            if self.board[i * self.board_size_x + x] == player:
                count += 1
                if count == 3:  # Win condition
                    return True
            else:
                count = 0
                
        # Check diagonal (top-left to bottom-right)
        count = 0
        var start_x = x - min(x, y)
        var start_y = y - min(x, y)
        while start_x < self.board_size_x and start_y < self.board_size_y:
            if self.board[start_y * self.board_size_x + start_x] == player:
                count += 1
                if count == 3:  # Win condition
                    return True
            else:
                count = 0
            start_x += 1
            start_y += 1
            
        # Check diagonal (top-right to bottom-left)
        count = 0
        start_x = x + min(self.board_size_x - 1 - x, y)
        start_y = y - min(self.board_size_x - 1 - x, y)
        while start_x >= 0 and start_y < self.board_size_y:
            if self.board[start_y * self.board_size_x + start_x] == player:
                count += 1
                if count == 3:  # Win condition
                    return True
            else:
                count = 0
            start_x -= 1
            start_y += 1
            
        return False
        
    fn is_game_over(self) -> Bool:
        """Check if the game is over."""
        # Check for winner
        if self.winner != EMPTY:
            return True
            
        # Check for draw (board full)
        var is_full = True
        for i in range(self.board_size_x * self.board_size_y):
            if self.board[i] == EMPTY:
                is_full = False
                break
                
        return is_full
