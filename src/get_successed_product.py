import glob
import os
import  json

def get_successed_id(json_file_path):
    successed_ids = set()

    if not os.path.exists(json_file_path):
        return successed_ids

    # Quét tất cả các file có đuôi .json trong thư mục đó và trả về một danh sách đường dẫn file thỏa mãn
    files = glob.glob(os.path.join(json_file_path, "*.json"))

    # Lấy tất cả Id đã crawl thành công để thêm vào set successed_ids
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                for item in data:
                    successed_ids.add(str(item['id']))
        except Exception:
            continue

    return successed_ids

# get_successed_id('/home/huytq/UNIGAP/Project2/jsonfile')
