# !/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os
import random
import threading
import json
import queue

try:
    from vosk import Model, KaldiRecognizer
    import sounddevice as sd
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False
    print("Voice recognition not available. Install with: pip install vosk sounddevice")

import pygame

pygame.init()

# Global Constants

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Chrome Dino Runner")

Ico = pygame.image.load("assets/DinoWallpaper.png")
pygame.display.set_icon(Ico)

RUNNING = [
    pygame.image.load(os.path.join("assets/Dino", "DinoRun1.png")),
    pygame.image.load(os.path.join("assets/Dino", "DinoRun2.png")),
]
JUMPING = pygame.image.load(os.path.join("assets/Dino", "DinoJump.png"))
DUCKING = [
    pygame.image.load(os.path.join("assets/Dino", "DinoDuck1.png")),
    pygame.image.load(os.path.join("assets/Dino", "DinoDuck2.png")),
]

SMALL_CACTUS = [
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus1.png")),
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus2.png")),
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus3.png")),
]
LARGE_CACTUS = [
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus1.png")),
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus2.png")),
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus3.png")),
]

BIRD = [
    pygame.image.load(os.path.join("assets/Bird", "Bird1.png")),
    pygame.image.load(os.path.join("assets/Bird", "Bird2.png")),
]

CLOUD = pygame.image.load(os.path.join("assets/Other", "Cloud.png"))

BG = pygame.image.load(os.path.join("assets/Other", "Track.png"))

FONT_COLOR=(0,0,0)

# Voice Control Setup
voice_command = None
voice_active = False
audio_queue = queue.Queue()

