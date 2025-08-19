import json
import numpy as np
import time
from Khai_bao import *
from Ban_co import init_board, display_board
from game_XuLyInput import get_player_move
from game_KiemTraNuocDiHopLe import is_valid_move, reset_valid_moves_cache
from game_KiemTraKetThuc import is_game_over, get_winner
from game_ThucHienNuocDi_CapNhatLichSu import GameState, make_move, reset_move_history_file, print_move_history
from ai_minimax import get_best_move

def save_game_state(board, game_state):
    """
    Lưu trạng thái trò chơi vào tệp JSON.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        game_state (GameState): Đối tượng trạng thái trò chơi.
    """
    with open('game_state.json', 'w', encoding='utf-8') as f:   # Mở file game_state.json ở chế độ ghi ('w'), sử dụng encoding utf-8.
        json.dump({
            'board': board.tolist(),              # Chuyển ma trận bàn cờ (board, NumPy array) thành danh sách Python bằng board.tolist()
            'current_player': game_state.current_player,    # Người chơi hiện tại (COLOR_LIGHT hoặc COLOR_DARK).
            'move_history': game_state.move_history,        # Lịch sử nước đi (từ game_state).
            'time_tracker': game_state.time_tracker         # Thời gian theo dõi (từ game_state).

         # Sử dụng json.dump với ensure_ascii=False để hỗ trợ ký tự tiếng Việt, và indent=2 để định dạng JSON dễ đọc.
        }, f, ensure_ascii=False, indent=2)


def game_player_vs_ai():
    """
    Chế độ chơi Người vs Máy, với người chơi là Đỏ (đi trước) và máy là Đen (đi sau).

    Notes:
        - Người chơi nhập nước đi qua tọa độ (m_from, n_from, m_to, n_to).
        - Máy sử dụng thuật toán Minimax để chọn nước đi.
        - Hỗ trợ thoát và lưu trạng thái trò chơi.
    """
    # Tạo game_state bằng GameState (từ game_ThucHienNuocDi_CapNhatLichSu.py)
    game_state = GameState()
    # Khởi tạo bàn cờ bằng init_board (từ Ban_co.py)
    board = init_board()
    # Xóa lịch sử nước đi bằng reset_move_history_file.
    reset_move_history_file()

    side = 2    # 2: Đỏ (người, đi trước), 1: Đen (máy, đi sau)
    game_state.current_player = COLOR_LIGHT
    ai_color = COLOR_DARK

    while True:
        display_board(board)        # Gọi display_board(board) để in ma trận bàn cờ
        
        if side == 2:  # Lượt của người chơi (Đỏ)
            print("\nLượt của Đỏ (người chơi)")
            move_input = get_player_move(board, side)   # Nhập nước đi bằng get_player_move(board, side) (từ game_XuLyInput.py).
            
            if move_input == "exit":                    # Nếu nhập exit, lưu trạng thái bằng save_game_state: lưu và thoát
                print("Lưu trạng thái trò chơi...")
                save_game_state(board, game_state)
                print("Đã thoát trò chơi!")
                break
            
            if is_valid_move(board, move_input, side):      # Kiểm tra nước đi hợp lệ bằng is_valid_move (từ game_KiemTraNuocDiHopLe.py)
                board = make_move(board, move_input, COLOR_LIGHT, game_state)   # Nếu hợp lệ, thực hiện nước đi bằng make_move
                reset_valid_moves_cache()           # xóa cache nước đi hợp lệ
                print_move_history(game_state)      # in lịch sử nước đi
                side = 1                            # chuyển lượt
                game_state.current_player = COLOR_DARK
        
        else:  # Lượt của máy (Đen)
            print("\nMáy (Đen) đang suy nghĩ...")
            start_time = time.time()

            # Gọi get_best_move (từ ai_minimax.py) với max_time=10s
            move = get_best_move(board, ai_color, max_time=10.0, game_state=game_state)
            if move is None:
                print("Máy không tìm được nước đi hợp lệ!")
                break
            m_from, n_from, m_to, n_to = move

            # In nước đi và thời gian suy nghĩ.
            print(f"Máy di chuyển: ({m_from}, {n_from}) đến ({m_to}, {n_to})")
            print(f"Thời gian suy nghĩ: {time.time() - start_time:.2f}s")
            
            # Kiểm tra nước đi hợp lệ, thực hiện nước đi, cập nhật lịch sử, và chuyển lượt
            if is_valid_move(board, move, side):
                board = make_move(board, move, ai_color, game_state)
                reset_valid_moves_cache()
                print_move_history(game_state)
                side = 2
                game_state.current_player = COLOR_LIGHT
            else:
                print("Lỗi: Nước đi của máy không hợp lệ!")
                break
        
        # Kết thúc trò chơi
        is_over, winner = is_game_over(board, game_state.current_player, game_state)
        if is_over:
            display_board(board)
            if winner == COLOR_DARK:
                print("\nTrò chơi kết thúc! Người thắng: Đen (máy)")
            elif winner == COLOR_LIGHT:
                print("\nTrò chơi kết thúc! Người thắng: Đỏ (người chơi)")
            else:
                print("\nTrò chơi kết thúc! Kết quả: Hòa")
            save_game_state(board, game_state)
            break