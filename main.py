from random import randint
import time
import values

class Map():
    def __init__(self, y, x):
        self.x, self.y = int(x), int(y)
        self.objs = []
        self.grass = []
        self.stone = []
        self.wait = randint(1, 10)
    def add(self, obj):
        self.objs.append(obj)
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
        
        for obj in self.grass:
            pole[obj.y][obj.x] = obj.znak
            
        for obj in self.objs + self.stone:
            pole[obj.y][obj.x] = obj.znak
        
        for i in range(x):
            pole[i] = "".join(pole[i])
        pole = "\n".join(pole)
        print(pole, end = "")
    def update(self):
        for obj in self.objs + self.grass:
            obj.update()
        self.wait -= 1
        if self.wait == 0:
            self.wait = randint(1, 10)
            self.addg(Grass(randint(1, self.x - 2), randint(1, self.y - 2), self))
        
class Sprite():
    def __init__(self, znak, y, x, mapa):
        self.y, self.x = y, x
        self.znak = znak
        self.mapa = mapa
        self.hungry = 25
        self.priority = "eat"
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
        self.hungry -= 1
        if self.hungry == 0:
            self.mapa.add(Corpse(self.y, self.x, mapa, self.food))
            self.mapa.objs.remove(self)
        elif self.hungry < 100:
            self.priority = "eat"
    def eat(self, eatit, toeat):
        for obj in self.mapa.objs + self.mapa.grass:
            if abs(self.x - obj.x) + abs(self.y - obj.y) == 1 and eatit == obj.znak:
                if toeat == 0:
                    return True
                if toeat > obj.food:
                    toeat = obj.food
                obj.food -= toeat
                self.hungry += toeat
                if self.hungry >= 200:
                    self.priority = "augment"
                return
    def validate(self, goto):
        gut = True
        for obj in self.mapa.objs + self.mapa.stone:
            if goto[0] == obj.x and goto[1] == obj.y:
                gut = False
        return gut
    def update(self):
        newpos = self.move()
        if newpos == None:
            pass
        elif self.validate(newpos) == True:
            self.x, self.y = newpos

class Dog(Sprite):
    def __init__(self, y, x, mapa):
        super().__init__("D", y, x, mapa)
        self.food = 20
    def move(self):
        self.hunger()
        goto = None
        if self.priority == "eat":
            if self.eat("C", 0):
                self.eat("C", 10)
            else:
                gofor = list(filter(lambda obj: (obj.znak == "S" or obj.znak == "C"), mapa.objs))
                if len(gofor) == 0:
                    beh = randint(0, 150)
                    goto = self.runrand(beh)
                else:
                    self.closest(gofor)
                    goto = self.runto()
                    if goto == None:
                        ox, oy = self.target.x, self.target.y
                        self.mapa.add(Corpse(oy, ox, self.mapa, self.target.food))
                        self.mapa.objs.remove(self.target)
#        print("D[" + str(self.x) + ",", str(self.y), end = "] ")
        return goto

class Sheep(Sprite):
    def __init__(self, y, x, mapa):
        super().__init__("S", y, x, mapa)
        self.food = 400
        self.eatthat = 5
        self.run = 200
    def move(self):
        self.hunger()
        if self.eat(".", 0):
            self.eat(".", self.eatthat)
            goto = None
        else:
            gofor = list(filter(lambda obj: obj.znak == ".", mapa.grass)) ### jen mapa.grass?
            if len(gofor) == 0:
                beh = randint(0, self.run)
                goto = self.runrand(beh)
            else:
                self.closest(gofor)
                go = self.runto()
                goto = (go[0], go[1])
#        print("S[" + str(self.x) + ",", str(self.y), end = "] ")
        return goto

class Corpse(Sprite):
    def __init__(self, y, x, mapa, food):
        super().__init__("C", y, x, mapa)
        self.food = food
    def move(self):
        if self.food == 0:
            self.mapa.objs.remove(self)
        return None

class Grass(Sprite):
    def __init__(self, y, x, mapa):
        super().__init__(".", y, x, mapa)
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
        super().__init__("@", y, x, mapa)

mapa = Map(values.map_x, values.map_y)

for i in range(2):
    mapa.add(Dog(randint(1, mapa.x-2), randint(1, mapa.y -2), mapa))
    
for i in range(5):
    mapa.add(Sheep(randint(1, mapa.x-2), randint(1, mapa.y -2), mapa))
    
for i in range(5):
    mapa.addg(Grass(randint(1, mapa.x-2), randint(1, mapa.y -2), mapa))

for i in range(mapa.y):
    mapa.adds(Stone(0, i, mapa))
    mapa.adds(Stone(mapa.x - 1, i, mapa))

for i in range(1, mapa.x - 1):
    mapa.adds(Stone(i, 0, mapa))
    mapa.adds(Stone(i, mapa.y -1, mapa))

mapa.update()
print()
mapa.draw()
time.sleep(1.5)
while True:
    a = time.time()
    mapa.update()
    print()
    mapa.draw()
    b = time.time()
#    print(b - a - 1/values.FPS)
    time.sleep(1/values.FPS + b - a)