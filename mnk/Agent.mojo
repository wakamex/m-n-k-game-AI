from python import Python
from collections.vector import InlinedFixedVector
from time import now

alias EMPTY = 0
alias BOARD_SIZE_X = 15
alias BOARD_SIZE_Y = 15
alias WIN_SIZE = 5
alias DEPTH = 2
alias SIMD_WIDTH = 8

struct AgentState:
    """Represents the state of an agent."""
    var player_number: Int
    var board_size_x: Int
    var board_size_y: Int
    var winning_size: Int
    var scoring_array: InlinedFixedVector[Int, 1024]
    var restrict_moves: Bool
    var _seed: Int  # Make this private and mutable
    var depth: Int  # Search depth
    var last_board_state: InlinedFixedVector[Int, 1024]
    var last_move_x: Int
    var last_move_y: Int
    var counts: InlinedFixedVector[Int, 1024]
    var directions: InlinedFixedVector[Int, 8]
    
    fn __init__(inout self, player_number: Int, board_size_x: Int, board_size_y: Int, winning_size: Int = 3, scoring_array: InlinedFixedVector[Int, 1024] = InlinedFixedVector[Int, 1024](1024), restrict_moves: Bool = False, depth: Int = 1):
        self.player_number = player_number
        self.board_size_x = board_size_x
        self.board_size_y = board_size_y
        self.winning_size = winning_size
        self.scoring_array = scoring_array
        self.restrict_moves = restrict_moves
        self._seed = 42
        self.depth = depth
        self.last_board_state = InlinedFixedVector[Int, 1024](1024)
        self.last_move_x = -1
        self.last_move_y = -1
        self.counts = InlinedFixedVector[Int, 1024](1024)
        self.directions = InlinedFixedVector[Int, 8](8)
        # Initialize directions
        self.directions[0] = 0
        self.directions[1] = 1
        self.directions[2] = 1
        self.directions[3] = 0
        self.directions[4] = 0
        self.directions[5] = -1
        self.directions[6] = -1
        self.directions[7] = 0
    
    fn random_int(inout self, min_val: Int, max_val: Int) -> Int:
        """Generate a random integer between min_val and max_val."""
        var a = 1664525
        var c = 1013904223
        var m = 2**32
        self._seed = (a * self._seed + c) % m
        return min_val + (self._seed % (max_val - min_val + 1))
    
    fn get_next_move(inout self, board: InlinedFixedVector[Int, 1024]) -> Tuple[Int, Int]:
        """Get the next move for this agent."""
        print("Entering get_next_move with depth:", self.depth)
        var start_time = now()
        
        # Use minimax to find the best move
        var best_x = -1
        var best_y = -1
        var best_eval = -1e9
        
        # Get possible moves
        var moves_x = InlinedFixedVector[Int, 100](100)
        var moves_y = InlinedFixedVector[Int, 100](100)
        var move_count = generate_next_moves(self, board, moves_x, moves_y)
        
        for i in range(move_count):
            var x = moves_x[i]
            var y = moves_y[i]
            var pos = y * self.board_size_x + x
            
            # Make move on a new board
            var new_board = InlinedFixedVector[Int, 1024](len(board))
            for j in range(len(board)):
                new_board[j] = board[j]
            new_board[pos] = self.player_number
            
            # Player 1 maximizes, Player 2 minimizes
            var eval = minimax(self, new_board, self.depth - 1, self.player_number == 1)
            if eval > best_eval:
                best_eval = eval
                best_x = x
                best_y = y
        
        var end_time = now()
        print("Minimax search took:", Float64(end_time - start_time) / 1_000_000.0, "ms")
        print("Best move found:", best_x, best_y, "with eval:", best_eval)
        return (best_x, best_y)
        
    fn check_win(self, board: InlinedFixedVector[Int, 1024], x: Int, y: Int) -> Bool:
        """Check if the last move at (x,y) wins the game."""
        var player = board[y * self.board_size_x + x]
        
        # Check horizontal
        var count = 0
        for i in range(self.board_size_x):
            if board[y * self.board_size_x + i] == player:
                count += 1
                if count == self.winning_size:
                    return True
            else:
                count = 0
                
        # Check vertical
        count = 0
        for i in range(self.board_size_y):
            if board[i * self.board_size_x + x] == player:
                count += 1
                if count == self.winning_size:
                    return True
            else:
                count = 0
                
        # Check diagonal (top-left to bottom-right)
        count = 0
        var start_x = x - min(x, y)
        var start_y = y - min(x, y)
        while start_x < self.board_size_x and start_y < self.board_size_y:
            if board[start_y * self.board_size_x + start_x] == player:
                count += 1
                if count == self.winning_size:
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
            if board[start_y * self.board_size_x + start_x] == player:
                count += 1
                if count == self.winning_size:
                    return True
            else:
                count = 0
            start_x -= 1
            start_y += 1
            
        return False

