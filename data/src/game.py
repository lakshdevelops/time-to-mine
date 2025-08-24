import pygame
from data.src.main_menu import MainMenu
from data.src.client import Client
from data.src.player import Player
import sys
pygame.init()
pygame.mixer.init()

class Game:

    def __init__(self):

        self.WIDTH = 704
        self.HEIGHT = 704
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Time to Mine")

        self.clock = pygame.time.Clock()
        self.FPS = 120
        self.game_name_img = pygame.image.load('./data/img/title.png').convert_alpha()

        self.client = Client()
        self.main_menu = MainMenu(self.client)

        pygame.mouse.set_visible(False)


    def game_loop(self):

        while True:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.client.sent = False
                    if self.client.connected:
                        self.client.send_server_message("LEAVING")
                    
                    self.client.delete()
                    pygame.quit(); sys.exit()
                
                if self.main_menu.game_start:
                    self.main_menu.level.timer.update_timer(event)


            self.screen.fill((22,22,22))
           
            self.main_menu.draw_menu()

            pygame.display.update()

            self.clock.tick(self.FPS)
            