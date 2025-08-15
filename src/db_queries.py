# db_queries.py

import sqlite3
from config import DB_PATH

def _dict_factory(cursor, row):
    """
    DB 조회 결과를 사용하기 편한 dict 형태로 변환합니다.
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# --------------------------------------------------------------------
# 고급 조회 함수 (여러 테이블 JOIN 및 분석용)
# --------------------------------------------------------------------

def get_tasks_by_company_name(company_name: str) -> list:
    """
    특정 회사 이름으로 해당 회사의 모든 Task 기록을 시간순으로 조회합니다.
    - 여러 테이블을 JOIN하여 ID 대신 실제 이름을 보여줍니다.
    
    Args:
        company_name (str): 조회할 회사의 이름.
        
    Returns:
        list: 각 Task 정보를 담은 사전(dict)의 리스트. 정보가 없으면 빈 리스트.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _dict_factory # 조회 결과를 dict로 받기 위한 설정
    c = conn.cursor()
    
    try:
        # 먼저 회사 이름으로 company_id를 찾습니다.
        c.execute("SELECT company_id FROM Companies WHERE company_name = ?", (company_name,))
        company_result = c.fetchone()
        
        if not company_result:
            print(f"정보: '{company_name}' 회사를 찾을 수 없습니다.")
            return []
            
        company_id = company_result['company_id']
        
        # Tasks 테이블을 중심으로 Users, Contacts 테이블을 LEFT JOIN 합니다.
        # LEFT JOIN: 담당자(Contact)가 지정되지 않은 Task도 결과에 포함시키기 위함입니다.
        sql = """
            SELECT
                T.task_id,
                T.action_date,
                T.agenda,
                T.action_item,
                T.due_date,
                T.task_status,
                U.username AS user_name,
                C.contact_name
            FROM 
                Tasks T
            JOIN 
                Users U ON T.user_id = U.user_id
            LEFT JOIN 
                Contacts C ON T.contact_id = C.contact_id
            WHERE 
                T.company_id = ?
            ORDER BY 
                T.action_date DESC
        """
        c.execute(sql, (company_id,))
        tasks = c.fetchall()
        return tasks
        
    finally:
        conn.close()

def get_all_companies_summary() -> list:
    """
    모든 회사의 목록과 각 회사에 연결된 매출, 진행중인 Task 수, 프로젝트 수를 함께 조회합니다.
    
    Returns:
        list: 각 회사 정보를 담은 사전(dict)의 리스트.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _dict_factory
    c = conn.cursor()
    
    try:
        # 서브쿼리를 사용하여 각 회사별 통계를 계산합니다.
        sql = """
            SELECT
                C.company_id,
                C.company_name,
                C.website,
                COALESCE((SELECT SUM(I.total_amount) 
                         FROM Invoices I 
                         WHERE I.company_id = C.company_id AND I.status = 2), 0) AS total_revenue,
                (SELECT COUNT(task_id) 
                 FROM Tasks 
                 WHERE company_id = C.company_id AND task_status = 0) AS active_tasks_count,
                (SELECT COUNT(project_id) 
                 FROM Projects 
                 WHERE company_id = C.company_id AND status = 'active') AS active_projects_count
            FROM
                Companies C
            ORDER BY
                C.company_name ASC
        """
        c.execute(sql)
        companies = c.fetchall()
        return companies
    finally:
        conn.close()

# --------------------------------------------------------------------
# 기본적인 전체 테이블 조회 함수 (디버깅 및 기본 UI 구성용)
# --------------------------------------------------------------------

def get_contacts_by_company_name(company_name: str) -> list:
    """
    특정 회사의 모든 담당자 목록을 조회합니다.
    
    Args:
        company_name (str): 조회할 회사의 이름.
        
    Returns:
        list: 담당자 정보를 담은 사전(dict)의 리스트.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _dict_factory
    c = conn.cursor()
    
    try:
        sql = """
            SELECT 
                C.contact_id,
                C.contact_name,
                C.position,
                C.email,
                C.phone,
                CO.company_name
            FROM 
                Contacts C
            JOIN 
                Companies CO ON C.company_id = CO.company_id
            WHERE 
                CO.company_name = ?
            ORDER BY 
                C.contact_name ASC
        """
        c.execute(sql, (company_name,))
        return c.fetchall()
    finally:
        conn.close()

