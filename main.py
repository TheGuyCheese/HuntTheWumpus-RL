import pygame
import random
import sys
import os
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 60
GRID_SIZE = 10
WIDTH = CELL_SIZE * GRID_SIZE
HEIGHT = CELL_SIZE * GRID_SIZE
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hunt the Wumpus")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
DARK_GRAY = (64, 64, 64)

# Game States
MENU = "menu"
PLAYING = "playing"
WON = "won"
LOST = "lost"
INSTRUCTIONS = "instructions"

# Load and scale images
def load_image(name):
    try:
        path = os.path.join('assets', f'{name}.png')
        image = pygame.image.load(path)
        return pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
    except:
        surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
        surface.fill(WHITE)
        pygame.draw.rect(surface, BLACK, surface.get_rect(), 1)
        print(f"Couldn't load image {name}, using fallback")
        return surface

# Game assets
IMAGES = {
    'empty': load_image('empty'),
    'agent': load_image('agent'),
    'wumpus': load_image('wumpus'),
    'pit': load_image('pit'),
    'gold': load_image('gold'),
    'breeze': load_image('breeze'),
    'stench': load_image('stench')
}

# Load sounds
def load_sounds():
    pygame.mixer.init()
    sounds = {}
    sound_files = {
        'move': 'step.wav',
        'gold': 'gold.wav',
        'death': 'death.wav',
        'win': 'win.wav'
    }
    for sound_name, file_name in sound_files.items():
        try:
            path = os.path.join('assets', file_name)
            sounds[sound_name] = pygame.mixer.Sound(path)
        except:
            print(f"Couldn't load sound {file_name}")
            sounds[sound_name] = None
    return sounds

SOUNDS = load_sounds()