fn generate_next_moves(state: AgentState, board: InlinedFixedVector[Int, 1024], inout moves_x: InlinedFixedVector[Int, 100], inout moves_y: InlinedFixedVector[Int, 100]) -> Int:
    """Generate all possible next moves for the current player. Returns number of moves found."""
    var move_count = 0
    
    # Try all possible moves
    for y in range(state.board_size_y):
        for x in range(state.board_size_x):
            if board[y * state.board_size_x + x] == EMPTY:
                if move_count < 100:
                    moves_x[move_count] = x
                    moves_y[move_count] = y
                    move_count += 1
    
    return move_count

fn minimax(state: AgentState, board: InlinedFixedVector[Int, 1024], depth: Int, maximizing: Bool) -> Float64:
    """Minimax algorithm with alpha-beta pruning."""
    print("Minimax depth:", depth, "maximizing:", maximizing)
    
    # Base case - evaluate position
    if depth == 0:
        # When evaluating, we need to consider whose turn it is
        var eval = evaluate(state, count_sequences(state, board))
        return eval if maximizing else -eval
    
    # Generate possible moves
    var moves_x = InlinedFixedVector[Int, 100](100)
    var moves_y = InlinedFixedVector[Int, 100](100)
    var move_count = generate_next_moves(state, board, moves_x, moves_y)
    
    if move_count == 0:
        var eval = evaluate(state, count_sequences(state, board))
        return eval if maximizing else -eval
    
    var best_eval = -1e9 if maximizing else 1e9
    
    for i in range(move_count):
        var x = moves_x[i]
        var y = moves_y[i]
        var pos = y * state.board_size_x + x
        
        # Make move
        var new_board = InlinedFixedVector[Int, 1024](len(board))
        for j in range(len(board)):
            new_board[j] = board[j]
        # Use current player's number for the move
        new_board[pos] = state.player_number
        
        # Check if this move wins
        if state.check_win(new_board, x, y):
            return 1e6 if maximizing else -1e6
        
        # Create opponent state for next turn
        var next_state = AgentState(state.board_size_x, state.board_size_y, state.winning_size, 3 - state.player_number)
        var eval = minimax(next_state, new_board, depth - 1, not maximizing)
        
        # Update best evaluation based on maximizing/minimizing
        best_eval = max(best_eval, eval) if maximizing else min(best_eval, eval)
    
    return best_eval

fn evaluate(state: AgentState, sequences: Sequences) -> Float64:
    """Evaluate a board position."""
    if sequences.win:
        return 1e6
    return Float64(sequences.count)

struct Sequences:
    var count: Int
    var win: Bool
    
    fn __init__(inout self, count: Int, win: Bool):
        self.count = count
        self.win = win

