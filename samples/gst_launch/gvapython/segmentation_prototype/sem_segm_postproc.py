import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')
gi.require_version("GstVideo", "1.0")
from gi.repository import GObject, Gst, GstApp, GstVideo, GLib

from gstgva import VideoFrame
from gstgva import Tensor
import numpy as np
import cv2 as cv

color_mask = {0: [255, 0, 0],
              1: [0, 255, 0],
              2: [0, 0, 255],
              3: [255, 255, 0],
              4: [0, 255, 255],
              5: [255, 0, 255],
              6: [255, 170, 0],
              7: [255, 0, 170],
              8: [0, 255, 170],
              9: [170, 255, 0],
              10: [170, 0, 255],
              11: [0, 170, 255],
              12: [255, 85, 0],
              13: [85, 255, 0],
              14: [0, 255, 85],
              15: [0, 85, 255],
              16: [85, 0, 255],
              17: [127, 127, 0],
              18: [0, 127, 127],
              19: [127, 0, 127],
              }

frame_num = 0
def process_frame(frame: VideoFrame) -> bool:
    global frame_num
    frame_num += 1
    try:
        frame_w = frame.video_meta().width
        frame_h = frame.video_meta().height
        with frame.data() as frame_img:
            frame_img = frame_img.reshape(
                (frame_h, frame_w, 3))  # 3 - should be BGR type
            for tensor in frame.tensors():
                data = tensor.data()
                mask = data.reshape((1024, 2048))  # model output shape
                color_image = np.zeros((1024, 2048, 3))
                for i, row in enumerate(mask):
                    for j, col in enumerate(row):
                        color_image[i, j] = color_mask[col]

                color_image = cv.resize(
                    color_image, (frame_w, frame_h))

                segm_img = color_image + frame_img
                segm_img /= segm_img.max() / 255.0

                cv.imwrite(
                    "segm_frames/segmented_image_{}.png".format(frame_num), segm_img)
    except Exception as e:
        print("Exception:", e)
        return False
    return True


if __name__ == "__main__":
    data = np.zeros((1024 * 2048))
    mask = data.reshape((1024, 2048))
