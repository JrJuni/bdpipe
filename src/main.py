import db_schema as schema

def main_menu():
    print("== 영업 관리 CRM 시작 ==")
    print("1. 데이터베이스 초기화")
    print("2. 작업 추가")
    print("3. 데이터 조회")
    print("4. 종료")
    # ... (여기에 메뉴 인터페이스 구현) ...

if __name__ == '__main__':
    # 프로그램 시작 전, 데이터베이스 구조가 준비되었는지 확인하고 초기화
    schema.initialize_database()

    # 데이터베이스가 준비되면 메인 메뉴를 보여줌
    main_menu()
