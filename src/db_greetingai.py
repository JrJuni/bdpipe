from llama_cpp import Llama
import json
from config import MODEL_PATH
import os
from datetime import datetime

# --- LLM 모델 로딩 ---
if os.path.exists(MODEL_PATH):
    print("LLM 모델을 로딩합니다...")
    llm = Llama(model_path=MODEL_PATH, n_ctx=2048, verbose=False)
    print("모델 로딩 완료.")
else:
    llm = None
    print(f"경고: 모델 파일을 찾을 수 없습니다. 경로: {MODEL_PATH}")

def _get_llm_response(prompt: str) -> str:
    """
    LLM에 프롬프트를 보내고 텍스트 응답을 반환하는 헬퍼 함수.
    """
    if llm is None:
        print("오류: LLM 모델이 로드되지 않았습니다.")
        return ""

    output = llm(
        prompt,
        max_tokens=1024,  # 메일 생성을 위해 충분한 토큰 수 설정
        temperature=0.3,  # 적절한 창의성을 위해 온도 설정
        echo=False
    )
    
    response_text = output["choices"][0]["text"].strip()
    return response_text

def generate_thank_you_email(event_name: str, visitor_name: str, company: str, discussion_content: str) -> str:
    """
    행사 방문 감사메일을 자동으로 생성합니다.
    
    Args:
        event_name: 행사명
        visitor_name: 방문자 성명
        company: 회사명
        discussion_content: 논의 내용
    
    Returns:
        생성된 감사메일 내용
    """
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    prompt = f"""<|system|>
당신은 비즈니스 개발 전문가입니다. 행사에서 만난 방문자에게 보낼 정중하고 전문적인 감사메일을 작성해주세요.
메일은 한국어로 작성하되, 비즈니스 상황에 적합한 격식을 갖춰야 합니다.

다음 구조로 작성해주세요:
1. 인사말 및 감사 표현
2. 행사에서의 만남과 논의 내용 언급
3. 향후 협업 가능성에 대한 긍정적 표현
4. 추가 연락 또는 미팅 제안
5. 마무리 인사

메일은 너무 길지 않게, 하지만 충분히 정중하게 작성해주세요.

<|user|>
행사명: {event_name}
방문자 성명: {visitor_name}
회사명: {company}
논의 내용: {discussion_content}
작성 날짜: {current_date}

<|assistant|>
"""
    
    return _get_llm_response(prompt)

def generate_follow_up_email(event_name: str, visitor_name: str, company: str, discussion_content: str, 
                           next_action: str = "") -> str:
    """
    후속 조치를 포함한 감사메일을 생성합니다.
    
    Args:
        event_name: 행사명
        visitor_name: 방문자 성명
        company: 회사명
        discussion_content: 논의 내용
        next_action: 다음 단계 또는 후속 조치
    
    Returns:
        생성된 후속 조치 포함 감사메일 내용
    """
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    prompt = f"""<|system|>
당신은 비즈니스 개발 전문가입니다. 행사에서 만난 방문자에게 보낼 감사메일을 작성하되, 
구체적인 후속 조치나 다음 단계를 포함해서 작성해주세요.
메일은 한국어로 작성하되, 비즈니스 상황에 적합한 격식을 갖춰야 합니다.

다음 구조로 작성해주세요:
1. 인사말 및 감사 표현
2. 행사에서의 만남과 논의 내용 언급
3. 구체적인 후속 조치나 다음 단계 제안
4. 일정 조율이나 추가 논의 제안
5. 마무리 인사

메일은 액션 아이템이 명확하게 드러나도록 작성해주세요.

<|user|>
행사명: {event_name}
방문자 성명: {visitor_name}
회사명: {company}
논의 내용: {discussion_content}
다음 단계/후속 조치: {next_action}
작성 날짜: {current_date}

<|assistant|>
"""
    
    return _get_llm_response(prompt)

def generate_meeting_proposal_email(event_name: str, visitor_name: str, company: str, 
                                  discussion_content: str, proposed_meeting_topics: str) -> str:
    """
    미팅 제안을 포함한 감사메일을 생성합니다.
    
    Args:
        event_name: 행사명
        visitor_name: 방문자 성명
        company: 회사명
        discussion_content: 논의 내용
        proposed_meeting_topics: 제안할 미팅 주제
    
    Returns:
        생성된 미팅 제안 포함 감사메일 내용
    """
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    prompt = f"""<|system|>
당신은 비즈니스 개발 전문가입니다. 행사에서 만난 방문자에게 보낼 감사메일을 작성하되,
구체적인 미팅 제안을 포함해서 작성해주세요.
메일은 한국어로 작성하되, 비즈니스 상황에 적합한 격식을 갖춰야 합니다.

다음 구조로 작성해주세요:
1. 인사말 및 감사 표현
2. 행사에서의 만남과 논의 내용 언급
3. 더 자세한 논의를 위한 미팅 제안
4. 미팅에서 다룰 구체적인 주제 제시
5. 일정 조율 요청
6. 마무리 인사

미팅 제안이 자연스럽고 구체적으로 드러나도록 작성해주세요.

<|user|>
행사명: {event_name}
방문자 성명: {visitor_name}
회사명: {company}
논의 내용: {discussion_content}
제안할 미팅 주제: {proposed_meeting_topics}
작성 날짜: {current_date}

<|assistant|>
"""
    
    return _get_llm_response(prompt)

