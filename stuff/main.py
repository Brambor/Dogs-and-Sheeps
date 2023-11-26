import heapq
import random
import sys

from itertools import chain
from time import sleep, time

from stuff import values
from stuff.crash_catcher import write_log_file

try:
	import pygame
except ImportError:
	pass


#0: (0, -1) 1: (1, 0) 2: (0, 1) 3: (-1, 0)
directions_to_filename = {
	(( 0,  1), ( 1,  0)): "01",
	((-1,  0), ( 0, -1)): "01",
	(( 0,  1), ( 0,  1)): "02",
	(( 0, -1), ( 0, -1)): "02",
	(( 0,  1), (-1,  0)): "03",
	(( 1,  0), ( 0, -1)): "03",
	((-1,  0), ( 0,  1)): "12",
	(( 0, -1), ( 1,  0)): "12",
	(( 1,  0), ( 1,  0)): "13",
	((-1,  0), (-1,  0)): "13",
	(( 0, -1), (-1,  0)): "23",
	(( 1,  0), ( 0,  1)): "23",
}


class PathFound(Exception):
	pass

class OppositeExists(Exception):
	pass

class OppositeNotFound(Exception):
	pass

class Map():
	def __init__(self, height, width):
		self.x, self.y = width, height
		if ver == "graphic":
			pygame.init()
			# pygame uses X, Y; we use Y X
			py, px = self.pos_to_pix(self.y, self.x)
			self.screen = pygame.display.set_mode((px, py))
			self.bg_color=(0,0,0)

			self.track = {}
			for t in ["01", "02", "03", "12", "13", "23", "cross", "target"]:
				self.track[t] = pygame.image.load(f"stuff/pic/track_{t}.png").convert_alpha()
		self.corpses, self.grass, self.stone, self.ID = [], [], [], 0
		self.sheep, self.sheep_babies, self.dogs = [], [], []
		self.colouring = None
		self.last_colouring = (None, None)
		self.wait = random.randint(*values.Grass_spawn_rate)

		# list for every tile storing all objects on that tile
		self.map = [
			[ [] for _ in range(self.x) ] for _ in range(self.y)
		]
		# object -> position
		self.map_positions = {}
		self.map_last_positions = {}

	def pixel_to_pos(self, y_pix, x_pix):
		return int(y_pix/8), int(x_pix/12)

	def pos_to_pix(self, y, x):
		return y * 8, x * 12

	def next_ID(self):
		r = self.ID
		self.ID += 1
		return r

	def add_sheep(self, obj, y, x):
		self.add_obj(obj, y, x)
		self.sheep.append(obj)

	def add_sheep_baby(self, obj, y, x):
		self.add_obj(obj, y, x)
		self.sheep_babies.append(obj)

	def add_dog(self, obj, y, x):
		self.add_obj(obj, y, x)
		self.dogs.append(obj)

	def add_corpse(self, obj, y, x):
		self.add_obj(obj, y, x)
		self.corpses.append(obj)

	def add_grass(self, obj, y, x):
		self.add_obj(obj, y, x)
		self.grass.append(obj)

	def add_stone(self, obj, y, x):
		self.add_obj(obj, y, x)
		self.stone.append(obj)

	def add_obj(self, obj, y, x):
		self.map[y][x].append(obj)
		self.map_positions[obj] = (y, x)

	def move_obj(self, obj, to_y, to_x):
		from_y, from_x = self.get_pos(obj)
		self.map[from_y][from_x].remove(obj)
		self.add_obj(obj, to_y, to_x)

	def remove_obj(self, obj):
		if obj.znak == "S":
			self.sheep.remove(obj)
		elif obj.znak == "s":
			self.sheep_babies.remove(obj)
		elif obj.znak == "D":
			self.dogs.remove(obj)
		elif obj.znak == "C":
			self.corpses.remove(obj)
		elif obj.znak == ".":
			self.grass.remove(obj)
		else:
			raise NotImplementedError

		from_y, from_x = self.get_pos(obj)
		self.map[from_y][from_x].remove(obj)
		self.map_positions.pop(obj)

	def draw(self, frame=1):
		if ver == "graphic":
			self.screen.fill(self.bg_color)

			if self.colouring != None:
				for obj in self.colouring:
					self.draw_path(obj)
					self.last_colouring = (self.colouring, self.tick)
				self.colouring = None

			for obj in chain(self.sheep, self.sheep_babies):
				if obj.selected:
					self.draw_path(obj)

			# <- on top <-
			for obj in chain(self.grass, self.stone, self.corpses):
				oy, ox = self.pos_to_pix(*self.get_pos(obj))
				# pygame is X Y, we are Y X
				obj.rect.topleft = (ox, oy)
				self.screen.blit(obj.img, obj.rect)

			for obj in chain(self.sheep, self.sheep_babies, self.dogs):
				if not self.has_last_pos(obj):
					# pygame is X Y, we are Y X
					oy, ox = self.pos_to_pix(*self.get_pos(obj))
					obj.rect.topleft = (ox, oy)
					self.screen.blit(obj.img, obj.rect)
				else: #Smooth mooving
					# pygame is X Y, we are Y X
					oy, ox = self.get_pos(obj)
					oly, olx = self.get_last_pos(obj)
					py, px = self.pos_to_pix((oly + (oy - oly)/values.FPU), (olx + (ox - olx)/values.FPU))
					obj.rect.topleft = (px, py)
					self.screen.blit(obj.img, obj.rect)

			pygame.display.update()

		elif ver == "text":

			x, y = self.x, self.y
			pole = [[" "]*x for i in range(y)]

			for obj in chain(self.grass, self.stone, self.corpses, self.sheep, self.sheep_babies, self.dogs):
				oy, ox = self.get_pos(obj)
				pole[oy][ox] = obj.znak

			for row in range(y):
				pole[row] = "".join(pole[row])
			pole = "\n".join(pole)
			print()
			print(pole, end = "")

	def update(self):
		# -> order -> (Sheep are always first)
		for obj in chain(self.sheep, self.sheep_babies, self.dogs, self.grass, self.corpses):
			obj.update()
		self.wait -= 1
		if self.wait == 0:
			self.wait = random.randint(*values.Grass_spawn_rate)
			self.add_grass(Grass(self), *self.get_random_pos()) # idea: grass should not be spawning on occupied tiles
	def get_impassable_objects(self):
		return chain(self.sheep, self.sheep_babies, self.dogs, self.corpses, self.stone)
	def get_all_sheep_pathes(self):
		return set(chain.from_iterable(obj.path for obj in chain(self.sheep, self.sheep_babies) if obj.path_exists))
	def get_random_pos(self, avoid_perimeter_stones=True):
		"""
		return random position on map

		ignore whether tile is occupied (with the exception of avoid_perimeter_stones)
		"""
		if avoid_perimeter_stones:
			return random.randint(1, self.y-2), random.randint(1, self.x-2)
		else:
			return random.randint(0, self.y-1), random.randint(0, self.x-1)

	def draw_path(self, obj):
		oy, ox = self.get_pos(obj)
		path = obj.path.copy()
		path.append((oy, ox))
		if self.has_last_pos(obj):
			oly, olx = self.get_last_pos(obj)
			path.append((oly, olx))
			used_last_pos = True
		else:
			used_last_pos = False
		if len(path) < 2 + used_last_pos:
			return

		path = tuple((x, y) for y, x in path)
		# pygame needs path as X Y
		self.screen.blit(self.track["cross"], (path[0][0]*12, path[0][1]*8))
		for prev_tile, cur_tile, next_tile in zip(path, path[1:], path[2:]):
			to_directions = (prev_tile[0] - cur_tile[0], prev_tile[1] - cur_tile[1])
			from_directions = (cur_tile[0] - next_tile[0], cur_tile[1] - next_tile[1])
			if (from_directions, to_directions) not in directions_to_filename:
				# this happens when obj moved to some direction
				# and now has to go the opposite direction
				# or when obj just stood in place...
				continue
			track = self.track[directions_to_filename[(from_directions, to_directions)]]

			x, y = cur_tile
			y, x = self.pos_to_pix(y, x)
			self.screen.blit(track, (x, y))

	def get_pos(self, obj):
		return self.map_positions[obj]

	def has_last_pos(self, obj):
		return obj in self.map_last_positions

	def get_last_pos(self, obj):
		return self.map_last_positions[obj]

	def set_last_pos_to_now(self, obj):
		self.map_last_positions[obj] = self.get_pos(obj)

	def tile_impassable(self, y, x):
		return any(obj.impassable for obj in self.map[y][x])

	def validate_empty(self, y, x):
		return not self.tile_impassable(y, x)

	def get_objs_by_position(self, y, x):
		return set(self.map[y][x])

	def adjacent_pos(self, position):
		for offset in ((1,0), (0,1), (-1,0), (0,-1)):
			yield (position[0] + offset[0], position[1] + offset[1])

