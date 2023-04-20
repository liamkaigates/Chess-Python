"""
Controls user inpput and displays state of the game
"""
import pygame as p
import copy

class GameState():
    def __init__(self):
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        ["bp" for i in range(8)], ["--" for i in range(8)], 
        ["--" for i in range(8)], ["--" for i in range(8)], ["--" for i in range(8)], 
        ["wp" for i in range(8)], ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.pieces = ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR", "bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp", "wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp", "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        self.whiteToMove = True
        self.moveLog = []
        self.moveFunctions = {"p": self.getPawnMoves, "R":self.getRookMoves, "N": self.getKnightMoves,
                                "B": self.getBishopMoves, "Q":self.getQueenMoves, "K":self.getKingMoves}
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation= (0,4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.boardLog = [copy.deepcopy(self.board)]
        self.checkMate = False
        self.staleMate = False
        self.insufficientMaterial = False
        self.threefoldRepition = False
        self.fiftyMoveDraw = False
        self.noCaptureCount = 0
        self.prevCount = []
        self.enpassantPossible = ()
        self.enpassantLog = [self.enpassantPossible]
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    def makeMove(self, move, calculate=False, ai=False):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        if move.isPawnPromotion:
            if ai:
                idx = "q"
            else:
                 idx = wait()
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + move.promotionChoice[idx]
            move.promotedPiece = self.board[move.endRow][move.endCol]
            self.pieces.remove(move.pieceMoved)
            self.pieces.append(move.pieceMoved[0] + move.promotionChoice[idx])
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow+move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"

        
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))
        self.currentCastlingRights = self.castleRightsLog[-1]
        self.updateCastleRights(move)
        self.enpassantLog.append(self.enpassantPossible)
        if move.pieceCaptured in self.pieces and not calculate:
            self.pieces.remove(move.pieceCaptured)
            self.prevCount.append(self.noCaptureCount)
            self.noCaptureCount = 0
        elif not calculate:
            self.noCaptureCount += 1
            if self.noCaptureCount >= 50:
                self.fiftyMoveDraw = True
        self.boardLog.append(copy.deepcopy(self.board))
        if len(self.boardLog) >= 8 and not calculate:
            if self.boardLog.count(self.boardLog[-1]) == 3 and self.boardLog.count(self.boardLog[-2]) == 3:
                self.threefoldRepition = True

    def undoMove(self, capture=False):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            if move.isPawnPromotion:
                self.pieces.pop()
                self.pieces.append(move.pieceMoved)
                move.promotedPiece = None
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"
            self.castleRightsLog.pop()
            self.currentCastlingRights = self.castleRightsLog[-1]
            self.enpassantLog.pop()
            self.enpassantPossible = self.enpassantLog[-1]
            if move.pieceCaptured != "--" and not capture:
                self.pieces.append(move.pieceCaptured)
                self.noCaptureCount = self.prevCount[-1]
            else:
                self.noCaptureCount -= 1
            self.boardLog.pop()
            self.checkMate = False
            self.staleMate = False
            

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False
        
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        kingRow = self.whiteKingLocation[0] if self.whiteToMove else self.blackKingLocation[0]
        kingCol = self.whiteKingLocation[1] if self.whiteToMove else self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()
        self.getCastleMoves(kingRow, kingCol, moves)
        if len(moves) == 0 and self.inCheck:
            self.checkMate = True
        elif len(moves) == 0 and not self.inCheck:
            self.staleMate = True
        elif self.getInsufficientMaterial():
            self.insufficientMaterial = True
        return moves

    def getInsufficientMaterial(self):
        if len(self.pieces) == 4 and "wK" in self.pieces and "bK" in self.pieces and "wB" in self.pieces and "bB" in self.pieces:
            for row in range(8):
                for col in range(8):
                    if self.board[row][col] == "wB":
                        whiteNum = (row + col) % 2
                    elif self.board[row][col] == "bB":
                        blackNum = (row + col) % 2
            return whiteNum == blackNum

        if len(self.pieces) == 3 and "wK" in self.pieces and "bK" in self.pieces and ("wB" in self.pieces or "bB" in self.pieces):
            return True
        elif len(self.pieces) == 3 and "wK" in self.pieces and "bK" in self.pieces and ("wN" in self.pieces or "bN" in self.pieces):
            return True
        elif len(self.pieces) == 2 and "wK" in self.pieces and "bK" in self.pieces:
            return True

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves
    
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        enemyColor = "b" if self.whiteToMove else "w"
        allyColor = "w" if self.whiteToMove else "b"
        startRow = self.whiteKingLocation[0] if self.whiteToMove else self.blackKingLocation[0]
        startCol = self.whiteKingLocation[1] if self.whiteToMove else self.blackKingLocation[1]
        direction = ((-1,0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(direction)):
            d = direction[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        pieceType = endPiece[1]
                        if (0 <= j <= 3 and pieceType == "R") or (4 <= j <= 7 and pieceType == "B") or \
                        (i == 1 and pieceType == "p" and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or \
                        (pieceType == "Q") or (i == 1 and pieceType == "K"):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break
        knightMoves = ((2,1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, -1), (-2, 1))
        for m in knightMoves:
            endRow= startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:
            if self.board[r-1][c] == "--":
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r,c), (r-1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":
                        moves.append(Move((r,c), (r-2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == "b":
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r,c), (r-1, c - 1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    attackingPiece = False
                    blockingPiece = False
                    if self.whiteKingLocation[0] == r:
                        if self.whiteKingLocation[1] < c:
                            insideRange = range(self.blackKingLocation[1] + 1, c - 1)
                            outsideRange = range(c + 1, 8)
                        else:
                            insideRange = range(self.blackKingLocation[1] - 1, c, -1)
                            outsideRange = range(c + 2, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            if self.board[r][i][0] == "b" and (self.board[r][i][1] == "R" or self.board[r][i][1] == "Q"):
                                attackingPiece = True
                            elif self.board[r][i][0] == "w":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r-1,c-1), self.board, isEnpassantMove=True))

            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == "b":
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r,c), (r-1, c + 1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    attackingPiece = False
                    blockingPiece = False
                    if self.whiteKingLocation[0] == r:
                        if self.whiteKingLocation[1] < c:
                            insideRange = range(self.blackKingLocation[1] + 1, c)
                            outsideRange = range(c + 2, 8)
                        else:
                            insideRange = range(self.blackKingLocation[1] - 1, c + 1, -1)
                            outsideRange = range(c - 1, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            if self.board[r][i][0] == "b" and (self.board[r][i][1] == "R" or self.board[r][i][1] == "Q"):
                                attackingPiece = True
                            elif self.board[r][i][0] == "w":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r-1,c+1), self.board, isEnpassantMove=True))
        else:
            if self.board[r+1][c] == "--":
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r,c), (r+1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r,c), (r+2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w":
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r,c), (r+1, c - 1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    attackingPiece = False
                    blockingPiece = False
                    if self.blackKingLocation[0] == r:
                        if self.blackKingLocation[1] < c:
                            insideRange = range(self.blackKingLocation[1] + 1, c - 1)
                            outsideRange = range(c + 1, 8)
                        else:
                            insideRange = range(self.blackKingLocation[1] - 1, c, -1)
                            outsideRange = range(c + 2, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            if self.board[r][i][0] == "w" and (self.board[r][i][1] == "R" or self.board[r][i][1] == "Q"):
                                attackingPiece = True
                            elif self.board[r][i][0] == "b":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r+1,c-1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == "w":
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r,c), (r+1, c + 1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    attackingPiece = False
                    blockingPiece = False
                    if self.blackKingLocation[0] == r:
                        if self.blackKingLocation[1] < c:
                            insideRange = range(self.blackKingLocation[1] + 1, c)
                            outsideRange = range(c + 2, 8)
                        else:
                            insideRange = range(self.blackKingLocation[1] - 1, c + 1, -1)
                            outsideRange = range(c - 1, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            if self.board[r][i][0] == "w" and (self.board[r][i][1] == "R" or self.board[r][i][1] == "Q"):
                                attackingPiece = True
                            elif self.board[r][i][0] == "b":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r+1,c-1), self.board, isEnpassantMove=True))


    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break
        direction = ((-1,0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in direction:
            for i in range(1, 8):
                endRow= r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: 
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break
    
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((2,1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, -1), (-2, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for m in knightMoves:
            endRow= r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--" or endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3]) 
                self.pins.remove(self.pins[i])
                break
        direction = ((-1,1), (1, -1), (-1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in direction:
            for i in range(1, 8):
                endRow= r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                    else:
                        break
    
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)
    
    def getKingMoves(self, r, c, moves):
        kingMoves = ((1,1), (1, -1), (1, 0), (0, 1), (0, -1), (-1, 0), (-1, -1), (-1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for m in kingMoves:
            endRow= r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor or endPiece == "--":
                    if enemyColor == "b":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                    if enemyColor == "b":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c) 
    
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(r, c, moves)
    
    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r,c), (r,c+2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r,c), (r,c-2), self.board, isCastleMove=True))
            

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    rankToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rowsToRank = {v: k for k, v in rankToRows.items()}
    filesToCol = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v: k for k, v in filesToCol.items()}
    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isEnpassantMove = isEnpassantMove
        self.promotionChoice = {"n": "N", "b": "B", "r":"R", "q":"Q"}
        self.promotedPiece = None
        self.isPawnPromotion = ((self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7))
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != "--"
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRank[r]
    
    def __str__(self, gs):
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"
        endSquare = self.getRankFile(self.endRow, self.endCol)
        if self.pieceMoved[1] == "p":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            elif self.isPawnPromotion and self.promotedPiece != None:
                return endSquare + "=" + self.promotedPiece[1]
            else:
                return endSquare
        else:
            moveString = self.pieceMoved[1]
            extra = ""
            if self.isCapture:
                extra = "x"
            elif gs.checkMate:
                extra = "#"
            elif gs.inCheck and len(gs.checks) >= 1:
                extra = "+"
                if len(gs.checks) == 2:
                    extra += "+"
            elif gs.staleMate or gs.insufficientMaterial or gs.threefoldRepition or gs.fiftyMoveDraw:
                return moveString + endSquare + " ="
            return moveString + endSquare  


def wait():
    while True:
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
            if event.type == p.KEYDOWN:
                if event.key == p.K_r:
                    return "r"
                elif event.key == p.K_b:
                    return "b"
                elif event.key == p.K_q:
                    return "q"
                elif event.key == p.K_n:
                    return "n"