"""
File này cung cấp các hàm để:

1. Kiểm tra ô đích có trống hoặc chứa quân đối phương (is_opponent_or_empty).
2. Kiểm tra hai Tướng có đối mặt nhau không (is_kings_facing).
3. Kiểm tra Tướng của một bên có bị chiếu không (is_king_in_check).
4. Xác định quân cờ đang chiếu Tướng (get_checking_piece).
5. Thực hiện nước đi tạm thời để kiểm tra (make_temp_move).
6. Tạo danh sách các nước đi hợp lệ cho một quân cờ (get_valid_moves).

"""
from Khai_bao import *
from Ban_co import get_piece_char

def is_opponent_or_empty(r, c, color_type, board):
    """Kiểm tra ô tại (r, c) có trống hoặc chứa quân đối phương."""
    value = board[r, c]
    return value == EMPTY or (value != EMPTY and value // 10 != color_type)

def is_kings_facing(board):
    """Kiểm tra xem hai Tướng có đối mặt nhau không."""
    dark_king_pos = None
    light_king_pos = None
    for row in range(ROWS):
        for col in range(COLS):

            # Tìm vị trí Tướng Đen (COLOR_DARK * 10 + KING) và Tướng Đỏ (COLOR_LIGHT * 10 + KING)
            if board[row, col] == COLOR_DARK * 10 + KING:
                dark_king_pos = (row, col)
            elif board[row, col] == COLOR_LIGHT * 10 + KING:
                light_king_pos = (row, col)

    # Nếu cả hai Tướng được tìm thấy và cùng cột, kiểm tra các ô giữa chúng (từ min_row + 1 đến max_row - 1).            
    if dark_king_pos and light_king_pos and dark_king_pos[1] == light_king_pos[1]:
        col = dark_king_pos[1]
        min_row = min(dark_king_pos[0], light_king_pos[0])
        max_row = max(dark_king_pos[0], light_king_pos[0])
        for r in range(min_row + 1, max_row):
            if board[r, col] != EMPTY:
                return False
            
        return True     # Nếu tất cả ô giữa đều trống, trả về True (hai Tướng đối mặt).
    return False

def is_king_in_check(board, color_type):
    """Kiểm tra xem Tướng của color_type có bị chiếu không."""
    king_pos = None
    for row in range(ROWS):
        for col in range(COLS):

            if board[row, col] == color_type * 10 + KING:
                king_pos = (row, col)   # Tìm vị trí Tướng của color_type
                break

        if king_pos:
            break
    if not king_pos:
        return False
    
    # Duyệt qua tất cả các ô trên bàn cờ, tìm quân đối phương (opponent_color)
    opponent_color = COLOR_LIGHT if color_type == COLOR_DARK else COLOR_DARK
    for row in range(ROWS):
        for col in range(COLS):
            if board[row, col] != EMPTY and board[row, col] // 10 == opponent_color:
                piece_type = board[row, col] % 10

                # Với mỗi quân đối phương, lấy danh sách nước đi hợp lệ bằng get_valid_moves
                moves = get_valid_moves(row, col, piece_type, opponent_color, board, check_king_facing=False, check_check=False)

                # Nếu vị trí Tướng nằm trong danh sách nước đi của bất kỳ quân đối phương nào, trả về True
                if king_pos in moves:
                    return True
    return False

def get_checking_piece(board, color_type):
    """Xác định quân cờ đang chiếu Tướng."""
    king_pos = None
    for row in range(ROWS):
        for col in range(COLS):
            if board[row, col] == color_type * 10 + KING:
                king_pos = (row, col)
                break
        if king_pos:
            break
    if not king_pos:
        return None
    opponent_color = COLOR_LIGHT if color_type == COLOR_DARK else COLOR_DARK
    for row in range(ROWS):
        for col in range(COLS):
            if board[row, col] != EMPTY and board[row, col] // 10 == opponent_color:
                piece_type = board[row, col] % 10
                moves = get_valid_moves(row, col, piece_type, opponent_color, board, check_king_facing=False, check_check=False)

                # Nếu vị trí Tướng nằm trong danh sách nước đi, trả về thông tin quân cờ (piece_type, position, direction).
                if king_pos in moves:
                    direction = None

                    # Với Xe và Pháo, tính hướng di chuyển (direction) dựa trên vị trí Tướng và quân cờ.
                    if piece_type in [ROOK, CANNON]:
                        kr, kc = king_pos
                        pr, pc = row, col
                        if kr == pr:
                            direction = (0, 1 if pc < kc else -1)
                        elif kc == pc:
                            direction = (1 if pr < kr else -1, 0)
                    return {
                        'piece_type': piece_type,
                        'position': (row, col),
                        'direction': direction
                    }
    return None

def make_temp_move(board, move):
    """Thực hiện nước đi tạm thời để kiểm tra."""

    m_from, n_from, m_to, n_to = move
    temp_board = board.copy()                               # Sao chép board

    temp_board[m_to, n_to] = temp_board[m_from, n_from]
    temp_board[m_from, n_from] = EMPTY

    return temp_board   # Trả về bàn cờ tạm thời.

def get_valid_moves(row, col, piece_type, color_type, board, check_king_facing=True, check_check=True):
    """Tạo danh sách các nước đi hợp lệ cho quân cờ tại (row, col)."""

    valid_moves = []
    if piece_type not in [PAWN, ROOK, KNIGHT, CANNON, BISHOP, ELEPHANT, KING] or board[row, col] // 10 != color_type:
        return valid_moves

    # Sĩ (BISHOP): Di chuyển chéo trong cung (3x3). Kiểm tra ô đích phải trong cung và là ô trống hoặc là quân đối phương
    if piece_type == BISHOP:
        # # Xác định cung của Sĩ theo màu
        palace = [(9, 3), (9, 4), (9, 5), (8, 3), (8, 4), (8, 5), (7, 3), (7, 4), (7, 5)] if color_type == COLOR_LIGHT else [(0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)]
        
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:     # Các hướng chéo của Sĩ
            new_row, new_col = row + dr, col + dc

            # Nếu tọa độ trong cung và hợp lệ, thêm nước đi vào danh sách
            if (new_row, new_col) in palace and is_opponent_or_empty(new_row, new_col, color_type, board):
                valid_moves.append((new_row, new_col))
    
    # Tượng (ELEPHANT): Di chuyển chéo 2 ô, kiểm tra không vượt sông, ô giữa trống, và ô đích hợp lệ.
    if piece_type == ELEPHANT:
        max_row = 4 if color_type == COLOR_DARK else 9      # Giới hạn hàng tối đa (Đen: 4, Đỏ: 9)
        min_row = 0 if color_type == COLOR_DARK else 5      # Giới hạn hàng tối thiểu (Đen: 0, Đỏ: 5)
        
        for dr, dc in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            new_row, new_col = row + dr, col + dc
            leg_row, leg_col = row + dr // 2, col + dc // 2  # Tính tọa độ điểm cản (giữa đường đi)
            
            if (min_row <= new_row <= max_row and 0 <= new_col < COLS and         # Kiểm tra tọa độ hợp lệ
                is_opponent_or_empty(new_row, new_col, color_type, board) and     # Ô đích trống hoặc có quân đối phương
                
                0 <= leg_row < ROWS and 0 <= leg_col < COLS and         # Điểm cản trong bàn cờ
                board[leg_row, leg_col] == EMPTY):                      # Điểm cản trống
                valid_moves.append((new_row, new_col))
    
    # Tướng (KING): Di chuyển 1 ô trong cung, kiểm tra ô đích hợp lệ
    if piece_type == KING:
        palace = [(9, 3), (9, 4), (9, 5), (8, 3), (8, 4), (8, 5), (7, 3), (7, 4), (7, 5)] if color_type == COLOR_LIGHT else [(0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)]
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + dr, col + dc
            
            if (new_row, new_col) in palace and is_opponent_or_empty(new_row, new_col, color_type, board):
                valid_moves.append((new_row, new_col))

    # Xe (ROOK): Di chuyển ngang/dọc bất kỳ số ô, dừng khi gặp quân cờ
    if piece_type == ROOK:
        for dr, dc in offset[ROOK]:     # Duyệt qua các hướng của Xe
            step = 1                    # Bắt đầu từ bước 1
            while True:                 # Tiếp tục di chuyển theo hướng
                new_row = row + dr * step       # Tính hàng mới
                new_col = col + dc * step       # Tính cột mới
                
                if not (0 <= new_row < ROWS and 0 <= new_col < COLS):   # Nếu ngoài bàn cờ, thoát vòng lặp
                    break   
                 # Nếu ô đích hợp lệ, thêm nước đi vào danh sách
                if is_opponent_or_empty(new_row, new_col, color_type, board):
                    valid_moves.append((new_row, new_col))
                
                # Nếu ô đích có quân cờ, Dừng tại ô này (Xe không vượt qua quân cờ)
                if board[new_row, new_col] != EMPTY:
                    break
                step += 1    # Tăng bước để kiểm tra ô tiếp theo

    # Mã (KNIGHT): Di chuyển hình chữ L, kiểm tra chân Mã không bị cản
    if piece_type == KNIGHT:
        for dr, dc in offset[KNIGHT]:
            new_row = row + dr
            new_col = col + dc
            
            if not (0 <= new_row < ROWS and 0 <= new_col < COLS):   # Nếu ngoài bàn cờ, bỏ qua hướng này
                continue
            lr, lc = knight_legs.get((dr, dc), (0, 0))
            leg_row = row + lr
            leg_col = col + lc
            
            #  # Nếu điểm cản trống, ô đích hợp lệ => thêm nước đi vào danh sách
            if 0 <= leg_row < ROWS and 0 <= leg_col < COLS and board[leg_row, leg_col] == EMPTY:
                if is_opponent_or_empty(new_row, new_col, color_type, board):
                    valid_moves.append((new_row, new_col))

    # Pháo (CANNON): Di chuyển như Xe khi không ăn, nhảy qua 1 quân để ăn quân đối phương
    if piece_type == CANNON:
        for dr, dc in offset[CANNON]:
            jump = False        # Cờ báo đã nhảy qua quân cờ hay chưa
            step = 1
            while True:
                new_row = row + dr * step
                new_col = col + dc * step
                
                if not (0 <= new_row < ROWS and 0 <= new_col < COLS):
                    break       # Nếu ngoài bàn cờ => thoát vòng lặp
                
                # Nếu chưa nhảy qua quân cờ, ô đích trống => thêm vào ds
                if not jump:
                    if board[new_row, new_col] == EMPTY:
                        valid_moves.append((new_row, new_col))
                    else:       # Nếu gặp quân cờ
                        jump = True     # Bật cờ nhảy

                # Nếu đã nhảy qua quân cờ
                else:
                    # Nếu gặp quân thứ hai, nếu là quân đối phương=> thêm nước đi vào ds
                    if board[new_row, new_col] != EMPTY:
                        if is_opponent_or_empty(new_row, new_col, color_type, board):
                            valid_moves.append((new_row, new_col))
                        break   # dùng tại ô này
                step += 1

    # Tốt (PAWN): Di chuyển tiến 1 ô, hoặc ngang khi qua sông
    if piece_type == PAWN:
        moves = offset[PAWN][color_type].copy()
        if (color_type == COLOR_DARK and row >= 5) or (color_type == COLOR_LIGHT and row <= 4):
            moves.extend([(0, -1), (0, 1)])     # thêm đi ngang khi qua sông

        for dr, dc in moves:
            new_row = row + dr
            new_col = col + dc
            # Nếu tọa độ và ô dích hợp lệ => thêm nước đi vào ds
            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                if is_opponent_or_empty(new_row, new_col, color_type, board):
                    valid_moves.append((new_row, new_col))

    """ Lọc lại các nước đi hợp lệ """
    filtered_moves = []
    if check_king_facing or check_check:
        
        # Bước 1: Loại bỏ các nước đi dẫn đến Tướng đối mặt
        temp_moves = []
        for move in valid_moves:
            new_row, new_col = move
            temp_board = make_temp_move(board, (row, col, new_row, new_col))
            # Nếu check_king_facing=True, loại bỏ nước đi gây ra hai Tướng đối mặt (is_kings_facing)
            if not check_king_facing or not is_kings_facing(temp_board):
                temp_moves.append(move)

        # Bước 2: Kiểm tra xem Tướng có bị chiếu không
        if check_check:
            # Nếu Tướng đang bị chiếu, chỉ giữ nước đi chặn/ăn quân chiếu hoặc di chuyển Tướng để thoát chiếu.
            checking_piece = get_checking_piece(board, color_type)      # Lấy thông tin quân đang chiếu
            if checking_piece:
                checking_row, checking_col = checking_piece['position']
                checking_piece_type = checking_piece['piece_type']
                direction = checking_piece['direction']

                for move in temp_moves:
                    new_row, new_col = move
                    temp_board = make_temp_move(board, (row, col, new_row, new_col))
                    resolves_check = False      # Cờ báo nước đi có hóa giải thế chiếu hay không
                    
                    king_pos = None
                    for r in range(ROWS):
                        for c in range(COLS):
                            if temp_board[r, c] == color_type * 10 + KING:
                                king_pos = (r, c)    # Tìm vị trí Tướng trên bàn cờ tạm thời
                                break
                        if king_pos:
                            break
                    
                    # Xử lý hóa giải thế chiếu theo loại quân
                    # Nếu quân chiếu là Tốt    
                    if checking_piece_type == PAWN:
                        # Cách 1: Ăn Tốt
                        if (new_row, new_col) == (checking_row, checking_col):
                            resolves_check = True
                        # Cách 2: Chạy Tướng
                        elif piece_type == KING and not is_king_in_check(temp_board, color_type):
                            resolves_check = True

                    # Nếu quân chiếu là Xe        
                    elif checking_piece_type == ROOK:
                        # Cách 1: Ăn Xe
                        if (new_row, new_col) == (checking_row, checking_col):
                            resolves_check = True
                        # Cách 2: Chặn đường giữa Xe và Tướng
                        elif piece_type != KING and direction:
                            dr, dc = direction
                            min_row = min(checking_row, king_pos[0]) if dc == 0 else checking_row
                            max_row = max(checking_row, king_pos[0]) if dc == 0 else checking_row
                            min_col = min(checking_col, king_pos[1]) if dr == 0 else checking_col
                            max_col = max(checking_col, king_pos[1]) if dr == 0 else checking_col
                            if (dc == 0 and new_col == checking_col and min_row < new_row < max_row) or \
                               (dr == 0 and new_row == checking_row and min_col < new_col < max_col):
                                resolves_check = True
                        # Cách 3: Chạy Tướng      
                        elif piece_type == KING and not is_king_in_check(temp_board, color_type):
                            resolves_check = True

                    # Nếu quân chiếu là Pháo
                    elif checking_piece_type == CANNON:
                        # Cách 1: Ăn Pháo
                        if (new_row, new_col) == (checking_row, checking_col):
                            resolves_check = True

                        # Cách 2: Đưa quân vào giữa để có 2 quân cản
                        # Cách 3: Rút quân cản để Pháo mất bệ phóng
                        elif piece_type != KING and direction:
                            dr, dc = direction
                            min_row = min(checking_row, king_pos[0]) if dc == 0 else checking_row
                            max_row = max(checking_row, king_pos[0]) if dc == 0 else checking_row
                            min_col = min(checking_col, king_pos[1]) if dr == 0 else checking_col
                            max_col = max(checking_col, king_pos[1]) if dr == 0 else checking_col
                            # Đếm số quân cản hiện tại giữa Pháo và Tướng
                            jump_count = 0
                            if dc == 0: # dọc
                                for r in range(min_row + 1, max_row):
                                    if board[r, checking_col] != EMPTY:
                                        jump_count += 1
                            else:   # ngang
                                for c in range(min_col + 1, max_col):
                                    if board[checking_row, c] != EMPTY:
                                        jump_count += 1

                            # Thêm quân để có 2 quân cản            
                            if (dc == 0 and new_col == checking_col and min_row < new_row < max_row) or \
                               (dr == 0 and new_row == checking_row and min_col < new_col < max_col):
                                new_jump_count = sum(1 for r in range(min_row + 1, max_row) if temp_board[r, checking_col] != EMPTY) if dc == 0 else \
                                                sum(1 for c in range(min_col + 1, max_col) if temp_board[checking_row, c] != EMPTY)
                                if new_jump_count == 2:
                                    resolves_check = True

                            # Rút quân cản để có 0 quân cản
                            if jump_count == 1 and (row, col) != (new_row, new_col):
                                old_jump_count = sum(1 for r in range(min_row + 1, max_row) if board[r, checking_col] != EMPTY) if dc == 0 else \
                                                sum(1 for c in range(min_col + 1, max_col) if board[checking_row, c] != EMPTY)
                                new_jump_count = sum(1 for r in range(min_row + 1, max_row) if temp_board[r, checking_col] != EMPTY) if dc == 0 else \
                                                sum(1 for c in range(min_col + 1, max_col) if temp_board[checking_row, c] != EMPTY)
                                if old_jump_count == 1 and new_jump_count == 0:
                                    resolves_check = True
                       
                        # Cách 4: Chạy Tướng  
                        elif piece_type == KING and not is_king_in_check(temp_board, color_type):
                            resolves_check = True
                        
                    # Nếu quân chiếu là Mã
                    elif checking_piece_type == KNIGHT:
                        # Cách 1: Ăn Mã
                        if (new_row, new_col) == (checking_row, checking_col):  
                            resolves_check = True

                        # Cách 2: Chặn chân Mã
                        elif piece_type != KING:
                            for dr, dc in offset[KNIGHT]:
                                block_row = checking_row + dr // 2 if abs(dr) == 2 else checking_row
                                block_col = checking_col + dc // 2 if abs(dc) == 2 else checking_col
                                if (new_row, new_col) == (block_row, block_col):
                                    resolves_check = True  # Block leg
                                    break
                        # Cách 3: Chạy Tướng
                        elif piece_type == KING and not is_king_in_check(temp_board, color_type):  
                            resolves_check = True
                    
                    if resolves_check:                  # Thêm nước đi vào danh sách hợp lệ 
                        filtered_moves.append(move)
                        
            else:
                # Nếu không có quân chiếu, kiểm tra xem nước đi có dẫn đến Tướng bị chiếu không
                for move in temp_moves:         # Duyệt qua các nước đi tạm đã lưu được ở trên
                    new_row, new_col = move
                    temp_board = make_temp_move(board, (row, col, new_row, new_col))
                    # Kiểm tra nước đi tiếp theo có làm Tướng mình bị chiếu không
                    if not is_king_in_check(temp_board, color_type):
                        filtered_moves.append(move)
        else:
            filtered_moves = temp_moves
    else:
        filtered_moves = valid_moves
    return filtered_moves