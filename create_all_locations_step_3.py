import os
import json
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
from PIL import Image
from geopy.geocoders import Nominatim
import time


def list_all_files(root_folder):
    files = []
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            # 构建文件的完整路径
            file_path = os.path.join(dirpath, filename)
            files.append(file_path)
    return files



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
def get_decimal_from_dms(dms, ref):
    """ 将度分秒 (DMS) 格式转换为十进制格式 """
    degrees, minutes, seconds = dms
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def get_gps_coordinates(exif_data):
    """ 从EXIF数据中获取GPS坐标 """
    gps_info = exif_data.get('GPSInfo')  # 34853 is the tag for 
    if gps_info:
        gps_latitude = gps_info[2]
        gps_latitude_ref = gps_info[1]
        gps_longitude = gps_info[4]
        gps_longitude_ref = gps_info[3]

        lat = get_decimal_from_dms(gps_latitude, gps_latitude_ref)
        lon = get_decimal_from_dms(gps_longitude, gps_longitude_ref)
        
        return lat, lon
    else:
        return None, None
    
def find_location(lat, lon):
    """ 使用geopy来找出给定坐标的地理位置 """
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse((lat, lon), language='en',addressdetails=False)
    return location
import os
import json
from PIL import Image  # 引入 Pillow 库用于读取图片尺寸

# def create_json_files(folder_path, photos):
#     photo_info_list = []
    
#     # 遍历照片文件夹中的文件
#     for file in photos:
#         # --- 新增部分：获取图片宽和高 ---
#         try:
#             # Image.open 是懒加载，只读取文件头获取尺寸，速度很快，不会加载整张图
#             with Image.open(file) as img:
#                 width, height = img.size
#         except Exception as e:
#             print(f"Error reading image size for {file}: {e}")
#             width = 0
#             height = 0
#         # -----------------------------

#         exif_metadata = get_exif_data(file) # 假设你已经有了这个函数
#         lat, lon = get_gps_coordinates(exif_metadata) # 假设你已经有了这个函数
        
#         # 默认坐标处理
#         if lat is None and lon is None:
#             lat = 48.8481
#             lon = 2.3958766666666667
            
#         # 路径处理 (处理 Windows 反斜杠)
#         if len(folder_path.split("\\")) == 1:
#             location = ""
#         else:
#             location = folder_path.split("\\")[-1]
            
#         filenames = file.split('\\')
#         filename = filenames[-1]

#         # 创建包含文件信息的字典
#         if exif_metadata != {}:
#             # 安全获取 EXIF 数据的辅助逻辑 (防止报错)
#             model = exif_metadata.get("Model", "Unknown Camera")
            
#             # 光圈处理
#             try:
#                 aperture_val = exif_metadata.get("ApertureValue", 0)
#                 aperture = f'f/{round(2 ** (aperture_val / 2), 1)}'
#             except:
#                 aperture = ""

#             # 快门处理
#             exp_time_raw = exif_metadata.get("ExposureTime", "")
#             if hasattr(exp_time_raw, 'numerator') and hasattr(exp_time_raw, 'denominator'):
#                 exposure_time = f'{exp_time_raw.numerator}/{exp_time_raw.denominator}'
#             else:
#                 exposure_time = str(exp_time_raw)

#             photo_info = {
#                 'filename': filename,
#                 'width': width,   # <--- 新增
#                 'height': height, # <--- 新增
#                 'title': filename,
#                 'CameraModel': f'{model}\n',
#                 'Aperture': f'{aperture}\n',
#                 'ExposureTime': f'{exposure_time}\n',
#                 'ISO': f'{exif_metadata.get("ISOSpeedRatings", "")}\n',
#                 'ExposureBiasValue': f'{exif_metadata.get("ExposureBiasValue", "")}\n',
#                 'FocalLength': f'{exif_metadata.get("FocalLength", "")}\n',
#                 'Location': f'{location}',
#                 "Link": f"https://www.google.com/maps?q={lat},{lon}"
#             }
#         else:
#             # 没有 EXIF 时的默认值
#             photo_info = {
#                 'filename': filename,
#                 'width': width,   # <--- 新增
#                 'height': height, # <--- 新增
#                 'title': filename,
#                 "CameraModel": "NIKON Z 5\n",
#                 "Aperture": "f/4.8\n",
#                 "ExposureTime": "1/10\n",
#                 "ISO": "1250\n",
#                 "ExposureBiasValue": "0.0\n",
#                 "FocalLength": "33.0\n",
#                 "Location": "Sweden",
#                 "Link": "https://www.google.com/maps?q=48.8481,2.3958766666666667"
#             }
            
