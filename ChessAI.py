import random
import time
from multiprocessing import Queue

# Define piece scores
pieceScore = {"K": 0, "p": 1, "N": 3, "B": 3, "R": 5, "Q": 9}

# Define scores for different piece positions
knightScore = [[1, 1, 1, 1, 1, 1, 1, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScore = [[4, 3, 2, 1, 1, 2, 3, 4],
               [3, 4, 3, 2, 2, 3, 4, 3],
               [2, 3, 4, 3, 3, 4, 3, 2],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [2, 3, 4, 3, 3, 4, 3, 2],
               [3, 4, 3, 2, 2, 3, 4, 3],
               [4, 3, 2, 1, 1, 2, 3, 4]]

queenScore = [[1, 1, 1, 3, 1, 1, 1, 1],
              [1, 2, 3, 3, 3, 1, 1, 1],
              [1, 4, 3, 3, 3, 4, 2, 1],
              [1, 2, 3, 3, 3, 2, 2, 1],
              [1, 2, 3, 3, 3, 2, 2, 1],
              [1, 4, 3, 3, 3, 4, 2, 1],
              [1, 1, 2, 3, 3, 1, 1, 1],
              [1, 1, 1, 3, 1, 1, 1, 1]]

rookScore = [[4, 3, 4, 4, 4, 4, 3, 4],
             [4, 4, 4, 4, 4, 4, 4, 4],
             [1, 1, 2, 3, 3, 2, 1, 1],
             [1, 2, 3, 4, 4, 3, 2, 1],
             [1, 2, 3, 4, 4, 3, 2, 1],
             [1, 1, 2, 2, 2, 2, 1, 1],
             [4, 4, 4, 4, 4, 4, 4, 4],
             [4, 3, 4, 4, 4, 4, 3, 4]]

whitePawnScore = [[10, 10, 10, 10, 10, 10, 10, 10],
                  [8, 8, 8, 8, 8, 8, 8, 8],
                  [5, 6, 6, 7, 7, 6, 6, 5],
                  [2, 3, 3, 5, 5, 3, 3, 2],
                  [1, 2, 3, 4, 4, 3, 2, 1],
                  [1, 1, 2, 3, 3, 2, 1, 1],
                  [1, 1, 1, 0, 0, 1, 1, 1],
                  [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScore = [[0, 0, 0, 0, 0, 0, 0, 0],
                  [1, 1, 1, 0, 0, 1, 1, 1],
                  [1, 1, 2, 3, 3, 2, 1, 1],
                  [1, 2, 3, 4, 4, 3, 2, 1],
                  [2, 3, 3, 5, 5, 3, 3, 2],
                  [5, 6, 6, 7, 7, 6, 6, 5],
                  [8, 8, 8, 8, 8, 8, 8, 8],
                  [10, 10, 10, 10, 10, 10, 10, 10]]

# Dictionary to store piece positions scores
piecePositionScore = {"N": knightScore, "B": bishopScore, "Q": queenScore, "R": rookScore, "wp": whitePawnScore, "bp": blackPawnScore}

# Constants
CHECKMATE = 100
STALEMATE = 0
DEPTH = 2

def findBestMove(gs, validMoves, returnQueue):
    global nextMove, count
    nextMove = None
    count = 0
    start_time = time.time()

    # Shuffle the validMoves to add randomness
    random.shuffle(validMoves)

    # Sort the validMoves based on certain criteria
    validMoves = sortMoves(gs, validMoves)
    
    # Call the alpha-beta pruning function to find the best move
    findMove(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    
    # Print statistics
    print(f"{count} cycles")
    print(f"--- {time.time() - start_time} seconds ---")

    # If nextMove is still None, choose a random move
    if nextMove is None:
        print("Random Move")
        returnQueue.put(random.choice(validMoves))
    else:
        returnQueue.put(nextMove)

def findMove(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, count
    count += 1
    if depth == 0:
        return turnMultiplier * getScore(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move, calculate=True, ai=True)

        nextMoves = gs.getValidMoves()

        if depth > 1:
            nextMoves = sortMoves(gs, nextMoves)

        score = -findMove(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)

        if score > maxScore:
            maxScore = score

            if depth == DEPTH:
                nextMove = move
                print(move.__str__(gs))
                print(maxScore)

        gs.undoMove(capture=True)
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

def sortMoves(gs, validMoves):
    res = []
    captureIdx = 1
    castleIdx = 2
    promoteIdx = 3
    restIdx = 4
    for i in range(len(validMoves)):
        gs.makeMove(validMoves[i], calculate=True, ai=True)
        if gs.inCheck:
            res.insert(0, validMoves[i])
            captureIdx += 1
            castleIdx += 1
            promoteIdx += 1
            restIdx += 1
        elif validMoves[i].isCapture:
            res.insert(captureIdx, validMoves[i])
            castleIdx += 1
            promoteIdx += 1
            restIdx += 1
        elif validMoves[i].isCastleMove:
            res.insert(castleIdx, validMoves[i])
            promoteIdx += 1
            restIdx += 1
        elif validMoves[i].isPawnPromotion:
            res.insert(promoteIdx, validMoves[i])
            restIdx += 1
        elif validMoves[i].pieceMoved[1] == "p" and not validMoves[i].isPawnPromotion:
            res.append(validMoves[i])
        else:
            res.insert(restIdx, validMoves[i])
        gs.undoMove(capture=True)
    return res

def getScore(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return CHECKMATE
        else:
            return -CHECKMATE
    elif gs.staleMate or gs.insufficientMaterial or gs.threefoldRepition:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            sq = gs.board[row][col]
            if sq != "--":
                positionScore = 0
                if sq[1] != "K":
                    if sq[1] == "p":
                        positionScore = piecePositionScore[sq][row][col]
                    else:
                        positionScore = piecePositionScore[sq[1]][row][col]
                else:
                    if len(gs.castleRightsLog) >= 2:
                        curr = gs.castleRightsLog[-1]
                        prev = gs.castleRightsLog[-2]
                        if (curr.wks != prev.wks) or (curr.wqs != prev.wqs) or (curr.bks != prev.bks) or (curr.bqs != prev.bqs):
                            if (col == 2 or col == 6) and (gs.board[row][col - 1][1] == "R" or gs.board[row][col + 1][1] == "R"):
                                if sq[0] == "w":
                                    positionScore += 5
                                elif sq[0] == "b":
                                    positionScore -= 5
                if gs.board[row][col][0] == "w":
                    score += pieceScore[sq[1]] + positionScore * 0.05
                elif gs.board[row][col][0] == "b":
                    score -= pieceScore[sq[1]] + positionScore * 0.05
    return score
