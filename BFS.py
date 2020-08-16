import pygame as pg
from collections import deque
import os
import sys
from settings import *
vec = pg.math.Vector2

pg.init()
window = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
clock2 = pg.time.Clock()
firsttime = True
# load images
folder = os.path.dirname(__file__)
home_img = pg.image.load(os.path.join(folder, 'home.png')).convert_alpha()
home_img = pg.transform.scale(home_img, (TILESIZE, TILESIZE))
target_img = pg.image.load(os.path.join(folder, 'target.png')).convert_alpha()
target_img = pg.transform.scale(target_img, (TILESIZE, TILESIZE))


class SquareGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []
        self.connections = [vec(1, 0), vec(-1, 0), vec(0, 1), vec(0, -1)]
        # self.connections += [vec(1, 1), vec(-1, 1), vec(1, -1), vec(-1, -1)]

    def in_bounds(self, node):
        return 0 <= node.x < self.width and 0 <= node.y < self.height

    def passable(self, node):
        return node not in self.walls

    def find_neighbors(self, node):
        neighbors = [node + connection for connection in self.connections]
        if (node.x + node.y) % 2 == 0:
            neighbors.reverse()
        neighbors = filter(self.in_bounds, neighbors)
        neighbors = filter(self.passable, neighbors)
        # print(list(neighbors))
        return neighbors

    def draw(self):
        for wall in self.walls:
            rect = pg.Rect(wall * TILESIZE, (TILESIZE, TILESIZE))
            pg.draw.rect(window, LIGHTGREY, rect)


def vec2int(vec):
    return (int(vec.x), int(vec.y))

def draw_icons():
    start_rect = pg.Rect(start.x * TILESIZE, start.y * TILESIZE, TILESIZE, TILESIZE)
    window.blit(home_img, start_rect)
    goal_rect = pg.Rect(goal * TILESIZE, (TILESIZE, TILESIZE))
    window.blit(target_img, goal_rect)

def color_rect(pos, color):
    r = pg.Rect(pos.x * TILESIZE, pos.y * TILESIZE, TILESIZE, TILESIZE)
    pg.draw.rect(window, color, r)


def draw_grid():
    for x in range(0, WIDTH, TILESIZE):
        pg.draw.line(window, LIGHTGREY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, TILESIZE):
        pg.draw.line(window, LIGHTGREY, (0, y), (WIDTH, y))

def reset_path():
    global frontier, visited, path, paused, done, start, goal, firsttime
    frontier = deque()
    frontier.append(start)
    visited = []
    visited.append(start)
    path = {}
    path[vec2int(start)] = None
    paused = True
    done = False
    firsttime = True


g = SquareGrid(GRIDWIDTH, GRIDHEIGHT)
start = vec(14, 8)
goal = vec(20, 0)
frontier = deque()
frontier.append(start)
visited = []
visited.append(start)
path = {}
path[vec2int(start)] = None

toggle_grid = False
drawing = False
erase = False
paused = True
done = False
running = True
while running:
    clock.tick(FPS)
    # Events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                paused = not paused
            if event.key == pg.K_g:
                toggle_grid = not toggle_grid
            if event.key == pg.K_r:
                reset_path()
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False
                erase = False
        if event.type == pg.MOUSEBUTTONDOWN:
            mpos = vec(pg.mouse.get_pos()) // TILESIZE
            # walls
            if event.button == 1:
                if mpos in g.walls:
                    erase = True
                else:
                    drawing = True
            if event.button == 3:
                if paused and not done:
                    start = mpos
                    reset_path()
            if event.button == 2:
                if paused and not done:
                    goal = mpos
                    reset_path()

    # Update
    if len(frontier) > 0 and not paused and not done:
        current = frontier.popleft()
        if current == goal:
            done = True
        for next in g.find_neighbors(current):
            if next not in visited:
                frontier.append(next)
                visited.append(next)
                path[vec2int(next)] = current - next
    if len(frontier) == 0:
        done = True
    pg.display.set_caption("{:.2f}".format(clock.get_fps()))

    # Draw
    window.fill(DARKGREY)
    if drawing:   # draw walls
        mpos = vec(pg.mouse.get_pos()) // TILESIZE
        if mpos not in g.walls and mpos != start and mpos != goal:
            g.walls.append(mpos)
        for wall in g.find_neighbors(mpos):
            if wall not in g.walls and wall != start and wall != goal:
                g.walls.append(wall)
    if erase:
        mpos = vec(pg.mouse.get_pos()) // TILESIZE
        if mpos in g.walls:
            g.walls.remove(mpos)
        for node in [mpos + connection for connection in g.connections]:    # g.neighbors does not return neighboring walls in list
            if node in g.walls:
                g.walls.remove(node)

    for loc in visited:   # visited nodes are cyan
        color_rect(loc, CYAN)

    if len(frontier) > 0:   # frontier nodes are red
        for node in frontier:
            color_rect(node, RED)

    if done:
        current = goal
        while current != start:
            # fill in current
            color_rect(current, YELLOW)
            # find next
            try:
                current = current + path[vec2int(current)]
            except:
                print("NO POSSIBLE PATH!!!")
                pg.quit()
                sys.exit()
            # draw path step by step
            if firsttime:
                clock2.tick(20)
                draw_icons()
                g.draw()   # draws walls
                if toggle_grid:
                    draw_grid()
                pg.display.update()
        pg.time.wait(50)
        color_rect(start, YELLOW)
        firsttime = False

    draw_icons()
    g.draw()
    if toggle_grid:
        draw_grid()
    pg.display.update()
pg.quit()
sys.exit()