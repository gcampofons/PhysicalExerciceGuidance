"""
MediaPipe pose landmark index constants and body connections.
See: https://developers.google.com/mediapipe/solutions/vision/pose_landmarker
"""

# ── Upper body ────────────────────────────────────────────────────────────────
NOSE            = 0
LEFT_EYE_INNER  = 1
LEFT_EYE        = 2
LEFT_EYE_OUTER  = 3
RIGHT_EYE_INNER = 4
RIGHT_EYE       = 5
RIGHT_EYE_OUTER = 6
LEFT_EAR        = 7
RIGHT_EAR       = 8
MOUTH_LEFT      = 9
MOUTH_RIGHT     = 10

LEFT_SHOULDER   = 11
RIGHT_SHOULDER  = 12
LEFT_ELBOW      = 13
RIGHT_ELBOW     = 14
LEFT_WRIST      = 15
RIGHT_WRIST     = 16
LEFT_PINKY      = 17
RIGHT_PINKY     = 18
LEFT_INDEX      = 19
RIGHT_INDEX     = 20
LEFT_THUMB      = 21
RIGHT_THUMB     = 22

# ── Lower body ────────────────────────────────────────────────────────────────
LEFT_HIP        = 23
RIGHT_HIP       = 24
LEFT_KNEE       = 25
RIGHT_KNEE      = 26
LEFT_ANKLE      = 27
RIGHT_ANKLE     = 28
LEFT_HEEL       = 29
RIGHT_HEEL      = 30
LEFT_FOOT_INDEX = 31
RIGHT_FOOT_INDEX= 32

# ── Skeleton connections for drawing ─────────────────────────────────────────
POSE_CONNECTIONS: list[tuple[int, int]] = [
    # Face
    (NOSE, LEFT_EYE_INNER), (LEFT_EYE_INNER, LEFT_EYE), (LEFT_EYE, LEFT_EYE_OUTER),
    (LEFT_EYE_OUTER, LEFT_EAR),
    (NOSE, RIGHT_EYE_INNER), (RIGHT_EYE_INNER, RIGHT_EYE), (RIGHT_EYE, RIGHT_EYE_OUTER),
    (RIGHT_EYE_OUTER, RIGHT_EAR),
    (MOUTH_LEFT, MOUTH_RIGHT),
    # Torso
    (LEFT_SHOULDER, RIGHT_SHOULDER),
    (LEFT_SHOULDER, LEFT_HIP), (RIGHT_SHOULDER, RIGHT_HIP),
    (LEFT_HIP, RIGHT_HIP),
    # Left arm
    (LEFT_SHOULDER, LEFT_ELBOW), (LEFT_ELBOW, LEFT_WRIST),
    (LEFT_WRIST, LEFT_PINKY), (LEFT_WRIST, LEFT_INDEX), (LEFT_WRIST, LEFT_THUMB),
    (LEFT_PINKY, LEFT_INDEX),
    # Right arm
    (RIGHT_SHOULDER, RIGHT_ELBOW), (RIGHT_ELBOW, RIGHT_WRIST),
    (RIGHT_WRIST, RIGHT_PINKY), (RIGHT_WRIST, RIGHT_INDEX), (RIGHT_WRIST, RIGHT_THUMB),
    (RIGHT_PINKY, RIGHT_INDEX),
    # Left leg
    (LEFT_HIP, LEFT_KNEE), (LEFT_KNEE, LEFT_ANKLE),
    (LEFT_ANKLE, LEFT_HEEL), (LEFT_ANKLE, LEFT_FOOT_INDEX), (LEFT_HEEL, LEFT_FOOT_INDEX),
    # Right leg
    (RIGHT_HIP, RIGHT_KNEE), (RIGHT_KNEE, RIGHT_ANKLE),
    (RIGHT_ANKLE, RIGHT_HEEL), (RIGHT_ANKLE, RIGHT_FOOT_INDEX), (RIGHT_HEEL, RIGHT_FOOT_INDEX),
]
