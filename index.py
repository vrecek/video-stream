from App import App
from utils import getDetectionStatus, getRecordStatus
from dotenv import load_dotenv
from os import getenv, path, mkdir
from multiprocessing import Process
from signal import signal, SIGINT



if __name__ == '__main__':
    load_dotenv('.env')

    RTSP:       str = getenv('RTSP')
    VIDEO_NAME: str = 'output/output.mp4'
    AUDIO_NAME: str = 'output/output.wav'
    
    def mainAudio() -> None:
        signal(SIGINT, lambda sig,frame: exit(0))

        APP: App = App(RTSP)
        APP.captureAudio(AUDIO_NAME, True)


    def mainVideo() -> None:
        signal(SIGINT, lambda sig,frame: exit(0))

        RESOLUTION: tuple = (800, 600)
        FPS:        float = 15.0
        WAV_SOUND:  str = 'alert.wav'
        IMGS_PATH:  str = 'output/detected'
        CASCADE:    str = 'xml/haarcascade_front.xml'
        APP:        App = App(RTSP)


        def mainLoop(frame) -> None:
            faces:     list = APP.getCascadeDetection(frame)
            faces_len: int  = len(faces)
            detect_i:  dict = getDetectionStatus(faces_len)
            status_i:  dict = getRecordStatus(APP.isRecording())

            if faces_len:
                for dim in faces:
                    APP.saveCascadeImage(frame, IMGS_PATH, 1.0, *dim)
                    
                APP.playSound(WAV_SOUND, 5.0)


            APP.displayText(frame, detect_i['text'], detect_i['color'], 'tr')
            APP.displayText(frame, status_i['text'], status_i['color'], 'br')

            APP.saveFrame(frame)


        APP.initVideo(VIDEO_NAME, FPS, RESOLUTION)
        APP.setCascade(CASCADE)

        APP.bindKey('q', APP.exitApp)
        APP.bindKey('r', lambda: APP.toggleRecording(True))

        APP.startCapturing(mainLoop)


    
    p: list[Process] = [
        Process(target=mainVideo),
        Process(target=mainAudio)
    ]

    for process in p:
        process.start()

    p[0].join()


    App(RTSP).mergeSources(VIDEO_NAME, AUDIO_NAME, 'output/merged.mp4')

