from llama_cpp import Llama
import json
from config import MODEL_PATH
import os

# --- LLM 모델 로딩 ---
# 앱이 시작될 때 한 번만 로드되도록 함수 밖에 배치하거나, 캐싱 기능을 활용합니다.
# 모델 파일이 있는지 먼저 확인
if os.path.exists(MODEL_PATH):
    print("LLM 모델을 로딩합니다...")
    llm = Llama(model_path=MODEL_PATH, verbose=False)
    print("모델 로딩 완료.")
else:
    llm = None
    print(f"경고: 모델 파일을 찾을 수 없습니다. 경로: {MODEL_PATH}")

def parse_contact_with_llm(email_body: str) -> dict:
    """
    LLM을 사용하여 이메일 본문에서 연락처 정보를 추출합니다.
    """
    if llm is None:
        print("오류: LLM 모델이 로드되지 않았습니다.")
        return {}
    
    prompt = f"""<|system|>
    당신은 한국어 및 영어 이메일 서명을 분석하여 연락처 정보를 추출하는 전문가입니다.
    다음 텍스트에서 이름, 이메일, 전화번호, 회사명, 회사주소, 팀, 직급을 찾아서 JSON 형식으로 반환해주세요.
    만약 특정 정보를 찾을 수 없다면, 값으로 null을 사용해주세요.

<|user|>
--- Text to Analyze ---
{email_body}
--------------------

<|assistant|>
```json
"""
    # 프롬프트 형식을 모델에 맞게 수정하면(예: ChatML) 성능이 더 좋아질 수 있습니다.



    # --- 실제 LLM 호출 부분 (개념) ---
    # 실제로는 아래 코드를 실행해야 합니다. 지금은 개념만 보여드립니다.
    output = llm(prompt, max_tokens=256, stop=["}"], echo=False)
    response_text = output["choices"][0]["text"] + "}"
    
    print(response_text)
    
    try:
        # LLM의 답변(텍스트)를 JSON(딕셔너리) 객체로 변환
        return json.loads(response_text)
    except json.JSONDecodeError:
        print("오류: LLM의 답변을 JSON으로 변환하는 데 실패했습니다.")
        return {}

'''
# --- 테스트 ---
if __name__ == '__main__':
    sample_email_signature = """
    Best regards,

Jiyeon Lee
Management Department Team| Manager

M. +82-10-8616-2555
E. jiyeon@mobilint.com

Mobilint, Inc.
3F, Narakium Yeoksam B Building,
35, Seolleung-ro 93-gil, Gangnam-gu, Seoul, Republic of Korea

    """
    
    # LLM이 있다면, 이런 다양한 형식도 모두 정확하게 분석해낼 수 있습니다.
    parsed_data = parse_contact_with_llm(sample_email_signature)
    
    print("--- LLM 기반 이메일 서명 분석 결과 ---")
    print(parsed_data)
'''    
    
def summarize_with_llm(email_content: str) -> dict:
    """
    LLM을 사용하여 이메일 내용을 요약합니다.
    """
    if llm is None:
        print("오류: LLM 모델이 로드되지 않았습니다.")
        return {}
    
    prompt = f"""<|system|>
    당신은 유능한 프로젝트 매니저입니다. 아래 이메일 내용을 분석하여 다음 항목에 따라 JSON 형식으로 요약해주세요:

    1. "핵심 결정사항": 이메일에서 최종적으로 결정되거나 문의한 내용은 무엇인가?
    2. "다음 행동(Action Item)": 누가, 무엇을, 언제까지 해야 하는가?
    3. "상태 변경": 프로젝트의 상태가 어떻게 변경되었는가? (예: '검토 중' -> '승인')
    4. "주요 논의 인물": 이 결정에 관련된 사람들의 이름은?

--- 분석할 이메일 ---
{email_content}
--------------------

JSON 결과:
"""
    # 프롬프트 형식을 모델에 맞게 수정하면(예: ChatML) 성능이 더 좋아질 수 있습니다.



    # --- 실제 LLM 호출 부분 (개념) ---
    # 실제로는 아래 코드를 실행해야 합니다. 지금은 개념만 보여드립니다.
    output = llm(prompt, max_tokens=256, stop=["}"], echo=False)
    response_text = output["choices"][0]["text"] + "}"
    
    print(response_text)
    
    try:
        # LLM의 답변(텍스트)를 JSON(딕셔너리) 객체로 변환
        return json.loads(response_text)
    except json.JSONDecodeError:
        print("오류: LLM의 답변을 JSON으로 변환하는 데 실패했습니다.")
        return {}
    

# --- 2차 테스트 ---
if __name__ == '__main__':
    sample_email_content = """
안녕하세요. 모빌린트 사업개발본부를 맡고 있는 김성모입니다.

먼저 저희 모빌린트 국산 AI 반도체 적용에 긍정적으로 검토 주시어 감사드립니다.
旣견적드린 REGULUS RDK는 개발자키트로 
폐사는 수량에 따라 SoM (System on Module)과 Chip 비즈니스를 혼용하여 운영 중에 있습니다.
빠르게 개발자키트 구매가 이루어지어 SoM 사업으로 이어지기를 희망 드립니다.
-. SoM 샘플가격: 50만원
-. SoM 양산가격: $200 (500EA 기준), $180 (1,000개 기준)
-. Chip 기준: 별도 협의 (사전에 생각하시는 수량이 어느정도 인지 확인이 필요합니다.)

감사합니다.
김성모드림
010-6526-6248


    """
    
    # LLM이 있다면, 이런 다양한 형식도 모두 정확하게 분석해낼 수 있습니다.
    parsed_data = summarize_with_llm(sample_email_content)
    
    print("--- LLM 기반 이메일 서명 분석 결과 ---")
    print(parsed_data)