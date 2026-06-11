from models.entities import Room

from data_structures.linked_lists import RoomLinkedList

from models.file_io import FileIOHandler

# =====================================================
# ROOM CONTROLLER: BỘ ĐIỀU KHIỂN HẠ TẦNG PHÒNG CHIẾU
# =====================================================

class RoomController:

    def __init__(
        self,
        io_handler: FileIOHandler
    ):
        self._io_handler = io_handler
        self._room_list = RoomLinkedList()
        self._io_handler.load_rooms(self._room_list)

    # =================================================
    # ADD ROOM: THÊM PHÒNG CHIẾU MỚI
    # =================================================
    def add_room(self, room: Room) -> bool:
        existed = self._room_list.find_room(room.get_room_id())
        if existed:
            return False

        current = self._room_list.get_head()
        while current is not None:
            old_room = current.get_data()
            
            # So khớp không phân biệt hoa thường để tránh trùng lặp
            if old_room.get_room_name().lower() == room.get_room_name().lower():
                return False

            current = current.get_next()

        self._room_list.add_room(room)
        self._io_handler.save_rooms(self._room_list)
        return True

    # =================================================
    # UPDATE ROOM: CẬP NHẬT THÔNG TIN PHÒNG
    # =================================================
    def update_room(self, room_id: str, new_name: str) -> bool:
        node = self.find_room(room_id)
        if node is None:
            return False

        current = self._room_list.get_head()
        while current is not None:
            old_room = current.get_data()
            
            # Kiểm tra xung đột tên với các phòng khác
            if (old_room.get_room_id() != room_id and 
                old_room.get_room_name().lower() == new_name.lower()):
                return False

            current = current.get_next()

        room = node.get_data()
        
        room.set_room_name(new_name)
        
        self._io_handler.save_rooms(self._room_list)
        return True

    # =================================================
    # DELETE ROOM: XÓA PHÒNG CHIẾU
    # =================================================
    def delete_room(self, room_id: str) -> bool:
        success = self._room_list.remove_room(room_id)
        if success:
            self._io_handler.save_rooms(self._room_list)
        return success

    # =================================================
    # FIND ROOM & OTHERS: CÁC HÀM TÌM KIẾM VÀ TRUY XUẤT
    # =================================================
    def find_room(self, room_id: str):
        return self._room_list.find_room(room_id)

    def find_room_by_name(self, room_name: str):
        current = self._room_list.get_head()
        while current is not None:
            room = current.get_data()
            
            # Chuyển về chữ thường để so sánh không phân biệt hoa thường
            if room.get_room_name().lower() == room_name.lower():
                return room

            current = current.get_next()

        return None

    def get_room_list(self):
        return self._room_list

    def get_room_data(self):
        result = []
        current = self._room_list.get_head()
        while current is not None:
            result += [current.get_data()]
            current = current.get_next()
        return result

    def count_rooms(self):
        count = 0
        current = self._room_list.get_head()
        while current is not None:
            count += 1
            current = current.get_next()
        return count