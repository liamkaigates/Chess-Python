# Chess AI with Minimax and Alpha-Beta Pruning

This project is a chess-playing AI implemented in Python, using the Minimax algorithm with Alpha-Beta pruning. The AI evaluates different moves on a chessboard and chooses the one that maximizes its chances of winning or minimizes the opponent's chances.

## Features

- Chessboard representation: The chessboard is represented using a 2D array, with pieces denoted by their initials (e.g., "K" for king, "p" for pawn).
- Piece scoring: Each piece is assigned a score, and the AI calculates the score for different moves to make strategic decisions.
- Minimax algorithm: The core algorithm for decision-making is the Minimax algorithm, which explores possible moves up to a certain depth to find the best move.
- Alpha-Beta pruning: To optimize the Minimax algorithm, Alpha-Beta pruning is implemented, reducing the number of nodes explored, thus improving performance.

## AI Strategies

- Piece scoring: The AI evaluates the position of each piece on the board based on predefined scores.
- Depth-limited search: The AI explores possible moves up to a certain depth, preventing an exhaustive search and balancing computational resources.
- Alpha-Beta pruning: The pruning technique further enhances the efficiency of the Minimax algorithm.

## Usage

1. Ensure you have Python installed on your machine.
2. Run the script using a Python interpreter:

   ```
   python chessMain.py
   ```

3. The AI will play against itself, demonstrating its decision-making capabilities.

## Customization

- You can adjust the `DEPTH` variable in the script to control the depth of the search performed by the AI.
- Modify the piece scores and board evaluation parameters in the script to experiment with different strategies.

## Credits

This project is inspired by chess AI concepts, Minimax algorithm, and Alpha-Beta pruning. The initial codebase is provided as a starting point for further exploration and customization.

Feel free to contribute, modify, or enhance the project as you see fit!
