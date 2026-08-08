import os
from pathlib import Path

import numpy as np
from PIL import Image


class EncodeMessage:
    @staticmethod
    def _validate_image_mode(image):
        if image.mode not in {"RGB", "RGBA"}:
            raise ValueError(f"Image format not supported: {image.mode}")

    def encode_message_(self, image_path, message, stop_indicator, output_dir, output_file_path=None):
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError("Selected image does not exist.")
        if not stop_indicator:
            raise ValueError("Password is required.")

        if output_file_path:
            output_path = Path(output_file_path)
            if not output_path.suffix:
                output_path = output_path.with_name(f"{image_path.stem}_encoded.png")
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            base_dir = Path(output_dir) / "encoded_images"
            base_dir.mkdir(parents=True, exist_ok=True)
            output_path = base_dir / f"{image_path.stem}_encoded.png"

        image = Image.open(image_path, "r")
        self._validate_image_mode(image)

        width, height = image.size
        img_arr = np.array(list(image.getdata()))

        channels = 4 if image.mode == "RGBA" else 3
        pixels = img_arr.size // channels

        payload = f"{message}{stop_indicator}"
        byte_msg = "".join(f"{ord(char):08b}" for char in payload)
        bits = len(byte_msg)

        if bits > pixels:
            raise ValueError("Insufficient space to hide message in the selected image.")

        bit_index = 0
        for i in range(pixels):
            for j in range(0, 3):
                if bit_index < bits:
                    img_arr[i][j] = (img_arr[i][j] & ~1) | int(byte_msg[bit_index])
                    bit_index += 1

        img_arr = img_arr.reshape((height, width, channels))
        result = Image.fromarray(img_arr.astype("uint8"), image.mode)

        result.save(output_path)
        return str(output_path)

    def decode_message(self, image_path, stop_indicator):
        image = Image.open(image_path, "r")
        self._validate_image_mode(image)

        img_arr = np.array(list(image.getdata()))
        channels = 4 if image.mode == "RGBA" else 3
        pixels = img_arr.size // channels

        secret_bits = [str(img_arr[i][j] & 1) for i in range(pixels) for j in range(0, 3)]
        secret_bits = "".join(secret_bits)
        secret_bits = [secret_bits[i:i + 8] for i in range(0, len(secret_bits), 8)]
        secret_msg = "".join(chr(int(chunk, 2)) for chunk in secret_bits)

        if stop_indicator not in secret_msg:
            raise ValueError("Could not decode message. Password may be incorrect.")

        return secret_msg[:secret_msg.index(stop_indicator)]

