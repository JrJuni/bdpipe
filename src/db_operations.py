import sqlite3
from config import DB_PATH # config 파일에서 DB 경로를 가져옴
from typing import Optional, List, Dict

# --------------------------------------------------------------------
# Helper Functions (Get or Create relational links)
# --------------------------------------------------------------------
def get_or_create_company(cursor, company_name: str) -> int:
    cursor.execute("SELECT company_id FROM Companies WHERE company_name = ?", (company_name,))
    r = cursor.fetchone()
    if r:
        return r[0]
    cursor.execute("INSERT INTO Companies (company_name) VALUES (?)", (company_name,))
    return cursor.lastrowid

def get_or_create_contact(cursor, company_id: int, contact_name: str) -> int | None:
    if not contact_name:
        return None
    cursor.execute(
        "SELECT contact_id FROM Contacts WHERE company_id = ? AND contact_name = ?",
        (company_id, contact_name)
    )
    r = cursor.fetchone()
    if r:
        return r[0]
    cursor.execute(
        "INSERT INTO Contacts (company_id, contact_name) VALUES (?, ?)",
        (company_id, contact_name)
    )
    return cursor.lastrowid

def get_or_create_project(cursor, company_id: int, project_name: str) -> int | None:
    """
    company_id와 project_name 조합으로 프로젝트를 조회하고,
    없으면 최소 정보로 새로 생성한 뒤 project_id를 리턴합니다.
    """
    if not project_name:
        return None
    cursor.execute(
        "SELECT project_id FROM Projects WHERE company_id = ? AND project_name = ?",
        (company_id, project_name)
    )
    r = cursor.fetchone()
    if r:
        return r[0]
    cursor.execute(
        "INSERT INTO Projects (company_id, project_name) VALUES (?, ?)",
        (company_id, project_name)
    )
    return cursor.lastrowid

# --------------------------------------------------------------------
# Master Data CRUD
# --------------------------------------------------------------------
def add_user(username: str, password_hash: str, user_email: str = None, auth_level: int = 0) -> int:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO Users (username, password_hash, user_email, auth_level) VALUES (?, ?, ?, ?)",
            (username, password_hash, user_email, auth_level)
        )
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def update_user(user_id: int, username: str, password_hash: str, user_email: str) -> bool:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    try:
        c.execute("""
            UPDATE Users
               SET username = ?, password_hash = ?, user_email = ?, updated_at = CURRENT_TIMESTAMP
             WHERE user_id = ?
        """, (username, password_hash, user_email, user_id))
        conn.commit()
        return c.rowcount == 1
    finally:
        conn.close()

def add_company(company_name: str,
                employee_count: int = None,
                revenue: int = None,
                overview: str = None,
                website: str = None,
                nationality: str = None) -> int:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO Companies
            (company_name, employee_count, revenue, overview, website, nationality)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company_name, employee_count, revenue, overview, website, nationality))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def update_company(company_id: int,
                   company_name: str,
                   employee_count: int,
                   revenue: int,
                   overview: str,
                   website: str,
                   nationality: str) -> bool:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    try:
        c.execute("""
            UPDATE Companies
               SET company_name = ?, employee_count = ?, revenue = ?,
                   overview = ?, website = ?, nationality = ?,
                   updated_at = CURRENT_TIMESTAMP
             WHERE company_id = ?
        """, (company_name, employee_count, revenue, overview, website, nationality, company_id))
        conn.commit()
        return c.rowcount == 1
    finally:
        conn.close()

def add_contact(company_id: int,
                contact_name: str,
                department: str = None,
                position: str = None,
                email: str = None,
                phone: str = None,
                mobile_phone: str = None) -> int:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO Contacts
            (company_id, contact_name, department, position, email, phone, mobile_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (company_id, contact_name, department, position, email, phone, mobile_phone))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def update_contact(contact_id: int,
                   company_id: int,
                   contact_name: str,
                   department: str,
                   position: str,
                   email: str,
                   phone: str,
                   mobile_phone: str) -> bool:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    try:
        c.execute("""
            UPDATE Contacts
               SET company_id = ?, contact_name = ?, department = ?,
                   position = ?, email = ?, phone = ?, mobile_phone = ?,
                   updated_at = CURRENT_TIMESTAMP
             WHERE contact_id = ?
        """, (company_id, contact_name, department, position, email, phone, mobile_phone, contact_id))
        conn.commit()
        return c.rowcount == 1
    finally:
        conn.close()

def add_product(product_name: str,
                min_price: float = None,
                max_price: float = None) -> int:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO Products (product_name, min_price, max_price) VALUES (?, ?, ?)",
            (product_name, min_price, max_price)
        )
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def update_product(product_id: int,
                   product_name: str,
                   min_price: float,
                   max_price: float) -> bool:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    try:
        c.execute("""
            UPDATE Products
               SET product_name = ?, min_price = ?, max_price = ?,
                   updated_at = CURRENT_TIMESTAMP
             WHERE product_id = ?
        """, (product_name, min_price, max_price, product_id))
        conn.commit()
        return c.rowcount == 1
    finally:
        conn.close()

