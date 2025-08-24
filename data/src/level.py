import pygame
from data.src.utils import import_folder
from random import randint, choice, random
from data.src.tile import Tile, Ore  
from data.src.player import Player
from data.src.light import Lamp
from data.src.enemy import Enemy
from data.src.ui import HealthBar, InteractableObject, UI, Value, Timer, Text

class Level:
    
    def __init__(self, client):
        
        pygame.mouse.set_visible(False)
        self.display = pygame.display.get_surface() 
        self.wall_tiles = import_folder('./data/img/walls/', as_dict=True)
        self.current_cave = "base_cave"
        self.transition_pending = False
        self.caves = ["dungeon_cave", "base_cave", "trader_cave"]
        self.active_boundaries = []
        self.client = client

        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.ore_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.temp_ui_sprites = pygame.sprite.Group()
        self.ui_sprites = UIGroup()

        self.enemy_graphics = import_folder('./data/img/enemies/', as_dict=True)

        self.player = Player([360,360], self.visible_sprites, self.obstacle_sprites, self.ore_sprites, self.enemy_sprites, self.ui_sprites)
        self.dungeon_cave_floor = pygame.image.load("./data/img/dungeon/map.png").convert_alpha()
        self.dungeon_cave = DungeonCave(self.visible_sprites, self.obstacle_sprites, self.client, self.player)
        self.health_bar = HealthBar(self.player, self.ui_sprites)
        self.value = Value(self.ui_sprites, self.player)
        self.timer = Timer(self.player, self.health_bar, self.value)

        self.base_cave = BaseCave(self.wall_tiles, self.visible_sprites, self.obstacle_sprites, self.ore_sprites, self.player)  
        self.base_cave_lamps = [Lamp((96,110), 12, 10, 20), Lamp((224,110), 10, 10, 20), Lamp((343,90), 11, 10, 20), Lamp((470,110), 13, 10, 20),Lamp((598,110), 10, 10, 20), Lamp((16, 305), 10, 10, 20), Lamp((676, 305), 10, 10, 20)]
        self.base_cave_floor = pygame.image.load('./data/img/dirt/map.png').convert_alpha()

        self.trader_cave = TraderCave(self.visible_sprites, self.obstacle_sprites, self.temp_ui_sprites, self.player)

        self.visible_sprites.set_lamps(self.base_cave_lamps)
        self.visible_sprites.set_floor(self.base_cave_floor, (-32,-32))
        self.base_cave.gen_ores()
        self.base_cave.gen_boundary()

        self.offset_x = 0
        self.offset_y = 0
        
        self.can_interact_other = True 
        self.interactable_surfaces = []

        self.active_texts = []

    def check_if_enemy_spawn(self):
        if self.player.mine_cycle_completed:
            type, rect = self.player.delete_ores()
            if type != None:
                rand = random()
                if rand < 0.5:
                    x = randint(48,80)
                    y = randint(48,80)
                else:
                    x = randint(-80,-48)
                    y = randint(-80,-48)

                spawn_chance = random()
                if spawn_chance < 0.3:
                    Enemy((self.visible_sprites, self.enemy_sprites), type, (max(rect.x+x, 96)
                    ,max(rect.y+y, 128)), self.enemy_graphics[type], self.player.damage_player)


    def check_player_in_curr_cave(self):
        if self.player.hitbox.topleft[0] < 64:
            self.offset_x = (self.player.hitbox.topleft[0] - 64) * 0.3
            self.player.offset_x = self.offset_x
            if self.player.hitbox.topleft[0] < -30:
                self.current_cave = self.next_cave()
                self.transition_pending = True
                self.player.hitbox.x = 670
                boundary1 = Tile((self.obstacle_sprites), (716,342), self.wall_tiles["side_wall"], inflated=False, sprite_type="wall")
                self.active_boundaries.append(boundary1)
        elif self.player.hitbox.topright[0] > 640:
            self.offset_x = (self.player.hitbox.topright[0] - 640) * 0.3
            self.player.offset_x = self.offset_x
            if self.player.hitbox.topleft[0] > 716:
                self.current_cave = self.next_cave()
                self.transition_pending = True
                self.player.hitbox.x = 0
                boundary2 = Tile((self.obstacle_sprites), (-36,342), self.wall_tiles["side_wall"], inflated=False, sprite_type="wall")
                self.active_boundaries.append(boundary2)
        else:
            self.offset_x = 0 
            self.player.offset_x = 0

        if self.player.hitbox.topleft[1] < 128:
            self.offset_y = (self.player.hitbox.topleft[1] - 128) * 0.3
            self.player.offset_y = self.offset_y
            if self.player.hitbox.topleft[1] < 82:
                self.current_cave = self.next_cave()
                self.transition_pending = True
                self.player.hitbox.y = 680
                boundary3 = Tile((self.obstacle_sprites, self.visible_sprites), (320,730), self.wall_tiles["bottom_wall"], inflated=False, sprite_type="wall")
                self.active_boundaries.append(boundary3)
        elif self.player.hitbox.topleft[1] > 640:
           self.offset_y = (self.player.hitbox.topleft[1] - 640) * 0.3
           self.player.offset_y = self.offset_y
           if self.player.hitbox.topleft[1] > 720:
                self.current_cave = self.next_cave()
                self.transition_pending = True
                self.player.hitbox.y = 120
                boundary4 = Tile((self.obstacle_sprites, self.visible_sprites), (320,102), self.wall_tiles["bottom_wall"], inflated=False, sprite_type="wall")    
                self.active_boundaries.append(boundary4) 
        else:
            self.offset_y = 0
            self.player.offset_y = 0


    def draw_interactable_surfs(self):
        if len(self.interactable_surfaces) > 0:
            for int_obj, rect in self.interactable_surfaces:
                if self.player.rect.colliderect(rect) and self.player.hover_rect.colliderect(rect):

                    if int_obj.type in ("chest1", "chest2"):
                        int_obj.create_interact_surf((rect.centerx-48, rect.centery+20), text="e to open")
                    else:
                        int_obj.create_interact_surf((rect.centerx-20, rect.centery))

                    if int_obj.check_if_interacted():
                        if int_obj.type == "health_stall":
                            self.can_interact_other = False
                            self.trader_cave.healthUI.drawing = True
                            self.player.active = False
                        elif int_obj.type == "pickaxe_stall":
                            self.can_interact_other = False
                            self.trader_cave.pickaxeUI.drawing = True
                            self.player.active = False
                        elif int_obj.type in ("chest1", "chest2"):
                            forfeit = self.dungeon_cave.get_forfeit()
                            text = Text()
                            surf = text.create_text_surf(f"{forfeit}", (255,255,255))
                            text.set_attrs([self.display.get_width()//2-surf.get_width()//2, self.display.get_height()//2-surf.get_height()//2], f"{forfeit}", (255,255,255), 32, 0)
                            self.active_texts.append(text)
                            self.dungeon_cave.handle_forfeit(forfeit)
                            self.dungeon_cave.open_chest(int_obj.type) 
                        


    def fade(self, width, height): 
        fade = pygame.Surface((width, height))
        fade.fill((0,0,0))
        for alpha in range(0, 300,5):
            fade.set_alpha(alpha)
            self.visible_sprites.custom_draw(offset_x=self.offset_x, offset_y=self.offset_y)
            self.display.blit(fade, (0,0))
            pygame.display.update()


    def kill_sprites(self):
        if len(self.visible_sprites) > 0:
            for sprite in self.visible_sprites:
                if sprite.sprite_type != "player" and sprite.sprite_type != "wall":
                    sprite.kill()
        if len(self.obstacle_sprites) > 0:
            for sprite in self.obstacle_sprites:
                if sprite.sprite_type != "wall":
                    sprite.kill()
        if len(self.ore_sprites) > 0:
            for sprite in self.ore_sprites:
                sprite.kill()
        if len(self.active_boundaries) > 1:
            for sprite in self.active_boundaries[:-1]:
                sprite.kill()
            self.active_boundaries = [self.active_boundaries[-1]]
        if len(self.temp_ui_sprites) > 0:
            for sprite in self.temp_ui_sprites:
                sprite.kill()


    def initialise_new_cave(self):
        if self.transition_pending:
            self.transition_pending = False
            self.fade(704, 704)
            self.kill_sprites()
            self.interactable_surfaces.clear()
            if self.current_cave == "base_cave":
                self.visible_sprites.set_floor(self.base_cave_floor, (-32,-32))
                self.base_cave.gen_ores()
            elif self.current_cave == "dungeon_cave":
                self.interactable_surfaces.append((self.dungeon_cave.chest1_interact, self.dungeon_cave.chest1_rect))
                self.interactable_surfaces.append((self.dungeon_cave.chest2_interact, self.dungeon_cave.chest2_rect))
                self.visible_sprites.set_lamps(self.base_cave_lamps)
                self.visible_sprites.set_floor(self.dungeon_cave_floor, (-32,-32))
                self.dungeon_cave.draw_chests()
            elif self.current_cave == "trader_cave":
                self.interactable_surfaces.append((self.trader_cave.health_interact, self.trader_cave.health_stall_rect))
                self.interactable_surfaces.append((self.trader_cave.pickaxe_interact, self.trader_cave.pickaxe_stall_rect))
                self.trader_cave.draw_stalls()
                self.visible_sprites.set_floor(self.dungeon_cave_floor, (-32,-32))
                self.visible_sprites.set_lamps(self.base_cave_lamps)


    def draw_current_cave(self):   
        self.check_if_enemy_spawn()

        self.visible_sprites.custom_draw(offset_x = self.offset_x, offset_y = self.offset_y)
        self.visible_sprites.update()

        if self.can_interact_other:
            self.draw_interactable_surfs()

        self.temp_ui_sprites.draw(self.display)
        self.temp_ui_sprites.update()

        self.trader_cave.healthUI.draw_tab("Health upgrades",(194,68,68),["Passive regeneration", "Refill health"])
        if not self.trader_cave.healthUI.drawing:
            self.can_interact_other = True
            self.player.active = True

        self.trader_cave.pickaxeUI.draw_tab("Speed and strength", (26,26,26), ["Mine strength", "Combat strength", "Speed"])
        if not self.trader_cave.pickaxeUI.drawing:
            self.can_interact_other = True
            self.player.active = True

        if len(self.enemy_sprites) > 0:
            for sprite in self.enemy_sprites:
                sprite.enemy_update(self.player)

        if len(self.active_texts) > 0:
            for text in self.active_texts:
                text.create_text_fade_rising()

            
    def run(self):
        self.initialise_new_cave()
        self.draw_current_cave()
        self.check_player_in_curr_cave()
        self.health_bar.update_hearts()
        self.value.display_value()
        self.timer.draw_timer()
        self.ui_sprites.custom_draw()
        self.ui_sprites.update()
        self.health_bar.get_if_dead()
        self.health_bar.display_physical_health()
        if self.client.stolen:
            self.player.stats["value"] -= 100
            self.client.stolen = False


    def next_cave(self):
        temp = self.caves.copy()
        temp.remove(self.current_cave)
        return choice(temp)


class BaseCave:

    def __init__(self, walls, visible_sprites, obstacle_sprites, ore_sprites, player):

        self.dirt_tiles = import_folder('./data/img/dirt/', as_dict=True)
        self.ores = import_folder('./data/img/ores/', as_dict=True, req_scale="32")
        
        self.wall_tiles = walls
        self.dirt_positions = self.gen_dirt()

        self.visible_sprites = visible_sprites
        self.obstacle_sprites = obstacle_sprites
        self.ore_sprites = ore_sprites
        self.player = player

        self.exit_coords = []

        self.ORE_PROBABILITIES = {
            "diamond" : range(1,6), # 5%
            "emerald" : range(6,17), # 10%
            "ruby" : range(17, 33), # 15%
            "amethyst" : range(33, 54), # 20%
            "gold" : range(54, 80) # 25%
        }
        self.MAX_ORES = 10
        #self.ore_pos_type = self.gen_ores()


    def gen_ores(self):
        for pos in self.dirt_positions:
            ore_spawn = random()
            if ore_spawn < 0.05 and len(self.ore_sprites) < self.MAX_ORES:
                ore_probability = randint(1,100)
                for ore, probability in self.ORE_PROBABILITIES.items():
                    if ore_probability in probability:
                        Ore((self.visible_sprites, self.ore_sprites, self.obstacle_sprites), pos, self.ores[ore], sprite_type="ore", hits_remaining=self.player.ore_hits[ore], ore_name=ore)

    def gen_dirt(self):

        dirt_positions = []
        for y in range(5,20):
            for x in range(2,20):
                dirt_positions.append((x * 32, y *32))

        return dirt_positions


    def gen_boundary(self):

        boundary_pos_type = []
        exit_pos_type = []

        # top wall
        for x in range(2, 19):
            if x == 2:
                boundary_pos_type.append(((x*32,640), self.wall_tiles["bottom_corner_wall"]))
            if x >= 9:
                if x == 9:
                    boundary_pos_type.append(((x*32, 64), self.wall_tiles["left_side_top_exit"]))
                    boundary_pos_type.append(((x*32+16, 64), self.wall_tiles["side_wall"]))

                    boundary_pos_type.append(((x*32+16, 640), self.wall_tiles["side_wall"]))
                elif x == 10:
                    exit_pos_type.append(((x*32,64), self.wall_tiles["top_exit"]))
                elif x == 11:
                    boundary_pos_type.append(((x*32 + 32, 64), self.wall_tiles["right_side_top_exit"]))
                    boundary_pos_type.append(((x*32 + 26, 64), self.wall_tiles["side_wall"]))

                    boundary_pos_type.append(((x*32+26, 640), self.wall_tiles["side_wall"]))
                else:
                    boundary_pos_type.append(((x*32 + 32, 96), self.wall_tiles["cave_wall"]))
                    boundary_pos_type.append(((x*32,640), self.wall_tiles["bottom_wall"]))
            else:
                boundary_pos_type.append(((x*32, 96), self.wall_tiles["cave_wall"]))
                boundary_pos_type.append(((x*32,640), self.wall_tiles["bottom_wall"]))

        # side walls
        for y in range(3,19):
            if y == 3:
                boundary_pos_type.append(((48, y*32), self.wall_tiles["corner_wall"]))
                boundary_pos_type.append(((640, y*32), self.wall_tiles["corner_wall_right"]))
            elif y in (10,11,12):
                if y == 10:
                    boundary_pos_type.append(((24, y*32 - 32), self.wall_tiles["cave_wall"]))
                    boundary_pos_type.append(((-8, y*32 - 32), self.wall_tiles["cave_wall"]))

                    boundary_pos_type.append(((648, y*32 - 32), self.wall_tiles["cave_wall"]))
                    boundary_pos_type.append(((680, y*32 - 32), self.wall_tiles["cave_wall"]))

                elif y == 12:
                    boundary_pos_type.append(((-10, y*32+32), self.wall_tiles["bottom_wall"]))
                    boundary_pos_type.append(((648, y*32+32), self.wall_tiles["bottom_wall"]))
            else:
                boundary_pos_type.append(((48, y*32), self.wall_tiles["side_wall"]))
                boundary_pos_type.append(((640, y*32), self.wall_tiles["side_wall_right"]))

        for pos, surf in boundary_pos_type:
            Tile((self.visible_sprites, self.obstacle_sprites), pos, surf, inflated=False, sprite_type="wall")
        
        for pos, surf, in exit_pos_type:
            Tile((self.visible_sprites), pos, surf, sprite_type="wall")


class DungeonCave:
    
    def __init__(self, visible_sprites, obstacle_sprites, client, player):
        self.visible_sprites = visible_sprites
        self.obstacle_sprites = obstacle_sprites
        self.chest = pygame.image.load('./data/img/dungeon/chest.png').convert_alpha()
        self.open_chest_img = pygame.image.load('./data/img/dungeon/open_chest.png').convert_alpha()

        self.chest1_interact = InteractableObject("chest1")
        self.chest2_interact = InteractableObject("chest2")
        self.chest1_rect = self.chest.get_rect(topleft=(290,352))
        self.chest2_rect = self.chest.get_rect(topleft=(380,352))

        self.dungeon_cave_lighting = Lamp((96,120), 2,2,2)

        self.chest_drops = ["Health refill", "Stole 100 from your opponent", "Enhance speed"]
        self.client = client

        self.player = player


    def draw_lava_light(self, offset_x, offset_y):
        self.dungeon_cave_lighting.draw_glow_rect((96,120),(32,160), offset_x, offset_y)
        pygame.display.update()


    def draw_chests(self):
        self.chest1_interact.activate()
        self.chest2_interact.activate()
        Tile((self.visible_sprites, self.obstacle_sprites), (290, 352), self.chest, sprite_type="chest1")
        Tile((self.visible_sprites, self.obstacle_sprites), (380, 352), self.chest, sprite_type="chest2")

    
    def open_chest(self, num):
        if num == "chest1":
            for sprite in self.visible_sprites:
                if sprite.sprite_type == "chest2":
                    sprite.kill()
                    self.chest2_interact.deactivate()
                if sprite.sprite_type == "chest1":
                    sprite.image = self.open_chest_img
                    self.chest1_interact.deactivate()
        elif num == "chest2":
            for sprite in self.visible_sprites:
                if sprite.sprite_type == "chest1":
                    sprite.kill()
                    self.chest1_interact.deactivate()
                if sprite.sprite_type == "chest2":
                    sprite.image = self.open_chest_img
                    self.chest2_interact.deactivate()

        forfeit = self.get_forfeit()
        self.handle_forfeit(forfeit)


    def handle_forfeit(self,forfeit):
        
        if forfeit == "Stole 100 from your opponent":
            self.player.stats["value"] += 100
            self.client.send_server_message("STEAL")
            forfeit = ""
        elif forfeit == "Health refill":
            self.player.stats["health"] = 90
            forfeit = ""
        elif forfeit == "Enhance speed":
            self.player.stats["Speed"] += 1
            forfeit = ""


    def get_forfeit(self):
        return choice(self.chest_drops)


class TraderCave:

    def __init__(self, visible_sprites, obstacle_sprites, temp_ui_sprites, player):
        self.visible_sprites = visible_sprites
        self.obstacle_sprites = obstacle_sprites
        self.temp_ui_sprites = temp_ui_sprites

        self.pickaxe_stall = pygame.image.load('./data/img/stalls/pickaxe.png').convert_alpha()
        self.pickaxe_stall_rect = self.pickaxe_stall.get_rect(topleft=(128,192))

        self.health_stall = pygame.image.load('./data/img/stalls/health.png').convert_alpha()
        self.health_stall_rect = self.health_stall.get_rect(topleft=(416,192))

        self.health_interact = InteractableObject("health_stall")
        self.pickaxe_interact = InteractableObject("pickaxe_stall")

        self.player = player 

        self.healthUI = UI(self.temp_ui_sprites, player)
        self.healthUI.initialise_buttons(("Passive regeneration", "Health refill"))

        self.pickaxeUI = UI(self.temp_ui_sprites, player)
        self.pickaxeUI.initialise_buttons(("Mine strength", "Combat strength", "Speed"))


    def draw_stalls(self):
        Tile((self.visible_sprites, self.obstacle_sprites), (128, 192), self.pickaxe_stall, sprite_type="stall")
        Tile((self.visible_sprites, self.obstacle_sprites), (416, 192), self.health_stall, sprite_type="stall")


    def get_if_tab_active(self):
        return self.healthUI.is_active()


class UIGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

    
    def custom_draw(self):

        for sprite in self.sprites():
            if sprite.sprite_type != "cursor":
                self.display_surface.blit(sprite.image, (sprite.rect.topleft[0], sprite.rect.topleft[1]))
            else:
                cursor = sprite

        self.display_surface.blit(cursor.image, cursor.rect)

        
    

class YSortCameraGroup(pygame.sprite.Group):


    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.lighting = []


    def set_floor(self, floor, pos):
        self.floor = floor
        self.floor_pos = pos


    def set_lamps(self, lamps):
        self.lamps = lamps

    
    def add_lighting(self, light):
        self.lighting.append(light)


    def clear_lighting(self):
        self.lighting.clear()

    def custom_draw(self, offset_x=0, offset_y=0):

        self.display_surface.blit(self.floor, (self.floor_pos[0]-offset_x,self.floor_pos[1]-offset_y))

        for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
            self.display_surface.blit(sprite.image,(sprite.rect.topleft[0]-offset_x, sprite.rect.topleft[1]-offset_y))

        for lamp in self.lamps:
            lamp.draw_with_glow(offset_x, offset_y)

        '''
        if len(self.lighting) > 0:
            for light in self.lighting:
                light.draw_glow_rect((96,120),(32,160), offset_x, offset_y)
        '''

