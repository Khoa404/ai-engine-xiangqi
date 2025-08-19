# Cây Thư Mục Dự Án Cờ Tướng

## Cấu trúc thư mục
```
\Game_Co_Tuong

├── _main.py/ _mains.ipynb       # Chương trình chính để chạy các chế độ chơi
├── Khai_bao.py                  # Định nghĩa hằng số và cấu trúc dữ liệu
├── Ban_co.py                    # Quản lý bàn cờ (khởi tạo, hiển thị) 
├── Sinh_nuoc_di.py              # Sinh nước đi hợp lệ

├── game_board_manager.py        # Quản lý vị trí Tướng và bàn cờ
├── game_XuLyInput.py            # Xử lý đầu vào của người chơi
├── game_KiemTraNuocDiHopLe.py   # Kiểm tra tính hợp lệ của nước đi
├── game_KiemTraKetThuc.py       # Kiểm tra điều kiện kết thúc trò chơi
├── game_ThucHienNuocDi_CapNhatLichSu.py      # Thực hiện nước đi và lưu lịch sử
├── game_player_vs_player.py     # Chế độ chơi Người vs Người
├── game_player_vs_ai.py         # Chế độ chơi Người vs Máy
├── game_suggest_move.py         # Gợi ý nước đi cho người chơi
├── game_replay.py               # Phát lại ván cờ từ lịch sử

├── ai_minimax.py                # Thuật toán Minimax cho AI
├── ai_Ham_danh_gia.py           # Hàm đánh giá bàn cờ cho AI
├── ai_board_recognition.py      # Thuật toán nhận diện quân cờ và chuyển thành ma trận

├── best.pt                      # File trọng số của mô hình YOLOv8s nhận diện quân cờ
├── game_state.json              # Lưu trạng thái trò chơi
├── move_history.json            # Lưu lịch sử nước đi
└── 
```

## Mô tả chi tiết các file

### 1. _main.py / _mains.ipynb
- **Chức năng**: Chương trình chính để chạy trò chơi, cung cấp giao diện chọn chế độ:
  - 1: Chơi với máy (gọi `game_player_vs_ai.py`).
  - 2: Chơi Người vs Người (gọi `game_player_vs_player.py`).
  - 3: Gợi ý nước đi (gọi `game_suggest_move.py`).
  - 4: Xem lại ván cờ (gọi `game_replay.py`).
- **Liên kết**: Nhập điểm xuất phát và đích của quân cờ, hiển thị bàn cờ, và gọi các hàm từ các file khác.

### 2. Khai_bao.py
- **Chức năng**: Định nghĩa các hằng số và cấu trúc dữ liệu:
  - `COLOR_DARK` (1): Quân Đen.
  - `COLOR_LIGHT` (2): Quân Đỏ.
  - `EMPTY` (0): Ô trống.
  - `KING`, `BISHOP`, `ELEPHANT`, `ROOK`, `KNIGHT`, `CANNON`, `PAWN`: Loại quân cờ.
  - `ROWS` (10), `COLS` (9): Kích thước bàn cờ.
  - `offset`: Danh sách hướng di chuyển của các quân cờ (Xe, Mã, Pháo, Tốt).
  - `knight_legs`: Hướng chân Mã bị cản.
  - `MAX_TABLE_SIZE` (200000): Kích thước bảng lưu trữ cho `ai_minimax.py`.
- **Liên kết**: Được nhập bởi hầu hết các file khác để sử dụng hằng số.

### 3. Ban_co.py
- **Chức năng**:
  - `init_board()`: Khởi tạo bàn cờ 10x9 với vị trí ban đầu của các quân cờ.
  - `display_board()`: Hiển thị bàn cờ dưới dạng ma trận hoặc giao diện đồ họa.
  - `get_piece_char()`: Chuyển giá trị quân cờ thành ký tự (ví dụ: Xe, Mã, Tốt).
- **Liên kết**: Được dùng trong `game_player_vs_player.py`, `game_replay.py`, và các file khác để hiển thị trạng thái bàn cờ.

### 4. game_board_manager.py
- **Chức năng**:
  - `update_king_pos(board, move)`: Cập nhật vị trí Tướng sau mỗi nước đi.
- **Liên kết**: Được gọi trong `game_ThucHienNuocDi_CapNhatLichSu.py` để theo dõi vị trí Tướng.

### 5. game_XuLyInput.py
- **Chức năng**:
  - `get_player_move(board, side)`: Nhận đầu vào từ người chơi (tọa độ nước đi: `m_from, n_from, m_to, n_to`) hoặc lệnh `exit`/`all`.
- **Liên kết**: Được dùng trong `game_player_vs_player.py` và `game_player_vs_ai.py` để xử lý nước đi của người chơi.

### 6. game_KiemTraNuocDiHopLe.py
- **Chức năng**:
  - `is_opponent_or_empty(r, c, color_type, board)`: Kiểm tra ô trống hoặc chứa quân đối phương.
  - `is_kings_facing(board)`: Kiểm tra hai Tướng có đối mặt nhau không.
  - `is_king_in_check(board, color_type)`: Kiểm tra Tướng có bị chiếu không.
  - `get_checking_piece(board, color_type)`: Xác định quân cờ đang chiếu Tướng.
  - `make_temp_move(board, move)`: Thực hiện nước đi tạm thời để kiểm tra.
  - `get_valid_moves(row, col, piece_type, color_type, board)`: Tạo danh sách nước đi hợp lệ.
