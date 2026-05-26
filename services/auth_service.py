import hashlib

from utils.csv_handler import CSVHandler

from datastructures.hashtable import HashTable


USER_FILE = "data/users.csv"


class AuthService:

    def __init__(self):

        self.cache = HashTable()

        self.load_users()

    def load_users(self):

        users = CSVHandler.load(

            USER_FILE

        )

        for user in users:

            self.cache.insert(

                user["username"],

                user

            )

    def hash_password(

        self,

        password

    ):

        return hashlib.sha256(

            password.encode()

        ).hexdigest()

    def register(

        self,

        username,

        password,

        role="customer"

    ):

        if self.cache.exists(

            username

        ):

            return False

        data = {

            "username":

            username,

            "password":

            self.hash_password(

                password

            ),

            "role":

            role

        }

        CSVHandler.append(

            USER_FILE,

            data,

            [

                "username",

                "password",

                "role"

            ]

        )

        self.cache.insert(

            username,

            data

        )

        return True

    def login(

        self,

        username,

        password

    ):

        user = self.cache.get(

            username

        )

        if user is None:

            return None

        password_hash = (

            self.hash_password(

                password

            )

        )

        if (

            user["password"]

            == password_hash

        ):

            return user

        return None
