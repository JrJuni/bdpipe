from llama_cpp import Llama
import json
from config import MODEL_PATH
import os

# --- LLM 모델 로딩 ---
if os.path.exists(MODEL_PATH):
    print("LLM 모델을 로딩합니다...")
    llm = Llama(model_path=MODEL_PATH, n_ctx=2048, verbose=False)
    print("모델 로딩 완료.")
else:
    llm = None
    print(f"경고: 모델 파일을 찾을 수 없습니다. 경로: {MODEL_PATH}")

def _get_llm_json_response(prompt: str) -> dict:
    """
    LLM에 프롬프트를 보내고, 응답에서 JSON 객체만 안전하게 추출하여 반환하는 헬퍼 함수.
    """
    if llm is None:
        print("오류: LLM 모델이 로드되지 않았습니다.")
        return {}

    output = llm(
        prompt,
        max_tokens=512,  # 더 긴 JSON 출력을 위해 토큰 수 증가
        stop=["```"],    # JSON 코드 블록이 끝나면 생성을 멈추도록 설정
        temperature=0.1, # 일관된 JSON 생성을 위해 온도를 낮춤
        echo=False
    )
    
    response_text = output["choices"][0]["text"]
    
    try:
        # 응답 텍스트에서 첫 '{'와 마지막 '}'를 찾아 그 사이의 내용만 추출
        start_index = response_text.find('{')
        end_index = response_text.rfind('}')
        
        if start_index != -1 and end_index != -1 and start_index < end_index:
            json_string = response_text[start_index : end_index + 1]
            return json.loads(json_string)
        else:
            raise json.JSONDecodeError("No valid JSON object found", response_text, 0)

    except json.JSONDecodeError as e:
        print(f"오류: LLM의 답변을 JSON으로 변환하는 데 실패했습니다. - {e}")
        print(f"--- LLM 원본 응답 ---\n{response_text}\n--------------------")
        return {}

def parse_contact_with_llm(email_body: str) -> dict:
    """
    LLM을 사용하여 이메일 본문에서 연락처 정보를 추출합니다.
    """
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
    return _get_llm_json_response(prompt)

def summarize_with_llm(email_content: str) -> dict:
    """
    LLM을 사용하여 이메일 내용을 요약합니다.
    """
    prompt = f"""<|system|>
당신은 유능한 프로젝트 매니저입니다. 아래 이메일 내용을 분석하여 다음 항목에 따라 JSON 형식으로 요약해주세요:

1. "핵심결정사항": 이메일에서 최종적으로 결정되거나 문의한 내용은 무엇인가?
2. "다음행동": 누가, 무엇을, 언제까지 해야 하는가?
3. "상태변경": 프로젝트의 상태가 어떻게 변경되었는가? (예: '검토 중' -> '승인')
4. "주요논의인물": 이 결정에 관련된 사람들의 이름은?

--- 분석할 이메일 ---
{email_content}
--------------------

<|assistant|>
```json
"""
    return _get_llm_json_response(prompt)


# --- 테스트 ---
if __name__ == '__main__':
    # --- 1차 테스트: 연락처 추출 ---
    sample_signature = """
    Best regards,

    Jiyeon Lee
    Management Department Team| Manager

    M. +82-10-8616-2555
    E. jiyeon@mobilint.com

    Mobilint, Inc.
    3F, Narakium Yeoksam B Building,
    35, Seolleung-ro 93-gil, Gangnam-gu, Seoul, Republic of Korea
    """
    
    print("="*20, "연락처 추출 테스트", "="*20)
    parsed_contact_data = parse_contact_with_llm(sample_signature)
    print("--- 최종 추출 결과 ---")
    print(parsed_contact_data)
    
    print("\n" + "="*50 + "\n")

    # --- 2차 테스트: 이메일 요약 ---
    sample_email_content = """
안녕하세요. 황재준소장님.
모빌린트 조윤석입니다.

첨부와 같이 관련 서류 송부하오니 확인하시어 발주 진행 요청드리며,
광명테크 사업자등록증 및 세금계산서 발행주소 회신 부탁드립니다.

또한, Mobilint NPU SDK 및 각종 리소스를 다운받기 위해서는 공식 배포처 (http://dl.mobilint.com) 계정 등록이 필요합니다.
첨부(Mobilint Distribution Website.pdf)를 통해 등록 방법을 안내드리오니 참고하시어 공식 배포처에 계정 등록을 완료해주신 후 회신 부탁드립니다.
아울러 문의가 있으실 경우 언제든 회신 부탁드리겠습니다.


@Jiyeon 님.
발주서 입수되는대로 Aries/Regulus 개발키트 및 SoM 준비 바랍니다.

@Somin 님.
발주서 입수 되는대로 계산서 발행 후 전체 공유 부탁 드립니다.


감사합니다.
조윤석드림.

    """
    
    print("="*20, "이메일 요약 테스트", "="*20)
    summarized_data = summarize_with_llm(sample_email_content)
    print("--- 최종 요약 결과 ---")
    print(summarized_data)