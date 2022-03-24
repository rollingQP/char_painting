# -*- coding=utf-8 -*-
# =========================
# 视频转字符画含音频version-2.3
# 参考1：https://blog.csdn.net/mp624183768/article/details/81161260
# 参考2：https://blog.csdn.net/qq_42820064/article/details/90958577
# 参考3：https://blog.csdn.net/zj360202/article/details/79026891
# =========================
import sys
import os
import time
import shutil
import tempfile
import platform
from multiprocessing import Process

try:
    from PIL import Image, ImageFont, ImageDraw
except ImportError:
    os.system('pip3 install Pillow -i https://mirrors.aliyun.com/pypi/simple/')
    from PIL import _imaging, Image, ImageFont, ImageDraw

try:
    import cv2
    from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize
except ImportError:
    os.system('pip3 install opencv-python-headless -i https://mirrors.aliyun.com/pypi/simple/')
    import cv2
    from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize


def get_char(r, g, b, alpha=256):
    # ascii_char = list("#RMNHQODBWGPZ*@$C&98?32I1>!:-;. ")
    ascii_char = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:oa+>!:+. ")
    if alpha == 0:
        return ''
    length = len(ascii_char)
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
    unit = (256.0 + 1) / len(ascii_char)
    return ascii_char[int(gray / unit)]


# 将视频转换为图片 并进行计数，返回总共生成了多少张图片！
def video_to_pic(vp, save_pic_path):
    print('\n正在对视频进行逐帧切片，请稍候...')
    # vp = cv2.VideoCapture(video_path)
    number = 0
    if vp.isOpened():
        r, frame = vp.read()
        if not os.path.exists(save_pic_path):
            os.mkdir(save_pic_path)
        #os.chdir(save_pic_path)
    else:
        r = False
    while r:
        number += 1
        cv2.imwrite(save_pic_path + '/' + str(number) + '.jpg', frame)
        r, frame = vp.read()
    print('由视频一共生成了{}张图片！'.format(number))
    #os.chdir(save_pic_path)
    # os.chdir("../../../Downloads")
    return number


def img_to_char(image_path, save_charpic_path, raw_width, raw_height, task):
    width = int(raw_width / 6)  # 默认 /6
    height = int(raw_height / 10)  # 默认 /15
    os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))
    im = Image.open(image_path).convert('RGB')  # 必须以RGB模式打开
    im = im.resize((width, height), Image.NEAREST)

    txt = ''
    color = []
    for i in range(height):
        for j in range(width):
            pixel = im.getpixel((j, i))
            color.append((pixel[0], pixel[1], pixel[2]))  # 将颜色加入进行索引
            if len(pixel) == 4:
                txt += get_char(pixel[0], pixel[1], pixel[2], pixel[3])
            else:
                txt += get_char(pixel[0], pixel[1], pixel[2])
        txt += '\n'
        color.append((255, 255, 255))

    im_txt = Image.new("RGB", (raw_width, raw_height), (255, 255, 255))
    dr = ImageDraw.Draw(im_txt)
    # font = ImageFont.truetype('consola.ttf', 10, encoding='unic') #改为这个字体会让图片比例改变
    font = ImageFont.load_default().font
    x, y = 0, 0
    font_w, font_h = font.getsize(txt[1])
    font_h *= 0.91  # 调整字体大小 默认1.37
    for i in range(len(txt)):
        if (txt[i] == '\n'):
            x += font_h
            y = -font_w
        dr.text((y, x), txt[i], fill=color[i])
        y += font_w
    os.chdir(save_charpic_path)
    # os.chdir('cache_char')
    im_txt.save(save_charpic_path + '/' + str(task) + '.jpg')
    os.chdir(save_charpic_path)
    # os.chdir("../../../Downloads")
    return 0


# 使用多进程进行图片转字符画，number是cahce_pic中图片总数，start_number是该进程从第几副图开始做，end_number是该进程到第几副图结束。
class StarToCharMultiProcess(Process):
    def __init__(self, threadID, number, save_pic_path, save_charpic_path, start_number, end_number):
        super().__init__()
        self.threadID = threadID
        self.number = number
        self.save_pic_path = save_pic_path
        self.save_charpic_path = save_charpic_path
        self.start_number = start_number
        self.end_number = end_number

    def run(self):
        print("开始进程：" + self.name)
        star_to_char2(self.number, self.save_pic_path, self.save_charpic_path, self.start_number, self.end_number)
        print("退出进程：" + self.name)


