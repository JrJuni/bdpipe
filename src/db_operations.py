import sqlite3
import pandas as pd
from typing import Dict, List, Tuple, Any
from config import DB_PATH # config 파일에서 DB 경로를 가져옴


# ====================================================================
# 기본 엔티티 테이블 CRUD (Users, Companies, Contacts, Products)
# ====================================================================

# --------------------------------------------------------------------
# Users 테이블 CRUD
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

def update_user(user_id: int, **kwargs) -> bool:
    """사용자 정보를 업데이트합니다."""
    if not kwargs:
        print("ℹ️ 업데이트할 정보가 없습니다.")
        return True
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        params = list(kwargs.values()) + [user_id]
        
        c.execute(f"UPDATE Users SET {set_clause} WHERE user_id = ?", params)
        
        if c.rowcount == 0:
            print(f"⚠️ 경고: ID {user_id}에 해당하는 사용자가 존재하지 않습니다.")
            return False
            
        conn.commit()
        print(f"✅ 사용자 ID {user_id}의 정보가 성공적으로 업데이트되었습니다.")
        return True
    except Exception as e:
        print(f"🚨 오류 발생: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_user(user_id: int) -> bool:
    """사용자를 소프트 삭제합니다 (is_deleted = 1)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("UPDATE Users SET is_deleted = 1 WHERE user_id = ?", (user_id,))
        
        if c.rowcount == 0:
            print(f"⚠️ 경고: ID {user_id}에 해당하는 사용자가 존재하지 않습니다.")
            return False
            
        conn.commit()
        print(f"✅ 사용자 ID {user_id}가 삭제되었습니다.")
        return True
    except Exception as e:
        print(f"🚨 오류 발생: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# --------------------------------------------------------------------
# Companies 테이블 CRUD
# --------------------------------------------------------------------

def add_company(company_name: str, **kwargs) -> int:
    """Companies 테이블에 새로운 회사를 추가합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # 기본값 설정
        employee_count = kwargs.get('employee_count')
        revenue = kwargs.get('revenue')
        overview = kwargs.get('overview')
        website = kwargs.get('website')
        nationality = kwargs.get('nationality', 'KOR')  # 기본값: 한국
        
        c.execute(
            """INSERT INTO Companies 
               (company_name, employee_count, revenue, overview, website, nationality) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (company_name, employee_count, revenue, overview, website, nationality)
        )
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        print(f"오류: 회사명 '{company_name}'이 이미 존재합니다.")
        return None
    finally:
        conn.close()

def update_company(company_id: int, **kwargs) -> bool:
    """회사 정보를 업데이트합니다."""
    if not kwargs:
        print("ℹ️ 업데이트할 정보가 없습니다.")
        return True
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        params = list(kwargs.values()) + [company_id]
        
        c.execute(f"UPDATE Companies SET {set_clause} WHERE company_id = ?", params)
        
        if c.rowcount == 0:
            print(f"⚠️ 경고: ID {company_id}에 해당하는 회사가 존재하지 않습니다.")
            return False
            
        conn.commit()
        print(f"✅ 회사 ID {company_id}의 정보가 성공적으로 업데이트되었습니다.")
        return True
    except Exception as e:
        print(f"🚨 오류 발생: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_company(company_id: int) -> bool:
    """회사를 소프트 삭제합니다 (is_deleted = 1)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("UPDATE Companies SET is_deleted = 1 WHERE company_id = ?", (company_id,))
        
        if c.rowcount == 0:
            print(f"⚠️ 경고: ID {company_id}에 해당하는 회사가 존재하지 않습니다.")
            return False
            
        conn.commit()
        print(f"✅ 회사 ID {company_id}가 삭제되었습니다.")
        return True
    except Exception as e:
        print(f"🚨 오류 발생: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def merge_companies(source_company_id: int, target_company_id: int) -> bool:
    """
    중복된 회사 데이터를 하나로 합칩니다. (source -> target)
    관련된 Contacts, Tasks, Projects의 소속이 모두 target으로 변경된 후 source는 삭제됩니다.
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

# --------------------------------------------------------------------
# Contacts 테이블 CRUD
# --------------------------------------------------------------------

def add_contact(company_id: int, contact_name: str, **kwargs) -> int:
    """Contacts 테이블에 새로운 연락처를 추가합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        department = kwargs.get('department')
        position = kwargs.get('position')
        email = kwargs.get('email')
        phone = kwargs.get('phone')
        mobile_phone = kwargs.get('mobile_phone')
        
        c.execute(
            """INSERT INTO Contacts 
               (company_id, contact_name, department, position, email, phone, mobile_phone) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (company_id, contact_name, department, position, email, phone, mobile_phone)
        )
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        print(f"오류: 이메일 '{email}'이 이미 존재합니다.")
        return None
    finally:
        conn.close()

def update_contact(contact_id: int, **kwargs) -> bool:
    """연락처 정보를 업데이트합니다."""
    if not kwargs:
        print("ℹ️ 업데이트할 정보가 없습니다.")
        return True
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        params = list(kwargs.values()) + [contact_id]
        
        c.execute(f"UPDATE Contacts SET {set_clause} WHERE contact_id = ?", params)
        
        if c.rowcount == 0:
            print(f"⚠️ 경고: ID {contact_id}에 해당하는 연락처가 존재하지 않습니다.")
            return False
            
        conn.commit()
        print(f"✅ 연락처 ID {contact_id}의 정보가 성공적으로 업데이트되었습니다.")
        return True
    except Exception as e:
        print(f"🚨 오류 발생: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_contact(contact_id: int) -> bool:
    """연락처를 소프트 삭제합니다 (is_deleted = 1)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("UPDATE Contacts SET is_deleted = 1 WHERE contact_id = ?", (contact_id,))
        
        if c.rowcount == 0:
            print(f"⚠️ 경고: ID {contact_id}에 해당하는 연락처가 존재하지 않습니다.")
            return False
            
        conn.commit()
        print(f"✅ 연락처 ID {contact_id}가 삭제되었습니다.")
        return True
    except Exception as e:
        print(f"🚨 오류 발생: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def merge_contacts(source_contact_id: int, target_contact_id: int) -> bool:
    """
    중복된 담당자 데이터를 하나로 합칩니다. (source -> target)
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

# --------------------------------------------------------------------
# Products 테이블 CRUD
# --------------------------------------------------------------------

def add_product(product_name: str, min_price: float = None, max_price: float = None) -> int:
    """Products 테이블에 새로운 상품을 추가합니다. (기준 가격 범위 설정)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO Products (product_name, min_price, max_price) VALUES (?, ?, ?)",
            (product_name, min_price, max_price)
        )
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        print(f"오류: 상품명 '{product_name}'이 이미 존재합니다.")
        return None
    finally:
        conn.close()

def update_product(product_id: int, **kwargs) -> bool:
    """상품 정보를 업데이트합니다."""
    if not kwargs:
        print("ℹ️ 업데이트할 정보가 없습니다.")
        return True
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        params = list(kwargs.values()) + [product_id]
        
        c.execute(f"UPDATE Products SET {set_clause} WHERE product_id = ?", params)
        
        if c.rowcount == 0:
            print(f"⚠️ 경고: ID {product_id}에 해당하는 상품이 존재하지 않습니다.")
            return False
            
        conn.commit()
        print(f"✅ 상품 ID {product_id}의 정보가 성공적으로 업데이트되었습니다.")
        return True
    except Exception as e:
        print(f"🚨 오류 발생: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_product(product_id: int) -> bool:
    """상품을 소프트 삭제합니다 (is_deleted = 1)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("UPDATE Products SET is_deleted = 1 WHERE product_id = ?", (product_id,))
        
        if c.rowcount == 0:
            print(f"⚠️ 경고: ID {product_id}에 해당하는 상품이 존재하지 않습니다.")
            return False
            
        conn.commit()
        print(f"✅ 상품 ID {product_id}가 삭제되었습니다.")
        return True
    except Exception as e:
        print(f"🚨 오류 발생: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# ====================================================================
# Streamlit 테이블 편집 처리 (DataFrame 기반)
# ====================================================================

def detect_dataframe_changes(original_df: pd.DataFrame, edited_df: pd.DataFrame) -> Dict[str, List[int]]:
    """
    DataFrame의 변경사항을 감지합니다.
    
    Args:
        original_df: 원본 DataFrame
        edited_df: 편집된 DataFrame
        
    Returns:
        Dict containing 'added', 'modified', 'deleted' row indices
    """
    # ID 컬럼 확인 (task_id가 있다고 가정)
    id_col = 'task_id'
    
    if original_df.empty and not edited_df.empty:
        # 최초 로드 시 모든 행이 새로운 것으로 처리
        return {
            'added': list(edited_df.index),
            'modified': [],
            'deleted': []
        }
    
    if edited_df.empty and not original_df.empty:
        # 모든 행이 삭제됨
        return {
            'added': [],
            'modified': [],
            'deleted': list(original_df.index)
        }
    
    # 기존 ID 세트와 새로운 ID 세트 비교
    original_ids = set(original_df[id_col].dropna()) if id_col in original_df.columns else set()
    edited_ids = set(edited_df[id_col].dropna()) if id_col in edited_df.columns else set()
    
    # 신규 추가된 행들 (ID가 없거나 새로운 ID)
    added_indices = []
    for idx, row in edited_df.iterrows():
        if pd.isna(row.get(id_col)) or row.get(id_col) not in original_ids:
            added_indices.append(idx)
    
    # 삭제된 행들
    deleted_ids = original_ids - edited_ids
    deleted_indices = []
    if deleted_ids:
        deleted_indices = list(original_df[original_df[id_col].isin(deleted_ids)].index)
    
    # 수정된 행들
    modified_indices = []
    for idx, row in edited_df.iterrows():
        if pd.notna(row.get(id_col)) and row.get(id_col) in original_ids:
            # 해당 ID의 원본 데이터와 비교
            original_row = original_df[original_df[id_col] == row[id_col]].iloc[0]
            
            # 각 컬럼 비교 (NaN 처리 포함)
            for col in edited_df.columns:
                if col in original_df.columns:
                    orig_val = original_row.get(col)
                    edit_val = row.get(col)
                    
                    # NaN 처리: 둘 다 NaN이면 같다고 판단
                    if pd.isna(orig_val) and pd.isna(edit_val):
                        continue
                    # 하나만 NaN이거나 값이 다르면 수정됨
                    elif orig_val != edit_val:
                        modified_indices.append(idx)
                        break
    
    return {
        'added': added_indices,
        'modified': modified_indices, 
        'deleted': deleted_indices
    }

def process_task_table_changes(
    original_df: pd.DataFrame,
    edited_df: pd.DataFrame, 
    user_id: int
) -> bool:
    """
    Tasks 테이블의 변경사항을 처리하고 관련 테이블들을 업데이트합니다.
    
    Args:
        original_df: 원본 Tasks DataFrame
        edited_df: 편집된 Tasks DataFrame  
        user_id: 현재 사용자 ID
        
    Returns:
        bool: 처리 성공 여부
    """
    print("--- Tasks 테이블 변경사항 처리 시작 ---")
    
    # 1. 변경사항 감지
    changes = detect_dataframe_changes(original_df, edited_df)
    
    added_count = len(changes['added'])
    modified_count = len(changes['modified'])  
    deleted_count = len(changes['deleted'])
    
    if added_count == 0 and modified_count == 0 and deleted_count == 0:
        print("ℹ️ 변경사항이 없습니다.")
        return True
        
    print(f"📊 감지된 변경사항: 추가 {added_count}개, 수정 {modified_count}개, 삭제 {deleted_count}개")
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 2. 삭제 처리 (소프트 삭제)
        if deleted_count > 0:
            print(f"🗑️ {deleted_count}개 행 삭제 처리 중...")
            for idx in changes['deleted']:
                task_id = original_df.loc[idx, 'task_id']
                c.execute("UPDATE Tasks SET is_deleted = 1 WHERE task_id = ?", (task_id,))
        
        # 3. 수정 처리  
        if modified_count > 0:
            print(f"✏️ {modified_count}개 행 수정 처리 중...")
            for idx in changes['modified']:
                _update_existing_task(c, edited_df.loc[idx])
        
        # 4. 추가 처리 (가장 복잡 - task_type별 분기 처리)
        if added_count > 0:
            print(f"➕ {added_count}개 행 추가 처리 중...")
            for idx in changes['added']:
                _process_new_task(c, edited_df.loc[idx], user_id)
        
        conn.commit()
        print("✅ 모든 변경사항이 성공적으로 처리되었습니다.")
        return True
        
    except Exception as e:
        print(f"🚨 오류 발생: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# --------------------------------------------------------------------
# Task 처리 내부 헬퍼 함수들 (cursor 기반)
# --------------------------------------------------------------------

def _update_existing_task(c: sqlite3.Cursor, row: pd.Series) -> None:
    """기존 Task를 업데이트합니다."""
    task_id = row['task_id']
    
    # 동적으로 업데이트할 필드들 준비 (task_id 제외)
    update_fields = {}
    task_columns = [
        'company_id', 'contact_id', 'project_id', 'invoice_id', 
        'action_date', 'agenda', 'action_item', 'due_date', 
        'task_status', 'task_type', 'priority', 'memo'
    ]
    
    for col in task_columns:
        if col in row and pd.notna(row[col]):
            update_fields[col] = row[col]
    
    if not update_fields:
        return
        
    # UPDATE 쿼리 생성
    set_clause = ", ".join([f"{key} = ?" for key in update_fields.keys()])
    params = list(update_fields.values()) + [task_id]
    
    c.execute(f"UPDATE Tasks SET {set_clause} WHERE task_id = ?", params)
    print(f"  ✓ Task ID {task_id} 업데이트 완료")

def _process_new_task(c: sqlite3.Cursor, row: pd.Series, user_id: int) -> None:
    """
    새로운 Task를 추가하고 task_type에 따라 관련 테이블들을 처리합니다.
    """
    print(f"  📝 새로운 Task 처리 중: task_type = {row.get('task_type', 'N/A')}")
    
    # 1. 기본 회사/연락처 처리 (기존 헬퍼 함수 활용)
    company_name = row.get('company_name', '').strip()
    contact_name = row.get('contact_name', '').strip() if pd.notna(row.get('contact_name')) else None
    
    if not company_name:
        raise ValueError("회사명은 필수입니다.")
    
    company_id = get_or_create_company(c, company_name)
    contact_id = get_or_create_contact(c, company_id, contact_name) if contact_name else None
    
    # 2. Task 기본 정보 삽입
    task_data = {
        'user_id': user_id,
        'company_id': company_id,
        'contact_id': contact_id,
        'action_date': row.get('action_date'),
        'agenda': row.get('agenda'),
        'action_item': row.get('action_item'), 
        'due_date': row.get('due_date'),
        'task_status': row.get('task_status', 0),  # 기본값: 미실행
        'task_type': row.get('task_type', 'meeting'),
        'priority': row.get('priority', 1),  # 기본값: 보통
        'memo': row.get('memo')
    }
    
    # NULL 값들을 None으로 변환
    for key, value in task_data.items():
        if pd.isna(value):
            task_data[key] = None
    
    c.execute("""
        INSERT INTO Tasks (
            user_id, company_id, contact_id, action_date, agenda,
            action_item, due_date, task_status, task_type, priority, memo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tuple(task_data.values()))
    
    task_id = c.lastrowid
    print(f"    ✓ Task 기본 정보 저장 완료 (ID: {task_id})")
    
    # 3. task_type별 추가 처리
    task_type = row.get('task_type', '').lower()
    
    if task_type == 'first_contact':
        _handle_first_contact_task(c, task_id, company_id, contact_id, row)
    elif task_type == 'meeting':
        _handle_meeting_task(c, task_id, company_id, contact_id, row)
    elif task_type == 'quote':
        _handle_quote_task(c, task_id, company_id, contact_id, row)
    elif task_type == 'trial':
        _handle_trial_task(c, task_id, company_id, contact_id, row)
    elif task_type == 'tech_inquiry':
        _handle_tech_inquiry_task(c, task_id, company_id, contact_id, row)
    else:
        print(f"    ⚠️ 알 수 없는 task_type: {task_type}")

def _handle_first_contact_task(c: sqlite3.Cursor, task_id: int, company_id: int, contact_id: int, row: pd.Series) -> None:
    """최초 컨택 task_type 처리"""
    print("    🤝 최초 컨택 처리 중...")
    
    # First_Contact_Logs 생성
    contact_type = row.get('contact_type', '인바운드')
    channel = row.get('channel', '미상')
    contact_date = row.get('action_date')
    
    c.execute("""
        INSERT INTO First_Contact_Logs 
        (company_id, contact_id, contact_type, channel, contact_date)
        VALUES (?, ?, ?, ?, ?)
    """, (company_id, contact_id, contact_type, channel, contact_date))
    
    print("      ✓ First_Contact_Logs 생성 완료")
    
    # 관심 제품이 있으면 Project 생성
    interested_products = row.get('interested_products', '').strip()
    if interested_products and pd.notna(interested_products):
        project_name = f"{row.get('company_name', '미상')} - 초기 문의"
        application = row.get('application', '')
        
        c.execute("""
            INSERT INTO Projects 
            (company_id, contact_id, project_name, description, status, application)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company_id, contact_id, project_name, 
              f"최초 컨택 기반 프로젝트 ({contact_date})", 
              '문의', application))
        
        project_id = c.lastrowid
        
        # Task와 Project 연결
        c.execute("UPDATE Tasks SET project_id = ? WHERE task_id = ?", (project_id, task_id))
        
        print(f"      ✓ Project 생성 완료 (ID: {project_id})")
        
        # 관심 제품들 연결 (콤마로 구분된 제품명들)
        product_names = [p.strip() for p in interested_products.split(',') if p.strip()]
        for product_name in product_names:
            # 제품이 존재하는지 확인
            c.execute("SELECT product_id FROM Products WHERE product_name = ? AND is_deleted = 0", (product_name,))
            product_result = c.fetchone()
            
            if product_result:
                product_id = product_result[0]
                # Project_Products 연결
                c.execute("""
                    INSERT OR IGNORE INTO Project_Products (project_id, product_id)
                    VALUES (?, ?)
                """, (project_id, product_id))
                print(f"        ✓ 제품 연결: {product_name}")
            else:
                print(f"        ⚠️ 제품을 찾을 수 없음: {product_name}")

def _handle_meeting_task(c: sqlite3.Cursor, task_id: int, company_id: int, contact_id: int, row: pd.Series) -> None:
    """미팅 task_type 처리"""
    print("    🤝 미팅 Task 처리 중...")
    
    # 기존 Project가 지정되어 있으면 연결
    project_id = row.get('project_id')
    if pd.notna(project_id):
        c.execute("UPDATE Tasks SET project_id = ? WHERE task_id = ?", (int(project_id), task_id))
        print(f"      ✓ 기존 프로젝트(ID: {int(project_id)})와 연결")
    
    # 추가 미팅 관련 로직이 필요하면 여기에 추가

def _handle_quote_task(c: sqlite3.Cursor, task_id: int, company_id: int, contact_id: int, row: pd.Series) -> None:
    """견적 task_type 처리 - 향후 Invoice 생성으로 이어질 수 있음"""
    print("    💰 견적 Task 처리 중...")
    
    # 견적 관련 추가 로직 (필요시 구현)
    # 예: 견적서 번호, 견적 금액 등 기록

def _handle_trial_task(c: sqlite3.Cursor, task_id: int, company_id: int, contact_id: int, row: pd.Series) -> None:
    """무상대여 task_type 처리"""
    print("    🔬 무상대여 Task 처리 중...")
    
    # Free_Trials 테이블에 기록
    project_id = row.get('project_id')
    product_name = row.get('trial_product', '').strip()
    start_date = row.get('trial_start_date', row.get('action_date'))
    end_date = row.get('trial_end_date')
    
    if not product_name:
        print("      ⚠️ 대여 제품명이 지정되지 않았습니다.")
        return
        
    # 제품 ID 찾기
    c.execute("SELECT product_id FROM Products WHERE product_name = ? AND is_deleted = 0", (product_name,))
    product_result = c.fetchone()
    
    if not product_result:
        print(f"      ⚠️ 제품을 찾을 수 없음: {product_name}")
        return
        
    product_id = product_result[0]
    
    c.execute("""
        INSERT INTO Free_Trials 
        (task_id, project_id, product_id, start_date, end_date)
        VALUES (?, ?, ?, ?, ?)
    """, (task_id, project_id, product_id, start_date, end_date))
    
    print(f"      ✓ 무상대여 기록 완료: {product_name}")

def _handle_tech_inquiry_task(c: sqlite3.Cursor, task_id: int, company_id: int, contact_id: int, row: pd.Series) -> None:
    """기술문의 task_type 처리"""
    print("    🔧 기술문의 Task 처리 중...")
    
    # Tech_Inquiries 테이블에 기록
    project_id = row.get('project_id')
    product_name = row.get('inquiry_product', '').strip()
    application = row.get('application', '')
    ai_model = row.get('ai_model', '')
    
    if not product_name:
        print("      ⚠️ 문의 제품명이 지정되지 않았습니다.")
        return
    
    # 제품 ID 찾기
    c.execute("SELECT product_id FROM Products WHERE product_name = ? AND is_deleted = 0", (product_name,))
    product_result = c.fetchone()
    
    if not product_result:
        print(f"      ⚠️ 제품을 찾을 수 없음: {product_name}")
        return
        
    product_id = product_result[0]
    
    c.execute("""
        INSERT INTO Tech_Inquiries 
        (task_id, project_id, product_id, application, ai_model)
        VALUES (?, ?, ?, ?, ?)
    """, (task_id, project_id, product_id, application, ai_model))
    
    print(f"      ✓ 기술문의 기록 완료: {product_name}")

# ====================================================================
# Task 중심 비즈니스 로직 및 트랜잭션 처리
# ====================================================================

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
# 추가적인 비즈니스 로직 함수들 
# --------------------------------------------------------------------

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
            
# update_company_name 함수는 위의 update_company로 대체됨
            
# update_contact_info 함수는 위의 update_contact로 대체됨
            
# update_project_details 함수는 추후 프로젝트 CRUD 섹션에서 구현 예정
            
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