#         # 将图片信息添加到列表中
#         photo_info_list.append(photo_info)

#     # 将图片信息列表保存为JSON文件
#     json_filename = os.path.join(folder_path, 'photos_info.json')
#     with open(json_filename, 'w', encoding='utf-8') as json_file: # 建议加上 encoding='utf-8'
#         json.dump(photo_info_list, json_file, indent=4, ensure_ascii=False) # ensure_ascii=False 防止中文乱码

#     print(f"JSON generated at: {json_filename}")

import os
import json
import numpy as np
from PIL import Image

# --- 1. 核心分析函数：生成颜色和氛围标签 ---
def analyze_color_theme(image_path):
    """
    分析图片的色调、颜色倾向和氛围，返回标签列表。
    例如: ['Blue', 'Cool', 'Dark', 'High Contrast']
    """
    tags = set()
    
    try:
        # 读取并缩放图片 (加速计算)
        img = Image.open(image_path).convert('RGB')
        img_small = img.resize((100, 100)) 
        
        # 转换为 HSV (Hue, Saturation, Value) 方便颜色判断
        # PIL 的 HSV 范围: H(0-255), S(0-255), V(0-255)
        # 注意: H 在 PIL 中是 0-255，对应 0-360度
        hsv_img = img_small.convert('HSV')
        hsv_arr = np.array(hsv_img)
        
        h = hsv_arr[:,:,0]
        s = hsv_arr[:,:,1]
        v = hsv_arr[:,:,2]
        
        # 计算平均值
        avg_s = np.mean(s)
        avg_v = np.mean(v)
        std_v = np.std(v) # 亮度标准差 = 对比度

        # --- A. 饱和度判断 (B&W / Muted / Vivid) ---
        if avg_s < 20: # 非常低饱和 -> 黑白
            tags.add("B&W")
            tags.add("Monochrome")
            return list(tags) # 黑白照片不需要判断颜色，直接返回
        elif avg_s < 60:
            tags.add("Muted")   # 低饱和/淡雅
        elif avg_s > 150:
            tags.add("Vivid")   # 鲜艳

        # --- B. 亮度/影调判断 (High Key / Low Key) ---
        if avg_v > 180:
            tags.add("High Key")    # 高调/明亮
        elif avg_v < 80:
            tags.add("Low Key")     # 低调/暗黑
            tags.add("Dark")

        # --- C. 对比度判断 ---
        if std_v > 60:
            tags.add("High Contrast") # 硬调
        elif std_v < 30:
            tags.add("Soft")          # 柔调

        # --- D. 主色调判断 (核心逻辑) ---
        # 我们只统计饱和度 > 40 的像素 (忽略灰色区域)
        valid_pixels = (s > 40) & (v > 40)
        if np.sum(valid_pixels) > 0:
            valid_h = h[valid_pixels]
            # 计算平均色相 (简单的平均法在环形空间可能有问题，但在单一主色调场景够用)
            # 更严谨的做法是统计直方图峰值，这里用简单的区间判断
            
            # 统计各颜色区间的像素占比
            # H (0-255) 映射到 360度: H * 360 / 255
            # Red: 0-20, 235-255
            # Orange: 20-40
            # Yellow: 40-70
            # Green: 70-105
            # Cyan: 105-135
            # Blue: 135-175
            # Purple: 175-215
            # Magenta: 215-235
            
            # 为了简化，我们直接用 numpy 统计区间
            hist, bins = np.histogram(valid_h, bins=[0, 20, 40, 70, 105, 135, 175, 215, 235, 256])
            # hist 对应: [Red1, Orange, Yellow, Green, Cyan, Blue, Purple, Magenta, Red2]
            
            # 把 Red1 和 Red2 合并
            color_counts = {
                'Red': hist[0] + hist[8],
                'Orange': hist[1],
                'Yellow': hist[2],
                'Green': hist[3],
                'Cyan': hist[4],
                'Blue': hist[5],
                'Purple': hist[6],
                'Magenta': hist[7]
            }
            
            # 找出占比最高的颜色
            primary_color = max(color_counts, key=color_counts.get)
            total_valid = np.sum(valid_pixels)
            
            # 只有当该颜色占比超过 25% 时才打标签，防止杂色干扰
            if color_counts[primary_color] / total_valid > 0.25:
                tags.add(primary_color)
                
                # 顺便打上冷暖标签
                if primary_color in ['Blue', 'Cyan', 'Green', 'Purple']:
                    tags.add('Cool')
                elif primary_color in ['Red', 'Orange', 'Yellow']:
                    tags.add('Warm')

    except Exception as e:
        print(f"Error analyzing color for {image_path}: {e}")

    return list(tags)


