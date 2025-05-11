from settings import *
import pytmx
from camera import Camera
from bonus_manager import Bonus
from broadcast import BroadcastManager
from tile import Tile


def load_tiled_map(map_path: str, tile_size: int, broadcast: BroadcastManager):
    """
    Charge une carte Tiled à partir d’un fichier .tmx et crée tous les objets nécessaires

    :param map_path: Chemin vers le fichier de la carte (.tmx)
    :param tile_size: Taille d’une tuile (en pixels)
    :param broadcast: Gestionnaire de broadcast
    :return: Tuple avec groupe de tuiles, point du spawn, du trou, et liste des bonus
    """
    tmx_data = pytmx.load_pygame(map_path)
    tiles = pygame.sprite.Group()
    bonuses = []
    spawn, hole = None, None

    # Parcours de chaque "calque" de la carte
    for layer in tmx_data.layers:
        # Si le calque contient des objets (comme le spawn, le trou ou les bonus)
        if layer.name == "Objects":
            for obj in layer:
                if obj.name == "spawn":
                    spawn = obj  # Enregistre le point de spawn
                elif obj.name == "hole":
                    hole = obj  # Enregistre le point du trou
                elif obj.name == "bonus":
                    b = Bonus(obj, broadcast)  # Crée un objet bonus
                    if DEBUG_MODE:
                        b.print_bonus_log()
                    bonuses.append(b)  # Ajoute à la liste des bonus

        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if gid != 0:
                    tile_image = tmx_data.get_tile_image_by_gid(gid)  # Récupère l’image de la tuile
                    tile_image = pygame.Surface.convert(tile_image)
                    # Crée la tuile
                    tile = Tile(
                        tile_type_id=layer.name,
                        x=x * tile_size,
                        y=y * tile_size,
                        width=tile_size,
                        height=tile_size,
                        image=tile_image,
                    )
                    tiles.add(tile)  # Ajoute la tuile au groupe de sprites

    return tiles, spawn, hole, bonuses


class Map:
    def __init__(self, infos: dict, screen: pygame.Surface, broadcast: BroadcastManager):
        """
        Initialise une nouvelle instance de Map à partir d’un fichier .tmx.
        Gère le chargement des tuiles, le spawn, le trou, les bonus et initialise la caméra.

        :param infos: Dictionnaire contenant les informations de la carte (notamment le chemin du fichier)
        :param screen: Surface Pygame sur laquelle la carte sera affichée
        :param broadcast: Objet chargé de diffuser les événements liés aux bonus
        """
        self.infos = infos
        self.tiles, self.spawn, self.hole, self.bonuses = load_tiled_map(self.infos["path"], TILE_SIZE, broadcast)

        # Création et configuration de la caméra
        self.camera = Camera(screen)
        # Caméra centrée sur le trou
        self.camera.offset_X = self.hole.x
        self.camera.offset_Y = self.hole.y
        self.camera.zoom_factor = 0.5

        # On récupère les dimensions de la carte
        tmx_data = pytmx.TiledMap(self.infos["path"])
        map_width = tmx_data.width
        map_height = tmx_data.height
        tile_width = tmx_data.tilewidth
        tile_height = tmx_data.tileheight

        # On termine par calculer les dimensions de la carte
        self.map_width = map_width * tile_width
        self.map_height = map_height * tile_height

    def teleportPlayersToSpawn(self, players: list):
        """
        Téléporte tous les joueurs au point de spawn (définie dans la carte).

        :param players: Liste des instances de joueurs à déplacer
        """
        for player in players:
            self.teleportPlayerToSpawn(player)

    def teleportPlayerToSpawn(self, player):
        """
        Téléporte le joueur à la position du spawn.

        :param player: Le joueur à téléporter
        """
        player.position.x = self.spawn.x
        player.position.y = self.spawn.y

    def load_gif_bonuses(self, map_surf: pygame.Surface):
        """
        Charge les GIFs liés aux bonus présents sur la carte.

        :param map_surf: Surface Pygame sur laquelle afficher les GIFs
        """
        if len(self.bonuses) == 0:
            return  # S'il n’y a pas de bonus, on ne fait rien
        for bonus in self.bonuses:
            bonus.gif.update(map_surf)  # Met à jour l’animation du bonus