fn count_sequences(state: AgentState, board: InlinedFixedVector[Int, 1024]) -> Sequences:
    """Count the number of sequences for the current player.
    For a sequence of length N, we count:
    - N singles (one for each piece)
    - N-1 sequences of length 2
    - N-2 sequences of length 3
    etc.
    """
    var count = 0
    var win = False
    
    # Check horizontal sequences
    for y in range(state.board_size_y):
        for x in range(state.board_size_x):
            if board[y * state.board_size_x + x] != state.player_number:
                continue
                
            # Count this as a single
            count += 1
                
            # Only start sequence from leftmost position
            if x > 0 and board[y * state.board_size_x + x - 1] == state.player_number:
                continue
                
            # Count sequence length
            var length = 1
            var curr_x = x + 1
            while curr_x < state.board_size_x:
                if board[y * state.board_size_x + curr_x] != state.player_number:
                    break
                length += 1
                curr_x += 1
                
            # Record sequence if longer than 1
            if length > 1:
                # For a sequence of length N, count:
                # - N-1 sequences of length 2
                # - N-2 sequences of length 3
                # etc.
                for seq_len in range(2, length + 1):
                    if seq_len <= state.winning_size:
                        count += length - seq_len + 1
                if length >= state.winning_size:
                    win = True
    
    # Check vertical sequences
    for x in range(state.board_size_x):
        for y in range(state.board_size_y):
            if board[y * state.board_size_x + x] != state.player_number:
                continue
                
            # Only start sequence from topmost position
            if y > 0 and board[(y - 1) * state.board_size_x + x] == state.player_number:
                continue
                
            # Count sequence length
            var length = 1
            var curr_y = y + 1
            while curr_y < state.board_size_y:
                if board[curr_y * state.board_size_x + x] != state.player_number:
                    break
                length += 1
                curr_y += 1
                
            # Record sequence if longer than 1
            if length > 1:
                for seq_len in range(2, length + 1):
                    if seq_len <= state.winning_size:
                        count += length - seq_len + 1
                if length >= state.winning_size:
                    win = True
    
    # Check diagonal sequences (top-left to bottom-right)
    for y in range(state.board_size_y):
        for x in range(state.board_size_x):
            if board[y * state.board_size_x + x] != state.player_number:
                continue
                
            # Only start sequence from topmost/leftmost position
            if (x > 0 and y > 0 and 
                board[(y - 1) * state.board_size_x + (x - 1)] == state.player_number):
                continue
                
            # Count sequence length
            var length = 1
            var curr_x = x + 1
            var curr_y = y + 1
            while (curr_x < state.board_size_x and 
                   curr_y < state.board_size_y):
                if board[curr_y * state.board_size_x + curr_x] != state.player_number:
                    break
                length += 1
                curr_x += 1
                curr_y += 1
                
            # Record sequence if longer than 1
            if length > 1:
                for seq_len in range(2, length + 1):
                    if seq_len <= state.winning_size:
                        count += length - seq_len + 1
                if length >= state.winning_size:
                    win = True
    
    # Check diagonal sequences (top-right to bottom-left)
    for y in range(state.board_size_y):
        for x in range(state.board_size_x):
            if board[y * state.board_size_x + x] != state.player_number:
                continue
                
            # Only start sequence from topmost/rightmost position
            if (x < state.board_size_x - 1 and y > 0 and 
                board[(y - 1) * state.board_size_x + (x + 1)] == state.player_number):
                continue
                
            # Count sequence length
            var length = 1
            var curr_x = x - 1
            var curr_y = y + 1
            while (curr_x >= 0 and 
                   curr_y < state.board_size_y):
                if board[curr_y * state.board_size_x + curr_x] != state.player_number:
                    break
                length += 1
                curr_x -= 1
                curr_y += 1
                
            # Record sequence if longer than 1
            if length > 1:
                for seq_len in range(2, length + 1):
                    if seq_len <= state.winning_size:
                        count += length - seq_len + 1
                if length >= state.winning_size:
                    win = True
    
    return Sequences(count=count, win=win)

