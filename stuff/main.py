from random import randint
from time import sleep, time
import queue
import sys

from stuff import values

try:
    import pygame
except ImportError:
    pass

class Map():
    def __init__(self, y, x):
        self.x, self.y = x, y
        if ver == "graphic":
           pygame.init()
           self.screen = pygame.display.set_mode((y * 12, x * 8))
           pygame.display.init() # is it needed?
           self.bg_color=(0,0,0)
        self.objs, self.corpses, self.grass, self.stone, self.ID = [], [], [], [], 0
        self.wait = randint(1, values.Grass_spawn_rate)
        self.znaky = ["$"]
        for i in range(self.x*self.y):
            self.znaky.append(str(i))
    def add(self, obj):
        self.objs.append(obj)
        self.ID += 1
    def addc(self, obj):
        self.corpses.append(obj)
    def addg(self, obj):
        self.grass.append(obj)
    def adds(self, obj):
        self.stone.append(obj)
    def draw(self):
        x, y = self.x, self.y

        pole = []
        for i in range(x):
            pole.append([])
            pole[i].extend([" "]*y)
            
        if ver == "graphic":
           self.screen.fill(self.bg_color)
        
           for obj in self.grass:
               obj.rect.topleft = (obj.x*12, obj.y*8)
               self.screen.blit(obj.img, obj.rect)
            
           for obj in self.objs + self.stone + self.corpses: #str(obj.ID)
               obj.rect.topleft = (obj.x*12, obj.y*8)
               self.screen.blit(obj.img, obj.rect)

           pygame.display.update()
           
        elif ver == "text":
           for obj in self.grass:
               pole[obj.y][obj.x] = obj.znak
            
           for obj in self.stone + self.corpses + self.objs:
               pole[obj.y][obj.x] = obj.znak # if objs: str(obj ID)
            
           for i in range(x):
               pole[i] = "".join(pole[i])
           pole = "\n".join(pole)
           print()
           print(pole, end = "")

    def update(self):
        for obj in self.objs + self.grass + self.corpses:
            obj.update()
        self.wait -= 1
        if self.wait == 0:
            self.wait = randint(1, values.Grass_spawn_rate)
            self.addg(Grass(randint(1, self.x - 2), randint(1, self.y - 2), self)) # idea: grass not spawning on ocuped tiles .gramar.
        
