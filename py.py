import os
import subprocess

def folder_is_clean(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            if not f.endswith(".py"):
                return False
    return True

for item in os.listdir("."):
    if os.path.isdir(item):
        if folder_is_clean(item):
            subprocess.run(["git", "add", item])
