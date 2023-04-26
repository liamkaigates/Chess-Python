"""
Stores information about the state of the game. Determines valid moves at each turn. 
Keeps track of moves throughout the game.
"""

import pygame as p
import sys
from multiprocessing import Process, Queue
import ChessEngine
import ChessAI
import json
import time

WIDTH = HEIGHT = 512
MOVE_LOG_WIDTH = 256
MOVE_LOG_HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bN", "bB", "bR", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("image/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def flipImages():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bN", "bB", "bR", "bQ", "bK"]
    for i in range(len(pieces)):
        piece = pieces[i]
        if piece[0] == "w":
            piece = "b" + pieces[i][1]
        else:
            piece = "w" + pieces[i][1]
        IMAGES[piece] = p.transform.scale(p.image.load("image/" + pieces[i] + ".png"), (SQ_SIZE, SQ_SIZE))

def reverseBoard(board):
    board[0][3], board[0][4] = board[0][4], board[0][3]
    board[7][3], board[7][4] = board[7][4], board[7][3]
    return board

def drawText(screen, text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

class Button():
    def __init__(self, x, y, width, height, buttonText, isHuman, onePress=False, quitting=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onePress = onePress
        self.alreadyPressed = False
        self.isHuman = isHuman
        self.fillColors = {
            'normal': '#ffffff',
            'hover': '#666666',
            'pressed': '#333333',
        }
        font = p.font.SysFont("Helvitca", 40, False, False)
        self.buttonSurface = p.Surface((self.width, self.height))
        self.buttonRect = p.Rect(self.x, self.y, self.width, self.height)
        self.buttonSurf = font.render(buttonText, True, (20, 20, 20))

    def process(self, screen):
        mousePos = p.mouse.get_pos()
        playerTwo = False
        run = True
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if p.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.onePress and quitting:
                    run = False
                    running = False
                elif self.onePress:
                    playerTwo = self.isHuman
                    run = False
                elif not self.alreadyPressed:
                    playerTwo = self.isHuman
                    run = False
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False
        self.buttonSurface.blit(self.buttonSurf, [
        self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
        self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)
        return run, playerTwo
    
    def quitProcess(self, screen):
        mousePos = p.mouse.get_pos()
        running = True
        run = True
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if p.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.onePress:
                    running = False
                    run = False
                elif not self.alreadyPressed:
                    running = False
                    run = False
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False
        self.buttonSurface.blit(self.buttonSurf, [
        self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
        self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)
        return run, running
    
    def chooseColor(self, screen):
        mousePos = p.mouse.get_pos()
        color = False
        run = True
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if p.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.onePress:
                    color = True
                    run = False
                elif not self.alreadyPressed:
                    color = True
                    run = False
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False
        self.buttonSurface.blit(self.buttonSurf, [
        self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
        self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)
        return run, color


def main():
    p.init()
    playerOne = True # True == Human / False (0 - 2 for level) == Computer
    playerTwo = False
    playerOne = True # True == Human / False (0 - 2 for level) == Computer
    playerTwo = False
    screen = p.display.set_mode((WIDTH + MOVE_LOG_WIDTH, HEIGHT))
    p.display.set_caption("Main Menu")
    run = True
    running = True
    font = p.font.SysFont("Helvitca", 40, False, False)
    human = Button(2 * SQ_SIZE, 3 * SQ_SIZE, SQ_SIZE * 2, SQ_SIZE * 2, "Human", True)
    ai = Button(8 * SQ_SIZE, 3 * SQ_SIZE, SQ_SIZE * 2, SQ_SIZE * 2, "AI", False)
    quitButton = Button(5 * SQ_SIZE, 6 * SQ_SIZE, SQ_SIZE * 2, SQ_SIZE * 2, "Quit", False)
    while run:
        screen.fill((139,136,120))
        drawText(screen, "Welcome to Chess!", font, (255,255,255), SQ_SIZE * 4, SQ_SIZE)
        drawText(screen, "Select your opponent!", font, (255,255,255), SQ_SIZE * 4 - SQ_SIZE // 2, 3 * SQ_SIZE // 2)
        run, running = quitButton.quitProcess(screen)
        if run and running:
            run, playerTwo = human.process(screen)
            if playerTwo == False and run == True:
                run, playerTwo = ai.process(screen)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                run = False
        p.display.update()
    run = True
    white = Button(2 * SQ_SIZE, 3 * SQ_SIZE, SQ_SIZE * 2, SQ_SIZE * 2, "White", False)
    black = Button(8 * SQ_SIZE, 3 * SQ_SIZE, SQ_SIZE * 2, SQ_SIZE * 2, "Black", False)
    whiteBool = False
    blackBool = False
    time.sleep(0.25)
    p.event.clear()
    while run:
        screen.fill((139,136,120))
        drawText(screen, "Welcome to Chess!", font, (255,255,255), SQ_SIZE * 4, SQ_SIZE)
        drawText(screen, "Select your color!", font, (255,255,255), SQ_SIZE * 4, 3 * SQ_SIZE // 2)
        run, running = quitButton.quitProcess(screen)
        if run and running:
            run, whiteBool = white.chooseColor(screen)
            if whiteBool == False and run == True:
                run, blackBool = black.chooseColor(screen)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                run = False
        p.display.update()
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    if blackBool and not whiteBool:
        gs.blackBool = True
        gs.whiteToMove = not gs.whiteToMove
        gs.board = reverseBoard(gs.board)
    else:
        gs.whiteBool  = True
    validMoves = gs.getValidMoves()
    moveLogFont = p.font.SysFont("Helvitca", 20, False, False)
    moveMade = False
    animate = False
    if blackBool and not whiteBool:
        flipImages()
    else:
        loadImages()
    start_time = 0
    sqSelected = ()
    playerClicks = []
    gameOver = False
    resetSkip = False
    AIthinking = False
    moveFinderProcess = None
    moveUndone = False
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 and humanTurn:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                undoMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
                    elif len(playerClicks) > 2:
                        playerClicks = []
                        sqSelected = ()
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    if not gameOver:
                        gs.undoMove()
                        moveMade = False
                        animate = False
                        resetSkip = True
                        sqSelected = ()
                        playerClicks = []
                        validMoves = gs.getValidMoves()
                        if AIthinking:
                            moveFinderProcess.terminate()
                            AIthinking = False
                        moveUndone = True
                if e.key == p.K_r and gameOver:
                    gs = ChessEngine.GameState()
                    if blackBool and not whiteBool:
                        gs.whiteToMove = not gs.whiteToMove
                        gs.board = reverseBoard(gs.board)
                    if blackBool and not whiteBool:
                        flipImages()
                    else:
                        loadImages()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    resetSkip = True
                    gs.whiteToMove = True
                    if AIthinking:
                        moveFinderProcess.terminate()
                        AIthinking = False
                        moveUndone = False
        if not gameOver and not humanTurn and not resetSkip and not moveUndone:
            if not AIthinking:
                AIthinking = True
                print("thinking...")
                returnQueue = Queue()
                moveFinderProcess = Process(target=ChessAI.findBestMoveAlphaBeta, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start()
                start_time = time.time()
            if not moveFinderProcess.is_alive():
                print("done thinking...")
                res = returnQueue.get()
                gs.makeMove(res,ai=True)
                moveMade = True
                animate = True
                AIthinking = False
                start_time = 0
            if start_time != 0:
                if time.time() - start_time >= 120:
                    if AIthinking:
                        moveFinderProcess.terminate()
                        AIthinking = False
                    
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False
        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)
        if gs.checkMate:
            gameOver = True
            text = "Black wins by checkmate!" if gs.whiteToMove else "White wins by checkmate!"
            drawEndGameText(screen, text)
        elif gs.staleMate:
            gameOver = True
            text = "Draw by stalemate!"
            drawEndGameText(screen, text)
        elif gs.insufficientMaterial:
            gameOver = True
            text = "Draw by insufficient matierial!"
            drawEndGameText(screen, text)
        elif gs.threefoldRepition:
            gameOver = True
            text = "Draw by threefold repetition!"
            drawEndGameText(screen, text)
        elif gs.fiftyMoveDraw:
            gameOver = True
            text = "Draw by fifty move rule!"
            drawEndGameText(screen, text)
        resetSkip = False
        clock.tick(MAX_FPS)
        p.display.flip()

def highlightStartSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("yellow"))
            screen.blit(s, (SQ_SIZE*c, SQ_SIZE*r))

def highlightEndSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
            circle = p.Surface((SQ_SIZE, SQ_SIZE))
            circle.set_alpha(100)
            p.draw.circle(circle, (193,205,205), (SQ_SIZE//2, SQ_SIZE//2), 10)
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(circle, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))

def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)
    highlightStartSquares(screen, gs, validMoves, sqSelected)
    drawPiece(screen, gs.board)
    highlightEndSquares(screen, gs, validMoves, sqSelected)
    drawMoveLog(screen, gs, moveLogFont)


def drawBoard(screen):
    colors = [p.Color(255,248,220), p.Color(110,139,61)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPiece(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawMoveLog(screen, gs, moveLogFont):
    moveLogRect = p.Rect(WIDTH, 0, MOVE_LOG_WIDTH, MOVE_LOG_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + moveLog[i].__str__(gs) + " "
        if i + 1 < len(moveLog):
            moveString += moveLog[i+1].__str__(gs) + " "
        moveTexts.append(moveString)
    movesPerRow = 3
    x = 5
    y = 5
    space = 2
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObj = moveLogFont.render(text, True, p.Color("white"))
        textLocation = moveLogRect.move(x, y)
        screen.blit(textObj, textLocation)
        y += textObj.get_height() + space

def animateMove(move, screen, board, clock):
    colors = [p.Color(255,248,220), p.Color(110,139,61)]
    coords = []
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame/frameCount, move.startCol + dC * frame/frameCount)
        drawBoard(screen)
        drawPiece(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(SQ_SIZE * move.endCol, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceMoved[0] == "w" else (move.endRow - 1)
                endSquare = p.Rect(SQ_SIZE * move.endCol, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObj = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0,0,WIDTH, HEIGHT).move(WIDTH/2 - textObj.get_width()/2, HEIGHT/2 - textObj.get_height()/2)
    screen.blit(textObj, textLocation)
    textObj = font.render(text, 0, p.Color("Gray"))
    screen.blit(textObj, textLocation.move(2,2))

if __name__ == "__main__":
    main()