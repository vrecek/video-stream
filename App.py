from vlc import MediaPlayer
from datetime import datetime
from threading import Timer
import cv2


class App:
    def __init__(self, stream: str, video_name: str, fps: float, res: tuple):
        self.is_recording:   bool  = True
        self.can_play_sound: bool  = True
        self.cascade:        any   = None
        self.resolution:     tuple = res
        self.video_name:     str   = video_name
        self.__keys:         dict  = {}

        self.cap = cv2.VideoCapture(stream)
        self.out = cv2.VideoWriter(
            video_name,
            cv2.VideoWriter_fourcc(*'mp4v'), 
            fps,
            res,
            True
        )


    # Quits the application
    def exitApp(self):
        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()


    # Plays the sound effect
    def playSound(self, sound_path: str, toggleSoundTime: float) -> None:
        if not self.can_play_sound:
            return

        self.can_play_sound = False
        MediaPlayer(sound_path).play()

        Timer(toggleSoundTime, self.toggleSoundplay).start()


    # Toggles the recording
    def toggleRecording(self) -> None:
        self.is_recording = not self.is_recording


    # Toggles the sound
    def toggleSoundplay(self) -> None:
        self.can_play_sound = not self.can_play_sound


    # Set the detection cascade
    def setCascade(self, xml: str) -> None:
        self.cascade = cv2.CascadeClassifier(xml)


    # Search for the detection
    def getCascade(self, frame) -> list:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        return self.cascade.detectMultiScale(gray, 1.2, 4, minSize=(80, 80))


    # Mark the detection and save it as an image
    def saveCascadeImage(self, frame, saveTo: str, x: int, y: int, w: int, h: int) -> None:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.imwrite(f"{saveTo}/{datetime.now().strftime('%y-%m-%d_%H:%M:%S.jpg')}", frame)


    # Bind the key to an action
    def bindKey(self, key: str, action) -> None:
        self.__keys[ord(key)] = action


    # Saves the video frame
    def saveFrame(self, frame) -> None:
        if self.is_recording:
            self.out.write(frame)


    # Display the text on the frame
    def displayText(self, frame, text: str, color: tuple, pos: str) -> None:
        txt_w, txt_h = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]

        if pos == 'tr':
            pos = (self.resolution[0] - txt_w, txt_h + 5)
        elif pos == 'br':
            pos = (self.resolution[0] - txt_w, self.resolution[1] - txt_h)
        else:
            pos = (0, 0)

        cv2.putText(
            frame, 
            text, 
            pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )


    # Start capturing the stream
    def startCapturing(self, fn) -> None:
        while self.cap.isOpened():
            _, frame = self.cap.read()
            frame    = cv2.resize(frame, self.resolution, interpolation=cv2.INTER_AREA)

            fn(frame)

            cv2.imshow('view', frame)

            key: int = cv2.waitKey(10)
            if key in self.__keys:
                self.__keys[key]()