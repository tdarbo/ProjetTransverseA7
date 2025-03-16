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

    def create_dictionary(self, players, hole_number):
        """
        Creates a dictionary using the number of players and the number of hole,
        In order to associate the scores of the games to the players
        """

        for player in players:
            tab = [0] * (hole_number + 1)  # Adding a line that will calculate
            # the global score of the player
            self.score[player] = tab

    def add_points(self, player, hole):
        """
        Increase the score of the player at the end of his turn
        """

        self.score[player][hole] += 1

    def score_calculation(self, players, hole_number):
        """
        Calculates the global score for each player
        """

        total = 0
        for player in players:
            for i in range(hole_number):
                total += self.score[player][i]
            self.score[player][hole_number + 1] = total

    def score_reset(self, players, hole_number):
        """
        Set the score of every player at 0 for every turn
        """

        for player in players:
            tab = [0] * (hole_number + 1)  # Adding a line to remove the total
            self.score[player] = tab
