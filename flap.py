import pygame
import numpy as np
from random import randint
from PIL import Image

pygame.init()

background_images = [pygame.image.load("sprites/background-day.png"), 
					pygame.image.load("sprites/background-night.png")]

bird_sprites = [[pygame.image.load("sprites/bluebird-downflap.png"), 
			pygame.image.load("sprites/bluebird-midflap.png"),
			pygame.image.load("sprites/bluebird-upflap.png"),
			pygame.image.load("sprites/bluebird-midflap.png")],
			[pygame.image.load("sprites/redbird-downflap.png"), 
			pygame.image.load("sprites/redbird-midflap.png"),
			pygame.image.load("sprites/redbird-upflap.png"),
			pygame.image.load("sprites/redbird-midflap.png")],
			[pygame.image.load("sprites/yellowbird-downflap.png"), 
			pygame.image.load("sprites/yellowbird-midflap.png"),
			pygame.image.load("sprites/yellowbird-upflap.png"),
			pygame.image.load("sprites/yellowbird-midflap.png")]
		]

base_sprite = pygame.image.load("sprites/base.png")
pipe_sprites = [pygame.image.load("sprites/pipe-green.png")]
pipe_sprites.append(pygame.transform.flip(pipe_sprites[0], False, True))
score_sprites = []
for i in range (10):
	score_sprites.append(pygame.image.load("sprites/" + str(i) + ".png"))
GO_sprite = pygame.image.load("sprites/gameover.png")

wing_sound = pygame.mixer.Sound("audio/wing.wav")
point_sound = pygame.mixer.Sound("audio/point.wav")
hit_sound = pygame.mixer.Sound("audio/hit.wav")

win_width, win_height = background_images[0].get_size()
win = pygame.display.set_mode((win_width, win_height))
clock = pygame.time.Clock()

fps = 30
gravity = 1
flap_speed = 3
scroll_vel = 4
night_day = randint(0,1)
totalPoints = 0