class Sprite():
	def __init__(self, znak, mapa, image):
		self.znak = znak
		self.mapa = mapa
		self.path = []
		self.priority = "eat"
		self.selected = False
		if ver == "graphic":
			self.img = pygame.image.load(f"stuff/pic/{image}").convert_alpha()
			self.rect = self.img.get_rect()

	def move(self):
		"""Returns Y X or None"""
		pass

	def closest(self, ents):
		self.target = ents[min((self.get_distance_from(ent), i) for i, ent in enumerate(ents))[1]]

	def get_distance_from(self, target):
		sy, sx = self.mapa.get_pos(self)
		ty, tx = self.mapa.get_pos(target)
		return abs(sx - tx) + abs(sy - ty)

	def get_shortest_distance_from(self, thing, targets):
		return min(abs(thing[0] - target[0]) + abs(thing[1] - target[1]) for target in targets)

	def get_opposites(self):
		return set(obj for obj in self.mapa.sheep if obj.priority == "augment" and self.ID != obj.ID)

	def runto(self):
		"""Returns Y X or None"""
		sy, sx = self.mapa.get_pos(self)
		ty, tx = self.mapa.get_pos(self.target)
		diff_x = abs(sx - tx)
		diff_y = abs(sy - ty)
		if diff_x + diff_y == 1:
			return None
		if diff_x >= diff_y:
			if sx > tx:
				go = (0, -1)
			else:
				go = (0, 1)
		else:
			if sy > ty:
				go = (-1, 0)
			else:
				go = (1, 0)
		return (sy + go[0], sx + go[1])

	def runrand(self, beh):
		"""Returns Y X or None"""
		sy, sx = self.mapa.get_pos(self)
		if beh < 25:
			return (sy - 1, sx)
		elif 25 <= beh and beh < 50:
			return (sy, sx + 1)
		elif 50 <= beh and beh < 75:
			return (sy + 1, sx)
		elif 75 <= beh and beh < 100:
			return (sy, sx - 1)

	def hunger(self):
		"""Returns true, if self dies."""
		if self.znak == "S":
			self.hungry -= values.Sheep_hungry
		elif self.znak == "s":
			self.hungry -= values.Sheep_baby_hungry
		elif self.znak == "D":
			self.hungry -= values.Dog_hungry
		if self.hungry <= 0:
			self.die()
			return True
		elif ( (self.znak == "S" and self.hungry < values.Sheep_I_am_hungry)
			or (self.znak == "s" and self.hungry < values.Sheep_baby_I_am_hungry)
			or (self.znak == "D" and self.hungry < values.Dog_I_am_hungry)
		):
			self.priority = "eat"
		return False

	def die(self):
		self.mapa.add_corpse(Corpse(self.mapa, self.food), *self.mapa.get_pos(self))
		self.mapa.remove_obj(self)

	def eat(self, eatit):
		for pos in self.mapa.adjacent_pos(self.mapa.get_pos(self)):
			for obj in self.mapa.get_objs_by_position(*pos):
				if eatit == obj.znak:
					toeat = min(obj.food, self.eat_per_turn)
					obj.food -= toeat
					self.hungry += toeat
					self.is_stomach_filled()
					return True
		return False

	def herbivore(self):
		if self.eat("."):
			return True
		else:
			if self.mapa.grass:
				if self.search_for_grass():
					return self.path.pop()
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

	def update(self):
		self.mapa.set_last_pos_to_now(self)
		# returns X Y
		newpos = self.move()
		if newpos != None and self.mapa.validate_empty(*newpos):
			self.mapa.move_obj(self, *newpos)

	def find_path(self, valid_targets, passable, purpose = "eat"):
		targets = set(self.mapa.get_pos(target) for target in valid_targets)
		valid_targets = set(valid_targets)

		min_heap = []
		sy, sx = self.mapa.get_pos(self)
		heapq.heappush(min_heap, (0, 0, (sy, sx) ))

		marked_map = [[" "]*self.mapa.x for i in range(self.mapa.y)]
		for obj in self.mapa.get_impassable_objects():
			oy, ox = self.mapa.get_pos(obj)
			marked_map[oy][ox] = "#"
		for target in valid_targets:
			ty, tx = self.mapa.get_pos(target)
			marked_map[ty][tx] = "&"
		marked_map[sy][sx] = "$"

		try:
			while min_heap:
				source = heapq.heappop(min_heap)
				next_step = -source[1] +1
				ghost = source[2]
				for next_tile in self.mapa.adjacent_pos(ghost):
					if marked_map[next_tile[0]][next_tile[1]] == "&":
						raise PathFound
					elif marked_map[next_tile[0]][next_tile[1]] in passable:
						target_remoteness = self.get_shortest_distance_from(next_tile, targets)
						if self.mapa.validate_empty(*next_tile):
							heapq.heappush(min_heap, (
								target_remoteness + next_step, #total_distance
								-next_step, #negative next_step for sorting
								next_tile, #(y, x)
								))
							marked_map[next_tile[0]][next_tile[1]] = next_step
			return None #if no path was found
		except PathFound:
			#prevent crossing any other sheep pathes (1st part)
			taken_tiles = self.mapa.get_all_sheep_pathes()

			self.path_exists = True
			#save target
			objs = self.mapa.get_objs_by_position(*next_tile)
			# take random target I want from the target tile
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
				for next_tile in self.mapa.adjacent_pos(ghost):
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
		return all(self.mapa.validate_empty(*tile) for tile in path)

	def path_is_shortest_possible(self, valid_targets):
		return len(self.path) + 1 == min(self.get_distance_from(target) for target in valid_targets)

	def pathes_are_shortest_possible(self, opposites):
		return len(self.path) + len(self.significant_other.path) + 1 == min(self.get_distance_from(oposite) for oposite in opposites)

	def augment(self, opposites):
		for obj in opposites:
			if self.get_distance_from(obj) == 1:
				self.hungry, obj.hungry = self.hungry - values.Sheep_rp_food_consume, obj.hungry - values.Sheep_rp_food_consume
				self.priority, obj.priority = ["eat"]*2
				self.significant_other, obj.significant_other = [None]*2
				self.path, obj.path = [], []
				self.mapa.add_sheep_baby(Sheep_baby(self.mapa), *self.mapa.get_pos(self))
				return True
		return False
	def evolve(self):
		if self.znak == "s":
			if self.evolution == values.Sheep_baby_evolution:
				self.mapa.add_sheep(Sheep(self.mapa), *self.mapa.get_pos(self))
				self.mapa.remove_obj(self)
				return True
			elif random.randint(1, values.Sheep_baby_evolution_chance) == values.Sheep_baby_evolution_chance:
				self.evolution += 1
				for i in range(values.Sheep_baby_evolution_cost):
					self.hunger()
		return False

