from settings import *
from ui_text import Text

WIDTH = 1200
HEIGHT = 500
class ScoreManager:
    """
    This class manages the scores of all the players during the game.
    Allows adding, removing and resetting points,
    Calculates the global score for each player
    """

    def __init__(self, players: list, hole_number: int):
        self.players = players
        self.hole_number = hole_number
        self.score = self.create_dictionary()  # Dictionary that contains the scores of the players

    def create_dictionary(self):
        score_dict = dict()
        for player in self.players:
            if player not in score_dict:
                score_dict[player] = dict()
            player_score = [0] * self.hole_number
            score_dict[player]["score"] = player_score
            score_dict[player]["total"] = 0

        return score_dict

    def add_points(self, player, hole):
        self.score[player]["score"][hole] += 1
        self.score_calculation()

    def score_calculation(self):
        for player in self.players:
            total = 0
            for i in range(self.hole_number):
                total += self.score[player]["score"][i]
            self.score[player]["total"] = total

    def score_reset(self):
        for player in self.players:
            tab = [0] * self.hole_number  # Adding a line to remove the total
            self.score[player]["score"] = tab
            self.score[player]["total"] = 0

    def _get_table_header(self):
        line = []
        line.append("Trou n°")
        for value in self.score.keys(): # Keys = Noms des joueurs
            line.append(value.name)

        return line

    def _get_table_line(self, hole):
        line = []
        line.append(str(hole + 1))
        for value in self.score.values():
            line.append(str(value["score"][hole])) # Score du joueur au trou "hole"

        return line

    def _get_table_footer(self):
        line = []
        line.append("Total")
        for value in self.score.values():
            line.append(str(value["total"])) # Récuperation du total du joueur

        return line

    def draw(self, screen):
        # On construit un tableau à partir des données du tableau
        header = self._get_table_header()
        footer = self._get_table_footer()
        lines = [header]
        for i in range(self.hole_number):
            lines.append(self._get_table_line(i))
        lines.append(footer)

        # Dimension des cellules
        cell_width = 100 # Largeur d'une cellule
        cell_height = 10 # Hauteur d'une cellule
        cell_gap = 5 # Espace entre cellules

        # Dimension du menu
        menu_gap = 50
        menu_height = (len(lines) - 1) * cell_gap + cell_height * len(lines)
        menu_width = (len(lines[0]) - 1) * cell_gap + cell_width * len(lines[0])

        # Calcul de la position de la première cellule pour que notre menu soit positionné à partir du coin inférieur droit
        start_x = screen.get_width() - menu_gap - menu_width
        start_y = screen.get_height() - menu_gap - menu_height

        # On dessine un rectangle englobant le menu
        pygame.draw.rect(screen, (255, 255, 255), (start_x, start_y, menu_width, menu_height), 3)

        # On affiche le tableau du score ligne par ligne
        for row_index in range(len(lines)):
            row = lines[row_index]
            for col_index in range(len(lines[0])):
                cell = row[col_index]
                current_cell_x = start_x + col_index * (cell_width + cell_gap)
                current_cell_y = start_y + row_index * (cell_height + cell_gap)

                text_obj = Text(
                    text=str(cell),
                    pos=(current_cell_x, current_cell_y),
                    color=(255, 255, 255),
                    font_size=10
                )
                text_obj.draw(screen)  # On affiche le texte de la cellule

    def print_score(self):
        print(self._get_table_header())
        for i in range(self.hole_number):
            print(self._get_table_line(i))
        print(self._get_table_footer())

if __name__ == '__main__':
    players = ["Louis", "Mathias", "Bastien", "Mattéo", "Thomas"]
    hole_number = 2
    score_manager = ScoreManager(players, hole_number)
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
    # score_manager.score_reset()
    print(score_manager.score, "après reset")
    score_manager.print_score()
    #score_manager.draw()

    for i in range(4, -1, -1):
        print(i)