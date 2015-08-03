from random import randint
from time import sleep
import queue
import values
import pygame

pygame.init()
screen = pygame.display.set_mode((values.map_x * 12, values.map_y * 8))
pygame.display.set_caption("Dogs&Sheeps")
#pygame.display.set_icon(pygame.image.load("pic/corpse.png")) #Later, I don't want to do it now...
bg_color=(0,0,0)

class Map():
    def __init__(self, y, x):
        self.x, self.y = x, y
        self.objs, self.corpses, self.grass, self.stone, self.ID = [], [], [], [], 0
        self.wait = randint(1, 10)
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

        screen.fill(bg_color)
        pole = []
        for i in range(x):
            pole.append([])
            pole[i].extend([" "]*y)
        
        for obj in self.grass:
            obj.rect.topleft = (obj.x*12, obj.y*8)
            screen.blit(obj.img, obj.rect)
            
        for obj in self.stone + self.corpses:
            obj.rect.topleft = (obj.x*12, obj.y*8)
            screen.blit(obj.img, obj.rect)

        for obj in self.objs: #str(obj.ID)
            obj.rect.topleft = (obj.x*12, obj.y*8)
            screen.blit(obj.img, obj.rect)
        
        for i in range(x): # still needed for searching
            pole[i] = "".join(pole[i])
        pole = "\n".join(pole)

        pygame.display.update()
    def update(self):
        for obj in self.objs + self.grass + self.corpses:
            obj.update()
        self.wait -= 1
        if self.wait == 0:
            self.wait = randint(1, 10)
            self.addg(Grass(randint(1, self.x - 2), randint(1, self.y - 2), self))
        
class Sprite():
    def __init__(self, znak, y, x, mapa, image):
        self.y, self.x = y, x
        self.znak = znak
        self.mapa = mapa
        self.hungry = 50
        self.priority = "eat"
        self.img = pygame.image.load("pic/"+image).convert_alpha()
        self.rect = self.img.get_rect()
    def move(self):
        pass            
    def closest(self, ents):
        far = mapa.x * mapa.y
        for i in range(len(ents)):
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
        self.hungry -= 2
        if self.hungry <= 0:
            self.mapa.addc(Corpse(self.y, self.x, mapa, self.food))
            self.mapa.objs.remove(self)
        elif self.hungry < 250:
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
                if self.hungry >= 350:
                    self.priority = "augment"
                return
    def validate(self, goto):
        gut = True
        for obj in self.mapa.objs + self.mapa.corpses + self.mapa.stone:
            if goto[0] == obj.x and goto[1] == obj.y:
                gut = False
        return gut
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
            self.pole.append([])
            self.pole[i].extend([" "]*self.mapa.x)
        for obj in self.mapa.grass:
            self.pole[obj.x][obj.y] = obj.znak
        for obj in self.mapa.stone + self.mapa.corpses:
            self.pole[obj.x][obj.y] = obj.znak
        for obj in self.mapa.objs:
            self.pole[obj.x][obj.y] = obj.znak + str(obj.ID)
        self.pole[self.x][self.y] = "$"
        if self.searchthere(dest, passit):
            return self.searchback()
        return None
    def searchthere(self, dest, passit):
        while not self.done:
            if not self.q.empty():
                me, x, y = self.q.get()
                for pos in [[x, y - 1], [x + 1, y], [x, y + 1], [x - 1, y]]:
                    self.searchit(pos[0], pos[1], me + 1, dest, passit)
            else:
                return False
        return True
    def searchit(self, x, y, next, dest, passit):
        place = self.pole[y][x]
        if place in passit:
            self.pole[y][x] = self.mapa.znaky[next]
            self.q.put((next, x, y))
        elif place in dest:
            self.done = True
            self.destin, self.destx, self.desty = next, x, y
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
    def augment(self, znak, close = False):
        for obj in self.opposites:
            if abs(self.x - obj.x) + abs(self.y - obj.y) == 1:
                if close:
                    return True
                self.hungry, obj.hungry = self.hungry - 200, obj.hungry - 200
                self.priority, obj.priority = ["eat"]*2
                mapa.add(Sheep(self.y, self.x, self.mapa.ID, mapa))
                return

class Dog(Sprite):
    def __init__(self, y, x, ID, mapa):
        super().__init__("D", y, x, mapa, "dog.png")
        self.ID = ID
        self.food = 20
        self.hungry = 100
    def move(self):
        self.hunger()
        goto = None
        if self.priority == "eat":
            if self.eat("C", 0):
                self.eat("C", 10)
            else:
                sheeps = list(filter(lambda obj: obj.znak == "S", self.mapa.objs))
                corpses = self.mapa.corpses
                if len(corpses) + len(sheeps) == 0:
                    beh = randint(0, 150)
                    goto = self.runrand(beh)
                else:
                    gofor = corpses
                    if len(corpses) == 0:
                        gofor = sheeps
                    self.closest(gofor)
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
        self.food = 400
        self.eatthat = 5
        self.run = 200
    def move(self):
        self.hunger()
        goto = None
        if self.priority == "eat":
            if self.eat(".", 0):
                self.eat(".", self.eatthat)
                goto = True
            else:
                gofor = self.mapa.grass
                if len(gofor) != 0:
                    goto = self.search(["."], [" "])
        elif self.priority == "augment":
            self.opposites = list(filter(lambda obj: obj.znak == "S" and obj.priority == "augment" and self.ID != obj.ID, self.mapa.objs))
            if len(self.opposites) > 0:
                if self.augment("S", True):
                    self.augment("S")
                else:
                    goto = self.search([opp.znak + str(opp.ID) for opp in self.opposites], [" ", "."])
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
        self.food = 5
    def move(self):
        if self.food == 0:
            self.mapa.grass.remove(self)
            return None
        else:
            self.food += 1
            return None

class Stone(Sprite):
    def __init__(self, y, x, mapa):
        super().__init__("@", y, x, mapa, "stone.png")

mapa = Map(values.map_x, values.map_y)

for i in range(values.Dogs):
    mapa.add(Dog(randint(1, mapa.x-2), randint(1, mapa.y -2), mapa.ID, mapa))
    
for i in range(values.Sheep):
    mapa.add(Sheep(randint(1, mapa.x-2), randint(1, mapa.y -2), mapa.ID, mapa))
    
for i in range(values.Grass):
    mapa.addg(Grass(randint(1, mapa.x-2), randint(1, mapa.y -2), mapa))

for i in range(mapa.y):
    mapa.adds(Stone(0, i, mapa))
    mapa.adds(Stone(mapa.x - 1, i, mapa))
for i in range(1, mapa.x - 1):
    mapa.adds(Stone(i, 0, mapa))
    mapa.adds(Stone(i, mapa.y -1, mapa))


mapa.update()
mapa.draw()
sleep(1.5)
while True:
#    a = time.time()
    pygame.time.Clock().tick(values.FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            sys.exit()
    mapa.update()
    mapa.draw() # add FPS and dropped FPS
#    print(time.time() - a)
