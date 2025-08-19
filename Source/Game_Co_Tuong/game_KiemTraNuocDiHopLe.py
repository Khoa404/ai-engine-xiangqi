from Khai_bao import *
from Sinh_nuoc_di import get_valid_moves
from Ban_co import get_piece_char
import random

# Cache để lưu trữ nước đi hợp lệ trong một lượt
_valid_moves_cache = {}

def reset_valid_moves_cache():
    """Xóa cache nước đi hợp lệ khi bắt đầu lượt mới."""
    _valid_moves_cache.clear()

def is_valid_move(board, move, side):
    """
    Kiểm tra tính hợp lệ của một nước đi.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        move (tuple): Nước đi dạng (m_from, n_from, m_to, n_to).
        side (int): Bên chơi (1 cho Đen, 2 cho Đỏ).

    Returns:
        bool: True nếu nước đi hợp lệ, False nếu không hợp lệ.

    Notes:
        In ra thông báo lỗi cụ thể và gợi ý nước đi hợp lệ khi cần.
    """
    m_from, n_from, m_to, n_to = move
    color_type = COLOR_DARK if side == 1 else COLOR_LIGHT  # Ánh xạ side sang màu (1: Đen, 2: Đỏ)
    
    # Kiểm tra nước đi phải thay đổi vị trí
    if m_from == m_to and n_from == n_to:
        print(f"\nLỗi: Nước đi từ ({m_from}, {n_from}) đến ({m_to}, {n_to}) không thay đổi vị trí!")
        return False
    
    # Kiểm tra tọa độ nằm trong bàn cờ
    if not (0 <= m_from < ROWS and 0 <= n_from < COLS and 0 <= m_to < ROWS and 0 <= n_to < COLS):
        print(f"\nLỗi: Tọa độ ({m_from}, {n_from}) hoặc ({m_to}, {n_to}) ngoài bàn cờ!")
        return False
    
    # Kiểm tra có quân cờ tại vị trí bắt đầu
    if board[m_from, n_from] == EMPTY:
        print(f"\nLỗi: Không có quân cờ tại vị trí bắt đầu ({m_from}, {n_from})!")
        return False
    
    # Kiểm tra quân cờ thuộc về người chơi
    if board[m_from, n_from] // 10 != color_type:
        print(f"\nLỗi: Quân cờ tại ({m_from}, {n_from}) không thuộc về {'Đen' if color_type == COLOR_DARK else 'Đỏ'}!")
        print("Hãy chọn một quân cờ thuộc về bạn.")
        return False
    
    # Kiểm tra không ăn quân cùng phe
    if board[m_to, n_to] != EMPTY and board[m_to, n_to] // 10 == color_type:
        print(f"\nLỗi: Không thể ăn quân cùng phe tại ({m_to}, {n_to})!")
        return False
    
    # Kiểm tra luật di chuyển của quân cờ
    piece_type = board[m_from, n_from] % 10
    cache_key = (m_from, n_from, color_type, hash(board.tobytes()))
    if cache_key not in _valid_moves_cache:
        _valid_moves_cache[cache_key] = get_valid_moves(m_from, n_from, piece_type, color_type, board, check_king_facing=True, check_check=True)
    
    valid_moves = _valid_moves_cache[cache_key]
    if (m_to, n_to) not in valid_moves:
        print(f"\nLỗi: Nước đi từ ({m_from}, {n_from}) đến ({m_to}, {n_to}) không đúng luật!")
        print(f"Nước đi hợp lệ cho {get_piece_char(board[m_from, n_from])} tại ({m_from}, {n_from}): {valid_moves}")
        if valid_moves:
            suggested_move = random.choice(valid_moves)
            print(f"Gợi ý: Thử di chuyển đến ({suggested_move[0]}, {suggested_move[1]})")
        return False
    
    print(f"\nOk!! Nước đi ({m_from}, {n_from}) đến ({m_to}, {n_to}) hợp lệ.")
    return True