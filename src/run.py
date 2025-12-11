import subprocess
import os
import sys
import time

# Lấy thư mục file hiện tại
current_dir = os.path.dirname(__file__)

# Khai báo tên file main chạy
main_script = 'main.py'

# Lấy đường dẫn đầy đủ của file main
main_path = os.path.join(current_dir, main_script)

# Lấy trình thông dịch python
interpreter = sys.executable

def run_with_auto_restart():
    count_number = 1

    while True:
        print(f"--- Bắt đầu chạy {main_script} ---")

        # Dùng subprocess để chạy, file run.py sẽ dừng lại để chờ main.py làm việc.
        # Chỉ khi nào main.py hoàn tất (xong việc hoặc crash), run.py mới tiếp tục chạy xuống dòng dưới
        process = subprocess.run([interpreter, main_path])

        if process.returncode == 0 or count_number > 5:
            print(f"--- Chạy {main_script} hoàn tất ---")
            break
        else:
            print(f"--- Đã gặp lỗi trong quá trình chạy {main_script}. Restart sau 10s ---")
            time.sleep(10)

        count_number += 1

if __name__ == "__main__":
    run_with_auto_restart()