# Download small Vosk model if not present
def download_vosk_model():
    """Download a small Vosk model for English"""
    model_path = "vosk-model-small-en-us-0.15"
    if not os.path.exists(model_path):
        print("Downloading Vosk model (first time only, ~40MB)...")
        import zipfile
        import urllib.request
        
        url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        zip_path = "vosk-model.zip"
        
        try:
            urllib.request.urlretrieve(url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(".")
            os.remove(zip_path)
            print("Model downloaded successfully!")
        except Exception as e:
            print(f"Failed to download model: {e}")
            return None
    return model_path

def audio_callback(indata, frames, time, status):
    """Audio callback - OPTIMIZED FOR MINIMAL LATENCY"""
    # Suppress overflow warnings (they're normal with small buffers)
    if status and "overflow" not in str(status).lower():
        print(status)
    
    # CRITICAL: Keep queue small for low latency
    # If queue has more than 1 item, skip this chunk (use latest audio only)
    if audio_queue.qsize() > 1:
        try:
            audio_queue.get_nowait()  # Remove old audio
        except:
            pass
    
    audio_queue.put(bytes(indata))

def listen_for_voice():
    """Background thread - ULTRA LOW LATENCY MODE"""
    global voice_command, voice_active, VOICE_ENABLED
    
    if not VOICE_ENABLED:
        return
    
    try:
        # ULTRA LOW LATENCY: 800 samples = 50ms chunks!
        with sd.RawInputStream(samplerate=16000, blocksize=400, dtype='int16',
                               channels=1, callback=audio_callback):
            print("🎤 ULTRA LOW LATENCY MODE ACTIVE!")
            print("🗣️  Commands: JUMP | DOWN | START | STOP | GO")
            print("⚡ Target latency: <150ms\n")
            
            last_processed = ""
            last_command_time = 0
            
            while voice_active:
                try:
                    # Non-blocking get with minimal timeout
                    data = audio_queue.get(timeout=0.01)
                except:
                    continue
                
                import time
                current_time = time.time()
                
                # CRITICAL: Process PARTIAL results for instant response
                if recognizer.AcceptWaveform(data):
                    # Final result - only process if different from last partial
                    result = json.loads(recognizer.Result())
                    text = result.get('text', '').strip().lower()
                    
                    if text and text != '[unk]' and text != last_processed:
                        if (current_time - last_command_time) > 0.8:
                            process_voice_command(text)
                            last_processed = text
                            last_command_time = current_time
                else:
                    # PARTIAL RESULT - Process immediately but avoid duplicates
                    partial = json.loads(recognizer.PartialResult())
                    partial_text = partial.get('partial', '').strip().lower()
                    
                    # Only process if: new word AND enough time passed
                    if (partial_text and 
                        partial_text != '[unk]' and 
                        partial_text != last_processed and
                        (current_time - last_command_time) > 0.8):
                        
                        if process_voice_command(partial_text):
                            last_processed = partial_text
                            last_command_time = current_time
                            
    except Exception as e:
        print(f"❌ Voice error: {e}")

def process_voice_command(text):
    """Process voice command - INSTANT EXECUTION, NO DELAYS"""
    global voice_command
    
    text = text.strip().lower()
    
    # Show what was heard for debugging
    print(f"🎤 Heard: '{text}'", end=" → ")
    
    # ULTRA FAST: Direct comparison, no loops, immediate return
    # JUMP commands - HIGHEST PRIORITY (added similar-sounding words)
    if text in ['jump', 'chump', 'pump', 'dump', 'junk', 'hop', 'up']:
        if voice_command != "jump":  # Prevent spam
            voice_command = "jump"
            print("⚡ JUMP")
        else:
            print("(skip)")
        return True
    
    # DUCK commands (added similar-sounding words)
    if text in ['duck', 'dark', 'dock', 'tuck', 'down', 'crouch']:
        if voice_command != "duck":
            voice_command = "duck"
            print("⚡ DUCK")
        else:
            print("(skip)")
        return True
    
    # START commands
    if text in ['start', 'star', 'begin', 'play']:
        if voice_command != "start":
            voice_command = "start"
            print("⚡ START")
        else:
            print("(skip)")
        return True
    
    # PAUSE commands
    if text in ['pause', 'paws', 'stop']:
        if voice_command != "pause":
            voice_command = "pause"
            print("⚡ PAUSE")
        else:
            print("(skip)")
        return True
    
    # RESUME commands
    if text in ['resume', 'go']:
        if voice_command != "unpause":
            voice_command = "unpause"
            print("⚡ GO")
        else:
            print("(skip)")
        return True
    
    # QUIT commands
    if text in ['quit', 'quite', 'close', 'exit']:
        if voice_command != "quit":
            voice_command = "quit"
            print("⚡ QUIT GAME")
        else:
            print("(skip)")
        return True
    
    print("(ignored)")
    return False

# Initialize Vosk after function definitions
if VOICE_ENABLED:
    try:
        model_path = download_vosk_model()
        if model_path and os.path.exists(model_path):
            vosk_model = Model(model_path)
            # Use smaller sample rate for faster processing
            recognizer = KaldiRecognizer(vosk_model, 16000)
            
            # CRITICAL: Set grammar to restrict recognition to only game commands
            # This dramatically improves accuracy and speed
            # Added phonetically similar words to improve recognition
            grammar = '["jump", "chump", "pump", "dump", "junk", "hop", "up", "duck", "dark", "dock", "tuck", "down", "crouch", "start", "star", "begin", "pause", "paws", "stop", "resume", "go", "play", "quit", "quite", "close", "exit", "[unk]"]'
            recognizer.SetGrammar(grammar)
            
            print("✅ Vosk model loaded with command grammar!")
            
            # Start voice recognition immediately
            voice_active = True
            voice_thread = threading.Thread(target=listen_for_voice, daemon=True)
            voice_thread.start()
        else:
            VOICE_ENABLED = False
            print("Vosk model not found. Voice control disabled.")
    except Exception as e:
        VOICE_ENABLED = False
        print(f"Failed to initialize Vosk: {e}")

class Dinosaur:

    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        global voice_command
        
        # Check voice FIRST for instant response
        jump_triggered = (voice_command == "jump" or userInput[pygame.K_UP] or userInput[pygame.K_SPACE])
        duck_triggered = (voice_command == "duck" or userInput[pygame.K_DOWN])
        
        # Execute actions IMMEDIATELY
        if jump_triggered and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
            # Clear voice command instantly after triggering
            if voice_command == "jump":
                voice_command = None
        elif duck_triggered and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or duck_triggered):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False
            # Clear duck command when not ducking
            if voice_command == "duck":
                voice_command = None
        
        # Update animations
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    BIRD_HEIGHTS = [250, 290, 320]

    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = random.choice(self.BIRD_HEIGHTS)
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1


