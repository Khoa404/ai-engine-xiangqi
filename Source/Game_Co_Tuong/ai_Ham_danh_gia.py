import numpy as np
from Khai_bao import *
from Sinh_nuoc_di import get_valid_moves, is_king_in_check
from game_board_manager import dark_king_pos, light_king_pos

def evaluate_material(board, color):
    """
    Đánh giá điểm vật chất trên bàn cờ.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        color (int): Màu của bên cần đánh giá (COLOR_DARK hoặc COLOR_LIGHT).

    Returns:
        tuple: (material_score, total_material)
            - material_score (float): Điểm vật chất, dương nếu có lợi cho color đang xét.
            - total_material (float): Tổng giá trị quân cờ (trừ Tướng) để xác định giai đoạn.
    """
    material_score = 0
    total_material = 0
    for row in range(ROWS):
        for col in range(COLS):
            if board[row, col] != EMPTY:
                piece_type = board[row, col] % 10       # Lấy loại quân
                piece_color = board[row, col] // 10     # Lấy màu quân

                value = PIECE_VALUES[piece_type]
                if piece_type != KING:
                    total_material += value
                if piece_color == color:        # Nếu quân cờ thuộc màu color: Cộng giá trị (material_score += value).
                    material_score += value
                else:
                    material_score -= value     # Nếu thuộc màu đối phương: Trừ giá trị (material_score -= value)
    return material_score, total_material


def evaluate_position(board, color):
    """
    Đánh giá điểm vị trí của các quân cờ.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        color (int): Màu của bên cần đánh giá (COLOR_DARK hoặc COLOR_LIGHT).

    Returns:
        float: Điểm vị trí, dương nếu có lợi cho color.
    """
    position_score = 0
    for row in range(ROWS):
        for col in range(COLS):
            if board[row, col] != EMPTY:
                piece_type = board[row, col] % 10
                piece_color = board[row, col] // 10

                pos_value = 0
                if piece_type == PAWN:
                    pos_value = PAWN_POSITION_TABLE[row, col]

                elif piece_type == KNIGHT:
                    pos_value = KNIGHT_POSITION_TABLE[row, col]

                elif piece_type in [ROOK, CANNON]:
                    pos_value = ROOK_CANNON_POSITION_TABLE[row, col]

                elif piece_type in [BISHOP, ELEPHANT]:
                    pos_value = BISHOP_ELEPHANT_POSITION_TABLE[row, col]

                elif piece_type == KING:
                    pos_value = KING_POSITION_TABLE[row, col]
                # Nếu quân mình ở vị trí tốt thì + điểm, nếu là quân đối thủ thì - điểm
                position_score += pos_value if piece_color == color else -pos_value
    return position_score


def evaluate_mobility(board, color, valid_moves_cache):
    """
    Đánh giá điểm di động dựa trên số nước đi hợp lệ.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        color (int): Màu của bên cần đánh giá (COLOR_DARK hoặc COLOR_LIGHT).
        valid_moves_cache (dict): Cache chứa nước đi hợp lệ cho mỗi quân cờ.

    Returns:
        float: Điểm di động, dương nếu có lợi cho color.
    """
    mobility_score = 0
    opponent_color = COLOR_LIGHT if color == COLOR_DARK else COLOR_DARK
    for row in range(ROWS):
        for col in range(COLS):
            if board[row, col] != EMPTY:
                piece_color = board[row, col] // 10

                if piece_color == color:
                    cache_key = (row, col, piece_color, hash(board.tobytes()))      # hash(board.tobytes(): Tạo key cho cache

                    # Nếu chưa có trong valid_moves_cache, gọi get_valid_moves để lấy danh sách nước đi hợp lệ, với:
                        # check_king_facing=True: Kiểm tra luật Tướng đối mặt.
                        # check_check=True: Kiểm tra nước đi không để Tướng bị chiếu.
                    if cache_key not in valid_moves_cache:
                        piece_type = board[row, col] % 10
                        valid_moves_cache[cache_key] = get_valid_moves(row, col, piece_type, piece_color, board, check_king_facing=True, check_check=True)
                    # Cộng số lượng nước đi hợp lệ (len(valid_moves_cache[cache_key])) vào mobility_score
                    mobility_score += len(valid_moves_cache[cache_key])
    return mobility_score


