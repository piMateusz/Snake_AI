import pygame
import random
import os
import neat

pygame.init()

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
CUBE_SIZE = 25

win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH))
pygame.display.set_caption("Snake Game")


class Cube:
    def __init__(self, x, y, direction):
        self.direction = direction
        self.width = CUBE_SIZE
        self.height = CUBE_SIZE
        self.x = x
        self.y = y

    def draw(self, win, color):
        pygame.draw.rect(win, color, (self.x, self.y, self.width, self.height))

    def move(self):
        if self.direction == 'right':
            self.x += self.width
        if self.direction == 'left':
            self.x -= self.width
        if self.direction == 'up':
            self.y -= self.height
        if self.direction == 'down':
            self.y += self.height


class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = CUBE_SIZE
        self.height = CUBE_SIZE
        self.changed = False

    def randomize_food(self):
        self.changed = False
        self.x = random.randrange(0, SCREEN_WIDTH, CUBE_SIZE)
        self.y = random.randrange(0, SCREEN_WIDTH, CUBE_SIZE)


class Snake:
    def __init__(self, rectangles, food):
        self.rectangles = rectangles
        self.food = food
        self.score = 0
        self.move_count = 0

    def check_for_collision(self):
        head = self.rectangles[0]
        for counter in range(1, len(self.rectangles)):
            if head.x == self.rectangles[counter].x and head.y == self.rectangles[counter].y:
                return True
        if head.x >= SCREEN_WIDTH:
            return True
        if head.x + CUBE_SIZE <= 0:
            return True
        if head.y + CUBE_SIZE <= 0:
            return True
        if head.y >= SCREEN_HEIGHT:
            return True

        return False

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

    def refresh(self):
        for counter in range(len(self.rectangles) - 1, 0, -1):
            self.rectangles[counter].direction = self.rectangles[counter - 1].direction

    def move_cubes(self):
        for cube in self.rectangles:
            cube.move()

    def check_for_food(self):
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

    def draw(self, win):
        for cube in self.rectangles:
            if cube == self.rectangles[0]:
                cube.draw(win, (0, 0, 255))
            else:
                cube.draw(win, (255, 0, 0))
        if not (self.rectangles[0].x == self.food.x and self.rectangles[0].y == self.food.y):
            pygame.draw.rect(win, (0, 255, 0), (self.food.x, self.food.y, self.food.width, self.food.height))


def redraw_game_window(win, snake):
    win.fill((0, 0, 0))
    snake.draw(win)
    score_text = font.render("Move: {}, Score: {}".format(snake.move_count, snake.score), 1,
                             (255, 255, 255))
    win.blit(score_text, (SCREEN_WIDTH - 200, 30))
    pygame.display.update()


font = pygame.font.SysFont('comicsans', 20, True, True)
font2 = pygame.font.SysFont('comicsans', 30, True, True)
food = Food(150, 150)


def fitness_function(genomes, config):
    nets = []
    ge = []
    snakes = []
    run = True

    directions = ['up', 'right', 'down', 'left']
    # mainloop

    # genomes -> tuple (genome_id , object)
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        cubes = [Cube(150, 200, 'right'), Cube(125, 200, 'right'), Cube(100, 200, 'right')]
        food = Food(150, 150)
        snakes.append(Snake(cubes, food))
        g.fitness = 0
        ge.append(g)

    clock = pygame.time.Clock()

    snake0 = snakes[0]

    while run and snakes:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        if snake0 in snakes:
            pygame.time.delay(100)
            redraw_game_window(win, snake0)

        for x, snake in enumerate(snakes):
            snake.refresh()
            ge[x].fitness += 0.1
            snake.move_count += 1

            head = snake.rectangles[0]

            # walls
            right_wall = left_wall = up_wall = down_wall = 0
            if head.x == SCREEN_WIDTH - CUBE_SIZE:
                right_wall = 1
            if head.x == 0:
                left_wall = 1
            if head.y == 0:
                up_wall = 1
            if head.y == SCREEN_HEIGHT - CUBE_SIZE:
                down_wall = 1

            # tails
            right_tail = left_tail = up_tail = down_tail = 0
            for counter in range(1, len(snake.rectangles)):
                if head.y == snake.rectangles[counter].y:
                    if head.x == snake.rectangles[counter].x - CUBE_SIZE:
                        right_tail = 1
                    if head.x == snake.rectangles[counter].x + CUBE_SIZE:
                        left_tail = 1
                if head.x == snake.rectangles[counter].x:
                    if head.y == snake.rectangles[counter].y + CUBE_SIZE:
                        up_tail = 1
                    if head.y == snake.rectangles[counter].y - CUBE_SIZE:
                        down_tail = 1

            # foods
            right_food = left_food = up_food = down_food = 0
            if snake.food.y >= head.y:
                down_food = head.y - snake.food.y
            if snake.food.y <= head.y:
                up_food = head.y - snake.food.y
            if snake.food.x <= head.x:
                left_food = head.x - snake.food.x
            if snake.food.x >= head.x:
                right_food = snake.food.x - head.x

            output = nets[x].activate([up_wall, up_food, up_tail, down_wall, down_food, down_tail,
                                       right_wall, right_food, right_tail, left_wall, left_food, left_tail])

            if head.direction == 'up':
                output[2] = -1
            if head.direction == 'down':
                output[1] = -1
            if head.direction == 'right':
                output[3] = -1
            if head.direction == 'left':
                output[0] = -1

            max_value = max(output)

            # output = ['right', 'up', 'down', 'left']

            if output.index(max_value) == 0:
                head.direction = 'right'
            elif output.index(max_value) == 1:
                head.direction = 'up'
            elif output.index(max_value) == 2:
                head.direction = 'down'
            else:
                head.direction = 'left'

            snake.move_cubes()
            snake.check_for_food()

            if snake0 not in snakes:
                snake0 = snake

            if snake.food.changed:
                ge[x].fitness += 1
                snake.move_count = 0
                snake.food.changed = False

            if snake.move_count > 100:
                ge[x].fitness -= 1
                snakes.pop(x)
                ge.pop(x)
                nets.pop(x)

        for x, snake in enumerate(snakes):
            if snake.check_for_collision():
                ge[x].fitness -= 1
                snakes.pop(x)
                nets.pop(x)
                ge.pop(x)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(fitness_function, 50)

    # with open('winner.pkl', 'wb') as output:
    #   pickle.dump(winner, output, 1)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.txt')
    run(config_path)
