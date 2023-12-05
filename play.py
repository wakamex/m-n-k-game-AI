import json
import os

from src.Agent import Agent
from src.Game import Game

with open(os.path.join(os.path.dirname(__file__), "./src/config/config.json"), encoding="utf-8") as f:
    config = json.load(f)

agents = config["agents"]

while len(agents) > 1:
    #Each agent playes with each, after agent playes with every one we don't have to consider him for other matches.
    pivot_agent = agents.pop()
    print(pivot_agent)
    for agent in agents:
        print(pivot_agent["name"] + ' vs. ' + agent["name"])
        game = Game(
            config["board"][0], 
            config["board"][1], 
            config["winningSize"], 
            config["totalGames"],  
            Agent(1, [config["board"][0], config["board"][1]], config["winningSize"], pivot_agent["scoring"], pivot_agent["restrictMoves"]), 
            Agent(-1, [config["board"][0], config["board"][1]], config["winningSize"], agent["scoring"], agent["restrictMoves"]), 
            config["printMoves"])
        while game.totalGames > game.playedGames:
            game.playAgentMove()  #Play all games between two agents
        print(game.scores)