class Dog(Sprite):
	impassable = True
	food = values.Dog_corpse_food
	eat_per_turn = values.Dog_eat
	stomach = values.Dog_stomach
	def __init__(self, mapa):
		super().__init__("D", mapa, "dog.png")
		self.ID = mapa.next_ID()
		self.hungry = values.Dog_start_food
	def move(self):
		if self.hunger():
			return
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
						self.target.die()
		else:
			beh = random.randint(0, 175)
			goto = self.runrand(beh)
		return goto
	def is_stomach_filled(self):
		if self.hungry >= self.stomach:
			self.priority = "augment"

class Sheep(Sprite):
	impassable = True
	food = values.Sheep_corpse_food
	eat_per_turn = values.Sheep_eat
	run = 200
	stomach = values.Sheep_stomach
	def __init__(self, mapa):
		super().__init__("S", mapa, "sheep.png")
		self.ID = mapa.next_ID()
		self.hungry = values.Sheep_start_food
		self.path_exists = False
		self.significant_other = None
	def move(self):
		if self.hunger():
			return None
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
	def is_stomach_filled(self):
		if self.hungry >= self.stomach:
			self.priority = "augment"

class Sheep_baby(Sprite):
	impassable = True
	food = values.Sheep_baby_corpse_food
	eat_per_turn = values.Sheep_baby_eat
	stomach = values.Sheep_baby_stomach
	run = 200
	def __init__(self, mapa):
		super().__init__("s", mapa, "sheep_baby.png")
		self.ID = mapa.next_ID()
		self.hungry = values.Sheep_baby_start_food
		self.evolution = 0
		self.path_exists = False
	def move(self):
		if self.hunger():
			return None
		goto = None
		if self.priority == "eat":
			goto = self.herbivore()
		elif self.priority == "evolve":
			if self.evolve():
				return None
			beh = random.randint(0, 125) ##
			goto = self.runrand(beh)
		if goto == True:
			return None
		elif goto == None:
			beh = random.randint(0, self.run)
			goto = self.runrand(beh)
		return goto
	def is_stomach_filled(self):
		if self.hungry >= self.stomach:
			self.priority = "evolve"

