import numpy as np
from game_player_vs_player import game_player_vs_player
from game_player_vs_ai import game_player_vs_ai
from game_ai_vs_ai import game_ai_vs_ai
from game_replay import replay_game
from game_suggest_move import suggest_move

def main():
    """
    Hàm chính để chạy trò chơi cờ tướng.
    """
    while True:
        # Hiển thị menu chính
        print("\n=== Trò Chơi Cờ Tướng ===")
        print("1. Người vs Người")
        print("2. Người vs Máy (Người chơi Đỏ, Máy chơi Đen)")
        print("3. Máy vs Máy")
        print("4. Phát lại ván cờ")
        print("5. Thoát")
        print("6. Gợi ý nước đi")
        print("==========================")
        
        choice = input("Nhập lựa chọn của bạn (1-6): ")
        
        if choice == '1':
            print("\nBắt đầu chế độ Người vs Người...")
            game_player_vs_player()
        elif choice == '2':
            print("\nBắt đầu chế độ Người vs Máy...")
            game_player_vs_ai()
        elif choice == '3':
            print("\nBắt đầu chế độ Máy vs Máy...")
            game_ai_vs_ai()
        elif choice == '4':
            print("\nBắt đầu chế độ Phát lại ván cờ...")
            replay_game()
        elif choice == '5':
            print("\nThoát trò chơi!")
            break
        elif choice == '6':
            suggest_move()
        else:
            print("\nLựa chọn không hợp lệ! Vui lòng chọn từ 1 đến 6.")

if __name__ == "__main__":
    main()