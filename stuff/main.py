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
	def __init__(self, height, width): #y, x is right
		self.x, self.y = width, height
		if ver == "graphic":
			pygame.init()
			self.screen = pygame.display.set_mode((self.x * 12, self.y * 8))
			pygame.display.init() # is it needed?
			self.bg_color=(0,0,0)

			self.track = {}
			for t in ["01", "02", "03", "12", "13", "23", "target"]:
				self.track[t] = pygame.image.load("stuff/pic/track_{}.png".format(t)).convert_alpha()
		self.objs, self.corpses, self.grass, self.stone, self.ID = [], [], [], [], 0
		self.colouring = None
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

		pole = [[" "]*x for i in range(y)]

		if ver == "graphic":
			self.screen.fill(self.bg_color)

			if self.colouring != None:
				self.draw_path(self.colouring)
				self.colouring = None

			for obj in self.grass:
				obj.rect.topleft = (obj.y*12, obj.x*8)
				self.screen.blit(obj.img, obj.rect)
			
			for obj in self.objs + self.stone + self.corpses: #str(obj.ID)
				obj.rect.topleft = (obj.y*12, obj.x*8)
				self.screen.blit(obj.img, obj.rect)

			pygame.display.update()
			
		elif ver == "text":
			for obj in self.grass:
				pole[obj.x][obj.y] = obj.znak
			
			for obj in self.stone + self.corpses + self.objs:
				pole[obj.x][obj.y] = obj.znak # if objs: str(obj ID)
			
			for row in range(y):
				pole[row] = "".join(pole[row])
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
	def get_objs_by_position(self, pos):
		to_return = []
		for obj in self.objs:
			if obj.x == pos[0] and obj.y == pos[1]:
				to_return.append(obj)
		return to_return
	def draw_path(self, path):
		if len(path) == 0:
			return None
		self.screen.blit(self.track["target"], (path[0][0]*12, path[0][1]*8))
		for p in range(len(path) - 2):
			to_directions = (path[p][0] - path[p+1][0], path[p][1] - path[p+1][1])
			from_directions = (path[p+1][0] - path[p+2][0], path[p+1][1] - path[p+2][1])
			#0: (0, -1) 1: (1, 0) 2: (0, 1) 3: (-1, 0)
			if ((from_directions, to_directions) == ((0, 1), (1, 0))) or ((from_directions, to_directions) == ((-1, 0), (0, -1))):
				track = self.track["01"] #01
			elif ((from_directions, to_directions) == ((0, 1), (0, 1))) or ((from_directions, to_directions) == ((0, -1), (0, -1))):
				track = self.track["02"] #02
			elif ((from_directions, to_directions) == ((0, 1), (-1, 0))) or ((from_directions, to_directions) == ((1, 0), (0, -1))):
				track = self.track["03"] #03
			elif ((from_directions, to_directions) == ((-1, 0), (0, 1))) or ((from_directions, to_directions) == ((0, -1), (1, 0))):
				track = self.track["12"] #12
			elif ((from_directions, to_directions) == ((1, 0), (1, 0))) or ((from_directions, to_directions) == ((-1, 0), (-1, 0))):
				track = self.track["13"] #13
			elif ((from_directions, to_directions) == ((0, -1), (-1, 0))) or ((from_directions, to_directions) == ((1, 0), (0, 1))):
				track = self.track["23"] #23
			self.screen.blit(track, (path[p+1][0]*12, path[p+1][1]*8))

