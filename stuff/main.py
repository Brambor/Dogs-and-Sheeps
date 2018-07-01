import heapq
import random
from time import sleep, time
import queue
import sys

from stuff import values

try:
	import pygame
except ImportError:
	pass

class PathFound(Exception):
	pass

class OppositeExists(Exception):
	pass

class OppositeNotFound(Exception):
	pass

class Map():
	def __init__(self, height, width): #y, x is right
		self.x, self.y = width, height
		if ver == "graphic":
			pygame.init()
			self.screen = pygame.display.set_mode((self.x * 12, self.y * 8))
			self.bg_color=(0,0,0)

			self.track = {}
			for t in ["01", "02", "03", "12", "13", "23", "cross", "target"]:
				self.track[t] = pygame.image.load("stuff/pic/track_{}.png".format(t)).convert_alpha()
		self.corpses, self.grass, self.stone, self.ID = [], [], [], 0
		self.sheep, self.sheep_babies, self.dogs = [], [], []
		self.colouring = None
		self.last_colouring = (None, None)
		self.wait = random.randint(*values.Grass_spawn_rate)
	def add_sheep(self, obj):
		self.sheep.append(obj)
		self.ID += 1
	def add_sheep_baby(self, obj):
		self.sheep_babies.append(obj)
		self.ID += 1
	def add_dog(self, obj):
		self.dogs.append(obj)
		self.ID += 1
	def addc(self, obj):
		self.corpses.append(obj)
	def addg(self, obj):
		self.grass.append(obj)
	def adds(self, obj):
		self.stone.append(obj)
	def draw(self, frame=1):

		if ver == "graphic":
			self.screen.fill(self.bg_color)

			if self.colouring != None:
				for obj in self.colouring:
					self.draw_path(obj)
					self.last_colouring = (self.colouring, self.tick)
				self.colouring = None

			for obj in self.sheep + self.sheep_babies:
				if obj.selected:
					self.draw_path(obj)
			
			# <- on top <-
			for obj in self.grass + self.stone + self.corpses:
				obj.rect.topleft = (obj.y*12, obj.x*8)
				self.screen.blit(obj.img, obj.rect)
			
			for obj in self.sheep + self.sheep_babies + self.dogs:
				if obj.last_pos == None:
					obj.rect.topleft = (obj.y*12, obj.x*8)
					self.screen.blit(obj.img, obj.rect)
				else: #Smooth mooving
					obj.rect.topleft = ( (obj.last_pos[1] + (obj.y - obj.last_pos[1])/values.FPU) *12, (obj.last_pos[0] + (obj.x - obj.last_pos[0])/values.FPU) *8 )
					self.screen.blit(obj.img, obj.rect)

			pygame.display.update()
			
		elif ver == "text":

			x, y = self.x, self.y
			pole = [[" "]*x for i in range(y)]

			for obj in self.grass + self.stone + self.corpses + self.sheep + self.sheep_babies + self.dogs:
				pole[obj.x][obj.y] = obj.znak
			
			for row in range(y):
				pole[row] = "".join(pole[row])
			pole = "\n".join(pole)
			print()
			print(pole, end = "")

	def update(self):
		# -> order -> (Sheep are always first)
		for obj in self.sheep + self.sheep_babies + self.dogs + self.grass + self.corpses:
			obj.update()
		self.wait -= 1
		if self.wait == 0:
			self.wait = random.randint(*values.Grass_spawn_rate)
			self.addg(Grass(random.randint(1, self.x - 2), random.randint(1, self.y - 2), self)) # idea: grass should not be spawning on occupied tiles
	def get_impassable_objects(self):
		return self.sheep + self.sheep_babies + self.dogs + self.corpses + self.stone
	def get_all_sheep_pathes(self):
		to_return = set()
		for obj in self.sheep + self.sheep_babies:
			if obj.path_exists:
				for p in obj.path:
					to_return.add(p)
		return to_return
	def draw_path(self, obj):
		path = obj.path + [(obj.x, obj.y)]
		if obj.last_pos != None:
			path += [obj.last_pos]
			used_last_pos = True
		else:
			used_last_pos = False
		if len(path) < 2 + used_last_pos:
			return None
		path = [(p1, p0) for p0, p1 in path]

		self.screen.blit(self.track["cross"], (path[0][0]*12, path[0][1]*8))
		for p in range(len(path) - 2):
			to_directions = (path[p][0] - path[p+1][0], path[p][1] - path[p+1][1])
			from_directions = (path[p+1][0] - path[p+2][0], path[p+1][1] - path[p+2][1])
			#0: (0, -1) 1: (1, 0) 2: (0, 1) 3: (-1, 0)
			matrix = (
				((0, 1), (1, 0)), ((-1, 0), (0, -1)),
				((0, 1), (0, 1)), ((0, -1), (0, -1)),
				((0, 1), (-1, 0)), ((1, 0), (0, -1)),
				((-1, 0), (0, 1)), ((0, -1), (1, 0)),
				((1, 0), (1, 0)), ((-1, 0), (-1, 0)),
				((0, -1), (-1, 0)), ((1, 0), (0, 1)),
			)
			try:
				track = self.track[
					("01", "02", "03", "12", "13", "23")[
						int(matrix.index((from_directions, to_directions))/2)
					]
				]
			except ValueError:
				from stuff.crash_catcher import write_log_file, send_mail
				print("\n\nSomething happened and we wrote a log file,")
				print("\nseed:{seed}\ntick:{tick}".format(seed = self.seed, tick = self.tick))
				path_to_file = write_log_file(self.seed, self.tick, False)
				send_mail(path_to_file, False)
				return None

			self.screen.blit(track, (path[p+1][0]*12, path[p+1][1]*8))

