"""
0. Tiền xử lý ảnh (resize_image_with_padding): Resize ảnh về kích thước 640x640, thêm padding để giữ tỷ lệ khung hình.

1. Phát hiện giao điểm (detect_intersections): Sử dụng API Roboflow để tìm các giao điểm trên bàn cờ (90 giao điểm cho bàn cờ 10x9).

2. Phân nhóm giao điểm (group_intersections): Sắp xếp các giao điểm thành hàng và cột, tạo ma trận tọa độ.

3. Phát hiện quân cờ (detect_pieces): Sử dụng YOLOv8 để nhận diện các quân cờ trong ảnh.

4. Gán quân cờ vào giao điểm (assign_pieces_to_board): Ánh xạ các quân cờ vào ma trận, xử lý xung đột và giới hạn số lượng quân.

5. Kiểm tra và sửa lỗi (check_and_fix_king_advisor): Đảm bảo Tướng và Sĩ ở vị trí hợp lệ.

6. Xoay bàn cờ (orient_board): Đảm bảo quân Đen ở trên, quân Đỏ ở dưới.

7. Chuyển đổi ma trận (convert_to_game_board): Chuyển ma trận ký tự thành ma trận số nguyên.

8. Hàm chính (recognize_chess_board): Kết hợp các bước trên và lưu kết quả trực quan.

"""
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from ultralytics import YOLO
from inference_sdk import InferenceHTTPClient
import math
import os
from Khai_bao import *

# Định nghĩa giới hạn số lượng tối đa cho mỗi loại quân cờ
MAX_PIECE_COUNTS = {
    'b_che': 2, 'b_jiang': 1, 'b_ma': 2, 'b_pao': 2, 'b_shi': 2, 'b_xiang': 2, 'b_zu': 5,
    'r_bing': 5, 'r_che': 2, 'r_ma': 2, 'r_pao': 2, 'r_shi': 2, 'r_shuai': 1, 'r_xiang': 2
}

def find_model_file(filename='best.pt'):
    """
    Tìm file mô hình trong thư mục hiện tại và các thư mục con.

    Args:
        filename (str): Tên file cần tìm (mặc định là 'best.pt').

    Returns:
        str: Đường dẫn tới file nếu tìm thấy, None nếu không tìm thấy.
    """
    current_dir = os.getcwd()   
    print(f"Tìm kiếm file '{filename}' trong thư mục hiện tại: {current_dir}")
    for root, _, files in os.walk(current_dir):     # Sử dụng os.walk để duyệt qua tất cả thư mục và file từ thư mục hiện tại
        # Nếu tìm thấy thì in ra thông báo
        if filename in files:
            model_path = os.path.join(root, filename)
            print(f"Đã tìm thấy file '{filename}' tại: {model_path}")
            return model_path
    print(f"Không tìm thấy file '{filename}' trong thư mục hiện tại hoặc các thư mục con!")
    return None

def resize_image_with_padding(image_path, target_size=640):
    """
    B0: Tiền xử lý ảnh, resize thành 640x640 với padding để giữ tỷ lệ khung hình.

    Args:
        image_path (str): Đường dẫn đến tệp ảnh.
        target_size (int): Kích thước mục tiêu (mặc định 640).

    Returns:
        tuple: (Ảnh đã resize, tỷ lệ resize, padding: left, top, right, bottom)
    """
    img = Image.open(image_path)
    img_width, img_height = img.size
    resize_ratio = min(target_size / img_width, target_size / img_height)
    new_width = int(img_width * resize_ratio)
    new_height = int(img_height * resize_ratio)
    
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)     # Resize ảnh bằng pp LANCZOS (cho chất lượng cao).
    
    padding_left = (target_size - new_width) // 2
    padding_right = target_size - new_width - padding_left
    padding_top = (target_size - new_height) // 2
    padding_bottom = target_size - new_height - padding_top
    
    img_padded = Image.new('RGB', (target_size, target_size), (0, 0, 0))
    img_padded.paste(img_resized, (padding_left, padding_top))
    img_padded.save('banco_padded.jpg')
    
    print(f"Ảnh đã được resize tỷ lệ {resize_ratio:.3f}, padding: left={padding_left}, top={padding_top}, right={padding_right}, bottom={padding_bottom}, kích thước: {target_size}x{target_size}.")
    return np.array(img_padded), resize_ratio, padding_left, padding_top

