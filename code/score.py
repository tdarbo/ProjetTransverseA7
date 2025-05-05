from player import Player
from settings import *
from ui_text import Text


class ScoreManager:
    """
    Gère les scores de tous les joueurs pendant la partie.
    Permet d'ajouter, réinitialiser les points et calcule les scores totaux.
    """

    def __init__(self, players: list[Player], holes_number: int):
        self.players: list[Player] = players # Liste des "objets" joueurs
        self.players_number = len(players) # Nombre total de joueurs
        self.holes_number = holes_number # Nombre de trous à jouer
        self.current_hole = 0 # Numéro du trou en train d'être joué
        self.score = self.create_dictionary() # Dictionnaire contenant tous les scores par joueur
        # ex : self.score = {Player: {"score": [0,0,0], "total": 0}}
        self.collapsed = True # Utilisé pour masquer/afficher l'affichage du score

        # Dimensions totales du menu de score
        self.menu_width = (
                SCORE_CELL_WIDTH * (self.players_number + 1) +
                SCORE_CELL_GAP * self.players_number +
                SCORE_MENU_PADDING * 2
        )
        self.menu_height = (
                SCORE_CELL_HEIGHT * (self.holes_number + 2) +
                SCORE_CELL_GAP * (self.holes_number + 1) +
                SCORE_MENU_PADDING * 2
        )

    def set_current_hole(self, hole_number):
        self.current_hole = hole_number

    # def toggle_menu(self):
    #     # Si le menu est collapsed, on inverse son état
    #     self.collapsed = not self.collapsed

    def create_dictionary(self):
        # Initialise le dictionnaire des scores pour chaque joueur
        score_dict = dict()
        for player in self.players:
            if player not in score_dict:
                score_dict[player] = dict()

            # Chaque joueur commence avec un tableau de scores à 0 pour chaque trou
            score_dict[player]["score"] = [0] * self.holes_number

            # Le total est initialisé à 0
            score_dict[player]["total"] = 0

        return score_dict

    def add_points(self, player, hole):
        # Ajoute un point au joueur pour le trou donné
        # Puis met à jour le total
        self.score[player]["score"][hole] += 1
        self.score_calculation()

    def score_calculation(self):
        # Calcule le score total pour chaque joueur en additionnant ses scores trou par trou
        for player in self.players:
            total = 0
            for i in range(self.holes_number):
                total += self.score[player]["score"][i]
            self.score[player]["total"] = total

    def score_reset(self):
        # Réinitialise tous les scores à 0 pour tous les joueurs
        for player in self.players:
            # On remet le score du joueur à chaque trou à zéros
            for i in range(self.holes_number):
                self.score[player]["score"][i] = 0
            self.score[player]["total"] = 0

    def draw(self, screen):
        # Position du menu en bas à droite de l'écran
        start_x = screen.get_width() - SCORE_MENU_MARGIN - self.menu_width
        start_y = screen.get_height() - SCORE_MENU_MARGIN - self.menu_height

        # Dessin du fond du menu (rectangle orange) et de sa bordure
        pygame.draw.rect(screen, (213, 85, 52), (start_x, start_y, self.menu_width, self.menu_height))
        pygame.draw.rect(screen, '#3F170D', (start_x, start_y, self.menu_width, self.menu_height), 3)

        # Décalage interne pour ne pas coller le contenu aux bords du menu
        start_x += SCORE_MENU_PADDING
        start_y += SCORE_MENU_PADDING

        for i in range(-1, self.players_number):
            # La colonne d'indice -1 est réservée aux en-têtes du tableau (numéros de trou, "Total", ...)
            # Toutes les autres colonnes affichent les scores de chaque joueur

            # Calcul position horizontale de la cellule
            current_cell_x = start_x + (i + 1) * SCORE_CELL_WIDTH + (i + 1) * SCORE_CELL_GAP

            if i != -1:
                # On récupère le joueur associé à cette colonne
                player = self.players[i]
            else:
                # Pas de joueur pour la colonne d'en-tête (colonne -1)
                player = None

            # Dessin des 3 parties du tableau : en-tête, scores et total
            self.draw_header(screen, i, player, current_cell_x, start_y)
            self.draw_body(screen, i, player, current_cell_x, start_y)
            self.draw_footer(screen, i, player, current_cell_x, start_y)

    def draw_header(self, screen, column_index, player, cell_x, cell_y):
        if column_index == -1:
            # Première colonne : on affiche le texte de l’en-tête "Trou n°"
            Text(
                text="Trou n°",
                pos=(cell_x, cell_y),
                color=(255, 255, 255),
                font_size=SCORE_MENU_FONT_SIZE
            ).draw(screen)
        else:
            # En-tête joueur : on affiche un cercle de couleur et son nom (ou "Vous" par défaut)
            pygame.draw.circle(
                surface=screen,
                color=player.color,
                center=(cell_x, cell_y + 5),
                radius=5
            )
            Text(
                text=player.name if self.players[column_index].name else "Vous",
                pos=(cell_x + 12, cell_y),
                color=(255, 255, 255),
                font_size=SCORE_MENU_FONT_SIZE
            ).draw(screen)

    def draw_body(self, screen, column_index, player, cell_x, start_y):
        for row_index in range(0, self.holes_number):
            # Position verticale de la cellule en fonction du trou (ligne)
            cell_y = start_y + (row_index + 1) * SCORE_CELL_HEIGHT + (row_index + 1) * SCORE_CELL_GAP

            if column_index == -1:
                # Première colonne : on affiche le numéro de chaque trou
                Text(
                    text=str(row_index + 1),
                    pos=(cell_x, cell_y),
                    color=(255, 255, 255),
                    font_size=SCORE_MENU_FONT_SIZE
                ).draw(screen)
            else:
                # Cellule score du joueur pour ce trou
                # Le score du joueur à un trou est une valeur dans le tableau à la clé "score" dans le dico associé au joueur
                # On récupère ce score à l'index du numéro du trou dans le tableau (ici row_index).
                # Rappel de la structure : score = {Player1: {"score": [...], "total": 0}, Player2: ...}
                score = str(self.score[player]["score"][row_index])
                Text(
                    text=score if score != "0" else "-",  # Affiche un tiret si le score est nul
                    pos=(cell_x, cell_y),
                    color=(255, 255, 255),
                    font_size=SCORE_MENU_FONT_SIZE
                ).draw(screen)

    def draw_footer(self, screen, column_index, player, cell_x, start_y):
        # Position verticale du footer (ligne "Total")
        cell_y = start_y + (self.holes_number + 1) * SCORE_CELL_HEIGHT + (self.holes_number + 1) * SCORE_CELL_GAP

        if column_index == -1:
            # Première colonne : on affiche "Total" en bas
            Text(
                text="Total",
                pos=(cell_x, cell_y),
                color=(255, 255, 255),
                font_size=SCORE_MENU_FONT_SIZE
            ).draw(screen)
        else:
            # Affichage du total du joueur
            # Le total est une valeur à la clé "total" dans le dico associé au joueur
            # Rappel de la structure : score = {Player1: {"score": [...], "total": 0}, Player2: ...}
            total = str(self.score[player]["total"])
            Text(
                text=total if total != "0" else "-",  # Tiret si score encore à 0
                pos=(cell_x, cell_y),
                color=(255, 255, 255),
                font_size=SCORE_MENU_FONT_SIZE
            ).draw(screen)


if __name__ == '__main__':
    players = ["Louis", "Mathias", "Bastien", "Mattéo", "Thomas"]
    holes_number = 2
    score_manager = ScoreManager(players, holes_number)
    score_manager.create_dictionary()
    print(score_manager.score, "initialisé")
    score_manager.add_points("Louis", 0)
    print(score_manager.score, "calcul score")
    score_manager.add_points("Louis", 1)
    print(score_manager.score, "calcul score")
    score_manager.add_points("Mathias", 0)
    print(score_manager.score, "calcul score")
    score_manager.score_calculation()
    print(score_manager.score, "calcul score total")
    score_manager.score_reset()
    print(score_manager.score, "après reset")