class Sprite():
	def __init__(self, znak, y, x, mapa, image):
		self.y, self.x = y, x
		self.znak = znak
		self.mapa = mapa
		self.path = []
		self.priority = "eat"
		self.selected = False
		self.last_pos = None
		if ver == "graphic":
			self.img = pygame.image.load("stuff/pic/{}".format(image)).convert_alpha()
			self.rect = self.img.get_rect()
	def move(self):
		pass
	def closest(self, ents):
		self.target = ents[min((abs(self.x - ent.x) + abs(self.y - ent.y), i) for i, ent in enumerate(ents))[1]]
	def get_distance_from(self, thing, target):
		return abs(thing[0] - target.x) + abs(thing[1] - target.y)
	def get_shortest_distance_from(self, thing, targets):
		return min(abs(thing[0] - target[0]) + abs(thing[1] - target[1]) for target in targets)
	def get_objs_by_position(self, objs, pos):
		to_return = set()
		for obj in objs:
			if obj.x == pos[0] and obj.y == pos[1]:
				to_return.add(obj)
		return to_return
	def get_opposites(self):
		return set(filter(lambda obj: obj.priority == "augment" and self.ID != obj.ID, self.mapa.sheep))
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
			if self.znak == "S":
				self.mapa.sheep.remove(self)
			elif self.znak == "s":
				self.mapa.sheep_babies.remove(self)
			elif self.znak == "D":
				self.mapa.dogs.remove(self)
		elif (self.znak == "S" and self.hungry < values.Sheep_I_am_hungry) or (self.znak == "s" and self.hungry < values.Sheep_baby_I_am_hungry) or (self.znak == "D" and self.hungry < values.Dog_I_am_hungry):
			self.priority = "eat"
	def eat(self, eatit):
		toeat = self.eat_per_turn
		for obj in self.mapa.corpses + self.mapa.grass:
			if abs(self.x - obj.x) + abs(self.y - obj.y) == 1 and eatit == obj.znak:
				if toeat > obj.food:
					toeat = obj.food
				obj.food -= toeat
				self.hungry += toeat
				self.am_i_full()
				return True
		return False
	def herbivore(self):
		if self.eat("."):
			return True
		else:
			if self.mapa.grass:
				if self.search_for_grass():
					return self.path.pop()
	def next_to_grass(self):
		for obj in self.mapa.grass:
			if abs(self.x - obj.x) + abs(self.y - obj.y) == 1:
				return True
	def search_for_grass(self):
		if self.path_exists:
			if self.what_i_want_to_get_to in self.mapa.grass:
				if self.path_is_not_blocked(self.path):
					if self.path_is_shortest_possible(self.mapa.grass):
						return True
		if self.find_path(self.mapa.grass, {" "}) != None:
			if self.what_i_want_to_get_to in self.mapa.grass:
				return True
		self.path = []
		self.path_exists = False
		return False
	def next_to_opposite(self, opposites):
		for obj in opposites:
			if abs(self.x - obj.x) + abs(self.y - obj.y) == 1:
				return True
	def search_for_opposite(self, opposites):
		if self.significant_other in opposites:
			if self.significant_other.significant_other == self:
				if self.path_is_not_blocked(self.path):
					if self.path_is_not_blocked(self.significant_other.path):
						if self.pathes_are_shortest_possible(opposites):
							return True
		if self.find_path(opposites, {" ", "."}, purpose="augment"):
			return True
		self.path = []
		self.path_exists = False
		return False

	def validate(self, goto):
		for obj in self.mapa.sheep + self.mapa.sheep_babies + self.mapa.dogs + self.mapa.corpses + self.mapa.stone:
			if goto[0] == obj.x and goto[1] == obj.y:
				return False
		return True
	def update(self):
		self.last_pos = (self.x, self.y)
		newpos = self.move()
		if newpos == None:
			pass #for objects like corpses and grass that doesn't move
		elif self.validate(newpos):
			self.x, self.y = newpos
	def find_path(self, valid_targets, passable, purpose = "eat"):
		targets = set((target.x, target.y) for target in valid_targets)
		valid_targets = set(valid_targets)

		a_star_path = []
		heapq.heapify(a_star_path)
		heapq.heappush(a_star_path, (0, 0, (self.x, self.y) ))

		marked_map = [[" "]*self.mapa.x for i in range(self.mapa.y)]
		for obj in self.mapa.get_impassable_objects():
			marked_map[obj.x][obj.y] = "#"
		for target in valid_targets:
			marked_map[target.x][target.y] = "&"
		marked_map[self.x][self.y] = "$"

		try:
			while a_star_path:
				source = heapq.heappop(a_star_path)
				next_step = -source[1] +1
				ghost = source[2]
				for offset in ((1,0), (0,1), (-1,0), (0,-1)):
					next_tile = (ghost[0] + offset[0], ghost[1] + offset[1])
					if marked_map[next_tile[0]][next_tile[1]] == "&":
						raise PathFound
					elif marked_map[next_tile[0]][next_tile[1]] in passable:
						target_remoteness = self.get_shortest_distance_from(next_tile, targets)
						if self.validate(next_tile):
							heapq.heappush(a_star_path, (
								target_remoteness + next_step, #total_distance
								-next_step, #negative next_step for sorting
								next_tile, #(x, y)
								))
							marked_map[next_tile[0]][next_tile[1]] = next_step
			return None #if no path was found
		except PathFound:
			#prevent crossing any other sheep pathes (1st part)
			taken_tiles = self.mapa.get_all_sheep_pathes()

			self.path_exists = True
			#save target
			objs = self.get_objs_by_position(self.mapa.sheep + self.mapa.sheep_babies + self.mapa.dogs + self.mapa.grass + self.mapa.corpses, next_tile)
			self.what_i_want_to_get_to = (objs & valid_targets).pop() #TODO"optimalization":? save whole tuple (then iterate)
			if purpose == "augment":
				self.significant_other = self.what_i_want_to_get_to

				self.significant_other.path_exists = True
				self.significant_other.what_i_want_to_get_to = self
				self.significant_other.significant_other = self
			#save path
			self.path = [ghost]
			while True:
				possible_tiles = [] #set() doesn't sort, so it has to be list
				#TODO"moovement_direction": change_direction	boolean
				for offset in ((1,0), (0,1), (-1,0), (0,-1)):
					next_tile = (ghost[0] + offset[0], ghost[1] + offset[1])
					distance_from_beacon = marked_map[next_tile[0]][next_tile[1]]
					if type(distance_from_beacon) == int:
						possible_tiles.append((-distance_from_beacon, next_tile))
					elif distance_from_beacon == "$":
						break

				if distance_from_beacon == "$":
					break

				possible_tiles.sort()
				p_t = possible_tiles.pop()
				shortest_distance = p_t[0]
				possible_tiles_set = {p_t[1]}
				for t in possible_tiles:
					if t[0] == shortest_distance:
						possible_tiles_set.add(t[1])

				#prevent crossing any other sheep pathes (2nd part)
				untaken_tiles = possible_tiles_set - taken_tiles
				if len(untaken_tiles):
					ghost = untaken_tiles.pop()
				else:
					ghost = possible_tiles_set.pop()

				self.path.append(ghost)

			if purpose == "augment":
				smaller_half = len(self.path)//2
				self.significant_other.path = self.path[:smaller_half]
				self.significant_other.path.reverse()
				self.path = self.path[smaller_half:]

			return True

	def path_is_not_blocked(self, path):
		for tile in path:
			if not self.validate(tile):
				return False
		return True
	def path_is_shortest_possible(self, valid_targets):
		if len(self.path) + 1 == min(self.get_distance_from((self.x, self.y), target) for target in valid_targets):
			return True
		else:
			return False
	def pathes_are_shortest_possible(self, opposites):
		if len(self.path) + len(self.significant_other.path) + 1 == min(self.get_distance_from((self.x, self.y), oposite) for oposite in opposites):
			return True
		else:
			return False
	def augment(self, opposites):
		for obj in opposites:
			if abs(self.x - obj.x) + abs(self.y - obj.y) == 1:
				self.hungry, obj.hungry = self.hungry - values.Sheep_rp_food_consume, obj.hungry - values.Sheep_rp_food_consume
				self.priority, obj.priority = ["eat"]*2
				self.significant_other, obj.significant_other = [None]*2
				self.path, obj.path = [], []
				self.mapa.add_sheep_baby(Sheep_baby(self.y, self.x, self.mapa.ID, self.mapa))
				return True
		return False
	def evolve(self):
		if self.znak == "s":
			if self.evolution == values.Sheep_baby_evolution:
				self.mapa.sheep_babies.remove(self)
				self.mapa.add_sheep(Sheep(self.y, self.x, self.mapa.ID, self.mapa))
			elif random.randint(1, values.Sheep_baby_evolution_chance) == values.Sheep_baby_evolution_chance:
				self.evolution += 1
				for i in range(values.Sheep_baby_evolution_cost):
					self.hunger()


