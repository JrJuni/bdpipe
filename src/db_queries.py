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
    모든 회사의 목록과 각 회사에 연결된 담당자 수, Task 수를 함께 조회합니다.
    
    Returns:
        list: 각 회사 정보를 담은 사전(dict)의 리스트.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _dict_factory
    c = conn.cursor()
    
    try:
        # 서브쿼리와 GROUP BY를 사용하여 각 회사별 통계를 계산합니다.
        sql = """
            SELECT
                C.company_id,
                C.company_name,
                C.website,
                (SELECT COUNT(contact_id) FROM Contacts WHERE company_id = C.company_id) AS contact_count,
                (SELECT COUNT(task_id) FROM Tasks WHERE company_id = C.company_id) AS task_count
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
            print(f"- {company['company_name']} (담당자 수: {company['contact_count']}, 활동 수: {company['task_count']})")

    print("\n" + "="*50)
    print("=== 'Contacts' 테이블 전체 조회 (기본 기능) ===")
    print("="*50)
    all_contacts = get_all_from_table('Contacts')
    pprint(all_contacts)