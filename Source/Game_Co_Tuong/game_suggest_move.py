"""
1. Nhập liệu từ người dùng: Yêu cầu đường dẫn ảnh bàn cờ (banco.jpg) và màu quân (Đỏ hoặc Đen).
2. Nhận diện bàn cờ: Sử dụng recognize_chess_board từ board_recognition.py để tạo ma trận bàn cờ (10x9, số nguyên).
3. Hiển thị bàn cờ: In ma trận bàn cờ bằng display_board.
4. Khởi tạo trạng thái trò chơi: Sử dụng GameState để lưu thông tin người chơi hiện tại.
5. Tính nước đi tốt nhất: Gọi get_best_move từ ai_minimax.py để gợi ý nước đi.
6. Hiển thị kết quả: Chuyển đổi quân cờ thành tên tiếng Việt (Xe, Mã, Tướng, v.v.) và in nước đi gợi ý.

"""
import numpy as np
from ai_board_recognition import recognize_chess_board
from game_ThucHienNuocDi_CapNhatLichSu import GameState
from ai_minimax import get_best_move
from Ban_co import display_board
from Khai_bao import COLOR_LIGHT, COLOR_DARK, ROOK, KNIGHT, CANNON, KING, ELEPHANT, BISHOP, PAWN, EMPTY

def suggest_move():
    """
    Gợi ý nước đi từ ảnh bàn cờ.
    - Yêu cầu người dùng nhập đường dẫn ảnh.
    - Yêu cầu người dùng chọn màu quân (Đỏ hoặc Đen).
    - Nhận diện bàn cờ từ ảnh.
    - Gợi ý nước đi tốt nhất cho màu quân được chọn.
    """
    print("\nLựa chọn 6: Gợi ý nước đi")
    image_path = input("Nhập đường dẫn đến tệp ảnh bàn cờ (ví dụ: banco.jpg): ")
    
    # Yêu cầu người dùng chọn màu quân
    while True:
        color_choice = input("Bạn muốn gợi ý nước đi cho quân nào? Đỏ (r) hay Đen (b): ").lower()
        if color_choice in ['r', 'b']:
            break
        print("Lựa chọn không hợp lệ! Vui lòng nhập 'r' (Đỏ) hoặc 'b' (Đen).")
    
    player_color = COLOR_LIGHT if color_choice == 'r' else COLOR_DARK
    color_name = "Đỏ" if color_choice == 'r' else "Đen"
    
    try:
        # Nhận diện bàn cờ từ ảnh
        game_board, num_rows, num_cols = recognize_chess_board(image_path)  # Output của recognize_chess_board là 1 ma trận đã được xử lý
        print("\nMa trận bàn cờ nhận diện được:")
        display_board(game_board)
        
        # Khởi tạo trạng thái trò chơi
        game_state = GameState()  # Khởi tạo trạng thái trò chơi
        game_state.current_player = player_color  # Đặt người chơi hiện tại
        
        # Gợi ý nước đi
        print(f"\nĐang tìm nước đi tốt nhất cho {color_name}...")
        move = get_best_move(game_board, player_color, max_time=10.0, game_state=game_state)

        if move is None:
            print(f"Không tìm được nước đi hợp lệ cho {color_name}!")
        else:
            m_from, n_from, m_to, n_to = move
            piece = game_board[m_from, n_from]
            piece_char = {
                COLOR_LIGHT * 10 + ROOK: 'Xe', COLOR_LIGHT * 10 + KNIGHT: 'Mã',
                COLOR_LIGHT * 10 + CANNON: 'Pháo', COLOR_LIGHT * 10 + KING: 'Tướng',
                COLOR_LIGHT * 10 + BISHOP: 'Sĩ', COLOR_LIGHT * 10 + ELEPHANT: 'Tượng',
                COLOR_LIGHT * 10 + PAWN: 'Tốt',
                COLOR_DARK * 10 + ROOK: 'Xe', COLOR_DARK * 10 + KNIGHT: 'Mã',
                COLOR_DARK * 10 + CANNON: 'Pháo', COLOR_DARK * 10 + KING: 'Tướng',
                COLOR_DARK * 10 + BISHOP: 'Sĩ', COLOR_DARK * 10 + ELEPHANT: 'Tượng',
                COLOR_DARK * 10 + PAWN: 'Tốt'
            }.get(piece, 'Unknown')
            print(f"Nước đi gợi ý cho {color_name}: {piece_char} từ ({m_from}, {n_from}) đến ({m_to}, {n_to})")
    
    except Exception as e:
        print(f"Lỗi khi nhận diện hoặc gợi ý nước đi: {e}")