class bird_class():

	def __init__(self, x, y, color, fall_vel, dead):
		self.x = x
		self.y = y
		self.color = color
		self.fall_vel = fall_vel
		self.dead = dead

		self.jump_vel = 10

		self.angle = 0
		self.count = 0
		self.jump_count = 0
		self.is_jump = False

		self.sprite = pygame.transform.rotate(bird_sprites[self.color][self.count//flap_speed%4], self.angle)

		self.width = self.sprite.get_width()
		self.height = self.sprite.get_height()
		self.score = 0

	def draw(self, win):
		win.blit(self.sprite, (self.x, self.y))

	def animate(self):
		self.count += 1
		self.y -= self.fall_vel
		self.angle = 1.5*self.fall_vel
		self.sprite = pygame.transform.rotate(bird_sprites[self.color][self.count//flap_speed%4], self.angle)
		self.fall_vel -= gravity
		self.jump_count += 1

	def jump(self):
		if self.jump_count > 4 and not(self.is_jump):
			self.fall_vel = self.jump_vel
			pygame.mixer.find_channel().play(wing_sound)
			self.jump_count = 0

	def hitbox(self):
		self.box = pygame.Rect(self.x, self.y, self.width, self.height)

class base_class():

	def __init__(self, x, y, vel):
		self.x = x
		self.y = y
		self.vel = vel

		self.sprite = base_sprite
		self.width = self.sprite.get_width()
		self.height = self.sprite.get_height()

	def draw(self, win):
		win.blit(self.sprite, (self.x, self.y))

	def animate(self):
		self.x -= self.vel
		if self.x - self.vel < -self.width:
			self.x = self.width

	def hitbox(self):
		self.box = pygame.Rect(self.x, self.y, self.width, self.height)

class pipe_class():

	def __init__(self, x, y, vel):
		self.x = x
		self.y = y
		self.vel = vel

		self.imbottom = pipe_sprites[0]
		self.imtop = pipe_sprites[1]
		self.height = self.imbottom.get_height()
		self.width = self.imbottom.get_width()
		self.left = False
		self.score = False

	def draw(self, win):
		win.blit(self.imbottom, (self.x, self.y))
		win.blit(self.imtop, (self.x, self.y - self.height - 100))

	def animate(self):
		self.x -= self.vel

	def hitbox(self):
		self.bottombox = pygame.Rect(self.x, self.y, self.width, self.height)
		self.topbox = pygame.Rect(self.x, self.y - self.height - 100, self.width, self.height)

class score_class():
	def __init__(self, x, y, points):
		self.x = x
		self.y = y
		self.points = points

		self.width = score_sprites[0].get_width()
		self.height = score_sprites[0].get_height()

	def draw(self, win):
		win.blit(score_sprites[self.points%10], (self.x - self.width//2, self.y))

class GO_class():

	def __init__(self, x, y):
		self.x = x
		self.y = y

		self.sprite = GO_sprite
	
	def draw(self, win):
		win.blit(self.sprite, (self.x, self.y))
		pygame.mixer.find_channel().play(hit_sound)

def reset():
	global bird
	global bases
	global pipes
	global GO
	bird = bird_class(win_width//4, win_height//2, randint(0,2), 0, False)
	bases = [base_class(0, 4*win_height//5, scroll_vel)]
	bases.append(base_class(bases[0].width, 4*win_height//5, scroll_vel))
	pipes = [pipe_class(win_width, win_height//2, scroll_vel)]
	GO = GO_class(win_width//2 - GO_sprite.get_width()//2, 100)

reset()

def spawn_pipe():
	rand_height = 0
	while rand_height < 150 or rand_height > win_height - bases[0].height - 50:
		rand_height = np.random.normal(win_height//2 - bases[0].height//2 + 50, 100)
	for pipe in pipes:
		if pipe.x + pipe.width < win_width//2 and not(pipe.left):
			pipes.append(pipe_class(win_width, rand_height, scroll_vel))
			pipe.left = True
		elif pipe.x + pipe.width < 0:
			pipes.pop(0)
			pipe.left = False

def point():
	for pipe in pipes:
		if pipe.x < bird.x and not(pipe.score):
			pygame.mixer.find_channel().play(point_sound)
			pipe.score = True
			bird.score += 1

def collision():
	for base in bases:
		if bird.box.colliderect(base.box):
			bird.dead = True

	for pipe in pipes:
		if bird.box.colliderect(pipe.bottombox) or bird.box.colliderect(pipe.topbox):
			bird.dead = True

	if bird.y < 0:
		bird.dead = True

def animate():
	bird.animate()
	bird.hitbox()
	for base in bases:
		base.animate()
		base.hitbox()
	for pipe in pipes:
		pipe.animate()
		pipe.hitbox()

def redrawGamewindow():
	win.blit(background_images[night_day%2], (0, 0))

	for pipe in pipes:
		pipe.draw(win)
	for base in bases:
		base.draw(win)

	bird.draw(win)

	scorecards = []
	digs = len(str(bird.score))
	for i in range(digs):
		scorecards.append(score_class(win_width//2 - int((score_sprites[0].get_width() + 1)*(digs - i - 1)), 60, int(str(bird.score)[i])))

	for card in scorecards:
		card.draw(win)

	if bird.dead:
		GO.draw(win)

	pygame.display.update()

run = True

while run:

	clock.tick(fps)
	keys = pygame.key.get_pressed()

	for event in pygame.event.get():
		if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
			run = False

	if not(bird.dead):
		if keys[pygame.K_SPACE]:
			bird.jump()
			bird.is_jump = True
		else:
			bird.is_jump = False

		point()
		spawn_pipe()
		animate()
		collision()
		redrawGamewindow()

	if bird.dead and (keys[pygame.K_RETURN] or keys[pygame.K_SPACE]):
			reset()

pygame.quit()
