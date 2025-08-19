import numpy as np                      # Xử lý ma trận bàn cờ (10x9)
import time                             # Đo thời gian để giới hạn tìm kiếm
from collections import OrderedDict                             # Tạo bảng với thứ tự để xóa mục cũ khi đầy
import random                           # Chọn nước đi ngẫu nhiên nếu không tìm được nước đi tối ưu

from Khai_bao import *
from Sinh_nuoc_di import get_valid_moves, is_king_in_check  # get_valid_moves (tạo danh sách nước đi hợp lệ) và is_king_in_check (kiểm tra Tướng bị chiếu).
from ai_Ham_danh_gia import evaluate_board                  # evaluate_board (đánh giá điểm số bàn cờ).
from game_KiemTraKetThuc import is_game_over                # is_game_over (kiểm tra trò chơi kết thúc)
from pieces import get_position_score                       # get_position_score (đánh giá điểm vị trí của quân cờ)

# Bảng lưu trữ với kích thước giới hạn
MAX_TABLE_SIZE = 200000                     # Có thể lưu được 200 000 trạng thái bàn cờ, mỗi trạng thái sẽ có 1 hash riêng để định danh
transposition_table = OrderedDict()         # Lưu trữ trạng thái bàn cờ (hash), độ sâu, điểm số, và nước đi tốt nhất dạng (m_from, n_from, m_to, n_to) hoặc None.
"""
Hash của bàn cờ (board_hash): Là một số nguyên 64-bit, chiếm khoảng 8 byte.
Độ sâu (depth): Số nguyên, khoảng 4 byte.
Điểm đánh giá (eval_score): Số thực (float), khoảng 8 byte.
Nước đi tốt nhất (best_move): Tuple 4 số nguyên (m_from, n_from, m_to, n_to) hoặc None, chiếm khoảng 16 byte (4 số nguyên x 4 byte) hoặc ít hơn nếu là None.

=> Tổng cộng, mỗi mục chiếm khoảng: 8 + 4 + 8 + 16 = 36 byte.
=> 200,000 x 36 byte = 7,200,000 byte ≈ khoảng 7.2 MB
"""


def get_pieces(board, color):
    """
    Tìm danh sách tọa độ (row, col) của các quân cờ thuộc cùng một màu (COLOR_DARK hoặc COLOR_LIGHT) trên bàn cờ.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        color (int): Màu của quân cờ (COLOR_DARK hoặc COLOR_LIGHT).

    Returns:
        list: Danh sách tọa độ (row, col) của các quân cờ thuộc màu được chỉ định.
    """
    pieces = []     # list chứa tọa độ
    for row in range(ROWS):
        for col in range(COLS):
            if board[row, col] != EMPTY and board[row, col] // 10 == color:     # Nếu ko phải empty và đúng màu đang xét thì thêm tọa độ vào list
                pieces.append((row, col))
    return pieces

def get_all_valid_moves(board, color):
    """
    Tạo danh sách tất cả nước đi hợp lệ cho các quân thuộc cùng 1 màu.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        color (int): Màu của quân cờ (COLOR_DARK hoặc COLOR_LIGHT).

    Returns:
        list: Danh sách các nước đi dạng (m_from, n_from, m_to, n_to).
    """
    moves = []
    for row, col in get_pieces(board, color):   # lấy row và col của các tọa độ từ list pieces
        piece_type = board[row, col] % 10       # xem tại đó là quân cờ gì
        valid_moves = get_valid_moves(row, col, piece_type, color, board)   # Gọi hàm Sinh nước đi 
        moves.extend([(row, col, m[0], m[1]) for m in valid_moves])     # Chuyển các nước đi thành dạng (m_from, n_from, m_to, n_to) và thêm vào danh sách
    return moves


def make_temp_move(board, move):    # Dùng để thử nước đi trong Minimax mà không làm thay đổi bàn cờ gốc
    """
    Thực hiện nước đi tạm thời và trả về thông tin để hoàn tác.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        move (tuple): Nước đi dạng (m_from, n_from, m_to, n_to).

    Returns:
        int: Quân cờ bị ăn tại ô đích (hoặc EMPTY nếu không có).
    """
    m_from, n_from, m_to, n_to = move       
    captured_piece = board[m_to, n_to]
    board[m_to, n_to] = board[m_from, n_from]
    board[m_from, n_from] = EMPTY
    return captured_piece

