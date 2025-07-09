import os
import sys

def get_project_root():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        # 이 파일이 src 폴더 안에 있으므로, 부모 폴더가 프로젝트 루트입니다.
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = get_project_root()
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# --- 데이터베이스 이름 설정 (Single Source of Truth) ---
# 이 부분의 값만 바꾸면 프로젝트 전체의 DB 파일이 변경됩니다.
DB_FILENAME = 'mobilint_crm.db' 
# 예: 테스트용 DB를 쓰고 싶다면 -> DB_FILENAME = 'test_crm.db'

# --- 최종 DB 경로 ---
# 다른 모든 파일들은 이 DB_PATH 변수 하나만 import해서 사용합니다.
DB_PATH = os.path.join(DATA_DIR, DB_FILENAME)