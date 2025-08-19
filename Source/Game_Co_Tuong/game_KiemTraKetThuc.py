from game_board_manager import dark_king_pos, light_king_pos
from Khai_bao import *
from Sinh_nuoc_di import get_valid_moves

def is_game_over(board, current_player, game_state):
    """
    Kiểm tra xem ván cờ đã kết thúc chưa.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        current_player (int): Người chơi hiện tại (COLOR_DARK hoặc COLOR_LIGHT).
        game_state (GameState): Đối tượng trạng thái trò chơi.

    Returns:
        tuple: (is_over, winner)
            - is_over (bool): True nếu ván cờ kết thúc.
            - winner (int or None): COLOR_DARK, COLOR_LIGHT nếu có người thắng, hoặc None nếu hòa.
    """
    # Kiểm tra Tướng
    if dark_king_pos is None:
        return True, COLOR_LIGHT
    if light_king_pos is None:
        return True, COLOR_DARK

    # Kiểm tra không có nước đi hợp lệ
    has_valid_move = False
    color_type = current_player
    for row in range(ROWS):
        for col in range(COLS):
            if board[row, col] != EMPTY and board[row, col] // 10 == color_type:
                piece_type = board[row, col] % 10
                if get_valid_moves(row, col, piece_type, color_type, board, check_king_facing=True, check_check=True):
                    has_valid_move = True
                    break
        if has_valid_move:
            break
    if not has_valid_move:
        print("Trò chơi kết thúc! Kết quả: Hòa (không còn nước đi hợp lệ)")
        return True, None

    return False, None

def get_winner(board, game_state):
    """
    Xác định người thắng dựa trên trạng thái bàn cờ.

    Args:
        board (np.ndarray): Mảng NumPy biểu diễn bàn cờ (10x9).
        game_state (GameState): Đối tượng trạng thái trò chơi.

    Returns:
        int or None: COLOR_DARK, COLOR_LIGHT nếu có người thắng, hoặc None nếu hòa.
    """
    is_over, winner = is_game_over(board, game_state.current_player, game_state)
    return winner if is_over else None