# --- 3. 主生成函数 ---

def create_json_files(folder_path, photos):
    photo_info_list = []
    
    print(f"开始处理 {len(photos)} 张照片...")
    
    for i, file in enumerate(photos):
        filename = os.path.basename(file)
        print(f"[{i+1}/{len(photos)}] 正在分析: {filename}")
        
        # 1. 获取宽高
        width, height = 0, 0
        try:
            with Image.open(file) as img:
                width, height = img.size
        except: pass

        # 2. 【核心】生成颜色标签
        color_tags = analyze_color_theme(file)
        # print(f"  -> Tags: {color_tags}") # 调试用
        
        # 3. 获取其他信息
        exif_metadata = get_exif_data(file)
        lat, lon = get_gps_coordinates(exif_metadata)
        
        if lat is None and lon is None:
            lat = 48.8481
            lon = 2.3958
            
        location = folder_path.split("\\")[-1] if len(folder_path.split("\\")) > 1 else ""

        # 基础信息
        base_info = {
            'filename': filename,
            'width': width,
            'height': height,
            'title': filename,
            'tags': color_tags,  # <--- 写入颜色标签 (例如 ["Blue", "Cool", "Dark"])
            'Location': location,
            "Link": f"https://www.google.com/maps?q={lat},{lon}"
        }

        # 合并 EXIF 信息 (保持你之前的逻辑结构)
        if exif_metadata:
            model = exif_metadata.get("Model", "Unknown")
            try:
                aperture_val = exif_metadata.get("ApertureValue", 0)
                aperture = f'f/{round(2 ** (aperture_val / 2), 1)}'
            except: aperture = ""

            exp_time_raw = exif_metadata.get("ExposureTime", "")
            if hasattr(exp_time_raw, 'numerator'):
                exposure_time = f'{exp_time_raw.numerator}/{exp_time_raw.denominator}'
            else: exposure_time = str(exp_time_raw)

            photo_info = {
                **base_info,
                'CameraModel': f'{model}\n',
                'Aperture': f'{aperture}\n',
                'ExposureTime': f'{exposure_time}\n',
                'ISO': f'{exif_metadata.get("ISOSpeedRatings", "")}\n',
                'ExposureBiasValue': f'{exif_metadata.get("ExposureBiasValue", "")}\n',
                'FocalLength': f'{exif_metadata.get("FocalLength", "")}\n',
            }
        else:
            photo_info = {
                **base_info,
                "CameraModel": "NIKON Z 5\n",
                "Aperture": "f/4.8\n",
                "ExposureTime": "1/10\n",
                "ISO": "1250\n",
                "ExposureBiasValue": "0.0\n",
                "FocalLength": "33.0\n",
                "Location": "Sweden",
                "Link": "https://www.google.com/maps?q=48.8481,2.3958766666666667"
            }

        photo_info_list.append(photo_info)

    # 保存 JSON
    json_filename = os.path.join(folder_path, 'photos_info.json')
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(photo_info_list, json_file, indent=4, ensure_ascii=False)
    
    print(f"\n✅ 完成！JSON 已生成: {json_filename}")

