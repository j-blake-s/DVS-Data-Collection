import cv2
import numpy as np
import time
from PIL import Image
import os
import signal
import uuid

class DVSCamera:
    def __init__(self, update_display_callback, check_running_callback):
        self.current_frame = None
        self.is_recording = False
        self.recorded_frames = []
        self.recorded_data = None
        self.update_display = update_display_callback
        self.check_running = check_running_callback

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
            self.update_display(self.current_frame)
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
            self.update_display(frame)
            self.current_frame = frame

    def get_frame(self):
        """Returns the current frame being displayed"""
        return self.current_frame