class Sprite():
    def __init__(self, znak, y, x, mapa, image):
        self.y, self.x = y, x
        self.znak = znak
        self.mapa = mapa
        self.priority = "eat"
        if ver == "graphic":
            self.img = pygame.image.load("stuff/pic/{}".format(image)).convert_alpha()
            self.rect = self.img.get_rect()
    def move(self):
        pass            
    def closest(self, ents):
        far = self.mapa.x * self.mapa.y
        for i in range(len(ents)): # min max?
            nfar = abs(ents[i].x - self.x) + abs(ents[i].y - self.y)
            if nfar < far:
                far = nfar
                self.target = ents[i]
    def runto(self):
        ax = abs(self.x - self.target.x)
        ay = abs(self.y - self.target.y)
        if ax + ay == 1:
            return None        
        if ax >= ay:
            go = (1, 0)
            if self.x > self.target.x:
                go = (-1, 0)
        else:
            go = (0, 1)        
            if self.y > self.target.y:
                go = (0, -1)
        return (self.x + go[0], self.y + go[1])
    def runrand(self, beh):
        if beh < 25:
            return (self.x, self.y - 1)
        elif 25 <= beh and beh < 50:
            return (self.x + 1, self.y)
        elif 50 <= beh and beh < 75:
            return (self.x, self.y + 1)
        elif 75 <= beh and beh < 100:
            return (self.x - 1, self.y)
    def hunger(self):
        if self.znak == "S":
            self.hungry -= values.Sheep_hungry
        elif self.znak == "s":
            self.hungry -= values.Sheep_baby_hungry
        elif self.znak == "D":
            self.hungry -= values.Dog_hungry
        if self.hungry <= 0:
            self.mapa.addc(Corpse(self.y, self.x, self.mapa, self.food))
            self.mapa.objs.remove(self)
        elif self.znak == "S" and self.hungry < values.Sheep_I_am_hungry:
            self.priority = "eat"
        elif self.znak == "s" and self.hungry < values.Sheep_baby_I_am_hungry:
            self.priority = "eat"
        elif self.znak == "D" and self.hungry < values.Dog_I_am_hungry:
            self.priority = "eat"
    def eat(self, eatit, toeat):
        for obj in self.mapa.corpses + self.mapa.grass:
            if abs(self.x - obj.x) + abs(self.y - obj.y) == 1 and eatit == obj.znak:
                if toeat == 0:
                    return True
                if toeat > obj.food:
                    toeat = obj.food
                obj.food -= toeat
                self.hungry += toeat
                if self.znak == "S" and self.hungry >= values.Sheep_stomach:
                    self.priority = "augment"
                if self.znak == "s" and self.hungry >= values.Sheep_baby_stomach:
                    self.priority = "evolve"
                elif self.znak == "D" and self.hungry >= values.Dog_stomach:
                    self.priority = "augment"
                return
    def validate(self, goto):
        gut = True #
        for obj in self.mapa.objs + self.mapa.corpses + self.mapa.stone:
            if goto[0] == obj.x and goto[1] == obj.y:
                gut = False #return False
        return gut #return True
    def update(self):
        newpos = self.move()
        if newpos == None:
            pass
        elif self.validate(newpos) == True:
            self.x, self.y = newpos
    def search(self, dest, passit):
        self.q, self.done, self.znaky, self.index = queue.Queue(), False, ["A"], 0
        self.pole = []
        self.q.put((0, self.y, self.x))
        for i in range(self.mapa.y):
            self.pole.append([]) #merge these two lines
            self.pole[i].extend([" "]*self.mapa.x) #is it slow?
        for obj in self.mapa.grass:
            self.pole[obj.x][obj.y] = obj.znak
        for obj in self.mapa.stone + self.mapa.corpses:
            self.pole[obj.x][obj.y] = obj.znak
        for obj in self.mapa.objs:
            self.pole[obj.x][obj.y] = obj.znak + str(obj.ID) #slow?
        self.pole[self.x][self.y] = "$" #is $ needed?
        if self.searchthere(dest, passit):
            return self.searchback()
        return None
    def searchthere(self, dest, passit):
        while not self.done:
            if not self.q.empty():
                me, x, y = self.q.get()
                for pos in [[x, y - 1], [x + 1, y], [x, y + 1], [x - 1, y]]: # tuple?
                    self.searchit(pos[0], pos[1], me + 1, dest, passit)
                    #if self.done:break
            else:
                return False
        return True
    def searchit(self, x, y, next, dest, passit):
        place = self.pole[y][x]
        #self.done = False
        if place in passit: # next to => passit = []
            self.pole[y][x] = self.mapa.znaky[next]
            self.q.put((next, x, y))
        elif place in dest:
            self.done = True
            self.destin, self.destx, self.desty = next, x, y
        #if passit == []: return self.done
    def searchback(self):
        for i in range(self.destin - 1):
            for e in [[self.destx, self.desty - 1], [self.destx + 1, self.desty], [self.destx, self.desty + 1], [self.destx - 1, self.desty]]:
                self.findback(e[0], e[1])
        return self.desty, self.destx
    def findback(self, x, y):
        place = self.pole[y][x]
        if place == self.mapa.znaky[self.destin - 1]:
            self.pole[y][x] = "X"
            self.destin, self.destx, self.desty = self.destin - 1, x, y
    def augment(self, znak, close = False): # Just for Sheep so far
        for obj in self.opposites:
            if abs(self.x - obj.x) + abs(self.y - obj.y) == 1:
                if close:
                    return True
                self.hungry, obj.hungry = self.hungry - values.Sheep_rp_food_consume, obj.hungry - values.Sheep_rp_food_consume
                self.priority, obj.priority = ["eat"]*2
                self.mapa.add(Sheep_baby(self.y, self.x, self.mapa.ID, self.mapa))
                return
    def evolve(self):
        if self.znak == "s":
            if self.evolution == values.Sheep_baby_evolution:
                self.mapa.objs.remove(self)
                self.mapa.add(Sheep(self.y, self.x, self.mapa.ID, self.mapa))
            elif randint(1, values.Sheep_baby_evolution_chance) == values.Sheep_baby_evolution_chance:
                self.evolution += 1
                for i in range(values.Sheep_baby_evolution_cost):
                    self.hunger()


class Dog(Sprite):
    def __init__(self, y, x, ID, mapa):
        super().__init__("D", y, x, mapa, "dog.png")
        self.ID = ID
        self.food = values.Dog_corpse_food
        self.hungry = values.Dog_start_food
        self.eatthat = values.Dog_eat
    def move(self):
        self.hunger()
        goto = None
        if self.priority == "eat":
            if self.eat("C", 0):
                self.eat("C", self.eatthat)
            else:
                sheeps = list(filter(lambda obj: obj.znak == "S" or obj.znak == "s", self.mapa.objs))
                corpses = self.mapa.corpses
                if len(corpses) + len(sheeps) == 0:
                    beh = randint(0, 150)
                    goto = self.runrand(beh)
                else:
                    gofor = corpses #C
                    if len(corpses) == 0:
                        gofor = sheeps #S
                    #for pos in [[self.x, self.y - 1], [self.x + 1, self.y], [self.x, self.y + 1], [self.x - 1, self.y]]:
                    #    for obj in self.mapa.objs:
                    #        if obj.x, obj.y == pos[0], pos[1]:
                    #            Don't continue
                    
                    #if do continue
                    self.closest(gofor)# from here
                    goto = self.runto()
                    if goto == None:
                        self.mapa.addc(Corpse(self.target.y, self.target.x, self.mapa, self.target.food))
                        self.mapa.objs.remove(self.target)
        else:
            beh = randint(0, 175)
            goto = self.runrand(beh)
        return goto

