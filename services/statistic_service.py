# services/statistic_service.py

from collections import Counter

from utils.csv_handler import CSVHandler


class StatisticService:

    def revenue(self):

        tickets=CSVHandler.load_csv(
            "data/tickets.csv"
        )

        total=sum(

            int(ticket["price"])

            for ticket in tickets

        )

        return total


    def hot_movies(self):

        tickets=CSVHandler.load_csv(
            "data/tickets.csv"
        )

        counter=Counter(

            ticket["movie"]

            for ticket in tickets

        )

        return sorted(

            counter.items(),

            key=lambda x:x[1],

            reverse=True

        )
