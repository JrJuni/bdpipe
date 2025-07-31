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
        # n=3,           # 다른 답변 후보 생성 
        temperature=0.1, # 일관된 JSON 생성을 위해 온도를 낮춤, 다수 답변 생성 시 온도를 0.5~0.8 정도로 설정
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

1. "핵심결정사항": 이메일에서 최종적으로 결정되거나 문의한 내용은 무엇인가? 자세하게 작성해주세요.
2. "다음행동": 누가, 무엇을, 언제까지 해야 하는가? 기한을 최대한 추측하고 만약 없으면 기한 없음이라고 반드시 표기해주세요.
3. "상태변경": 프로젝트의 상태가 어떻게 변경되었는가? (예: '검토 중' -> '승인') 변경이 없다면 현재 상태를 서술해주세요.
4. "주요논의인물": 이 결정에 관련된 사람들의 이름은?
5. "메일 정보": 메일 제목과 송수신 시간이 표기되었다면 표기해주세요. 메일 정보는 최대한 원본 그대로 추출해주세요.

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
    Junyeob Kim
Business Development Team | Senior Manager
 
M +82-10-4753-8125
E junyeob@mobilint.com 
L https://www.linkedin.com/in/juni0409/
 
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
    
Re: [University of Toronto] Partnership-250728
2025-07-28 (월) 오후 2:30

안녕하세요. 박민수 부장님

UofT의 Innovation Hub라는 곳을 통해서 담당자들을 만나고, 필요한 서류를 3주전부터 준비하고 있는 데,
예상했던 것보다 늦어지고 있어서, 담당자를 통해서 재촉하고 있습니다.
다음 주안에는 초안이 가능할 것으로 여겨집니다.

TechVision에서 45K를 지원받는 것을 기부금으로 서류를 준비하고 있습니다.
연구비 혹은 프로젝트 펀드로 받는 경우, 학교에서 55%까지 간접비를 가져간다고 합니다.
기부금의 경우, 간접비가 15% 이내라고 들었습니다.

연구비 혹은 프로젝트 펀드는 자금을 제공하는 측에서 뭔가 구체적인 결과물을 명확하게 요구되는 경우이고,
기부금은 명확하게 구체적인 결과물이 요구되지 않는 경우 입니다.

기부금 협정서의 부속서류로 업무협약서를 포함하고자 합니다.
혹시 업무협약서에 포함시키고 싶은 내용이 있으면 알려주십시오.

또한, GPU A6000 서버를 제공받는 것은 또다른 양식(파일 첨부)으로 작성해야 합니다.
이것은 상대적으로 간단한 것 같습니다.
다만, 이것은 금액이 $7000을 넘어가게 되면, TechVision에서 IRS 8282 양식을 작성해야 합니다.
학교에서는 세무 목적상 가치를 $6,999로 하자는 건의가 있습니다.

감사합니다.

이상훈 드림. 

    """
    
    print("="*20, "이메일 요약 테스트", "="*20)
    summarized_data = summarize_with_llm(sample_email_content)
    print("--- 최종 요약 결과 ---")
    print(summarized_data)