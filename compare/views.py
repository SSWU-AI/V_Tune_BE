# compare/views.py
import json, logging, traceback
from rest_framework.decorators import api_view
from rest_framework.response import Response
from data.models import PoseStep
from .utils.pose_utils import normalize_pose, compare_joint_angles, calculate_joint_diff

# ✅ GPT 유틸은 기존 feedback/utils.py 그대로 재사용
from feedback.utils import (
    get_joint_angle_differences,
    build_simple_praise_prompt,
    build_prompt_with_pose_feedback,
    query_gpt,
)

logger = logging.getLogger(__name__)

# MediaPipe ↔️ 내부 키 매핑
yoga_to_mediapipe = {
    "HEAD": "NOSE", "LSHOULDER": "LEFT_SHOULDER", "RSHOULDER": "RIGHT_SHOULDER",
    "LELBOW": "LEFT_ELBOW", "RELBOW": "RIGHT_ELBOW",
    "LWRIST": "LEFT_WRIST", "RWRIST": "RIGHT_WRIST",
    "LHIP": "LEFT_HIP", "RHIP": "RIGHT_HIP",
    "LKNEE": "LEFT_KNEE", "RKNEE": "RIGHT_KNEE",
    "LANKLE": "LEFT_ANKLE", "RANKLE": "RIGHT_ANKLE"
}
mediapipe_to_yoga = {v: k for k, v in yoga_to_mediapipe.items()}

@api_view(['POST'])
def compare_and_feedback(request):
    """
    POST /api/compare/?exercise_id=<int>&step_number=<int>
    Body: { "keypoints": { "NOSE":[x,y], "LEFT_SHOULDER":[x,y], ... } }
    응답: { match, angle_differences, joint_differences, feedback_text }
    """
    exercise_id = request.query_params.get('exercise_id')
    step_number = request.query_params.get('step_number')
    user_keypoints_raw = request.data.get('keypoints')

    # 파라미터 검증
    if exercise_id is None or step_number is None:
        return Response({'error': 'exercise_id와 step_number가 필요합니다.'}, status=400)
    if user_keypoints_raw is None or not isinstance(user_keypoints_raw, dict) or len(user_keypoints_raw) == 0:
        return Response({'error': 'keypoints 데이터가 필요합니다. (JSON body, Content-Type: application/json)'}, status=400)

    # 기준 포즈 가져오기
    try:
        step = PoseStep.objects.get(exercise_id=exercise_id, step_number=step_number)
    except PoseStep.DoesNotExist:
        return Response({'error': '해당 step이 존재하지 않습니다.'}, status=404)

    try:
        # DB에 문자열로 저장된 경우 JSON 우선, 실패 시 eval(기존 데이터 호환)
        try:
            ref_pose = json.loads(step.keypoints)
        except Exception:
            ref_pose = eval(step.keypoints)

        ref_pose_norm = normalize_pose(ref_pose)

        # 프론트(Mediapipe) → 내부 키로 역매핑
        mapped_user_pose = {
            mediapipe_to_yoga[k]: v for k, v in user_keypoints_raw.items() if k in mediapipe_to_yoga
        }
        user_pose_norm = normalize_pose(mapped_user_pose)

        # 각도/좌표 비교
        angle_result, angle_differences = compare_joint_angles(ref_pose_norm, user_pose_norm)
        joint_diff = calculate_joint_diff(ref_pose_norm, user_pose_norm)
        match = bool(angle_result and all(angle_result.values()))

        # GPT 프롬프트 생성
        if match:
            prompt = build_simple_praise_prompt()
        else:
            # GPT가 이해하기 쉬운 형태로 각도차 산출
            diffs_for_gpt = get_joint_angle_differences(ref_pose_norm, user_pose_norm)
            joint_names = list(diffs_for_gpt.keys())
            angle_values = list(diffs_for_gpt.values())
            prompt = build_prompt_with_pose_feedback(joint_names, angle_values)

        # GPT 호출 (키 문제 등 실패하면 피드백만 None으로)
        feedback_text = None
        try:
            feedback_text = query_gpt(prompt)
        except Exception as gpt_err:
            logger.warning("GPT 호출 실패: %s", gpt_err)

        return Response({
            'match': match,
            'angle_differences': angle_differences,
            'joint_differences': joint_diff,
            'feedback_text': feedback_text,
        })

    except Exception as e:
        logger.exception("compare_and_feedback error: %s", e)
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)
