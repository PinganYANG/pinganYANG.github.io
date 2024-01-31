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

def create_json_files(folder_path,photos):
    photo_info_list = []
    # 遍历照片文件夹中的文件
    for file in photos:
        exif_metadata = get_exif_data(file)
        lat, lon = get_gps_coordinates(exif_metadata)
        if lat is None and lon is None:
            lat = 48.8481
            lon = 2.3958766666666667
        if len(folder_path.split("\\")) == 1:
            location = ""
        else:
            location = folder_path.split("\\")[-1]
        filenames = file.split('\\')
        # 创建包含文件信息的字典
        photo_info = {
            'filename': filenames[-1],
            'title': filenames[-1],
            'CameraModel': f'{exif_metadata["Model"]}\n',
            'Aperture': f'f/{round(2 ** (exif_metadata["ApertureValue"] / 2), 1) }\n',
            'ExposureTime': f'{exif_metadata["ExposureTime"].numerator}/{exif_metadata["ExposureTime"].denominator}\n',
            'ISO':f'{exif_metadata["ISOSpeedRatings"]}\n',
            'ExposureBiasValue': f'{exif_metadata["ExposureBiasValue"]}\n',
            'FocalLength': f'{exif_metadata["FocalLength"]}\n',
            'Location': f'{location}',
            "Link": f"https://www.google.com/maps?q={lat},{lon}"
        }
        
        # 将图片信息添加到列表中
        photo_info_list.append(photo_info)

    # 将图片信息列表保存为JSON文件
    json_filename = os.path.join(folder_path,'photos_info.json')
    with open(json_filename, 'w') as json_file:
        json.dump(photo_info_list, json_file, indent=4)


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
    <h1>Welcome to My Portfolio</h1>
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






root_folder = "D:\\Lr\\to_upload_on_web"
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