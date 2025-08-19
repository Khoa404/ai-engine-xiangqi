import json
import time
import numpy as np
from Ban_co import get_piece_char
from game_board_manager import update_king_pos
from Khai_bao import *

# Quản lý trạng thái trò chơi (GameState): Lưu người chơi hiện tại, lịch sử nước đi, và thời gian tích lũy.
# Cung cấp một đối tượng để theo dõi trạng thái trò chơi xuyên suốt các chế độ chơi.
class GameState:
    def __init__(self):
        self.current_player = COLOR_LIGHT # 1: Đen, 2: Đỏ
        self.move_history = []  # Lưu trữ lịch sử nước đi
        self.time_tracker = {COLOR_DARK: 0.0, COLOR_LIGHT: 0.0}  # Thời gian tích lũy mỗi bên

def save_move_history_to_file(move_history):
    """
    Lưu lịch sử nước đi vào tệp JSON.

    Args:
        move_history (list): Danh sách các nước đi.
    """
    with open('move_history.json', 'w', encoding='utf-8') as f:
        json.dump(move_history, f, ensure_ascii=False, indent=2)

def reset_move_history_file():
    """
    Đặt lại tệp lịch sử nước đi.
    """
    with open('move_history.json', 'w', encoding='utf-8') as f:
        json.dump([], f)

def print_move_history(game_state):
    """
    In lịch sử nước đi ra console.

    Args:
        game_state (GameState): Đối tượng trạng thái trò chơi.
    """
    if not game_state.move_history:
        print("Chưa có nước đi nào.")
        return
    print("\nLịch sử nước đi:")
    for move in game_state.move_history:
        print(move['move'])

def make_move(board, move, color_type, game_state):
    """
    Thực hiện một nước đi trên bàn cờ và cập nhật trạng thái trò chơi.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        move (tuple): Nước đi dạng (m_from, n_from, m_to, n_to).
        color_type (int): Màu của người chơi (COLOR_DARK hoặc COLOR_LIGHT).
        game_state (GameState): Đối tượng trạng thái trò chơi.

    Returns:
        np.ndarray: Bàn cờ đã cập nhật.
    """
    m_from, n_from, m_to, n_to = move
    start_time = time.time()

    # Tạo bản sao bàn cờ
    new_board = board.copy()            # Sao chép board để tránh thay đổi trực tiếp (new_board = board.copy()).
    
    # Lấy thông tin quân cờ
    piece = new_board[m_from, n_from]   # Lấy giá trị quân cờ tại (m_from, n_from) bằng new_board[m_from, n_from]
    piece_char = get_piece_char(piece)  # Chuyển thành tên quân cờ (Xe, Mã, Tốt, v.v.) bằng get_piece_char (từ Ban_co.py)
    
    # Cập nhật bàn cờ
    new_board[m_to, n_to] = new_board[m_from, n_from]
    new_board[m_from, n_from] = EMPTY
    
    # Cập nhật vị trí Tướng
    # Gọi update_king_pos(new_board, move) (từ game_board_manager.py) để cập nhật vị trí Tướng nếu nước đi liên quan đến Tướng.
    update_king_pos(new_board, move)   
    
    # Tính thời gian nước đi
    move_time = time.time() - start_time
    game_state.time_tracker[color_type] += move_time
    
    # Tạo chuỗi mô tả nước đi
    player = 'Đen' if color_type == COLOR_DARK else 'Đỏ'
    move_str = f"{player} di chuyển {piece_char} từ ({m_from}, {n_from}) đến ({m_to}, {n_to})"
    
    # Lưu vào lịch sử nước đi
    game_state.move_history.append({
        'move': move_str,
        'color': color_type,
        'time': move_time
    })
    
    # Lưu lịch sử vào tệp
    save_move_history_to_file(game_state.move_history)
    
    return new_board