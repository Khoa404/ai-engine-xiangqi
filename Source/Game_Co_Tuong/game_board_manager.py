import time
from collections import defaultdict
from Khai_bao import *
from Ban_co import init_board

# Biến toàn cục
board = None
move_history = []
time_tracker = {COLOR_DARK: 0.0, COLOR_LIGHT: 0.0}
current_player = COLOR_DARK
last_move_time = time.time()
move_repetition = defaultdict(int)

dark_king_pos = (0, 4)  # Vị trí ban đầu của Tướng Đen
light_king_pos = (9, 4)  # Vị trí ban đầu của Tướng Đỏ

def update_king_pos(board, move):
    """Cập nhật vị trí Tướng sau mỗi nước đi."""
    global dark_king_pos, light_king_pos
    m_from, n_from, m_to, n_to = move
    piece = board[m_to, n_to]
    if piece == COLOR_DARK * 10 + KING:
        dark_king_pos = (m_to, n_to)
    elif piece == COLOR_LIGHT * 10 + KING:
        light_king_pos = (m_to, n_to)
    # Kiểm tra nếu Tướng bị ăn
    captured_piece = board[m_to, n_to] if board[m_to, n_to] != piece else EMPTY
    if captured_piece == COLOR_DARK * 10 + KING:
        dark_king_pos = None
    elif captured_piece == COLOR_LIGHT * 10 + KING:
        light_king_pos = None