
#def replay_game():
#    print("Chế độ Xem lại ván đấu chưa được triển khai!")  # In thông báo chưa triển khai

import json
import numpy as np
import time
from Khai_bao import *
from Ban_co import init_board, display_board
from game_ThucHienNuocDi_CapNhatLichSu import GameState, make_move, reset_move_history_file

def replay_game():
    """
    Phát lại ván cờ từ tệp move_history.json.
    """
    try:
        with open('move_history.json', 'r', encoding='utf-8') as f:     # 'r': chế độ đọc
            move_data = json.load(f)        # Dùng json.load để đọc dữ liệu thành danh sách move_data.
    except FileNotFoundError:
        print("Không tìm thấy lịch sử nước đi!")
        return

    board = init_board()
    game_state = GameState()
    reset_move_history_file()   # Gọi reset_move_history_file() để xóa lịch sử nước đi hiện tại (tránh ghi đè khi phát lại).

    for move_entry in move_data:    # Duyệt qua từng move_entry trong move_data
        move_str = move_entry['move']
        # Phân tích nước đi từ chuỗi (giả sử định dạng: "Đen di chuyển Tốt từ (3, 2) đến (4, 2)")
        import re
        # Sử dụng (re.search) để trích xuất tọa độ (m_from, n_from, m_to, n_to) từ chuỗi.
        match = re.search(r'\((\d+), (\d+)\) đến \((\d+), (\d+)\)', move_str)

        if match:
            m_from, n_from, m_to, n_to = map(int, match.groups())
            color_type = COLOR_DARK if "Đen" in move_str else COLOR_LIGHT

            display_board(board)
            
            print(f"\nPhát lại: {move_str}")
            board = make_move(board, (m_from, n_from, m_to, n_to), color_type, game_state)
            time.sleep(1)  # Tạm dừng 1 giây để xem nước đi
        else:
            print(f"Lỗi: Không thể phân tích nước đi: {move_str}")

    display_board(board)
    print("\nKết thúc phát lại ván cờ!")