def get_projects_by_company_name(company_name: str) -> list:
    """
    특정 회사의 모든 프로젝트 목록을 조회합니다.
    
    Args:
        company_name (str): 조회할 회사의 이름.
        
    Returns:
        list: 프로젝트 정보를 담은 사전(dict)의 리스트.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _dict_factory
    c = conn.cursor()
    
    try:
        sql = """
            SELECT 
                P.project_id,
                P.project_name,
                P.start_date,
                P.end_date,
                P.project_status,
                P.budget,
                CO.company_name
            FROM 
                Projects P
            JOIN 
                Companies CO ON P.company_id = CO.company_id
            WHERE 
                CO.company_name = ?
            ORDER BY 
                P.start_date DESC
        """
        c.execute(sql, (company_name,))
        return c.fetchall()
    finally:
        conn.close()

def get_project_details_with_participants(project_id: int) -> dict:
    """
    특정 프로젝트의 상세 정보와 참여자 목록을 조회합니다.
    
    Args:
        project_id (int): 조회할 프로젝트의 ID.
        
    Returns:
        dict: 프로젝트 정보와 참여자 목록을 포함한 사전.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _dict_factory
    c = conn.cursor()
    
    try:
        # 프로젝트 기본 정보 조회
        project_sql = """
            SELECT 
                P.*,
                CO.company_name
            FROM 
                Projects P
            JOIN 
                Companies CO ON P.company_id = CO.company_id
            WHERE 
                P.project_id = ?
        """
        c.execute(project_sql, (project_id,))
        project_info = c.fetchone()
        
        if not project_info:
            return {}
        
        # 프로젝트 참여자 조회
        participants_sql = """
            SELECT 
                PP.participant_id,
                PP.role,
                U.username,
                U.email
            FROM 
                Project_Participants PP
            JOIN 
                Users U ON PP.user_id = U.user_id
            WHERE 
                PP.project_id = ?
            ORDER BY 
                PP.role ASC
        """
        c.execute(participants_sql, (project_id,))
        participants = c.fetchall()
        
        return {
            'project_info': project_info,
            'participants': participants
        }
    finally:
        conn.close()

def get_invoice_details_with_items(invoice_id: int) -> dict:
    """
    특정 인보이스의 상세 정보와 항목 목록을 조회합니다.
    
    Args:
        invoice_id (int): 조회할 인보이스의 ID.
        
    Returns:
        dict: 인보이스 정보와 항목 목록을 포함한 사전.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _dict_factory
    c = conn.cursor()
    
    try:
        # 인보이스 기본 정보 조회
        invoice_sql = """
            SELECT 
                I.*,
                CO.company_name
            FROM 
                Invoices I
            JOIN 
                Companies CO ON I.company_id = CO.company_id
            WHERE 
                I.invoice_id = ?
        """
        c.execute(invoice_sql, (invoice_id,))
        invoice_info = c.fetchone()
        
        if not invoice_info:
            return {}
        
        # 인보이스 항목 조회
        items_sql = """
            SELECT 
                II.*,
                P.product_name
            FROM 
                Invoice_Items II
            LEFT JOIN 
                Products P ON II.product_id = P.product_id
            WHERE 
                II.invoice_id = ?
            ORDER BY 
                II.item_id ASC
        """
        c.execute(items_sql, (invoice_id,))
        items = c.fetchall()
        
        return {
            'invoice_info': invoice_info,
            'items': items
        }
    finally:
        conn.close()

def get_tasks_by_date_range(start_date: str, end_date: str) -> list:
    """
    특정 기간의 Task 목록을 조회합니다.
    
    Args:
        start_date (str): 시작일 (YYYY-MM-DD 형식).
        end_date (str): 종료일 (YYYY-MM-DD 형식).
        
    Returns:
        list: Task 정보를 담은 사전(dict)의 리스트.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _dict_factory
    c = conn.cursor()
    
    try:
        sql = """
            SELECT
                T.task_id,
                T.action_date,
                T.agenda,
                T.action_item,
                T.due_date,
                T.task_status,
                U.username AS user_name,
                CO.company_name,
                C.contact_name
            FROM 
                Tasks T
            JOIN 
                Users U ON T.user_id = U.user_id
            JOIN 
                Companies CO ON T.company_id = CO.company_id
            LEFT JOIN 
                Contacts C ON T.contact_id = C.contact_id
            WHERE 
                T.action_date BETWEEN ? AND ?
            ORDER BY 
                T.action_date DESC
        """
        c.execute(sql, (start_date, end_date))
        return c.fetchall()
    finally:
        conn.close()