def undo_move(board, move, captured_piece):     # Đảm bảo bàn cờ trở về trạng thái ban đầu sau khi thử nước đi trong Minimax.
    """
    Hoàn tác nước đi tạm thời.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        move (tuple): Nước đi dạng (m_from, n_from, m_to, n_to).
        captured_piece (int): Quân cờ bị ăn tại ô đích (hoặc EMPTY).
    """
    m_from, n_from, m_to, n_to = move
    board[m_from, n_from] = board[m_to, n_to]
    board[m_to, n_to] = captured_piece

##############
def evaluate_move(board, move, ai_color):
    """
    Đánh giá nhanh nước đi để sắp xếp ưu tiên, dựa trên ăn quân, vị trí tốt, và bảo vệ Tướng.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        move (tuple): Nước đi dạng (m_from, n_from, m_to, n_to).
        ai_color (int): Màu của AI (COLOR_DARK hoặc COLOR_LIGHT).

    Returns:
        float: Điểm số của nước đi, ưu tiên ăn quân, vị trí tốt, và bảo vệ Tướng.
    """
    m_from, n_from, m_to, n_to = move
    score = 0
    
    # Ưu tiên 1: Ăn quân
    if board[m_to, n_to] != EMPTY:
        score += PIECE_VALUES.get(board[m_to, n_to] % 10, 0) * 50
    
    # Ưu tiên 2: Cải thiện vị trí
    piece_type = board[m_from, n_from] % 10
    from_score = get_position_score(piece_type, m_from, n_from, ai_color)
    to_score = get_position_score(piece_type, m_to, n_to, ai_color)
    score += (to_score - from_score) * 10
    
    # Ưu tiên 3: Bảo vệ Tướng
    temp_board = board.copy()
    captured_piece = make_temp_move(temp_board, move)
    if not is_king_in_check(temp_board, ai_color):
        score += 50
    else:
        score -= 50
    # Chỉ kiểm tra các quân tấn công chính (Xe, Pháo, Mã) của đối thủ
    opponent_color = COLOR_LIGHT if ai_color == COLOR_DARK else COLOR_DARK
    opponent_pieces = get_pieces(temp_board, opponent_color)
    king_threatened = False
    for row, col in opponent_pieces:
        piece_type = temp_board[row, col] % 10
        if piece_type in [ROOK, CANNON, KNIGHT]:  # Chỉ kiểm tra Xe, Pháo, Mã
            valid_moves = get_valid_moves(row, col, piece_type, opponent_color, temp_board)
            for m_to, n_to in valid_moves:
                opp_temp_board = temp_board.copy()
                opp_captured = make_temp_move(opp_temp_board, (row, col, m_to, n_to))
                if is_king_in_check(opp_temp_board, ai_color):
                    king_threatened = True
                    break
                undo_move(opp_temp_board, (row, col, m_to, n_to), opp_captured)
            if king_threatened:
                break
    if not king_threatened:
        score += 30
    undo_move(temp_board, move, captured_piece)
    
    return score