class Dog(Sprite):
	food = values.Dog_corpse_food
	eat_per_turn = values.Dog_eat
	stomach = values.Dog_stomach
	def __init__(self, y, x, ID, mapa):
		super().__init__("D", y, x, mapa, "dog.png")
		self.ID = ID
		self.hungry = values.Dog_start_food
	def move(self):
		self.hunger()
		goto = None
		if self.priority == "eat":
			if not self.eat("C"):
				sheeps = self.mapa.sheep + self.mapa.sheep_babies
				corpses = self.mapa.corpses
				if (not corpses) and (not sheeps):
					beh = random.randint(0, 150)
					goto = self.runrand(beh)
				else:
					gofor = corpses #C
					if not corpses: #TODO: and if corpses are too far relative to sheep
						gofor = sheeps #S
					self.closest(gofor)# from here
					goto = self.runto()
					if goto == None:
						self.mapa.addc(Corpse(self.target.y, self.target.x, self.mapa, self.target.food))
						if self.target.znak == "S":
							self.mapa.sheep.remove(self.target)
						if self.target.znak == "s":
							self.mapa.sheep_babies.remove(self.target)
		else:
			beh = random.randint(0, 175)
			goto = self.runrand(beh)
		return goto
	def am_i_full(self):
		if self.hungry >= self.stomach:
			self.priority = "augment"

