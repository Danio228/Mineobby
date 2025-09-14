import pygame 
from pygame import *
import os
import time
import math
import random


pygame.init()
window = pygame.display.set_mode((1920, 1300))
clock = pygame.time.Clock() 
pygame.display.set_caption("Lava Obby")



mixer.init()
Explosion = pygame.mixer.Sound('./Sounds/allah-akbar.mp3')
Dead = pygame.mixer.Sound('./Sounds/Steve_Dead.mp3')
boww = pygame.mixer.Sound('./Sounds/bow.mp3')
bowhit = pygame.mixer.Sound('./Sounds/bowhit.mp3')
bowhit2 = pygame.mixer.Sound('./Sounds/bowhit3.mp3')
Creeper_Dead = pygame.mixer.Sound('./Sounds/Creeper_Dead.mp3')
fizz = pygame.mixer.Sound('./Sounds/fizz.mp3')
fuse = pygame.mixer.Sound('./Sounds/fuse.mp3')
explode = pygame.mixer.Sound('./Sounds/explode.mp3')
hit = pygame.mixer.Sound('./Sounds/hit1.mp3')
music_mutation = pygame.mixer.Sound('./Sounds/inecraft_mutation.mp3')
portal_sound = pygame.mixer.Sound('./Sounds/portal.mp3')
cave_sound = pygame.mixer.Sound('./Sounds/cave1.mp3')
cave2_sound = pygame.mixer.Sound('./Sounds/cave2.mp3')
slime_sound = pygame.mixer.Sound('./Sounds/slime.mp3')
ignite = pygame.mixer.Sound('./Sounds/ignite.mp3')
trigger = pygame.mixer.Sound('./Sounds/trigger.mp3')
travel = pygame.mixer.Sound('./Sounds/travel.mp3')
explosion_sound = pygame.mixer.Sound('./Sounds/explosion.mp3')



gray = (123, 123, 123)
background = (18, 16, 20)

knockback_dx = 0
knockback_dy = 0
knockback_frames = 0
camera_shake_frames = 0

minecraft_font = pygame.font.Font('./minecraft.ttf', 100)

def distance(obj1, obj2):
    x1, y1 = obj1.rect.center
    x2, y2 = obj2.rect.center
    return math.hypot(x2 - x1, y2 - y1)




#Класси
class Background():
    def __init__(self, x, y, width, height, bg_color = gray):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.width = width
        self.height = height


