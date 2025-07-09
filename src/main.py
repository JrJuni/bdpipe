# main.py (수정)

import db_operations as ops
import db_queries as queries
import db_export as excel_exporter # <- 엑셀 내보내기 모듈 import
from pprint import pprint

def main_menu():
    """메인 메뉴를 보여주고 사용자 입력을 받습니다."""
    while True:
        print("\n--- Mobilint CRM ---")
        print("1. 전체 회사 목록 보기")
        print("2. 전체 Task 목록 보기")
        print("3. 신규 Task 추가하기")
        print("9. 전체 회사 목록을 엑셀로 내보내기") # <- 메뉴 추가
        print("0. 종료") # <- 번호 변경
        choice = input("원하는 작업의 번호를 입력하세요: ")

        if choice == '1':
            print("\n--- 전체 회사 목록 ---")
            # get_all_companies_summary()가 더 유용한 정보를 보여줍니다.
            companies = queries.get_all_companies_summary()
            pprint(companies)

        elif choice == '2':
            print("\n--- 전체 Task 목록 ---")
            tasks = queries.get_all_from_table('Tasks')
            pprint(tasks)

        elif choice == '3':
            print("\n--- 신규 Task 추가 ---")
            company_name = input("회사 이름을 입력하세요: ")
            contact_name = input("담당자 이름을 입력하세요 (없으면 Enter): ")
            agenda = input("주요 안건을 입력하세요: ")
            
            from datetime import date
            today = date.today().strftime("%Y-%m-%d")

            new_task_id = ops.add_task(
                user_id=1,
                company_name=company_name,
                contact_name=contact_name,
                action_date=today,
                agenda=agenda
            )
            if new_task_id:
                print(f"\n성공: 새로운 Task(ID: {new_task_id})가 추가되었습니다.")

        elif choice == '9': # <- 엑셀 내보내기 로직
            print("\n--- 회사 목록 엑셀 내보내기 ---")
            # 1. DB에서 데이터를 조회합니다.
            companies_data = queries.get_all_companies_summary()
            # 2. 조회한 데이터를 엑셀 내보내기 함수에 전달합니다.
            excel_exporter.export_to_excel(companies_data, 'companies_summary')

        elif choice == '0': # <- 번호 변경
            print("프로그램을 종료합니다.")
            break

        else:
            print("잘못된 입력입니다. 다시 입력하세요.")

if __name__ == '__main__':
    main_menu()