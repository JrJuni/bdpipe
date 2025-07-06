import sqlite3
from config import DB_PATH # config 파일에서 DB 경로를 가져옴

# --------------------------------------------------------------------
# Helper Functions (Get or Create)
# 이 함수들은 직접 호출되기보다, 주 입력 함수(add_task) 내부에서 사용됩니다.
# --------------------------------------------------------------------

def get_or_create_company(company_name: str) -> int:
    """
    회사 이름으로 company_id를 찾고, 없으면 새로 생성합니다.
    - 데이터 중복 방지를 위한 핵심 함수입니다.
    Args:
        company_name (str): 찾거나 생성할 회사의 이름.
    Returns:
        int: 해당 회사의 company_id.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # 1. 먼저 회사가 존재하는지 검색
        c.execute("SELECT company_id FROM Companies WHERE company_name = ?", (company_name,))
        result = c.fetchone()
        
        if result:
            # 2a. 회사가 존재하면, 해당 ID 반환
            print(f"기존 회사 정보 확인: '{company_name}' (ID: {result[0]})")
            return result[0]
        else:
            # 2b. 회사가 없으면, 새로 추가
            print(f"신규 회사 등록: '{company_name}'")
            c.execute("INSERT INTO Companies (company_name) VALUES (?)", (company_name,))
            conn.commit()
            new_id = c.lastrowid
            print(f"-> 등록 완료 (신규 ID: {new_id})")
            return new_id
    finally:
        conn.close()

def get_or_create_contact(company_id: int, contact_name: str) -> int:
    """
    회사 ID와 담당자 이름으로 contact_id를 찾고, 없으면 새로 생성합니다.
    Args:
        company_id (int): 담당자가 소속된 회사의 ID.
        contact_name (str): 찾거나 생성할 담당자의 이름.
    Returns:
        int: 해당 담당자의 contact_id.
    """
    # 담당자 이름이 제공되지 않은 경우, 처리를 건너뛰고 None을 반환
    if not contact_name:
        return 0

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # 1. 특정 회사에 해당 이름의 담당자가 있는지 검색
        c.execute("SELECT contact_id FROM Contacts WHERE company_id = ? AND contact_name = ?", (company_id, contact_name))
        result = c.fetchone()
        
        if result:
            # 2a. 담당자가 존재하면, 해당 ID 반환
            print(f"기존 담당자 정보 확인: '{contact_name}' (ID: {result[0]})")
            return result[0]
        else:
            # 2b. 담당자가 없으면, 새로 추가
            print(f"신규 담당자 등록: '{contact_name}'")
            c.execute("INSERT INTO Contacts (company_id, contact_name) VALUES (?, ?)", (company_id, contact_name))
            conn.commit()
            new_id = c.lastrowid
            print(f"-> 등록 완료 (신규 ID: {new_id})")
            return new_id
    finally:
        conn.close()

# --------------------------------------------------------------------
# Main Input Function (Action-Centric)
# 사용자가 주로 사용하게 될 핵심 데이터 입력 함수입니다.
# --------------------------------------------------------------------

def add_task(
    user_id: int, 
    company_name: str, 
    action_date: str, 
    contact_name: str = None, 
    agenda: str = None, 
    action_item: str = None, 
    due_date: str = None, 
    task_status: str = 'To-Do',
    project_id: int = None
    ) -> int:
    """
    하나의 'Task' 입력을 통해 회사, 담당자, 할 일 정보를 한 번에 처리합니다.
    - 사용자가 직접 호출하는 메인 함수입니다.
    - 내부적으로 get_or_create_company/contact를 호출하여 데이터를 정리합니다.
    Args:
        user_id (int): 작업을 수행한 유저의 ID (NOT NULL).
        company_name (str): 관련 회사의 이름 (NOT NULL).
        action_date (str): 활동 날짜 (예: 'YYYY-MM-DD') (NOT NULL).
        contact_name (str, optional): 관련 담당자의 이름. Defaults to None.
        agenda (str, optional): 논의 안건. Defaults to None.
        action_item (str, optional): 후속 조치 사항. Defaults to None.
        due_date (str, optional): 후속 조치 기한 (예: 'YYYY-MM-DD'). Defaults to None.
        task_status (str, optional): 업무 상태. Defaults to 'To-Do'.
        project_id (int, optional): 관련된 프로젝트 ID. Defaults to None.
    Returns:
        int: 새로 생성된 task_id.
    """
    # 1. 회사 ID 확보 (Get or Create)
    company_id = get_or_create_company(company_name)
    
    # 2. 담당자 ID 확보 (Get or Create)
    contact_id = get_or_create_contact(company_id, contact_name)
    
    # 3. Task 정보 최종 저장
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        print(f"\n--- 최종 Task 등록 시작 ---")
        sql = """
            INSERT INTO Tasks (
                user_id, company_id, contact_id, action_date, agenda, 
                action_item, due_date, task_status, project_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            user_id, company_id, contact_id, action_date, agenda, 
            action_item, due_date, task_status, project_id
        )
        c.execute(sql, params)
        conn.commit()
        new_task_id = c.lastrowid
        print(f"-> Task 등록 성공! (신규 Task ID: {new_task_id})")
        return new_task_id
    finally:
        conn.close()

