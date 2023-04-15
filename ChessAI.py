import random

pieceScore = {"K": 0, "p": 1, "N": 3, "B": 3, "R": 5, "Q":9}
CHECKMATE = 100
STALEMATE = 0

def findRandomMove(validMoves):
    if len(validMoves) >= 1:
        return validMoves[random.randint(0, len(validMoves) - 1)]

def findCaptureMove(validMoves):
    moves = []
    for move in validMoves:
        if move.pieceCaptured != "--":
            moves.append(move)
    if len(moves) >= 1:
        return moves[random.randint(0, len(moves) - 1)]
    elif len(validMoves) >= 1:
        return validMoves[random.randint(0, len(validMoves) - 1)]

def findBestMove(gs, validMoves):
    turnMulitplier = 1 if gs.whiteToMove else -1
    oppMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove, calculate=True)
        opponentsMoves = gs.getValidMoves()
        opponentMaxScore = -CHECKMATE
        for oppMove in opponentsMoves:
            gs.makeMove(oppMove, calculate=True)
            if gs.checkMate:
                score = CHECKMATE * -turnMulitplier
            elif gs.staleMate or gs.insufficientMaterial or gs.threefoldRepition:
                score = STALEMATE
            else:
                score = -turnMulitplier * getScore(gs.board)
            if score > opponentMaxScore:
                opponentMaxScore = score
            gs.undoMove()
        if opponentMaxScore < oppMinMaxScore:
            oppMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove

def getScore(board):
    score = 0
    for row in board:
        for sq in row:
            if sq[0] == "w":
                score += pieceScore[sq[1]]
            elif sq[0] == "b":
                score -= pieceScore[sq[1]]
    return score
