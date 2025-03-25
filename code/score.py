from settings import *
from ui_text import Text

class ScoreManager:
    """
    This class manages the scores of all the players during the game.
    Allows adding, removing and resetting points,
    Calculates the global score for each player
    """

    def __init__(self, players: list, hole_number: int):
        self.score = {}  # Dictionary that contains the scores of the players
        self.players = players
        self.hole_number = hole_number

    def create_dictionary(self):
        """
        Creates a dictionary using the number of players and the number of hole,
        In order to associate the scores of the games to the players
        """
        for player in self.players:
            if player not in self.score:
                self.score[player] = dict()
            player_score = [0] * self.hole_number
            self.score[player]["score"] = player_score
            self.score[player]["total"] = 0

    def add_points(self, player, hole):
        """
        Increase the score of the player at the end of his turn
        """
        self.score[player]["score"][hole] += 1

    def score_calculation(self):
        """
        Calculates the global score for each player
        """
        for player in self.players:
            total = 0
            for i in range(self.hole_number):
                total += self.score[player]["score"][i]
            self.score[player]["total"] = total

    def score_reset(self):
        """
        Set the score of every player at 0 for every turn
        """
        for player in self.players:
            tab = [0] * self.hole_number  # Adding a line to remove the total
            self.score[player]["score"] = tab
            self.score[player]["total"] = 0

    def _get_table_header(self):
        line = []
        line.append("Trou n°")
        for value in self.score.keys(): # Keys = Noms des joueurs
            line.append(value)

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

    def draw(self):
        self.print_score()
        Text("Cliquez \npour changer", (100, 150), color="BLACK")

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