class Game:
    def __init__(self):
        self.reset_game()
        self.game_state = MENU
        self.message = None
        self.message_timer = 0
        self.last_direction = (0, 1)  # Default facing right

    def reset_game(self):
        self.grid = [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.player_pos = [GRID_SIZE-1, 0]
        self.wumpus_pos = None
        self.gold_pos = None
        self.pits = []
        self.score = 0  # Start from 0
        self.game_state = PLAYING
        self.has_gold = False
        self.visited_cells = {(GRID_SIZE-1, 0)}
        self.arrows = 1  # Start with 1 arrow
        self.last_direction = (0, 1)
        self.message = None
        self.message_timer = 0
        self.initialize_game()

    def initialize_game(self):
        # Place Wumpus
        self.wumpus_pos = [random.randint(0, GRID_SIZE-2), random.randint(0, GRID_SIZE-1)]
        
        # Place Gold
        while True:
            pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
            if pos != self.wumpus_pos and pos != self.player_pos:
                self.gold_pos = pos
                break
        
        # Place Pits
        num_pits = GRID_SIZE
        for _ in range(num_pits):
            while True:
                pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
                if (pos != self.wumpus_pos and pos != self.gold_pos and 
                    pos != self.player_pos and pos not in self.pits):
                    self.pits.append(pos)
                    break

    def shoot_arrow(self):
        if self.arrows <= 0:
            self.show_message("No arrows left!", 60)
            return

        # Get the target position based on player's facing direction
        dx, dy = self.last_direction
        target_x = self.player_pos[0] + dx
        target_y = self.player_pos[1] + dy

        # Check if we hit the wumpus
        if [target_x, target_y] == self.wumpus_pos:
            self.show_message("You killed the Wumpus! +2 arrows!", 60)
            self.wumpus_pos = None  # Remove the wumpus
            self.arrows += 2  # Get 2 more arrows for a successful hit
            self.score += 200  # Better bonus for killing wumpus
            if SOUNDS['death']:
                SOUNDS['death'].play()
        else:
            self.show_message("Oh you missed!", 60)

        self.arrows -= 1  # Use up one arrow

    def show_message(self, text, duration):
        self.message = text
        self.message_timer = duration

    def move_player(self, dx, dy):
        if self.game_state != PLAYING:
            return

        # Update facing direction if moving
        if (dx, dy) != (0, 0):
            self.last_direction = (dx, dy)

        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy
        
        if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
            self.player_pos = [new_x, new_y]
            if SOUNDS['move']:
                SOUNDS['move'].play()
            
            self.visited_cells.add((new_x, new_y))
            self.score += 5  # Points for exploring
            
            if self.has_gold:
                self.score += 10  # Better bonus for moving with gold
            
            self.check_current_position()

    def check_current_position(self):
        pos = self.player_pos
        
        # Check for Wumpus or Pit (game over conditions)
        if pos == self.wumpus_pos or pos in self.pits:
            self.game_state = LOST
            if SOUNDS['death']:
                SOUNDS['death'].play()
            # Auto-restart after 2 seconds
            pygame.time.set_timer(pygame.USEREVENT + 1, 2000, loops=1)
            return

        # Check for Gold
        if pos == self.gold_pos and not self.has_gold:
            self.has_gold = True
            if SOUNDS['gold']:
                SOUNDS['gold'].play()
            self.score += 1000  # Better bonus for collecting gold
        
        # Check for Win (back at start with gold)
        if self.has_gold and pos == [GRID_SIZE-1, 0]:
            self.game_state = WON
            if SOUNDS['win']:
                SOUNDS['win'].play()
            self.score += 2000  # Better bonus for winning
            # Auto-restart after 2 seconds
            pygame.time.set_timer(pygame.USEREVENT + 1, 2000, loops=1)

    def is_adjacent_to_wumpus(self, pos):
        x, y = pos
        wx, wy = self.wumpus_pos
        return abs(x - wx) + abs(y - wy) == 1

    def is_adjacent_to_pit(self, pos):
        x, y = pos
        for pit_x, pit_y in self.pits:
            if abs(x - pit_x) + abs(y - pit_y) == 1:
                return True
        return False

    def draw(self, screen):
        screen.fill(BLACK)
        
        if self.game_state == MENU:
            self.draw_menu(screen)
        elif self.game_state == INSTRUCTIONS:
            self.draw_instructions(screen)
        else:
            self.draw_game(screen)

    def draw_menu(self, screen):
        # Draw background
        screen.fill(BLACK)
        
        # Create gradient effect
        for i in range(HEIGHT):
            alpha = int(255 * (1 - i/HEIGHT))
            gradient = pygame.Surface((WIDTH, 2))
            gradient.fill(PURPLE)
            gradient.set_alpha(alpha)
            screen.blit(gradient, (0, i))

        # Draw title with shadow effect
        font = pygame.font.SysFont('arial', 64, bold=True)
        title_shadow = font.render('Hunt the Wumpus', True, PURPLE)
        title = font.render('Hunt the Wumpus', True, GOLD)
        
        shadow_pos = title_shadow.get_rect(center=(WIDTH//2 + 4, HEIGHT//4 + 4))
        title_pos = title.get_rect(center=(WIDTH//2, HEIGHT//4))
        
        screen.blit(title_shadow, shadow_pos)
        screen.blit(title, title_pos)

        # Draw menu options with hover effect
        font = pygame.font.SysFont('arial', 32)
        mouse_pos = pygame.mouse.get_pos()
        
        # Play button
        play_text = font.render('Play Game', True, WHITE)
        play_rect = play_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        if play_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, DARK_GRAY, play_rect.inflate(20, 10))
            play_text = font.render('Play Game', True, GOLD)
        screen.blit(play_text, play_rect)
        
        # Instructions button
        inst_text = font.render('Instructions', True, WHITE)
        inst_rect = inst_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
        if inst_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, DARK_GRAY, inst_rect.inflate(20, 10))
            inst_text = font.render('Instructions', True, GOLD)
        screen.blit(inst_text, inst_rect)
        
        # Quit button
        quit_text = font.render('Quit', True, WHITE)
        quit_rect = quit_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 120))
        if quit_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, DARK_GRAY, quit_rect.inflate(20, 10))
            quit_text = font.render('Quit', True, GOLD)
        screen.blit(quit_text, quit_rect)

        # Draw decorative elements
        pygame.draw.line(screen, GOLD, (WIDTH//4, HEIGHT//3), (3*WIDTH//4, HEIGHT//3), 2)
        pygame.draw.line(screen, GOLD, (WIDTH//4, HEIGHT*2//3), (3*WIDTH//4, HEIGHT*2//3), 2)

    def draw_instructions(self, screen):
        screen.fill(BLACK)
        
        # Draw title
        font = pygame.font.SysFont('arial', 48)
        title = font.render('How to Play', True, GOLD)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 50)))

        # Draw instructions
        font = pygame.font.SysFont('arial', 24)
        instructions = [
            "Use WASD keys to move your character",
            "Collect the gold (yellow) and return to start",
            "Avoid the Wumpus (red) and pits (gray)",
            "Feel a breeze near pits",
            "Smell a stench near the Wumpus",
            "Press SPACE to shoot an arrow",
            "Press ESC to return to menu"
        ]
        
        y = 150
        for line in instructions:
            text = font.render(line, True, WHITE)
            rect = text.get_rect(center=(WIDTH//2, y))
            # Draw text shadow
            shadow = font.render(line, True, DARK_GRAY)
            screen.blit(shadow, rect.move(2, 2))
            screen.blit(text, rect)
            y += 50

        # Draw decorative frame
        pygame.draw.rect(screen, GOLD, (50, 100, WIDTH-100, HEIGHT-150), 2)

    def draw_game(self, screen):
        screen.fill(BLACK)
        
        # Draw grid and game elements
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                cell_rect = pygame.Rect(j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                if (i, j) in self.visited_cells:
                    pygame.draw.rect(screen, DARK_GRAY, cell_rect)
                    
                    # Draw breeze
                    if self.is_adjacent_to_pit((i, j)):
                        screen.blit(IMAGES['breeze'], (j*CELL_SIZE, i*CELL_SIZE))
                    
                    # Draw stench
                    if self.wumpus_pos and self.is_adjacent_to_wumpus((i, j)):
                        screen.blit(IMAGES['stench'], (j*CELL_SIZE, i*CELL_SIZE))
                    
                    # Draw entities
                    if [i, j] == self.player_pos:
                        # Rotate player image based on facing direction
                        angle = 0
                        if self.last_direction == (-1, 0):  # Up
                            angle = 90
                        elif self.last_direction == (1, 0):  # Down
                            angle = -90
                        elif self.last_direction == (0, -1):  # Left
                            angle = 180
                        rotated_player = pygame.transform.rotate(IMAGES['agent'], angle)
                        screen.blit(rotated_player, (j*CELL_SIZE, i*CELL_SIZE))
                    if self.wumpus_pos and [i, j] == self.wumpus_pos:
                        screen.blit(IMAGES['wumpus'], (j*CELL_SIZE, i*CELL_SIZE))
                    if [i, j] == self.gold_pos:
                        screen.blit(IMAGES['gold'], (j*CELL_SIZE, i*CELL_SIZE))
                    if [i, j] in self.pits:
                        screen.blit(IMAGES['pit'], (j*CELL_SIZE, i*CELL_SIZE))
                
                pygame.draw.rect(screen, WHITE, cell_rect, 1)
        
        # Draw score and arrows
        font = pygame.font.SysFont('arial', 24)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        screen.blit(score_text, (10, HEIGHT - 30))

        # Draw arrow count
        arrow_text = font.render(f'Arrows: {self.arrows}', True, WHITE)
        screen.blit(arrow_text, (WIDTH - 120, HEIGHT - 30))

        # Draw message if exists
        if self.message and self.message_timer > 0:
            message_text = font.render(self.message, True, GOLD)
            screen.blit(message_text, message_text.get_rect(center=(WIDTH//2, 30)))
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = None

        # Draw game over message
        if self.game_state in [WON, LOST]:
            s = pygame.Surface((WIDTH, HEIGHT))
            s.set_alpha(128)
            s.fill(BLACK)
            screen.blit(s, (0, 0))
            
            font = pygame.font.SysFont('arial', 48)
            if self.game_state == WON:
                msg = 'You Won!'
                color = GOLD
            else:
                msg = 'Game Over'
                color = RED
            text = font.render(msg, True, color)
            screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))
            
            font = pygame.font.SysFont('arial', 24)
            restart = font.render('Restarting...', True, WHITE)
            screen.blit(restart, restart.get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))

def main():
    game = Game()
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if game.game_state == MENU:
                        mouse_pos = pygame.mouse.get_pos()
                        play_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 - 20, 100, 40)
                        if play_rect.collidepoint(mouse_pos):
                            game.reset_game()
                        inst_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 40, 100, 40)
                        if inst_rect.collidepoint(mouse_pos):
                            game.game_state = INSTRUCTIONS
                        quit_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 100, 100, 40)
                        if quit_rect.collidepoint(mouse_pos):
                            running = False
            
            elif event.type == pygame.KEYDOWN:
                if game.game_state == MENU:
                    if event.key == pygame.K_SPACE:
                        game.reset_game()
                    elif event.key == pygame.K_i:
                        game.game_state = INSTRUCTIONS
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                
                elif game.game_state == INSTRUCTIONS:
                    if event.key == pygame.K_ESCAPE:
                        game.game_state = MENU
                
                elif game.game_state == PLAYING:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        game.move_player(-1, 0)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        game.move_player(1, 0)
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        game.move_player(0, -1)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        game.move_player(0, 1)
                    elif event.key == pygame.K_SPACE:
                        game.shoot_arrow()
                    elif event.key == pygame.K_ESCAPE:
                        game.game_state = MENU
                
                elif game.game_state in [WON, LOST]:
                    if event.key == pygame.K_SPACE:
                        game.game_state = MENU
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            elif event.type == pygame.USEREVENT + 1:  # Auto-restart timer
                game.game_state = MENU
                game.reset_game()
        
        game.draw(SCREEN)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()