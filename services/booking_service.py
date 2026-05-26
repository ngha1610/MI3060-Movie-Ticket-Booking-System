import uuid

from utils.csv_handler import CSVHandler

from services.movie_service import MovieService


TICKET_FILE="data/tickets.csv"


class BookingService:

    def __init__(self):

        self.movie_service=(

            MovieService()

        )

    def book_ticket(

        self,

        username,

        movie_id,

        seat_id,

        showtime_id

    ):

        ticket_id=(

            str(

                uuid.uuid4()

            )[:8]

        )

        ticket={

            "ticket_id":
            ticket_id,

            "user_id":
            username,

            "movie_id":
            movie_id,

            "seat_id":
            seat_id,

            "status":
            "paid",

            "showtime_id":
            showtime_id

        }

        CSVHandler.append(

            TICKET_FILE,

            ticket,

            [

                "ticket_id",

                "user_id",

                "movie_id",

                "seat_id",

                "status",

                "showtime_id"

            ]

        )

        self.movie_service.update_revenue(

            movie_id,

            90000

        )

        return True

    def history(

        self,

        username

    ):

        tickets=(

            CSVHandler.load(

                TICKET_FILE

            )
        )

        result=[]

        for ticket in tickets:

            if (

                ticket["user_id"]

                == username

            ):

                result.append(

                    ticket

                )

        return result