def detect_intersections(image_path, conf=0.6, max_attempts=3):
    """
    B1: Phát hiện giao điểm sử dụng Roboflow API.

    Args:
        image_path (str): Đường dẫn đến ảnh đã padding.
        conf (float): Ngưỡng độ tin cậy ban đầu.
        max_attempts (int): Số lần thử tối đa.

    Returns:
        list: Danh sách các giao điểm [{'x': float, 'y': float, 'width': float, 'height': float, 'confidence': float, 'class': str}]
    """
    print("\nBước 1: Gửi ảnh lên API board-inter/2 để lấy giao điểm...")
    CLIENT = InferenceHTTPClient(api_url="https://serverless.roboflow.com", api_key="n7xRQpq1IzO3kTThXJAH")
    intersections = []
    attempt = 0
    
    while attempt < max_attempts:
        print(f"Phát hiện giao điểm với conf={conf:.2f} (lần {attempt + 1}/{max_attempts})")
        try:
            result = CLIENT.infer(image_path, model_id="board-inter/2")
            intersections = [
                {'x': pred['x'], 'y': pred['y'], 'width': pred['width'], 'height': pred['height'], 'confidence': pred['confidence'], 'class': 'chess_cross'}
                for pred in result['predictions'] if pred['class'] == '0' and pred['confidence'] >= conf
            ]
            print(f"Số lượng giao điểm: {len(intersections)}")
            # Nếu sô lượng giao điểm phát hiện được < 70 hoặc >95 thì điều chỉnh độ tin cậy
            if 70 <= len(intersections) <= 95:
                break
            elif len(intersections) < 70:
                conf = max(0.3, conf - 0.1)
            else:
                conf = min(0.9, conf + 0.1)
            attempt += 1
        except Exception as e:
            print(f"Lỗi khi gọi API: {e}")
            break
    
    if len(intersections) < 70 or len(intersections) > 95:
        print(f"Cảnh báo: Số lượng giao điểm ({len(intersections)}) không nằm trong khoảng 70-95 sau {max_attempts} lần thử!")
    
    return intersections

