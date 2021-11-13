import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *

# Class for the game object, which controls everything
class Game:
	def __init__(self):
		# Initialize pygame and set up the screen and clock
		pg.init()
		self.screen = pg.display.set_mode((WIDTH, HEIGHT), 32)
		pg.display.set_caption(TITLE)
		self.clock = pg.time.Clock()
		pg.time.set_timer(pg.USEREVENT, 40)
		pg.mouse.set_visible(False)
		self.load_data()

	#Basic text drawing function
	def draw_text(self, text, font_name, size, color, x, y, align="nw"):
		font = pg.font.Font(font_name, size)
		text_surface = font.render(text, True, color)
		text_rect = text_surface.get_rect()
		if align == "nw":
			text_rect.topleft = (x, y)
		if align == "ne":
			text_rect.topright = (x, y)
		if align == "sw":
			text_rect.bottomleft = (x, y)
		if align == "se":
			text_rect.bottomright = (x, y)
		if align == "n":
			text_rect.midtop = (x, y)
		if align == "s":
			text_rect.midbottom = (x, y)
		if align == "e":
			text_rect.midright = (x, y)
		if align == "w":
			text_rect.midleft = (x, y)
		if align == "center":
			text_rect.center = (x, y)
		self.screen.blit(text_surface, text_rect)

	# Load data for the game
	def load_data(self):
		# Locations of assets
		self.game_folder = path.dirname(__file__)
		self.img_folder = path.join(self.game_folder, 'assets')
		self.map_folder = path.join(self.game_folder, 'maps')
		
		# Game font
		self.font = path.join(self.img_folder, 'chunky.ttf')

		# Screen dimming effect
		self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
		self.dim_screen.fill((0, 0, 0, 125))
		
		# Initializing dialog box
		self.dialog_box = DialogBox(self, active=False)

		# Setting default map file
		self.map_file = 'testMap.tmx'

		# Initialize sprite groups
		self.all_sprites = pg.sprite.Group()
		self.npcs = pg.sprite.Group()
		self.walls = pg.sprite.Group()
		self.warps = pg.sprite.Group()
		self.debug = pg.sprite.Group()

	# Load a new map file
	def new(self, map, player_pos = None):

		# Load map
		self.map = TiledMap(path.join(self.map_folder, 'testMap2.tmx'))
		self.map_img = self.map.make_map()
		self.map_rect = self.map_img.get_rect()
		self.wall_rect = self.map.get_walls()

		# Create objects from map
		for tile_object in self.map.tmxdata.objects:
			obj_center = vec(tile_object.x + (tile_object.width // 2), tile_object.y + (tile_object.height // 2))
			if tile_object.name == 'player':
				if player_pos:
					pass
				else:
					self.player = Player(self, tile_object.x, tile_object.y)
			elif tile_object.name == 'wall':
				Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
			elif tile_object.name == 'NPC':
				npcInfo = tile_object.type.split(',')
				NPC(self, tile_object.x, tile_object.y, npcInfo[1], img = npcInfo[0], w = TILESIZE * 0.75, h = TILESIZE * 0.75)

		# Initialize camera
		self.camera = Camera(self.map.width, self.map.height)

		# Establishing game variables
		self.draw_debug = False
		self.paused = False

	# Game loop
	def run(self):
		self.playing = True
		while self.playing:
			self.dt = self.clock.tick(FPS)
			self.events()
			if not self.paused:
				self.update()
			self.draw()

	# Quit the game
	def quit(self):
		pg.quit()
		sys.exit()

	# Update function
	def update(self):
		# Update the sprites
		self.all_sprites.update()
		self.player.update()

		# Update camera
		self.camera.update(self.player)

	# Draw to the screen
	def draw(self):
		# Background fill
		self.screen.fill(BGCOLOR)

		# Draw map
		self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))

		# Draw sprites and debug
		for sprite in self.all_sprites:
			self.screen.blit(sprite.image, self.camera.apply(sprite))
			if self.draw_debug:
				pg.draw.rect(self.screen, (100,200,255), self.camera.apply_rect(sprite.rect), 1)
		if self.draw_debug:
			for obj in self.debug:
				pg.draw.rect(self.screen, (100,200,255), self.camera.apply_rect(obj.rect), 1)

		# Draw walls
		self.screen.blit(self.wall_rect, self.camera.apply_rect(self.map_rect))

		# Draw dialog box
		if self.dialog_box.active: self.dialog_box.draw()

		# Draw pause screen
		if self.paused:
			self.screen.blit(self.dim_screen, (0, 0))
			self.draw_text('Paused', self.font, 105, WHITE, WIDTH//2, HEIGHT//2, align='center')

		# Flip the display
		pg.display.flip()

	# Handle events
	def events(self):
		# Loop through the events
		for event in pg.event.get():

			# Close the game
			if event.type == pg.QUIT:
				self.quit()

			# Dialog box update
			if event.type == pg.USEREVENT: self.dialog_box.update()

			if event.type == pg.KEYDOWN:
				# Pause game
				if event.key == pg.K_ESCAPE:
					self.paused = not self.paused
				# Debug toggle
				if event.key == pg.K_h:
					self.draw_debug = not self.draw_debug
				# Dialog next button
				if event.key == pg.K_SPACE:
					self.dialog_box.active = self.dialog_box.next()
				# NPC interact
				if event.key == pg.K_e:
					for npc in self.npcs:
						if npc.rect.collidepoint(self.player.facing_pos):
							npc.interact()
				# Quit game
				if event.key == pg.K_BACKQUOTE:
					self.quit()

	def show_start_screen(self):
		pass

	def show_game_over_screen(self):
		pass

# Scrolling text generator
def text_generator(text):
	tmp = ''
	for letter in text:
		tmp += letter
		# don't pause for spaces
		if letter != ' ':
			yield tmp

#Scrolling text class
class DynamicText:
	def __init__(self, font, text, pos, autoreset=False):
		# Initializing variables
		self.done = False
		self.font = font
		self.text = text
		self._gen = text_generator(self.text)
		self.pos = pos
		self.autoreset = autoreset

	# Reset text scroll
	def reset(self):
		self._gen = text_generator(self.text)
		self.done = False
		self.update()

	# Update text scroll
	def update(self):
		if not self.done:
			try: self.rendered = self.font.render(next(self._gen), True, (255, 255, 255))
			except StopIteration: 
				self.done = True
				if self.autoreset: self.reset()

	# Draw text to screen
	def draw(self, screen):
		screen.blit(self.rendered, self.pos)

# Dialog box class
class DialogBox:
	def __init__(self, game, text = [], active = False):
		# Initializing variables
		self.game = game
		self.pos = (180, HEIGHT - 140)
		self.textPos = (self.pos[0] + 10, self.pos[1] + 10)
		self.text = text
		self.text1 = None
		self.text2 = None
		self.text3 = None
		self.text4 = None
		self.rect1 = pg.Rect(180, HEIGHT - 140, WIDTH - 360, 130)
		self.rect2 = pg.Rect(185, HEIGHT - 135, WIDTH - 370, 120)
		self.active = active

	# Next dialog box text
	def next(self, text=None):
		# If text is provided
		if text:
			# Activate text box
			self.active = True
			# Turn text into scrolling text
			for line in text:
				self.text.append(DynamicText(pg.font.Font(self.game.font, 25), line, (0,0), autoreset = False))
		# If text is not provided, use own text
		else:
			text = self.text

		# If last line of text exists and is not done scrolling
		if self.text4:
			if not self.text4.done:
				# Skip to the end of the dialog box
				while not self.text4.done:
					self.update()
				# Exit function
				return True

		# Add to line 1
		if len(self.text) >= 1:
			self.text1 = self.text.pop(0)
		else:
			# Close the dialog box if the text is done scrolling
			self.game.player.mobile = True
			return False
		# Add to line 2
		if len(self.text) >= 1:
			self.text2 = self.text.pop(0)
		else:
			self.text2 = DynamicText(pg.font.Font(self.game.font, 25), " ", (0, 0), autoreset=False)
		# Add to line 3
		if len(self.text) >= 1:
			self.text3 = self.text.pop(0)
		else:
			self.text3 = DynamicText(pg.font.Font(self.game.font, 25), " ", (0, 0), autoreset=False)
		# Add to line 4
		if len(self.text) >= 1:
			self.text4 = self.text.pop(0)
		else:
			self.text4 = DynamicText(pg.font.Font(self.game.font, 25), " ", (0, 0), autoreset=False)

		# Set positions for lines of dialog
		self.text1.pos = self.textPos
		self.text2.pos = (self.textPos[0], self.textPos[1] + 30)
		self.text3.pos = (self.textPos[0], self.textPos[1] + 60)
		self.text4.pos = (self.textPos[0], self.textPos[1] + 90)

		# Update the current line
		self.update()
		return True

	# Draw dialog box
	def draw(self):
		# Draw box
		pg.draw.rect(self.game.screen, (255, 255, 255), self.rect1)
		pg.draw.rect(self.game.screen, (0,0,0), self.rect2)

		# If there is no text, leave function
		if not self.text1: return

		# Draw line 1
		self.text1.draw(self.game.screen)

		# Try to draw line 2
		if self.text1.done:
			try:
				self.text2.draw(self.game.screen)
			except:
				self.text2.update()
		# Try to draw line 3
		if self.text2.done:
			try:
				self.text3.draw(self.game.screen)
			except:
				self.text3.update()
		# Try to draw line 4
		if self.text3.done:
			try:
				self.text4.draw(self.game.screen)
			except:
				self.text4.update()

	# Update dialog box
	def update(self):
		# If there is no text, leave function
		if not self.text1: return 

		# Update the lines in order (1-4)
		if not self.text1.done:
			self.text1.update()
		elif not self.text2.done:
			self.text2.update()
		elif not self.text3.done:
			self.text3.update()
		else:
			self.text4.update()

# Create game
g = Game()

# Start the game
g.show_start_screen()
while True:
	# Load the map
	g.new(g.map_file)

	# Run the loop
	g.run()