# --- 대화형 메일 생성 함수 ---
def interactive_email_generator():
    """
    사용자와 대화하며 감사메일을 생성하는 함수
    """
    print("="*50)
    print("행사 방문 감사메일 자동 생성기")
    print("="*50)
    
    # 기본 정보 입력
    event_name = input("행사명을 입력하세요: ").strip()
    visitor_name = input("방문자 성명을 입력하세요: ").strip()
    company = input("회사명을 입력하세요: ").strip()
    discussion_content = input("논의 내용을 입력하세요: ").strip()
    
    # 메일 유형 선택
    print("\n메일 유형을 선택하세요:")
    print("1. 기본 감사메일")
    print("2. 후속 조치 포함 감사메일")
    print("3. 미팅 제안 포함 감사메일")
    
    choice = input("선택 (1-3): ").strip()
    
    generated_email = ""
    
    if choice == "1":
        print("\n기본 감사메일을 생성합니다...")
        generated_email = generate_thank_you_email(event_name, visitor_name, company, discussion_content)
    
    elif choice == "2":
        next_action = input("다음 단계/후속 조치를 입력하세요: ").strip()
        print("\n후속 조치 포함 감사메일을 생성합니다...")
        generated_email = generate_follow_up_email(event_name, visitor_name, company, discussion_content, next_action)
    
    elif choice == "3":
        meeting_topics = input("제안할 미팅 주제를 입력하세요: ").strip()
        print("\n미팅 제안 포함 감사메일을 생성합니다...")
        generated_email = generate_meeting_proposal_email(event_name, visitor_name, company, discussion_content, meeting_topics)
    
    else:
        print("잘못된 선택입니다. 기본 감사메일을 생성합니다...")
        generated_email = generate_thank_you_email(event_name, visitor_name, company, discussion_content)
    
    print("\n" + "="*50)
    print("생성된 감사메일:")
    print("="*50)
    print(generated_email)
    print("="*50)
    
    # 파일 저장 옵션
    save_option = input("\n생성된 메일을 파일로 저장하시겠습니까? (y/n): ").strip().lower()
    if save_option == 'y' or save_option == 'yes':
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"감사메일_{visitor_name}_{company}_{timestamp}.txt"
        
        # exports 디렉토리가 없으면 생성
        if not os.path.exists("../exports"):
            os.makedirs("../exports")
        
        filepath = f"../exports/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"행사명: {event_name}\n")
            f.write(f"방문자: {visitor_name}\n")
            f.write(f"회사: {company}\n")
            f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            f.write(generated_email)
        
        print(f"파일이 저장되었습니다: {filepath}")

# --- 테스트 ---
if __name__ == '__main__':
    # --- 테스트 1: 기본 감사메일 생성 ---
    print("="*20, "기본 감사메일 생성 테스트", "="*20)
    
    test_email = generate_thank_you_email(
        event_name="2025 AI 컨퍼런스",
        visitor_name="김철수",
        company="테크솔루션",
        discussion_content="AI 기반 고객 서비스 자동화 솔루션에 대한 협업 방안 논의"
    )
    
    print("--- 생성된 기본 감사메일 ---")
    print(test_email)
    print("\n" + "="*60 + "\n")
    
    # --- 테스트 2: 후속 조치 포함 감사메일 생성 ---
    print("="*20, "후속 조치 포함 감사메일 테스트", "="*20)
    
    test_followup_email = generate_follow_up_email(
        event_name="스타트업 네트워킹 데이",
        visitor_name="박영희",
        company="이노베이션랩",
        discussion_content="블록체인 기반 공급망 관리 솔루션 개발 협력",
        next_action="기술 스펙 문서 공유 및 프로토타입 데모 일정 조율"
    )
    
    print("--- 생성된 후속 조치 포함 감사메일 ---")
    print(test_followup_email)
    print("\n" + "="*60 + "\n")
    
    # --- 테스트 3: 미팅 제안 포함 감사메일 생성 ---
    print("="*20, "미팅 제안 포함 감사메일 테스트", "="*20)
    
    test_meeting_email = generate_meeting_proposal_email(
        event_name="디지털 트랜스포메이션 세미나",
        visitor_name="이대표",
        company="퓨처테크",
        discussion_content="클라우드 마이그레이션 및 데이터 분석 플랫폼 구축",
        proposed_meeting_topics="구체적인 기술 요구사항 분석, 프로젝트 타임라인 수립, 예산 및 리소스 계획"
    )
    
    print("--- 생성된 미팅 제안 포함 감사메일 ---")
    print(test_meeting_email)
    print("\n" + "="*60 + "\n")
    
    # --- 대화형 생성기 실행 ---
    run_interactive = input("대화형 메일 생성기를 실행하시겠습니까? (y/n): ").strip().lower()
    if run_interactive == 'y' or run_interactive == 'yes':
        interactive_email_generator()