from mnk.Agent import Agent
from mnk.Game import Game
import time

from mnk.constants import EMPTY, NOONE, MAX_TIME

# Configuration
BOARD_SIZE = (3, 3)
WINNING_SIZE = 3
TOTAL_GAMES = 10
PRINT_MOVES = False # Set to True to see game play

# Agent configurations - now includes depth
AGENTS_CONFIG = [
    # {"name": "DeepSpread", "scoring": [1000, 10, 10, 10], "depth": 4},
    {"name": "ShallowLinear", "scoring": [1, 10, 100, 1000], "depth": 2},
    {"name": "ShallowerLinear", "scoring": [1, 10, 100, 1000], "depth": 1}
]

# If you want to play with agents having the same depth, adjust here or in AGENTS_CONFIG
DEFAULT_AGENT_DEPTH = 3

# Helper functions
def generate_circle(radius):
    # Generates a list of (dx, dy) tuples for a filled circle
    # Corrected to only include unique points and handle radius 0
    if radius < 0: return []
    if radius == 0: return [(0,0)]
    points = set()
    for r_sq in range(radius * radius + 1): # Iterate over squared radius
        for dx_candidate in range(-radius, radius + 1):
            dy_sq_candidate = r_sq - dx_candidate * dx_candidate
            if dy_sq_candidate >= 0:
                dy_candidate_abs = int(round(dy_sq_candidate**0.5))
                if dy_candidate_abs * dy_candidate_abs == dy_sq_candidate : # Check if dy_sq_candidate is a perfect square
                    points.add((dx_candidate, dy_candidate_abs))
                    points.add((dx_candidate, -dy_candidate_abs))
    # Ensure the provided circle_of_two logic from Agent.py is used if it's different.
    # The one in Agent.py `is_move_too_far_from_action` seems to expect a pre-defined list.
    # Let's use a simpler square for this example, as in the original project
    return [(dx, dy) for dx in range(-radius, radius + 1)
                    for dy in range(-radius, radius + 1)
                    if not (dx == 0 and dy == 0)] # Exclude center for "nearby" check

CIRCLE_OF_TWO_CONFIG = generate_circle(2) # For the agent

