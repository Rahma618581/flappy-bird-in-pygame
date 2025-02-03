import pygame as pg
import sys
import time
from bird import Bird
from pipe import Pipe
pg.init()
pg.mixer.init()  # Initialize the mixer for sound effects

class Game:
    def __init__(self):
        # Setting window config
        self.width = 600
        self.height = 768
        self.scale_factor = 1.5
        self.win = pg.display.set_mode((self.width, self.height))
        self.clock = pg.time.Clock()
        self.move_speed = 250
        self.start_monitoring = False
        self.score = 0
        self.font = pg.font.Font("assests/font.ttf", 24)
        self.score_text = self.font.render("Score: 0", True, (0, 0, 0))
        self.score_text_rect = self.score_text.get_rect(center=(100, 30))
        self.restart_text = self.font.render("Restart: 0", True, (0, 0, 0))
        self.restart_text_rect = self.restart_text.get_rect(center=(300, 700))
        self.bird = Bird(self.scale_factor)
        self.difficulty_message = self.show_difficulty_message = False
        self.message_display_time = 2  # Time to display message (seconds)
        self.message_timer = 0
        self.is_enter_pressed = False
        self.is_game_started = False  # Start the game only after level selection
        self.pipes = []
        self.pipe_generate_counter = 71
        self.setUpBgAndGround()
        self.level_threshold = 5
        self.max_increases = 20
        self.speed_increase_per_level = 10
        
        # Loading audio files
        self.dead_sound = pg.mixer.Sound("assests/sfx/dead.wav")
        self.score_sound = pg.mixer.Sound("assests/sfx/score.wav")
        self.flap_sound = pg.mixer.Sound("assests/sfx/flap.wav")

        self.showLevelSelectionScreen()

    def showLevelSelectionScreen(self):
        self.start_sound = pg.mixer.Sound("assests/sfx/start.wav")  # Load start sound
        self.start_sound.play()  # Play start sound

        level_screen_img = pg.image.load("assests/level2.png").convert()
        level_screen_img = pg.transform.scale(level_screen_img, (self.width, self.height))

        simple_button_rect = pg.Rect(self.width / 4 - 50, self.height / 2 - 50, 100, 50)
        medium_button_rect = pg.Rect(self.width / 2 - 50, self.height / 2 - 50, 100, 50)
        hard_button_rect = pg.Rect(3 * self.width / 4 - 50, self.height / 2 - 50, 100, 50)

        selected_level = None

        while selected_level is None:
            self.win.blit(level_screen_img, (0, 0))
            pg.draw.rect(self.win, (0, 255, 0), simple_button_rect)
            pg.draw.rect(self.win, (255, 255, 0), medium_button_rect)
            pg.draw.rect(self.win, (255, 0, 0), hard_button_rect)

            simple_text = self.font.render("Simple", True, (0, 0, 0))
            medium_text = self.font.render("Medium", True, (0, 0, 0))
            hard_text = self.font.render("Hard", True, (0, 0, 0))

            self.win.blit(simple_text, simple_button_rect.topleft)
            self.win.blit(medium_text, medium_button_rect.topleft)
            self.win.blit(hard_text, hard_button_rect.topleft)

            pg.display.update()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if simple_button_rect.collidepoint(event.pos):
                        selected_level = "simple"
                    elif medium_button_rect.collidepoint(event.pos):
                        selected_level = "medium"
                    elif hard_button_rect.collidepoint(event.pos):
                        selected_level = "hard"

        self.setGameDifficulty(selected_level)
        self.gameLoop()

    def setGameDifficulty(self, level):
        if level == "simple":
            self.move_speed = 200  # Slow pipe movement
            self.bird.flap_strength = -8  # Slower bird flap
            self.pipe_gap = 250  # Large gap between pipes
        elif level == "medium":
            self.move_speed = 300  # Medium pipe movement
            self.bird.flap_strength = -10  # Normal bird flap
            self.pipe_gap = 200  # Medium gap between pipes
        elif level == "hard":
            self.move_speed = 400  # Fast pipe movement
            self.bird.flap_strength = -12  # Stronger bird flap
            self.pipe_gap = 150  # Smallest gap between pipes

        self.is_game_started = True  # Start the game

    def gameLoop(self):
        last_time = time.time()
        while True:
            new_time = time.time()
            dt = new_time - last_time
            last_time = new_time

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN and self.is_game_started:
                    if event.key == pg.K_RETURN:
                        self.is_enter_pressed = True
                        self.bird.update_on = True
                    if event.key == pg.K_SPACE and self.is_enter_pressed:
                        self.bird.flap(dt)
                        self.flap_sound.play()  
                if event.type == pg.MOUSEBUTTONUP:
                    if self.restart_text_rect.collidepoint(pg.mouse.get_pos()):
                        self.restartGame()

            self.updateEverything(dt)
            self.checkCollisions()
            self.checkScore()
            self.drawEverything()
            pg.display.update()
            self.clock.tick(60)

    def restartGame(self):
        self.over_sound = pg.mixer.Sound("assests/sfx/over.wav")  
        self.over_sound.play()  

        self.score = 0
        self.score_text = self.font.render("Score: 0", True, (0, 0, 0))
        self.is_enter_pressed = False
        self.is_game_started = False
        self.bird.resetPosition()
        self.pipes.clear()
        self.pipe_generate_counter = 71
        self.bird.update_on = False

        self.showLevelSelectionScreen()

    def checkScore(self):
        if len(self.pipes) > 0:
            if self.bird.rect.left > self.pipes[0].rect_down.left and self.bird.rect.right < self.pipes[0].rect_down.right and not self.start_monitoring:
                self.start_monitoring = True
            if self.bird.rect.left > self.pipes[0].rect_down.right and self.start_monitoring:
                self.start_monitoring = False
                self.score += 1
                self.score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
                self.score_sound.play() 

    def checkCollisions(self):
        if len(self.pipes):
            if self.bird.rect.bottom > 568:
                self.bird.update_on = False
                self.is_enter_pressed = False
                self.is_game_started = False
                self.dead_sound.play()  
            if (self.bird.rect.colliderect(self.pipes[0].rect_down) or self.bird.rect.colliderect(self.pipes[0].rect_up)):
                self.is_enter_pressed = False
                self.is_game_started = False
                self.dead_sound.play()  
    def updateEverything(self, dt):
        if self.is_enter_pressed:
            # Moving the ground
            self.ground1_rect.x -= int(self.move_speed * dt)
            self.ground2_rect.x -= int(self.move_speed * dt)

            if self.ground1_rect.right < 0:
                self.ground1_rect.x = self.ground2_rect.right
            if self.ground2_rect.right < 0:
                self.ground2_rect.x = self.ground1_rect.right

            # Generating pipes
            if self.pipe_generate_counter > 70:
                self.pipes.append(Pipe(self.scale_factor, self.move_speed, self.pipe_gap))

                self.pipe_generate_counter = 0

            self.pipe_generate_counter += 1

            # Moving the pipes
            for pipe in self.pipes:
                pipe.update(dt)

            # Removing pipes if out of screen
            if len(self.pipes) != 0:
                if self.pipes[0].rect_up.right < 0:
                    self.pipes.pop(0)

            # Moving the bird
        self.bird.update(dt)
        # Check if difficulty message should still be displayed
        if self.show_difficulty_message:
            if time.time() - self.message_timer > self.message_display_time:
                self.show_difficulty_message = False  # Hide message after set time

    def drawEverything(self):
        self.win.blit(self.bg_img, (0, -300))
        for pipe in self.pipes:
            pipe.drawPipe(self.win)
        self.win.blit(self.ground1_img, self.ground1_rect)
        self.win.blit(self.ground2_img, self.ground2_rect)
        self.win.blit(self.bird.image, self.bird.rect)
        self.win.blit(self.score_text, self.score_text_rect)
        if not self.is_game_started:
            self.win.blit(self.restart_text, self.restart_text_rect)
        # Display the difficulty message if active
        if self.show_difficulty_message:
            difficulty_text = self.font.render(self.difficulty_message, True, (255, 0, 0))
            difficulty_text_rect = difficulty_text.get_rect(center=(self.width // 2, self.height // 2))
            self.win.blit(difficulty_text, difficulty_text_rect)
        # Display the "Nice try! Game is ended. Try again" message when the game ends
        if not self.is_game_started:
            end_text = self.font.render("Game is ended. Nice try!", True, (255, 0, 0))
            end_text_rect = end_text.get_rect(center=(self.width / 2, self.height // 2))
            self.win.blit(end_text, end_text_rect)

    def setUpBgAndGround(self):
        # Loading images for bg and ground
        self.bg_img = pg.transform.scale_by(pg.image.load("assests/bg.png").convert(), self.scale_factor)
        self.ground1_img = pg.transform.scale_by(pg.image.load("assests/ground.png").convert(), self.scale_factor)
        self.ground2_img = pg.transform.scale_by(pg.image.load("assests/ground.png").convert(), self.scale_factor)

        self.ground1_rect = self.ground1_img.get_rect()
        self.ground2_rect = self.ground2_img.get_rect()

        self.ground1_rect.x = 0
        self.ground2_rect.x = self.ground1_rect.right
        self.ground1_rect.y = 568
        self.ground2_rect.y = 568

game = Game()