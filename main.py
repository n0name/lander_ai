import math
import pygame
import random
from pygame.locals import *
from math2d import Vec2d, Angle
from math2d.ray2d import Ray2D
from math2d.shapes import Segment2D
import neat
import copy

def to_rect(pos, w, h):
    r = Rect(0, 0, 0, 0)
    r.center = pos.as_int_tup()
    r.size = (w, h)
    return r


def does_intersect(rect, seg):
    segments = [
        Segment2D(Vec2d(*rect.topleft), Vec2d(*rect.bottomleft)),
        Segment2D(Vec2d(*rect.bottomleft), Vec2d(*rect.bottomright)),
        Segment2D(Vec2d(*rect.bottomright), Vec2d(*rect.topright)),
        Segment2D(Vec2d(*rect.topright), Vec2d(*rect.topleft))
    ]
    for s in segments:
        if len(seg.intersect_with(s)) > 0:
            return True
    return False

def clamp(val, v_min, v_max):
    return min(val, max(val, v_min), v_max)

class FireParticle:

    def __init__(self, pos, direct, life):
        self.particlePos = Vec2d(pos)
        self.particleDir = Vec2d(direct)
        self.life = life

    def draw(self, screen):
        pygame.draw.circle(screen, (200 + self.life, 50 +  4 * self.life,self.life * 5), self.particlePos.as_int_tup(), 2, 1)

    def update(self):
        self.life -= 1
        self.particlePos += self.particleDir

class Fire:

    def __init__(self):
        self.particles = []

    def update(self, thrust, thrustPos, thrustAng):
        newParticles = []
        for ember in self.particles:
            ember.update()
            if ember.life > 0:
                newParticles.append(ember)
        for _ in range(thrust):
            fireDir = Vec2d(-thrust/2, 0)
            fireDir.rotate(-thrustAng + random.randint(0, 10))
            firePos = thrustPos + Vec2d(0, 25).rotated(90 - thrustAng)
            newParticles.append(FireParticle(firePos, fireDir, random.randint(20, 50)))
        self.particles = newParticles

    def draw(self, screen):
        for ptcl in self.particles:
            ptcl.draw(screen)

class Ship:
    def __init__(self, pos, maxfuel, *, color=(0, 200, 0)):
        self.start_pos = copy.copy(pos)
        self.pos = pos
        self.vel = Vec2d(0, 0)
        self.thrust = 0
        self.angle = Angle(deg=90)
        self.fuel = maxfuel
        self.maxFuel = maxfuel
        self.color = color

        self.halfSizeX = 25
        self.halfSizeY = 12

        self.landed = False
        self.dead = False

        self.fire = Fire()

    def reset(self):
        self.pos = self.start_pos
        self.vel = Vec2d(0, 0)
        self.thrust = 0
        self.angle = Angle(deg=90)
        self.fuel = self.maxFuel
        self.landed = False
        self.dead = False


    def get_bound_rect(self):
        return to_rect(self.pos, 25, 50)

    def draw(self, screen):
        br = self.get_bound_rect()
        pos = br.center
        if self.dead:
            draw_color = (128, 128, 128)
        else:
            draw_color = self.color
        vtc = []
        vtc.append(Vec2d(-self.halfSizeX, self.halfSizeY).rotated(-self.angle.deg) + pos)
        vtc.append(Vec2d(self.halfSizeX, self.halfSizeY).rotated(-self.angle.deg) + pos)
        vtc.append(Vec2d(self.halfSizeX, -self.halfSizeY).rotated(-self.angle.deg) + pos)
        vtc.append(Vec2d(-self.halfSizeX, -self.halfSizeY).rotated(-self.angle.deg) + pos)
        pygame.draw.polygon(screen, draw_color, vtc, 0)

        fillvtc = []
        gaugeLen = 2*self.halfSizeX*(1-(self.fuel/self.maxFuel))
        fillvtc.append(Vec2d(self.halfSizeX+1-gaugeLen, self.halfSizeY-1).rotated(-self.angle.deg) + pos)
        fillvtc.append(Vec2d(self.halfSizeX-1, self.halfSizeY-1).rotated(-self.angle.deg) + pos)
        fillvtc.append(Vec2d(self.halfSizeX-1, 1-self.halfSizeY).rotated(-self.angle.deg) + pos)
        fillvtc.append(Vec2d(self.halfSizeX+1-gaugeLen, 1-self.halfSizeY).rotated(-self.angle.deg) + pos)
        pygame.draw.polygon(screen, (30,30,30), fillvtc, 0)

        # Debug draw bound rect
        # pygame.draw.rect(screen, (255, 0, 0), br, 2)

        if not self.landed and not self.dead:
            self.fire.draw(screen)

    def update(self, dt):
        if self.fuel <= 0:
            self.thrust = 0

        self.force = Vec2d(math.cos(self.angle.rad), math.sin(self.angle.rad))
        self.force.length = self.thrust * 20
        self.force += Vec2d(0, -3 * 20) # gravity is a bit weak
        self.force.y *= -1
        self.pos += self.vel * dt
        self.vel += self.force * dt# we asume that mass == 1
        self.fuel -= self.thrust * dt

        if not self.landed and not self.dead:
            self.fire.update(self.thrust, self.pos + Vec2d(25/2, 50/2), self.angle.deg)

