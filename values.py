map_x = 60 #Map width; any natural number higher than 2; default = 60
map_y = 25 #Map height; any natural number higher than 2; default = 25
FPS = 10 #Frames per second AND turns per second; any natural number higher than 0; default = 10

Dogs = 2 #Starting numer of Dogs; any natural number; default = 2
Dog_start_food = 100 #Food that Dogs have in stomach at start; any natural number higher than 0 (because 0 means it will die immediatelly); default = 100
Dog_eat = 10 #How much can Dogs eat per one turn; any natural number higher than 0; default = 10
Dog_stomach = 350 #Maximum food it can have in stomach() - at maximum they will try to reproduce once it will be added); any natural number higher than 0; default = 350
Dog_I_am_hungry = 250 #Limit on wich they don't try to reproduce but eat; any natural number; default = 250
Dog_hungry = 2 #How much food will it use per one turn; any natural number (even 0); default = 2
Dog_corpse_food = 20 #How much food will be in corpse from Dog; any natural number; default = 20

Sheep = 7 #Starting numer of Sheeps; any natural number; default = 6 OR 7 => too less OR too many, will be improved in future versions
Sheep_start_food = 50 #Food that Sheep have in stomach at start; any natural number higher than 0 (because 0 means it will die immediatelly); default = 50
Sheep_eat = 5 #How much can Sheep eat per one turn; any natural number higher than 0; default = 5
Sheep_stomach = 350 #Maximum food it can have in stomach - at maximum they will try to reproduce; any natural number higher than 0; default = 350
Sheep_I_am_hungry = 250 #Limit on wich they don't try to reproduce but eat; any natural number; default = 250
Sheep_hungry = 2 #How much food will it use per one turn; any natural number (even 0); default = 2
Sheep_rp_food_consume = 200 #How much food will be used from each parent to reproduce BEWARE the Sheep_stomach value; any natural number; default = 200
Sheep_corpse_food = 400 #How much food will be in corpse from Sheep; any natural number; default = 400

Grass = 100 #Starting numer of Grass; any natural number; default = 100
Grass_spawn_rate = 10 #Grass is spawned in random intervals between [1 and Grass_spawn_rate] turns, so smaller interval means more grass spawned over time; any natural number higher than 0; default = 10
Grass_food = 5 #Food Grass have on spawn; any natural number higher than 0 (because 0 means it will erase immediatelly); any natural number; default = 5
Grass_grow = 1 #Amount by which is increased food supply each turn in each Grass; any whole number (grass may dying); default = 1
Grass_max = 50 #Maximal amount of food that can be in one Grass thingie; any natural number higher than 0; default = 50