def evaluate_king_safety(board, color, own_king_pos, palace_rows):
    """
    Đánh giá an toàn Tướng dựa trên Sĩ/Tượng trong cung.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        color (int): Màu của bên cần đánh giá (COLOR_DARK hoặc COLOR_LIGHT).
        own_king_pos (tuple): Vị trí Tướng của bên color (row, col).
        palace_rows (list): Danh sách hàng của cung (0-2 cho Đen, 7-9 cho Đỏ).

    Returns:
        float: Điểm an toàn Tướng, dương nếu có lợi cho color.
    """
    king_safety_score = 0
    palace_pieces = 0       # Đếm sô Sĩ/Tướng có gần Tướng
    if own_king_pos:
        row, col = own_king_pos     # Vị trí Tướng

        # Kiểm tra 8 ô xung quanh Tướng (lên, xuống, trái, phải, chéo).
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:  
            r, c = row + dr, col + dc

            # Xác định cung (palace_rows: hàng 0-2 cho Đen, 7-9 cho Đỏ; cột 3-5).
            if r in palace_rows and 3 <= c <= 5 and board[r, c] % 10 in [BISHOP, ELEPHANT]:
                king_safety_score += 10             # Nếu có Sĩ/Tượng (BISHOP, ELEPHANT): Cộng +10 vào king_safety_score
                if board[r, c] // 10 == color:      
                    palace_pieces += 1              # Nếu Sĩ/Tượng thuộc màu color: Tăng palace_pieces

    # Nếu số Sĩ/Tượng trong cung < 2: Phạt -20 * (2 - palace_pieces)
    if palace_pieces < 2:
        king_safety_score -= 20 * (2 - palace_pieces)
    return king_safety_score


def evaluate_cannon_control(board, color, valid_moves_cache):
    """
    Đánh giá kiểm soát Pháo (cột mở, Pháo sau bình phong, Pháo đầu).

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        color (int): Màu của bên cần đánh giá (COLOR_DARK hoặc COLOR_LIGHT).
        valid_moves_cache (dict): Cache chứa nước đi hợp lệ cho mỗi quân cờ.

    Returns:
        float: Điểm kiểm soát Pháo, dương nếu có lợi cho color.
    """
    cannon_control_score = 0
    opponent_color = COLOR_LIGHT if color == COLOR_DARK else COLOR_DARK
    for row in range(ROWS):
        for col in range(COLS):
            # Duyệt qua bàn cờ tìm Pháo thuộc màu mình đang xét
            if board[row, col] != EMPTY and board[row, col] % 10 == CANNON and board[row, col] // 10 == color:

                # Pháo đầu: Nếu ở hàng 2 (Đen) hoặc 7 (Đỏ), cộng +15 (vị trí tấn công mạnh)
                if (color == COLOR_DARK and row == 2) or (color == COLOR_LIGHT and row == 7):
                    cannon_control_score += 15

                # Pháo ngang (kiểm soát hàng)
                for dc in [-1, 1]:
                    c = col
                    while 0 <= c + dc < COLS:
                        c += dc
                        if board[row, c] != EMPTY:
                            break
                    else:
                        cannon_control_score += 10  # Hàng mở, nếu không có quân cờ chắn, cộng +10

                # Cột mở
                for dr in [-1, 1]:
                    r = row
                    while 0 <= r + dr < ROWS:
                        r += dr
                        if board[r, col] != EMPTY:
                            break
                    else:
                        cannon_control_score += 20  # Cột dọc, nếu không có quân cờ chắn, cộng +20

                # Pháo sau bình phong, nếu có đúng một quân cờ làm bình phong và quân tiếp theo là quân đối phương, cộng +30
                for dr in [-1, 1]:
                    r, screen_count = row, 0
                    while 0 <= r + dr < ROWS:
                        r += dr
                        if board[r, col] != EMPTY:
                            screen_count += 1
                            if screen_count == 1:
                                continue
                            if screen_count == 2 and board[r, col] // 10 == opponent_color: # opponent_color: màu của đối thủ
                                cannon_control_score += 30
                                break
                            break
    return cannon_control_score


