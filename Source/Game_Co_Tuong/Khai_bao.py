import numpy as np

# Hằng số định nghĩa loại quân cờ và màu
EMPTY = 0       # Ô trống trên bàn cờ
PAWN = 1        # Quân Tốt
BISHOP = 2      # Quân Sĩ
ELEPHANT = 3    # Quân Tượng
KNIGHT = 4      # Quân Mã
CANNON = 5      # Quân Pháo
ROOK = 6        # Quân Xe
KING = 7        # Quân Tướng

COLOR_DARK = 1      # Màu Đen
COLOR_LIGHT = 2     # Màu Đỏ

ROWS = 10       # Số hàng của bàn cờ (tọa độ hàng từ 0 đến 9)
COLS = 9        # Số cột của bàn cờ (tọa độ cột từ 0 đến 8)

MAILBOX_ROWS = 14  # Số hàng của bàn cờ mở rộng (mailbox)
MAILBOX_COLS = 13  # Số cột của bàn cờ mở rộng (mailbox)

# Giá trị của quân cờ
PIECE_VALUES = {
    PAWN: 100,      # Tốt: 100 điểm
    BISHOP: 200,    # Sĩ: 200 điểm
    ELEPHANT: 200,  # Tượng: 200 điểm
    KNIGHT: 400,    # Mã: 400 điểm
    CANNON: 450,    # Pháo: 450 điểm
    ROOK: 900,      # Xe: 900 điểm
    KING: 10000     # Tướng: 10000 điểm
}

# Tốt
# Điểm cao hơn ở các hàng xa hơn (Tốt tiến lên, đặc biệt sau khi qua sông)
PAWN_POSITION_TABLE = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [10, 10, 10, 10, 10, 10, 10, 10, 10],
    [20, 20, 20, 20, 20, 20, 20, 20, 20],
    [50, 50, 50, 50, 50, 50, 50, 50, 50],
    [60, 60, 60, 60, 60, 60, 60, 60, 60],
    [70, 70, 70, 70, 70, 70, 70, 70, 70],
    [80, 80, 80, 80, 80, 80, 80, 80, 80],
    [90, 90, 90, 90, 90, 90, 90, 90, 90]
])

# Mã
# Điểm cao hơn ở trung tâm và các vị trí linh hoạt (hàng 3-6, cột 2-6)
KNIGHT_POSITION_TABLE = np.array([
    [10, 10, 10, 10, 10, 10, 10, 10, 10],
    [15, 20, 20, 20, 20, 20, 20, 20, 15],
    [20, 25, 30, 30, 30, 30, 30, 25, 20],
    [20, 30, 35, 40, 40, 40, 35, 30, 20],
    [20, 30, 40, 50, 50, 50, 40, 30, 20],
    [20, 30, 40, 50, 50, 50, 40, 30, 20],
    [20, 30, 35, 40, 40, 40, 35, 30, 20],
    [20, 25, 30, 30, 30, 30, 30, 25, 20],
    [15, 20, 20, 20, 20, 20, 20, 20, 15],
    [10, 10, 10, 10, 10, 10, 10, 10, 10]
])

# Xe và Pháo
# Điểm cao hơn ở các hàng biên (0 và 9) và giảm dần về trung tâm
ROOK_CANNON_POSITION_TABLE = np.array([
    [50, 50, 50, 50, 50, 50, 50, 50, 50],
    [40, 40, 40, 40, 40, 40, 40, 40, 40],
    [30, 30, 30, 30, 30, 30, 30, 30, 30],
    [20, 20, 20, 20, 20, 20, 20, 20, 20],
    [10, 10, 10, 10, 10, 10, 10, 10, 10],
    [10, 10, 10, 10, 10, 10, 10, 10, 10],
    [20, 20, 20, 20, 20, 20, 20, 20, 20],
    [30, 30, 30, 30, 30, 30, 30, 30, 30],
    [40, 40, 40, 40, 40, 40, 40, 40, 40],
    [50, 50, 50, 50, 50, 50, 50, 50, 50]
])

# Sĩ và Tượng
# Điểm cao hơn ở các vị trí trong cung (cột 3-5, hàng 0-2 hoặc 7-9)
BISHOP_ELEPHANT_POSITION_TABLE = np.array([
    [20, 20, 20, 50, 50, 50, 20, 20, 20],
    [20, 20, 20, 50, 50, 50, 20, 20, 20],
    [20, 20, 20, 50, 50, 50, 20, 20, 20],
    [10, 10, 10, 10, 10, 10, 10, 10, 10],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [10, 10, 10, 10, 10, 10, 10, 10, 10],
    [20, 20, 20, 50, 50, 50, 20, 20, 20],
    [20, 20, 20, 50, 50, 50, 20, 20, 20],
    [20, 20, 20, 50, 50, 50, 20, 20, 20]
])

