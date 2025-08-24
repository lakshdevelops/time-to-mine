import random

class FloorMaker:

    def __init__(self, MAX_FLOORS, START_POS, TILE_SIZE):
        self.DIRECTIONS = {
            "right": (1,0),
            "left": (-1,0), 
            "up": (0,-1),
            "down": (0,1)
        }
        self.ORE_PROBABILITIES = {
            "diamond" : range(1,6), # 5%
            "emerald" : range(6,17), # 10%
            "ruby" : range(17, 33), # 15%
            "amethyst" : range(33, 54), # 20%
            "gold" : range(54, 80) # 25%
        }
        self.MAX_FLOORS = MAX_FLOORS
        self.START_POS = START_POS
        self.TILE_SIZE = TILE_SIZE
        
    def generate_floor_positions(self):
        
        positions = []
        stone_types = []
        current_position = self.START_POS

        while len(positions) < self.MAX_FLOORS:

            if current_position not in positions:
                positions.append([current_position[0], current_position[1]])

                stone_chance = round(random.random(), 2)
                if stone_chance < 0.2:
                    stone_types.append(random.choice(["cobble2", "cobble3", "cobble4"])) #custom stone
                else:
                    stone_types.append("cobble") #default stone

            next_direction = random.choice(list(self.DIRECTIONS.values()))
            current_position[0] += next_direction[0] * self.TILE_SIZE
            current_position[1] += next_direction[1] * self.TILE_SIZE

        split_positions = list(zip(*positions))
        x_positions = list(split_positions[0])
        y_positions = list(split_positions[1])

        min_x = min(x_positions)
        min_y = min(y_positions)

        if min(x_positions) < 0:
            x_positions = map(lambda x: x + abs(min_x), x_positions)

        if min(y_positions) < 0:
            y_positions = map(lambda y: y + abs(min_y), y_positions)

        return list(zip(x_positions, y_positions)), stone_types


    def generate_ore_positions(self, floor_positions):
        ore_positions = []

        for pos in floor_positions:
            ore_spawning = random.random()
            if ore_spawning < 0.05:
                ore_probability = random.randint(1,100)
                for ore, probability in self.ORE_PROBABILITIES.items():
                    if ore_probability in probability:
                        ore_positions.append((ore, pos))

        return ore_positions

    def draw_map(self):
    
        for pos, s_type in zip(self.positions, self.stone_types):
            self.display.blit(self.cobbles[s_type], pos) # later need to implement a tile class to keep track of collideable and non collideable tiles
            #add lair spawns for a chance to get more valuable things 
            #create system so that the cave always spawns in the middle of the screen

    def draw_ores(self):
        for ore_pos in self.ore_positions:
            self.display.blit(self.ores[ore_pos[0]], ore_pos[1])

