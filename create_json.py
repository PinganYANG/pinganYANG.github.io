import os
import json
from PIL import Image, ExifTags

# 指定照片文件夹的路径
photos_folder = 'photos'

# 初始化一个空的图片信息列表
photo_info_list = []

# 为了方便提取EXIF信息，需要创建一个反向映射
exif_tags = {v: k for k, v in ExifTags.TAGS.items()}

# 遍历照片文件夹中的文件
for filename in os.listdir(photos_folder):
    if filename.endswith('.jpg'):
        # 提取文件名（去除文件扩展名）
        file_title = os.path.splitext(filename)[0]

        # 读取图片文件
        file_path = os.path.join(photos_folder, filename)
        img = Image.open(file_path)

        # 获取EXIF数据
        exif_data = img._getexif()

        # 提取所需的EXIF信息
        camera_model = exif_data.get(exif_tags.get('Model'), 'Unknown')
        aperture = exif_data.get(exif_tags.get('ApertureValue'), 'Unknown')
        exposure_time = exif_data.get(exif_tags.get('ExposureTime'), 'Unknown')
        iso = exif_data.get(exif_tags.get('ISOSpeedRatings'), 'Unknown')
        exposure_compensation = exif_data.get(exif_tags.get('ExposureBiasValue'), 'Unknown')
        focal_length = exif_data.get(exif_tags.get('FocalLength'), 'Unknown')

        # 创建包含文件信息的字典
        photo_info = {
            'filename': filename,
            'title': f'{file_title} Title',
            'description': f'Camera Model: {camera_model}, Aperture: {aperture}, '
                            f'Exposure Time: {exposure_time}, ISO: {iso}, '
                            f'Exposure Compensation: {exposure_compensation}, '
                            f'Focal Length: {focal_length}. Location: 斯德哥尔摩'
        }
        
        # 将图片信息添加到列表中
        photo_info_list.append(photo_info)

# 将图片信息列表保存为JSON文件
json_filename = 'photos_info.json'
with open(json_filename, 'w') as json_file:
    json.dump(photo_info_list, json_file, indent=4)

print(f'JSON文件已生成：{json_filename}')
