# services/movie_service.py

from utils.csv_handler import CSVHandler

MOVIE_FILE="data/movies.csv"


class MovieService:

    def get_movies(self):

        return CSVHandler.load_csv(
            MOVIE_FILE
        )


    def add_movie(

        self,
        movie

    ):

        CSVHandler.append_csv(

            MOVIE_FILE,

            movie,

            [
                "id",
                "title",
                "genre",
                "duration",
                "rating"
            ]

        )


    def search_movie(
        self,
        keyword
    ):

        movies=self.get_movies()

        return [

            movie

            for movie in movies

            if keyword.lower()

            in movie["title"].lower()

        ]