- **Liên kết**: Được dùng trong `game_player_vs_player.py`, `game_player_vs_ai.py`, và `ai_minimax.py` để đảm bảo nước đi hợp lệ.

### 7. game_KiemTraKetThuc.py
- **Chức năng**:
  - `is_game_over(board, current_player, game_state)`: Kiểm tra trò chơi kết thúc (Tướng bị bắt, hòa, v.v.).
  - `get_winner(board, game_state)`: Xác định người thắng (Đen, Đỏ, hoặc Hòa).
- **Liên kết**: Được dùng trong `game_player_vs_player.py` và `game_player_vs_ai.py` để kiểm tra điều kiện kết thúc.

### 8. game_ThucHienNuocDi_CapNhatLichSu.py
- **Chức năng**:
  - `GameState`: Lớp lưu trạng thái trò chơi (`current_player`, `move_history`, `time_tracker`, `king_positions`).
  - `save_move_history_to_file(move_history)`: Lưu lịch sử nước đi vào `move_history.json`.
  - `reset_move_history_file()`: Xóa lịch sử nước đi.
  - `print_move_history(game_state)`: In lịch sử nước đi.
  - `make_move(board, move, color_type, game_state)`: Thực hiện nước đi và cập nhật trạng thái.
- **Liên kết**: Được dùng trong `game_player_vs_player.py`, `game_player_vs_ai.py`, `game_suggest_move.py`, và `game_replay.py`.

### 9. game_player_vs_player.py
- **Chức năng**:
  - `save_game_state(board, game_state)`: Lưu trạng thái trò chơi vào `game_state.json`.
  - `game_player_vs_player()`: Chế độ chơi Người vs Người, luân phiên nhập nước đi cho Đỏ và Đen.
- **Liên kết**: Được gọi từ `main.ipynb` (option 2).

### 10. game_player_vs_ai.py
- **Chức năng**:
  - Chế độ chơi Người vs Máy, người chơi nhập nước đi, máy sử dụng `ai_minimax.py` để tính nước đi.
- **Liên kết**: Được gọi từ `main.ipynb` (option 1), sử dụng `get_best_move` từ `ai_minimax.py`.

### 11. game_suggest_move.py

- **Chức năng**: Gợi ý nước đi tối ưu cho người chơi bằng `get_best_move` từ `ai_minimax.py`.
- **Liên kết**: Được gọi từ `main.ipynb` (option 3), liên quan đến `ai_minimax.py` và `ai_Ham_danh_gia.py`.

### 12. game_replay.py
- **Chức năng**:
  - `replay_game()`: Phát lại ván cờ từ `move_history.json`, hiển thị từng nước đi với độ trễ 1 giây.
- **Liên kết**: Được gọi từ `main.ipynb` (option 4), sử dụng `move_history.json` từ `game_ThucHienNuocDi_CapNhatLichSu.py`.

### 13. ai_minimax.py
- **Chức năng**:
  - `get_best_move(board, color_type, max_time, game_state)`: Tìm nước đi tốt nhất bằng thuật toán Minimax với cắt tỉa Alpha-Beta.
  - Sử dụng bảng lưu trữ (`transposition_table`) và một vài phương pháp tăng cường khác.
- **Liên kết**: Được dùng trong `game_player_vs_ai.py` và `game_suggest_move.py`.

### 14. ai_Ham_danh_gia.py

- **Chức năng**: `evaluate_board(board, color_type)`: Đánh giá bàn cờ 
- **Liên kết**: Được dùng trong `ai_minimax.py` để chấm điểm các trạng thái bàn cờ.

### 15. game_state.json
- **Chức năng**: Lưu trạng thái trò chơi (bàn cờ, người chơi hiện tại, lịch sử nước đi, thời gian) từ `save_game_state` trong `game_player_vs_player.py`.
- **Liên kết**: Dùng để xem lại ván cờ sau khi thoát.

### 16. move_history.json
- **Chức năng**: Lưu lịch sử nước đi (chuỗi mô tả, màu quân, thời gian) từ `save_move_history_to_file`.
- **Liên kết**: Được dùng trong `game_replay.py` để phát lại ván cờ.


## Tóm tắt chức năng và liên kết
- **Chạy trò chơi**: `main.ipynb` là điểm vào, gọi các chế độ chơi (`game_player_vs_player.py`, `game_player_vs_ai.py`, `game_suggest_move.py`, `game_replay.py`).
- **Quản lý bàn cờ**: `Ban_co.py` (khởi tạo, hiển thị), `game_board_manager.py` (cập nhật vị trí Tướng).
- **Kiểm tra nước đi**: `game_KiemTraNuocDiHopLe.py` (đảm bảo hợp lệ), `game_KiemTraKetThuc.py` (kiểm tra kết thúc).
- **Thực hiện nước đi**: `game_ThucHienNuocDi_CapNhatLichSu.py` (cập nhật bàn cờ, lịch sử).
- **AI và gợi ý**: `ai_minimax.py` (tìm nước đi tốt nhất), `ai_Ham_danh_gia.py` (đánh giá bàn cờ), `ai_board_recognition.py` (nhận diện quân cờ).
- **Lưu trữ và phát lại**: `game_state.json` (trạng thái), `move_history.json` (lịch sử), `game_replay.py` (phát lại).
