from settings import *
import pytmx
from camera import Camera
from tile import Tile


def load_tiled_map(map_path, tile_size):
    tmx_data = pytmx.load_pygame(map_path)
    tiles = pygame.sprite.Group()

    spawn, hole = None, None

    print(tmx_data.layers)

    for layer in tmx_data.layers:
        print(f"Layer : {layer.name}")
        if layer.name == "Objects":
            for obj in layer:
                print(f"Nom : {obj.name}, Type : {obj.type}, Position : ({obj.x}, {obj.y})")
                if obj.name == "spawn":
                    spawn = obj
                elif obj.name == "hole":
                    hole = obj

        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if gid == 0:
                    continue
                tile_image = tmx_data.get_tile_image_by_gid(gid)
                if tile_image:
                    tile = Tile(
                        layer.name,
                        x * tile_size,
                        y * tile_size,
                        tile_size,
                        tile_size,
                        image_surface=tile_image
                    )
                    tiles.add(tile)

    return tiles, spawn, hole


class Map:
    def __init__(self, path, surf):
        self.tiles, self.spawn, self.hole = load_tiled_map(path, TILE_SIZE)
        self.surface = surf

        self.camera = Camera(surf)
        self.camera.offset_X = self.hole.x
        self.camera.offset_Y = self.hole.y
        self.camera.zoom_factor = 0.5

        tmx_data = pytmx.TiledMap(path)
        map_width = tmx_data.width  # Nombre de tuiles (colonnes)
        map_height = tmx_data.height  # Nombre de tuiles (lignes)
        tile_width = tmx_data.tilewidth  # Largeur d'une tuile en pixels
        tile_height = tmx_data.tileheight  # Hauteur d'une tuile en pixels

        self.map_width = map_width * tile_width
        self.map_height = map_height * tile_height

    def teleportPlayersToSpawn(self, players):
        for player in players:
            self.teleportPlayerToSpawn(player)

    def teleportPlayerToSpawn(self, player):
        player.position.x = self.spawn.x
        player.position.y = self.spawn.y
