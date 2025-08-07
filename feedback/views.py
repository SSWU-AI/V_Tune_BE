from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import (
    get_joint_angle_differences,
    build_simple_praise_prompt,
    build_prompt_with_pose_feedback,
    query_gpt
)

@api_view(["POST"])
def feedback_api(request):
    user_pose = request.data.get("user_pose")
    correct_pose = request.data.get("correct_pose")
    result = request.data.get("result")  # "T" or "F"

    if not user_pose or not correct_pose or not result:
        return Response({"error": "Missing required fields"}, status=400)

    # GPT 피드백 텍스트 생성
    if result == "T":
        prompt = build_simple_praise_prompt()
    else:
        angle_diffs = get_joint_angle_differences(correct_pose, user_pose)
        joint_names = list(angle_diffs.keys())
        angle_differences = list(angle_diffs.values())
        prompt = build_prompt_with_pose_feedback(joint_names, angle_differences)

    feedback_text = query_gpt(prompt)

    return Response({"feedback_text": feedback_text})
