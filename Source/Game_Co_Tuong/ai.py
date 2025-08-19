from ai_Ham_danh_gia import evaluate_board
from ai_minimax import minimax, get_best_move

"""
Module trung gian để tái xuất các hàm liên quan đến AI cờ tướng.
Bao gồm hàm đánh giá bàn cờ và thuật toán Minimax để tìm nước đi tối ưu.

"""

# Re-export các hàm để các file khác có thể nhập từ ai.py
__all__ = ['evaluate_board', 'minimax', 'get_best_move']