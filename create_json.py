import os
import json

# 指定照片文件夹的路径
photos_folder = 'photos'

# 初始化一个空的图片信息列表
photo_info_list = []

# 遍历照片文件夹中的文件
for filename in os.listdir(photos_folder):
    if filename.endswith('.jpg'):
        # 提取文件名（去除文件扩展名）
        file_title = os.path.splitext(filename)[0]
        
        # 创建一个包含文件信息的字典
        photo_info = {
            'filename': filename,
            'title': f'{file_title} Title',
            'description': f'This is a description of {file_title}.'
        }
        
        # 将图片信息添加到列表中
        photo_info_list.append(photo_info)

# 将图片信息列表保存为JSON文件
json_filename = 'photos_info.json'
with open(json_filename, 'w') as json_file:
    json.dump(photo_info_list, json_file, indent=4)

print(f'JSON文件已生成：{json_filename}')