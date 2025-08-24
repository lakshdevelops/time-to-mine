import pygame

class Tile(pygame.sprite.Sprite): # create an ore class inheriting from tile so that it can have attributes such as hit remaining

    def __init__(self, groups, pos, surf, sprite_type="", inflated=True):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos 
        if sprite_type == "stall":
            self.hitbox = self.rect.inflate(-30,-30)
        else:
            self.hitbox = self.rect
        self.sprite_type = sprite_type

ORE_HITS = {"diamond" : 4, "emerald" : 3, "ruby" : 3, "amethyst" : 2, "gold" : 1} 

# when an ore is broke let it be either cracked, fake, legendary, ordinary etc and vary the value received from it based on that terraria style

class Ore(Tile):
    def __init__(self, groups, pos, surf, sprite_type, hits_remaining, ore_name):
        super().__init__(groups, pos, surf, sprite_type)
        self.ore_name = ore_name
        self.side_ore_rect = self.rect
        self.bottom_rect = self.rect.inflate(0,-10)
        self.hits_remaining = hits_remaining