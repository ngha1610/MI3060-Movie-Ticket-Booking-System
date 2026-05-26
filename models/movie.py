class Movie:

    def __init__(

        self,
        movie_id,
        title,
        genre,
        revenue=0

    ):

        self.movie_id = movie_id

        self.title = title

        self.genre = genre

        self.revenue = revenue

    def increase_revenue(

        self,
        amount

    ):

        self.revenue += amount

    def to_dict(self):

        return {

            "movie_id": self.movie_id,

            "title": self.title,

            "genre": self.genre,

            "revenue": self.revenue

        }
