import sqlite3
import os
from config import DB_PATH # config 파일에서 DB 경로를 가져옴

# --- 데이터베이스 초기화 ---
def initialize_database():
    """데이터베이스와 모든 테이블 구조를 생성(DDL)합니다."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        print("--- 데이터베이스 초기화 시작 ---")
        # 1. Users 테이블 생성
        c.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username        TEXT NOT NULL UNIQUE,
                password_hash   TEXT NOT NULL,
                user_email      TEXT UNIQUE
            )
        ''')
        print("-> Users 테이블 준비 완료.")
        # 2. Companies 테이블 생성
        c.execute('''
            CREATE TABLE IF NOT EXISTS Companies (
                company_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name    TEXT NOT NULL UNIQUE,
                employee_count  INTEGER,
                revenue         INTEGER,
                overview        TEXT,
                website         TEXT
            )
        ''')
        print("-> Companies 테이블 준비 완료.")

        # 3. Contacts 테이블 생성
        c.execute('''
            CREATE TABLE IF NOT EXISTS Contacts (
                contact_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id      INTEGER,
                contact_name    TEXT NOT NULL,
                department      TEXT,
                position        TEXT,
                email           TEXT UNIQUE,
                phone           TEXT,
                mobile_phone    TEXT,
                FOREIGN KEY (company_id) REFERENCES Companies (company_id)
            )
        ''')
        print("-> Contacts 테이블 준비 완료.")
        
        # 4. Products 테이블 생성
        c.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                product_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name    TEXT NOT NULL UNIQUE,
                unit_price      REAL NOT NULL
            )
        ''')
        print("-> Products 테이블 준비 완료.")

        # 5. Projects 테이블 생성
        c.execute('''
            CREATE TABLE IF NOT EXISTS Projects (
                project_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id      INTEGER NOT NULL,
                project_name    TEXT NOT NULL,
                description     TEXT,
                status          TEXT,
                start_date      DATE,
                end_date        DATE,
                FOREIGN KEY (company_id) REFERENCES Companies (company_id)
            )
        ''')
        print("-> Projects 테이블 준비 완료.")
        
        # 6. Invoices 테이블 생성
        c.execute('''
            CREATE TABLE IF NOT EXISTS Invoices (
                invoice_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id      INTEGER NOT NULL,
                company_id      INTEGER NOT NULL,
                contact_id      INTEGER NOT NULL,
                user_id         INTEGER NOT NULL,
                issue_date      DATE NOT NULL,
                due_date        DATE,
                total_amount    REAL,
                status          TEXT,
                FOREIGN KEY (project_id) REFERENCES Projects (project_id),
                FOREIGN KEY (company_id) REFERENCES Companies (company_id),
                FOREIGN KEY (contact_id) REFERENCES Contacts (contact_id),
                FOREIGN KEY (user_id) REFERENCES Users (user_id)
            )
        ''')
        print("-> Invoices 테이블 준비 완료.")

        # 7. Tasks 테이블 생성
        c.execute('''
            CREATE TABLE IF NOT EXISTS Tasks (
                task_id         INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id      INTEGER,
                company_id      INTEGER NOT NULL,
                contact_id      INTEGER,
                user_id         INTEGER NOT NULL,
                action_date     DATE NOT NULL,
                agenda          TEXT,
                action_item     TEXT,
                due_date        DATE,
                task_status     TEXT, -- 예: 'To-Do', '진행 중', '완료'
                FOREIGN KEY (project_id) REFERENCES Projects (project_id),
                FOREIGN KEY (company_id) REFERENCES Companies (company_id),
                FOREIGN KEY (contact_id) REFERENCES Contacts (contact_id),
                FOREIGN KEY (user_id) REFERENCES Users (user_id)
            )
        ''')
        print("-> Tasks 테이블 준비 완료.")
        
        # 8. Invoice_Items 테이블 생성
        c.execute('''
            CREATE TABLE IF NOT EXISTS Invoice_Items (
                item_id             INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id          INTEGER NOT NULL,
                product_id          INTEGER NOT NULL,
                quantity            INTEGER NOT NULL,
                unit_price_at_sale  REAL NOT NULL,
                discount_rate       REAL DEFAULT 0,
                subtotal            REAL NOT NULL,
                FOREIGN KEY (invoice_id) REFERENCES Invoices (invoice_id),
                FOREIGN KEY (product_id) REFERENCES Products (product_id)
            )
        ''')
        print("-> Invoice_Items (연결 테이블) 준비 완료.")

        # 9. Project_Participants 테이블 생성
        c.execute('''
            CREATE TABLE IF NOT EXISTS Project_Participants (
                project_id      INTEGER NOT NULL,
                contact_id      INTEGER NOT NULL,
                role            TEXT, -- 예: '영업 담당', '기술 지원', 'PM' 등 담당자의 프로젝트 내 역할
                PRIMARY KEY (project_id, contact_id), -- 한 프로젝트에 같은 담당자가 중복 추가되는 것을 방지
                FOREIGN KEY (project_id) REFERENCES Projects (project_id),
                FOREIGN KEY (contact_id) REFERENCES Contacts (contact_id)
            )
        ''')
        print("-> Project_Participants (연결 테이블) 준비 완료.")
        
        conn.commit()
        print("--- 데이터베이스 초기화 완료: 모든 테이블이 준비되었습니다. ---")

    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("데이터베이스 스키마가 성공적으로 초기화/확인되었습니다.")

# 이 스크립트 파일(database.py)을 직접 실행했을 때만 아래 코드가 동작함
if __name__ == '__main__':
    print("database.py가 직접 실행되었습니다. 데이터베이스 초기화를 진행합니다.")
    initialize_database()
