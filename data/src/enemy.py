import pygame

class Enemy(pygame.sprite.Sprite):

    def __init__(self, groups, type, pos, image, damage_player):
        super().__init__(groups)
        self.sprite_type = type
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(10,10)
        self.attack_rad = 32
        self.notice_rad = 200
        self.speed = 2
        self.status = ""
        self.dir = pygame.math.Vector2()
        self.can_attack = False
        self.attack_cooldown_time = 1200
        self.damage_player = damage_player
        self.times_hit = 0
        self.attack_time = 0
        self.health = 10

        self.knock_strength = 1 
        self.knocked = False
        self.can_move = True


    def knockback(self, knock_strength, knock_dist):
        self.knocked = True
        self.knock_strength = knock_strength
        self.knock_dist = knock_dist


    def move(self):
       
        if self.dir.magnitude() != 0:
            self.dir = self.dir.normalize()

        if self.can_move or self.knocked:
            self.hitbox.x += self.dir.x * self.speed * self.knock_strength
            self.hitbox.y += self.dir.y * self.speed * self.knock_strength
            self.rect.center = self.hitbox.center


    def get_player_dist_dir(self, player):
        enemy_pos = pygame.math.Vector2(self.rect.center)
        player_pos = pygame.math.Vector2(player.hitbox.center)   
        dist = (player_pos - enemy_pos).magnitude()

        if dist > 0:
            dir = (player_pos - enemy_pos).normalize()
        else:
            dir = pygame.math.Vector2()
        
        if dist < 5:
            self.can_move = False
        else:
            self.can_move = True

        return (dist, dir)
    
    
    def get_status(self, player):
        dist = self.get_player_dist_dir(player)[0]
        if dist <= self.attack_rad:
            self.status = "attack"
        elif dist <= self.notice_rad:
            self.status = "move"
        else:
            self.status = "idle"

    
    def cooldown(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if current_time - self.attack_time > self.attack_cooldown_time:
                self.can_attack = True


    def actions(self, player):
        if self.knocked:
            self.dir = self.get_player_dist_dir(player)[1]
            self.dir = -self.dir
            if self.get_player_dist_dir(player)[0] >= self.knock_dist: #create a point of knock var 
                self.knocked = False
                self.knock_strength = 1 

        elif self.status == "attack" and self.can_attack:
            self.can_attack = False
            self.attack_time = pygame.time.get_ticks()
            self.damage_player()
        elif self.status == "move":
            self.dir = self.get_player_dist_dir(player)[1]
        else:
            self.dir = pygame.math.Vector2()


    def update(self):
        self.move()
        self.cooldown()


    def enemy_update(self, player):
        self.get_status(player)
        self.actions(player)

    