class Sprite():
	def __init__(self, znak, y, x, mapa, image):
		self.y, self.x = y, x
		self.znak = znak
		self.mapa = mapa
		self.path = []
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
		elif (self.znak == "S" and self.hungry < values.Sheep_I_am_hungry) or (self.znak == "s" and self.hungry < values.Sheep_baby_I_am_hungry) or (self.znak == "D" and self.hungry < values.Dog_I_am_hungry):
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
		for obj in self.mapa.objs + self.mapa.corpses + self.mapa.stone:
			if goto[0] == obj.x and goto[1] == obj.y:
				return False
		return True
	def update(self):
		newpos = self.move()
		if newpos == None:
			pass
		elif self.validate(newpos) == True:
			self.x, self.y = newpos

	#The begining of searching
	#TODO"search":
	#Change it so that it searches intelligently towards the nearest object and check if some other could be theoretically closer, but CHOOSE the closest object
	def search(self, dest, passit):
		self.q, self.done, self.znaky, self.index = queue.Queue(), False, ["A"], 0
		self.q.put((0, self.y, self.x))
		self.pole = [[" "]*self.mapa.x for i in range(self.mapa.y)]
		for obj in self.mapa.grass:
			self.pole[obj.x][obj.y] = obj.znak
		for obj in self.mapa.stone + self.mapa.corpses:
			self.pole[obj.x][obj.y] = obj.znak
		for obj in self.mapa.objs:
			self.pole[obj.x][obj.y] = "{}{}".format(obj.znak, str(obj.ID)) # TODO: instead look what is at the tile they found (and choose from these objs)
		self.pole[self.x][self.y] = "$" #is $ needed?
		self.path = []
		if self.searchthere(dest, passit):
			return self.searchback()
		return None
	def searchthere(self, dest, passit):
		while not self.done:
			if not self.q.empty():
				me, x, y = self.q.get()
				for pos in ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)):
					self.searchit(pos[0], pos[1], me + 1, dest, passit)
					if self.done:
						break
			else:
				return False
		return True
	def searchit(self, x, y, next, dest, passit):
		place = self.pole[y][x]
		if place in passit: # next to => passit = []
			self.pole[y][x] = self.mapa.znaky[next]
			self.q.put((next, x, y))
		elif place in dest:
			self.path.append((x, y))
			self.done = True
			self.destin, self.destx, self.desty = next, x, y #TODO"path": check x, y for objects and save targeted object as self.path_target
			#TODO
			#for obj in grass+corpses+objects: # if self.target mark == ".": grass; if self.target mark =="s", or "S" or "C": corpses + objects
				#if x,y are right and obj.mark_on_map in dest:
					#self.path_target = obj
	def searchback(self):
		#self.path_boolean = True
		for i in range(self.destin - 1):
			for e in ((self.destx, self.desty - 1), (self.destx + 1, self.desty), (self.destx, self.desty + 1), (self.destx - 1, self.desty)):
				self.findback(e[0], e[1])
		#for PP

		#x, y = self.mapa.x, self.mapa.y
		#for row in range(y):
		#	for point in range(x):
		#		if len(self.pole[row][point]) > 1:
		#			self.pole[row][point] = self.pole[row][point][0]
		#self.pole_print = []
		#for row in self.pole:
		#	self.pole_print.append("".join(row))
		##print("\n".join(self.pole_print))

		#end for PP
		return self.desty, self.destx
	def findback(self, x, y):
		place = self.pole[y][x]
		if place == self.mapa.znaky[self.destin - 1]:
			#TODO"path": MAYBE let run the last layer (7th for example) and save ALL possible patches, then sheep will run the ones that have most same tiles and cut off if any is not validated
			#BUT it may be slower than search from begining for new path if current is interupted
			self.pole[y][x] = "X"
			self.path.append((x, y))
			self.destin, self.destx, self.desty = self.destin - 1, x, y
	#End of searching
	#BETTER searching
	def b_search(self, targets, ignore, pole = False, targets_used = []):
		#set variables
		#self.targets, self.ignore = targets, ignore
		q = queue.Queue()
		q.put((0, self.x, self.y))
		if not pole:
			self.pole = [[" "]*self.mapa.x for i in range(self.mapa.y)]
			for obj in self.mapa.grass:
				self.pole[obj.x][obj.y] = obj.znak
			for obj in self.mapa.stone + self.mapa.corpses + self.mapa.objs:
				self.pole[obj.x][obj.y] = obj.znak
		else:
			self.pole = pole
		#set target
		target_closest = None
		distance = self.mapa.x * self.mapa.y#distance, distance_previous = [self.mapa.x * self.mapa.y]*2
		targets_possible = self.mapa.grass + self.mapa.corpses + self.mapa.objs
		for e in targets_used:
			if e in targets_possible:
				del targets_possible[targets_possible.index(e)]
		for tar in targets_possible: #filter instead of if znak
			if tar.znak in self.targets:
				dist = abs(self.x - tar.x) + abs(self.y - tar.y)
				if dist < distance:
					distance = dist #distance, distance_previous = dist, distance
					target_closest = tar
		if target_closest == None:
			return None
		#search
		#Take the places that are closest (dist) to target and put the +1 all around them, then mark them as used. In next cycle the closest only will be choosen to do it`s thing. If no new places are created and the target is still not found then use the ones not marked as used.
		walked = 0
		while True:
			me, x, y = q.get()
			for xy in ((x, y-1), (x+1, y), (x, y+1), (x-1, y)):
				dist = abs(target_closest.x - xy[0]) + abs(target_closest.y - xy[1])
			walked += 1
					
		#if self.searchthere(dest, passit):
		#	return self.searchback()
		#return None
	#end of BETTER searching

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
	food = values.Dog_corpse_food
	eatthat = values.Dog_eat
	def __init__(self, y, x, ID, mapa):
		super().__init__("D", y, x, mapa, "dog.png")
		self.ID = ID
		self.hungry = values.Dog_start_food
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
					if len(corpses) == 0: #TODO: and if corpses are too far relative to sheep
						gofor = sheeps #S
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
	food = values.Sheep_corpse_food
	eatthat = values.Sheep_eat
	run = 200
	def __init__(self, y, x, ID, mapa):
		super().__init__("S", y, x, mapa, "sheep.png")
		self.ID = ID
		self.hungry = values.Sheep_start_food
		#self.path_boolean = False #just self.path_target == None?
		#self.path_target = None
	def move(self):
		self.hunger()
		goto = None
		if self.priority == "eat":
			if self.eat(".", 0):
				self.eat(".", self.eatthat)
				goto = True
			else:
				#if self.path_boolean:
				gofor = self.mapa.grass#
				if len(gofor) != 0:
					#TODO"path":
					#validate that the self.path_target exist
					#validate() each of path steps
					#check for closer <grass> than len(self.path_list)
					#!!!no list of banned <grass> (because of moving objects)
					#go by self.path[-1]
				#if not self.path_boolean:
					goto = self.search(["."], [" "]) #TODO"path": replace that
		elif self.priority == "augment":
			self.opposites = list(filter(lambda obj: obj.znak == "S" and obj.priority == "augment" and self.ID != obj.ID, self.mapa.objs))
			if len(self.opposites) > 0:
				if self.augment("S", True):
					self.augment("S")
				else:
					#TODO"path":
					#new path finding will work with different rules
					#they will find a path, check if there is theoretical shorter path, then one of them will remember it, the second one will use it as well,
					#one from one side of the list, the other from the other
					#that means that there will be "love" and they might start to augment later if they find a partner AND they will already know how much the path will take them,
					#if one don't want to risk low food supply, then the "love" is canceled and the second one might find another partner if he has enough food
					goto = self.search([opp.znak + str(opp.ID) for opp in self.opposites], [" ", "."]) #format
		if goto == True:
			goto = None
		elif goto == None:
			beh = randint(0, self.run)
			goto = self.runrand(beh)
		return goto

