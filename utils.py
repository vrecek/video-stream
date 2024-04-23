def getRecordStatus(is_recording: bool) -> dict:
    if is_recording:
        return { "text": "Recording: Yes", "color": (0, 255, 0) }

    return { "text": "Recording: No",  "color": (0, 0, 255) }



def getDetectionStatus(detect_len: int) -> dict:
    if detect_len:
        return { "text": "STATUS: Detected", "color": (0, 0, 255) }

    return { "text": "STATUS: Clear", "color": (0, 255, 0) }