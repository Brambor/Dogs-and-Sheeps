UPS = 30 #updates (or turns) per second; any natural number; 0 means as much as possible; default = 30
FPU = 4 # Frames per update (or turn); any natural number; default = 4
map_width = 119 #Map width; any natural number higher than 2; default = 60
map_height = 30 #Map height; any natural number higher than 2; default = 25
seed = 31597888809742680 #Decides what should happen when event is random such as place of generated grass, speed of Sheep_baby evolving, running while idle etc. same seeds result in identical simulations; anything, "random" means that it will be picked at random; default = "random"

Dogs = 3 #Starting numer of Dogs; any natural number; default = 2
Dog_start_food = 100 #Food that Dogs have in stomach at start; any natural number higher than 0 (because 0 means it will die immediatelly); default = 100
Dog_eat = 10 #How much can Dogs eat per one turn; any natural number higher than 0; default = 10
Dog_stomach = 350 #Maximum food it can have in stomach() - at maximum they will try to reproduce once it will be added); any natural number higher than 0; default = 350
Dog_I_am_hungry = 250 #Limit on wich they don't try to reproduce but eat; any natural number; default = 250
Dog_hungry = 2 #How much food will it use per one turn; any natural number (even 0); default = 2
Dog_corpse_food = 20 #How much food will be in corpse from Dog; any natural number; default = 20

Sheep = 24 #Starting numer of Sheep; any natural number; default = 12
Sheep_start_food = 50 #Food that Sheep have in stomach at start; any natural number higher than 0 (because 0 means it will die immediatelly); default = 50
Sheep_eat = 5 #How much can Sheep eat per one turn; any natural number higher than 0; default = 5
Sheep_stomach = 350 #Maximum food it can have in stomach - at maximum they will try to reproduce; any natural number higher than 0; default = 350
Sheep_I_am_hungry = 250 #Limit on wich they don't try to reproduce but eat; any natural number; default = 250
Sheep_hungry = 2 #How much food will it use per one turn; any natural number (even 0); default = 2
Sheep_rp_food_consume = 200 #How much food will be used from each parent to reproduce BEWARE the Sheep_stomach value; any natural number; default = 200
Sheep_corpse_food = 400 #How much food will be in corpse from Sheep; any natural number; default = 400

Sheep_baby = 0 #Starting numer of Sheep_baby; any natural number; default = 0
Sheep_baby_start_food = 50 #Food that Sheep_baby have in stomach at start; any natural number higher than 0 (because 0 means it will die immediatelly); default = 50
Sheep_baby_eat = 4 #How much can Sheep_baby eat per one turn; any natural number higher than 0; default = 4
Sheep_baby_stomach = 250 #Maximum food it can have in stomach - at maximum they will try to grow up (evolve); any natural number higher than 0; default = 250
Sheep_baby_I_am_hungry = 100 #Limit on wich they don't try to evolve but eat; any natural number; default = 100
Sheep_baby_hungry = 1 #How much food will it use per one turn; any natural number (even 0); default = 1
Sheep_baby_corpse_food = 125 #How much food will be in corpse from Sheep_baby; any natural number; default = 125
Sheep_baby_evolution = 25 #How many evolution points does evolution of Sheep_baby take; any natural number; default = 25
Sheep_baby_evolution_chance = 3 #What is the chance of getting an evolution point (1/Sheep_baby_evolution_chance); any natural number; default = 3
Sheep_baby_evolution_cost = 3 #How much of hunger*Sheep_baby_hungry will it use per one evolution token; any natural number; default = 3

Grass = 400 #Starting numer of Grass; any natural number; default = 200
Grass_spawn_rate = (1, 1) #Grass is spawned in random intervals between [1st and 2nd value] turns, so smaller numbers means more grass spawned over time; any natural number higher than 0; default = (1, 1)
Grass_food = 25 #Food Grass have on spawn; any natural number higher than 0 (because 0 means it will erase immediatelly); default = 7
Grass_grow = 1 #Amount by which is increased food supply each turn in each Grass; any whole number (grass may dying); default = 1
Grass_max = 50 #Maximal amount of food that can be in one Grass thingie; any natural number higher than 0; default = 50


DaSversion = "1.0.2" # Current version, written in log file; Changing that will result in shenanigans in crash resolving.