class Object():
    def __init__(self, file_name, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.file_name = file_name
        self.width = width
        self.height = height
    def load_image(self):
        path_image = os.path.join(os.path.abspath(__file__ + "/.."), self.file_name)
        load_image = pygame.image.load(path_image)
        self.image = pygame.transform.scale(load_image, (self.width, self.height))

    def draw(self):
        window.blit(self.image, (self.rect.x + shake_offset[0], self.rect.y + shake_offset[1]))

    def collidePoint(self, x, y):
        return self.rect.collidepoint(x, y)
    
class Enemy():
    def __init__(self, file_name, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.file_name = file_name
        self.width = width
        self.height = height
    def load_image(self):
        path_image = os.path.join(os.path.abspath(__file__ + "/.."), self.file_name)
        load_image = pygame.image.load(path_image)
        self.image = pygame.transform.scale(load_image, (self.width, self.height))

    def draw(self):
        window.blit(self.image, (self.rect.x + shake_offset[0], self.rect.y + shake_offset[1]))

    def collidePoint(self, x, y):
        return self.rect.collidepoint(x, y)



class Dynamite(Object):
    def __init__(self, file_name, x, y, width, height):
        super().__init__(file_name, x, y, width, height)
        self.activated = False
        self.activation_time = None
        self.exploded = False
        self.explosion_effect_active = False
        self.explosion_effect_time = None

    def update(self, player):
        global knockback_dx, knockback_dy, knockback_frames, camera_shake_frames

        now = pygame.time.get_ticks()

        if self.activated and not self.exploded:
            if (now - self.activation_time) >= 4000:
                self.exploded = True
                self.explosion_effect_active = True
                self.explosion_effect_time = now
                explosion_sound.play()
                camera_shake_frames = 15

                self.image = pygame.image.load('./Textures/explode.png')
                self.image = pygame.transform.scale(self.image, (self.width, self.height))

                if distance(self, player) <= 250:
                    print("Игрок погиб от взрыва!")
                    Dead.play()
                    global player_dead
                    player_dead = True
                    player.image = pygame.image.load('./Textures/dead_Steve.png')
                    player.image = pygame.transform.scale(player.image, (player.width, player.height))

                    # Расчёт направления отталкивания
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery
                    dist = math.hypot(dx, dy)
                    if dist == 0:
                        dist = 1
                    dx /= dist
                    dy /= dist

                    # Задаём отскок на 15 кадров
                    knockback_dx = int(dx * 10)
                    knockback_dy = int(dy * 15)
                    knockback_frames = 25

            else:
                # Мигание
                if (now // 250) % 2 == 0:
                    self.image = pygame.image.load('./Textures/active_dynamite.png')
                else:
                    self.image = pygame.image.load('./Textures/dynamite.png')
                self.image = pygame.transform.scale(self.image, (self.width, self.height))

        elif self.explosion_effect_active:
            if now - self.explosion_effect_time >= 900:
                self.explosion_effect_active = False
                
                self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # Прозрачный


class AnimatedObject(Object):
    def __init__(self, frames, x, y, width, height, frame_duration=100):
        super().__init__(frames[0], x, y, width, height)
        self.frames = [pygame.transform.scale(pygame.image.load(f), (width, height)) for f in frames]
        self.frame_duration = frame_duration
        self.last_update = pygame.time.get_ticks()
        self.current_frame = 0
        self.image = self.frames[self.current_frame]

    def update_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]


def draw_buttons():
    respawn_button = pygame.Rect(800, 400, 300, 80)
    exit_button = pygame.Rect(800, 500, 300, 80)

    pygame.draw.rect(window, (0, 200, 0), respawn_button)
    pygame.draw.rect(window, (200, 0, 0), exit_button)

    rebirth_text = minecraft_font.render("REBIRTH", True, (255, 255, 255))
    exit_text = minecraft_font.render("EXIT", True, (255, 255, 255))

    window.blit(rebirth_text, (respawn_button.x + 70, respawn_button.y + 20))
    window.blit(exit_text, (exit_button.x + 100, exit_button.y + 20))

    return respawn_button, exit_button

def reset_game():
    lava_touch_time = None
    global player, player_vel_y, on_ground, player_dead, bows, dynamites, Creeper, Creeper_dead

    player.rect.x = 20
    player.rect.y = 1000
    player_vel_y = 0
    on_ground = False
    player_dead = False
    bows.clear()
    player.image = steve_alive
    player.image = pygame.transform.scale(player.image, (player.width, player.height))
    Creeper.rect.x = 100
    Creeper.rect.y = 100
    Creeper_dead = False
    

    for dynamite in dynamites:
        dynamite.activated = False
        dynamite.exploded = False
        dynamite.explosion_effect_active = False
        dynamite.load_image()
        




#Спрайти
player = Object('./Textures/Steve.png', 20, 1040, 42, 90)
player.load_image()
steve_alive = pygame.image.load('./Textures/Steve.png')
steve_alive = pygame.transform.scale(steve_alive, (player.width, player.height))
steve_dead = pygame.image.load('./Textures/dead_Steve.png')
steve_dead = pygame.transform.scale(steve_dead, (player.width, player.height))
burned_steve = pygame.image.load('./Textures/burned_Steve.png')
burned_steve = pygame.transform.scale(burned_steve, (player.width, player.height))
Creeper = Enemy('./Textures/Creeper.png', 100, 600, 160, 144)
Creeper.load_image()



stone = Object('./Textures/Stone.png', 0, 1140, 60, 60)
stone.load_image() 
stone2 = Object('./Textures/Stone.png', 60, 1140, 60, 60)
stone2.load_image()
stone3 = Object('./Textures/Stone.png', 120, 1140, 60, 60)
stone3.load_image()
stone4 = Object('./Textures/Stone.png', 180, 1140, 60, 60)
stone4.load_image()
stone5 = Object('./Textures/Stone.png', 240, 1140, 60, 60)
stone5.load_image()
stone6 = Object('./Textures/Stone.png', 300, 1140, 60, 60)
stone6.load_image()
stone7 = Object('./Textures/Stone.png', 540, 1080, 60, 60)
stone7.load_image()
stone8 = Object('./Textures/Stone.png', 660, 1140, 60, 60)
stone8.load_image()
stone9 = Object('./Textures/Stone.png', 720, 1140, 60, 60)
stone9.load_image() 
stone10 = Object('./Textures/Stone.png', 780, 1140, 60, 60)
stone10.load_image()
stone11 = Object('./Textures/Stone.png', 840, 1140, 60, 60)
stone11.load_image()
stone12 = Object('./Textures/Stone.png', 1080, 1140, 60, 60)
stone12.load_image()
stone13 = Object('./Textures/Stone.png', 1140, 1140, 60, 60)
stone13.load_image()

stone14 = Object('./Textures/Stone.png', 1200 , 1140, 60, 60)
stone14.load_image()

stone15 = Object('./Textures/Stone.png', 540, 1080, 60, 60)
stone15.load_image()

stone16 = Object('./Textures/Stone.png', 660, 1140, 60, 60)
stone16.load_image()

stones = [stone, stone2, stone3, stone4, stone5, stone6, stone7, stone8,
          stone9, stone10, stone11, stone12, stone13, stone14, stone15, stone16,

          
]

lava_frames = ['./lava_frames/lava_frame_0.png', './lava_frames/lava_frame_1.png', './lava_frames/lava_frame_2.png', './lava_frames/lava_frame_3.png', './lava_frames/lava_frame_4.png', './lava_frames/lava_frame_5.png', './lava_frames/lava_frame_6.png', './lava_frames/lava_frame_5.png', './lava_frames/lava_frame_4.png', './lava_frames/lava_frame_3.png', './lava_frames/lava_frame_2.png', './lava_frames/lava_frame_1.png']
lava = AnimatedObject(lava_frames, 360, 1150, 60, 50)
lava2 = AnimatedObject(lava_frames, 420, 1150, 60, 50)
lava3 = AnimatedObject(lava_frames, 480, 1150, 60, 50)
lava4 = AnimatedObject(lava_frames, 540, 1150, 60, 50)
lava5 = AnimatedObject(lava_frames, 600, 1000, 60, 50)
lava6 = AnimatedObject(lava_frames, 900, 1150, 60, 50)
lava7 = AnimatedObject(lava_frames, 960, 1150, 60, 50)
lava8 = AnimatedObject(lava_frames, 1020, 1150, 60, 50)

lavaa = [lava, lava2, lava3, lava4, lava5, lava6, lava7, lava8]



you_died_image = pygame.image.load('./Textures/You_died.png')
you_died_image = pygame.transform.scale(you_died_image, (600, 150))

btn_font = pygame.font.Font('./minecraft.ttf', 35)
btn_color = (70, 70, 70)
btn_hover_color = (100, 100, 100)
text_color = (255, 255, 255)


respawn_btn = pygame.Rect(800, 400, 300, 70)
exit_btn = pygame.Rect(800, 500, 300, 70)


player_dead = False  


dynamite = Dynamite('./Textures/dynamite.png', 700, 120, 60, 60)
dynamite.load_image()
dynamite2 = Dynamite('./Textures/dynamite.png', 800, 1000, 60, 60)
dynamite2.load_image()

dynamites = [dynamite, dynamite2]
players = [player]
bows = []



move_right = False
move_left = False

is_fullscreen = False

player_direction = 'right'
player_dead = False
Creeper_dead = False
player_vel_y = 0
Creeper_vel_y = 0
gravity = 1
jump_speed = -17
on_ground = False

lava_contact_time = None
lava_blink_timer = 0
lava_blink_interval = 600
lava_blink_state = False

program_work = True
while program_work:

    shake_offset = [0, 0]
    if camera_shake_frames > 0:
        shake_offset[0] = random.randint(-10, 10)
        shake_offset[1] = random.randint(-10, 10)
        camera_shake_frames -= 0.5


    window.fill(background)
    player.draw()
    old_rect = player.rect.copy()
    Creeper.draw()
    Creeper_old_rect = Creeper.rect.copy()
    keys = pygame.key.get_pressed()



    for bow in bows[:]:
        if bow.direction == 'right':
           bow.rect.x += 15
        else:
            bow.rect.x -= 15
        if bow.rect.right > 1920:
            bows.remove(bow)
            continue


        for stone in stones:
            if bow.rect.colliderect(stone.rect):
                bows.remove(bow)
                bowhit2.play()
                break

        for lava in lavaa:
            if bow.rect.colliderect(lava.rect) and not  getattr(bow, "on_fire", False):
                bow.file_name = './Textures/fire_bow.png'
                bow.load_image()
                bow.on_fire = True

                if bow.direction == 'left':
                    bow.image = pygame.transform.flip(bow.image, True, False)

        for dynamite in dynamites:
            if bow.rect.colliderect(dynamite.rect) and getattr(bow, "on_fire", False):
                if not dynamite.activated and not dynamite.exploded:
                    dynamite.activated = True
                    dynamite.activation_time = pygame.time.get_ticks()
                    bowhit.play()
                    fuse.play()
                    bows.remove(bow)
                    break
            if bow.rect.colliderect(dynamite.rect) and getattr(bow, "on_fire", False):
                if dynamite.activated and not dynamite.exploded:
                    bowhit.play()
                    
                    bows.remove(bow)
                    break
            if bow.rect.colliderect(dynamite.rect) and not getattr(bow, "on_fire", False):
                if not dynamite.activated and not dynamite.exploded:
                    bowhit.play()
                    
                    bows.remove(bow)
                    break
        
        if bow.rect.colliderect(Creeper):
            Creeper.rect.x = -1000
            bows.remove(bow)
            bowhit.play()
            Creeper_dead = True
    
                
    for bow in bows:
       bow.draw()


    for dynamite in dynamites:
        dynamite.update(player)
        dynamite.draw()
        

    if player_dead:
        # Отображаем "You Died"
        window.blit(you_died_image, (window.get_width() // 2 - 300, 200))

        # Отображаем кнопки
        mouse_pos = pygame.mouse.get_pos()

        for btn, text in [(respawn_btn, "Respawn"), (exit_btn, "Exit")]:
            color = btn_hover_color if btn.collidepoint(mouse_pos) else btn_color
            pygame.draw.rect(window, color, btn)
            label = btn_font.render(text, True, text_color)
            window.blit(label, (btn.x + btn.width // 2 - label.get_width() // 2,
                                btn.y + btn.height // 2 - label.get_height() // 2))

    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            program_work = False
        if event.type == pygame.KEYDOWN and not player_dead:
            if event.key == pygame.K_d:
                move_right = True
                player_direction = 'right'
            
            if event.key == pygame.K_a:
                move_left = True
                player_direction = 'left'
            if event.key == pygame.K_SPACE and on_ground:
                player_vel_y = jump_speed
                on_ground = False
            if event.key == pygame.K_F11:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    window = pygame.display.set_mode((1920, 1140))


        elif event.type == pygame.KEYUP and not player_dead:
            if event.key == pygame.K_d:
                move_right = False
            if event.key == pygame.K_a:
                move_left = False
            
            if event.key == pygame.K_e:
                bow = Object('./Textures/bow.png', player.rect.x - -40 // 2, player.rect.top + 25, 25, 8)
                bow.load_image()
                bow.direction = player_direction
                if bow.direction == 'left':
                    bow.image = pygame.transform.flip(bow.image, True, False)
                bows.append(bow)
                boww.play()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if player_dead:
                if respawn_btn.collidepoint(event.pos):
                    reset_game()
                elif exit_btn.collidepoint(event.pos):
                    program_work = False
                


    player_vel_y += gravity
    player.rect.y += player_vel_y

    if not Creeper_dead:

        Creeper_vel_y += gravity
        Creeper.rect.y += Creeper_vel_y

    if not player_dead:
        if move_right:
            player.rect.x += 6
        if move_left:
            player.rect.x -= 6

    
    if knockback_frames > 0:
        player.rect.x += knockback_dx
        player.rect.y += knockback_dy
        knockback_frames -= 1



    for stone in stones:
        
        if player.rect.colliderect(stone.rect):
            if old_rect.bottom <= stone.rect.top and player.rect.bottom > stone.rect.top:
                player.rect.bottom = stone.rect.top
                player_vel_y = 0
                on_ground = True
            elif old_rect.top >= stone.rect.bottom and player.rect.top < stone.rect.bottom:
                player.rect.top = stone.rect.bottom
                player_vel_y = 0
            elif old_rect.right <= stone.rect.left and player.rect.right > stone.rect.left:
                player.rect.right = stone.rect.left
            elif old_rect.left >= stone.rect.right and player.rect.left < stone.rect.right:
                player.rect.left = stone.rect.right

    for stone in stones: 
        if Creeper.rect.colliderect(stone.rect):
            if Creeper_old_rect.bottom <= stone.rect.top and Creeper.rect.bottom > stone.rect.top:
                Creeper.rect.bottom = stone.rect.top
                Creeper_vel_y = 0
                on_ground = True
            elif Creeper_old_rect.top >= stone.rect.bottom and Creeper.rect.top < stone.rect.bottom:
                Creeper.rect.top = stone.rect.bottom
                Creeper_vel_y = 0
            elif Creeper_old_rect.right <= stone.rect.left and Creeper.rect.right > stone.rect.left:
                Creeper.rect.right = stone.rect.left
            elif Creeper_old_rect.left >= stone.rect.right and Creeper.rect.left < stone.rect.right:
                Creeper.rect.left = stone.rect.right

        
        stone.draw()

    for dynamite in dynamites:
        if player.rect.colliderect(dynamite.rect):
            if not dynamite.activated and not dynamite.exploded:
                if old_rect.bottom <= dynamite.rect.top and player.rect.bottom > dynamite.rect.top:
                    player.rect.bottom = dynamite.rect.top
                    player_vel_y = 0
                    on_ground = True
                elif old_rect.top >= dynamite.rect.bottom and player.rect.top < dynamite.rect.bottom:
                    player.rect.top = dynamite.rect.bottom
                    player_vel_y = 0
                elif old_rect.right <= dynamite.rect.left and player.rect.right > dynamite.rect.left:
                    player.rect.right = dynamite.rect.left
                elif old_rect.left >= dynamite.rect.right and player.rect.left < dynamite.rect.right:
                    player.rect.left = dynamite.rect.right
            if dynamite.activated and not dynamite.exploded:
                if old_rect.bottom <= dynamite.rect.top and player.rect.bottom > dynamite.rect.top:
                    player.rect.bottom = dynamite.rect.top
                    player_vel_y = 0
                    on_ground = True
                elif old_rect.top >= dynamite.rect.bottom and player.rect.top < dynamite.rect.bottom:
                    player.rect.top = dynamite.rect.bottom
                    player_vel_y = 0
                elif old_rect.right <= dynamite.rect.left and player.rect.right > dynamite.rect.left:
                    player.rect.right = dynamite.rect.left
                elif old_rect.left >= dynamite.rect.right and player.rect.left < dynamite.rect.right:
                    player.rect.left = dynamite.rect.right



    now = pygame.time.get_ticks()

    for lava in lavaa:
        lava.update_animation()
        lava.draw()
        

        touching_lava = any(player.rect.colliderect(lava.rect) for lava in lavaa)

        if not player_dead:
            if player.rect.colliderect(lava):
                player_vel_y = -0.5
                player.image = pygame.image.load('./Textures/dead_Steve.png')
                player.image = pygame.transform.scale(player.image, (player.width, player.height))
        if player_dead:
            if player.rect.colliderect(lava):
                player_vel_y = -0.5
                
        
        if touching_lava and not player_dead:
            if lava_contact_time is None:
                lava_contact_time = now

        

            if now - lava_blink_timer >= lava_blink_interval:
                lava_blink_timer = now
                lava_blink_state = not lava_blink_state
                hit.play()
                fizz.play()
                if lava_blink_state:
                    player.image = pygame.image.load('./Textures/dead_Steve.png')
                else:
                    player.image = pygame.image.load('./Textures/Steve.png')
                player.image = pygame.transform.scale(player.image, (player.width, player.height))

            if now - lava_contact_time >= 1500:
                player_dead = True
                Dead.play()
                player.image = burned_steve
                player.image = pygame.transform.scale(player.image, (player.width, player.height))
            
                

        elif not touching_lava:
            lava_contact_time = None
            lava_blink_timer = 0
            lava_blink_state = False
            player.image = steve_alive
            player.image = pygame.transform.scale(player.image, (player.width, player.height))
            if player_dead:
                player.image = burned_steve
                player.image = pygame.transform.scale(player.image, (player.width, player.height))
        


            
        



    pygame.display.update()
    clock.tick(60)