# --------------------------------------------------------------------
# Task CRUD
# --------------------------------------------------------------------
def add_task_transactional(
    user_id: int,
    company_name: str,
    action_date: str,
    contact_name: str = None,
    project_name: str = None,
    agenda: str = None,
    action_item: str = None,
    due_date: str = None,
    task_status: int = 0,
    task_type: str = 'contact',
    priority: int = 1,
    memo: str = None,
    invoice_id: int = None,
) -> int:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    try:
        comp_id = get_or_create_company(c, company_name)
        cont_id = get_or_create_contact(c, comp_id, contact_name)
        proj_id = get_or_create_project(c, comp_id, project_name)
        
        c.execute("""
            INSERT INTO Tasks
            (user_id, company_id, contact_id, project_id, invoice_id,
             action_date, agenda, action_item, due_date,
             task_status, task_type, priority, memo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, comp_id, cont_id, proj_id, invoice_id,
            action_date, agenda, action_item, due_date,
            task_status, task_type, priority, memo,
        ))
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()
        
ALLOWED_TASK_FIELDS = {
    "company_id","contact_id","project_id","invoice_id",
    "action_date","agenda","action_item","due_date",
    "task_status","task_type","priority","memo","is_deleted"
}

def update_task(task_id: int, **fields) -> bool:
    """
    Update one or more columns on a Task.
    - fields가 비어있으면 아무 작업도 하지 않고 False 반환
    - 성공 시 True, 실패/영향 row 없음 시 False
    """
    if not fields:
        return False

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        cols = ", ".join(f"{k}=?" for k in fields)
        vals = list(fields.values()) + [task_id]
        sql = f"""
            UPDATE Tasks
               SET {cols},
                   updated_at = CURRENT_TIMESTAMP
             WHERE task_id = ?
        """
        c.execute(sql, vals)
        conn.commit()
        return c.rowcount == 1
    finally:
        conn.close()

def delete_task(task_id: int, soft: bool = True) -> bool:
    """
    Task 삭제.
      soft=True  : is_deleted=1, updated_at 갱신
      soft=False : 레코드 완전 삭제
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        if soft:
            c.execute("""
                UPDATE Tasks
                   SET is_deleted     = 1,
                       updated_at     = CURRENT_TIMESTAMP
                 WHERE task_id = ?
            """, (task_id,))
        else:
            c.execute("DELETE FROM Tasks WHERE task_id = ?", (task_id,))
        conn.commit()
        return c.rowcount == 1
    finally:
        conn.close()

def get_task(task_id: int) -> Optional[Dict]:
    """
    단일 Task를 dict로 반환 (없으면 None).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM Tasks WHERE task_id = ?", (task_id,))
        row = c.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def list_tasks(include_deleted: bool = False) -> List[Dict]:
    """
    모든 Task 리스트를 반환.
    include_deleted=False일 때 is_deleted=0만 리턴.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        if include_deleted:
            c.execute("SELECT * FROM Tasks")
        else:
            c.execute("SELECT * FROM Tasks WHERE is_deleted = 0")
        return [dict(r) for r in c.fetchall()]
    finally:
        conn.close()

# --------------------------------------------------------------------
# Project Operations
# --------------------------------------------------------------------
def add_project(company_id: int,
                project_name: str,
                contact_id: int = None,
                description: str = None,
                application: str = None,
                ai_model: str = None,
                requirement: str = None,
                start_date: str = None,
                end_date: str = None,
                status: str = None,
                phase: int = 0,
                memo: str = None) -> int:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO Projects
            (company_id, project_name, contact_id, description,
             application, ai_model, requirement,
             start_date, end_date, status, phase, memo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, project_name, contact_id, description,
              application, ai_model, requirement,
              start_date, end_date, status, phase, memo))
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()

def link_task_to_project(task_id: int, project_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("UPDATE Tasks SET project_id = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ?",
              (project_id, task_id))
    conn.commit()
    success = c.rowcount == 1
    conn.close()
    return success

# --------------------------------------------------------------------
# Invoice Operations
# --------------------------------------------------------------------
def add_invoice(project_id: int,
                company_id: int,
                user_id: int,
                contact_id: int = None,
                issue_date: str = None,
                due_date: str = None,
                status: int = 0,
                total_amount: float = None) -> int:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO Invoices
            (project_id, company_id, contact_id, user_id,
             issue_date, due_date, status, total_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, company_id, contact_id, user_id,
              issue_date, due_date, status, total_amount))
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()

def add_invoice_item(invoice_id: int,
                     product_id: int,
                     quantity: int,
                     unit_price_at_sale: float) -> int:
    subtotal = quantity * unit_price_at_sale
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("""
        INSERT INTO Invoice_Items
        (invoice_id, product_id, quantity, unit_price_at_sale, subtotal)
        VALUES (?, ?, ?, ?, ?)
    """, (invoice_id, product_id, quantity, unit_price_at_sale, subtotal))
    conn.commit()
    last = c.lastrowid
    conn.close()
    return last

# --------------------------------------------------------------------
# Free Trial Operations
# --------------------------------------------------------------------
def add_free_trial(task_id: int,
                   project_id: int,
                   product_id: int,
                   start_date: str = None,
                   end_date: str = None) -> bool:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO Free_Trials
            (task_id, project_id, product_id, start_date, end_date)
            VALUES (?, ?, ?, ?, ?)
        """, (task_id, project_id, product_id, start_date, end_date))
        conn.commit()
        return True
    finally:
        conn.close()

# --------------------------------------------------------------------
# Tech Inquiry Operations
# --------------------------------------------------------------------
def add_tech_inquiry(task_id: int,
                     project_id: int = None,
                     product_id: int = None,
                     application: str = None,
                     ai_model: str = None,
                     is_resolved: int = 0) -> bool:
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO Tech_Inquiries
            (task_id, project_id, product_id, application, ai_model, is_resolved)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (task_id, project_id, product_id, application, ai_model, is_resolved))
        conn.commit()
        return True
    finally:
        conn.close()