class Level:
    @staticmethod
    def generate(total_len, min_height, max_heigh, num_steps):
        step_size = total_len // num_steps
        flat_step = random.randint(1, num_steps)
        last_y = random.randint(min_height, max_heigh)
        pts = [Vec2d(0, last_y)]
        for i in range(num_steps + 1):
            cur_x = i * step_size
            if i == flat_step:
                cur_pt = last_y
            else:
                cur_pt = random.randint(min_height, max_heigh)

            pts.append(Vec2d(cur_x, cur_pt))
            last_y = cur_pt
        lvl = Level(pts)
        lvl.index_landing = flat_step
        return lvl

    def landing_center(self):
        p1 = self.floor[self.index_landing]
        p2 = self.floor[self.index_landing + 1]
        return (p1 + p2) / 2

    def __init__(self, floor_pts, ceiling_pts=[]):
        self.floor = floor_pts
        self.ceiling = ceiling_pts
        self.index_landing = -1

    def draw(self, screen):
        color = (150, 50, 0)
        color_landing = (0, 255, 0)
        screen_rect = screen.get_rect()
        if len(self.floor) > 1:
            floor_pts = [screen_rect.bottomleft]
            floor_pts += list(map(lambda p: p.as_int_tup(), self.floor))
            floor_pts.append(screen_rect.bottomright)
            pygame.draw.polygon(screen, color, floor_pts)
            if self.index_landing >= 0:
                p1 = self.floor[self.index_landing].as_int_tup()
                p2 = self.floor[self.index_landing + 1].as_int_tup()
                pygame.draw.line(screen, color_landing,p1, p2, 3)
        if len(self.ceiling) > 1:
            pygame.draw.polygon(screen, color, list(map(lambda p: p.as_int_tup(), self.ceiling)))

class Game:
    def __init__(self, level, ships, area):
        self.level = level
        self.ships = ships
        self.area = area
        self.dead = []


    def check_landed(self, ship):
        # print("angle", ship.angle.deg)
        # print("velocity", ship.vel)
        angle_check = abs(ship.angle.deg - 90) < 2
        vertical_speed_check = abs(ship.vel.y) < 20
        horizontal_speed_check = abs(ship.vel.x) < 10
        return angle_check and vertical_speed_check and horizontal_speed_check

    def check_collisions(self):
        # Check if outside
        to_remove = set()

        for s in self.ships:
            if s.pos.x < 0 or s.pos.x > self.area.x:
                to_remove.add(s)
            elif s.pos.y < 0 or s.pos.y > self.area.y:
                to_remove.add(s)

        for s in to_remove:
            self.ships.remove(s)
            if not s.landed:
                s.dead = True
            self.dead.append(s)

        # Check if colided with ground
        to_remove = set()

        for p1, p2 in zip(self.level.floor, self.level.floor[1:]):
            seg = Segment2D(p1, p2)
            for s in self.ships:
                if does_intersect(s.get_bound_rect(), seg):
                    if seg.beg.y == seg.end.y:
                        if self.check_landed(s):
                            s.landed = True
                    to_remove.add(s)

        for s in to_remove:
            self.ships.remove(s)
            if not s.landed:
                s.dead = True
            self.dead.append(s)

    def update(self, dt):
        for s in self.ships:
            if not s.landed:
                s.update(dt)
        
        self.check_collisions()

    def draw(self, screen):
        self.level.draw(screen)

        for s in self.dead:
            s.draw(screen)

        for s in self.ships:
            s.draw(screen)