# Tướng
# Điểm cao hơn ở trung tâm cung (cột 4, hàng 0-2 hoặc 7-9)
KING_POSITION_TABLE = np.array([
    [20, 20, 20, 50, 70, 50, 20, 20, 20],
    [20, 20, 20, 50, 70, 50, 20, 20, 20],
    [20, 20, 20, 50, 70, 50, 20, 20, 20],
    [10, 10, 10, 10, 10, 10, 10, 10, 10],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [10, 10, 10, 10, 10, 10, 10, 10, 10],
    [20, 20, 20, 50, 70, 50, 20, 20, 20],
    [20, 20, 20, 50, 70, 50, 20, 20, 20],
    [20, 20, 20, 50, 70, 50, 20, 20, 20]
])

# Mảng ánh xạ từ bàn cờ 10x9 sang bàn cờ mở rộng 14x13
mailbox90 = [
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, -1, -1,
    -1, -1, 9, 10, 11, 12, 13, 14, 15, 16, 17, -1, -1,
    -1, -1, 18, 19, 20, 21, 22, 23, 24, 25, 26, -1, -1,
    -1, -1, 27, 28, 29, 30, 31, 32, 33, 34, 35, -1, -1,
    -1, -1, 36, 37, 38, 39, 40, 41, 42, 43, 44, -1, -1,
    -1, -1, 45, 46, 47, 48, 49, 50, 51, 52, 53, -1, -1,
    -1, -1, 54, 55, 56, 57, 58, 59, 60, 61, 62, -1, -1,
    -1, -1, 63, 64, 65, 66, 67, 68, 69, 70, 71, -1, -1,
    -1, -1, 72, 73, 74, 75, 76, 77, 78, 79, 80, -1, -1,
    -1, -1, 81, 82, 83, 84, 85, 86, 87, 88, 89, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1
]

# Mảng ánh xạ từ bàn cờ mở rộng 14x13 về bàn cờ 10x9
mailbox182 = [-1] * (MAILBOX_ROWS * MAILBOX_COLS)
for i in range(90):
    if mailbox90[i + 28] != -1:
        mailbox182[mailbox90[i + 28]] = i

# Mảng offset cho các hướng di chuyển của từng loại quân
offset = {
    ROOK: [(-1, 0), (1, 0), (0, -1), (0, 1)],
    KNIGHT: [(-2, 1), (-2, -1), (2, 1), (2, -1), (-1, 2), (-1, -2), (1, 2), (1, -2)],
    CANNON: [(-1, 0), (1, 0), (0, -1), (0, 1)],
    PAWN: {COLOR_DARK: [(1, 0)], COLOR_LIGHT: [(-1, 0)]}
}

# Mảng offset cho vị trí "chân" của Mã (điểm cản)
knight_legs = {
    (-2, 1): (-1, 0), (-2, -1): (-1, 0), (2, 1): (1, 0), (2, -1): (1, 0),
    (-1, 2): (0, 1), (-1, -2): (0, -1), (1, 2): (0, 1), (1, -2): (0, -1)
}

# Trọng số theo giai đoạn trận đấu

#- opening: Ưu tiên di động và kiểm soát trung tâm
#- middlegame: Cân bằng giữa vật chất, tấn công, và phòng thủ
#- endgame: Tăng trọng số vật chất và an toàn Tướng

WEIGHTS = {
    'opening': {
        'material': 0.8, 'position': 0.6, 'mobility': 2.5, 'king_safety': 1.0,
        'check': 1.5, 'center_control': 1.5, 'pawn_structure': 0.8, 'attack_defense': 1.0,
        'cannon_control': 1.2, 'king_threat': 1.0
    },
    'middlegame': {
        'material': 1.0, 'position': 0.5, 'mobility': 2.0, 'king_safety': 1.5,
        'check': 2.0, 'center_control': 1.0, 'pawn_structure': 0.8, 'attack_defense': 1.2,
        'cannon_control': 1.5, 'king_threat': 1.5
    },
    'endgame': {
        'material': 1.2, 'position': 0.3, 'mobility': 1.5, 'king_safety': 2.0,
        'check': 2.5, 'center_control': 0.8, 'pawn_structure': 1.0, 'attack_defense': 1.0,
        'cannon_control': 1.0, 'king_threat': 2.0
    }
}