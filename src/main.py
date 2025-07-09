from database import initialize_database

def main_menu():
    print("== 영업 관리 CRM 시작 ==")
    # ... (여기에 메뉴 인터페이스 구현) ...

if __name__ == '__main__':
    # 프로그램 시작 전, 데이터베이스 구조가 준비되었는지 확인하고 초기화
    initialize_database()

    # 데이터베이스가 준비되면 메인 메뉴를 보여줌
    main_menu()