def star_to_char(number, save_pic_path):
    if not os.path.exists('cache_char'):
        os.mkdir('cache_char')
    img_path_list = [save_pic_path + r'/{}.jpg'.format(i) for i in range(1, number + 1)]  # 生成目标图片文件的路径列表
    task = 0
    for image_path in img_path_list:
        img_width, img_height = Image.open(image_path).size  # 获取图片的分辨率
        task += 1
        img_to_char(image_path, img_width, img_height, task)
        print('{}/{} is finished.'.format(task, number))
    print('=======================')
    print('All images were finished!')
    print('=======================')
    return 0


def star_to_char2(number, save_pic_path, save_charpic_path, start_number, end_number):
    # os.chdir(save_charpic_path)
    if not os.path.exists(save_charpic_path):
        try:
            os.mkdir(save_charpic_path)
        except:
            pass
    img_path_list = [save_pic_path + r'/{}.jpg'.format(i) for i in range(start_number, end_number + 1)]  # 生成目标图片文件的路径列表
    task = start_number - 1
    for image_path in img_path_list:
        img_width, img_height = Image.open(image_path).size  # 获取图片的分辨率
        task += 1
        img_to_char(image_path, save_charpic_path, img_width, img_height, task)
        # print('{}/{} is finished.'.format(task, number))
    # print('=======================')
    # print('Finished!')
    # print('=======================')
    return 0


def star_to_char_multi_process(number, save_pic_path, save_charpic_path, process_number):
    print("\n正在把图片转字符画，请稍候...")
    print("启动多进程处理：")
    processes = []
    for count in range(1, process_number + 1):
        if count == 1:
            start_number = 1
            end_number = start_number + number // process_number
        elif count == process_number:
            start_number = end_number + 1
            end_number = number
        else:
            start_number = end_number + 1
            end_number = start_number + number // process_number
        process = StarToCharMultiProcess(count, number, save_pic_path, save_charpic_path, start_number, end_number)
        process.start()
        processes.append(process)
        time.sleep(1)
    return processes


def process_bar(percent, start_str='', end_str='', total_length=0):
    # 进度条
    bar = ''.join("■ " * int(percent * total_length)) + ''
    bar = '\r' + start_str + bar.ljust(total_length) + ' {:0>4.1f}%|'.format(percent * 100) + end_str
    print(bar, end='', flush=True)


def jpg_to_video(char_image_path, FPS):
    print("\n开始合成视频")
    video_fourcc = VideoWriter_fourcc(*"MP42")  # 设置视频编码器,这里使用使用MP42编码器,可以生成更小的视频文件
    char_img_path_list = [char_image_path + r'/{}.jpg'.format(i) for i in range(1, number + 1)]  # 生成目标字符图片文件的路径列表
    char_img_test = Image.open(char_img_path_list[1]).size  # 获取图片的分辨率
    os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))
    if not os.path.exists('video'):
        os.mkdir('video')
    video_writter = VideoWriter('video/new_char_video.avi', video_fourcc, FPS, char_img_test)
    sum = len(char_img_path_list)
    count = 0
    for image_path in char_img_path_list:
        img = cv2.imread(image_path)
        video_writter.write(img)
        end_str = '100%'
        count = count + 1
        process_bar(count / sum, start_str='', end_str=end_str, total_length=15)

    video_writter.release()
    print('\n')
    print('=======================')
    print('The video is finished!')
    print('=======================')


