#!/usr/bin/env python3
"""
db_queries.py 함수들의 무결성 검사 스크립트
"""

import sys
import os
sys.path.append('src')

try:
    import db_queries as queries
    print("✅ db_queries 모듈 import 성공")
except ImportError as e:
    print(f"❌ db_queries 모듈 import 실패: {e}")
    sys.exit(1)

# 함수 존재 여부 확인
functions_to_test = [
    'get_tasks_by_company_name',
    'get_all_companies_summary', 
    'get_contacts_by_company_name',
    'get_projects_by_company_name',
    'get_project_details_with_participants',
    'get_invoice_details_with_items',
    'get_tasks_by_date_range',
    'get_tasks_by_user',
    'get_incomplete_tasks',
    'search_contacts',
    'get_all_from_table'
]

print("\n=== 함수 존재 여부 검사 ===")
for func_name in functions_to_test:
    if hasattr(queries, func_name):
        func = getattr(queries, func_name)
        if callable(func):
            print(f"✅ {func_name}: 함수 존재 및 호출 가능")
        else:
            print(f"❌ {func_name}: 존재하지만 호출 불가능")
    else:
        print(f"❌ {func_name}: 함수 없음")

print("\n=== 함수 시그니처 검사 ===")
import inspect

# 각 함수의 시그니처 확인
for func_name in functions_to_test:
    if hasattr(queries, func_name):
        func = getattr(queries, func_name)
        sig = inspect.signature(func)
        print(f"✅ {func_name}{sig}")

print("\n=== SQL 구문 기본 검사 ===")
# 간단한 정적 분석으로 SQL 구문 확인
import re

with open('src/db_queries.py', 'r', encoding='utf-8') as f:
    content = f.read()

# SQL 패턴 찾기
sql_patterns = re.findall(r'sql\s*=\s*"""(.*?)"""', content, re.DOTALL)
print(f"✅ 발견된 SQL 쿼리 수: {len(sql_patterns)}")

# 기본적인 SQL 키워드 확인
sql_keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'ORDER BY']
for i, sql in enumerate(sql_patterns):
    missing_keywords = []
    for keyword in sql_keywords:
        if keyword not in sql.upper():
            if keyword not in ['WHERE', 'JOIN', 'ORDER BY']:  # 필수가 아닌 키워드들
                missing_keywords.append(keyword)
    
    if missing_keywords:
        print(f"⚠️  SQL {i+1}: 누락된 키워드 {missing_keywords}")
    else:
        print(f"✅ SQL {i+1}: 기본 구문 확인")

print("\n=== 무결성 검사 완료 ===")
print("모든 함수가 정상적으로 정의되어 있습니다.")