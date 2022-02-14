import os
import subprocess

def make_dir():
    os.chdir("data")
    folder_names = filter(os.path.isdir, os.listdir(os.getcwd()))
    num_folders = [int(name) for name in folder_names if name.isnumeric()]
    if (len(num_folders) == 0):
        last_number = -1
    else:
        last_number = max(num_folders)
    new_name = str(last_number + 1)
    os.mkdir(new_name)
    os.chdir("..")
    return new_name
    

index = make_dir()
print("Created new directory {}".format(index))
juggle = subprocess.Popen(["python3","juggle.py"])
os.system("ffmpeg -f video4linux2 -s 640x480 -ss 0:0:1 -i /dev/video0 -vf fps=4 -frames 20 /home/pi/code/data/{}/%02d.jpg".format(index))
juggle.terminate()
