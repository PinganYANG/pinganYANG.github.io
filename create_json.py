import os
import json
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS

# 指定照片文件夹的路径
photos_folder = 'photos'

# 初始化一个空的图片信息列表
photo_info_list = []

# 为了方便提取EXIF信息，需要创建一个反向映射
exif_tags = {v: k for k, v in ExifTags.TAGS.items()}

def get_exif_data(image_path):
    image = Image.open(image_path)
    exif_data = {}
    if hasattr(image, '_getexif'):  # 检查图片是否包含EXIF数据
        exif_info = image._getexif()
        if exif_info is not None:
            for tag, value in exif_info.items():
                decoded_tag = TAGS.get(tag, tag)
                exif_data[decoded_tag] = value
    return exif_data

# 遍历照片文件夹中的文件
for filename in os.listdir(photos_folder):
    if filename.endswith('.jpg'):
        # 提取文件名（去除文件扩展名）
        file_title = os.path.splitext(filename)[0]

        # 读取图片文件
        file_path = os.path.join(photos_folder, filename)
        img = Image.open(file_path)


        exif_metadata = get_exif_data(file_path)

        # 创建包含文件信息的字典
        photo_info = {
            'filename': filename,
            'title': f'{file_title} Title',
            'CameraModel': f'{exif_metadata["Model"]}\n',
            'Aperture': f'f/{round(2 ** (exif_metadata["ApertureValue"] / 2), 1) }\n',
            'ExposureTime': f'{exif_metadata["ExposureTime"].numerator}/{exif_metadata["ExposureTime"].denominator}\n',
            'ISO':f'{exif_metadata["ISOSpeedRatings"]}\n',
            'ExposureBiasValue': f'{exif_metadata["ExposureBiasValue"]}\n',
            'FocalLength': f'{exif_metadata["FocalLength"]}\n',
            'Location': '斯德哥尔摩',
            "Link": "https://www.google.fr/maps"
        }
        
        # 将图片信息添加到列表中
        photo_info_list.append(photo_info)

# 将图片信息列表保存为JSON文件
json_filename = 'photos_info.json'
with open(json_filename, 'w') as json_file:
    json.dump(photo_info_list, json_file, indent=4)

print(f'JSON文件已生成：{json_filename}')
