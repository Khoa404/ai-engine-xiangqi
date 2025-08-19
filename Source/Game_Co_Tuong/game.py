from game_XuLyInput import print_all_valid_moves, get_player_move
from game_ThucHienNuocDi_CapNhatLichSu import GameState, make_move, print_move_history, reset_move_history_file
from game_KiemTraNuocDiHopLe import is_valid_move
from Ban_co import init_board

# Re-export các hàm để các file khác có thể nhập từ game.py
__all__ = [
    'is_valid_move',                    # Hàm kiểm tra tính hợp lệ của một nước đi
    'make_move',                        # Hàm thực hiện nước đi và cập nhật bàn cờ, lịch sử
    'print_move_history',               # Hàm in lịch sử nước đi ra console
    'print_all_valid_moves',            # Hàm hiển thị tất cả các nước đi hợp lệ cho người chơi
    'get_player_move',                  # Hàm lấy nước đi từ đầu vào của người chơi
    'init_board',                       # Hàm khởi tạo bàn cờ
    'GameState',                        # Lớp quản lý trạng thái trò chơi
    'reset_move_history_file'           # Hàm đặt lại tệp lịch sử nước đi
]