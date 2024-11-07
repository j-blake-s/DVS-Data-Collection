import sys
import os
import uuid
import signal
import numpy as np
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QFrame
from PySide6.QtCore import Qt, QTimer, QThread, Signal, Slot
from PySide6.QtGui import QPixmap, QImage
from camera import DVSCamera
import threading


class CameraThread(QThread):
    update_display_signal = Signal(np.ndarray)

    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        self.is_running = True

    def run(self):
        print("camera thread started")
        # while self.is_running:
        while True:
            frame = self.camera.get_frame()
            print(frame)
            # print("frame is retrieved")
            if frame is not None:
                self.update_display_signal.emit(frame)
                print("frame emitted because it was not none")

    def stop(self):
        self.is_running = False

class RoundedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("background-color: #FFD700; border-radius: 10px;")  # Gold color with rounded corners
        
    def enable_action(self):
        self.setEnabled(True)
        
    def disable_action(self):
        self.setEnabled(False)

class DVSInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.replaying = False
        self.running = True
        self.settings = Settings()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("DVS Data Collection")
        self.setGeometry(100, 100, 1280, 1024)
        self.setStyleSheet("background-color: #F8F8FF;")  # Ghost White background

        # Create main layout
        layout = QVBoxLayout(self)
        
        # Create display label
        self.display_label = QLabel(self)
        layout.addWidget(self.display_label)

        # Create username input section
        self.username_label = QLabel("Enter your name:", self)
        self.username_entry = QLineEdit(self)
        self.submit_button = RoundedButton("Submit", self)
        self.submit_button.clicked.connect(self.submit_username)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_entry)
        layout.addWidget(self.submit_button)

    def submit_username(self):
        username = self.username_entry.text()
        if username:
            self.settings.set_username(username)
            self.create_main_screen()

    def create_main_screen(self):
        # Clear the layout
        for i in reversed(range(self.layout().count())): 
            widget = self.layout().itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Create display label
        self.display_label = QLabel(self)
        self.layout().addWidget(self.display_label)

        # Create buttons
        self.record_button = RoundedButton("Record", self)
        self.replay_button = RoundedButton("Replay", self)
        self.save_button = RoundedButton("Save", self)
        self.delete_button = RoundedButton("Delete", self)

        # Connect button signals
        self.record_button.clicked.connect(self.start_recording)
        self.replay_button.clicked.connect(DVSManager.get_instance().show_replay)
        self.save_button.clicked.connect(DVSManager.get_instance().save_recording)
        self.delete_button.clicked.connect(DVSManager.get_instance().delete_recording)

        # Add buttons to layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.record_button)
        button_layout.addWidget(self.replay_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)
        
        self.layout().addLayout(button_layout)

    def start_recording(self):
        self.is_recording = True
        self.record_button.disable_action()

    def finish_recording(self):
        self.is_recording = False
        print("Recording finished")

    @Slot(np.ndarray)
    def update_display(self, image):

        try:
            if image is None:
                print("image is none")
                return
            # print("image is not none")
            # Convert PIL Image to QImage
            image_array = np.array(image)
            height, width, channels = image_array.shape
            qimage = QImage(image_array.data, width, height, width * channels, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            self.display_label.setPixmap(pixmap)
        except Exception as e:
            print(f"Error updating display: {e}")

    def closeEvent(self, event):
        self.running = False
        DVSManager.get_instance().shut_down()
        super().closeEvent(event)

class Settings:
    def __init__(self):
        self.username = None
        self.selected_label = None
        self.save_dir = "recordings"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
    def set_username(self, username):
        self.username = username
        
    def get_duration_seconds(self):
        return 5  # Default recording duration
        
    def get_label_index(self, label):
        return 0  # Default label index

class CameraManagerThread(QThread):
    update_display_signal = Signal(np.ndarray)
    def __init__(self, camera, interface, parent=None):
        super().__init__(parent)

        self.camera = camera
        self.interface = interface
        self.running = True
        self.recording_ended = True

    def run(self):
        # Start preview immediately
        self.camera.preview()
        
        while self.running:
            if self.recording_ended:
                self.recording_ended = False
            try:
                if self.interface.is_recording:
                    seconds = self.interface.settings.get_duration_seconds()
                    self.camera.record(seconds)
                    self.camera.playback_recording()
                    while (not self.recording_ended) and (self.running):
                        if self.interface.replaying:
                            self.camera.playback_recording()
                            self.interface.replaying = False
                            self.interface.replay_button.enable_action()
                    self.camera.is_recording = False
                    self.interface.is_recording = False
                    print("Recording cycle completed.")
                    self.camera.preview()  # Return to preview after recording
            except Exception as e:
                print(f"Error in manage_camera: {e}")
                self.camera.preview()  # Return to preview on error
        print("manage camera ended")

    def stop(self):
        self.running = False
        self.recording_ended = True


class DVSManager:
    instance = None

    @staticmethod
    def get_instance():
        if DVSManager.instance is None:
            DVSManager.instance = DVSManager()
        return DVSManager.instance

    def __init__(self):
        self.interface = DVSInterface()
        self.camera = DVSCamera(update_display_callback=self.interface.update_display,
                              check_running_callback=self.check_running)
        self.recording_ended = True
        self.trial_number = 0
        self.running = True

    def shut_down(self):
        self.running = False
        self.recording_ended = True
        os.kill(os.getpid(), signal.SIGTERM)

    def save_recording(self):
        username = self.interface.settings.username
        label = self.interface.settings.selected_label
        unique_id = str(uuid.uuid4())[:4]  # Take first 4 characters of UUID
        filename = f"{username}{self.trial_number}_{label}_{unique_id}"
        save_path = os.path.join(self.interface.settings.save_dir, filename)
        print("Saving recorded data...")
        boolean_data = self.camera.recorded_data.astype(bool)
        label_index = self.interface.settings.get_label_index(label)
        np.savez_compressed(save_path, x=boolean_data, y=np.array([label_index]))
        self.recording_ended = True
        self.camera.recorded_frames = []
        self.trial_number += 1

    def delete_recording(self):
        self.camera.recorded_frames = []
        self.recording_ended = True

    def show_replay(self):
        self.camera.playback_recording()

    def check_running(self):
        return self.running

    # def update_display(self):
    #     while self.running:
    #         self.interface.update_display(self.camera.current_frame)
    #         if self.interface.is_recording:
    #             self.camera.is_recording = True
    #     print("update display ended")

    def show_replay(self):
        self.camera.playback_recording()


    def run(self):
        self.camera.preview()
        camera_thread = CameraThread(self.camera)
        camera_thread.update_display_signal.connect(self.interface.update_display)
        camera_thread.start()

        self.interface.show()
        print("interface shown")

    def check_running(self):
        return self.running

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = DVSManager.get_instance()
    manager.run()
    sys.exit(app.exec())