def run_tournament(agent_config1, agent_config2, num_games=100): # Take full configs
    """Run a tournament between two agents"""
    game = Game(BOARD_SIZE, WINNING_SIZE, PRINT_MOVES) # Use global PRINT_MOVES

    # Create agents based on configs
    # Player 0 always uses agent_config1, Player 1 always uses agent_config2 for this specific match setup
    # Swapping happens by changing which config is agent_config1/agent_config2 in the outer loop
    agent1 = Agent(player_number=0, board_size=BOARD_SIZE, winning_size=WINNING_SIZE,
                   scoring_array=agent_config1["scoring"], circle_of_two=CIRCLE_OF_TWO_CONFIG,
                   name=agent_config1["name"], depth=agent_config1.get("depth", DEFAULT_AGENT_DEPTH))
    
    agent2 = Agent(player_number=1, board_size=BOARD_SIZE, winning_size=WINNING_SIZE,
                   scoring_array=agent_config2["scoring"], circle_of_two=CIRCLE_OF_TWO_CONFIG,
                   name=agent_config2["name"], depth=agent_config2.get("depth", DEFAULT_AGENT_DEPTH))

    game.agents = [agent1, agent2]
    agent1.set_game(game)
    agent2.set_game(game)

    print(f"\n--- {agent1.name} (P0, Depth {agent1.search_depth}) vs {agent2.name} (P1, Depth {agent2.search_depth}) ---")

    match_scores = [0, 0] # agent1_wins, agent2_wins for this specific pairing
    draws = 0

    for i in range(num_games):
        game_start_time = time.time()
        print(f"Starting game {i+1}/{num_games}...")
        game.reset_game() # Reset board, player_turn, winner, and agent memory

        # In this setup, agent1 is always P0 and agent2 is always P1 for this match.
        # If you want to swap who starts, you'd need a different loop structure or pass player assignments.
        # The original code swapped agent objects in game.agents.
        # Let's stick to agent1=P0, agent2=P1 for this match for simplicity of score tracking.
        # Swapping of who is "agent_config1" happens in main().

        while not game.is_game_over():
            if PRINT_MOVES:
                print(f"Turn for Player {game.player_turn} ({game.agents[game.player_turn].name})")
            
            current_agent = game.agents[game.player_turn]
            
            # Add timeout for agent's move
            move_decision_start = time.time()
            try:
                move = current_agent.get_next_move()
            except Exception as e:
                print(f"Error during get_next_move for {current_agent.name}: {e}")
                game.winner = 1 - current_agent.player_number # Opponent wins by default
                if PRINT_MOVES: game.print_board()
                break # End game
            
            move_decision_time = time.time() - move_decision_start
            if PRINT_MOVES:
                print(f"{current_agent.name} (P{current_agent.player_number}) plays at index {move} (Time: {move_decision_time:.3f}s)")

            if game.board[move] != EMPTY: # Should be caught by agent, but as a safeguard
                print(f"Error: Agent {current_agent.name} tried to play on occupied spot {move}. Opponent wins.")
                game.winner = 1 - current_agent.player_number
                if PRINT_MOVES: game.print_board()
                break
            
            game.play_move(move) # play_move updates board, notifies agents, and switches turn (or handles win)

            if time.time() - game_start_time > (MAX_TIME * (BOARD_SIZE[0]*BOARD_SIZE[1])): # Game timeout
                 print(f"Game {i+1} timed out. Declaring draw.")
                 game.winner = NOONE # Tie
                 break
        
        # After game.is_game_over() or break:
        if game.winner == 0: # Agent1 (P0) won
            match_scores[0] += 1
        elif game.winner == 1: # Agent2 (P1) won
            match_scores[1] += 1
        elif game.winner == NOONE: # Draw
            draws += 1
        else: # Should not happen if winner is properly NOONE for draw
            print(f"Unknown game winner state: {game.winner}")
            draws +=1 # Count as draw

        if (i + 1) % (num_games // 10 if num_games >=10 else 1) == 0 or i == num_games -1 :
            print(f"Game {i+1} ended. Winner: Player {game.winner if game.winner != NOONE else 'Draw'}. "
                  f"Current match score: {agent1.name} {match_scores[0]} - {agent2.name} {match_scores[1]} (Draws: {draws})")

    return match_scores, draws


def main():
    all_agent_configs = AGENTS_CONFIG.copy()
    
    # Store overall tournament results: agent_name -> {wins: x, losses: y, draws: z, games_played: n}
    tournament_results = {cfg["name"]: {"wins": 0, "losses": 0, "draws": 0, "games_played":0} for cfg in all_agent_configs}

    for i in range(len(all_agent_configs)):
        for j in range(i + 1, len(all_agent_configs)):
            config1 = all_agent_configs[i]
            config2 = all_agent_configs[j]

            # Match 1: config1 as P0, config2 as P1
            print(f"\n=== Match: {config1['name']} (P0) vs {config2['name']} (P1) ===")
            scores1, draws1 = run_tournament(config1, config2, TOTAL_GAMES // 2 or 1) # Play half games
            tournament_results[config1['name']]['wins'] += scores1[0]
            tournament_results[config1['name']]['games_played'] += (TOTAL_GAMES // 2 or 1)
            tournament_results[config2['name']]['losses'] += scores1[0] # P2 loss = P1 win

            tournament_results[config2['name']]['wins'] += scores1[1]
            tournament_results[config2['name']]['games_played'] += (TOTAL_GAMES // 2 or 1)
            tournament_results[config1['name']]['losses'] += scores1[1] # P1 loss = P2 win
            
            tournament_results[config1['name']]['draws'] += draws1
            tournament_results[config2['name']]['draws'] += draws1


            # Match 2: config2 as P0, config1 as P1
            print(f"\n=== Match: {config2['name']} (P0) vs {config1['name']} (P1) ===")
            scores2, draws2 = run_tournament(config2, config1, TOTAL_GAMES // 2 or 1) # Play other half
            tournament_results[config2['name']]['wins'] += scores2[0]
            tournament_results[config2['name']]['games_played'] += (TOTAL_GAMES // 2 or 1)
            tournament_results[config1['name']]['losses'] += scores2[0]

            tournament_results[config1['name']]['wins'] += scores2[1]
            tournament_results[config1['name']]['games_played'] += (TOTAL_GAMES // 2 or 1)
            tournament_results[config2['name']]['losses'] += scores2[1]

            tournament_results[config2['name']]['draws'] += draws2
            tournament_results[config1['name']]['draws'] += draws2


    print("\n--- Overall Tournament Results ---")
    for name, stats in tournament_results.items():
        win_rate = (stats['wins'] / stats['games_played'] * 100) if stats['games_played'] > 0 else 0
        print(f"{name}: Wins: {stats['wins']}, Losses: {stats['losses']}, Draws: {stats['draws']} "
              f"(Games: {stats['games_played']}, Win Rate: {win_rate:.1f}%)")


if __name__ == "__main__":
    main()