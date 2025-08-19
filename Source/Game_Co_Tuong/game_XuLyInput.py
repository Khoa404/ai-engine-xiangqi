import re
from Khai_bao import *
from Ban_co import get_piece_char
from game_KiemTraNuocDiHopLe import is_valid_move
from Sinh_nuoc_di import get_valid_moves

def parse_move_input(input_str):
    """
    Phân tích chuỗi đầu vào thành tọa độ nước đi.

    Returns:
        tuple or str: Tọa độ (m_from, n_from, m_to, n_to) nếu hợp lệ, hoặc "exit" nếu người dùng muốn thoát.

    """
    if input_str.lower() == "exit":
        return "exit"
    
    # Kiểm tra định dạng tọa độ: "m_from,n_from,m_to,n_to"
    pattern = r'^\d+ \d+ \d+ \d+$'
    if not re.match(pattern, input_str):
        raise ValueError("Định dạng không hợp lệ! Vui lòng nhập theo dạng: m_from n_from m_to n_to (ví dụ: 3 2 4 2)")
    
    try:
        m_from, n_from, m_to, n_to = map(int, input_str.split(' '))
        return (m_from, n_from, m_to, n_to)
    except ValueError:
        raise ValueError("Tọa độ phải là số nguyên! Vui lòng nhập lại.")

def print_all_valid_moves(board, side):
    """
    Hiển thị tất cả nước đi hợp lệ cho các quân cờ của một bên.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        side (int): Bên chơi (1 cho Đen, 2 cho Đỏ).
    """
    color_type = COLOR_DARK if side == 1 else COLOR_LIGHT
    print(f"\nDanh sách nước đi hợp lệ cho {'Đen' if side == 1 else 'Đỏ'}:")
    for row in range(ROWS):
        for col in range(COLS):

            if board[row, col] != EMPTY and board[row, col] // 10 == color_type:
                piece_type = board[row, col] % 10
                valid_moves = get_valid_moves(row, col, piece_type, color_type, board, check_king_facing=True, check_check=True)
                if valid_moves:
                    piece_char = get_piece_char(board[row, col])
                    print(f"{piece_char} tại ({row}, {col}): {valid_moves}")

def get_player_move(board, side):
    """
    Lấy nước đi từ người chơi thông qua đầu vào bàn phím.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        side (int): Bên chơi (1 cho Đen, 2 cho Đỏ).
        
    Notes:
        - Kiểm tra định dạng đầu vào và tính hợp lệ của nước đi.
        - Hiển thị danh sách nước đi hợp lệ cho quân cờ được chọn nếu nhập sai.
        - Hỗ trợ in tất cả nước đi hợp lệ nếu người dùng nhập 'all'.
    """
    color_type = COLOR_DARK if side == 1 else COLOR_LIGHT
    while True:
        try:
            input_str = input(f"Nhập nước đi cho {'Đen' if side == 1 else 'Đỏ'} (m_from,n_from,m_to,n_to, 'all' để xem nước đi hợp lệ, hoặc 'exit' để thoát): ")
            
            if input_str.lower() == "all":
                print_all_valid_moves(board, side)
                continue
            
            move = parse_move_input(input_str)
            
            if move == "exit":
                return "exit"
            
            m_from, n_from, m_to, n_to = move
            # Kiểm tra sơ bộ tọa độ có nằm trong bàn cờ không
            if not (0 <= m_from < ROWS and 0 <= n_from < COLS and 0 <= m_to < ROWS and 0 <= n_to < COLS):
                print(f"Lỗi: Tọa độ ({m_from}, {n_from}) hoặc ({m_to}, {n_to}) ngoài bàn cờ!")
                continue
            
            # Kiểm tra có quân cờ tại vị trí bắt đầu
            if board[m_from, n_from] == EMPTY:
                print(f"Lỗi: Không có quân cờ tại vị trí ({m_from}, {n_from})!")
                continue
            
            # Kiểm tra quân cờ thuộc về người chơi
            if board[m_from, n_from] // 10 != color_type:
                print(f"Lỗi: Quân cờ tại ({m_from}, {n_from}) không thuộc về {'Đen' if color_type == COLOR_DARK else 'Đỏ'}!")
                continue
            
            # Kiểm tra tính hợp lệ của nước đi
            if is_valid_move(board, move, side):
                return move
            # Thông báo lỗi và danh sách nước đi hợp lệ đã được in trong is_valid_move
            
        except ValueError as e:
            print(f"Lỗi: {str(e)}")
        except Exception as e:
            print(f"Lỗi không xác định: {str(e)}. Vui lòng nhập lại.")