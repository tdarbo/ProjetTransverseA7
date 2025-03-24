from pickletools import pyunicode

import pytmx
import pygame

from camera import Camera
from tile import Tile

from settings import TILE_SIZE


def load_tiled_map(map_path, tile_size):
    tmx_data = pytmx.load_pygame(map_path)
    tiles = pygame.sprite.Group()

    for layer in tmx_data.layers:
        if isinstance(layer,pytmx.TiledTileLayer):
            for x,y,gid in layer:
                if gid==0:
                    continue

                tile_image = tmx_data.get_tile_image_by_gid(gid)

                if tile_image:
                    tile = Tile(layer.name, x * tile_size, y * tile_size, tile_size, tile_size, image_surface=tile_image)
                    tiles.add(tile)

    return tiles


class Map:

    def __init__(self,path,surf):
        self.camera = Camera(surf)
        self.tiles = load_tiled_map(path,TILE_SIZE)
        self.surface = surf





