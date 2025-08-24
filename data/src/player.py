import pygame
from data.src.utils import import_folder, import_sounds
from data.src.light import Light 
from random import random, choice, randint
from data.src.ui import Text
from data.src.tile import Tile

class Player(pygame.sprite.Sprite):

    def __init__(self, pos, groups, obstacle_sprites, ore_sprites, enemy_sprites, ui_sprites):
        super().__init__(groups)
        self.image = pygame.image.load('./data/img/player_animations/idle_down/idle_down1.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect
        self.position = pos
        self.sprite_type = "player"
        self.hover_image = pygame.image.load("./data/img/cursor.png").convert_alpha()
        self.offset_x = 0
        self.offset_y = 0
        
        self.enemy_sprites = enemy_sprites
        self.obstacle_sprites = obstacle_sprites
        self.ore_sprites = ore_sprites
        self.ui_sprites = ui_sprites

        self.hover_tile = Tile(self.ui_sprites, (300,300), self.hover_image, sprite_type="cursor")
        self.hover_rect = self.hover_image.get_rect()

        self.direction = pygame.math.Vector2()
        self.speed = 2
        self.status = "down"
        self.animation_speed = 0.08
        self.frame_index = 0
        self.player_tile_col = 0
        self.player_tile_row = 0 

        self.display = pygame.display.get_surface()

        self.load_player_assets()

        self.light_radius = 20
        self.color = [10,10,10]
        self.player_light = Light()
        self.player_light.set_start_max_glow_rad(10,15)

        self.mining = False
        self.mine_cycle_completed = False
        self.mining_sounds = import_sounds('./data/sound/mining/')

        self.ore_positions = [sprite.pos for sprite in self.obstacle_sprites if sprite.sprite_type=="ore"]
        self.ores_mined = {"ruby" : 0, "amethyst" : 0, "diamond" : 0, "gold" : 0, "emerald" : 0}
        self.ore_colors = {"ruby" : (205,92,92), "amethyst" : (171,122,167), "diamond" : (137,207,240), "gold": (219,172,52), "emerald": (144,238,144)}
        self.ore_values = {"diamond" : 100, "emerald" : 40, "ruby" : 35, "amethyst" : 30, "gold": 25}
        self.ore_hits = {"diamond" : 4, "emerald" : 3, "ruby" : 3, "amethyst" : 2, "gold" : 1} 

        self.stats = {"Speed" : 2, "mine_strength" : 1, "Combat strength" : 3, "health" : 90, "value" : 0, "Passive regeneration" : 0, "max_health":90}
        self.levels = {"Passive regeneration" : 1, "Combat strength" : 1, "Mine strength" : 1, "Speed" : 1, "Refill health": 1}
        self.upgrade_costs = {"Passive regeneration" : (100,150,200,"Max"), "Refill health": (100,), "Mine strength" : (50,75,100,200,"Max"), "Speed" : (50,75,"Max"), "Combat strength" : (50,75,100,150, "Max")}

        self.active_texts = []
        self.active = True
    

    def damage_player(self):
        self.stats["health"] -= 10
        new_text = Text() # could cause performance to drop after many instansiations
        new_text.set_attrs([self.rect.centerx, self.rect.centery], f"10", (253,32,21), 24, 2)
        self.active_texts.append(new_text)


    def ore_mined(self): 
        direction = self.status
        if "_" in direction:
            direction = self.status[self.status.index("_")+1:]
        for sprite in self.ore_sprites:
            if self.rect.colliderect(sprite.side_ore_rect) and self.hover_rect.colliderect(sprite.side_ore_rect):
                y_distance = sprite.side_ore_rect.y - self.rect.y
                x_distance = sprite.side_ore_rect.x - self.rect.x
                if direction == "up" and y_distance < 0 and x_distance < 48:
                    sprite.hits_remaining -= 1 
                    choice(list(self.mining_sounds.values())).play()
                elif direction == "down" and y_distance > 0 and x_distance < 48:
                    sprite.hits_remaining -= 1
                    choice(list(self.mining_sounds.values())).play()
                elif direction == "right" and x_distance > 0 and y_distance < 48:
                    sprite.hits_remaining -= 1
                    choice(list(self.mining_sounds.values())).play()
                elif direction == "left" and x_distance < 0 and y_distance < 48:
                    sprite.hits_remaining -= 1
                    choice(list(self.mining_sounds.values())).play()

        for sprite in self.enemy_sprites:
            if self.rect.colliderect(sprite.hitbox) and self.hover_rect.colliderect(sprite.hitbox):
                new_text = Text()

                crit_hit_chance = random()

                if crit_hit_chance < 0.1:
                    damage = self.stats['Combat strength']+randint(1,3)
                    size = 32
                    text = str(damage) + "!"
                    knock = 2.5
                    knock_dist = 120
                else:
                    damage = self.stats['Combat strength']
                    size = 24
                    text = damage
                    knock = 1.5
                    knock_dist = 75

                new_text.set_attrs([sprite.rect.centerx, sprite.rect.centery], f"{text}", (255,255,255), size, 1)
                sprite.health -= damage

                self.active_texts.append(new_text)
                sprite.knockback(knock, knock_dist)

                if sprite.health <= 0: 
                    sprite.kill()

    def check_if_player_dead(self):
        pass
 
    def delete_ores(self):
        for sprite in self.ore_sprites:
            if sprite.hits_remaining == 0:
                self.stats["value"] += self.ore_values[sprite.ore_name]

                new_text = Text()
                new_text.set_attrs([sprite.rect.centerx, sprite.rect.centery], f"1x {sprite.ore_name}", self.ore_colors[sprite.ore_name], 24, 1)
                self.active_texts.append(new_text)

                new_text2 = Text()
                new_text2.set_attrs([sprite.rect.centerx-20, sprite.rect.centery-20], f"+{self.ore_values[sprite.ore_name]}", (255,215,0), 24, 2)
                self.active_texts.append(new_text2)

                self.ores_mined[sprite.ore_name] += 1 
                name = sprite.ore_name
                rect = sprite.side_ore_rect
                sprite.kill()

                enemy_spawn = random()
                if enemy_spawn < 1:
                    return name, rect

        return (None, None)


    def draw_texts(self):
        for text in self.active_texts:
            text.create_text_fade_rising()


    def delete_old_texts(self):
        if len(self.active_texts) > 0:
            for text in self.active_texts:
                if not text.life:
                    self.active_texts.remove(text)
                    del text


    def collision(self, direction):

        if direction == "horizontal":
            for sprite in self.obstacle_sprites:
                if self.hitbox.colliderect(sprite.hitbox):

                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
    
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right

        if direction == "vertical":
            for sprite in self.obstacle_sprites:
                if self.hitbox.colliderect(sprite.hitbox):

                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top

                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom 

    def move(self):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += (self.direction.x * self.stats["Speed"])
        self.collision('horizontal')
        self.hitbox.y += (self.direction.y * self.stats["Speed"])
        self.collision('vertical')

        self.rect.center = self.hitbox.center
        self.player_tile_row = self.rect.x // 32
        self.player_tile_col = self.rect.y // 32


    def input(self):
        
        if not self.mining:
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()

            if mouse_buttons[0]:
                self.frame_index = 0
                self.mining = True
                self.ore_mined()

            self.direction.x = 0
            self.direction.y = 0
            
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.direction.x = 0
                self.status = "walk_up"
            
            if keys[pygame.K_s]:
                self.direction.y = 1
                self.direction.x = 0
                self.status = "walk_down"

            if keys[pygame.K_d]:
                self.direction.x = 1
                self.direction.y = 0
                self.status = "walk_right"

            if keys[pygame.K_a]:
                self.direction.x = -1
                self.direction.y = 0
                self.status = "walk_left"
                

    def draw_hover_surf(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_col = (mouse_pos[0] + 16) // 32
        mouse_row = (mouse_pos[1] +16) // 32
        self.hover_rect = pygame.Rect(mouse_col*32, mouse_row*32, 32, 32)
        self.exact_hover_rect = pygame.Rect(mouse_pos[0]+8, mouse_pos[1]+8, 8,8)
        self.hover_tile.rect = mouse_pos


    def load_player_assets(self):
        char_path = './data/img/player_animations/'
        self.animations = {"idle_down": [], "idle_right": [], "idle_left": [],  "idle_up": [], "walk_down": [], "walk_right": [], "walk_left": [], "walk_up": [], "mine_down": [], "mine_left": [], "mine_right": [],"mine_up": []}

        for animation in self.animations.keys():
            if animation in ("idle_left", "idle_right", "walk_right", "walk_left", "mine_left", "mine_right"):
                full_path = char_path + animation[:animation.index("_")] + "_side"
            else:
                full_path = char_path + animation
            
            if "left" in animation:
                self.animations[animation] = [pygame.transform.flip(img, flip_x=True,flip_y=False) for img in import_folder(full_path, req_scale="64")]
                
            else:
                self.animations[animation] = import_folder(full_path, req_scale="64")


    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            self.animation_speed = 0.1
            if not "idle" in self.status and not "mine" in self.status:
                if "walk" in self.status:
                    self.status = self.status.replace("walk", "")
                    self.status = "idle" + self.status
                else:
                    self.status = "walk_" + self.status
        else:
            self.animation_speed = 0.15

        if self.mining: 
            self.direction.x = 0
            self.direction.y = 0
            self.animation_speed = 0.2
            
            mouse_pos = pygame.mouse.get_pos()
            dist = (mouse_pos[0] - (self.rect.x + 12), (self.rect.y + 20) - mouse_pos[1])

            if dist[0] - dist[1] < 0 and dist[0] + dist[1] > 0:
                self.status = self.status.replace(self.status[self.status.index("_")+1:], "up")
            elif dist[0] - dist[1] < 0 and dist[0] + dist[1] < 0:
                self.status = self.status.replace(self.status[self.status.index("_")+1:], "left")
            elif dist[0] + dist[1] > 0 and dist[0] - dist[1] > 0:
                self.status = self.status.replace(self.status[self.status.index("_")+1:], "right")
            elif dist[0] - dist[1] > 0 and dist[0] + dist[1] < 0:
                self.status = self.status.replace(self.status[self.status.index("_")+1:], "down")
            
            if not "mine" in self.status:
                if "walk" in self.status:
                    self.status = self.status.replace("walk", "mine")
                elif "idle" in self.status:
                    self.status = self.status.replace("idle", "mine")
                else:
                    self.status = "mine_" + self.status
        else:
            if "mine" in self.status:
                self.status.replace("mine_", "")
                self.animation_speed = 0.15
        

    def cooldowns(self):
        if self.mining:
            if self.mine_cycle_completed:
                self.frame_index = 0
                self.mining = False
                self.status = self.status.replace("mine", "idle")
                self.mine_cycle_completed = False
                self.delete_ores()


    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            if self.mining:
                self.mine_cycle_completed = True
            self.frame_index = 0
        prev_pos = (self.rect.x, self.rect.y)
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(topleft=prev_pos)


    def update(self):
        if self.active:
            self.input()
            self.cooldowns()
            self.get_status()
            self.animate()
            self.move()
            self.draw_hover_surf()
            self.player_light.draw_player_glow(self.rect, (20,20,10), (self.offset_x, self.offset_y))
            self.draw_texts()
            self.delete_old_texts()
        else:
            self.get_status()
            self.animate()
            self.draw_hover_surf()
            self.player_light.draw_player_glow(self.rect, (20,20,10), (self.offset_x, self.offset_y))