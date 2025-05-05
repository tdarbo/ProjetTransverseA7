from bonus_manager import Bonus
from settings import *
import pytmx
from camera import Camera
from tile import Tile

def load_tiled_map(map_path: str, tile_size: int):
    """
    Charge une carte Tiled à partir d'un fichier et crée des objets Tile pour chaque tuile de la carte.

    :param map_path: Chemin vers la carte Tiled
    :param tile_size: Taille des tuiles en pixels
    :return: Un tuple contenant un groupe de tuiles, le point du spawn et du trou
    """
    # On charge les données de la carte
    tmx_data = pytmx.load_pygame(map_path)
    tiles = pygame.sprite.Group()
    bonuses = []
    spawn, hole = None, None

    # Parcours des layers de la carte
    # Une carte possède plusieurs layers
    # Chaque layer permet de définir un type de tuile spécifique comme le sable, l'herbe, la glace ou l'eau
    for layer in tmx_data.layers:
        # Traitement des objets
        # Les objets représentent tout ce qui ne se trouve pas sur la grille des tuiles,
        # comme les bonus, le point de spawn et le trou
        if layer.name == "Objects":
            for obj in layer:
                if obj.name == "spawn":
                    spawn = obj
                elif obj.name == "hole":
                    hole = obj
                elif obj.name == "bonus":
                    b = Bonus(obj)
                    b.print_bonus_log()
                    bonuses.append(b)

        # Traitement des tuiles
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if gid != 0:
                    # On récupère l'image de la tuile
                    tile_image = tmx_data.get_tile_image_by_gid(gid)
                    # On crée l'objet associé à cette tuile
                    tile = Tile(
                        tile_type_id=layer.name,
                        x=x * tile_size,
                        y=y * tile_size,
                        width=tile_size,
                        height=tile_size,
                        image_surface=tile_image,
                    )
                    # On ajoute la tuile au groupe de sprites pygame
                    tiles.add(tile)


    return tiles, spawn, hole, bonuses


class Map:
    def __init__(self, path: str, surf):
        """
        Création d'une nouvelle Map.

        :param path: Chemin vers le fichier de la carte
        :param surf: Surface sur laquelle la carte sera dessinée
        """
        # Chargement des tuiles, du point de spawn et du trou à partir de la carte
        self.tiles, self.spawn, self.hole, self.bonuses = load_tiled_map(path, TILE_SIZE)
        self.surface = surf

        # On initialise la caméra
        self.camera = Camera(surf)
        self.camera.offset_X = self.hole.x
        self.camera.offset_Y = self.hole.y
        self.camera.zoom_factor = 0.5

        # On charge les données de la carte
        tmx_data = pytmx.TiledMap(path)
        map_width = tmx_data.width  # Nombre de tuiles en largeur
        map_height = tmx_data.height  # Nombre de tuiles en hauteur
        tile_width = tmx_data.tilewidth  # Largeur d'une tuile en pixels
        tile_height = tmx_data.tileheight  # Hauteur d'une tuile en pixels

        # On termine par calculer les dimensions de la carte en pixels
        self.map_width = map_width * tile_width
        self.map_height = map_height * tile_height



    def teleportPlayersToSpawn(self, players: list):
        """
        Téléporte tous les joueurs au spawn.

        :param players: Liste des joueurs à téléporter
        """
        for player in players:
            self.teleportPlayerToSpawn(player)

    def teleportPlayerToSpawn(self, player):
        """
        Téléporte un joueur au spawn.

        :param player: Joueur à téléporter
        """
        player.position.x = self.spawn.x
        player.position.y = self.spawn.y