class Sheep_baby(Sprite):
	food = values.Sheep_baby_corpse_food
	eatthat = values.Sheep_baby_eat
	run = 200
	def __init__(self, y, x, ID, mapa):
		super().__init__("s", y, x, mapa, "sheep_baby.png")
		self.ID = ID
		self.hungry = values.Sheep_baby_start_food
		self.evolution = 0
		#self.path_boolean = False #just self.path_target == None?
		#self.path_target = None
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

		mapa = Map(values.map_height, values.map_width)

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
		wait = time()
		paused = False
		#for PP
		#i = 0
		#end for PP
		while go:
			#TODO"stats":hower over (write "Sheep n.8") to show stats(food, path, priority... everything)
			#for PP
			#i += 1
			#if i % 100 == 0:
			#	print(i)
			#	go = False
			#end for PP
		#	a = time()
			if ver == "graphic" and values.FPS > 0:
				pygame.time.Clock().tick(values.FPS)
			elif ver == "text" and values.FPS > 0:
				wait = time()
			if not paused or one_more_frame:
				mapa.update()
			mapa.draw() # add FPS
			if ver == "graphic":
				one_more_frame = False
				pos = pygame.mouse.get_pos()
				pos = (int(pos[0]/12), int(pos[1]/8))
				objs = mapa.get_objs_by_position((pos[1], pos[0]))
				for obj in objs:
					if obj.znak == "S" or "s": #or "D"
						mapa.colouring = obj.path

				for event in pygame.event.get():
					if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
						go = False
					elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
						if paused:
							paused = False
						else:
							paused = True
					elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
						one_more_frame = True
					elif event.type == pygame.QUIT:
						#print("Thanks for using!")
						#sleep(2)
						sys.exit()

			elif ver == "text" and values.FPS > 0:
				wait = time()
				waitfor = 1/values.FPS + time() - wait
				if waitfor > 0:
					sleep(waitfor)
		#	print(time.time() - a)
		#if go == False:
		#	save and such
