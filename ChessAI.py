import random
import time
import sys
import json
from multiprocessing import Process, Queue

pieceScore = {"K": 0, "p": 1, "N": 3, "B": 3, "R": 5, "Q":9}
knightScore = [[1,1,1,1,1,1,1,1],[1,2,2,2,2,2,2,1],[1,2,3,3,3,3,2,1,],[1,2,3,4,4,3,2,1],[1,2,3,4,4,3,2,1],[1,2,3,3,3,3,2,1,],[1,2,2,2,2,2,2,1],[1,1,1,1,1,1,1,1]]
bishopScore = [[4,3,2,1,1,2,3,4],[3,4,3,2,2,3,4,3],[2,3,4,3,3,4,3,2],[1,2,3,4,4,3,2,1],[1,2,3,4,4,3,2,1],[2,3,4,3,3,4,3,2],[3,4,3,2,2,3,4,3],[4,3,2,1,1,2,3,4]]
queenScore = [[1,1,1,3,1,1,1,1],[1,2,3,3,3,1,1,1],[1,4,3,3,3,4,2,1],[1,2,3,3,3,2,2,1],[1,2,3,3,3,2,2,1],[1,4,3,3,3,4,2,1],[1,1,2,3,3,1,1,1],[1,1,1,3,1,1,1,1]]
rookScore = [[4,3,4,4,4,4,3,4],[4,4,4,4,4,4,4,4],[1,1,2,3,3,2,1,1],[1,2,3,4,4,3,2,1],[1,2,3,4,4,3,2,1],[1,1,2,2,2,2,1,1],[4,4,4,4,4,4,4,4],[4,3,4,4,4,4,3,4]]
whitePawnScore = [[10,10,10,10,10,10,10,10],[8,8,8,8,8,8,8,8],[5,6,6,7,7,6,6,5],[2,3,3,5,5,3,3,2],[1,2,3,4,4,3,2,1],[1,1,2,3,3,2,1,1],[1,1,1,0,0,1,1,1],[0,0,0,0,0,0,0,0]]
blackPawnScore = [[0,0,0,0,0,0,0,0],[1,1,1,0,0,1,1,1],[1,1,2,3,3,2,1,1],[1,2,3,4,4,3,2,1],[2,3,3,5,5,3,3,2],[5,6,6,7,7,6,6,5],[8,8,8,8,8,8,8,8],[10,10,10,10,10,10,10,10]]
piecePositionScore = {"N": knightScore, "B": bishopScore, "Q": queenScore, "R": rookScore, "wp":whitePawnScore, "bp": blackPawnScore}
CHECKMATE = 100
STALEMATE = 0
DEPTH = 1

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

def findBestMoveAlphaBeta(gs, validMoves, returnQueue):
    global nextMove, count, scoreBoard
    nextMove = None
    count = 0
    random.shuffle(validMoves)
    start_time = time.time()
    validMoves = sortMoves(gs, validMoves)
    with open('scoreLog.json', 'r') as convert_file:
        scoreBoard = json.load(convert_file)
    findMoveAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(len(scoreBoard))
    print(str(count) + " cycles")
    print("--- %s seconds ---" % (time.time() - start_time))
    if nextMove == None:
        return validMoves[random.randint(0, len(validMoves) - 1)]
    with open('scoreLog.json', 'w') as convert_file:
        convert_file.write(json.dumps(scoreBoard))
    returnQueue.put(nextMove)
    
def findMoveAlphaBeta(gs, validMoves, depth, alpha, beta, turnMulitplier):
    global nextMove, count, scoreBoard
    count += 1
    if depth == 0:
        return turnMulitplier * getScore(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move, calculate=True, ai=True)
        boardString = ''.join(str(item) for innerlist in gs.board for item in innerlist)
        if boardString in scoreBoard and scoreBoard[boardString][1] > depth:
                score = scoreBoard[boardString][0]
        else:
            nextMoves = gs.getValidMoves()
            if depth > 1:
                nextMoves = sortMoves(gs, nextMoves)
            score = -findMoveAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMulitplier)
            scoreBoard[boardString] = [score, depth]
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                print(nextMove.__str__(gs))
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
                    score += pieceScore[sq[1]] + positionScore * 0.1
                elif gs.board[row][col][0] == "b":
                    score -= pieceScore[sq[1]] + positionScore * 0.1
    return score
