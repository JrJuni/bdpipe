import pandas as pd
import os
from datetime import datetime

# --- 설정: 엑셀 파일을 저장할 폴더 ---
EXPORT_DIR = 'exports'

def export_to_excel(data: list, filename_prefix: str):
    """
    데이터(딕셔너리의 리스트)를 엑셀 파일로 저장합니다.
    
    Args:
        data (list): db_queries에서 반환된 것과 같은 딕셔너리의 리스트.
        filename_prefix (str): 저장할 엑셀 파일 이름의 접두사.
                               (예: 'companies_summary')
                               
    Returns:
        str: 저장된 파일의 전체 경로. 실패 시 None.
    """
    if not data:
        print("경고: 내보낼 데이터가 없습니다.")
        return None

    # 'exports' 폴더가 없으면 생성
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    # 현재 시간을 포함한 동적인 파일 이름 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.xlsx"
    filepath = os.path.join(EXPORT_DIR, filename)
    
    try:
        # 1. 데이터를 pandas DataFrame으로 변환합니다.
        df = pd.DataFrame(data)
        
        # 2. DataFrame을 엑셀 파일로 저장합니다.
        #    index=False 옵션은 엑셀에 불필요한 순번이 적히는 것을 방지합니다.
        df.to_excel(filepath, index=False)
        
        print(f"성공: 데이터가 '{filepath}' 파일로 저장되었습니다.")
        return filepath
        
    except Exception as e:
        print(f"오류: 엑셀 파일 저장 중 문제가 발생했습니다 - {e}")
        return None

# --- 이 파일을 직접 실행했을 때 테스트할 수 있는 코드 ---
if __name__ == '__main__':
    # 테스트를 위한 가상 데이터 생성
    sample_data = [
        {'id': 1, 'name': '모빌린트', 'task_count': 10},
        {'id': 2, 'name': '퀄컴', 'task_count': 5},
        {'id': 3, 'name': '인텔', 'task_count': 8}
    ]
    
    print("--- 엑셀 내보내기 기능 테스트 ---")
    export_to_excel(sample_data, 'test_export')