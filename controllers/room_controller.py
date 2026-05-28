from models.entities import Room

from data_structures.linked_lists import (
    RoomLinkedList
)

from data_structures.file_io import (
    FileIOHandler
)

# =====================================================
# ROOM CONTROLLER
# =====================================================

class RoomController:

    def __init__(
        self,
        io_handler: FileIOHandler
    ):

        self._io_handler = io_handler

        self._room_list = (
            RoomLinkedList()
        )

        self._io_handler.load_rooms(
            self._room_list
        )

    # =================================================
    # ADD ROOM
    # =================================================

    def add_room(
        self,
        room: Room
    ) -> bool:

        # check trùng room_id
        existed = (
            self._room_list
            .find_room(
                room.get_room_id()
            )
        )

        if existed:
            return False

        # check trùng tên phòng
        current = (
            self._room_list
            .get_head()
        )

        while current is not None:

            old_room = (
                current.get_data()
            )

            if (
                old_room.get_room_name()
                .lower()
                ==
                room.get_room_name()
                .lower()
            ):
                return False

            current = (
                current.get_next()
            )

        # thêm phòng
        self._room_list.add_room(
            room
        )

        # lưu file
        self._io_handler.save_rooms(
            self._room_list
        )

        return True

    # =================================================
    # UPDATE ROOM
    # =================================================

    def update_room(
        self,
        room_id: str,
        new_name: str
    ) -> bool:

        node = (
            self.find_room(room_id)
        )

        if node is None:
            return False

        # check tên phòng mới có bị trùng không
        current = (
            self._room_list
            .get_head()
        )

        while current is not None:

            old_room = (
                current.get_data()
            )

            if (
                old_room.get_room_id()
                != room_id
                and
                old_room.get_room_name()
                .lower()
                ==
                new_name.lower()
            ):
                return False

            current = (
                current.get_next()
            )

        # update tên
        room = node.get_data()

        room.room_name = (
            new_name.strip()
        )

        # lưu file
        self._io_handler.save_rooms(
            self._room_list
        )

        return True

    # =================================================
    # DELETE ROOM
    # =================================================

    def delete_room(
        self,
        room_id: str,
        showtime_controller
    ) -> bool:

        # không cho xóa nếu còn suất chiếu
        showtimes = (
            showtime_controller
            .get_showtime_data()
        )

        for st in showtimes:

            if (
                st.get_room_id()
                ==
                room_id
            ):
                return False

        success = (
            self._room_list
            .remove_room(room_id)
        )

        if success:

            self._io_handler.save_rooms(
                self._room_list
            )

        return success

    # =================================================
    # FIND ROOM
    # =================================================

    def find_room(
        self,
        room_id: str
    ):

        return (
            self._room_list
            .find_room(room_id)
        )

    # =================================================
    # FIND ROOM BY NAME
    # =================================================

    def find_room_by_name(
        self,
        room_name: str
    ):

        current = (
            self._room_list
            .get_head()
        )

        while current is not None:

            room = (
                current.get_data()
            )

            if (
                room.get_room_name()
                .lower()
                ==
                room_name.lower()
            ):
                return room

            current = (
                current.get_next()
            )

        return None

    # =================================================
    # GET ROOM LIST
    # =================================================

    def get_room_list(self):

        return self._room_list

    # =================================================
    # GET ROOM DATA
    # =================================================

    def get_room_data(self):

        result = []

        current = (
            self._room_list
            .get_head()
        )

        while current is not None:

            result.append(
                current.get_data()
            )

            current = (
                current.get_next()
            )

        return result

    # =================================================
    # COUNT ROOMS
    # =================================================

    def count_rooms(self):

        count = 0

        current = (
            self._room_list
            .get_head()
        )

        while current is not None:

            count += 1

            current = (
                current.get_next()
            )

        return count