def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, voice_command, voice_active
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font("freesansbold.ttf", 20)
    obstacles = []
    death_count = 0
    pause = False

    def score():
        global points, game_speed, voice_command
        points += 1
        # DISABLED: Speed increase for constant game speed
        # if points % 100 == 0:
        #     game_speed += 1
        current_time = datetime.datetime.now().hour
        with open("score.txt", "r") as f:
            score_ints = [int(x) for x in f.read().split()]  
            highscore = max(score_ints)
            if points > highscore:
                highscore=points 
            text = font.render("High Score: "+ str(highscore) + "  Points: " + str(points), True, FONT_COLOR)
        textRect = text.get_rect()
        textRect.center = (900, 40)
        SCREEN.blit(text, textRect)
        
        # Show voice command indicator
        if VOICE_ENABLED:
            voice_font = pygame.font.Font("freesansbold.ttf", 16)
            if voice_command:
                voice_text = voice_font.render(f"🎤 Voice: {voice_command.upper()}", True, (0, 200, 0))
            else:
                voice_text = voice_font.render("🎤 Listening...", True, (100, 100, 100))
            voice_rect = voice_text.get_rect()
            voice_rect.center = (100, 40)
            SCREEN.blit(voice_text, voice_rect)

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    def unpause():
        nonlocal pause, run
        pause = False
        run = True

    def paused():
        nonlocal pause
        global voice_command
        pause = True
        font = pygame.font.Font("freesansbold.ttf", 30)
        text = font.render("Game Paused, Press 'u' or say 'unpause' to Resume", True, FONT_COLOR)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT  // 3)
        SCREEN.blit(text, textRect)
        pygame.display.update()

        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                    unpause()
            
            # Check for voice unpause command
            if voice_command == "unpause":
                voice_command = None
                unpause()
            
            # Check for voice quit command in pause menu
            if voice_command == "quit":
                voice_command = None
                voice_active = False
                pygame.quit()
                exit()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                voice_active = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                run = False
                paused()
        
        # Check for voice pause command
        if voice_command == "pause":
            voice_command = None
            run = False
            paused()
        
        # Check for voice quit command
        if voice_command == "quit":
            voice_command = None
            voice_active = False
            run = False
            pygame.quit()
            exit()

        current_time = datetime.datetime.now().hour
        if 7 < current_time < 19:
            SCREEN.fill((255, 255, 255))
        else:
            SCREEN.fill((0, 0, 0))
        userInput = pygame.key.get_pressed()

        player.draw(SCREEN)
        player.update(userInput)

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 2) == 2:
                obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                pygame.time.delay(2000)
                death_count += 1
                menu(death_count)

        background()

        cloud.draw(SCREEN)
        cloud.update()

        score()

        clock.tick(30)  # Back to 30 FPS for normal game speed
        pygame.display.update()


def menu(death_count):
    global points
    global FONT_COLOR
    global voice_command
    run = True
    while run:
        current_time = datetime.datetime.now().hour
        if 7 < current_time < 19:
            FONT_COLOR=(0,0,0)
            SCREEN.fill((255, 255, 255))
        else:
            FONT_COLOR=(255,255,255)
            SCREEN.fill((128, 128, 128))
        font = pygame.font.Font("freesansbold.ttf", 30)

        if death_count == 0:
            text = font.render("Press any Key or say 'Start' to Begin", True, FONT_COLOR)
        elif death_count > 0:
            text = font.render("Press any Key or say 'Start' to Restart", True, FONT_COLOR)
            score = font.render("Your Score: " + str(points), True, FONT_COLOR)
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)
            f = open("score.txt", "a")
            f.write(str(points) + "\n")
            f.close()
            with open("score.txt", "r") as f:
                score = (
                    f.read()
                )  # Read all file in case values are not on a single line
                score_ints = [int(x) for x in score.split()]  # Convert strings to ints
            highscore = max(score_ints)  # sum all elements of the list
            hs_score_text = font.render(
                "High Score : " + str(highscore), True, FONT_COLOR
            )
            hs_score_rect = hs_score_text.get_rect()
            hs_score_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
            SCREEN.blit(hs_score_text, hs_score_rect)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                main()
        
        # Check for voice start command
        if voice_command == "start":
            voice_command = None
            main()
   


t1 = threading.Thread(target=menu(death_count=0), daemon=True)
t1.start()
