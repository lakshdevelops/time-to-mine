import pygame

class Light:

    def __init__(self):

        self.lamp = pygame.image.load('./data/img/walls/cave_lamp.png').convert_alpha()
        self.lamp_data = []
        self.reached_rad_limit = False
        self.reached_lamp_rad_limit = False

        self.display = pygame.display.get_surface()

    def set_start_max_glow_rad(self,min_rad, max_rad):
        self.glow_rad = min_rad
        self.max_glow_rad = max_rad

    def draw_player_glow(self, player_rect, color, offset, modulating=True):

        if not self.reached_rad_limit:
            self.glow_rad += 0.1
        else:
            self.glow_rad -= 0.1

        if self.glow_rad > self.max_glow_rad:
            self.reached_rad_limit = True 
        elif self.glow_rad < 10:
            self.reached_rad_limit = False

        self.create_glow(self.glow_rad, color, player_rect, offset)


    def create_glow(self, glow_radius, color, rect, offset):
        light = pygame.Surface((self.max_glow_rad*2, self.max_glow_rad*2))
        pygame.draw.circle(light, color, (self.max_glow_rad, self.max_glow_rad), glow_radius)
        light.set_colorkey((0,0,0))

        self.display.blit(light, (rect.x+13-offset[0], rect.y-16-offset[1]), special_flags=pygame.BLEND_RGB_ADD)


class Lamp:

    def __init__(self, pos, starting_rad, min_rad, max_rad):
        self.pos = pos
        self.display = pygame.display.get_surface()

        self.lamp = pygame.image.load('./data/img/walls/cave_lamp.png').convert_alpha()
        self.lamp_rect = self.lamp.get_rect(topleft=pos)

        self.rad_limit = False
        self.starting_rad = starting_rad
        self.min_rad = min_rad
        self.max_rad = max_rad

        self.color_limit = False
        self.start_col = [10,10,10]


    def draw_with_glow(self, offset_x, offset_y):
        self.display.blit(self.lamp, (self.lamp_rect.x-offset_x, self.lamp_rect.y-offset_y))
        self.display.blit(self.modulate_rad(), (self.lamp_rect.x-14-offset_x, self.lamp_rect.y-11-offset_y), special_flags=pygame.BLEND_RGB_ADD)


    def draw_glow_rect(self, pos, dim, offset_x, offset_y):
        self.display.blit(self.modulate_col(pos,dim), (pos[0]-offset_x, pos[1]-offset_y), special_flags=pygame.BLEND_RGB_ADD)


    def modulate_col(self, pos, dim):
        if not self.color_limit:
            self.start_col[0] += 0.1
            self.start_col[1] += 0.1
            self.start_col[2] += 0.1
        else:
            self.start_col[0] -= 0.1
            self.start_col[1] -= 0.1
            self.start_col[2] -= 0.1

        if sum(self.start_col) > 60:
            self.color_limit = True 
        elif sum(self.start_col) < 30:
            self.color_limit = False

        return self.create_glow_rect(pos, dim, self.start_col)


    def create_glow_rect(self, pos, dimensions, color):
        glow_surf = pygame.Surface(dimensions)
        glow_rect = pygame.Rect(pos[0], pos[1], dimensions[0], dimensions[1])
        pygame.draw.rect(glow_surf, color, glow_rect)
        glow_surf.set_colorkey((0,0,0))
        return glow_surf
    

    def modulate_rad(self):
        if not self.rad_limit:
            self.min_rad += 0.1
        else:
            self.min_rad -= 0.1

        if self.min_rad > self.max_rad:
            self.rad_limit = True 
        elif self.min_rad < self.starting_rad:
            self.rad_limit = False

        return self.create_glow(self.min_rad, self.max_rad)

    def create_glow(self, glow_radius, max_rad):

        glow = pygame.Surface((max_rad*2, max_rad*2))
        pygame.draw.circle(glow, (20,20,10), (max_rad, max_rad), glow_radius)
        glow.set_colorkey((0,0,0))

        return glow   
    