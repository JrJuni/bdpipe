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
        print("4. 회사별 상세 조회")
        print("5. 프로젝트 관리")
        print("6. 인보이스 조회")
        print("7. Task 검색 및 필터")
        print("8. 담당자 검색")
        print("9. 전체 회사 목록을 엑셀로 내보내기")
        print("0. 종료")
        choice = input("원하는 작업의 번호를 입력하세요: ")

        if choice == '1':
            print("\n--- 전체 회사 목록 ---")
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

        elif choice == '4':
            company_detail_menu()

        elif choice == '5':
            project_menu()

        elif choice == '6':
            invoice_menu()

        elif choice == '7':
            task_search_menu()

        elif choice == '8':
            contact_search_menu()

        elif choice == '9':
            print("\n--- 회사 목록 엑셀 내보내기 ---")
            companies_data = queries.get_all_companies_summary()
            excel_exporter.export_to_excel(companies_data, 'companies_summary')

        elif choice == '0':
            print("프로그램을 종료합니다.")
            break

        else:
            print("잘못된 입력입니다. 다시 입력하세요.")

def company_detail_menu():
    """회사별 상세 조회 메뉴"""
    while True:
        print("\n--- 회사별 상세 조회 ---")
        print("1. 회사별 담당자 목록")
        print("2. 회사별 Task 목록")
        print("3. 회사별 프로젝트 목록")
        print("0. 메인 메뉴로 돌아가기")
        choice = input("선택하세요: ")
        
        if choice == '1':
            company_name = input("회사 이름을 입력하세요: ")
            contacts = queries.get_contacts_by_company_name(company_name)
            if contacts:
                print(f"\n--- '{company_name}' 담당자 목록 ---")
                pprint(contacts)
            else:
                print(f"'{company_name}' 회사의 담당자가 없습니다.")
                
        elif choice == '2':
            company_name = input("회사 이름을 입력하세요: ")
            tasks = queries.get_tasks_by_company_name(company_name)
            if tasks:
                print(f"\n--- '{company_name}' Task 목록 ---")
                pprint(tasks)
            else:
                print(f"'{company_name}' 회사의 Task가 없습니다.")
                
        elif choice == '3':
            company_name = input("회사 이름을 입력하세요: ")
            projects = queries.get_projects_by_company_name(company_name)
            if projects:
                print(f"\n--- '{company_name}' 프로젝트 목록 ---")
                pprint(projects)
            else:
                print(f"'{company_name}' 회사의 프로젝트가 없습니다.")
                
        elif choice == '0':
            break
        else:
            print("잘못된 입력입니다.")

def project_menu():
    """프로젝트 관리 메뉴"""
    while True:
        print("\n--- 프로젝트 관리 ---")
        print("1. 전체 프로젝트 목록")
        print("2. 프로젝트 상세 정보 (참여자 포함)")
        print("0. 메인 메뉴로 돌아가기")
        choice = input("선택하세요: ")
        
        if choice == '1':
            projects = queries.get_all_from_table('Projects')
            print("\n--- 전체 프로젝트 목록 ---")
            pprint(projects)
            
        elif choice == '2':
            try:
                project_id = int(input("프로젝트 ID를 입력하세요: "))
                project_details = queries.get_project_details_with_participants(project_id)
                if project_details:
                    print(f"\n--- 프로젝트 ID {project_id} 상세 정보 ---")
                    pprint(project_details)
                else:
                    print(f"프로젝트 ID {project_id}를 찾을 수 없습니다.")
            except ValueError:
                print("유효한 숫자를 입력하세요.")
                
        elif choice == '0':
            break
        else:
            print("잘못된 입력입니다.")

def invoice_menu():
    """인보이스 조회 메뉴"""
    while True:
        print("\n--- 인보이스 조회 ---")
        print("1. 전체 인보이스 목록")
        print("2. 인보이스 상세 정보 (항목 포함)")
        print("0. 메인 메뉴로 돌아가기")
        choice = input("선택하세요: ")
        
        if choice == '1':
            invoices = queries.get_all_from_table('Invoices')
            print("\n--- 전체 인보이스 목록 ---")
            pprint(invoices)
            
        elif choice == '2':
            try:
                invoice_id = int(input("인보이스 ID를 입력하세요: "))
                invoice_details = queries.get_invoice_details_with_items(invoice_id)
                if invoice_details:
                    print(f"\n--- 인보이스 ID {invoice_id} 상세 정보 ---")
                    pprint(invoice_details)
                else:
                    print(f"인보이스 ID {invoice_id}를 찾을 수 없습니다.")
            except ValueError:
                print("유효한 숫자를 입력하세요.")
                
        elif choice == '0':
            break
        else:
            print("잘못된 입력입니다.")

def task_search_menu():
    """Task 검색 및 필터 메뉴"""
    while True:
        print("\n--- Task 검색 및 필터 ---")
        print("1. 기간별 Task 조회")
        print("2. 사용자별 Task 조회")
        print("3. 미완료 Task 조회")
        print("0. 메인 메뉴로 돌아가기")
        choice = input("선택하세요: ")
        
        if choice == '1':
            start_date = input("시작일을 입력하세요 (YYYY-MM-DD): ")
            end_date = input("종료일을 입력하세요 (YYYY-MM-DD): ")
            tasks = queries.get_tasks_by_date_range(start_date, end_date)
            if tasks:
                print(f"\n--- {start_date} ~ {end_date} Task 목록 ---")
                pprint(tasks)
            else:
                print("해당 기간의 Task가 없습니다.")
                
        elif choice == '2':
            try:
                user_id = int(input("사용자 ID를 입력하세요: "))
                tasks = queries.get_tasks_by_user(user_id)
                if tasks:
                    print(f"\n--- 사용자 ID {user_id} Task 목록 ---")
                    pprint(tasks)
                else:
                    print(f"사용자 ID {user_id}의 Task가 없습니다.")
            except ValueError:
                print("유효한 숫자를 입력하세요.")
                
        elif choice == '3':
            tasks = queries.get_incomplete_tasks()
            if tasks:
                print("\n--- 미완료 Task 목록 ---")
                pprint(tasks)
            else:
                print("미완료 Task가 없습니다.")
                
        elif choice == '0':
            break
        else:
            print("잘못된 입력입니다.")

def contact_search_menu():
    """담당자 검색 메뉴"""
    while True:
        print("\n--- 담당자 검색 ---")
        print("1. 담당자 검색 (이름, 이메일, 전화번호)")
        print("2. 전체 담당자 목록")
        print("0. 메인 메뉴로 돌아가기")
        choice = input("선택하세요: ")
        
        if choice == '1':
            search_term = input("검색어를 입력하세요: ")
            contacts = queries.search_contacts(search_term)
            if contacts:
                print(f"\n--- '{search_term}' 검색 결과 ---")
                pprint(contacts)
            else:
                print(f"'{search_term}'에 대한 검색 결과가 없습니다.")
                
        elif choice == '2':
            contacts = queries.get_all_from_table('Contacts')
            print("\n--- 전체 담당자 목록 ---")
            pprint(contacts)
            
        elif choice == '0':
            break
        else:
            print("잘못된 입력입니다.")

if __name__ == '__main__':
    main_menu()