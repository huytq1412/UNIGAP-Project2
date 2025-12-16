from configparser import ConfigParser
import os
from dotenv import load_dotenv

# Lấy thư mục file hiện tại
current_dir = os.path.dirname(__file__)

# Lấy thư mục gốc của project
project_dir = os.path.abspath(os.path.join(current_dir, '..'))

# Lấy thư mục file .env
env_path = os.path.join(project_dir, '.env')

load_dotenv(dotenv_path=env_path)

filename = os.environ.get('DATABASE_CONN_FILE')
filename = os.path.expanduser(filename)

def load_config(filename=filename, section='postgresql'):
    parser = ConfigParser()

    parser.read(filename)

    config = {}

    if parser.has_section(section):
        params = parser.items(section)

        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Không tìm thấy mục {0} trong file {1}'.format(section, filename))

    return config

if __name__ == "__main__":
    config = load_config()

