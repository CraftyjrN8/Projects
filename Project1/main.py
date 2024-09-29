import pygame
import random
import json

#Player Class
class Player(pygame.sprite.Sprite):

    #Set's all the attributes for the Player class
    def __init__(self, sprite_group):

        super().__init__(sprite_group)
        self.image = pygame.image.load('images/player.png').convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        self.direction = pygame.Vector2()
        self.speed = 800

        self.can_shoot = True
        self.laser_shoot_time = 0 
        self.cooldown_duration = 200

        self.mask = pygame.mask.from_surface(self.image)

    #Makes a laser cooldown of 400 milliseconds
    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    #This method updates every frame (moves player, fire's gun, checks boundaries)
    def update(self, dt):
        key = pygame.key.get_pressed()

        self.direction.y = int(key[pygame.K_s]) - int(key[pygame.K_w])
        self.direction.x = int(key[pygame.K_d]) - int(key[pygame.K_a])

        if self.direction:
            self.direction = self.direction.normalize()
        else:
            self.direction = self.direction

        if pygame.key.get_just_pressed()[pygame.K_SPACE] and self.can_shoot:
            laser_sound.play()
            Laser(laser_surf, self.rect.midtop, (all_sprites, weapon_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
        
        self.laser_timer()
        
        self.rect.center += self.direction * self.speed * dt

        if self.rect.right > WINDOW_WIDTH:
            self.rect.right -= 2
        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom -= 2
        if self.rect.left < 0:
            self.rect.left += 2
        if self.rect.bottom < WINDOW_HEIGHT - 150:
            self.rect.bottom += 2

#Star class
class Star(pygame.sprite.Sprite):

    #set's all the attributes for the Star class
    def __init__(self, sprite_group, star_surf):
        super().__init__(sprite_group)

        self.image = star_surf
        self.rect = self.image.get_frect(center = (random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT)))

#Laser class
class Laser(pygame.sprite.Sprite):

    #Set's up attributes for the Laser class
    def __init__(self, surf, pos, sprite_group):
        super().__init__(sprite_group)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
    
    #Called every frame (moves laser up, once out of window then die)
    def update(self, dt):
        self.rect.centery -= 400 * dt

        if self.rect.bottom < 0:
            self.kill()

#Meteor class
class Meteor(pygame.sprite.Sprite):

    #Set's up attributes for Meteor class
    def __init__(self, surf, pos, sprite_group):
        super().__init__(sprite_group)
        self.rotate_speed = random.randint(100, 800)
        self.original_image = surf
        self.image = self.original_image
        self.rect = self.image.get_frect(center = pos)
        self.direction = pygame.Vector2(random.uniform(-0.5, 0.5), 1)
        self.speed = random.randint(200, 800)

        self.start_time = pygame.time.get_ticks()
        self.life_time = 4000

    #Called every frame (goes down in an direction, kills after 4 seconds, rotates image)
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

        if pygame.time.get_ticks() - self.start_time >= self.life_time:
            self.kill()
        
        if self.rect.right > WINDOW_WIDTH or self.rect.left < 0:
            self.direction.x *= -1
        
        self.rotate_speed += 100 * dt
        self.image = pygame.transform.rotozoom(self.original_image, self.rotate_speed, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

#AnimatedExplosion class     
class AnimatedExplosion(pygame.sprite.Sprite,):

    #Set's up Attributes for class
    def __init__(self, explosion_frames, pos, groups):
        super().__init__(groups)
        self.frames = explosion_frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)


    #Called once every frame (Goes through a list of images)
    def update(self, dt):
        self.frame_index += 60 * dt
        if self.frame_index < len(self.frames):
            self.image = explostion_frames[int(self.frame_index) % len(self.frames)]
        else:
            self.kill()

#Handles collisions
def collisions():

    global high_score
    global running
    global meteors_destroyed
    global meteor_spawn_time
    global death_score
    global old_score
    if pygame.sprite.spritecollide(player, meteor_sprites, False, pygame.sprite.collide_mask):
        if score > old_score:
            high_score = score
        for meteor in meteor_sprites:
            meteor.kill()
        death_score = (int(pygame.time.get_ticks() / 10)) + (meteors_destroyed)
        meteor_spawn_time = 400
        meteors_destroyed = 0
    for weapons in weapon_sprites:
        collided_sprites = pygame.sprite.spritecollide(weapons, meteor_sprites, True)
        if collided_sprites:
            explosion_sound.play()
            weapons.kill()
            meteors_destroyed += 1
            AnimatedExplosion(explostion_frames, weapons.rect.midtop, all_sprites)

#Handles score
def display_score():
    current_time = pygame.time.get_ticks()
    text_surf = font.render(f'Score: {score}', True, "Black")
    if old_score > score:
        text_surf2 = font.render(f'High score: {high_score}', True, "Black")
    else:
        text_surf2 = font.render(f'High score: {score}', True, "Black")
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH/2, 100))
    text_rect2 = text_surf2.get_frect(midbottom = (WINDOW_WIDTH/2, 180))
    pygame.draw.rect(display_surface, "black", text_rect.inflate(20, 15).move(0, -8), 5, 10)
    pygame.draw.rect(display_surface, "black", text_rect2.inflate(20, 15).move(0, -8), 5, 10)
    display_surface.blit(text_surf, text_rect)
    display_surface.blit(text_surf2, text_rect2)

