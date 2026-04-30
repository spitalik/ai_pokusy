import pygame
import random
import sys
import os

pygame.init()

BLOCK = 30
COLS = 10
ROWS = 20
WIDTH = BLOCK * COLS
HEIGHT = BLOCK * ROWS
FPS = 60

WIN = pygame.display.set_mode((WIDTH + 200, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Tetris - Python')

SHAPES = [
    [[1, 1, 1, 1]],
    [[2, 2], [2, 2]],
    [[0,3,0],[3,3,3]],
    [[4,0,0],[4,4,4]],
    [[0,0,5],[5,5,5]],
    [[0,6,6],[6,6,0]],
    [[7,7,0],[0,7,7]],
]

COLORS = [ (0,0,0), (0,255,255), (255,255,0), (128,0,128), (255,165,0), (0,0,255), (0,255,0), (255,0,0) ]

# High-score persistence
HIGHSCORE_FILE = 'highscore.txt'

def load_highscore():
    try:
        if not os.path.exists(HIGHSCORE_FILE):
            return 0
        with open(HIGHSCORE_FILE, 'r', encoding='utf-8') as f:
            return int(f.read().strip() or 0)
    except Exception:
        return 0

def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, 'w', encoding='utf-8') as f:
            f.write(str(int(score)))
    except Exception:
        pass

def create_grid(locked_positions={}):
    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLS):
            if (x,y) in locked_positions:
                grid[y][x] = locked_positions[(x,y)]
    return grid

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape[0][0] if shape and shape[0] else 1
        self.rotation = 0

def convert_shape_format(piece):
    """Return list of (x, y, val) for non-empty cells of the piece."""
    positions = []
    shape = piece.shape
    for i, row in enumerate(shape):
        for j, val in enumerate(row):
            if val:
                positions.append((piece.x + j, piece.y + i, val))
    return positions

def valid_space(piece, grid):
    accepted = {(x, y) for y in range(ROWS) for x in range(COLS) if grid[y][x] == 0}
    formatted = convert_shape_format(piece)
    for pos in formatted:
        x, y, _ = pos
        if (x, y) not in accepted:
            if y > -1:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    shape_template = random.choice(SHAPES)
    return Piece(COLS//2 - len(shape_template[0])//2, 0, shape_template)

def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if 0 not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc

def draw_grid(surface, grid):
    sx = 0
    sy = 0
    for i in range(ROWS):
        for j in range(COLS):
            pygame.draw.rect(surface, COLORS[grid[i][j]], (sx + j*BLOCK, sy + i*BLOCK, BLOCK, BLOCK), 0)
            pygame.draw.rect(surface, (50,50,50), (sx + j*BLOCK, sy + i*BLOCK, BLOCK, BLOCK), 1)

def draw_window(surface, grid, score=0, level=1, highscore=0):
    surface.fill((0,0,0))
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('KARITRIS', 1, (255,255,255))
    surface.blit(label, (WIDTH + 20, 20))

    high_label = font.render(f'High: {highscore}', 1, (255,255,255))
    surface.blit(high_label, (WIDTH + 20, 60))

    score_label = font.render(f'Score: {score}', 1, (255,255,255))
    surface.blit(score_label, (WIDTH + 20, 100))

    level_label = font.render(f'Level: {level}', 1, (255,255,255))
    surface.blit(level_label, (WIDTH + 20, 140))

    draw_grid(surface, grid)

def main():
    # load persisted high-score once per program run
    highscore = load_highscore()
    while True:
        win = WIN
        locked_positions = {}
        grid = create_grid(locked_positions)

        change_piece = False
        run = True
        current_piece = get_shape()
        next_pieces = [get_shape(), get_shape()]
        clock = pygame.time.Clock()
        fall_time = 0
        fall_speed = 0.5
        level = 1
        score = 0

        while run:
            grid = create_grid(locked_positions)
            fall_time += clock.get_rawtime()
            clock.tick(FPS)

            if fall_time/1000 >= fall_speed:
                fall_time = 0
                current_piece.y += 1
                if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                    current_piece.y -= 1
                    change_piece = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.VIDEORESIZE:
                    win = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1
                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1
                    elif event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid):
                            current_piece.y -= 1
                    elif event.key == pygame.K_UP:
                        current_piece.shape = [list(row) for row in zip(*current_piece.shape[::-1])]
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1
                            if not valid_space(current_piece, grid):
                                current_piece.x += 2
                                if not valid_space(current_piece, grid):
                                    current_piece.x -= 1
                                    current_piece.shape = [list(row) for row in zip(*current_piece.shape)[::-1]]
                    elif event.key == pygame.K_SPACE:
                        while valid_space(current_piece, grid):
                            current_piece.y += 1
                        current_piece.y -= 1
                        change_piece = True
                    elif event.key == pygame.K_p:
                        paused = True
                        while paused:
                            for e in pygame.event.get():
                                if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                                    paused = False
                                if e.type == pygame.QUIT:
                                    pygame.quit(); sys.exit()

            shape_pos = convert_shape_format(current_piece)

            for i in range(len(shape_pos)):
                x, y, val = shape_pos[i]
                if y > -1:
                    grid[y][x] = val

            if change_piece:
                for pos in shape_pos:
                    x, y, val = pos
                    p = (x, y)
                    locked_positions[p] = val
                # advance the queue: take first upcoming piece as current and append a new random piece
                current_piece = next_pieces.pop(0)
                next_pieces.append(get_shape())
                change_piece = False
                cleared = clear_rows(grid, locked_positions)
                if cleared > 0:
                    score += (cleared ** 2) * 100
                    level = 1 + score // 1000
                    fall_speed = max(0.05, 0.5 - (level-1)*0.03)

            draw_window(win, grid, score, level, highscore)
            nx = WIDTH + 30
            ny = 220
            font = pygame.font.SysFont('comicsans', 24)
            lbl = font.render('Next', 1, (255,255,255))
            win.blit(lbl, (nx, ny-40))
            # draw two upcoming pieces stacked vertically
            for idx, npiece in enumerate(next_pieces):
                offset_y = ny + idx * (BLOCK * 4 + 20)
                for i, row in enumerate(npiece.shape):
                    for j, val in enumerate(row):
                        if val:
                            pygame.draw.rect(win, COLORS[val], (nx + j*BLOCK, offset_y + i*BLOCK, BLOCK, BLOCK))
                            pygame.draw.rect(win, (50,50,50), (nx + j*BLOCK, offset_y + i*BLOCK, BLOCK, BLOCK), 1)

            pygame.display.update()

            if check_lost(list(locked_positions.keys())):
                run = False

        # Game over - persist high-score and show menu to restart or quit
        if score > highscore:
            save_highscore(score)
            highscore = score
        pygame.time.delay(500)
        menu = True
        restart = False
        while menu:
            draw_window(win, grid, score, level, highscore)
            font = pygame.font.SysFont('comicsans', 40)
            game_over_label = font.render('Game Over', 1, (255,0,0))
            win.blit(game_over_label, (WIDTH//2 - game_over_label.get_width()//2, HEIGHT//2 - 50))
            small_font = pygame.font.SysFont('comicsans', 24)
            msg = small_font.render('Press R to Restart or Q to Quit', 1, (255,255,255))
            win.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 + 10))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.VIDEORESIZE:
                    win = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        restart = True
                        menu = False
                    elif event.key == pygame.K_q:
                        pygame.quit(); sys.exit()

        if restart:
            continue
        else:
            break

    pygame.quit()

if __name__ == '__main__':
    main()
