import pygame
import random
from tkinter import *
import os

pygame.init()

SCREEN_WIDTH = 500
CUBE_SIZE = 25

win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()


class Cube:
    def __init__(self, x, y, direction):
        self.direction = direction
        self.width = CUBE_SIZE
        self.height = CUBE_SIZE
        self.x = x
        self.y = y

    def draw(self, win):
        pygame.draw.rect(win, (255, 0, 0), (self.x, self.y, self.width, self.height))

    def move(self):
        if self.direction == 'right':
            if self.x == SCREEN_WIDTH - self.width:
                self.x = 0
            else:
                self.x += self.width
        if self.direction == 'left':
            if self.x == 0:
                self.x = SCREEN_WIDTH - self.width
            else:
                self.x -= self.width
        if self.direction == 'up':
            if self.y == 0:
                self.y = SCREEN_WIDTH - self.height
            else:
                self.y -= self.height
        if self.direction == 'down':
            if self.y == SCREEN_WIDTH - self.height:
                self.y = 0
            else:
                self.y += self.height


class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = CUBE_SIZE
        self.height = CUBE_SIZE
        self.changed = False

    def randomize_food(self):
        self.x = random.randrange(0, SCREEN_WIDTH, CUBE_SIZE)
        self.y = random.randrange(0, SCREEN_WIDTH, CUBE_SIZE)


class Snake:
    def __init__(self, rectangles, food):
        self.rectangles = rectangles
        self.food = food
        self.score = 0
        self.started = False

    def tail_check(self):
        for counter in range(1, len(self.rectangles)):
            if self.rectangles[0].x == self.rectangles[counter].x and self.rectangles[0].y == self.rectangles[counter].y:
                return False
        return True

    def add_cube(self):
        tail = self.rectangles[-1]
        if tail.direction == 'right':
            cube = Cube(tail.x - tail.width, tail.y, 'right')
            self.rectangles.append(cube)
        if tail.direction == 'left':
            cube = Cube(tail.x + tail.width, tail.y, 'left')
            self.rectangles.append(cube)
        if tail.direction == 'up':
            cube = Cube(tail.x, tail.y + tail.height, 'up')
            self.rectangles.append(cube)
        if tail.direction == 'down':
            cube = Cube(tail.x, tail.y - tail.height, 'down')
            self.rectangles.append(cube)
        self.score += 1

    def move(self):
        head = self.rectangles[0]
        for counter in range(len(self.rectangles)-1, 0, -1):
            self.rectangles[counter].direction = self.rectangles[counter-1].direction

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and head.direction != 'right':
            head.direction = 'left'
            self.started = True

        if keys[pygame.K_RIGHT] and head.direction != 'left':
            head.direction = 'right'
            self.started = True

        if keys[pygame.K_DOWN] and head.direction != 'up':
            head.direction = 'down'
            self.started = True

        if keys[pygame.K_UP] and head.direction != 'down':
            head.direction = 'up'
            self.started = True

        if self.started:
            for cube in self.rectangles:
                cube.move()

    def draw(self, win):
        for cube in self.rectangles:
            cube.draw(win)
        if self.rectangles[0].x == self.food.x and self.rectangles[0].y == self.food.y:
            self.add_cube()
            self.food.randomize_food()
            while not self.food.changed:
                for cube in self.rectangles:
                    if cube.x == self.food.x and cube.y == self.food.y:
                        self.food.randomize_food()
                        break
                    if cube == self.rectangles[-1]:
                        self.food.changed = True
        else:
            pygame.draw.rect(win, (0, 255, 0), (self.food.x, self.food.y, self.food.width, self.food.height))

    def reset(self):
        self.rectangles = [Cube(100, 25, 'right'), Cube(75, 25, 'right'), Cube(50, 25, 'right')]
        self.food = food
        self.started = False
        self.score = 0


font = pygame.font.SysFont('comicsans', 20, True, True)
font2 = pygame.font.SysFont('comicsans', 30, True, True)
cubes = [Cube(100, 25, 'right'), Cube(75, 25, 'right'), Cube(50, 25, 'right')]
food = Food(150, 150)
my_snake = Snake(cubes, food)


def message_box():
    root = Tk()
    root.title("Game over")
    label = Label(root, text='You lost!', width=20, pady=10)
    label.pack()
    play_again_button = Button(root, text="Play again", width=20, pady=10, fg='green2', command=root.destroy)
    play_again_button.pack()

    def exit_button_command():
        global run
        run = False
        root.destroy()

    exit_button = Button(root, text='exit', width=20, pady=10, fg='red', command=exit_button_command)
    exit_button.pack()
    root.mainloop()


def redraw_game_window():
    win.fill((0, 0, 0))
    my_snake.draw(win)

    if my_snake.tail_check():
        my_snake.move()
        score_text = font.render("Score: {}".format(my_snake.score), 1, (255, 255, 255))
        win.blit(score_text, (SCREEN_WIDTH - 100, 30))
        pygame.display.update()
    else:
        text = font2.render('You hit your tail! Your score is {}'.format(my_snake.score), 1, (255, 255, 255))
        center = SCREEN_WIDTH//2, SCREEN_WIDTH//2
        centered_box = text.get_rect(center=center)
        win.blit(text, centered_box)
        pygame.display.update()
        message_box()
        my_snake.reset()


run = True

# mainloop

while run:

    pygame.time.delay(50)
    # delay and clock.tick parameters decide on the snake 'fluency'
    # it can work differently on other computers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    redraw_game_window()
    clock.tick(10)

pygame.quit()


# def run():
#     pass
#
#
# if __name__ == "__main__":
#     local_dir = os.path.dirname(__file__)
#     config_path = os.path.join(local_dir, 'neat-config.txt')