def evaluate_board(board, color):
    """
    Đánh giá trạng thái bàn cờ từ góc nhìn của một bên.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        color (int): Màu của bên cần đánh giá (COLOR_DARK hoặc COLOR_LIGHT).

    Returns:
        float: Điểm số tổng hợp, dương nếu có lợi cho color, âm nếu bất lợi.

    Notes:
        Đánh giá dựa trên các yếu tố: vật chất, vị trí, di động, an toàn Tướng, chiếu tướng,
        kiểm soát trung tâm, cấu trúc Tốt, tấn công/phòng thủ, kiểm soát Pháo, đe dọa Tướng.
    """
    # Khởi tạo các điểm số
    valid_moves_cache = {}      # Tạo valid_moves_cache để lưu trữ nước đi hợp lệ, sử dụng hash(board.tobytes())
    material_score = 0          # vật chất
    position_score = 0          # vị trí
    mobility_score = 0          # linh hoạt
    king_safety_score = 0       # an toàn Tướng

    check_score = 0             # chiếu Tướng
    center_control_score = 0    # kiểm soát trung tâm
    pawn_structure_score = 0    # cấu trúc quân Binh
    attack_defense_score = 0    # tấn công / phòng thủ
    cannon_control_score = 0    # kiểm soát Pháo
    king_threat_score = 0       # đe dọa Tướng
    
    # Màu đối phương
    opponent_color = COLOR_LIGHT if color == COLOR_DARK else COLOR_DARK
    
    # Phạm vi hàng của cung
    palace_rows = [0, 1, 2] if color == COLOR_DARK else [7, 8, 9]
    
    # Các ô trung tâm
    center_squares = [(4, 3), (4, 4), (4, 5), (5, 3), (5, 4), (5, 5)]
    
    # Tính vật chất và giai đoạn trận đấu
    material_score, total_material = evaluate_material(board, color)
    
    # Tính điểm vị trí
    position_score = evaluate_position(board, color)
    
    # Tính điểm di động
    mobility_score = evaluate_mobility(board, color, valid_moves_cache)
    
    # Tính điểm an toàn Tướng
    king_safety_score = evaluate_king_safety(board, color, dark_king_pos if color == COLOR_DARK else light_king_pos, palace_rows)
    
    # Tính điểm kiểm soát Pháo
    cannon_control_score = evaluate_cannon_control(board, color, valid_moves_cache)
    
    # Tính điểm chiếu tướng và đe dọa Tướng
    if is_king_in_check(board, opponent_color):
        check_score += 50
    

    # Đánh giá tấn công/phòng thủ và đe dọa Tướng
    for row in range(ROWS):
        for col in range(COLS):

            if board[row, col] != EMPTY:
                piece_type = board[row, col] % 10
                piece_color = board[row, col] // 10

                if piece_color == color:
                    cache_key = (row, col, piece_color, hash(board.tobytes()))

                    if cache_key not in valid_moves_cache:
                        valid_moves_cache[cache_key] = get_valid_moves(row, col, piece_type, piece_color, board, check_king_facing=True, check_check=True)
                    
                    for move_row, move_col in valid_moves_cache[cache_key]:
                        # Cộng điểm nếu quân cờ của color có thể ăn quân đối phương (target_value // 2)
                        if board[move_row, move_col] != EMPTY and board[move_row, move_col] // 10 == opponent_color:
                            target_value = PIECE_VALUES[board[move_row, move_col] % 10]
                            attack_defense_score += target_value // 2

                    # Thưởng thêm nếu Xe/Pháo/Mã ở sâu trong lãnh thổ đối phương (hàng 7-9 cho Đen, 0-2 cho Đỏ).
                    if piece_type in [ROOK, CANNON, KNIGHT]:
                        if (color == COLOR_DARK and row >= 7) or (color == COLOR_LIGHT and row <= 2):
                            attack_defense_score += 15 if piece_type in [ROOK, CANNON] else 10

                elif piece_type in [ROOK, CANNON, KNIGHT]:
                    cache_key = (row, col, piece_color, hash(board.tobytes()))

                    if cache_key not in valid_moves_cache:
                        valid_moves_cache[cache_key] = get_valid_moves(row, col, piece_type, piece_color, board, check_king_facing=True, check_check=True)
                    own_king_pos = dark_king_pos if color == COLOR_DARK else light_king_pos

                    # Phạt nếu quân đối phương (Xe, Pháo, Mã) có thể tấn công Tướng của color đang xét
                    for move_row, move_col in valid_moves_cache[cache_key]:
                        if own_king_pos and (move_row, move_col) == own_king_pos:
                            king_threat_score -= 50 if piece_type in [ROOK, CANNON, KNIGHT] else 30
                        
                        # Phạt nặng hơn nếu có đường thông thoáng từ Xe/Pháo đến Tướng (clear_path)
                        if piece_type in [ROOK, CANNON] and own_king_pos and move_col == own_king_pos[1]:
                            clear_path = True
                            r = row
                            while r != own_king_pos[0]:
                                r += 1 if r < own_king_pos[0] else -1
                                if r != own_king_pos[0] and board[r, col] != EMPTY:
                                    clear_path = False
                                    break
                            if clear_path:
                                king_threat_score -= 40
    
    # Đánh giá cấu trúc Tốt
    for row in range(ROWS):
        for col in range(COLS):

            if board[row, col] % 10 == PAWN and board[row, col] // 10 == color:

                # Thưởng nếu Tốt tiến sâu (hàng 5+ cho Đen, 4- cho Đỏ)
                if (color == COLOR_DARK and row >= 5) or (color == COLOR_LIGHT and row <= 4):
                    pawn_structure_score += 20

                # Thưởng nếu Tốt ở trung tâm cung đối phương (cột 3-5)
                if (color == COLOR_DARK and row >= 7 and col in [3, 4, 5]) or \
                   (color == COLOR_LIGHT and row <= 2 and col in [3, 4, 5]):
                    pawn_structure_score += 20

                # Thưởng nếu có Tốt liền kề (+10)
                for dc in [-1, 1]:
                    if 0 <= col + dc < COLS and board[row, col + dc] % 10 == PAWN:
                        pawn_structure_score += 10

                # Phạt nếu Tốt bị cô lập (-10) 
                pawn_range = range(row, ROWS) if color == COLOR_DARK else range(0, row + 1)
                is_isolated = True
                for dc in [-1, 1]:
                    if 0 <= col + dc < COLS:
                        for r in pawn_range:
                            if board[r, col + dc] % 10 == PAWN:
                                is_isolated = False
                                break
                    if not is_isolated:
                        break
                if is_isolated:
                    pawn_structure_score -= 10
    
    # Kiểm soát trung tâm
    # Thưởng nếu quân cờ của color chiếm các ô trung tâm (4,3), (4,4), (4,5), (5,3), (5,4), (5,5).
    for row, col in center_squares:
        if board[row, col] != EMPTY and board[row, col] // 10 == color:
            piece_type = board[row, col] % 10
            # Xe/Pháo/Mã được thưởng +10, các quân khác +5
            center_control_score += 10 if piece_type in [ROOK, CANNON, KNIGHT] else 5
    
    # Xác định giai đoạn trận đấu
    if total_material < 2000:
        game_phase = 'endgame'      # Tàn cuộc
    elif total_material < 4000:
        game_phase = 'middlegame'   # Tung cuộc
    else:
        game_phase = 'opening'      # Khai cuộc

    weights = WEIGHTS[game_phase]   # Áp dụng trọng số (WEIGHTS[game_phase]) để điều chỉnh tầm quan trọng của từng yếu tố
    
    # Kết hợp điểm với trọng số
    score = (
        material_score * weights['material'] +
        position_score * weights['position'] +
        mobility_score * weights['mobility'] +
        king_safety_score * weights['king_safety'] +
        check_score * weights['check'] +
        center_control_score * weights['center_control'] +
        pawn_structure_score * weights['pawn_structure'] +
        attack_defense_score * weights['attack_defense'] +
        cannon_control_score * weights['cannon_control'] +
        king_threat_score * weights['king_threat']
    )
    
    return score