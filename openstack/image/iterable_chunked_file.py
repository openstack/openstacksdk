#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#


class IterableChunkedFile(object):
    """File object chunk iterator using yield.

    Represents a local file as an iterable object by splitting the file
    into chunks. Avoids the file from being completely loaded into memory.
    """

    def __init__(self, file_object, chunk_size=1024 * 1024 * 128, close=False):
        self.close_after_read = close
        self.file_object = file_object
        self.chunk_size = chunk_size

    def __iter__(self):
        try:
            while True:
                data = self.file_object.read(self.chunk_size)
                if not data:
                    break
                yield data
        finally:
            if self.close_after_read:
                self.file_object.close()

    def __len__(self):
        return len(self.file_object)
