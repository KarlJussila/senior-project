import pygame as pg
from os import path
from settings import *
vec = pg.math.Vector2

# Player sprite class
class Player(pg.sprite.Sprite):
	def __init__(self, game, x, y, w = TILESIZE * 0.75, h = TILESIZE * 0.75, facing = 'n'):
		# Setting groups
		self.groups = game.all_sprites
		# Initialize sprite
		pg.sprite.Sprite.__init__(self, self.groups)

		# Initialize variables
		self.game = game
		self.image = pg.image.load(path.join(path.dirname(__file__), "assets/mainCharacter.png"))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.vel = vec(0, 0)
		self.pos = vec(x, y)
		self.mobile = True
		self.facing = facing
		self.facing_pos = self.get_facing()
		self.facing_rect = Position(game, self.facing_pos[0], self.facing_pos[1])

	# Get key presses for player movement
	def get_keys(self):
		self.vel = vec(0, 0)

		# Get pressed keys
		keys = pg.key.get_pressed()
		if keys[pg.K_LEFT] or keys[pg.K_a]: # left
			self.vel.x = -PLAYER_SPEED
		if keys[pg.K_RIGHT] or keys[pg.K_d]: # right
			self.vel.x = PLAYER_SPEED
		if keys[pg.K_UP] or keys[pg.K_w]: # up
			self.vel.y = -PLAYER_SPEED
		if keys[pg.K_DOWN] or keys[pg.K_s]: # down
			self.vel.y = PLAYER_SPEED

		# Lessen velocity for diagonal movement
		if self.vel.x != 0 and self.vel.y != 0:
			self.vel.x *= 0.7071
			self.vel.y *= 0.7071

	# Get player's facing position
	def get_facing(self):
		if self.facing == 'n': # facing north
			return (self.rect.center[0], self.rect.center[1] - 48)
		elif self.facing == 'e': # facing east
			return (self.rect.center[0] + 48, self.rect.center[1])
		elif self.facing == 's': # facing south
			return (self.rect.center[0], self.rect.center[1] + 48)
		else: # facing west
			return (self.rect.center[0] - 48, self.rect.center[1])

	# Check for wall collisions
	def collide_with_walls(self, d):
		# Check x direction
		if d == 'x':
			# Get collisions
			hits = pg.sprite.spritecollide(self, self.game.walls, False)

			# If there are collisions
			if hits:
				# Set positon to the edge of the wall
				if self.vel.x > 0:
					self.pos.x = hits[0].rect.left - self.rect.width
				if self.vel.x < 0:
					self.pos.x = hits[0].rect.right

				# Reset velocity and position
				self.vel.x = 0
				self.rect.x = self.pos.x

		# Check y direction
		if d == 'y':
			# Get collisions
			hits = pg.sprite.spritecollide(self, self.game.walls, False)

			# If there are collisions
			if hits:
				# Set position to the edge of the wall
				if self.vel.y > 0:
					self.pos.y = hits[0].rect.top - self.rect.height
				if self.vel.y < 0:
					self.pos.y = hits[0].rect.bottom

				# Reset velocity and position
				self.vel.y = 0
				self.rect.y = self.pos.y

	# Update player
	def update(self):
		if self.mobile:
			# Update velocity
			self.get_keys()

			# Update position accordingly
			self.pos += self.vel * self.game.dt
			self.rect.x = self.pos.x

			# Check wall collisions
			self.collide_with_walls('x')
			self.rect.y = self.pos.y
			self.collide_with_walls('y')

			# Update facing position
			self.facing_pos = self.get_facing()
			self.facing_rect.update_pos(self.facing_pos[0], self.facing_pos[1])

# NPC class
class NPC(pg.sprite.Sprite):
	def __init__(self, game, x, y, dialog, img = "assets/candle_man_final.png", w = TILESIZE * 0.75, h = TILESIZE * 0.75):
		# Setting groups
		self.groups = game.all_sprites, game.npcs, game.walls
		# Initialize sprite
		pg.sprite.Sprite.__init__(self, self.groups)

		# Initialize variables
		self.game = game
		self.image = pg.image.load(path.join(path.dirname(__file__), img))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.vel = vec(0, 0)
		self.pos = vec(x, y)
		self.mobile = True

		# Get dialog
		self.dialog_path = path.join(path.dirname(__file__), dialog)
		dialog_file = open(self.dialog_path, 'r')
		# Format dialog
		self.dialog_data = dialog_file.read().split('\n')
		self.dialog = self.dialog_data[0].split('~')
		self.options = self.dialog_data[1]
		self.reward = self.dialog_data[2]

	# Interact function
	def interact(self):
		# Disable movement
		self.game.player.mobile = False

		# Start dialog
		self.game.dialog_box.next(self.dialog.copy())
		self.game.dialog_box.active = True

# Wall class (DEPRECATED)
class Wall(pg.sprite.Sprite):
	def __init__(self, game, x, y):
		# Setting groups
		self.groups = game.all_sprites, game.walls
		# Initialize sprite
		pg.sprite.Sprite.__init__(self, self.groups)

		# Initialize variables
		self.game = game
		self.image = pg.Surface((TILESIZE, TILESIZE))
		self.image.fill(GREEN)
		self.rect = self.image.get_rect()
		self.x = x
		self.y = y
		self.rect.x = x * TILESIZE
		self.rect.y = y * TILESIZE

# Wall class
class Obstacle(pg.sprite.Sprite):
	def __init__(self, game, x, y, w, h):
		# Setting groups
		self.groups = game.walls, game.debug
		# Initializing sprite
		pg.sprite.Sprite.__init__(self, self.groups)

		# Initialize variables
		self.game = game
		self.rect = pg.Rect(x, y, w, h)
		self.x = x
		self.y = y

# Position class for viewing in debug mode
class Position(pg.sprite.Sprite):
	def __init__(self, game, x, y, w = 7, h = 7):
		# Setting groups
		self.groups = game.debug
		# Initialize sprite
		pg.sprite.Sprite.__init__(self, self.groups)

		# Initialize variables
		self.game = game
		self.rect = pg.Rect(x - 3, y - 3, 7, 7)
		self.x = x
		self.y = y

	# Update position of the display
	def update_pos(self, x, y):
		self.x = x
		self.y = y
		self.rect.center = (x, y)

# Warp class
class Warp(pg.sprite.Sprite):
	def __init__(self, game, x, y, w, h, warp, player_pos):
		# Setting groups
		self.groups = game.warps, game.debug
		# Initialize sprite
		pg.sprite.Sprite.__init__(self, self.groups)

		# Initialize variables
		self.game = game
		self.rect = pg.Rect(x, y, w, h)
		self.x = x
		self.y = y
		self.warp = warp
		self.player_pos = player_pos

	# Activate warp
	def activate(self):
		# Set map
		self.game.map_file = self.warp

		# End current game loop
		self.game.playing = False