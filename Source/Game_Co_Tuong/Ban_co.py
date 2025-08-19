import numpy as np
from Khai_bao import *

def init_board():
    """Khởi tạo bàn cờ cờ tướng với trạng thái ban đầu."""
    board = np.zeros((ROWS, COLS), dtype=int)
    # Đặt các quân cờ Đen
    pieces = [ROOK, KNIGHT, ELEPHANT, BISHOP, KING, BISHOP, ELEPHANT, KNIGHT, ROOK]
    for col, piece in enumerate(pieces):
        board[0, col] = piece + COLOR_DARK * 10
    board[2, [1, 7]] = CANNON + COLOR_DARK * 10
    board[3, [0, 2, 4, 6, 8]] = PAWN + COLOR_DARK * 10
    # Đặt các quân cờ Đỏ
    for col, piece in enumerate(pieces):
        board[9, col] = piece + COLOR_LIGHT * 10
    board[7, [1, 7]] = CANNON + COLOR_LIGHT * 10
    board[6, [0, 2, 4, 6, 8]] = PAWN + COLOR_LIGHT * 10
    # Debug: In giá trị bàn cờ sau khi khởi tạo
    #print("[DEBUG] Giá trị bàn cờ sau khi khởi tạo:")
    #print(board)
    return board

def get_piece_char(value):
    """Trả về ký tự biểu diễn quân cờ dựa trên giá trị ô."""
    piece_names = {
        EMPTY: '.', PAWN: 'b', BISHOP: 's', ELEPHANT: 't',
        KNIGHT: 'm', CANNON: 'p', ROOK: 'x', KING: 'tg'
    }
    piece_type = value % 10
    color_type = value // 10
    char = piece_names.get(piece_type, '?')
    if color_type == COLOR_DARK:
        return char.lower()
    elif color_type == COLOR_LIGHT:
        return char.upper()
    return '.'

def display_board(board):
    """Hiển thị bàn cờ ra màn hình."""
    print("     " + "  ".join(f"{i}" for i in range(COLS)) + "  ")
    print(" ")
    for row in range(ROWS):
        line = f"{row:^2}|  "
        for col in range(COLS):
            char = get_piece_char(board[row, col])
            line += char.center(2) + " "
        line += "|"
        print(line.rstrip())
        if row == 4:
            print("  |  " + " ~~ " * 6 + "   |")
    print(" ")

def to_mailbox_index(row, col):
    """Chuyển tọa độ (row, col) sang chỉ số trong mailbox 14x13."""
    return (row + 2) * MAILBOX_COLS + (col + 2)

def from_mailbox_index(idx):
    """Chuyển chỉ số mailbox về tọa độ (row, col) trên bàn cờ 10x9."""
    if idx < 0 or idx >= len(mailbox182) or mailbox182[idx] == -1:
        return None
    pos = mailbox182[idx]
    return (pos // COLS, pos % COLS)