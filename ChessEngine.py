"""
Controls user inpput and displays state of the game
"""

class GameState():
    def __init__(self):
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        ["bp" for i in range(8)], ["--" for i in range(8)], 
        ["--" for i in range(8)], ["--" for i in range(8)], ["--" for i in range(8)], 
        ["wp" for i in range(8)], ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.whiteToMove = True
        self.moveLog = []