class Corpse(Sprite):
	impassable = True
	def __init__(self, mapa, food):
		super().__init__("C", mapa, "corpse.png")
		self.food = food
	def move(self):
		if self.food == 0:
			self.mapa.remove_obj(self)

class Grass(Sprite):
	impassable = False
	def __init__(self, mapa):
		super().__init__(".", mapa, "grass.png")
		self.food = values.Grass_food
	def move(self):
		if self.food == 0:
			self.mapa.remove_obj(self)
		else:
			if self.food < values.Grass_max:
				self.food += values.Grass_grow
				if self.food > values.Grass_max:
					self.food = values.Grass_max

class Stone(Sprite):
	impassable = True
	def __init__(self, mapa):
		super().__init__("@", mapa, "stone.png")

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
			mapa.add_dog(Dog(mapa), *mapa.get_random_pos())

		for i in range(values.Sheep):
			mapa.add_sheep(Sheep(mapa), *mapa.get_random_pos())

		for i in range(values.Sheep_baby):
			mapa.add_sheep_baby(Sheep_baby(mapa), *mapa.get_random_pos())

		for i in range(values.Grass):
			mapa.add_grass(Grass(mapa), *mapa.get_random_pos())

		for i in range(mapa.y):
			mapa.add_stone(Stone(mapa), i, 0)
			mapa.add_stone(Stone(mapa), i, mapa.x - 1)
		for i in range(1, mapa.x - 1):
			mapa.add_stone(Stone(mapa), 0, i)
			mapa.add_stone(Stone(mapa), mapa.y - 1, i)

		mapa.tick = 0
		mapa.update()
		mapa.draw()
		sleep(1.5)
		go = True
		wait = time()
		paused = False
		if ver == 'graphic':
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
				if ver == "graphic":
					for frame in range(values.FPU):  # f1: spend ALL time I can (splitted into equal parts per FPU)
						mapa.draw(frame)
						Clock.tick(values.UPS*values.FPU)
						#Clock.tick_busy_loop(values.UPS*values.FPU)

					one_more_frame = False
					# pygame uses X, Y we use Y X
					px, py = pygame.mouse.get_pos()
					objs = tuple(obj for obj in mapa.get_objs_by_position(*mapa.pixel_to_pos(py, px))
						if obj.znak == "S" or obj.znak == "s")
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
								paused = not paused
							elif event.key == pygame.K_f:
								one_more_frame = True
							elif event.key == pygame.K_a:
								for obj in chain(mapa.sheep, mapa.sheep_babies):
									obj.selected = True
							elif event.key == pygame.K_d:
								for obj in chain(mapa.sheep, mapa.sheep_babies):
									obj.selected = False
							elif event.key == pygame.K_t:
								for obj in chain(mapa.sheep, mapa.sheep_babies):
									obj.selected = not obj.selected
						elif event.type == pygame.MOUSEBUTTONDOWN:
							if event.button == 1:
								for obj in objs:
									obj.selected = not obj.selected
						elif event.type == pygame.QUIT:
							sys.exit()

				elif ver == "text" and values.UPS > 0:
					wait = time()
					waitfor = 1/values.UPS + time() - wait
					if waitfor > 0:
						sleep(waitfor)
					mapa.draw()
			print(f"Simulation stopped at tick {mapa.tick}.")
		except SystemExit:
			raise
		except:
			if ver == "graphic":
				crash_img = pygame.image.load("stuff/pic/crash.png").convert_alpha()
				crash_rect = crash_img.get_rect()
				crash_rect.center = (values.map_width*6, values.map_height*4)
				mapa.screen.blit(crash_img, crash_rect)
				pygame.display.update()
			write_log_file(mapa.seed, mapa.tick)
			#input("\nPress Enter to crash")
			raise