fn new_move_played(inout state: AgentState, board: InlinedFixedVector[Int, 1024]):
    """Update agent state with new board state."""
    print("Entering new_move_played")
    # Find the new move
    for i in range(len(board)):
        if board[i] != state.last_board_state[i]:
            print("Found new move at index:", i)
            state.last_move_x = i % state.board_size_x
            state.last_move_y = i // state.board_size_x
            print("Updated last_move to:", state.last_move_x, state.last_move_y)
            break
    
    print("Counting sequences")
    # Update counts
    var new_counts = count_sequences(state, board)
    print("Updating counts array")
    for i in range(len(state.counts)):
        state.counts[i] = new_counts[i]
    
    print("Updating board state")
    # Update board state
    for i in range(len(board)):
        state.last_board_state[i] = board[i]
    print("Finished new_move_played")

fn is_move_too_far(state: AgentState, board: InlinedFixedVector[Int, 1024], move_x: Int, move_y: Int) -> Bool:
    """Check if a move is too far from existing pieces."""
    for i in range(0, len(state.directions), 2):
        let dir_x = state.directions[i]
        let dir_y = state.directions[i + 1]
        let x = move_x + dir_x
        let y = move_y + dir_y
        if 0 <= x < state.board_size_x and 0 <= y < state.board_size_y:
            if board[x + y * state.board_size_x] != EMPTY:
                return False
    return True

fn can_form_sequence(state: AgentState, board: InlinedFixedVector[Int, 1024], pos: Int, direction: Int) -> Bool:
    """Check if a sequence can be formed from a given position."""
    print("Checking sequence from pos:", pos, "direction:", direction)
    var x = pos % state.board_size_x
    var y = pos // state.board_size_x
    var dx = state.directions[direction * 2]
    var dy = state.directions[direction * 2 + 1]
    print("Starting at x:", x, "y:", y, "dx:", dx, "dy:", dy)
    
    # Only check sequences that start with a piece
    if board[pos] == EMPTY:
        print("Starting position is empty")
        return False
    
    # Check if we can fit a winning sequence from this position
    var max_length = 1
    var current_player = board[pos]
    var has_empty = False
    
    for i in range(1, state.winning_size):
        var nx = x + i * dx
        var ny = y + i * dy
        if nx < 0 or nx >= state.board_size_x or ny < 0 or ny >= state.board_size_y:
            break
        var piece = board[ny * state.board_size_x + nx]
        if piece == current_player:
            max_length += 1
        elif piece == EMPTY:
            has_empty = True
            max_length += 1
        else:
            break
    
    print("Max possible length:", max_length, "has empty spaces:", has_empty)
    # We should only count sequences that:
    # 1. Can potentially reach winning_size (have enough space)
    # 2. Have at least one empty space (can still grow)
    return max_length >= state.winning_size and has_empty

fn get_next_pos(pos: Int, direction: Int, state: AgentState) -> Int:
    """Get the next position in a given direction."""
    print("get_next_pos - pos:", pos, "direction:", direction)
    var x = pos % state.board_size_x
    var y = pos // state.board_size_x
    var dx = state.directions[direction * 2]
    var dy = state.directions[direction * 2 + 1]
    print("Current position - x:", x, "y:", y, "dx:", dx, "dy:", dy)
    
    x += dx
    y += dy
    print("Next position - x:", x, "y:", y)
    
    if x < 0 or x >= state.board_size_x or y < 0 or y >= state.board_size_y:
        print("Position out of bounds")
        return len(state.last_board_state)
    
    var next_pos = y * state.board_size_x + x
    print("Returning next_pos:", next_pos)
    return next_pos

fn has_board_changed(self: Self, board: InlinedFixedVector[Int, 1024]) -> Bool:
    """Check if the board has changed since last time."""
    var changed = False
    for i in range(len(board)):
        if board[i] != 0:  # Compare with empty space instead of last_board_state
            changed = True
            break
    return changed
