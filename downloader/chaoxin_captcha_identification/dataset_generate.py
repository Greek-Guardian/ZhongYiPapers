import json, random
from PIL import Image,ImageDraw,ImageFont
import numpy as np

def generate_color():
    '''生成高亮度的颜色'''
    tmp = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
    index = random.randint(0, 2)
    tmp[index] = random.randint(253, 255)
    tmp[(index+random.randint(1, 2))%3] = random.randint(1, 10)
    return tuple(tmp)

def color(img):
    '''给汉字上色（渐变色）'''
    # 1/5概率不使用渐变色，直接退出函数
    if not random.randint(0, 5):
        return img
    def Make_gradation_img_data(width, height, rgb_start, rgb_stop, horizontal=(True, True, True)):
        '''Make gradation image data'''
        result = np.zeros((height, width, 3), dtype=np.uint8)
        for i, (m,n,o) in enumerate(zip(rgb_start, rgb_stop, horizontal)):
            if o:
                result[:,:,i] = np.tile(np.linspace(m, n, width), (height, 1))
            else:
                result[:,:,i] = np.tile(np.linspace(m, n, width), (height, 1)).T
        return result

    MakeGradationImg = lambda width, height, rgb_start, rgb_stop, horizontal=(True, True, True):Image.fromarray(Make_gradation_img_data(width, height, rgb_start, rgb_stop, horizontal))

    # 生成渐变色图片
    raw_size = 60
    gra_img = MakeGradationImg(raw_size, raw_size, generate_color(), generate_color(), (True, True, True))
    gra_img = gra_img.rotate(45)
    box = ((raw_size-40)/2, (raw_size-40)/2, (raw_size-40)/2+40, (raw_size-40)/2+40)
    gra_img = gra_img.crop(box)
    gra_img = gra_img.convert('RGBA')

    # 抠出汉字
    gra_pixel = gra_img.load()
    img_pixel = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if img_pixel[x, y][3]!=0:
                gra_pixel[x, y] = (gra_pixel[x, y][0], gra_pixel[x, y][1], gra_pixel[x, y][2], 255)
            else:
                gra_pixel[x, y] = (gra_pixel[x, y][0], gra_pixel[x, y][1], gra_pixel[x, y][2], 0)

    return gra_img
    
def mess(img):
    '''给图像加上噪点'''
    img_pixels = img.load()
    noise = 20
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if img_pixels[x, y][3]!=0:
                img_pixels[x, y] = (img_pixels[x, y][0]+random.randint(-noise, noise), img_pixels[x, y][1]+random.randint(-noise, noise), img_pixels[x, y][2]+random.randint(-noise, noise), 255)
    return img

def shadow(hanzi_img):
    '''向左上方投影1像素'''
    shadow = Image.new('RGBA', hanzi_img.size, (0, 0, 0, 0))
    shift_pos = 1
    hanziz_pixels = hanzi_img.load()
    shadow_pixels = shadow.load()
    for x in range(hanzi_img.size[0]):
        for y in range(hanzi_img.size[1]):
            if hanziz_pixels[x, y][3]!=0:
                if x>=shift_pos and y>=shift_pos:
                    shadow_pixels[x-shift_pos, y-shift_pos] = (int(hanziz_pixels[x, y][0]/4), int(hanziz_pixels[x, y][1]/4), int(hanziz_pixels[x, y][2]/4), 255)
    
    shadow.paste(hanzi_img, (0, 0), mask=hanzi_img)
    return shadow

def append_hanzi(raw_img, character):
    '''选取五个汉字中的一个，将其放在图片右侧'''
    out_img = Image.new('L', (360, 160), (0))
    draw = ImageDraw.Draw(out_img)
    draw.text((320, 0), character, fill=(255), font=ImageFont.truetype(r"D:\vscode_workspace\Python\ZhongYi\chaoxin\ttc\msyh.ttc", 28, encoding="unic"))
    draw.text((320, 40), character, fill=(255), font=ImageFont.truetype(r"D:\vscode_workspace\Python\ZhongYi\chaoxin\ttc\STXINGKA.TTF", 40, encoding="unic"))
    draw.text((320, 80), character, fill=(255), font=ImageFont.truetype(r"D:\vscode_workspace\Python\ZhongYi\chaoxin\ttc\STZHONGS.TTF", 30, encoding="unic"))
    draw.text((320, 120), character, fill=(255), font=ImageFont.truetype(r"D:\vscode_workspace\Python\ZhongYi\chaoxin\ttc\SIMLI.TTF", 30, encoding="unic"))
    out_img.paste(raw_img, (0, 0), mask=raw_img)
    return out_img

def generate_pic(output_index):
    # 读取常用汉字列表
    hanzi_path = r"D:\vscode_workspace\Python\ZhongYi\chaoxin\common_chinese_characters.json"
    with open(hanzi_path, 'r', encoding='utf-8') as f:
        hanzi_list = json.load(f)

    # 读取不同字体
    fonts = []
    fonts.append(ImageFont.truetype(r"D:\vscode_workspace\Python\ZhongYi\chaoxin\ttc\msyh.ttc", 28, encoding="unic"))
    fonts.append(ImageFont.truetype(r"D:\vscode_workspace\Python\ZhongYi\chaoxin\ttc\STXINGKA.TTF", 40, encoding="unic"))
    fonts.append(ImageFont.truetype(r"D:\vscode_workspace\Python\ZhongYi\chaoxin\ttc\STZHONGS.TTF", 30, encoding="unic"))

    # 随机读取一张动物图片
    animal_path = r"D:\vscode_workspace\Python\ZhongYi\chaoxin\reshaped\\"+str(random.randint(1,501))+".jpg"
    full_img = Image.open(animal_path)
    full_img = full_img.convert('RGBA')

    # 添加汉字
    characters = []
    character_fonts = [] # 字体
    character_rotates = [] # 旋转度数
    character_poses = [] # 位置
    for i in range(5):
        img = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        # 生成随机汉字
        character = hanzi_list[random.randint(0, len(hanzi_list)-1)]
        characters.append(character)
        # 随机选择字体
        character_fonts.append(random.randint(0, len(fonts)-1))
        # 绘制汉字
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), characters[i], fill=generate_color(), font=fonts[character_fonts[i]])
        # 上色
        img = color(img)
        # 旋转汉字
        character_rotates.append(random.randint(-45, 45))
        img = img.rotate(character_rotates[i])
        # 阴影(阴影要放在旋转之前，让旋转操作让阴影变得更自然（相当于额外平滑了一次像素）)
        img = shadow(img)
        # 加噪点
        img = mess(img)
        # 覆盖图片
        label = True
        tmp = (0, 0)
        while label:
            label = False
            tmp = (random.randint(0, 280), random.randint(0, 120))
            for item in character_poses:
                if tmp[0]-item[0]>= -25 and tmp[0]-item[0]<=25 and tmp[1]-item[1]>= -25 and tmp[1]-item[1]<=25:
                    label = True
        character_poses.append(tmp)
        full_img.paste(img, character_poses[i], mask=img)
    # 灰度化
    full_img = full_img.convert('L')
    # 选取五个汉字中的一个，将其放在图片右侧
    which_hanzi = random.randint(0, 4)
    full_img = append_hanzi(full_img, characters[which_hanzi])
    full_img.save(r"D:\vscode_workspace\Python\ZhongYi\chaoxin\dataset\\"+str(index)+"_"+str(character_poses[which_hanzi][0]+20)+"_"+str(character_poses[which_hanzi][1]+20)+".jpg")


if 1:
    datasetsize = 10000
    for index in range(datasetsize):
        generate_pic(index)
        print(index)