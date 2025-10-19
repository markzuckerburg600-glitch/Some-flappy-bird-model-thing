import os
from sys import exit
import random
import pygame
import numpy as np
from time import sleep
pygame.init()
pygame.mixer.init()

class Birdgame():
    def __init__(self, render = False):
        self.render = render
        if render == False:
            # Create dummy environment if not render
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        if render:
            # Sounds
            # self.song = pygame.mixer.music.load("2016music.wav")
            # pygame.mixer.music.set_volume(0.9)
            # pygame.mixer.music.play(-1)
            # self.jump_sound = pygame.mixer.Sound("sound.wav")
            # self.jump_sound.set_volume(1)
            # self.death_sound = pygame.mixer.Sound("gta_death.wav")
            # self.death_sound.set_volume(0.7)       
            pygame.display.set_caption("Flappy Rat")
        self.screen = pygame.display.set_mode((1300, 1000))
        self.top_level = 20
        self.ground_level = 770
        if render:
            self.test_font = pygame.font.SysFont("Impact",50)
            self.game_over_text = self.test_font.render("Game Over", False, "White")
            self.press_space = self.test_font.render("Press Space to Retry", False, "White")
        self.clock = pygame.time.Clock()
            # Background
        self.background = pygame.image.load("flap_background.jpg")
        self.resized_background = pygame.transform.smoothscale(self.background, (1300,1000))
        self.background_rect = self.resized_background.get_rect(midleft=(0,450))

            # Player
        self.player_surface = pygame.image.load("rat.png").convert_alpha()
        self.resized_player = pygame.transform.smoothscale(self.player_surface, (70,70))
        self.player_rect = self.resized_player.get_rect(midleft=(450,280))

        self.player_gravity = 0
        self.background_speed = -5
        self.bg_x = 0

        self.new_val = 0
        self.game_timer = 0
        self.y_velocity = 0

            # create initial traps
        self.traps = self.create_traps(3)
        self.start_seconds = 0
        self.score = True
        self.game_active = True
        self.just_jumped = False
        self.bird_y = 0
        self.y_velocity = 0
        self.pipe_y = 0
        self.pipe_x = 0
        self.reward = 0

    def create_traps(self, num_traps, start_x=1500, spacing=600):
        traps = []
        for i in range(num_traps):
            rat_trap = pygame.image.load("rattrap.png")
            resized_rat_trap = pygame.transform.smoothscale(rat_trap, (80,400))

            top_rat_trap = pygame.image.load("rattrap2.png")
            resized_top_trap = pygame.transform.rotate(pygame.transform.smoothscale(top_rat_trap, (80,400)), 180)

            trap_gap = random.randint(980,1000)
            trap_height = random.randint(800,850)

            rat_trap_rect = resized_rat_trap.get_rect(midbottom=(start_x + i*spacing, trap_height))
            top_rat_trap_rect = resized_top_trap.get_rect(midtop=(start_x + i*spacing, trap_height - trap_gap))
            hit_box_rect = rat_trap_rect.inflate(-10,-15)
            top_hit_box_rect = top_rat_trap_rect.inflate(-10,-15)

            traps.append({
                "resized_trap": resized_rat_trap,
                "resized_top_trap": resized_top_trap,
                "rat_rect": rat_trap_rect,
                "top_rect": top_rat_trap_rect,
                "hit_box": hit_box_rect,
                "top_hit_box": top_hit_box_rect,
                "passed": False
            })
        return traps

    def reset_position(self, traps):
        for trap in self.traps:
            if trap["rat_rect"].x <= 0:
                trap["rat_rect"].right = 1800
                trap["top_rect"].right = 1800
                trap["hit_box"].right = 1800
                trap["top_hit_box"].right = 1800
                trap["passed"] = False
        return traps

    def get_state(self):
        self.bird_y = self.player_rect.centery
        # X distance to closest pipe
        pipe_x_list = [trap["hit_box"].left - self.player_rect.centerx for trap in self.traps]
        self.pipe_x = min(pipe_x_list)

        # Closest pipe index
        distances = [trap["hit_box"].x for trap in self.traps]
        min_index = np.argmin(distances)

        # Y distance to closest pipe
        self.pipe_y = self.traps[min_index]["hit_box"].top - self.player_rect.centery
        self.pipe_bottom = self.traps[min_index]["hit_box"].bottom - self.player_rect.centery
        self.bird_y = ((self.bird_y - 500) / 500)
        self.y_velocity = self.y_velocity / 30
        self.pipe_x = (self.pipe_x - 750) / 750
        self.pipe_y = (self.pipe_y / 400)
        self.pipe_bottom = (self.pipe_bottom/400)

        output = [self.bird_y, self.y_velocity, self.pipe_x, self.pipe_y, self.pipe_bottom]
        return output

    def reset_game(self):
        self.game_active = True
        self.score = True
        self.traps = self.create_traps(3,start_x = 1500, spacing = 600)  
        self.start_seconds = 0
        self.game_timer = 0
        self.player_gravity = 0
        self.player_rect = self.resized_player.get_rect(midleft =(450,280))
        self.new_val = 0
        self.background_speed = -5
        for trap in self.traps:
            trap["passed"] = False 


    # Game loop, probably should use this for viewing 
    def run(self, action):
        reward = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not self.game_active and self.render:
                    self.game_active = True
                    self.score = True
                    self.traps = self.create_traps(3)  
                    self.start_seconds = 0
                    self.game_timer = 0
                    self.player_gravity = 0
                    self.player_rect = self.resized_player.get_rect(midleft =(450,280))
                    self.new_val = 0
                    self.background_speed = -5 
                    pygame.mixer.music.play()

            if self.game_active:
                if action == 1:
                    self.player_gravity = -10
                    self.jump_sound.play()
                dt = self.clock.tick(60)/1000
                self.y_velocity += self.player_gravity * dt
                self.player_gravity += 1
                self.player_rect.bottom += int(self.player_gravity)

                self.start_seconds = pygame.time.get_ticks()
                elapsed_time = self.start_seconds/1000
                if elapsed_time >= self.game_timer + 8:
                    self.background_speed -= 0.5
                    self.game_timer = elapsed_time 

                # Check collisions with top/bottom
                if self.player_rect.bottom <= self.top_level or self.player_rect.top >= self.ground_level:
                    self.death_sound.play()
                    pygame.mixer.music.stop()
                    reward -= 10
                    self.game_active = False

                # Update traps
                for trap in self.traps:
                    trap["rat_rect"].x += self.background_speed
                    trap["top_rect"].x += self.background_speed
                    trap["hit_box"].x += self.background_speed
                    trap["top_hit_box"].x += self.background_speed

                    # Increment score
                    if not trap["passed"] and self.player_rect.left >= trap["hit_box"].right:
                        self.new_val += 1
                        reward += 5
                        trap["passed"] = True

                self.reset_position(self.traps)

            self.screen.blit(self.resized_background, (self.bg_x,0))
            self.screen.blit(self.resized_player, self.player_rect)
            for trap in self.traps:
                self.screen.blit(trap["resized_trap"], trap["rat_rect"])
                self.screen.blit(trap["resized_top_trap"], trap["top_rect"])

                # If we hit a mousetrap we die
            for trap in self.traps:
                if trap["hit_box"].colliderect(self.player_rect) or trap["top_hit_box"].colliderect(self.player_rect):
                    self.death_sound.play()
                    pygame.mixer_music.stop()
                    self.game_active = False
                    reward -= 10
                    break

            if self.game_active == False:
                self.screen.blit(self.game_over_text,(550,200))
                score_board = self.test_font.render(f"Score: {self.new_val}", False, "White")
                self.screen.blit(score_board, (575,10))
                self.screen.blit(self.resized_background,(1300,1000))
                self.screen.blit(self.resized_player,self.player_rect)
                self.screen.blit(self.press_space, (460,400))
                if self.score == True:
                    print(f"Your score is {self.new_val}")
                    self.score = False

            elif not self.game_active:
                self.reset_game()
                next_state = self.get_state
                return next_state, reward, False
            pygame.display.update()
            pygame.display.flip
            self.clock.tick(60)

    # Use this for training. It's only one frame of the game, but model learns very quickly this way
    def step(self, action):
        pygame.display.update()
        pygame.display.flip()
        if self.render:
            self.screen.blit(self.resized_background, (self.bg_x,0))
            self.screen.blit(self.resized_player, self.player_rect)
            for trap in self.traps:
                self.screen.blit(trap["resized_trap"], trap["rat_rect"])
                self.screen.blit(trap["resized_top_trap"], trap["top_rect"])

        self.reward = 0
        self.reward += 0.1
        self.reset_position(self.traps)
        # Apply the action
        if action == 1:
            self.player_gravity = -10
            self.just_jumped = True
            self.reward -= 0.05
            dt = 0
            # if self.render:
            #     self.jump_sound.play()
        # Update physics
        dt = self.clock.tick(60)/1000
        self.y_velocity += (self.player_gravity * dt)/30
        self.player_gravity += 1
        self.player_rect.bottom += int(self.player_gravity)
        
        # Move traps
        for trap in self.traps:
            trap["rat_rect"].x += self.background_speed
            trap["top_rect"].x += self.background_speed
            trap["hit_box"].x += self.background_speed
            trap["top_hit_box"].x += self.background_speed
            if self.player_rect.left > trap["hit_box"].right and not trap["passed"]:
                self.reward += 3
                trap["passed"] = True
        # Check collisions
        for trap in self.traps:
            if self.player_rect.colliderect(trap["hit_box"]) or self.player_rect.colliderect(trap["top_hit_box"]):
                self.game_active = False
                self.reward -= 5
                next_state = self.get_state()
                return next_state, self.reward, self.game_active
        if self.player_rect.bottom <= self.top_level or self.player_rect.top >= self.ground_level:
            self.reward -= 7
            self.game_active = False
            next_state = self.get_state()
            return next_state, self.reward, self.game_active

        # Return everything
        next_state = self.get_state()
        return next_state, self.reward, self.game_active
