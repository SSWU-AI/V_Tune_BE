# compare/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from data.models import PoseStep
from .utils.pose_utils import normalize_pose, compare_joint_angles, calculate_joint_diff
import traceback

yoga_to_mediapipe = {
    "HEAD": "NOSE", "LSHOULDER": "LEFT_SHOULDER", "RSHOULDER": "RIGHT_SHOULDER",
    "LELBOW": "LEFT_ELBOW", "RELBOW": "RIGHT_ELBOW",
    "LWRIST": "LEFT_WRIST", "RWRIST": "RIGHT_WRIST",
    "LHIP": "LEFT_HIP", "RHIP": "RIGHT_HIP",
    "LKNEE": "LEFT_KNEE", "RKNEE": "RIGHT_KNEE",
    "LANKLE": "LEFT_ANKLE", "RANKLE": "RIGHT_ANKLE"
}

@api_view(['POST'])
def compare_pose(request):
    exercise_id = request.query_params.get('exercise_id')
    step_number = request.query_params.get('step_number')
    user_keypoints_raw = request.data.get('keypoints')

    if exercise_id is None or step_number is None:
        return Response({'error': 'exercise_id와 step_number가 필요합니다.'}, status=400)
    if not user_keypoints_raw:
        return Response({'error': 'keypoints 데이터가 필요합니다.'}, status=400)

    try:
        step = PoseStep.objects.get(exercise_id=exercise_id, step_number=step_number)
    except PoseStep.DoesNotExist:
        return Response({'error': '해당 step이 존재하지 않습니다.'}, status=404)

    try:
        ref_pose = eval(step.keypoints)
        ref_pose_norm = normalize_pose(ref_pose)

        # ✅ 여기에 디버그 출력 추가
        # 역매핑: MediaPipe → 요가 명칭
        mediapipe_to_yoga = {v: k for k, v in yoga_to_mediapipe.items()}

        # 입력값 변환
        mapped_user_pose = {
            mediapipe_to_yoga[k]: v for k, v in user_keypoints_raw.items() if k in mediapipe_to_yoga
        }

        print("🧾 원본 user_keypoints_raw:", user_keypoints_raw)
        print("📍 mapped_user_pose:", mapped_user_pose)

        user_pose_norm = normalize_pose(mapped_user_pose)

        angle_result, angle_differences = compare_joint_angles(ref_pose_norm, user_pose_norm)
        joint_diff = calculate_joint_diff(ref_pose_norm, user_pose_norm)

        return Response({
            'match': all(angle_result.values()),
            'angle_differences': angle_differences,
            'joint_differences': joint_diff
        })

    except Exception as e:
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)