def minimax(board, depth, alpha, beta, maximizing_player, ai_color, game_state):
    """
    Thuật toán Minimax với cắt tỉa Alpha-Beta và Transposition Table.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        depth (int): Độ sâu tìm kiếm còn lại.
        alpha (float): Giá trị alpha cho cắt tỉa Alpha-Beta.
        beta (float): Giá trị beta cho cắt tỉa Alpha-Beta.
        maximizing_player (bool): True nếu là lượt của AI, False nếu là đối thủ.
        ai_color (int): Màu của AI (COLOR_DARK hoặc COLOR_LIGHT).

    Returns:
        tuple: (eval_score, best_move)
            - eval_score (float): Điểm đánh giá của trạng thái.
            - best_move (tuple or None): Nước đi tốt nhất dạng (m_from, n_from, m_to, n_to).
    """
    board_hash = hash(board.tobytes())
    if board_hash in transposition_table and transposition_table[board_hash][0] >= depth:
    # Nếu trạng thái đã được tính toán với độ sâu đủ lớn, trả về kết quả từ transposition_table.
        return transposition_table[board_hash][1], transposition_table[board_hash][2]
        

    if depth == 0 or is_game_over(board, ai_color, game_state)[0]:
    # Nếu depth == 0 hoặc trò chơi kết thúc (is_game_over), trả về điểm đánh giá từ evaluate_board.
        eval_score = evaluate_board(board, ai_color)
        transposition_table[board_hash] = (depth, eval_score, None)
        if len(transposition_table) > MAX_TABLE_SIZE:
            transposition_table.popitem(last=False)
        return eval_score, None

    best_move = None
    moves = get_all_valid_moves(board, ai_color if maximizing_player else (COLOR_LIGHT if ai_color == COLOR_DARK else COLOR_DARK))
    if not moves:
        eval_score = evaluate_board(board, ai_color)
        transposition_table[board_hash] = (depth, eval_score, None)
        if len(transposition_table) > MAX_TABLE_SIZE:
            transposition_table.popitem(last=False)
        return eval_score, None

    # Sắp xếp nước đi theo điểm số, Sử dụng evaluate_move để ưu tiên nước đi tốt (ăn quân, vị trí tốt)
    moves = sorted(moves, key=lambda m: evaluate_move(board, m, ai_color), reverse=True)

    if maximizing_player:       # Nếu maximizing_player (lượt AI): Tìm nước đi tối đa hóa điểm số, cập nhật alpha
        max_eval = float('-inf')
        for move in moves:
            captured_piece = make_temp_move(board, move)
            if is_king_in_check(board, ai_color):           # Kiểm tra is_king_in_check để bỏ qua nước đi khiến Tướng bị chiếu
                undo_move(board, move, captured_piece)
                continue
            eval_score, _ = minimax(board, depth - 1, alpha, beta, False, ai_color, game_state)
            undo_move(board, move, captured_piece)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:       # Cắt tỉa nếu beta <= alpha
                break
        transposition_table[board_hash] = (depth, max_eval, best_move)
        if len(transposition_table) > MAX_TABLE_SIZE:
            transposition_table.popitem(last=False)
        return max_eval, best_move
    
    else:   # Nếu không (lượt đối thủ): Tìm nước đi tối thiểu hóa điểm số, cập nhật beta
        min_eval = float('inf')
        opponent_color = COLOR_LIGHT if ai_color == COLOR_DARK else COLOR_DARK
        for move in moves:
            captured_piece = make_temp_move(board, move)
            if is_king_in_check(board, opponent_color):
                undo_move(board, move, captured_piece)
                continue
            eval_score, _ = minimax(board, depth - 1, alpha, beta, True, ai_color, game_state)
            undo_move(board, move, captured_piece)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        transposition_table[board_hash] = (depth, min_eval, best_move)
        if len(transposition_table) > MAX_TABLE_SIZE:
            transposition_table.popitem(last=False)
        return min_eval, best_move

def get_best_move(board, ai_color, max_time=30.0, game_state=None):
    """
    Tìm nước đi tốt nhất cho AI trong giới hạn thời gian.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        ai_color (int): Màu của AI (COLOR_DARK hoặc COLOR_LIGHT).
        max_time (float): Thời gian tối đa để tìm kiếm (giây).

    Returns:
        tuple or None: Nước đi tốt nhất dạng (m_from, n_from, m_to, n_to), hoặc ngẫu nhiên nếu không tìm được.
    """
    start_time = time.time()
    best_move = None
    depth = 2
    best_moves = {}  # Lưu nước đi tốt nhất theo độ sâu
    while time.time() - start_time < max_time: # and depth <= 6:  # Giới hạn độ sâu tối đa
        eval_score, move = minimax(board, depth, float('-inf'), float('inf'), True, ai_color, game_state)
        if move:
            best_move = move
            best_moves[depth] = move
        depth += 1

    # Nếu không tìm được nước đi, chọn ngẫu nhiên từ các nước đi hợp lệ
    if best_move is None:
        moves = get_all_valid_moves(board, ai_color)
        if moves:
            best_move = random.choice(moves)
            print(f"Không tìm được nước đi tối ưu trong {max_time}s, chọn ngẫu nhiên: {best_move}")
    
    return best_move