import os
import run

def downloadcover(fanhao, path):
    run.downloadSpecImg(fanhao, path, False)


path="./work"

for root, dirs, files in os.walk(path):
    for dir in dirs:
        array=dir.split(' ')
        fanhao=array[0]
        path=os.path.join(root,dir)
        videofile=os.path.join(path, fanhao+".mp4")
        if os.path.exists(videofile):
            downloadcover(fanhao, path)

