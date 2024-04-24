from vlc import MediaPlayer
from datetime import datetime
from threading import Timer
from signal import SIGINT, SIGSTOP, SIGCONT
from subprocess import run, DEVNULL
from multiprocessing import Process
from glob import glob
import os
import psutil
import ffmpeg
import cv2



class App:
    def __init__(self, stream: str):
        self.stream: str   = stream



    def __toggleSoundplay(self) -> None:
        self.__can_play_sound = not self.__can_play_sound

    def __toggleSaveImage(self) -> None:
        self.__can_save_image = not self.__can_save_image



    # Get the recording status
    def isRecording(self) -> bool:
        return self.__is_recording


    # Initialize the video capture
    def initVideo(self, video_name: str, fps: float, res: tuple) -> None:
        self.__is_recording:   bool  = True
        self.__can_play_sound: bool  = True
        self.__can_save_image: bool  = True
        self.__resolution:     tuple = res
        self.__keys:           dict  = {}
        self.__cascade:        any   = None

        self.__cap = cv2.VideoCapture(self.stream)
        self.__out = cv2.VideoWriter(
            video_name,
            cv2.VideoWriter_fourcc(*'mp4v'), 
            fps,
            res,
            True
        )


    # Quits the application
    def exitApp(self):
        print('[EXIT] Terminating...')

        self.__cap.release()
        self.__out.release()
        cv2.destroyAllWindows()

        PIDs: list = psutil.Process(os.getppid()) \
                           .children(recursive=True)
        PIDs.reverse()

        for pid in PIDs:
            os.kill(pid.pid, SIGINT)


    # Plays the sound effect
    def playSound(self, sound_path: str, toggleSoundTime: float) -> None:
        if not self.__can_play_sound:
            return

        MediaPlayer(sound_path).play()

        self.__can_play_sound = False
        Timer(toggleSoundTime, self.__toggleSoundplay).start()


    # Toggles the recording
    def toggleRecording(self, audio: bool) -> None:
        self.__is_recording = not self.__is_recording

        if not audio:
            return

        if not self.__is_recording:
            # Stopped recording
            PIDs: list = psutil.Process(os.getppid()) \
                            .children(recursive=True)
            ff:   list = list(filter(lambda x: x.name() == 'ffmpeg', PIDs))
            
            if len(ff):
                os.kill(ff[0].pid, SIGINT)

            return


        # Resumed recording
        outputs: list = glob('output/output*.wav')

        p: Process = Process(target=self.captureAudio, args=(f'output/output{len(outputs) + 1}.wav',))
        p.start()


    # Set the detection cascade
    def setCascade(self, xml: str) -> None:
        self.__cascade = cv2.CascadeClassifier(xml)


    # Search for the detection
    def getCascadeDetection(self, frame) -> list:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        return self.__cascade.detectMultiScale(gray, 1.1, 6, minSize=(80, 80))


    # Mark the detection and save it as an image
    def saveCascadeImage(self, frame, saveTo: str, toggleSaveTime: float, x: int, y: int, w: int, h: int) -> None:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        if self.__can_save_image:
            cv2.imwrite(f"{saveTo}/{datetime.now().strftime('%y-%m-%d_%H:%M:%S.jpg')}", frame)

        self.__can_save_image = False
        Timer(toggleSaveTime, self.__toggleSaveImage).start()


    # Bind the key to an action
    def bindKey(self, key: str, action) -> None:
        self.__keys[ord(key)] = action


    # Saves the video frame
    def saveFrame(self, frame) -> None:
        if self.__is_recording:
            self.__out.write(frame)


    # Display the text on the frame
    def displayText(self, frame, text: str, color: tuple, pos: str or tuple) -> None:
        txt_w, txt_h = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]

        if pos == 'tr':
            pos = (self.__resolution[0] - txt_w, txt_h + 5)
        elif pos == 'br':
            pos = (self.__resolution[0] - txt_w, self.__resolution[1] - txt_h)

        cv2.putText(
            frame, 
            text, 
            pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )


    # Capture the audio
    def captureAudio(self, output_name: str, deleteCurrent: bool = False) -> None:
        if deleteCurrent:
            file, ext = os.path.splitext(output_name) 

            for x in glob(f'{file}*{ext}'):
                os.remove(x)


        ffobj = ffmpeg.input(self.stream) \
                      .audio \
                      .filter('volume', volume=8) \
                      .output(output_name)

        try:
            ffmpeg.run(ffobj, overwrite_output=True, quiet=True)
        except: pass


    # Merge both video and audio
    def mergeSources(self, mp4: str, wav: str, output: str) -> None:
        print('[INFO] Merging sound...')

        file, ext = os.path.splitext(wav)

        output_files: list = glob(f'{file}*{ext}')
        output_len:   int  = len(output_files)
        
        if output_len > 1:
            audio_sources: list = []
            output_maps:   str  = ''

            output_files.sort()

            for i,x in enumerate(output_files):
                output_maps += f'[{i}:0]'
                audio_sources.extend(['-i', x])


            run([
                'ffmpeg', *audio_sources,
                '-filter_complex', f"{output_maps}concat=n={output_len}:v=0:a=1[out]",
                '-map', "[out]", 
                '-y', 'merged_audio.wav'
            ], stdout=DEVNULL, stderr=DEVNULL)

            for x in output_files:
                os.remove(x)

            os.rename('merged_audio.wav', wav)


        run([
            'ffmpeg',
            '-i', mp4,
            '-i', wav,
            '-c:v', 'copy', '-c:a', 'aac',
            '-y', output
        ], stdout=DEVNULL, stderr=DEVNULL)


    # Start capturing the stream
    def startCapturing(self, fn) -> None:
        while self.__cap.isOpened():
            _, frame = self.__cap.read()
            frame    = cv2.resize(frame, self.__resolution, interpolation=cv2.INTER_AREA)

            fn(frame)

            cv2.imshow('view', frame)

            key: int = cv2.waitKey(10)
            if key in self.__keys:
                self.__keys[key]()