import pygame as pg
from settings import *
import pytmx

# Map class (DEPRECATED)
class Map:
	def __init__(self, filename):
		# Get data
		self.data = []
		with open(filename, 'rt') as f:
			for line in f:
				self.data.append(line.strip())

		self.tilewidth = len(self.data[0])
		self.tileheight = len(self.data)
		self.width = self.tilewidth * TILESIZE
		self.height = self.tileheight * TILESIZE

# New map class
class TiledMap:
	def __init__(self, filename):
		# Load tiled and initialize variables
		tm = pytmx.load_pygame(filename, pixelalpha=True)
		self.width = tm.width * tm.tilewidth
		self.height = tm.height * tm.tileheight
		self.tmxdata = tm

	# Render map
	def renderer(self, surface):
		ti = self.tmxdata.get_tile_image_by_gid
		for layer in self.tmxdata.visible_layers:
			if isinstance(layer, pytmx.TiledTileLayer):
				for x, y, gid in layer:
					tile = ti(gid)
					if tile:
						surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))

	# Construct map
	def make_map(self):
		temp_surface = pg.Surface((self.width, self.height))
		self.renderer(temp_surface)
		return temp_surface

	# Render and construct walls
	def get_walls(self):
		temp_surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
		for x, y, gid in self.tmxdata.get_layer_by_name('walls2'):
			tile = self.tmxdata.get_tile_image_by_gid(gid)
			if tile:
				temp_surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))
		return temp_surface

# Camera class
class Camera:
	def __init__(self, width, height):
		# Initializing variables
		self.camera = pg.Rect(0, 0, width, height)
		self.width = width
		self.height = height

	# Offset sprite
	def apply(self, entity):
		return entity.rect.move(self.camera.topleft)

	# Offset rect
	def apply_rect(self, rect):
		return rect.move(self.camera.topleft)

	# Offset point
	def apply_point(self, pos):
		return (pos[0] + self.camera.left, pos[1] + self.camera.top)

	# Update camera relative to target
	def update(self, target):
		# Adjust positioning to match that of target
		x = -target.rect.x + int(WIDTH / 2) - target.rect.width/2
		y = -target.rect.y + int(HEIGHT / 2) - target.rect.height/2

		# Limit scrolling to map size
		x = min(0, x)  # left
		y = min(0, y)  # top
		x = max(-(self.width - WIDTH), x)  # right
		y = max(-(self.height - HEIGHT), y)  # bottom
		
		self.camera = pg.Rect(x, y, self.width, self.height)