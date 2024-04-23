from App import App
from utils import getDetectionStatus, getRecordStatus
from dotenv import load_dotenv
from os import getenv, path, mkdir



if __name__ == '__main__':
    load_dotenv('.env')

    RTSP:       str = getenv('RTSP')
    WAV_SOUND:  str = 'alert.wav'
    VIDEO_NAME: str = 'output.mp4'
    IMGS_PATH:  str = 'detected'
    CASCADE:    str = 'xml/haarcascade_front.xml'
    RESOLUTION: tuple = (800, 600)
    FPS:        float = 15.0

    APP = App(RTSP, VIDEO_NAME, FPS, RESOLUTION)


    if not path.exists(IMGS_PATH):
        mkdir(IMGS_PATH)


    def main(frame) -> None:
        faces:    list = APP.getCascade(frame)
        detect_i: dict = getDetectionStatus(len(faces))
        status_i: dict = getRecordStatus(APP.is_recording)

        if len(faces):
            APP.playSound(WAV_SOUND, 5.0)

            for dim in faces:
                APP.saveCascadeImage(frame, IMGS_PATH, *dim)


        APP.displayText(frame, detect_i['text'], detect_i['color'], 'tr')
        APP.displayText(frame, status_i['text'], status_i['color'], 'br')

        APP.saveFrame(frame)


    APP.setCascade(CASCADE)

    APP.bindKey('q', APP.exitApp)
    APP.bindKey('r', APP.toggleRecording)

    APP.startCapturing(main)
