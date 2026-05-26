import streamlit as st

from interface.login_page import login_page

from interface.register_page import register_page

from interface.movie_page import movie_page

from interface.history_page import history_page

from interface.admin_page import admin_page


def menu():

    pages = [

        "Phim",

        "Lịch sử"

    ]

    if (

        "user"

        not in

        st.session_state

    ):

        pages.extend(

            [

                "Đăng nhập",

                "Đăng ký"

            ]

        )

    else:

        if (

            st.session_state

            ["user"]

            ["role"]

            == "admin"

        ):

            pages.append(

                "Admin"

            )

        pages.append(

            "Đăng xuất"

        )

    choice = (

        st.sidebar.selectbox(

            "Menu",

            pages

        )
    )

    if choice=="Đăng nhập":

        login_page()

    elif choice=="Đăng ký":

        register_page()

    elif choice=="Phim":

        movie_page()

    elif choice=="Lịch sử":

        history_page()

    elif choice=="Admin":

        admin_page()

    elif choice=="Đăng xuất":

        del st.session_state[

            "user"

        ]

        st.rerun()