class Sheep(Sprite):
    def __init__(self, y, x, ID, mapa):
        super().__init__("S", y, x, mapa, "sheep.png")
        self.ID = ID
        self.food = values.Sheep_corpse_food
        self.hungry = values.Sheep_start_food
        self.eatthat = values.Sheep_eat
        self.run = 200
    def move(self):
        self.hunger()
        goto = None
        if self.priority == "eat":
            if self.eat(".", 0):
                self.eat(".", self.eatthat)
                goto = True
            else:
                gofor = self.mapa.grass#
                if len(gofor) != 0:
                    goto = self.search(["."], [" "])#
        elif self.priority == "augment":
            self.opposites = list(filter(lambda obj: obj.znak == "S" and obj.priority == "augment" and self.ID != obj.ID, self.mapa.objs))
            if len(self.opposites) > 0:
                if self.augment("S", True):
                    self.augment("S")
                else:
                    goto = self.search([opp.znak + str(opp.ID) for opp in self.opposites], [" ", "."]) #format
        if goto == True:
            goto = None
        elif goto == None:
            beh = randint(0, self.run)
            goto = self.runrand(beh)
        return goto

class Sheep_baby(Sprite):
    def __init__(self, y, x, ID, mapa):
        super().__init__("s", y, x, mapa, "sheep_baby.png")
        self.ID = ID
        self.food = values.Sheep_baby_corpse_food
        self.hungry = values.Sheep_baby_start_food
        self.eatthat = values.Sheep_baby_eat
        self.run = 200
        self.evolution = 0
    def move(self):
        self.hunger()
        goto = None
        if self.priority == "eat":
            if self.eat(".", 0):
                self.eat(".", self.eatthat)
                goto = True
            else:
                gofor = self.mapa.grass#
                if len(gofor) != 0:
                    goto = self.search(["."], [" "])#
        elif self.priority == "evolve":
            self.evolve()
            beh = randint(0, 125) ##
            goto = self.runrand(beh)
        if goto == True:
            goto = None
        elif goto == None:
            beh = randint(0, self.run)
            goto = self.runrand(beh)
        return goto

class Corpse(Sprite):
    def __init__(self, y, x, mapa, food):
        super().__init__("C", y, x, mapa, "corpse.png")
        self.food = food
    def move(self):
        if self.food == 0:
            self.mapa.corpses.remove(self)
        return None

class Grass(Sprite):
    def __init__(self, y, x, mapa):
        super().__init__(".", y, x, mapa, "grass.png")
        self.food = values.Grass_food
    def move(self):
        if self.food == 0:
            self.mapa.grass.remove(self)
        else:
            if self.food < values.Grass_max:
                self.food += values.Grass_grow
                if self.food > values.Grass_max:
                    self.food = values.Grass_max
        return None

class Stone(Sprite):
    def __init__(self, y, x, mapa):
        super().__init__("@", y, x, mapa, "stone.png")

class Run():
    def __init__(self, version, Map = Map, Dog = Dog, Grass = Grass, Stone = Stone, values= values):
        global ver
        ver = version

        mapa = Map(values.map_x, values.map_y)

        for i in range(values.Dogs):
            mapa.add(Dog(randint(1, mapa.x-2), randint(1, mapa.y -2), mapa.ID, mapa))
            
        for i in range(values.Sheep):
            mapa.add(Sheep(randint(1, mapa.x-2), randint(1, mapa.y -2), mapa.ID, mapa))

        for i in range(values.Sheep_baby):
            mapa.add(Sheep_baby(randint(1, mapa.x-2), randint(1, mapa.y -2), mapa.ID, mapa))
            
        for i in range(values.Grass):
            mapa.addg(Grass(randint(1, mapa.x-2), randint(1, mapa.y -2), mapa))

        for i in range(mapa.y):
            mapa.adds(Stone(0, i, mapa))
            mapa.adds(Stone(mapa.x - 1, i, mapa))
        for i in range(1, mapa.x - 1):
            mapa.adds(Stone(i, 0, mapa))
            mapa.adds(Stone(i, mapa.y - 1, mapa))


        mapa.update()
        mapa.draw()
        sleep(1.5)
        go = True
        while go:
        #    a = time()
            if ver == "graphic":
                pygame.time.Clock().tick(values.FPS)
            elif ver == "text":
                wait = time()
            mapa.update()
            mapa.draw() # add FPS and dropped FPS
            if ver == "graphic":
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        go = False
                    elif event.type == pygame.QUIT:
                        #print("Thanks for using!")
                        #sleep(2)
                        sys.exit()
            elif ver == "text":
                waitfor = 0.1 + time() - wait
                if waitfor > 0:
                    sleep(waitfor)
        #    print(time.time() - a)
