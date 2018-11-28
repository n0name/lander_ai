import math
import pygame
import random
from pygame.locals import *
from math2d import *
from math2d.shapes import Segment2D
import neat

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

        self.fire = Fire()

    def get_bound_rect(self):
        return to_rect(self.pos, 25, 50)

    def draw(self, screen):
        br = self.get_bound_rect()
        pos = br.center
        vtc = []
        vtc.append(Vec2d(-self.halfSizeX, self.halfSizeY).rotated(-self.angle.deg) + pos)
        vtc.append(Vec2d(self.halfSizeX, self.halfSizeY).rotated(-self.angle.deg) + pos)
        vtc.append(Vec2d(self.halfSizeX, -self.halfSizeY).rotated(-self.angle.deg) + pos)
        vtc.append(Vec2d(-self.halfSizeX, -self.halfSizeY).rotated(-self.angle.deg) + pos)
        pygame.draw.polygon(screen, self.color, vtc, 0)

        fillvtc = []
        gaugeLen = 2*self.halfSizeX*(1-(self.fuel/self.maxFuel))
        fillvtc.append(Vec2d(self.halfSizeX+1-gaugeLen, self.halfSizeY-1).rotated(-self.angle.deg) + pos)
        fillvtc.append(Vec2d(self.halfSizeX-1, self.halfSizeY-1).rotated(-self.angle.deg) + pos)
        fillvtc.append(Vec2d(self.halfSizeX-1, 1-self.halfSizeY).rotated(-self.angle.deg) + pos)
        fillvtc.append(Vec2d(self.halfSizeX+1-gaugeLen, 1-self.halfSizeY).rotated(-self.angle.deg) + pos)
        pygame.draw.polygon(screen, (30,30,30), fillvtc, 0)

        # Debug draw bound rect
        # pygame.draw.rect(screen, (255, 0, 0), br, 2)

        if not self.landed:
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

        if not self.landed:
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
    def __init__(self, level, ships):
        self.level = level
        self.ships = ships


    def check_landed(self, ship):
        print("angle", ship.angle.deg)
        print("velocity", ship.vel)
        angle_check = abs(ship.angle.deg - 90) < 2
        vertical_speed_check = abs(ship.vel.y) < 20
        horizontal_speed_check = abs(ship.vel.x) < 10
        return angle_check and vertical_speed_check and horizontal_speed_check

    def check_collisions(self):
        to_remove = []
        for p1, p2 in zip(self.level.floor, self.level.floor[1:]):
            seg = Segment2D(p1, p2)
            for s in self.ships:
                if does_intersect(s.get_bound_rect(), seg):
                    if seg.beg.y == seg.end.y:
                        if self.check_landed(s):
                            s.landed = True
                        else:
                            to_remove.append(s)
                    else:
                        to_remove.append(s)
        
        for s in to_remove:
            self.ships.remove(s)

    def update(self, dt):
        for s in self.ships:
            if not s.landed:
                s.update(dt)
        
        self.check_collisions()

    def draw(self, screen):
        self.level.draw(screen)
        for s in self.ships:
            s.draw(screen)


class AiShip(Ship):
    def __init__(self, pos, maxfuel, *, color=(0, 200, 0)):
        super().__init__(pos, maxfuel, color=color)
        self.genome = neat.Genome(3, 2)

    def update(self, dt):
        angle, thrust = self.genome.eval([self.vel.x, self.vel.y, self.fuel])

        super().update(dt)

def draw_text(screen, font, text, pos):
    surf = font.render(text, False, (0, 255, 0))
    screen.blit(surf, pos)

def debug_hud(ship, screen):
    size = 20
    pos = 50
    font = pygame.font.SysFont('Arial', size)
    draw_text(screen, font, 'thrust: {}'.format(ship.thrust), (50, pos))
    pos += size
    draw_text(screen, font, 'velocity: {}'.format(ship.vel), (50, pos))
    pos += size
    draw_text(screen, font, 'Angle: {}'.format(ship.angle.deg), (50, pos))
    pos += size
    draw_text(screen, font, 'fuel: {}'.format(ship.fuel), (50, pos))


def main():
    screen_size = Vec2d(1280, 720)
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(screen_size.as_int_tup())

    ship = Ship(screen_size / 2, 50, color=(20, 190, 250))
    level = Level.generate(screen_size.x, 2 * screen_size.y // 3, screen_size.y, 10)

    game = Game(level, [])
    if ship is not None:
        game.ships.append(ship)
    clock = pygame.time.Clock()


    num_stars = 100
    stars = []
    for _ in range(num_stars):
        star = Vec2d(
            random.randrange(0, screen_size.x),
            random.randrange(0, screen_size.y)
        )
        stars.append(star)

    mainloop = True
    while mainloop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                mainloop = False # pygame window closed by user
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False # user pressed ESC
            elif event.type == pygame.KEYUP:
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
        game.update(dt)
        # if len(game.ships) == 0:
        #     mainloop = False

        # Drawing
        screen.fill((0, 0, 33))

        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), star.as_int_tup(), 2)

        game.draw(screen)
        if ship is not None:
            debug_hud(ship, screen)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()