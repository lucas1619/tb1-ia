import pygame
import time
import random
import math

from sqlalchemy import null
from utils import scale_image, blit_rotate_center

LIDER_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
CAR = scale_image(pygame.image.load("imgs/white-car.png"), 0.55)
class AbstractCar:
    def __init__(self, max_vel, rotation_vel, path=[]):
        self.img = CAR
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.winner = False
        self.looser = False
        self.path = path
        self.path_index = 0
        self.distance = 0

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self, winner=False):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0
        self.winner = winner
        if not winner:
            self.looser = True


class Car(AbstractCar):
    START_POS = (180, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = 0
        #self.move()


def draw(win, images, cars):
    for img, pos in images:
        win.blit(img, pos)
    for car in cars:
        car.draw(win)
    pygame.display.update()


def move_car(car):
    if car.looser: return
    move = None
    if car.path_index < len(car.path):
        move = car.path[car.path_index]
    else:
        move = random.randint(1, 2)
        car.path.append(move)
    car.path_index += 1
    if move == 1:
        car.rotate(left=True)
    if move == 2:
        car.rotate(right=True)
    car.move_forward()
    car.distance += 1
    
def test_cars(cars):
    track_border = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
    track_border_mask = pygame.mask.from_surface(track_border)
    track = scale_image(pygame.image.load("imgs/track.png"), 0.9)
    width, height = track.get_width(), track.get_height()
    grass = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
    win = pygame.display.set_mode((width, height))
    finish = pygame.image.load("imgs/finish.png")
    finish_mask = pygame.mask.from_surface(finish)
    finish_position = (130, 250)
    clock = pygame.time.Clock()
    images = [(grass, (0, 0)), (track, (0, 0)),
            (finish, finish_position), (track_border, (0, 0))]
    run = True
    while run:
        clock.tick(60)
        loosers = 0
        for car in cars:
            if car.looser:
                loosers += 1
            if loosers == len(cars):
                break
        if loosers == len(cars):
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        for car in cars:
            move_car(car)

            if car.collide(track_border_mask) != None:
                car.reset()

            finish_poi_collide = car.collide(finish_mask, *finish_position)
            if finish_poi_collide != None:
                if finish_poi_collide[1] == 0:
                    car.reset()
                else:
                    car.reset(True)
                    print("finish")
        draw(win, images, cars)
    pygame.quit()

def fitness(cars):
    scores = []
    for car in cars:
        score = car.distance
        scores.append(score)
    return scores

def genetic_algorithm(population, generations):
    cars = []
    for _ in range(population):
        cars.append(Car(8,8)) # Generate first chromosomes

    for _ in range(generations):
        print("Generation: ", _)
        # reset cars
        for i in range(population):
            cars[i].winner = False
            cars[i].looser = False
            cars[i].path_index = 0
            cars[i].distance = 0
        # test cars
        test_cars(cars)
        # calculate fitness
        scores = fitness(cars)
        # sort cars by fitness
        cars = sorted(cars, key=lambda x: x.distance)

        # select best cars
        best_cars_path = [cars[-1].path, cars[-2].path]
        # crossover point
        crossover_point = random.randint(1, min(len(best_cars_path[0]), len(best_cars_path[1])) - 1)
        # crossover
        child1 = best_cars_path[0][:crossover_point] + best_cars_path[1][crossover_point:]
        child2 = best_cars_path[1][:crossover_point] + best_cars_path[0][crossover_point:]
        # mutate
        child1[random.randint(0, len(child1) - 1)] = random.randint(1, 2)
        child2[random.randint(0, len(child2) - 1)] = random.randint(1, 2)
        # add new cars
        cars[0].path = child1
        cars[1].path = child2
    

        for i in range(population - 2):
            cars[i].img = CAR

        cars[-1].img = LIDER_CAR
        cars[-2].img = LIDER_CAR



genetic_algorithm(100, 10000)
