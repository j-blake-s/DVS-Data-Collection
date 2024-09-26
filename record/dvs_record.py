import cv2
import numpy as np
import time
import tkinter as tk
from PIL import ImageTk, Image
import threading
import uuid
import os
import signal

class RecordingSettings:
    def __init__(self):
        self.duration = ""
        self.selected_label = "EMPTY_LABEL"
        self.label_options = {
            0: "Tuesday",
            1: "Bathroom",
            2: "Name",
            3: "Weight",
            4: "Brown",
            5: "Beer",
            6: "Favorite",
            7: "Colors",
            8: "Hamburger",
            9: "Marriage"
        }
        self.duration_options = {1: "2 Seconds", 2: "7 Seconds", 3: "10 Seconds", 4: "20 Seconds"}
        self.username = ""
        self.save_dir = "data"

    def set_duration(self, duration):
        self.duration = duration

    def set_label(self, label):
        self.selected_label = label

    def set_username(self, username):
        self.username = username

    def update_setting(self, input_str):
        if input_str in self.label_options.values():
            self.set_label(input_str)
        else:
            self.set_duration(input_str)

    def get_duration_seconds(self):
        return int(self.duration.split(" ")[0])

    def get_label_index(self, label):
        for key, value in self.label_options.items():
            if value == label:
                return key
        return -1


class DVSInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.frame_display = None
        self.label_buttons = {}
        self.duration_buttons = {}
        self.settings = RecordingSettings()
        self.is_recording = False
        self.countdown_label = None
        self.replaying = False
        self.running = True

    def setup_ui(self):
        self.root.title("DVS Data Collection")
        self._create_username_screen()

    def on_closing(self):
        print("Closing interface...")
        self.running = False
        DVSManager.get_instance().shut_down()
        self.root.quit()
        self.root.destroy()
        print("DVSManager shut down")

    def _create_username_screen(self):
        self.root.geometry("1024x768")
        
        username_frame = tk.Frame(self.root)
        username_frame.pack(expand=True)

        username_label = tk.Label(username_frame, text="Enter your name:", font=("Arial", 16))
        username_label.pack(pady=20)

        username_entry = tk.Entry(username_frame, font=("Arial", 14), width=30)
        username_entry.pack(pady=20)

        submit_button = tk.Button(username_frame, text="Submit", command=lambda: self._submit_username(username_entry.get()), font=("Arial", 14), width=15)
        submit_button.pack(pady=20)
        
        username_entry.bind('<Return>', lambda event: self._submit_username(username_entry.get()))
        username_entry.focus_set()

    def _submit_username(self, username):
        if username:
            self.settings.set_username(username)
            for widget in self.root.winfo_children():
                widget.destroy()
            self._create_main_screen()

    def _create_main_screen(self):
        self._create_frames()
        self._create_buttons()
        self._create_display()

    def _create_frames(self):
        intro_label = tk.Label(self.root, text=f"Welcome to DVS Data Collection, {self.settings.username}!")
        intro_label.pack(pady=10)

        top_frame = tk.Frame(self.root)
        top_frame.pack(expand=True)

        self.left_frame = tk.Frame(top_frame)
        self.left_frame.pack(side="left", padx=5)

        self.countdown_frame = tk.Frame(top_frame)
        self.countdown_frame.pack(side="right", padx=5)

        self.right_frame = tk.Frame(top_frame)
        self.right_frame.pack(anchor=tk.CENTER, side='right', padx=5)

        self.middle_frame = tk.Frame(top_frame, bg="black")
        self.middle_frame.pack(side="right")

    def _create_buttons(self):
        self.countdown_label = tk.Label(self.countdown_frame, text="", font=("Arial", 72, "bold"))
        self.countdown_label.pack(side='top', padx=20)

        for key, value in self.settings.label_options.items():
            button = tk.Button(self.left_frame, text=value, width=20,
                               command=lambda k=key, v=value: self._on_button_click(k, v, self.label_buttons))
            button.pack()
            self.label_buttons[key] = button

        for key, value in self.settings.duration_options.items():
            button = tk.Button(self.middle_frame, text=value, width=20,
                               command=lambda k=key, v=value: self._on_button_click(k, v, self.duration_buttons))
            button.pack()
            self.duration_buttons[key] = button

        button_frame = tk.Frame(self.right_frame)
        button_frame.pack(side='bottom', anchor=tk.CENTER)
        self.record_button = tk.Button(button_frame, text="Record", command=self.start_recording, width=10)
        self.record_button.pack(side='top', pady=5)

        self.save_button = tk.Button(button_frame, text="Save", command=self.save_recording, width=10, state=tk.DISABLED)
        self.save_button.pack(side='top', pady=5)

        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_recording, width=10, state=tk.DISABLED)
        self.delete_button.pack(side='top', pady=5)

        self.replay_button = tk.Button(button_frame, text="Replay", command=self.show_replay, width=10, state=tk.DISABLED)
        self.replay_button.pack(side='top', pady=5)

    def start_recording(self):
        self._countdown(3, "red", "Go!")
        self.is_recording = True
        duration = self.settings.get_duration_seconds()
        self._countdown(duration, "green", "End!")
        print("Countdown ended")
        self._update_button_states(record=tk.DISABLED, others=tk.NORMAL)

    def _countdown(self, duration, color, final_text):
        start_time = time.time()
        while time.time() - start_time < duration:
            remaining = round(duration - (time.time() - start_time))
            text = str(remaining) if remaining > 0 else final_text
            size = 30 if text == final_text else 72
            self.countdown_label.config(text=text, foreground=color, font=("Arial", size))
            self.root.update()

    def _update_button_states(self, record, others):
        self.record_button.config(state=record)
        self.save_button.config(state=others)
        self.delete_button.config(state=others)
        self.replay_button.config(state=others)

    def reset_buttons(self):
        self._update_button_states(record=tk.NORMAL, others=tk.DISABLED)

    def delete_recording(self):
        DVSManager.get_instance().delete_recording()
        self.reset_buttons()
        self.countdown_label.config(text="Deleted!", font=("Arial", 30))

    def save_recording(self):
        DVSManager.get_instance().save_recording()
        self.reset_buttons()
        self.countdown_label.config(text="Saved!", font=("Arial", 30))

    def show_replay(self):
        self.replaying = True

    def _create_display(self):
        self.frame_display = tk.Label(self.root, image=None)
        self.frame_display.pack(side="bottom", pady=20)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def start(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def _on_button_click(self, key, value, buttons):
        buttons[key].config(relief=tk.SUNKEN, activebackground="lightgreen", bg="green")
        for other_key, button in buttons.items():
            if other_key != key:
                button.config(relief=tk.RAISED, bg='#f0f0f0')
        self.settings.update_setting(value)

    def update_display(self, image):
        if not self.running or image is None:
            return
        try:
            img_tk = ImageTk.PhotoImage(image=image)
            self.frame_display.config(image=img_tk)
            self.frame_display.image = img_tk
        except:
            pass

class DVSCamera:
    def __init__(self):
        self.current_frame = None
        self.is_recording = False
        self.recorded_frames = []
        self.recorded_data = None

    def check_running(self):
        return DVSManager.get_instance().running

    def open_camera(self):
        print("Opening Camera...", end="")
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        fps = cam.get(cv2.CAP_PROP_FPS)
        print(f"FPS: {fps}")

        if ret:
            print("Complete")
            return cam, frame.shape[0], frame.shape[1], int(round(fps))
        else:
            print("Failure")
            print("Please check camera!")
            print("Exiting...")
            quit()

    def process_dvs(self, prev, curr, threshold=0.05, light=[162, 249, 84], dark=[255, 139, 237]):
        light = [c / 255. for c in light]
        dark = [c / 255. for c in dark]

        diff = np.mean(curr - prev, axis=-1)
        diff = np.where(np.abs(diff) < threshold, 0, diff)

        data = np.zeros(shape=(1, 2, diff.shape[0], diff.shape[1]), dtype=bool)
        data[0, 0, diff > 0] = True
        data[0, 1, diff < 0] = True

        color = np.zeros_like(curr)
        color[diff > 0, :] = light
        color[diff < 0, :] = dark

        return data, color

    def preview(self):
        print("Starting preview...")
        cam, _, _, fps = self.open_camera()
        _, frame = cam.read()
        prev = np.ones_like(frame) * (frame / 255.)

        while not self.is_recording and self.check_running():
            _, frame = cam.read()
            frame = np.array(frame, np.float32) / 255.
            _, color = self.process_dvs(prev, frame, threshold=0.05)
            array_uint8 = (color * 255).astype(np.uint8)
            self.current_frame = Image.fromarray(array_uint8)
            prev = frame

        cam.release()

    def record(self, duration):
        if not self.check_running():
            return
        print(f"Recording for {duration} seconds...")
        cam, height, width, fps = self.open_camera()
        num_frames = duration * fps
        self.recorded_data = np.zeros(shape=(2, height, width, num_frames), dtype=bool)

        _, frame = cam.read()
        prev = np.ones_like(frame) * (frame / 255.)

        start_time = time.time()
        for i in range(num_frames):
            _, frame = cam.read()
            frame = np.array(frame, np.float32) / 255.
            spikes, color = self.process_dvs(prev, frame, threshold=0.05)
            array_uint8 = (color * 255).astype(np.uint8)
            img = Image.fromarray(array_uint8)
            self.current_frame = img
            self.recorded_frames.append(img)
            self.recorded_data[:, :, :, i] = spikes
            prev = frame

        end_time = time.time()
        print(f"Recording completed in {end_time - start_time:.2f} seconds")
        self.is_recording = False
        cam.release()

    def playback_recording(self):
        if not self.check_running():
            return
        print("Playing back recording...")
        for frame in self.recorded_frames:
            time.sleep(1 / 30)  # Assuming 30 FPS playback
            DVSManager.get_instance().interface.update_display(frame)
            self.current_frame = frame

class DVSManager:
    instance = None

    @staticmethod
    def get_instance():
        if DVSManager.instance is None:
            DVSManager.instance = DVSManager()
        return DVSManager.instance

    def __init__(self):
        self.interface = DVSInterface()
        self.camera = DVSCamera()
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

    def update_display(self):
        while self.running:
            self.interface.update_display(self.camera.current_frame)
            if self.interface.is_recording:
                self.camera.is_recording = True
        print("update display ended")

    def show_replay(self):
        self.camera.playback_recording()

    def manage_camera(self):
        while self.running:
            if self.recording_ended:
                self.recording_ended = False
                self.camera.preview()
            try:
                seconds = self.interface.settings.get_duration_seconds()
                self.camera.record(seconds)
                self.camera.playback_recording()
                while (not self.recording_ended) and (self.running):
                    # print("Waiting for recording to end...")
                    if self.interface.replaying:
                        self.camera.playback_recording()
                        self.interface.replaying = False
                self.camera.is_recording = False
                self.interface.is_recording = False
                print("Recording cycle completed.")
            except Exception as e:
                print(f"Error in manage_camera: {e}")
        print("manage camera ended")

    def run(self):
        self.interface.setup_ui()
        
        camera_thread = threading.Thread(target=self.manage_camera)
        camera_thread.start()

        display_thread = threading.Thread(target=self.update_display)
        display_thread.start()

        self.interface.start()
        camera_thread.join()
        print("camera thread joined")
        display_thread.join()
        print("Threads joined")

if __name__ == "__main__":
    manager = DVSManager.get_instance()
    manager.run()
    print("Program ended")