# --- 测试运行 (请根据实际情况取消注释) ---
# folder = r"C:\Users\YourName\Pictures\Gallery"
# files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
# create_json_files(folder, files)





import os

def create_index_htmls(photos,output_folder):
    output_html = output_folder+"\\"+"index.html"
    # 获取photos文件夹中所有的.jpg文件
    image_files = [f.split("\\")[-1] for f in photos]

    # 创建图片元素的HTML字符串
    image_elements = '\n'.join(
        f'<img src="{os.path.join(filename)}" alt="{filename}">'
        for filename in image_files
    )

    # 创建整个HTML页面的内容
    html_content = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Photo Gallery</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .gallery {{
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 10px;
                margin-top: 20px;
            }}
            .gallery img {{
                max-width: 200px; /* Adjust the size as needed */
                border: 1px solid #ccc;
                padding: 5px;
                background-color: #f8f8f8;
            }}
        </style>
    </head>
    <body>
        <h1>Photo Gallery</h1>
        <div class="gallery">
            {image_elements}
        </div>
    </body>
    </html>
    """

    # 将HTML内容写入到index.html文件
    with open(output_html, 'w') as file:
        file.write(html_content)



def create_photo_htmls(photos,output_folder,level):
    output_html = output_folder+"\\"+"photo.html"
    folders = '/'.join(output_folder.split('\\'))
    # 创建整个HTML页面的内容
    
    first = photos[0].split("\\")[-1]
    location = output_folder.split('\\')[-1]
    with open("html_menu.txt", 'r', encoding='utf-8') as file:
        cat = file.read()
    html_content = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" type="text/css" href="{level * "../"}img.css">
        <link rel="stylesheet" type="text/css" href="{level * "../"}st.css">
        <link rel="stylesheet" type="text/css" href="{level * "../"}menus.css">
        
        <link rel="stylesheet" type="text/css" href="{level * "../"}stylesheet.css">
    <title>Photography Portfolio</title>
    <style>
    
    </style>
    </head>
    {cat}



    <body>

    <div class="navbar">
    <!-- 导航链接 -->
    </div>
    <div class="image-info">
        <!-- 其它信息内容 -->
        <a href="https://www.google.fr/maps" target="_blank">点击查看更多</a>
    </div>
    <div class="banner" style="background-image: url('{level * "../"}photos/{first}');">
    <h1>Welcome to {location}</h1>
    </div>

    <div id="myModal" class="modal">
        <!-- 模态框内容 -->
        <span class="close">&times;</span>
        <img class="modal-content" id="img01">
        <div id="caption"></div>
    </div>

    <div class="gallery" id="gallery">
    <!-- 初始图片 -->
    </div>

    <div id="loading">
    <p>Loading more photos...</p>
    </div>



    <footer>
    <!-- 页脚信息 -->
    </footer>
    <script>
        const photosJsonUrl = 'https://pinganyang.github.io/{folders}/photos_info.json';
    </script>
    <script src="{level * "../"}img_random.js"></script>

    

    </body>
    </html>

    """

    # 将HTML内容写入到index.html文件
    with open(output_html, 'w', encoding='utf-8') as file:
        file.write(html_content)






root_folder = "D:\\Lr\\My_Gallery"
folder_name_dict = {}
for dirpath, dirnames, filenames in os.walk(root_folder):
    # 先打印当前目录
    folder_names = dirpath.split("\\")
    folder_name = "\\".join(folder_names[2:])
    print(folder_name)
    raw_folder = "\\".join(folder_names[:2])
    if not os.path.exists(folder_name):
        # 如果不存在，创建新目录
        os.makedirs(folder_name)
    files_lists = list_all_files(raw_folder+"\\"+folder_name)
    create_json_files(folder_name,files_lists)
    create_index_htmls(files_lists,folder_name)
    level = len(folder_name.split("\\"))
    create_photo_htmls(files_lists,folder_name,level)