class AiShip(Ship):
    def __init__(self, pos, maxfuel, *, color=(0, 200, 0), genome=None):
        super().__init__(pos, maxfuel, color=color)
        if genome is None:
            self.genome = neat.Genome(7, 2, node_mut_rate=0.2, con_mut_rate=0.2)
        else:
            self.genome = genome

        self.fitness = 0
        self.time_alive = 0

    def update_ai(self, level):
        landing_site = level.landing_center()
        r = Ray2D(self.pos, Vec2d(0, 1))
        height = 0
        for p1, p2 in zip(level.floor, level.floor[1:]):
            seg = Segment2D(p1, p2)
            crosses = seg.intersect_with(r)
            if len(crosses) == 1:
                height = self.pos.get_distance(crosses[0])
                break

        new_angle, new_thrust = self.genome.eval([self.pos.x, self.pos.y, self.vel.x, self.vel.y, landing_site.x, landing_site.y, height])
        self.angle.deg = clamp(new_angle, 0, 180)
        if new_thrust > 4:
            new_thrust = 4
        if new_thrust < 0:
            new_thrust = 0
        self.thrust = int(new_thrust)
        # self.thrust = abs(int(clamp(new_thrust, 0, 4)))

    def update(self, dt):
        self.time_alive += dt
        super().update(dt)

    def calculate_fitness(self, level, max_dist):
        landing_site = level.landing_center()
        dist_to_landing = (self.pos - landing_site).length
        fitness = 0
        fitness -= dist_to_landing# + self.fuel
        fitness -= abs(90 - self.angle.deg)
        # fitness += 10 * self.time_alive
        fitness += self.fuel
        fitness -= self.vel.length
        if self.landed:
            fitness += 9000 # yes it goes over 9000
        
        self.fitness = fitness

def draw_text(screen, font, text, pos):
    surf = font.render(text, False, (0, 255, 0))
    screen.blit(surf, pos)

def debug_hud(ship, screen, pos=Vec2d(50, 50)):
    size = 20
    font = pygame.font.SysFont('Arial', size)
    draw_text(screen, font, 'thrust: {}'.format(ship.thrust), pos.as_int_tup())
    pos.y += size
    draw_text(screen, font, 'velocity: {}'.format(ship.vel), pos.as_int_tup())
    pos.y += size
    draw_text(screen, font, 'Angle: {}'.format(ship.angle.deg), pos.as_int_tup())
    pos.y += size
    draw_text(screen, font, 'fuel: {}'.format(ship.fuel), pos.as_int_tup())

tracked = None
def ai_debug_hud(screen, game, generation, fitness, *, tracking=False):
    global tracked
    size = 20
    pos = 50
    font = pygame.font.SysFont('Arial', size)

    text = [
        'Generation: {}'.format(generation),
        'Fitness: {}'.format(fitness),
        'Alive: {}'.format(len(game.ships))
    ]

    for t in text:
        draw_text(screen, font, t, (50, pos))
        pos += size

    if tracking:
        if tracked is None or tracked.dead:
            if tracked is not None:
                tracked.color = (20, 190, 250)
            tracked = random.choice(game.ships)
            tracked.color = (0, 255, 0)

        debug_hud(tracked, screen, Vec2d(screen.get_rect().width - 400, 50))

