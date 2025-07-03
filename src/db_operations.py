import sqlite3
from config import DB_PATH # config 파일에서 DB 경로를 가져옴

def add_company(name, employee_count=None, revenue=None, website=None):
    """Companies 테이블에 새로운 회사 정보를 추가(DML)합니다."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        sql = "INSERT INTO Companies (company_name, ...) VALUES (?, ?, ?, ?)"
        c.execute(sql, (name, employee_count, revenue, website))
        conn.commit()
        new_id = c.lastrowid
        return new_id
    except sqlite3.IntegrityError:
        return None # 이미 존재하는 경우
    finally:
        if conn:
            conn.close()

# ... (add_contact, get_companies 등 앞으로 만들 모든 DML 함수가 여기에 들어옴) ...