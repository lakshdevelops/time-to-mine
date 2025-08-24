import pygame
from data.src.ui import Button, Text
from data.src.level import Level

class MainMenu:

    def __init__(self, client):
        self.display = pygame.display.get_surface()
        self.menu_background = pygame.image.load('./data/img/bg_menu.png').convert_alpha()
        self.game_name_img = pygame.image.load('./data/img/title.png').convert_alpha()
        self.cursor_img = pygame.image.load('./data/img/cursor.png').convert_alpha()
        self.cursor_img_rect = self.cursor_img.get_rect()

        self.play_button = Button("play", None)
        self.play_button.text_renderer.set_font_size_name(64)

        self.menu_screen = True
        self.looking_for_opponent = False
        self.game_start = False

        self.searching_text = Text()
        self.searching_text.set_font_size_name(48)

        self.back_button = Button("exit", None)
        self.back_button.text_renderer.set_font_size_name(32)

        self.game_client = client

        self.level = Level(self.game_client)

        self.menu_music_played = False

        self.game_music_played = False


    def draw_menu(self):

        if not self.menu_music_played:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.music.load('./data/game_music/3 Minutes.ogg')
            pygame.mixer.music.set_volume(0.7)
            pygame.mixer.music.play(-1)
            self.menu_music_played = True

        if self.menu_screen:
            mp = pygame.mouse.get_pos()
            self.cursor_img_rect.topleft = mp
            self.exact_hover_rect = pygame.Rect(mp[0]+8, mp[1]+8, 8,8)
            self.display.blit(self.menu_background, (0,0))
            self.display.blit(self.cursor_img, self.cursor_img_rect)
            self.create_buttons()

        elif self.looking_for_opponent:
            self.draw_looking_for_player_screen()

        elif self.game_start:

            if not self.game_music_played:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                pygame.mixer.music.load('./data/game_music/1 Minute.ogg')
                pygame.mixer.music.set_volume(0.7)
                pygame.mixer.music.play(-1)
                self.game_music_played = True

            self.level.run()
            self.game_client.set_value_data(self.level.player.stats["value"])
            self.level.value.get_opp_value(self.game_client.opponent_value)

            if self.game_client.is_connection_lost() or self.level.timer.is_round_over():
                if self.level.timer.is_round_over():
                    self.game_client.send_server_message("FINISHED")
                    self.game_client.disconnect()
                self.game_start = False
                self.menu_screen = True
                self.game_client.connection_lost = False
                del self.level
                self.level = Level(self.game_client)


    def draw_looking_for_player_screen(self):
        mp = pygame.mouse.get_pos()
        self.cursor_img_rect.topleft = mp
        self.exact_hover_rect = pygame.Rect(mp[0]+8, mp[1]+8, 8,8)
        self.display.blit(self.menu_background, (0,0))

        surf = self.searching_text.create_text_surf("Looking for an opponent...", (255,255,255))
        self.display.blit(surf, (self.display.get_width()//2-surf.get_width()//2, self.display.get_height()//2-surf.get_height()//2))

        back_surf, back_rect = self.back_button.create_surface_rect(None, None, ((self.display.get_width()//2)-20, (self.display.get_height()//2)+40), colour=(192,192,192))

        if self.exact_hover_rect.colliderect(back_rect):
            back_surf.set_alpha(170)
        else:
            back_surf.set_alpha(255)

        self.display.blit(back_surf, back_rect)

        self.display.blit(self.cursor_img, self.cursor_img_rect)

        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and self.exact_hover_rect.colliderect(back_rect):
            self.menu_screen = True
            self.looking_for_opponent = False
            self.game_client.disconnect()

        if self.game_client.opponent_found():
            self.looking_for_opponent = False
            self.game_start = True

        if self.game_client.is_connection_lost():
            self.looking_for_opponent = False


    def create_buttons(self):
        self.play_surf, self.play_rect = self.play_button.create_surface_rect(None, None, (self.display.get_width()//2-20, 320))

        if self.exact_hover_rect.colliderect(self.play_rect):
            self.play_surf.set_alpha(170)
        else:
            self.play_surf.set_alpha(255)

        self.display.blit(self.play_surf,self.play_rect)

        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and self.exact_hover_rect.colliderect(self.play_rect):
            self.menu_screen = False
            self.looking_for_opponent = True
            self.look_for_opponent()


    def look_for_opponent(self):
        self.game_client.connect()