def spawn_and_reset(screen, game, cnt, *, reset_level=False):
    screen_rect = screen.get_rect()
    if cnt < 3:
        cnt = 3
    ai_ships = []
    for s in game.dead:
        if isinstance(s, AiShip):
            s.calculate_fitness(game.level, screen_rect.width)
            ai_ships.append(s)

    screen_size = Vec2d(*screen_rect.size)

    game.dead = []
    game.ships = []
    if reset_level:
        game.level = Level.generate(screen_size.x, 2 * screen_size.y // 3, screen_size.y, 10)
    reproduceable = sorted(ai_ships, key=lambda s: s.fitness, reverse=True)[:4] # the top 3

    tf = reproduceable[0].fitness
    print(reproduceable[0].genome)

    for s in reproduceable:
        s.reset()
        # game.ships.append(s)
        game.ships.append(AiShip(Vec2d(*screen_rect.center), s.maxFuel, color=(20, 190, 250), genome=copy.deepcopy(s.genome)))
        for _ in range(cnt // 3 - 1):
            new_genome = copy.deepcopy(s.genome)
            new_genome.mutate()
            game.ships.append(AiShip(Vec2d(*screen_rect.center), s.maxFuel, color=(20, 190, 250), genome=new_genome))

    return tf

def main():
    screen_size = Vec2d(1280, 720)
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(screen_size.as_int_tup())

    ship = None #Ship(screen_size / 2, 50, color=(20, 190, 250))
    level = Level.generate(screen_size.x, 2 * screen_size.y // 3, screen_size.y, 10)

    game = Game(level, [], screen_size)
    if ship is not None:
        game.ships.append(ship)

    generation = 0
    top_fitness = 0
    generation_cnt = 50
    for _ in range(generation_cnt):
        s = AiShip(screen_size / 2, 50, color=(20, 190, 250))
        s.genome.mutate()
        game.ships.append(s)
    clock = pygame.time.Clock()


    num_stars = 100
    stars = []
    for _ in range(num_stars):
        star = Vec2d(
            random.randrange(0, screen_size.x),
            random.randrange(0, screen_size.y)
        )
        stars.append(star)

    fitness_history = []

    asap = False
    mainloop = True
    while mainloop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                mainloop = False # pygame window closed by user
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False # user pressed ESC
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    asap = not asap
                if ship is not None: # Debug stuff
                    if event.key == pygame.K_UP:
                        if ship.thrust < 4:
                            ship.thrust += 1
                    elif event.key == pygame.K_DOWN:
                        if ship.thrust > 0:
                            ship.thrust -= 1
                    elif event.key == pygame.K_LEFT:
                        if ship.angle.deg < 180:
                            ship.angle.deg = ship.angle.deg + 10
                    elif event.key == pygame.K_RIGHT:
                        if ship.angle.deg > 0:
                            ship.angle.deg = ship.angle.deg - 10

        dt = clock.get_time() / 1000
        if dt > 1:
            dt = 0.017


        # Update
        for s in game.ships:
            if isinstance(s, AiShip):
                s.update_ai(game.level)
        game.update(dt)
        if len(game.ships) == 0:
            print('=============================================')
            print('Generation:', generation)
            generation += 1
            top_fitness = spawn_and_reset(screen, game, generation_cnt, reset_level=generation % 5 == 0)
            fitness_history.append(top_fitness)

        # Drawing
        screen.fill((0, 0, 33))
        ai_debug_hud(screen, game, generation, top_fitness, tracking=True)

        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), star.as_int_tup(), 2)

        game.draw(screen)
        if ship is not None:
            debug_hud(ship, screen)
        pygame.display.flip()
        if not asap:
            clock.tick(60)
        else:
            clock.tick(999)
    
    # print evolution history
    pygame.quit()
    import matplotlib
    from matplotlib import pyplot as plt
    matplotlib.style.use('dark_background')
    print("Fitness:", fitness_history)
    plt.figure(figsize=(20, 15))
    plt.plot(fitness_history)
    plt.show()

if __name__ == "__main__":
    main()