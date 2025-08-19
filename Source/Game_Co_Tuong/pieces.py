from Khai_bao import *

def get_piece_value(piece_type):
    """Trả về giá trị của quân cờ."""
    return PIECE_VALUES.get(piece_type, 0)  # Lấy giá trị của quân cờ từ từ điển PIECE_VALUES, trả về 0 nếu piece_type không tồn tại


def get_position_score(piece_type, row, col, color):
    """Trả về điểm số vị trí cho quân cờ tại (row, col)."""

    if color == COLOR_LIGHT:    # Kiểm tra nếu quân cờ thuộc phe Đỏ (COLOR_LIGHT)
        row = ROWS - 1 - row    # Đảo hàng (row) để điều chỉnh vị trí cho phe Đỏ, vì bàn cờ đối xứng theo chiều dọc

    if piece_type == PAWN:                      # Nếu quân cờ là Tốt (PAWN)
        return PAWN_POSITION_TABLE[row, col]    # Trả về điểm số vị trí từ bảng PAWN_POSITION_TABLE
    
    elif piece_type == KNIGHT:                      # Nếu quân cờ là Mã (KNIGHT)
        return KNIGHT_POSITION_TABLE[row, col]      # Trả về điểm số vị trí từ bảng KNIGHT_POSITION_TABLE
    
    elif piece_type in [ROOK, CANNON]:                  # Nếu quân cờ là Xe (ROOK) hoặc Pháo (CANNON)
        return ROOK_CANNON_POSITION_TABLE[row, col]     # Trả về điểm số vị trí từ bảng ROOK_CANNON_POSITION_TABLE
    
    elif piece_type in [BISHOP, ELEPHANT]:                  # Nếu quân cờ là Sĩ (BISHOP) hoặc Tượng (ELEPHANT)
        return BISHOP_ELEPHANT_POSITION_TABLE[row, col]     # Trả về điểm số vị trí từ bảng BISHOP_ELEPHANT_POSITION_TABLE
    
    elif piece_type == KING:                    # Nếu quân cờ là Tướng (KING)
        return KING_POSITION_TABLE[row, col]    # Trả về điểm số vị trí từ bảng KING_POSITION_TABLE
    
    return 0     # Trả về 0 nếu piece_type không khớp với bất kỳ loại quân cờ nào