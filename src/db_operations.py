import sqlite3
from config import DB_PATH # config 파일에서 DB 경로를 가져옴


# --------------------------------------------------------------------
# 내부 헬퍼 함수 (Internal Helper Functions)
# - 이 함수들은 DB 연결/종료나 commit을 직접 수행하지 않습니다.
# - 상위 트랜잭션 함수로부터 cursor 객체를 받아 작업만 처리합니다.
# --------------------------------------------------------------------

def get_or_create_company(c: sqlite3.Cursor, company_name: str) -> int:
    """[내부용] 회사 이름을 기반으로 ID를 찾거나 생성합니다. cursor를 인자로 받습니다."""
    c.execute("SELECT company_id FROM Companies WHERE company_name = ?", (company_name,))
    result = c.fetchone()
    
    if result:
        # 회사가 존재하면 기존 ID 반환
        return result[0]
    else:
        # 회사가 없으면 새로 추가하고 새 ID 반환
        c.execute("INSERT INTO Companies (company_name) VALUES (?)", (company_name,))
        return c.lastrowid

def get_or_create_contact(c: sqlite3.Cursor, company_id: int, contact_name: str) -> int | None:
    """[내부용] 담당자 이름을 기반으로 ID를 찾거나 생성합니다. cursor를 인자로 받습니다."""
    if not contact_name:
        return None # 담당자 이름이 없으면 0 대신 None을 반환하는 것이 더 안전합니다.

    c.execute("SELECT contact_id FROM Contacts WHERE company_id = ? AND contact_name = ?", (company_id, contact_name))
    result = c.fetchone()

    if result:
        # 담당자가 존재하면 기존 ID 반환
        return result[0]
    else:
        # 담당자가 없으면 새로 추가하고 새 ID 반환
        c.execute("INSERT INTO Contacts (company_id, contact_name) VALUES (?, ?)", (company_id, contact_name))
        return c.lastrowid

# --------------------------------------------------------------------
# Main Transactional Function (사용자가 호출할 함수)
# - 이 함수가 DB 연결과 트랜잭션을 책임집니다.
# --------------------------------------------------------------------

def add_task_transactional(
    user_id: int, 
    company_name: str, 
    action_date: str, 
    contact_name: str = None, 
    agenda: str = None, 
    action_item: str = None, 
    due_date: str = None, 
    task_status: str = 'To-Do',
    project_id: int = None
) -> int | None:
    """
    하나의 'Task' 입력을 위한 모든 DB 작업을 단일 트랜잭션으로 처리합니다.
    - 회사/담당자 생성, Task 생성이 모두 성공하거나 하나라도 실패하면 모두 취소됩니다.
    
    Returns:
        int | None: 성공 시 새로운 task_id, 실패 시 None을 반환합니다.
    """
    conn = None  # finally 블록에서 사용하기 위해 미리 선언
    try:
        # 1. 데이터베이스 연결
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        print("--- 트랜잭션 시작 ---")

        # 2. 회사 ID 확보 (내부 함수 호출)
        company_id = get_or_create_company(c, company_name)
        print(f"회사 처리 완료: '{company_name}' (ID: {company_id})")

        # 3. 담당자 ID 확보 (내부 함수 호출)
        contact_id = get_or_create_contact(c, company_id, contact_name)
        if contact_name:
            print(f"담당자 처리 완료: '{contact_name}' (ID: {contact_id})")

        # 4. 최종 Task 정보 저장
        print("최종 Task 등록 시도...")
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
        new_task_id = c.lastrowid

        # 5. 모든 작업이 성공했을 때만 DB에 최종 반영 (Commit)
        conn.commit()
        print(f"--- 트랜잭션 성공 ---")
        print(f"-> Task 등록 완료! (신규 Task ID: {new_task_id})")
        
        return new_task_id

    except Exception as e:
        print(f"!!! 오류 발생: 트랜잭션을 롤백합니다. !!!")
        print(f"오류 내용: {e}")
        # 6. 하나라도 오류가 발생하면 모든 변경사항을 되돌림 (Rollback)
        if conn:
            conn.rollback()
        return None # 실패 시 None 반환

    finally:
        # 7. 성공/실패 여부와 관계없이 항상 DB 연결을 닫음
        if conn:
            conn.close()
            print("--- 데이터베이스 연결 종료 ---")


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
def add_invoice(
    project_id: int,
    company_id: int,
    contact_id: int,
    user_id: int,
    issue_date: str,
    due_date: str = None,
    total_amount: float = None,
    status: str = '발행 대기'
) -> int:
    """Invoices 테이블에 새로운 인보이스를 추가합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            """INSERT INTO Invoices 
               (project_id, company_id, contact_id, user_id, issue_date, due_date, total_amount, status) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, company_id, contact_id, user_id, issue_date, due_date, total_amount, status)
        )
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()