def group_intersections(intersections):
    """
    B2: Phân nhóm giao điểm thành hàng và cột.

    Args:
        intersections (list): Danh sách các giao điểm.

    Returns:
        tuple: (Ma trận tọa độ, số hàng, số cột, danh sách tọa độ phẳng)
    """
    print("\nBước 2: Phân nhóm giao điểm...")
    intersection_coords = [(i['x'], i['y']) for i in intersections]
    y_values = sorted([coord[1] for coord in intersection_coords])
    x_values = sorted([coord[0] for coord in intersection_coords])
    
    y_groups = []
    remaining_y = y_values.copy()
    while remaining_y:
        y_1 = remaining_y[0]
        group = [y for y in remaining_y if y_1 - 10 <= y <= y_1 + 10]       # Gộp các điểm có tọa độ y trong khoảng ±10 pixel
        y_groups.append(group)
        remaining_y = [y for y in remaining_y if y not in group]
    
    x_groups = []
    remaining_x = x_values.copy()
    while remaining_x:
        x_1 = remaining_x[0]
        group = [x for x in remaining_x if x_1 - 10 <= x <= x_1 + 10]       # Gộp các điểm có tọa độ x trong khoảng ±10 pixel
        x_groups.append(group)
        remaining_x = [x for x in remaining_x if x not in group]
    
    # Loại bỏ những nhóm có ít hơn 4 tọa độ (có thể là nhiễu)
    y_groups = [g for g in y_groups if len(g) >= 4]
    x_groups = [g for g in x_groups if len(g) >= 4]
    num_y_groups = len(y_groups)
    num_x_groups = len(x_groups)
    print(f"Số nhóm y sau khi lọc: {num_y_groups}, Số nhóm x sau khi lọc: {num_x_groups}")
    
    # Xác định kích thước ma trận
    if num_y_groups == 9 and num_x_groups == 10:
        num_rows, num_cols = 9, 10
        print("Ma trận: 9 hàng x 10 cột")
    elif num_y_groups == 10 and num_x_groups == 9:
        num_rows, num_cols = 10, 9
        print("Ma trận: 10 hàng x 9 cột")
    else:
        raise ValueError(f"Số cụm không hợp lệ: y={num_y_groups}, x={num_x_groups}")
    
    # Tính giá trị đại diện cho mỗi nhóm x và y
    y_representatives = [np.mean(group) for group in y_groups]
    x_representatives = [np.mean(group) for group in x_groups]
    y_representatives.sort()
    x_representatives.sort()
    
    # Gán giao điểm vào ma trận matrix_coords dựa trên khoảng cách gần nhất tới tọa độ đại diện 
    matrix_coords = [[None for _ in range(num_cols)] for _ in range(num_rows)]
    for group in y_groups:
        for x, y in [(x, y) for x, y in intersection_coords if y in group]:
            min_y_dist = float('inf')
            best_row = 0
            for i, y_rep in enumerate(y_representatives):
                dist = abs(y - y_rep)
                if dist < min_y_dist:
                    min_y_dist = dist
                    best_row = i
            min_x_dist = float('inf')
            best_col = 0
            for j, x_rep in enumerate(x_representatives):
                dist = abs(x - x_rep)
                if dist < min_x_dist:
                    min_x_dist = dist
                    best_col = j
            matrix_coords[best_row][best_col] = (x, y)
    
    # Nếu thiếu giao điểm, ước lượng tọa độ bằng trung bình của hàng/cột.
    estimated_coords = []
    total_slots = num_rows * num_cols
    filled_slots = sum(1 for row in matrix_coords for coord in row if coord is not None)
    if filled_slots < total_slots:
        for i in range(num_rows):
            for j in range(num_cols):
                if matrix_coords[i][j] is None:
                    estimated_x = x_representatives[j]
                    estimated_y = y_representatives[i]
                    matrix_coords[i][j] = (estimated_x, estimated_y)
                    estimated_coords.append((estimated_x, estimated_y))
    
    sorted_coords = [coord for row in matrix_coords for coord in row if coord is not None]
    print("\nMa trận tọa độ của các giao điểm từ YOLO:")
    for i in range(0, len(sorted_coords), num_cols):
        row_coords = sorted_coords[i:i+num_cols]
        print([f"({x:.1f}, {y:.1f})" for x, y in row_coords])
    if estimated_coords:
        print("\nTọa độ ước lượng cho các vị trí thiếu:")
        for x, y in estimated_coords:
            print(f"({x:.1f}, {y:.1f})")
    
    return matrix_coords, num_rows, num_cols, sorted_coords # sorted_coords (danh sách tọa độ phẳng)


def detect_pieces(image_path):
    """
    B3: Phát hiện quân cờ sử dụng YOLOv8.

    Args:
        image_path (str): Đường dẫn đến ảnh đã padding.

    Returns:
        list: Danh sách các bounding box của quân cờ.
    """
    print("\nBước 3: Tải mô hình YOLO để phát hiện quân cờ và dự đoán...")
    model_path = find_model_file('best.pt')
    if not model_path:
        raise FileNotFoundError("Không tìm thấy file mô hình 'best.pt' trong thư mục hiện tại hoặc các thư mục con. Vui lòng kiểm tra và đặt file đúng vị trí.")
    model_pieces = YOLO(model_path)
    results_pieces = model_pieces.predict(image_path, conf=0.02, iou=0.7)
    print(f"Số lượng bounding box quân cờ ban đầu: {len(results_pieces[0].boxes)}")
    return results_pieces[0]


