import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 인스턴스화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 사용할 관절쌍 정의
angle_joints = [
    ("LEFT_ELBOW", "LEFT_SHOULDER", "LEFT_WRIST"),
    ("RIGHT_ELBOW", "RIGHT_SHOULDER", "RIGHT_WRIST"),
    ("LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_HIP"),
    ("RIGHT_SHOULDER", "RIGHT_ELBOW", "RIGHT_HIP"),
    ("LEFT_KNEE", "LEFT_HIP", "LEFT_ANKLE"),
    ("RIGHT_KNEE", "RIGHT_HIP", "RIGHT_ANKLE"),
    ("LEFT_HIP", "LEFT_KNEE", "LEFT_SHOULDER"),
    ("RIGHT_HIP", "RIGHT_KNEE", "RIGHT_SHOULDER"),
    ("NOSE", "LEFT_SHOULDER", "RIGHT_SHOULDER")
]

# 관절 한글 이름 매핑
joint_name_map = {
    "LEFT_ELBOW": "왼쪽 팔꿈치", "RIGHT_ELBOW": "오른쪽 팔꿈치",
    "LEFT_SHOULDER": "왼쪽 어깨", "RIGHT_SHOULDER": "오른쪽 어깨",
    "LEFT_KNEE": "왼쪽 무릎", "RIGHT_KNEE": "오른쪽 무릎",
    "LEFT_HIP": "왼쪽 엉덩이", "RIGHT_HIP": "오른쪽 엉덩이",
    "NECK": "목"
}

# 각도 계산 함수
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

# 관절별 각도 차이 계산
def get_joint_angle_differences(ref_pose, user_pose):
    angle_diffs = {}
    for center, a, b in angle_joints:
        if all(j in ref_pose and j in user_pose for j in (a, center, b)):
            ref_angle = calculate_angle(ref_pose[a], ref_pose[center], ref_pose[b])
            user_angle = calculate_angle(user_pose[a], user_pose[center], user_pose[b])
            angle_diffs[center] = abs(ref_angle - user_angle)
        else:
            angle_diffs[center] = None
    return angle_diffs

# 피드백 프롬프트 생성 (자세가 틀렸을 때)
def build_prompt_with_pose_feedback(joint_names, angle_differences, threshold=15):
    feedback_parts = []
    for joint, diff in zip(joint_names, angle_differences):
        if diff is not None and diff > threshold:
            friendly_name = joint_name_map.get(joint, joint)
            feedback_parts.append(f"- {friendly_name}가 기준보다 {diff:.1f}도 차이가 납니다.")
    feedback_detail = "\n".join(feedback_parts)


    return f""" 

당신은 피트니스 앱의 요가 코치입니다. 사용자는 일반인 또는 시각적 제약이 있는 사람입니다.
사용자가 정답 자세와 일치할 수 있도록 상황에 맞는 적절한 피드백을 해주세요.
명확한 방향 표현(오른쪽, 왼쪽, 위, 아래), 몸의 긴장도, 호흡 등의 여러가지 표현을 사용하여 정답 자세와 가까워질 수 있도록 피드백을 해주세요.
아래 ‘관절별 각도 차이’만을 근거로, **딱 2문장**의 피드백을 대화체로 작성하세요.

[관절별 각도 차이]
{feedback_detail}

작성 규칙(아래를 엄격히 지킴):
1) 선택 로직: 각도 차이의 절대값을 기준으로 내림차순 정렬 → 가장 큰 1개 부위(타이 동률이면 2개)만 다룸.
   - 우선순위: 어깨, 골반 > 무릎/팔꿈치 > 손목/발목 > 목/등/가슴.
   - 데이터에 없는 부위는 언급 금지. 좌/우도 데이터가 큰 쪽만 명시.
2) 정확성: “한쪽이 올라갔다/기울었다” 등 비대칭 표현은 좌/우 데이터 차이가 클 때만 사용.
   과잉 해석 금지. 주어진 차이만 근거로 기술.
3) 문장 구성(2문장):
   - 1문장차: 틀린 부위를 감각 중심으로 짧게.
   - 2문장차: 마이크로 큐 1~2개, 가능하면 호흡 큐 포함.
4) 표현: 일상 부위명만 사용(어깨/골반/무릎/손목/가슴/복부/등/목/발).
   숫자·각도·전문용어 금지. 원인/병명/과한 경고 금지.
5) 길이 제한: 각 문장 12단어 이하, 전체 22단어 이하. 부드러운 구어체.
6) 오차가 전반적으로 매우 작으면: 짧은 칭찬 + 미세 정렬 1가지만 제안.

"""


# 칭찬 프롬프트 생성 (자세가 정확할 때)
def build_simple_praise_prompt():
    return """
당신은 피트니스 앱의 AI 코치입니다.  
사용자의 현재 자세는 기준 자세와 거의 일치합니다.  
한 문장으로, 현재 자세에 대한 상황에 마다 다르게 간단한 칭찬과 유지 피드백을 해주세요.

조건:
1. ‘좋아요’, ‘아주 좋아요’처럼 뻔한 표현을 단독으로 쓰지 말고, **상황에 맞는 포인트**(호흡, 안정감, 균형 등)를 짧게 포함.
2. 예시는 참고만 하고 **그대로 복사하지 말기**, 문장 구조·단어를 상황에 맞게 변형.
3. 10~14단어 이내, 부드럽고 친근한 말투.
4. 출력은 한 문장만, 불필요한 설명·기호·이모지 없이.

"""

# 최신 버전 OpenAI 라이브러리 대응 GPT 호출 함수
def query_gpt(prompt, model="gpt-4o"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content