def write_audio(video_path):
    if sys.platform.startswith('win'):  # 判断平台，如果是Windows，使用同目录下的ffmpeg.exe
        # 加入音频
        cmd = os.path.dirname(os.path.realpath(sys.argv[0])) + '\\ffmpeg.exe -i ' + os.path.dirname(os.path.realpath(sys.argv[0])) + '/video/new_char_video.avi' + ' -i ' + video_path + ' -c copy -map 0 -map 1:1 -y -shortest ' + \
              os.path.dirname(os.path.realpath(sys.argv[0])) + '/video/videoWithAudio.avi' + ' -y'
        os.system(cmd)
        # 压制成H.264 mp4格式
        cmd2 = os.path.dirname(os.path.realpath(sys.argv[0])) + '\\ffmpeg.exe -i ' + os.path.dirname(os.path.realpath(sys.argv[0])) + '/video/videoWithAudio.avi' + ' -c:v libx264 -strict -2 ' + \
               os.path.dirname(os.path.realpath(sys.argv[0])) + '/video/finalOutput_VideoWithAudio.mp4' + ' -y'
    elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        if os.system('ffmpeg') == 32512:
            print('未检测到FFmpeg，请先安装！')
            print('无法写入音频并压制成mp4，已输出无音频版字符动画视频。')
            return -1
        # 加入音频
        cmd = 'ffmpeg -i ' + os.path.dirname(os.path.realpath(sys.argv[0])) + '/video/new_char_video.avi' + ' -i ' + video_path + ' -c copy -map 0 -map 1:1 -y -shortest ' + \
              os.path.dirname(os.path.realpath(sys.argv[0])) + '/video/videoWithAudio.avi' + ' -y'
        # 压制成H.264 mp4格式
        cmd2 = 'ffmpeg -i ' + os.path.dirname(os.path.realpath(sys.argv[0])) + '/video/videoWithAudio.avi' + ' -c:v libx264 -strict -2 ' + os.path.dirname(os.path.realpath(sys.argv[0])) + '/video/finalOutput_VideoWithAudio.mp4' + ' -y'
    else:
        print('未识别的平台，可能无法使用FFmpeg！')
        cmd = 'ffmpeg -i ' + os.path.dirname(os.path.realpath(sys.argv[0])) + '/video/new_char_video.avi' + ' -i ' + video_path + ' -c copy -map 0 -map 1:1 -y -shortest ' + \
              os.path.dirname(os.path.realpath(sys.argv[0])) + '/video/videoWithAudio.avi' + ' -y'
        # 压制成H.264 mp4格式
        cmd2 = 'ffmpeg -i ' + os.path.dirname(os.path.realpath(sys.argv[0])) + '/video/videoWithAudio.avi' + ' -c:v libx264 -strict -2 ' + os.path.dirname(os.path.realpath(sys.argv[0])) + '/video/finalOutput_VideoWithAudio.mp4' + ' -y'
    os.system(cmd)
    os.system(cmd2)
    return 0


def delete(path):
    try:
        shutil.rmtree(path)
        print('已删除：' + path)
        return 0
    except:
        print('删除' + path + '失败，可能是权限不足或目录不存在')
        return -1


def input_process(default_video_path):
    video_path = default_video_path
    while not os.path.exists(video_path):
        if len(sys.argv) == 2:
            video_path = sys.argv[1]
        elif len(sys.argv) == 1 and not os.path.exists(video_path):
            video_path = input('请输入待处理视频的完整路径：')
            # video_path = os.path.dirname(os.path.realpath(sys.argv[0])) + '/' + video_path
    return video_path


# save_pic_path = os.path.dirname(os.path.realpath(sys.argv[0])) + '/cache_pic'  # 别动
# save_charpic_path = os.path.dirname(os.path.realpath(sys.argv[0])) + '/cache_char'  # 别动

if __name__ == '__main__':
    # 各种参数
    # global save_charpic_path, save_pic_path
    multiprocessing.freeze_support()    #pyinstaller打包时要用到，直接使用python运行本文件请注释掉
    tempdir = tempfile.mkdtemp()
    try:
        save_pic_path = tempdir + '/cache_pic'  # 别动
        save_charpic_path = tempdir + '/cache_char'  # 别动
        video_path = os.path.dirname(os.path.realpath(sys.argv[0])) + '/input.mp4'  # 把input.mp4改成你的视频名字，注意前面的斜杠要保留
        processes_number = os.cpu_count() - 2  # 使用多少个进程同时处理图片，通常不超过CPU线程数，可以自行设置，例如 processes_number = 8
        video_path = input_process(video_path)

        # 处理
        vp = cv2.VideoCapture(video_path)
        number = video_to_pic(vp, save_pic_path)
        FPS = vp.get(cv2.CAP_PROP_FPS)
        threads = star_to_char_multi_process(number, save_pic_path, save_charpic_path, processes_number)
        for thread in threads:
            thread.join()
        vp.release()
        jpg_to_video(save_charpic_path, FPS)
        write_audio(video_path)  # 把原视频的音频复制到新视频中。需要安装ffmpeg，否则报错。没有ffmpeg请注释掉这行代码。
        delete(tempdir)
        input('运行完毕，任意键退出...')
    except KeyboardInterrupt:
        delete(tempdir)
        input('程序中止，任意键退出...')
