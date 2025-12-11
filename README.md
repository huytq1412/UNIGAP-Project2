# Tiki Product Crawler 

Công cụ thu thập dữ liệu sản phẩm Tiki số lượng lớn, được tối ưu hóa cho tốc độ, độ ổn định.

![Python](https://img.shields.io/badge/Python-3.0%2B-blue) ![Status](https://img.shields.io/badge/Status-Completed-success)

## Tính năng

* Tốc độ cao: Sử dụng kỹ thuật Multithreading (`concurrent.futures`) để xử lý 30 request song song, tăng tốc độ gấp nhiều lần so với tuần tự.
* Xử lý dữ liệu phân lô: hệ thống sử dụng kỹ thuật Stream Processing thông qua tham số chunksize của Pandas.
* Cơ chế (Auto-Restart): 
  * sử dụng subprocess để tự động khởi động lại tiến trình sau 10 giây nếu gặp sự cố (Crash/Mất mạng) thông qua script giám sát `run.py`.
  * Tự thử lại tối đa 5 lần khi gặp sự cố.
* Cơ chế (Resume): Nếu chương trình bị ngắt, lần sau chạy lại sẽ loại trừ danh sách các id đã crawl thành công và tiếp tục tại batch dừng (không crawl lại từ đầu). Tự động bỏ qua các Batch đã tải xong. 
*  Dữ liệu sạch:
    * Tự động loại bỏ thẻ HTML
    * Chuẩn hóa xuống dòng (`\n`).
* Chống chặn: Sử dụng `fake-useragent` để xoay vòng danh tính, tránh việc request quá nhiều lên server từ một nguồn sẽ dễ bị chặn


Cấu trúc của Project2

```
Project2/
├── data/
│   └── products-0-200000.csv   # File input dữ liệu danh sách Id các sản phẩm của Tiki 
├── src/
│   ├── __init__.py
│   ├── add_error.py            # Xử lý ghi dữ liệu vào file
│   ├── get_product.py          # Crawl dữ liệu chi tiết từng sản phẩm và làm sạch description
│   ├── retry_error_product.py  # Crawl lại dữ liệu danh sách các id bị lỗi từ phía client
│   ├── main.py                 # Đọc CSV input, crawl đa luồng, xử lý dữ liệu và đẩy vào các file ouput
│   └── run.py                  # Chạy toàn bộ project xử lý có hỗ trợ auto restart
├── jsonfile/                   # Thư mục chứa các file output của các sản phẩm crawl thành công (không đẩy lên git)
├── errorfile/                  # Thư mục chứa các file output là các Id của sản phẩm crawl gặp lỗi (không đẩy lên git)
├── .env                        # Các biến môi trường (không đẩy lên git)
│                               Bao gồm các biến để kết nối PostgreSQL,
│                                       DATA_PATH(đường dẫn lưu file csv),
│                                       JSON_FILE_PATH(đường dẫn kết xuất các file json),
│                                       ERROR_FILE_PATH(đường dẫn kết xuất các file chứa Id sản phẩm lỗi)
├── .gitignore                # File loại trừ khi đẩy lên git
├── requirements.txt          # Các thư viện cần cài
└── README.md                 # Tài liệu hướng dẫn sử dụng
```

## Cài đặt & Cấu hình
1. Yêu cầu hệ thống
Python 3.10 trở lên.

2. Cài đặt thư viện
Khuyên dùng môi trường ảo (venv):

```
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt (Linux/Mac)
source .venv/bin/activate

# Kích hoạt (Windows)
.venv\Scripts\activate

# Cài đặt thư viện
pip install -r requirements.txt
```
3. Cấu hình biến môi trường (.env)
Tạo file .env tại thư mục gốc và điền thông tin tương ứng:
```
# Đường dẫn dữ liệu 
DATA_PATH = "~/UNIGAP/Project2/data"
JSON_FILE_PATH = "~/UNIGAP/Project2/jsonfile"
ERROR_FILE_PATH = "~/UNIGAP/Project2/errorfile"
```

## Hướng dẫn sử dụng
Chạy script giám sát `run.py` (Khuyên dùng). Chương trình sẽ tự động Restart nếu gặp sự cố.

```
python src/run.py
```

## Định dạng file output (JSON)
Mỗi file JSON chứa khoảng 1.000 sản phẩm với cấu trúc:

```
[
    {
        "id": 1391347,
        "name": "Bộ Xếp Hình...",
        "url_key": "bo-xep-hinh-tia-sang",
        "price": 211200,
        "description": "Thông tin chi tiết...\n- Chất liệu an toàn.",
        "images": [...]
    }
```