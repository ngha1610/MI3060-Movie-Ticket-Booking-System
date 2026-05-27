Movie-Ticket-Booking-System/
│
├── data/                       # Nơi chứa các file CSDL
│   ├── users.csv
│   ├── movies.csv
│   ├── rooms.csv              
│   ├── showtimes.csv
│   ├── tickets.csv
│   └── data_generator.py       # Tool chạy độc lập để sinh file CSV
│
├── models/                     # TẦNG 4: DATA MODELS LAYER
│   └── entities.py             # Chứa toàn bộ các class thực thể (Data Models)
│
├── structures/                 # TẦNG 3: DATA ACCESS & STRUCTURES LAYER
│   ├── nodes.py                # Chứa các class Node (UserNode, MovieNode...)
│   ├── linked_lists.py         # Chứa MovieLinkedList, TicketLinkedList...
│   ├── hash_table.py           # Chứa UserHashTable
│   └── file_io.py              # Chứa FileIOHandler (Đọc/Ghi file)
│
├── controllers/                # TẦNG 2: BUSINESS LOGIC LAYER
│   ├── auth_controller.py
│   ├── movie_controller.py
│   ├── room_controller.py      
│   ├── showtime_controller.py
│   ├── booking_controller.py
│   └── admin_controller.py
│
├── ui/                         # TẦNG 1: PRESENTATION LAYER (Giao diện Streamlit)
│   ├── ui_admin.py             # Chứa class/hàm AdminUI
│   └── ui_customer.py          # Chứa class/hàm CustomerUI
│   
│
└── app.py                      # MAIN MENU: Điểm khởi chạy của ứng dụng Streamlit