# (기존의 get_or_create_company, get_or_create_contact, add_task 함수는 그대로 둡니다)

# --------------------------------------------------------------------
# 추가적인 데이터 입력 함수 (Direct Insert)
# --------------------------------------------------------------------

def add_user(username: str, password_hash: str, user_email: str = None) -> int:
    """Users 테이블에 새로운 사용자를 추가합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO Users (username, password_hash, user_email) VALUES (?, ?, ?)",
            (username, password_hash, user_email)
        )
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        print(f"오류: 사용자 이름 '{username}' 또는 이메일 '{user_email}'이 이미 존재합니다.")
        return None
    finally:
        conn.close()

def add_product(product_name: str, unit_price: float) -> int:
    """Products 테이블에 새로운 상품을 추가합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO Products (product_name, unit_price) VALUES (?, ?)",
            (product_name, unit_price)
        )
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        print(f"오류: 상품명 '{product_name}'이 이미 존재합니다.")
        return None
    finally:
        conn.close()

def add_project(company_id: int, project_name: str, **kwargs) -> int:
    """Projects 테이블에 새로운 프로젝트를 추가합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # 기본값 설정
        status = kwargs.get('status', '시작 전')
        description = kwargs.get('description')
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        c.execute(
            """INSERT INTO Projects 
               (company_id, project_name, description, status, start_date, end_date) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (company_id, project_name, description, status, start_date, end_date)
        )
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()

def add_project_participant(project_id: int, contact_id: int, role: str = None) -> bool:
    """Project_Participants (연결 테이블)에 프로젝트 참여자를 추가합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO Project_Participants (project_id, contact_id, role) VALUES (?, ?, ?)",
            (project_id, contact_id, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"오류: 해당 담당자(ID: {contact_id})는 이미 프로젝트(ID: {project_id})에 참여하고 있습니다.")
        return False
    finally:
        conn.close()

# (Invoice 및 Invoice_Items 관련 함수는 필요시 동일한 패턴으로 추가할 수 있습니다)

# --- 사용 예시 ---
# 이 파일이 직접 실행될 때 아래 코드가 동작하여 테스트를 돕습니다.
'''
if __name__ == '__main__':
    # 테스트를 위해 데이터베이스를 초기화합니다.
    from db_schema import initialize_database
    print("테스트를 위해 데이터베이스를 초기화합니다.")
    initialize_database()

    # 테스트를 위해 Users 테이블에 가상의 유저를 추가합니다.
    # 실제 애플리케이션에서는 회원가입/로그인 기능으로 처리됩니다.
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # UNIQUE 제약조건 때문에 이미 있으면 에러가 발생할 수 있으므로, 없을 때만 넣도록 처리
        c.execute("INSERT OR IGNORE INTO Users (user_id, username, password_hash) VALUES (?, ?, ?)", (1, 'test_user', 'hashed_password'))
        conn.commit()
    finally:
        conn.close()

    print("\n" + "="*50)
    print("=== 시나리오 1: 신규 회사, 신규 담당자와의 첫 미팅 기록 ===")
    print("="*50)
    add_task(
        user_id=1,
        company_name="모빌인트",
        contact_name="김철수",
        action_date="2025-07-07",
        agenda="신규 AI CRM 솔루션 도입 제안",
        action_item="제안서 및 견적서 전달",
        due_date="2025-07-14",
        task_status="진행 중"
    )

    print("\n" + "="*50)
    print("=== 시나리오 2: 기존 회사, 다른 담당자와의 후속 연락 ===")
    print("="*50)
    add_task(
        user_id=1,
        company_name="모빌인트",
        contact_name="이영희",
        action_date="2025-07-08",
        agenda="기술팀 실무 담당자 소개 및 Q&A",
        action_item="기술 사양서 전달",
        due_date="2025-07-10"
    )

    print("\n" + "="*50)
    print("=== 시나리오 3: 기존 회사 담당자와의 빠른 메모 (담당자 이름 생략) ===")
    print("="*50)
    add_task(
        user_id=1,
        company_name="모빌인트",
        action_date="2025-07-09",
        agenda="내부 아이디어 회의"
    )
'''