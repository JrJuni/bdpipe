import hashlib
import sqlite3
from config import DB_PATH
import db_operations as ops

def hash_password(password: str) -> str:
    """비밀번호를 해시화합니다."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """비밀번호를 검증합니다."""
    return hash_password(password) == hashed

def authenticate_user(username: str, password: str) -> dict:
    """사용자 인증을 수행합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            SELECT user_id, username, password_hash, auth_level 
            FROM Users 
            WHERE username = ? AND is_deleted = 0
        """, (username,))
        user = c.fetchone()
        
        if user and verify_password(password, user[2]):
            return {
                'user_id': user[0],
                'username': user[1],
                'auth_level': user[3],
                'authenticated': True
            }
        return {'authenticated': False}
    finally:
        conn.close()

def authenticate_user_by_username(username: str) -> dict:
    """사용자명으로만 사용자 정보를 조회합니다. (세션 복원용)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            SELECT user_id, username, auth_level 
            FROM Users 
            WHERE username = ? AND is_deleted = 0
        """, (username,))
        user = c.fetchone()
        
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'auth_level': user[2],
                'authenticated': True
            }
        return {'authenticated': False}
    finally:
        conn.close()

def register_user(username: str, password: str, email: str = None) -> bool:
    """신규 사용자 등록 (레벨 0으로 시작)"""
    password_hash = hash_password(password)
    # 빈 문자열을 None으로 변환하여 UNIQUE 제약조건 문제 해결
    if email == "":
        email = None
    user_id = ops.add_user(username, password_hash, email, auth_level=0)
    return user_id is not None

def approve_user(admin_username: str, target_username: str, level: int = 1) -> bool:
    """Level 4 이상 사용자가 권한 레벨 설정 가능"""
    # 요청자의 권한 레벨 확인
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            SELECT auth_level FROM Users 
            WHERE username = ? AND is_deleted = 0
        """, (admin_username,))
        admin_info = c.fetchone()
        
        if not admin_info or admin_info[0] < 4:
            return False
        
        admin_level = admin_info[0]
        
        # 권한 제한: 자신의 레벨까지만 설정 가능 (Level 5는 예외)
        if level > admin_level and admin_level < 5:
            return False
        
        if not (0 <= level <= 5):
            return False
        
        c.execute("""
            UPDATE Users 
            SET auth_level = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE username = ? AND is_deleted = 0
        """, (level, target_username))
        conn.commit()
        return c.rowcount == 1
    finally:
        conn.close()

def get_pending_users() -> list:
    """레벨 0 사용자 목록 (승인 대기)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            SELECT username, user_email, created_at, auth_level 
            FROM Users 
            WHERE auth_level = 0 AND is_deleted = 0
        """)
        return c.fetchall()
    finally:
        conn.close()

def get_all_users() -> list:
    """모든 사용자 목록 (관리자용)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            SELECT username, user_email, auth_level, created_at 
            FROM Users 
            WHERE is_deleted = 0 
            ORDER BY auth_level DESC, created_at
        """)
        return c.fetchall()
    finally:
        conn.close()

def initialize_admin_user():
    """관리자 계정 초기화"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("SELECT COUNT(*) FROM Users WHERE username = 'admin'")
        if c.fetchone()[0] == 0:
            admin_hash = hash_password('admin0417')
            ops.add_user('admin', admin_hash, 'admin@bdpipe.com', auth_level=5)
            print("관리자 계정이 생성되었습니다. (Level 5)")
        else:
            print("관리자 계정이 이미 존재합니다.")
    finally:
        conn.close()

def get_auth_level_name(level: int) -> str:
    """권한 레벨 이름 반환"""
    level_names = {
        0: "대기",
        1: "일반",
        2: "승인됨",
        3: "고급",
        4: "매니저",
        5: "관리자"
    }
    return level_names.get(level, "알 수 없음")

def update_user_email(username: str, new_email: str) -> bool:
    """사용자 이메일 업데이트"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # 빈 문자열을 None으로 변환
        if new_email == "":
            new_email = None
        
        c.execute("""
            UPDATE Users 
            SET user_email = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE username = ? AND is_deleted = 0
        """, (new_email, username))
        conn.commit()
        return c.rowcount == 1
    except sqlite3.IntegrityError:
        return False  # 이메일 중복
    finally:
        conn.close()

def update_user_password(username: str, old_password: str, new_password: str) -> bool:
    """사용자 비밀번호 업데이트 (기존 비밀번호 확인)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # 기존 비밀번호 확인
        c.execute("""
            SELECT password_hash FROM Users 
            WHERE username = ? AND is_deleted = 0
        """, (username,))
        user = c.fetchone()
        
        if not user or not verify_password(old_password, user[0]):
            return False
        
        # 새 비밀번호로 업데이트
        new_password_hash = hash_password(new_password)
        c.execute("""
            UPDATE Users 
            SET password_hash = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE username = ? AND is_deleted = 0
        """, (new_password_hash, username))
        conn.commit()
        return c.rowcount == 1
    finally:
        conn.close()

def get_user_info(username: str) -> dict:
    """사용자 정보 조회 (정보수정용)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            SELECT username, user_email, auth_level, created_at 
            FROM Users 
            WHERE username = ? AND is_deleted = 0
        """, (username,))
        user = c.fetchone()
        
        if user:
            return {
                'username': user[0],
                'email': user[1] or "",
                'auth_level': user[2],
                'created_at': user[3],
                'found': True
            }
        return {'found': False}
    finally:
        conn.close()

def delete_user(admin_username: str, target_username: str) -> bool:
    """Level 4 이상 사용자가 삭제 가능 (soft delete)"""
    # admin 계정은 삭제 불가
    if target_username == 'admin':
        return False
    
    # 요청자의 권한 레벨 확인
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            SELECT auth_level FROM Users 
            WHERE username = ? AND is_deleted = 0
        """, (admin_username,))
        admin_info = c.fetchone()
        
        if not admin_info or admin_info[0] < 4:
            return False
        
        c.execute("""
            UPDATE Users 
            SET is_deleted = 1, 
                username = username || '_deleted_' || strftime('%s', 'now'),
                updated_at = CURRENT_TIMESTAMP 
            WHERE username = ? AND is_deleted = 0
        """, (target_username,))
        conn.commit()
        return c.rowcount == 1
    finally:
        conn.close()