#Game Setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
running = True
pygame.display.set_caption('My Game')
clock = pygame.time.Clock()
high_score = 0
old_score = 0
death_score = 0
score = 0
meteors_destroyed = 0

#Tries to see if there is a txt file to load the score, if not then the code passes
try:
    with open('images/score_save.txt') as score_file:
        old_score = json.load(score_file)
    high_score = old_score
except:
    print("user has no score")

#Import images
star_surf =  pygame.image.load('images/star.png').convert_alpha()
laser_surf = pygame.image.load('images/laser.png').convert_alpha()
meteor_surf = pygame.image.load('images/meteor.png').convert_alpha()
font = pygame.font.Font("images/Oxanium-Bold.ttf", 40)
explostion_frames = [pygame.image.load(f"images/explosion/{i}.png").convert_alpha() for i in range(21)]

#Import sound
laser_sound = pygame.mixer.Sound('audio/laser.wav')
laser_sound.set_volume(0.05)
explosion_sound = pygame.mixer.Sound('audio/explosion.wav')
explosion_sound.set_volume(0.05)
game_sound = pygame.mixer.Sound('audio/game_music.wav')
game_sound.set_volume(0.03)
game_sound.play(loops=-1)

#Sprite (Surface) Groups
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
weapon_sprites = pygame.sprite.Group()

#Creates 20 star objects
for i in range(20):
    Star(all_sprites, star_surf)

#Creates Player
player = Player(all_sprites)

#Custom Meteor event
meteor_spawn_time = 400
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, meteor_spawn_time)

#Game loop
while running:
    print(meteor_spawn_time)
    score = int(pygame.time.get_ticks() / 10) + (meteors_destroyed * 100) - death_score

    if score < 0:
        score = 0
    
    #Delta Time
    dt = clock.tick() / 1000

    #Fills window lightblue
    display_surface.fill((150, 80, 150))

    #Checks for pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            Meteor(meteor_surf, (random.randint(80, (WINDOW_WIDTH - 80)),  0), (all_sprites, meteor_sprites))

            #decreases spawn time by 0.002% and resets the timer
            meteor_spawn_time *= 0.998
            pygame.time.set_timer(meteor_event, int(meteor_spawn_time))
    
    #Calls all Objects update methods
    all_sprites.update(dt)

    #Calls collisions function every frame
    collisions()

    #Draws all_sprites to window (display_surface)
    all_sprites.draw(display_surface)

    #Calls display_score function every frame
    display_score()

    #Updates Screen every frame
    pygame.display.update()

#If this print's it means code worked as well as it shows your final score
print(f'Exited with Code 0')

# if highscore is lower than score then it saves the score as a new highscore
if old_score < high_score:
    with open('images/score_save.txt', 'w') as score_file:
        json.dump(high_score,score_file)

#Quits pygame
pygame.quit()