def get_tasks_by_user(user_id: int) -> list:
    """
    특정 사용자의 모든 Task 목록을 조회합니다.
    
    Args:
        user_id (int): 조회할 사용자의 ID.
        
    Returns:
        list: Task 정보를 담은 사전(dict)의 리스트.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _dict_factory
    c = conn.cursor()
    
    try:
        sql = """
            SELECT
                T.task_id,
                T.action_date,
                T.agenda,
                T.action_item,
                T.due_date,
                T.task_status,
                U.username AS user_name,
                CO.company_name,
                C.contact_name
            FROM 
                Tasks T
            JOIN 
                Users U ON T.user_id = U.user_id
            JOIN 
                Companies CO ON T.company_id = CO.company_id
            LEFT JOIN 
                Contacts C ON T.contact_id = C.contact_id
            WHERE 
                T.user_id = ?
            ORDER BY 
                T.action_date DESC
        """
        c.execute(sql, (user_id,))
        return c.fetchall()
    finally:
        conn.close()

def get_incomplete_tasks() -> list:
    """
    미완료 상태의 모든 Task 목록을 조회합니다.
    
    Returns:
        list: 미완료 Task 정보를 담은 사전(dict)의 리스트.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _dict_factory
    c = conn.cursor()
    
    try:
        sql = """
            SELECT
                T.task_id,
                T.action_date,
                T.agenda,
                T.action_item,
                T.due_date,
                T.task_status,
                T.task_type,
                T.priority,
                U.username AS user_name,
                CO.company_name,
                C.contact_name
            FROM 
                Tasks T
            JOIN 
                Users U ON T.user_id = U.user_id
            JOIN 
                Companies CO ON T.company_id = CO.company_id
            LEFT JOIN 
                Contacts C ON T.contact_id = C.contact_id
            WHERE 
                T.task_status = 0
            ORDER BY 
                T.due_date ASC, T.action_date DESC
        """
        c.execute(sql)
        return c.fetchall()
    finally:
        conn.close()

def search_contacts(search_term: str) -> list:
    """
    담당자 이름, 이메일, 전화번호로 검색합니다.
    
    Args:
        search_term (str): 검색어.
        
    Returns:
        list: 검색된 담당자 정보를 담은 사전(dict)의 리스트.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _dict_factory
    c = conn.cursor()
    
    try:
        sql = """
            SELECT 
                C.contact_id,
                C.contact_name,
                C.position,
                C.email,
                C.phone,
                CO.company_name
            FROM 
                Contacts C
            JOIN 
                Companies CO ON C.company_id = CO.company_id
            WHERE 
                C.contact_name LIKE ? OR
                C.email LIKE ? OR
                C.phone LIKE ?
            ORDER BY 
                C.contact_name ASC
        """
        search_pattern = f"%{search_term}%"
        c.execute(sql, (search_pattern, search_pattern, search_pattern))
        return c.fetchall()
    finally:
        conn.close()

def get_all_from_table(table_name: str) -> list:
    """
    지정된 테이블의 모든 데이터를 조회합니다.
    Args:
        table_name (str): 조회할 테이블 이름.
    Returns:
        list: 해당 테이블의 모든 레코드를 담은 사전(dict)의 리스트.
    """
    # SQL 인젝션 공격을 막기 위해 허용된 테이블 이름 목록을 확인하는 것이 좋습니다.
    allowed_tables = [
        'Users', 'Companies', 'Contacts', 'Products', 
        'Projects', 'Invoices', 'Tasks', 'Invoice_Items', 'Project_Participants'
    ]
    if table_name not in allowed_tables:
        raise ValueError(f"허용되지 않은 테이블 이름입니다: {table_name}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _dict_factory
    c = conn.cursor()
    
    try:
        # f-string을 사용하지만, 위에서 테이블 이름을 검증했으므로 안전합니다.
        c.execute(f"SELECT * FROM {table_name}")
        return c.fetchall()
    finally:
        conn.close()


# --- 이 파일을 직접 실행했을 때 테스트할 수 있는 코드 ---
if __name__ == '__main__':
    # 테스트를 위해 db_operations를 실행하여 데이터가 미리 입력되어 있어야 합니다.
    from pprint import pprint
    
    print("\n" + "="*50)
    print("=== '모빌린트' 회사의 모든 활동 내역 조회 (고급 기능) ===")
    print("="*50)
    tasks = get_tasks_by_company_name("모빌린트")
    if tasks:
        for task in tasks:
            print(f"[{task['action_date']}] {task['agenda']} (담당자: {task['contact_name'] or 'N/A'}, 담당직원: {task['user_name']}) -> Status: {task['task_status']}")
    else:
        print("-> 해당 회사의 Task 데이터가 없습니다. db_operations.py의 예시 코드를 먼저 실행해주세요.")
    
    print("\n" + "="*50)
    print("=== 전체 회사 목록 요약 (고급 기능) ===")
    print("="*50)
    companies = get_all_companies_summary()
    if companies:
        for company in companies:
            print(f"- {company['company_name']} (매출: {company['total_revenue']}, 진행중 Task: {company['active_tasks_count']}, 활성 프로젝트: {company['active_projects_count']})")

    print("\n" + "="*50)
    print("=== 'Contacts' 테이블 전체 조회 (기본 기능) ===")
    print("="*50)
    all_contacts = get_all_from_table('Contacts')
    pprint(all_contacts)