def assign_pieces_to_board(results_pieces, matrix_coords, num_rows, num_cols, sorted_coords):
    """
    B4: Ánh xạ quân cờ vào các giao điểm và xử lý xung đột.

    Args:
        results_pieces: Kết quả dự đoán từ YOLOv8.
        matrix_coords (list): Ma trận tọa độ giao điểm.
        num_rows (int): Số hàng của ma trận.
        num_cols (int): Số cột của ma trận.
        sorted_coords (list): Danh sách tọa độ phẳng.

    Returns:
        tuple: (Ma trận bàn cờ, số lượng quân cờ, vị trí đã gán)
    """
    print("\nBước 4: Ánh xạ nhãn từ YOLO sang giao điểm...")
    # Ánh xạ nhãn (label_map): Chuyển nhãn YOLO (b_che, r_shuai, v.v.) thành ký tự (x, TG, v.v.)
    label_map = {
        'b_che': 'x', 'b_jiang': 'tg', 'b_ma': 'm', 'b_pao': 'p', 'b_shi': 's', 'b_xiang': 't', 'b_zu': 'b',
        'r_bing': 'B', 'r_che': 'X', 'r_ma': 'M', 'r_pao': 'P', 'r_shi': 'S', 'r_xiang': 'T', 'r_shuai': 'TG'
    }
    piece_counts = {label: 0 for label in MAX_PIECE_COUNTS}
    # Theo dõi số lượng quân cờ (piece_counts) và vị trí đã gán (assigned_positions)
    board = [['.' for _ in range(num_cols)] for _ in range(num_rows)]   
    assigned_positions = {}
    
    position_predictions = {}
    for box in results_pieces.boxes:
        x1, y1, x2, y2 = box.xyxy[0].numpy()
        # Tính tâm (x_center, y_center) của bounding box
        x_center = (x1 + x2) / 2
        y_center = (y1 + y2) / 2
        cls_id = int(box.cls[0])
        label = results_pieces.names[cls_id]
        conf = box.conf.item()
        
        if label in label_map:
            min_dist = float('inf')
            best_intersection_idx = -1
            # Tìm giao điểm gần nhất trong sorted_coords bằng khoảng cách Euclidean.
            for idx, (x_int, y_int) in enumerate(sorted_coords):
                dist = math.sqrt((x_center - x_int) ** 2 + (y_center - y_int) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    best_intersection_idx = idx

            if best_intersection_idx != -1:
                row = best_intersection_idx // num_cols
                col = best_intersection_idx % num_cols

                if 0 <= row < num_rows and 0 <= col < num_cols:
                    pos_key = (row, col)
                    # Gán quân cờ vào vị trí (row, col) trong position_predictions với thông tin nhãn, độ tin cậy, và box.
                    if pos_key not in position_predictions:
                        position_predictions[pos_key] = []
                    position_predictions[pos_key].append({
                        'label': label_map[label],
                        'conf': conf,
                        'box': box,
                        'orig_label': label
                    })
                    print(f"Tạm gán {label_map[label]} (conf={conf:.3f}) to board[{row}][{col}] at (x={x_center:.1f}, y={y_center:.1f})")
    
    # Xử lý xung đột:
    # Sắp xếp dự đoán tại mỗi vị trí theo độ tin cậy (conf) giảm dần.
    for pos_key in position_predictions:
        position_predictions[pos_key] = sorted(position_predictions[pos_key], key=lambda x: x['conf'], reverse=True)
    
    # Gán quân cờ có độ tin cậy cao nhất, kiểm tra giới hạn MAX_PIECE_COUNTS (ví dụ: tối đa 2 Xe Đen,...)
    for pos_key in position_predictions:
        row, col = pos_key
        predictions = position_predictions[pos_key]
        for pred in predictions:
            label = pred['orig_label']
            mapped_label = pred['label']
            conf = pred['conf']
            box = pred['box']

            if piece_counts[label] < MAX_PIECE_COUNTS[label]:
                if pos_key not in assigned_positions:
                    board[row][col] = mapped_label

                    assigned_positions[pos_key] = {'label': mapped_label, 'conf': conf, 'box': box}
                    piece_counts[label] += 1

                    x_center = (box.xyxy[0][0].numpy() + box.xyxy[0][2].numpy()) / 2
                    y_center = (box.xyxy[0][1].numpy() + box.xyxy[0][3].numpy()) / 2
                    print(f"Assigned {mapped_label} (conf={conf:.3f}) to board[{row}][{col}] at (x={x_center:.1f}, y={y_center:.1f})")
                
                # Nếu có xung đột, giữ quân cờ có độ tin cậy cao hơn, cập nhật piece_counts và assigned_positions.
                else:
                    existing_conf = assigned_positions[pos_key]['conf']
                    if conf > existing_conf:
                        old_label = results_pieces.names[int(assigned_positions[pos_key]['box'].cls[0])]

                        piece_counts[old_label] -= 1
                        board[row][col] = mapped_label

                        assigned_positions[pos_key] = {'label': mapped_label, 'conf': conf, 'box': box}
                        piece_counts[label] += 1
                        print(f"Xung đột tại board[{row}][{col}]: Thay thế {label_map[old_label]} (conf={existing_conf:.3f}) bằng {mapped_label} (conf={conf:.3f})")
                    else:
                        print(f"Xung đột tại board[{row}][{col}]: Giữ {assigned_positions[pos_key]['label']} (conf={existing_conf:.3f}), bỏ qua {mapped_label} (conf={conf:.3f})")
            else:
                print(f"Bỏ qua {mapped_label} tại board[{row}][{col}] vì vượt quá giới hạn {MAX_PIECE_COUNTS[label]}")
    
    print("\nSố lượng quân cờ được gán:")
    for label, count in piece_counts.items():
        print(f"{label}: {count}/{MAX_PIECE_COUNTS[label]}")
    
    return board, piece_counts, assigned_positions

def check_and_fix_king_advisor(board, num_rows, num_cols, position_predictions, piece_counts, assigned_positions, label_map, results_pieces):
    """
    B5: Kiểm tra và sửa tính hợp lệ của Tướng và Sĩ.

    Args:
        board (list): Ma trận bàn cờ.
        num_rows (int): Số hàng.
        num_cols (int): Số cột.
        position_predictions (dict): Dự đoán vị trí.
        piece_counts (dict): Số lượng quân cờ.
        assigned_positions (dict): Vị trí đã gán.
        label_map (dict): Ánh xạ nhãn.
        results_pieces: Kết quả YOLOv8.

    Returns:
        list: Danh sách lỗi (nếu có).
    """
    print("\nBước 5: Kiểm tra và sửa tính hợp lệ của Tướng và Sĩ...")
    errors = []
    black_king_count = piece_counts.get('b_jiang', 0)
    red_king_count = piece_counts.get('r_shuai', 0)
    black_advisor_positions = [(i, j) for i in range(num_rows) for j in range(num_cols) if board[i][j] == 's' and (i not in [0, 1, 2] or j not in [3, 4, 5])]
    red_advisor_positions = [(i, j) for i in range(num_rows) for j in range(num_cols) if board[i][j] == 'S' and (i not in [num_rows-3, num_rows-2, num_rows-1] or j not in [3, 4, 5])]
    
    if black_king_count != 1:
        errors.append(f"Số lượng Tướng Đen: {black_king_count}, yêu cầu đúng 1.")
    if red_king_count != 1:
        errors.append(f"Số lượng Tướng Đỏ: {red_king_count}, yêu cầu đúng 1.")
    if black_advisor_positions:
        errors.append(f"Sĩ Đen tại vị trí không hợp lệ: {black_advisor_positions}")
    if red_advisor_positions:
        errors.append(f"Sĩ Đỏ tại vị trí không hợp lệ: {red_advisor_positions}")
    
    return errors


def orient_board(board, num_rows, num_cols):
    """
    B6: Xoay bàn cờ để đảm bảo quân Đen ở trên, quân Đỏ ở dưới.

    Args:
        board (list): Ma trận bàn cờ.
        num_rows (int): Số hàng.
        num_cols (int): Số cột.

    Returns:
        tuple: (Ma trận đã xoay, số hàng, số cột)
    """
    print("\nBước 6: Kiểm tra và xoay ma trận nếu cần...")
    if num_rows == 9 and num_cols == 10:
        print("Bàn cờ nằm ngang (9 hàng x 10 cột), xoay 90 độ để thành dọc (10 hàng x 9 cột)...")
        rotated_board = [['.' for _ in range(9)] for _ in range(10)]
        for i in range(num_rows):
            for j in range(num_cols):
                rotated_board[j][num_rows-1-i] = board[i][j]
        board = rotated_board
        num_rows, num_cols = 10, 9
        print("Đã xoay ma trận 90 độ thành công!")
    
    # Kiểm tra s, tg, t phải ở nửa trê; S, T, TG phải ở nữa dưới bàn cờ
    black_pieces = {'s', 'tg', 't'}
    red_pieces = {'TG', 'S', 'T'}
    invalid_positions = []
    for i in range(num_rows):
        for j in range(num_cols):
            piece = board[i][j]
            if i < 5 and piece in red_pieces:
                invalid_positions.append(f"Quân đỏ {piece} tại [{i}][{j}] ở nửa trên!")
            elif i >= 5 and piece in black_pieces:
                invalid_positions.append(f"Quân đen {piece} tại [{i}][{j}] ở nửa dưới!")
    
    if invalid_positions:
        print("Phát hiện vị trí không hợp lệ, xoay ma trận 180 độ...")
        for error in invalid_positions:
            print(f"- {error}")
        rotated_board = [['.' for _ in range(num_cols)] for _ in range(num_rows)]
        for i in range(num_rows):
            for j in range(num_cols):
                rotated_board[num_rows-1-i][num_cols-1-j] = board[i][j]
        board = rotated_board
        print("Đã xoay ma trận 180 độ thành công!")
    
    print("\nMa trận cuối cùng sau khi xử lý:")
    for row in board:
        print(' '.join(row))
    
    return board, num_rows, num_cols

def convert_to_game_board(board):
    """
    Chuyển ma trận nhận diện thành ma trận bàn cờ của trò chơi (10x9, số nguyên).

    Args:
        board (list): Ma trận nhận diện (ký tự).

    Returns:
        np.ndarray: Ma trận bàn cờ (10x9, số nguyên).
    """
    piece_to_value = {
        'x': COLOR_DARK * 10 + ROOK, 'tg': COLOR_DARK * 10 + KING, 'm': COLOR_DARK * 10 + KNIGHT,
        'p': COLOR_DARK * 10 + CANNON, 't': COLOR_DARK * 10 + ELEPHANT, 's': COLOR_DARK * 10 + BISHOP,
        'b': COLOR_DARK * 10 + PAWN, 'X': COLOR_LIGHT * 10 + ROOK, 'TG': COLOR_LIGHT * 10 + KING,
        'M': COLOR_LIGHT * 10 + KNIGHT, 'P': COLOR_LIGHT * 10 + CANNON, 'T': COLOR_LIGHT * 10 + ELEPHANT,
        'S': COLOR_LIGHT * 10 + BISHOP, 'B': COLOR_LIGHT * 10 + PAWN, '.': EMPTY
    }
    game_board = np.zeros((10, 9), dtype=int)
    for i in range(10):
        for j in range(9):
            game_board[i, j] = piece_to_value.get(board[i][j], EMPTY)
    return game_board


def recognize_chess_board(image_path):
    """
    Hàm chính để nhận diện bàn cờ từ ảnh.

    Args:
        image_path (str): Đường dẫn đến tệp ảnh.

    Returns:
        tuple: (Ma trận bàn cờ, số hàng, số cột)
    """
    # B0: Gọi resize_image_with_padding để xử lý ảnh đầu vào
    img_padded, _, _, _ = resize_image_with_padding(image_path)
    intersections = detect_intersections('banco_padded.jpg')
    
    # B1: Gọi detect_intersections để lấy giao điểm, lưu kết quả trực quan vào intersections_output.jpg.
    fig, ax = plt.subplots(figsize=(9, 10))
    ax.imshow(img_padded)
    for box in intersections:
        x = box['x'] - box['width'] / 2
        y = box['y'] - box['height'] / 2
        width = box['width']
        height = box['height']
        confidence = box['confidence']
        ax.add_patch(plt.Rectangle((x, y), width, height, linewidth=1, edgecolor='b', facecolor='none'))
        ax.text(x, y, f"({confidence:.3f})", color='b')
    ax.set_title('Bounding Boxes từ API Roboflow (chess_cross)')
    plt.savefig('intersections_output.jpg')
    plt.close(fig)
    
    # B2: Gọi group_intersections để tạo ma trận tọa độ.
    matrix_coords, num_rows, num_cols, sorted_coords = group_intersections(intersections)
    results_pieces = detect_pieces('banco_padded.jpg')
    
    # B3: Gọi detect_pieces để phát hiện quân cờ, lưu kết quả trực quan vào pieces_output.jpg
    fig, ax = plt.subplots(figsize=(9, 10))
    ax.imshow(results_pieces.orig_img)
    for box in results_pieces.boxes:
        x1, y1, x2, y2 = box.xyxy[0].numpy()
        cls_id = int(box.cls[0])
        label = results_pieces.names[cls_id]
        ax.add_patch(plt.Rectangle((x1, y1), x2-x1, y2-y1, linewidth=1, edgecolor='r', facecolor='none'))
        ax.text(x1, y1, f"{label} ({box.conf.item():.3f})", color='r')
    ax.set_title('Bounding Boxes từ YOLOv8 (quân cờ)')
    plt.savefig('pieces_output.jpg')
    plt.close(fig)
    
    # B4: Gọi assign_pieces_to_board để gán quân cờ vào ma trận.
    board, piece_counts, assigned_positions = assign_pieces_to_board(results_pieces, matrix_coords, num_rows, num_cols, sorted_coords)
    
    # B5: Gọi check_and_fix_king_advisor để kiểm tra Tướng và Sĩ.
    errors = check_and_fix_king_advisor(board, num_rows, num_cols, {}, piece_counts, assigned_positions, {
        'b_che': 'x', 'b_jiang': 'tg', 'b_ma': 'm', 'b_pao': 'p', 'b_shi': 's', 'b_xiang': 't', 'b_zu': 'b',
        'r_bing': 'B', 'r_che': 'X', 'r_ma': 'M', 'r_pao': 'P', 'r_shi': 'S', 'r_xiang': 'T', 'r_shuai': 'TG'
    }, results_pieces)
    if errors:
        print("Lỗi phát hiện trong ma trận:")
        for error in errors:
            print(f"- {error}")
    
    # B6: Gọi orient_board để xoay bàn cờ.
    board, num_rows, num_cols = orient_board(board, num_rows, num_cols)

    # B7: Gọi convert_to_game_board để tạo ma trận số nguyên
    game_board = convert_to_game_board(board)
    return game_board, num_rows, num_cols