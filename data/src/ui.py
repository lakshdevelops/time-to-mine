import pygame

from data.src.tile import Tile

class UI: # for the health tab we need to show the 

    def __init__(self, temp_ui_sprites, player):
        self.font = pygame.font.Font('./data/fonts/PixgamerRegular-OVD6A.ttf', 24)
        self.display = pygame.display.get_surface()
        self.ui_tab = pygame.image.load('./data/img/ui/ui_tab.png').convert_alpha()
        self.coin_icon = pygame.image.load('./data/img/coin_icon.png').convert_alpha()
        self.temp_ui_sprites = temp_ui_sprites
        self.heading_text = Text()
        self.text = Text()
        self.text.set_font_size_name(24)
        self.tab_active = True
        self.player = player
        self.drawing = False

        self.buttons = []
        self.exit_button = Button("exit", self.player)
        self.upgrade_time = 0
        self.upgrade_cooldown = 300


    def initialise_buttons(self,types):
        for button_type in types:
            self.buttons.append(Button(button_type,self.player))


    def draw_tab(self, heading_text, heading_colour, text_upgrade):

        if self.drawing:
            self.display.blit(self.ui_tab, ((self.display.get_width() // 2) - self.ui_tab.get_width() // 2,(self.display.get_height() // 2) - self.ui_tab.get_height() // 2))
            
            heading_surf = self.heading_text.create_text_surf(heading_text,heading_colour)
            self.display.blit(heading_surf, (self.display.get_width()//2-heading_surf.get_width()//2, 210))
            exit_surf, exit_rect = self.exit_button.create_surface_rect(None, None, (335,450))
            self.display.blit(exit_surf, (exit_rect.centerx-(exit_surf.get_width()//2), exit_rect.centery-(exit_surf.get_width()//2)))
            
            for i in range(len(text_upgrade)):
                self.display.blit(self.text.create_text_surf(text_upgrade[i], (255,255,255)), (234,256+i*44))
                self.display.blit(self.text.create_text_surf(f"(Level {self.player.levels[text_upgrade[i]]})", (192,192,192)), (234, 276+i*44))

                surf, rect = self.buttons[i].create_surface_rect(self.player.stats["value"],self.player.upgrade_costs[text_upgrade[i]], (420,256+i*44))

                if self.player.exact_hover_rect.colliderect(rect):
                    surf.set_alpha(180)
                else:
                    surf.set_alpha(255)

                self.display.blit(surf, (rect.centerx-(surf.get_width()//2), rect.centery-(surf.get_width()//2)))
                self.display.blit(self.coin_icon, (rect.midright[0], rect.midright[1]-15))

                curr_time = pygame.time.get_ticks()
                mouse_buttons = pygame.mouse.get_pressed()
                if mouse_buttons[0] and self.player.exact_hover_rect.colliderect(exit_rect):
                    self.drawing = False
                if mouse_buttons[0] and self.player.exact_hover_rect.colliderect(rect) and curr_time - self.upgrade_time > self.upgrade_cooldown:
                    self.upgrade_time = pygame.time.get_ticks()
                    self.buttons[i].if_clicked(self.player.upgrade_costs[text_upgrade[i]])


class Button:

    def __init__(self, button_type, player):
        self.display = pygame.display.get_surface()

        self.button_type = button_type
        self.player = player
        self.times_upgraded = 0

        self.text_renderer = Text()

        self.can_afford = False
        self.is_active = True

        self.maxxed = False


    def if_clicked(self, price_progression):
        if self.button_type == "play":
            return True
        elif self.button_type == "exit":
            return True
        elif self.button_type == "credits":
            return True
        elif price_progression[self.times_upgraded] != "Max":
            if self.player.stats["value"] >= price_progression[self.times_upgraded]:
                self.player.stats["value"] -= price_progression[self.times_upgraded]
                self.times_upgraded += 1

                if self.button_type == "Passive regeneration":
                    self.player.levels["Passive regeneration"] += 1
                    self.player.stats["Passive regeneration"] += 1
                elif self.button_type == "Health refill":
                    self.player.stats["health"] = self.player.stats["max_health"]
                    self.times_upgraded = 0
                elif self.button_type == "Speed":
                    self.player.stats["Speed"] += 1
                    self.player.levels["Speed"] += 1
                elif self.button_type == "Combat strength":
                    self.player.stats["Combat strength"] += 2
                    self.player.levels["Combat strength"] += 1
                elif self.button_type == "Mine strength":
                    for sprite in self.player.ore_sprites:
                        if sprite.hits_remaining > 1:
                            sprite.hits_remaining -= 1
                    for ore, ore_hits in self.player.ore_hits.items():
                        if ore_hits > 1:
                            self.player.ore_hits[ore] = ore_hits - 1
                    self.player.levels["Mine strength"] += 1
        else:
            self.maxxed = True
 

    
    def create_surface_rect(self, player_value, price_progression, position, colour=(255,255,255)):
        if self.button_type == "play":
            self.button_surf = self.text_renderer.create_text_surf("Play", colour)
            self.button_rect = self.button_surf.get_rect(topleft=position).inflate(10,5)
        elif self.button_type == "exit":
            self.button_surf = self.text_renderer.create_text_surf("Back", colour)
            self.button_rect = self.button_surf.get_rect(topleft=position).inflate(10,5)
        elif self.button_type == "credits":
            self.button_surf = self.text_renderer.create_text_surf("Credits", colour)
            self.button_rect = self.button_surf.get_rect(topleft=position).inflate(10,5)
        else:
            if price_progression[self.times_upgraded] == "Max":
                color = (198,115,225)
            elif player_value < price_progression[self.times_upgraded]:
                color = (194,68,68)
            else:
                color = (220,220,220)

            self.button_surf = self.text_renderer.create_text_surf(str(price_progression[self.times_upgraded]), color)
            self.button_rect = self.button_surf.get_rect(topleft=position).inflate(10,5)
        
        return self.button_surf, self.button_rect
    

class Value:

    def __init__(self, ui_sprites, player):
        self.coins = pygame.image.load('./data/img/ui/value.png').convert_alpha()
        self.coin_rect = self.coins.get_rect(topleft=(486,20))
        self.opp_coin_rect = self.coins.get_rect(topleft=(616,20))
        self.ui_sprites = ui_sprites
        Tile(self.ui_sprites, (486, 20), self.coins, sprite_type="value")
        Tile(self.ui_sprites, (616,20), self.coins, sprite_type="value")
        self.display = pygame.display.get_surface()
        self.value_text = Text()
        self.value_text.set_font_size_name(24)
        self.player = player
        self.opp_value = 0
        self.versus = self.value_text.create_text_surf("VS", (255,255,255))

    
    def get_opp_value(self, opp_value):
        self.opp_value = opp_value
      

    def display_value(self):
        self.display.blit(self.value_text.create_text_surf(f"{self.player.stats['value']}",(255,255,255)), (self.coin_rect.midright[0]+5, self.coin_rect.midright[1]-12))
        self.display.blit(self.versus, (self.coin_rect.midright[0]+45,25))
        self.display.blit(self.value_text.create_text_surf(f"{self.opp_value}",(194,68,68)), (self.opp_coin_rect.midright[0]+5, self.opp_coin_rect.midright[1]-12))


class Timer:

    def __init__(self, player, health_bar, value):

        self.first_music_not_played = True
        self.second_music_not_played = True
        self.third_music_not_played = True

        self.display = pygame.display.get_surface()
        self.tick = pygame.USEREVENT + 1
        pygame.time.set_timer(self.tick, 1000)

        self.timer_text = Text()
        self.timer_text.set_font_size_name(32)

        self.health_bar = health_bar
        self.value = value
        
        self.curr_time = "3:00"
        self.time_surf = self.timer_text.create_text_surf(self.curr_time, (255,255,255))
        self.display_timer = True
        
        self.dead_text = Text()
        self.dead_text.set_font_size_name(48)
        self.dead_surf = self.dead_text.create_text_surf("Respawning in", (194,68,68))
        
        self.dead_time = "0:20"
        self.player = player
        self.dead_time_surf = self.dead_text.create_text_surf(self.dead_time, (194,68,68))

        self.round_over = False
        self.respawned = False

        self.dead_alpha = pygame.Surface((704,704))
        self.dead_alpha.fill((32,32,32))
        self.dead_alpha.set_alpha(180)

        self.end_text = ""
        self.end_colour = ()
        self.winner_text = Text()
        self.winner_text.set_font_size_name(64)
        self.display_winner_text = False

    
    def update_timer(self, ev):
        if not self.round_over:
            if ev.type == self.tick:
                self.curr_time = self.subtract_time(self.curr_time) 
                
                if self.curr_time == True and self.display_timer:
                    self.player.active = False
                    self.display_timer = False
                    self.display_winner_text = True
                    self.get_winner()
                    self.winner_text_surf = self.winner_text.create_text_surf(self.end_text, self.end_colour)
                    self.curr_time = "0:05"
                elif self.curr_time == True and self.display_winner_text:
                    self.round_over = True
                else:
                    self.time_surf = self.timer_text.create_text_surf(self.curr_time, (255,255,255))


                if self.player.stats["health"] < self.player.stats["max_health"]:
                    self.player.stats["health"] += self.player.stats["Passive regeneration"]

                if self.health_bar.dead:
                    self.dead_time = self.subtract_time(self.dead_time)
                    if self.dead_time == True:
                        print("why")
                        self.health_bar.dead = False
                        self.player.active = True
                        self.player.stats["health"] = 90
                        self.dead_time = "0:20"
                    else:
                        self.dead_time_surf = self.dead_text.create_text_surf(self.dead_time, (194,68,68))


    def is_round_over(self):
        return self.round_over
    

    def draw_timer(self):
        if self.display_timer:
            self.display.blit(self.time_surf,((self.display.get_width() // 2) - (self.time_surf.get_width() // 2),20))
        if self.display_winner_text:
            self.player.active = False
            self.display.blit(self.winner_text_surf, ((self.display.get_width() // 2) - (self.winner_text_surf.get_width() // 2), (self.display.get_height()//2)-(self.winner_text_surf.get_height()//2)))
        if self.health_bar.dead:
            self.display.blit(self.dead_alpha,(0,0))
            self.display.blit(self.dead_surf, ((self.display.get_width() // 2) - (self.dead_surf.get_width() // 2), (self.display.get_height()//2)-(self.dead_surf.get_height()//2)))
            self.display.blit(self.dead_time_surf, ((self.display.get_width() // 2) - (self.dead_time_surf.get_width() // 2), (self.display.get_height()//2)-(self.dead_time_surf.get_height()//2)+40))


    
    def subtract_time(self, time):
        minutes = int(time[0])
        seconds = int(time[time.index(":")+1:])

        if seconds == 0:
            minutes -= 1
            seconds = 59
        else:
            seconds -= 1

        if minutes == 0 and seconds == 0:
            return True

        if seconds < 10:
            seconds = "0" + str(seconds)
        else:
            seconds = str(seconds)
        
        return str(minutes)+":"+seconds
    

    def get_winner(self):
        self.player.active = False
        if self.player.stats["value"] > int(self.value.opp_value):
            self.end_text = "YOU WON"
            self.end_colour = (198,115,225)
        elif self.player.stats["value"] == int(self.value.opp_value):
            self.end_text = "DRAW"
            self.end_colour = (192,192,192)
        else:
            self.end_text = "YOU LOSE"
            self.end_colour = (194,68,68)


class HealthBar:

    def __init__(self, player, ui_sprites):
        self.display = pygame.display.get_surface()
        self.text = Text()
        self.text.set_font_size_name(16)
        self.player = player
        self.heart = pygame.image.load('./data/img/heart.png').convert_alpha()
        self.dead_heart = pygame.image.load('./data/img/dead_heart.png').convert_alpha()
        self.ui_sprites = ui_sprites
        self.max_health = 90
        self.hearts = [Tile((self.ui_sprites), (20,20), self.heart, sprite_type="heart1"),
                Tile((self.ui_sprites), (52,20), self.heart, sprite_type="heart2"),
                Tile((self.ui_sprites), (84,20), self.heart, sprite_type="heart3")]
        self.heart_value = self.max_health // 3 
        self.dead = False


    def increase_max_health(self, max_health):
        self.max_health = max_health
        self.heart_value = self.max_health // 3


    def update_hearts(self):
        self.damage_taken = abs(self.player.stats["health"] - self.max_health)
        hearts_dead = self.damage_taken // self.heart_value
        if hearts_dead == 0:
            for heart in self.hearts:
                heart.image = self.heart
        elif hearts_dead == 1:
            self.hearts[-1].image = self.dead_heart
        elif hearts_dead == 2:
            self.hearts[-1].image = self.dead_heart
            self.hearts[-2].image = self.dead_heart
        elif hearts_dead == 3:
            for heart in self.hearts:
                heart.image = self.dead_heart


    def display_physical_health(self):
        self.display.blit(self.text.create_text_surf(f"{self.player.stats['health']}/{self.max_health}", (255,255,255)), (50,55))
            
    
    def get_if_dead(self):
        if self.player.stats["health"] <= 0:
            self.dead = True
            self.player.active = False
            self.player.stats["health"] = 0


class Text:

    def __init__(self):
        self.display = pygame.display.get_surface()
        self.rise_velocity = 2
        self.start_alpha = 255
        self.life = True
        self.font_size = 32
        self.font = pygame.font.Font('./data/fonts/PixgamerRegular-OVD6A.ttf', self.font_size)


    def set_font_size_name(self, size, name='./data/fonts/PixgamerRegular-OVD6A.ttf'):
        self.font_size = size
        self.font = pygame.font.Font(name, size)

    
    def set_attrs(self, pos, text, color, font_size, rise_velocity):
        self.font = pygame.font.Font('./data/fonts/PixgamerRegular-OVD6A.ttf', font_size)
        self.start_pos = pos
        self.color = color
        self.text = text
        self.rise_velocity = rise_velocity


    def create_text_fade_rising(self): # 
        if self.start_alpha < 0:
            self.life = False

        txtsurf = self.font.render(self.text, True, self.color)
        txtsurf.set_alpha(self.start_alpha)

        self.start_pos[1] -= self.rise_velocity
        self.start_alpha -= 4

        self.display.blit(txtsurf, (self.start_pos))

    
    def create_text_surf(self, text, color):
        txtsurf = self.font.render(text, True, color)
        return txtsurf


class InteractableObject:

    def __init__(self, type):
        self.font = pygame.font.Font('./data/fonts/PixgamerRegular-OVD6A.ttf', 24)
        self.display = pygame.display.get_surface()
        self.type = type
        self.activated = True

    
    def create_interact_surf(self, position, text="e to interact"):
        if self.activated:
            txtsurf = self.font.render(text, True, (255,255,255))
            self.display.blit(txtsurf, position)

    
    def check_if_interacted(self):
        if self.activated:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e]:
                return True
        

    def deactivate(self):
        self.activated = False


    def activate(self):
        self.activated = True