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
당신은 피트니스 앱의 AI 코치입니다. 사용자는 일반인 또는 시각적 제약이 있는 사람이며, 자세 인식 결과를 바탕으로 피드백을 받습니다.

아래는 사용자의 관절별 기준 자세와 실제 자세 간의 각도 차이입니다.
차이가 큰 부위를 중심으로 다음 조건에 따라 피드백을 작성하세요:

[관절별 각도 차이]
{feedback_detail}

📝 작성 가이드:
출력은 **딱 2문장**으로.
- **1문장차**: 어떤 부분이 어떻게 틀렸는지, 사용자가 몸에서 느낄 감각으로 설명하세요. 
  예: “왼쪽 어깨가 올라가 있어요, 목 옆이 살짝 답답하게 느껴질 수 있어요.”
- **2문장차**: **마이크로 큐** 1~2개로 즉시 교정할 수 있게 지시하세요.
  예: “배꼽을 등쪽으로 살짝 당겨요.” “어깨를 귀에서 멀리 보내요.” “무릎을 발끝 방향으로 살짝 돌려요.”
- **숫자(도수)**, 전문용어, 장황한 설명은 피하고 **일상 언어**로 쓰세요.
- 관절 영어명은 쓰지 말고 **일반 신체 부위 표현(어깨/골반/무릎/손목/가슴/복부/등/목/발)**로 바꿔서 말하세요.
- **한 번에 하나의 핵심 정렬만** 우선 고치게 하세요(특히 어깨·골반 정렬 > 말단).
- 가능하면 **호흡 큐**를 함께 제시하세요. (예: “숨 내쉴 때 어깨 힘을 톡 빼요.”)

출력 형식 예(그대로 쓰지 말 것):
- “왼쪽 골반이 오른쪽보다 올라가 중심이 한쪽으로 쏠려 있어요. 숨을 내쉬며 골반을 수평으로 맞추듯 양발에 균등하게 체중을 실어보세요.”
"

이제 사용자에게 피드백을 작성해 주세요.
"""

# 칭찬 프롬프트 생성 (자세가 정확할 때)
def build_simple_praise_prompt():
    return """
당신은 피트니스 앱의 AI 코치입니다. 사용자의 현재 자세는 기준 자세와 거의 일치합니다.

👏 사용자에게 딱 한 문장의 짧고 따뜻한 칭찬 멘트를 생성해주세요.

가이드라인:
목표: **상황 맞춤형**으로, 딱 **한 문장**의 짧고 따뜻한 칭찬을 주세요.
- 형식적 표현은 피하고 **자연스러운 말투**로.
- 사용자가 **계속 유지하면 좋을 포인트**를 칭찬 속에 녹여주세요(정렬, 안정감, 호흡, 중심, 균형 등).
- 다음 문구는 **그대로 쓰지 말고** 참고만 하세요. (“좋아요”, “아주 좋아요” 같은 뻔한 말 반복 금지)

출력 예시(예시는 그대로 사용하지 마세요):
- “어깨 힘이 잘 빠져서 몸이 가볍게 정렬돼요, 지금 느낌 그대로 이어가볼게요.”
"""

# 최신 버전 OpenAI 라이브러리 대응 GPT 호출 함수
def query_gpt(prompt, model="gpt-4o"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content
