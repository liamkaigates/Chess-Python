import random

pieceScore = {"K": 0, "p": 1, "N": 3, "B": 3, "R": 5, "Q":9}
CHECKMATE = 100
STALEMATE = 0
DEPTH = 2

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
        if gs.checkMate:
            opponentMaxScore = -CHECKMATE
        elif gs.staleMate or gs.insufficientMaterial or gs.threefoldRepition:
            opponentMaxScore = STALEMATE
        else:
            opponentMaxScore = -CHECKMATE
            for oppMove in opponentsMoves:
                gs.makeMove(oppMove, calculate=True)
                gs.getValidMoves()
                if gs.checkMate:
                    score = -CHECKMATE
                elif gs.staleMate or gs.insufficientMaterial or gs.threefoldRepition:
                    score = STALEMATE
                else:
                    score = -turnMulitplier * getScore(gs)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undoMove()
        if opponentMaxScore < oppMinMaxScore:
            oppMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove

def findBestMoveMinMax(gs, validMoves):
    global nextMove
    nextMove = None
    findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    return nextMove


def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return getScore(gs)
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move, calculate=True)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move, calculate=True)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True) 
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore

def findBestMoveNegaMax(gs, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    if nextMove == None:
        gs.checkMate = True
    return nextMove


def findMoveNegaMax(gs, validMoves, depth, turnMulitplier):
    global nextMove
    if depth == 0:
        return turnMulitplier * getScore(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move, calculate=True)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth - 1, -turnMulitplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore

def findBestMoveAlphaBeta(gs, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    findMoveAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    return nextMove

def findMoveAlphaBeta(gs, validMoves, depth, alpha, beta, turnMulitplier):
    global nextMove
    if depth == 0:
        return turnMulitplier * getScore(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move, calculate=True, ai=True)
        nextMoves = gs.getValidMoves()
        score = -findMoveAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMulitplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove(capture=True)
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


def getScore(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return CHECKMATE
        else:
            return -CHECKMATE
    elif gs.staleMate or gs.insufficientMaterial or gs.threefoldRepition:
        return STALEMATE
    score = 0
    for row in gs.board:
        for sq in row:
            if sq[0] == "w":
                score += pieceScore[sq[1]]
            elif sq[0] == "b":
                score -= pieceScore[sq[1]]
    return score
