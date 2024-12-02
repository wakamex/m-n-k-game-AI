from src.Agent import Agent
from src.Game import Game
import time

# Configuration
BOARD_SIZE = (3, 3)  # Changed from list to tuple
WINNING_SIZE = 3
TOTAL_GAMES = 10  # Reduced from 100 for testing
PRINT_MOVES = False

# Agent configurations
AGENTS = [
    {"name": "Spread", "scoring": [1000, 10, 10, 10]},
    {"name": "Linear", "scoring": [1, 10, 100, 1000]}
]

# Helper functions
def generate_circle(radius):
    return [(dx, dy) for dx in range(-radius, radius + 1)
                    for dy in range(-radius, radius + 1)
                    if dx**2 + dy**2 <= radius**2]

CIRCLE_OF_TWO = generate_circle(2)

def run_tournament(agent1, agent2, num_games=100):
    """Run a tournament between two agents"""
    game = Game(BOARD_SIZE, WINNING_SIZE, False)
    game.agents = [agent1, agent2]
    
    # Set up agents
    agent1.set_game(game)
    agent2.set_game(game)
    
    print(f"{agent1.name} vs {agent2.name}")
    
    start_time = time.time()
    max_time_per_game = 5  # Maximum seconds per game
    
    scores = [0, 0]
    for i in range(num_games):
        game_start = time.time()
        while not game.is_game_over():
            game.play_agent_move()
            if time.time() - game_start > max_time_per_game:
                print(f"Game {i+1} timed out")
                game.winner = None  # Force a tie
                break
        
        # Update total scores based on who played as player 0/1
        if i % 2 == 0:
            scores[0] += game.scores[0]
            scores[1] += game.scores[1]
        else:
            scores[0] += game.scores[1]
            scores[1] += game.scores[0]
        
        # Reset for next game and swap players
        game.reset_game()
        if i % 2 == 1:
            game.agents = [agent1, agent2]
        else:
            game.agents = [agent2, agent1]
        
        # Print progress
        if (i + 1) % 10 == 0:
            print(f"Completed {i+1} games. Current score: {scores[0]}:{scores[1]}")
            
    total_time = time.time() - start_time
    print(f"\nTournament complete!")
    print(f"Final score: {agent1.name}: {scores[0]}, {agent2.name}: {scores[1]}")
    print(f"Win rates: {agent1.name}: {scores[0]/num_games:.1%}, {agent2.name}: {scores[1]/num_games:.1%}")
    print(f"Total time: {total_time:.1f}s, Average time per game: {total_time/num_games:.2f}s")

def main():
    agents = AGENTS.copy()
    while len(agents) > 1:
        # Each agent plays with each, after agent plays with everyone we don't have to consider them for other matches
        pivot_agent = agents.pop()
        print(f"\n{pivot_agent['name']} tournament results:")
        for agent in agents:
            print(f"\n{pivot_agent['name']} vs {agent['name']}")
            
            # Create fresh agents for this match
            agent1 = Agent(0, BOARD_SIZE, WINNING_SIZE, pivot_agent["scoring"], CIRCLE_OF_TWO, pivot_agent["name"])
            agent2 = Agent(1, BOARD_SIZE, WINNING_SIZE, agent["scoring"], CIRCLE_OF_TWO, agent["name"])
            
            run_tournament(agent1, agent2, TOTAL_GAMES)

if __name__ == "__main__":
    main()
