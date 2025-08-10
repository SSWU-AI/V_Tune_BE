# utils/pose_utils.py
import numpy as np
import math

joints_to_use = [
    "NOSE", "LEFT_SHOULDER", "RIGHT_SHOULDER",
    "LEFT_ELBOW", "RIGHT_ELBOW",
    "LEFT_WRIST", "RIGHT_WRIST",
    "LEFT_HIP", "RIGHT_HIP",
    "LEFT_KNEE", "RIGHT_KNEE",
    "LEFT_ANKLE", "RIGHT_ANKLE"
]

angle_joints = [
    ("LEFT_ELBOW", "LEFT_SHOULDER", "LEFT_WRIST"),
    ("RIGHT_ELBOW", "RIGHT_SHOULDER", "RIGHT_WRIST"),
    ("LEFT_KNEE", "LEFT_HIP", "LEFT_ANKLE"),
    ("RIGHT_KNEE", "RIGHT_HIP", "RIGHT_ANKLE")
]

def normalize_pose(pose_dict):
    if not pose_dict or any(v is None or len(v) != 2 for v in pose_dict.values()):
        raise ValueError("normalize_pose에 전달된 pose_dict가 비어 있거나 잘못된 형식입니다.")

    xs, ys = zip(*pose_dict.values())
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    return {
        joint: (
            (x - x_min) / (x_max - x_min + 1e-6),
            (y - y_min) / (y_max - y_min + 1e-6)
        )
        for joint, (x, y) in pose_dict.items()
    }


def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def compare_joint_angles(ref_pose, user_pose):
    joints_to_use = {
        "LELBOW": ("LSHOULDER", "LELBOW", "LWRIST"),
        "RELBOW": ("RSHOULDER", "RELBOW", "RWRIST"),
        "LKNEE": ("LHIP", "LKNEE", "LANKLE"),
        "RKNEE": ("RHIP", "RKNEE", "RANKLE"),
    }

    angle_result = {}
    angle_differences = {}

    # ✅ 여기에 디버깅 추가
    print("🧠 ref_pose keys:", list(ref_pose.keys()))
    print("🧠 user_pose keys:", list(user_pose.keys()))

    for joint_name, (a, b, c) in joints_to_use.items():
        try:
            print(f"🔍 Comparing angles for: {a}, {b}, {c}")
            ref_angle = calculate_angle(ref_pose[a], ref_pose[b], ref_pose[c])
            user_angle = calculate_angle(user_pose[a], user_pose[b], user_pose[c])
        except KeyError as e:
            print(f"❌ KeyError during angle calc for {joint_name}: {e}")
            angle_result[joint_name] = False
            angle_differences[joint_name] = None
            continue

        if ref_angle is None or user_angle is None:
            angle_result[joint_name] = False
            angle_differences[joint_name] = None
        else:
            diff = abs(ref_angle - user_angle)
            angle_result[joint_name] = diff < 50
            angle_differences[joint_name] = round(diff, 2)

    return angle_result, angle_differences


def calculate_joint_diff(ref_pose, user_pose):
    joint_diff = {}

    for joint in ref_pose:
        if joint in user_pose:
            ref_x, ref_y = ref_pose[joint]
            user_x, user_y = user_pose[joint]
            dx = round(abs(ref_x - user_x), 2)
            dy = round(abs(ref_y - user_y), 2)
            joint_diff[joint] = (dx, dy)
        else:
            joint_diff[joint] = None

    return joint_diff


def compare_angles(ref_pose, user_pose):
    angle_diffs = {}
    for center, a, b in angle_joints:
        if all(j in user_pose and j in ref_pose for j in (a, center, b)):
            ref_angle = calculate_angle(ref_pose[a], ref_pose[center], ref_pose[b])
            user_angle = calculate_angle(user_pose[a], user_pose[center], user_pose[b])
            angle_diffs[center] = round(abs(ref_angle - user_angle), 2)
        else:
            angle_diffs[center] = None
    return angle_diffs

def compare_all_joints(ref_pose, user_pose):
    # 각 관절 쌍에 대해 유클리드 거리 비교 (모든 관절)
    joint_diffs = {}
    for joint in joints_to_use:
        if joint in ref_pose and joint in user_pose:
            ref = np.array(ref_pose[joint])
            user = np.array(user_pose[joint])
            diff = np.linalg.norm(ref - user)
            joint_diffs[joint] = round(float(diff), 4)
        else:
            joint_diffs[joint] = None
    return joint_diffs
