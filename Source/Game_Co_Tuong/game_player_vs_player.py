import json
import numpy as np
from Khai_bao import *
from Ban_co import init_board, display_board
from game_XuLyInput import get_player_move
from game_KiemTraNuocDiHopLe import is_valid_move, reset_valid_moves_cache
from game_KiemTraKetThuc import is_game_over, get_winner
from game_ThucHienNuocDi_CapNhatLichSu import GameState, make_move, reset_move_history_file, print_move_history

def save_game_state(board, game_state):
    """
    Lưu trạng thái trò chơi vào tệp JSON.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        game_state (GameState): Đối tượng trạng thái trò chơi.
    """
    with open('game_state.json', 'w', encoding='utf-8') as f:
        json.dump({
            'board': board.tolist(),
            'current_player': game_state.current_player,
            'move_history': game_state.move_history,
            'time_tracker': game_state.time_tracker
        }, f, ensure_ascii=False, indent=2)

def game_player_vs_player():
    """
    Chế độ chơi Người vs Người.

    Notes:
        - Đỏ đi trước, Đen đi sau.
        - Người chơi nhập nước đi qua tọa độ (m_from, n_from, m_to, n_to).
        - Hiển thị bàn cờ và lịch sử nước đi sau mỗi lượt.
        - Hỗ trợ thoát và lưu trạng thái trò chơi.
    """
    game_state = GameState()        # Tạo game_state bằng GameState (từ game_ThucHienNuocDi_CapNhatLichSu.py)
    board = init_board()            # Khởi tạo bàn cờ bằng init_board (từ Ban_co.py), thiết lập trạng thái ban đầu của cờ tướng
    reset_move_history_file()       # Xóa lịch sử nước đi bằng reset_move_history_file.
    side = 2  # 2: Đỏ (đi trước), 1: Đen (đi sau)
    game_state.current_player = COLOR_LIGHT

    while True:
        display_board(board)        # Gọi display_board(board) để in ma trận bàn cờ (10x9).

        print(f"\nLượt của {'Đỏ' if side == 2 else 'Đen'}")
        # Gọi get_player_move(board, side) (từ game_XuLyInput.py) để lấy tọa độ (m_from, n_from, m_to, n_to).
        move_input = get_player_move(board, side)   
        
        if move_input == "exit":
            print("Lưu trạng thái trò chơi...")
            save_game_state(board, game_state)
            print("Đã thoát trò chơi!")
            break
        # Gọi is_valid_move(board, move_input, side) (từ game_KiemTraNuocDiHopLe.py) để kiểm tra nước đi hợp lệ theo luật cờ tướng.
        if is_valid_move(board, move_input, side):

            # Xác định màu quân (color_type = COLOR_LIGHT cho Đỏ, COLOR_DARK cho Đen)
            color_type = COLOR_LIGHT if side == 2 else COLOR_DARK

            # Thực hiện nước đi bằng make_move(board, move_input, color_type, game_state) (từ game_ThucHienNuocDi_CapNhatLichSu.py)
            board = make_move(board, move_input, color_type, game_state)

            # Xóa cache nước đi hợp lệ bằng reset_valid_moves_cache.
            reset_valid_moves_cache()

            # In lịch sử nước đi bằng print_move_history(game_state).
            print_move_history(game_state)

            # Chuyển lượt bằng side = 3 - side (2 → 1, 1 → 2) và cập nhật game_state.current_player.
            side = 3 - side  # Chuyển lượt: 2 -> 1, 1 -> 2
            game_state.current_player = COLOR_DARK if game_state.current_player == COLOR_LIGHT else COLOR_LIGHT
            

            # Kiểm tra kết thúc
            is_over, winner = is_game_over(board, game_state.current_player, game_state)
            if is_over:
                display_board(board)
                if winner == COLOR_DARK:
                    print("\nTrò chơi kết thúc! Người thắng: Đen")
                elif winner == COLOR_LIGHT:
                    print("\nTrò chơi kết thúc! Người thắng: Đỏ")
                else:
                    print("\nTrò chơi kết thúc! Kết quả: Hòa")
                save_game_state(board, game_state)
                break