def add_invoice_item(
    invoice_id: int,
    product_id: int,
    quantity: int,
    unit_price_at_sale: float,
    discount_rate: float = 0
) -> int:
    """Invoice_Items 테이블에 새로운 인보이스 항목을 추가합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # 할인율을 적용한 단위 가격 계산
        discounted_unit_price = unit_price_at_sale * (1 - discount_rate / 100)
        # 소계 계산
        subtotal = discounted_unit_price * quantity
        
        c.execute(
            """INSERT INTO Invoice_Items 
               (invoice_id, product_id, quantity, unit_price_at_sale, discount_rate, subtotal) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (invoice_id, product_id, quantity, unit_price_at_sale, discount_rate, subtotal)
        )
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()

def add_invoice_with_items_transactional(
    project_id: int,
    company_id: int,
    contact_id: int,
    user_id: int,
    issue_date: str,
    items: list,  # [(product_id, quantity, unit_price, discount_rate), ...]
    due_date: str = None,
    status: str = '발행 대기'
) -> int | None:
    """
    인보이스와 인보이스 항목들을 단일 트랜잭션으로 처리합니다.
    - 인보이스 생성과 모든 항목 추가가 모두 성공하거나 하나라도 실패하면 모두 취소됩니다.
    
    Args:
        items: 인보이스 항목들의 리스트. 각 항목은 (product_id, quantity, unit_price, discount_rate) 튜플
    Returns:
        int | None: 성공 시 새로운 invoice_id, 실패 시 None을 반환합니다.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        print("--- 인보이스 트랜잭션 시작 ---")

        # 1. 인보이스 생성
        total_amount = 0
        for product_id, quantity, unit_price, discount_rate in items:
            discounted_unit_price = unit_price * (1 - discount_rate / 100)
            subtotal = discounted_unit_price * quantity
            total_amount += subtotal

        c.execute(
            """INSERT INTO Invoices 
               (project_id, company_id, contact_id, user_id, issue_date, due_date, total_amount, status) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, company_id, contact_id, user_id, issue_date, due_date, total_amount, status)
        )
        new_invoice_id = c.lastrowid
        print(f"인보이스 생성 완료: ID {new_invoice_id}")

        # 2. 인보이스 항목들 추가
        for product_id, quantity, unit_price, discount_rate in items:
            discounted_unit_price = unit_price * (1 - discount_rate / 100)
            subtotal = discounted_unit_price * quantity
            
            c.execute(
                """INSERT INTO Invoice_Items 
                   (invoice_id, product_id, quantity, unit_price_at_sale, discount_rate, subtotal) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (new_invoice_id, product_id, quantity, unit_price, discount_rate, subtotal)
            )
            print(f"항목 추가 완료: 상품 ID {product_id}, 수량 {quantity}, 소계 {subtotal}")

        conn.commit()
        print(f"--- 인보이스 트랜잭션 성공 ---")
        print(f"-> 인보이스 등록 완료! (신규 Invoice ID: {new_invoice_id})")
        print(f"-> 총 금액: {total_amount}")
        
        return new_invoice_id

    except Exception as e:
        print(f"!!! 오류 발생: 트랜잭션을 롤백합니다. !!!")
        print(f"오류 내용: {e}")
        if conn:
            conn.rollback()
        return None

    finally:
        if conn:
            conn.close()
            print("--- 데이터베이스 연결 종료 ---")



'''

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
        return None

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
'''

# Update
def update_tasks_in_batch(tasks_to_update: list[dict]) -> bool:
    """
    여러 Task를 한 번에 업데이트합니다. (배치 업데이트)
    [{'task_id': id, 'column_to_update': new_value}, ...] 형식의 리스트를 받습니다.

    Args:
        tasks_to_update (list[dict]): 각 dict는 task_id와 변경할 컬럼 및 값을 포함해야 합니다.
                                     예: [{'task_id': 5, 'agenda': '회의록 오타 수정'}]
    
    Returns:
        bool: 작업 성공 여부
    """
    if not tasks_to_update:
        print("ℹ️ 업데이트할 Task가 없습니다.")
        return True

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        print(f"--- Task 배치 업데이트 트랜잭션 시작 ({len(tasks_to_update)}개 항목) ---")

        for task_data in tasks_to_update:
            # task_id가 없으면 해당 항목은 건너뜀
            if 'task_id' not in task_data:
                print(f"⚠️ 경고: 'task_id'가 없는 데이터가 있어 건너뜁니다. -> {task_data}")
                continue
                
            task_id = task_data.pop('task_id')
            
            # 업데이트할 필드가 없는 경우 건너뜁니다.
            if not task_data:
                continue

            # 동적으로 SET 절 생성 (예: "agenda = ?, action_item = ?")
            set_clause = ", ".join([f"{key} = ?" for key in task_data.keys()])
            params = list(task_data.values())
            params.append(task_id)

            sql = f"UPDATE Tasks SET {set_clause} WHERE task_id = ?"
            c.execute(sql, tuple(params))
            print(f"  - Task ID {task_id} 업데이트 준비 완료.")

        conn.commit()
        print("✅ 트랜잭션 성공: 모든 Task가 업데이트 되었습니다.")
        return True

    except Exception as e:
        print(f"🚨 오류 발생: 트랜잭션을 롤백합니다. !!!\n오류 내용: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
            
def update_company_name(company_id: int, new_name: str) -> bool:
    """
    지정된 ID의 회사 이름을 변경합니다.

    Args:
        company_id (int): 수정할 회사의 ID.
        new_name (str): 새로운 회사 이름.

    Returns:
        bool: 작업 성공 여부.
    """
    if not new_name or not isinstance(new_name, str):
        print("🚨 오류: 새로운 회사 이름은 비어있지 않은 문자열이어야 합니다.")
        return False

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        sql = "UPDATE Companies SET company_name = ? WHERE company_id = ?"
        c.execute(sql, (new_name, company_id))

        # rowcount가 0이면, 해당 ID의 회사가 없다는 의미
        if c.rowcount == 0:
            print(f"⚠️ 경고: ID {company_id}에 해당하는 회사가 존재하지 않습니다.")
            return False

        conn.commit()
        print(f"✅ 회사 ID {company_id}의 이름이 '{new_name}'(으)로 변경되었습니다.")
        return True

    except Exception as e:
        print(f"🚨 오류 발생: 회사 이름 변경에 실패했습니다.\n오류 내용: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def merge_companies(source_company_id: int, target_company_id: int) -> bool:
    """
    중복된 회사 데이터를 하나로 합칩니다. (source -> target)
    관련된 Contacts, Tasks, Projects의 소속이 모두 target으로 변경된 후 source는 삭제됩니다.

    Args:
        source_company_id (int): 흡수되어 사라질 회사의 ID.
        target_company_id (int): 기준으로 남을 회사의 ID.

    Returns:
        bool: 작업 성공 여부.
    """
    if source_company_id == target_company_id:
        print("🚨 오류: 원본과 대상 회사의 ID가 동일합니다.")
        return False

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        print(f"--- 회사 병합 트랜잭션 시작: {source_company_id} -> {target_company_id} ---")

        # 1. 관련된 테이블의 company_id를 target_id로 UPDATE
        tables_to_update = ['Contacts', 'Tasks', 'Projects']
        for table in tables_to_update:
            print(f"  - {table} 테이블 업데이트 중...")
            c.execute(
                f"UPDATE {table} SET company_id = ? WHERE company_id = ?",
                (target_company_id, source_company_id)
            )
        
        # 2. 모든 관계가 이전된 후, 원본 source 데이터를 DELETE
        print(f"  - 원본 회사(ID: {source_company_id}) 삭제 중...")
        c.execute("DELETE FROM Companies WHERE company_id = ?", (source_company_id,))

        conn.commit()
        print("✅ 트랜잭션 성공: 회사 병합이 완료되었습니다.")
        return True

    except Exception as e:
        print(f"🚨 오류 발생: 트랜잭션을 롤백합니다. !!!\n오류 내용: {e}")
        if conn:
            conn.rollback()
        return False
    
    finally:
        if conn:
            conn.close()

            
def update_contact_info(contact_id: int, **kwargs) -> bool:
    """
    담당자 정보를 선택적으로 업데이트합니다.
    (예: update_contact_info(10, contact_name='김철수', contact_email='cskim@example.com'))

    Args:
        contact_id (int): 수정할 담당자의 ID.
        **kwargs: 변경할 컬럼과 값 (예: contact_name='이름', contact_phone='010-...')

    Returns:
        bool: 작업 성공 여부.
    """
    if not kwargs:
        print("ℹ️ 업데이트할 정보가 없습니다.")
        return True

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # 동적으로 SET 절 생성
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        params = list(kwargs.values())
        params.append(contact_id)

        sql = f"UPDATE Contacts SET {set_clause} WHERE contact_id = ?"
        c.execute(sql, tuple(params))

        if c.rowcount == 0:
            print(f"⚠️ 경고: ID {contact_id}에 해당하는 담당자가 존재하지 않습니다.")
            return False

        conn.commit()
        print(f"✅ 담당자 ID {contact_id}의 정보가 성공적으로 업데이트되었습니다.")
        return True
    
    except Exception as e:
        print(f"🚨 오류 발생: 담당자 정보 업데이트에 실패했습니다.\n오류 내용: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
            
def merge_contacts(source_contact_id: int, target_contact_id: int) -> bool:
    """
    중복된 담당자 데이터를 하나로 합칩니다. (source -> target)

    Args:
        source_contact_id (int): 흡수되어 사라질 담당자의 ID.
        target_contact_id (int): 기준으로 남을 담당자의 ID.

    Returns:
        bool: 작업 성공 여부.
    """
    if source_contact_id == target_contact_id:
        print("🚨 오류: 원본과 대상 담당자의 ID가 동일합니다.")
        return False

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        print(f"--- 담당자 병합 트랜잭션 시작: {source_contact_id} -> {target_contact_id} ---")

        # 1. Tasks 테이블의 담당자 ID 변경
        print("  - Tasks 테이블 업데이트 중...")
        c.execute(
            "UPDATE Tasks SET contact_id = ? WHERE contact_id = ?",
            (target_contact_id, source_contact_id)
        )
        
        # 2. Project_Participants 테이블 처리
        # UNIQUE 제약조건(project_id, contact_id) 충돌 가능성이 있으므로,
        # 충돌 시 원본(source) 참여 기록을 삭제하는 방식으로 처리합니다.
        print("  - 프로젝트 참여 정보 업데이트 중...")
        try:
            c.execute(
                "UPDATE Project_Participants SET contact_id = ? WHERE contact_id = ?",
                (target_contact_id, source_contact_id)
            )
        except sqlite3.IntegrityError:
            print("  ⚠️ 경고: 대상 담당자가 이미 참여중인 프로젝트가 있어, 중복되는 원본 참여 기록을 삭제합니다.")
            c.execute(
                "DELETE FROM Project_Participants WHERE contact_id = ?",
                (source_contact_id,)
            )

        # 3. 원본 담당자 데이터 삭제
        print(f"  - 원본 담당자(ID: {source_contact_id}) 삭제 중...")
        c.execute("DELETE FROM Contacts WHERE contact_id = ?", (source_contact_id,))

        conn.commit()
        print("✅ 트랜잭션 성공: 담당자 병합이 완료되었습니다.")
        return True

    except Exception as e:
        print(f"🚨 오류 발생: 트랜잭션을 롤백합니다. !!!\n오류 내용: {e}")
        if conn:
            conn.rollback()
        return False
    
    finally:
        if conn:
            conn.close()
            
def update_project_details(project_id: int, **kwargs) -> bool:
    """
    프로젝트 정보를 선택적으로 업데이트합니다.
    (예: update_project_details(3, status='완료', description='최종 보고서 제출 완료'))

    Args:
        project_id (int): 수정할 프로젝트의 ID.
        **kwargs: 변경할 컬럼과 값 (project_name, description, status, start_date, end_date 등)

    Returns:
        bool: 작업 성공 여부.
    """
    if not kwargs:
        print("ℹ️ 업데이트할 정보가 없습니다.")
        return True

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        params = list(kwargs.values())
        params.append(project_id)

        sql = f"UPDATE Projects SET {set_clause} WHERE project_id = ?"
        c.execute(sql, tuple(params))

        if c.rowcount == 0:
            print(f"⚠️ 경고: ID {project_id}에 해당하는 프로젝트가 존재하지 않습니다.")
            return False

        conn.commit()
        print(f"✅ 프로젝트 ID {project_id}의 정보가 성공적으로 업데이트되었습니다.")
        return True
    
    except Exception as e:
        print(f"🚨 오류 발생: 프로젝트 정보 업데이트에 실패했습니다.\n오류 내용: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
            
def merge_projects(source_project_id: int, target_project_id: int) -> bool:
    """
    중복된 프로젝트를 하나로 합칩니다. (source -> target)
    Source 프로젝트에 속한 모든 Task와 참여자 기록이 Target으로 이전됩니다.

    Args:
        source_project_id (int): 흡수되어 사라질 프로젝트의 ID.
        target_project_id (int): 기준으로 남을 프로젝트의 ID.

    Returns:
        bool: 작업 성공 여부.
    """
    if source_project_id == target_project_id:
        print("🚨 오류: 원본과 대상 프로젝트의 ID가 동일합니다.")
        return False

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        print(f"--- 프로젝트 병합 트랜잭션 시작: {source_project_id} -> {target_project_id} ---")

        # 1. Tasks 테이블의 프로젝트 ID 변경
        print("  - Tasks 테이블 업데이트 중...")
        c.execute(
            "UPDATE Tasks SET project_id = ? WHERE project_id = ?",
            (target_project_id, source_project_id)
        )
        
        # 2. Project_Participants 테이블 처리 (담당자 병합과 동일한 충돌 처리 로직)
        print("  - 참여자 정보 업데이트 중...")
        try:
            c.execute(
                "UPDATE Project_Participants SET project_id = ? WHERE project_id = ?",
                (target_project_id, source_project_id)
            )
        except sqlite3.IntegrityError:
            print("  ⚠️ 경고: 대상 프로젝트에 이미 참여중인 담당자가 있어, 중복되는 원본 참여 기록을 삭제합니다.")
            c.execute(
                "DELETE FROM Project_Participants WHERE project_id = ?",
                (source_project_id,)
            )

        # 3. 원본 프로젝트 데이터 삭제
        print(f"  - 원본 프로젝트(ID: {source_project_id}) 삭제 중...")
        c.execute("DELETE FROM Projects WHERE project_id = ?", (source_project_id,))

        conn.commit()
        print("✅ 트랜잭션 성공: 프로젝트 병합이 완료되었습니다.")
        return True

    except Exception as e:
        print(f"🚨 오류 발생: 트랜잭션을 롤백합니다. !!!\n오류 내용: {e}")
        if conn:
            conn.rollback()
        return False
    
    finally:
        if conn:
            conn.close()