class Sheep(Sprite):
	food = values.Sheep_corpse_food
	eat_per_turn = values.Sheep_eat
	run = 200
	stomach = values.Sheep_stomach
	def __init__(self, y, x, ID, mapa):
		super().__init__("S", y, x, mapa, "sheep.png")
		self.ID = ID
		self.hungry = values.Sheep_start_food
		self.path_exists = False
		self.significant_other = None
	def move(self):
		self.hunger()
		goto = None
		if self.priority == "eat":
			goto = self.herbivore()
		elif self.priority == "augment":
			opposites = self.get_opposites()
			if opposites:
				if not self.augment(opposites):
					if self.search_for_opposite(opposites):
						goto = self.path.pop()
			else:
				self.path = [] # so that path is not shown if partner isn't avaible anymore
				self.significant_other = None #and, for sure, no SO exist anymore
		if goto == True:
			return None
		elif goto == None:
			beh = random.randint(0, self.run)
			goto = self.runrand(beh)
		return goto
	def am_i_full(self):
		if self.hungry >= self.stomach:
			self.priority = "augment"

class Sheep_baby(Sprite):
	food = values.Sheep_baby_corpse_food
	eat_per_turn = values.Sheep_baby_eat
	stomach = values.Sheep_baby_stomach
	run = 200
	def __init__(self, y, x, ID, mapa):
		super().__init__("s", y, x, mapa, "sheep_baby.png")
		self.ID = ID
		self.hungry = values.Sheep_baby_start_food
		self.evolution = 0
		self.path_exists = False
	def move(self):
		self.hunger()
		goto = None
		if self.priority == "eat":
			goto = self.herbivore()
		elif self.priority == "evolve":
			self.evolve()
			beh = random.randint(0, 125) ##
			goto = self.runrand(beh)
		if goto == True:
			return None
		elif goto == None:
			beh = random.randint(0, self.run)
			goto = self.runrand(beh)
		return goto
	def am_i_full(self):
		if self.hungry >= self.stomach:
			self.priority = "evolve"

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
	def __init__(self, version):
		global ver
		ver = version

		mapa = Map(values.map_height, values.map_width)

		if values.seed == "random":
			mapa.seed = int(random.random()*10**17)
		else:
			mapa.seed = values.seed
		random.seed(mapa.seed)

		for i in range(values.Dogs):
			mapa.add_dog(Dog(random.randint(1, mapa.x-2), random.randint(1, mapa.y -2), mapa.ID, mapa))
			
		for i in range(values.Sheep):
			mapa.add_sheep(Sheep(random.randint(1, mapa.x-2), random.randint(1, mapa.y -2), mapa.ID, mapa))

		for i in range(values.Sheep_baby):
			mapa.add_sheep_baby(Sheep_baby(random.randint(1, mapa.x-2), random.randint(1, mapa.y -2), mapa.ID, mapa))
			
		for i in range(values.Grass):
			mapa.addg(Grass(random.randint(1, mapa.x-2), random.randint(1, mapa.y -2), mapa))

		for i in range(mapa.y):
			mapa.adds(Stone(0, i, mapa))
			mapa.adds(Stone(mapa.x - 1, i, mapa))
		for i in range(1, mapa.x - 1):
			mapa.adds(Stone(i, 0, mapa))
			mapa.adds(Stone(i, mapa.y - 1, mapa))


		mapa.tick = 0
		mapa.update()
		mapa.draw()
		sleep(1.5)
		go = True
		wait = time()
		paused = False
		sprite = Sprite(None, None, None, None, "stone.png")
		Clock = pygame.time.Clock()
		try:
			while go:
				if ver == "graphic" and values.UPS > 0:
					pass  # f1: get time I can spend
				elif ver == "text" and values.UPS > 0:
					wait = time()
				if not paused or one_more_frame:
					mapa.tick += 1
					mapa.update()

				for frame in range(values.FPU):  # f1: spend ALL time I can (splitted into equal parts per FPU)
					mapa.draw(frame)
					Clock.tick(values.UPS*values.FPU)
					#Clock.tick_busy_loop(values.UPS*values.FPU)
				if ver == "graphic":
					one_more_frame = False
					cursor_pos = pygame.mouse.get_pos()
					cursor_pos = (int(cursor_pos[0]/12), int(cursor_pos[1]/8))
					objs = sprite.get_objs_by_position(mapa.sheep + mapa.sheep_babies, (cursor_pos[1], cursor_pos[0]))
					for obj in objs:
						mapa.colouring = [obj]
						if obj.znak == "S":
							if obj.significant_other != None:
								mapa.colouring.append(obj.significant_other)

					for event in pygame.event.get():

						if event.type == pygame.KEYDOWN:
							if event.key == pygame.K_ESCAPE:
								go = False
							elif event.key == pygame.K_SPACE:
								if paused:
									paused = False
								else:
									paused = True
							elif event.key == pygame.K_f:
								one_more_frame = True
							elif event.key == pygame.K_a:
								for obj in mapa.sheep + mapa.sheep_babies:
									obj.selected = True
							elif event.key == pygame.K_d:
								for obj in mapa.sheep + mapa.sheep_babies:
									obj.selected = False
							elif event.key == pygame.K_t:
								for obj in mapa.sheep + mapa.sheep_babies:
									if obj.selected:
										obj.selected = False
									else:
										obj.selected = True

						if event.type == pygame.MOUSEBUTTONDOWN:
							if event.button == 1:
								for obj in objs:
									if obj.selected:
										obj.selected = False
									else:
										obj.selected = True


						elif event.type == pygame.QUIT:
							sys.exit()

				elif ver == "text" and values.UPS > 0:
					wait = time()
					waitfor = 1/values.UPS + time() - wait
					if waitfor > 0:
						sleep(waitfor)
			print("Simulation stopped at tick {tick}.".format(tick=mapa.tick))
		except SystemExit:
			raise
		except:
			from stuff.crash_catcher import write_log_file, send_mail
			if ver == "graphic":
				crash_img = pygame.image.load("stuff/pic/crash.png").convert_alpha()
				crash_rect = crash_img.get_rect()
				crash_rect.center = (values.map_width*6, values.map_height*4)
				mapa.screen.blit(crash_img, crash_rect)
				pygame.display.update()
			print("\n\nSomething happened and the program is about to crash")
			print("\nseed:{seed}\ntick:{tick}".format(seed = mapa.seed, tick = mapa.tick))
			path_to_file = write_log_file(mapa.seed, mapa.tick)
			send_mail(path_to_file)
			#input("\nPress Enter to crash")
			raise
