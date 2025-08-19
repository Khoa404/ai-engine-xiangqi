import sys
import platform

def clear_input_buffer():
    """Xóa bộ đệm đầu vào, tương thích với Windows và các hệ thống khác."""
    if platform.system() == "Windows":
        try:
            import msvcrt
            while msvcrt.kbhit():  # Kiểm tra xem có phím nào đang chờ trong bộ đệm
                msvcrt.getch()     # Đọc và bỏ qua phím đó
        except ImportError:
            pass  # Nếu msvcrt không khả dụng, bỏ qua
    else:
        try:
            import select
            while select.select([sys.stdin], [], [], 0)[0]:
                sys.stdin.readline()
        except:
            pass  # Nếu select không khả dụng, bỏ qua