import os
import subprocess

# peer.pyを繰り返し実行する
dir = os.path.dirname(os.path.abspath(__file__))
while True:
    subprocess.run(['Python', os.path.join(dir, 'peer.py')])
    