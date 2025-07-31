import sqlite3
import os
from config import DB_PATH

def initialize_database():
    """데이터베이스와 모든 테이블 구조를 생성(DDL)합니다."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        print("--- 데이터베이스 초기화 시작 ---")

        # 기존 테이블들 -------------------------------
        
        # User (e.g., Junyeob, Seongmo, ...)
        c.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                user_email TEXT UNIQUE,
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted     BOOLEAN DEFAULT 0
            )
        ''')

        # Clients (e.g., LG electronics, Hanwha Systems, ...)
        c.execute('''
            CREATE TABLE IF NOT EXISTS Companies (
                company_id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL UNIQUE,
                employee_count INTEGER,
                revenue INTEGER,
                overview TEXT,
                website TEXT,
                nationality TEXT NOT NULL  -- alpha-3 code (e.g., KOR, USA),
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted     BOOLEAN DEFAULT 0
            )
        ''')

        # Contacts (e.g., 박봉팔 부장님, 길정현 상무님, ...)
        c.execute('''
            CREATE TABLE IF NOT EXISTS Contacts (
                contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                contact_name TEXT NOT NULL,
                department TEXT,
                position TEXT,
                email TEXT UNIQUE,
                phone TEXT,
                mobile_phone TEXT,
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted     BOOLEAN DEFAULT 0,
                
                FOREIGN KEY (company_id) REFERENCES Companies (company_id)
            )
        ''')

        # 제품(e.g., MLA100, REGULUS, Sample PC, SDK license, ...)
        c.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL UNIQUE,
                min_price REAL,
                max_price REAL,
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted     BOOLEAN DEFAULT 0
            )
        ''')

        # Projects (e.g., Hanwha System-Teleport, ...)
        c.execute('''
            CREATE TABLE IF NOT EXISTS Projects (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                contact_id INTEGER,
                project_name TEXT NOT NULL,
                description TEXT,
                status TEXT,
                start_date DATE,
                end_date DATE,
                application TEXT,   -- 예: 반도체 품질검사, 영상처리 등
                ai_model TEXT,      -- 예: YOLOv8, Llama2-7B
                requirement TEXT,   -- 기술적 요구사항
                memo TEXT,
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted     BOOLEAN DEFAULT 0,
                
                FOREIGN KEY (company_id) REFERENCES Companies (company_id),
                FOREIGN KEY (contact_id) REFERENCES Contacts (contact_id)
            )
        ''')
        
        # 다중 제품 사용 시
        c.execute('''
                CREATE TABLE IF NOT EXISTS Project_Products (
                project_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted     BOOLEAN DEFAULT 0,
                
                PRIMARY KEY (project_id, product_id),
                FOREIGN KEY (project_id) REFERENCES Projects(project_id),
                FOREIGN KEY (product_id) REFERENCES Products(product_id)
            )
        ''')

        # Invoice가 발생한 것을 관리
        c.execute('''
            CREATE TABLE IF NOT EXISTS Invoices (
                invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                contact_id INTEGER,
                user_id INTEGER NOT NULL,
                issue_date DATE NOT NULL,
                due_date DATE,
                total_amount REAL,
                status INTEGER DEFAULT 0 CHECK (status IN (0, 1, 2, 3, 4, 5)),
                -- status 의미:
                -- 0: 발행 전 / 1: 발행 완료 / 2: 입금 완료 / 3: 발송 완료
                -- 4: 취소됨 / 5: 반품 처리
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted     BOOLEAN DEFAULT 0,
                
                FOREIGN KEY (project_id) REFERENCES Projects (project_id),
                FOREIGN KEY (company_id) REFERENCES Companies (company_id),
                FOREIGN KEY (contact_id) REFERENCES Contacts (contact_id),
                FOREIGN KEY (user_id) REFERENCES Users (user_id)
            )
        ''')
        
        # Task 입력 (이메일, 연락, 지시사항 등 변동 사항 발생 시 모두 기록)
        c.execute('''
            CREATE TABLE IF NOT EXISTS Tasks (
                task_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id     INTEGER,
                company_id     INTEGER NOT NULL,
                contact_id     INTEGER,
                user_id        INTEGER NOT NULL,
                invoice_id     INTEGER,  -- 주문/청구 관련 연락일 경우 연결
                action_date    DATE NOT NULL,
                agenda         TEXT,
                action_item    TEXT,
                due_date       DATE,
                task_status    INTEGER DEFAULT 0 CHECK (task_status IN (0, 1)),
                -- 0: 미실행 / 1: 실행 완료 (트리거 조건)
                task_type TEXT NOT NULL,    -- 'meeting','contact','quote','trial','tech_inquiry','delayed',...
                priority       INTEGER DEFAULT 1 CHECK(priority IN (0,1,2)),
                -- 0: 낮음, 1: 보통, 2: 높음
                memo TEXT,                  -- 기타 특이사항, 만족도 등 자유 기록
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted     BOOLEAN DEFAULT 0,
                
                FOREIGN KEY (project_id) REFERENCES Projects (project_id),
                FOREIGN KEY (company_id) REFERENCES Companies (company_id),
                FOREIGN KEY (contact_id) REFERENCES Contacts (contact_id),
                FOREIGN KEY (user_id) REFERENCES Users (user_id),
                FOREIGN KEY (invoice_id) REFERENCES Invoices (invoice_id)
            )
        ''')

        # Invoice 발생 시 세부 내역
        c.execute('''
            CREATE TABLE IF NOT EXISTS Invoice_Items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price_at_sale REAL NOT NULL,
                subtotal REAL NOT NULL,
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted     BOOLEAN DEFAULT 0,
                
                FOREIGN KEY (invoice_id) REFERENCES Invoices (invoice_id),
                FOREIGN KEY (product_id) REFERENCES Products (product_id)
            )
        ''')

        # Project Participants Management
        c.execute('''
            CREATE TABLE IF NOT EXISTS Project_Participants (
                project_id INTEGER NOT NULL,
                contact_id INTEGER NOT NULL,
                role TEXT,
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted     BOOLEAN DEFAULT 0,
                
                PRIMARY KEY (project_id, contact_id),
                FOREIGN KEY (project_id) REFERENCES Projects (project_id),
                FOREIGN KEY (contact_id) REFERENCES Contacts (contact_id)
            )
        ''')

        # 신규 테이블들 -------------------------------

        # 최초 컨택 (인바운드/콜드콜/전시 등)
        c.execute('''
            CREATE TABLE IF NOT EXISTS First_Contact_Logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 각 컨택 이력의 고유 ID
                company_id INTEGER NOT NULL,                -- 컨택된(한) 회사
                contact_id INTEGER,                         -- 특정 담당자 (없을 수 있음)
                project_id INTEGER DEFAULT 0,               -- 전환된 프로젝트 ID (없으면 0)
                contact_type TEXT,                          -- 인바운드 / 콜드콜 / 전시 등 컨택 유형
                channel TEXT,                               -- 알게된 경로(전시명, 뉴스, 네트워킹 등)
                contact_date DATE NOT NULL,                 -- 최초 접촉 날짜
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted     BOOLEAN DEFAULT 0,
                
                FOREIGN KEY (company_id) REFERENCES Companies(company_id),
                FOREIGN KEY (contact_id) REFERENCES Contacts(contact_id),
                FOREIGN KEY (project_id) REFERENCES Projects(project_id)
            )
        ''')

        # 무상 대여
        c.execute('''
            CREATE TABLE IF NOT EXISTS Free_Trials (
            task_id INTEGER PRIMARY KEY,              -- Tasks와 1:1 연결
            project_id INTEGER NOT NULL,              -- 어떤 프로젝트에서의 대여인지
            product_id INTEGER NOT NULL,              -- 어떤 제품을 대여했는지
            start_date DATE,                          -- 대여 시작일
            end_date DATE,                            -- 대여 종료일
            is_converted BOOLEAN DEFAULT 0,           -- 전환 여부 (예: 실제 구매 발생 여부)
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted     BOOLEAN DEFAULT 0,
            
            FOREIGN KEY (task_id) REFERENCES Tasks(task_id),
            FOREIGN KEY (project_id) REFERENCES Projects(project_id),
            FOREIGN KEY (product_id) REFERENCES Products(product_id)
            )
        ''')

        # 기술 문의
        c.execute('''
            CREATE TABLE IF NOT EXISTS Tech_Inquiries (
                task_id INTEGER PRIMARY KEY,              -- Tasks와 1:1 연결
                project_id INTEGER,                       -- 연관된 프로젝트 (없을 수 있음)
                product_id INTEGER,                       -- 어떤 제품 관련 이슈인지
                application TEXT,                         -- 사용 분야 (project_id가 없을 때만 입력)
                ai_model TEXT,                            -- 적용 모델 (project_id가 없을 때만 입력)
                is_resolved BOOLEAN DEFAULT 0,            -- 문제 해결 여부 (0=미해결, 1=해결)
                -- 해결/요약 내용은 Tasks.agenda에 기록합니다.
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted     BOOLEAN DEFAULT 0,

                FOREIGN KEY (task_id) REFERENCES Tasks(task_id),
                FOREIGN KEY (project_id) REFERENCES Projects(project_id),
                FOREIGN KEY (product_id) REFERENCES Products(product_id),
            )
        ''')

         # --- 2. 인덱스 생성 (성능 최적화) ---
        c.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user    ON Tasks(user_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON Tasks(project_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_tasks_type    ON Tasks(task_type);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_invoices_user  ON Invoices(user_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_invoices_proj  ON Invoices(project_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_firstcontact_co ON First_Contact_Logs(company_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_free_trials_pr ON Free_Trials(project_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_techinq_product ON Tech_Inquiries(product_id);")
        
        conn.commit()
        print("--- 데이터베이스 초기화 완료: 모든 테이블이 준비되었습니다. ---")

    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
    finally:
        conn.close()

NATIONALITY_MAP = {
    "KOR": {"ko": "대한민국", "en": "South Korea"},
    "USA": {"ko": "미국",     "en": "United States"},
    "JPN": {"ko": "일본",     "en": "Japan"},
    "CHN": {"ko": "중국",     "en": "China"},
    "DEU": {"ko": "독일",     "en": "Germany"},
    "GBR": {"ko": "영국",     "en": "United Kingdom"},
    "FRA": {"ko": "프랑스",   "en": "France"},
    "SGP": {"ko": "싱가포르", "en": "Singapore"},
    "CAN": {"ko": "캐나다",   "en": "Canada"},
    "IND": {"ko": "인도",     "en": "India"},
}
        
INVOICE_STATUS = {
    0: {"ko": "발행 전", "en": "Draft"},
    1: {"ko": "발행 완료", "en": "Issued"},
    2: {"ko": "입금 완료", "en": "Paid"},
    3: {"ko": "발송 완료", "en": "Shipped"},
    4: {"ko": "취소됨",     "en": "Cancelled"},
    5: {"ko": "반품 처리", "en": "Returned"},
}

def get_nationality_label(code: str, lang: str = "ko") -> str:
    return NATIONALITY_MAP.get(code.upper(), {}).get(lang, "알 수 없음")

def get_status_label(status: int, lang: str = "ko") -> str:
    return INVOICE_STATUS.get(status, {}).get(lang, "알 수 없음")        

if __name__ == '__main__':
    print("database.py가 직접 실행되었습니다. 데이터베이스 초기화를 진행합니다.")
    initialize_database()
