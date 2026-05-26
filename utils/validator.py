import re


class Validator:

    @staticmethod
    def username(name):

        return len(name) >= 4


    @staticmethod
    def password(password):

        if len(password) < 6:

            return False

        upper = re.search(
            r"[A-Z]",
            password
        )

        digit = re.search(
            r"\d",
            password
        )

        return upper and digit


    @staticmethod
    def role(role):

        return role in [

            "customer",
            "admin"

        ]


    @staticmethod
    def seat(seat):

        pattern = r"^[A-Z]\d+$"

        return re.match(
            pattern,
            seat
        ) is not None
