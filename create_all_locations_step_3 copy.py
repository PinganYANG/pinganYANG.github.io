import os
import json
import time
import hashlib
import numpy as np
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
from geopy.geocoders import Nominatim

# --- 配置 ---
ROOT_FOLDER = r"D:\Lr\My_Gallery"  # 你的图库根目录
MASTER_JSON_PATH = "master_photos.json" # 主数据库文件
PHOTO_CACHE = {} # 内存缓存

# --- 1. 基础工具函数 ---

def list_image_files(folder_path):
    """列出指定文件夹下的所有图片文件 (jpg, jpeg, png)"""
    extensions = ('.jpg', '.jpeg', '.png', '.webp')
    files = []
    for dirpath, dirnames, filenames in os.walk(folder_path):

        for filename in filenames:
            if filename.lower().endswith(extensions):
                files.append(os.path.join(dirpath, filename))
    return files


# def list_all_files(root_folder):
#     files = []
#     for dirpath, dirnames, filenames in os.walk(root_folder):
#         for filename in filenames:
#             # 构建文件的完整路径
#             file_path = os.path.join(dirpath, filename)
#             files.append(file_path)
#     return files

def get_file_id(filepath):
    """
    生成文件的唯一ID。
    使用 '绝对路径 + 修改时间'，这样如果修图后文件变了，ID也会变，触发重新分析。
    """
    mtime = os.path.getmtime(filepath)
    abspath = os.path.abspath(filepath)
    # 简单拼接即可，不需要真算hash，速度快
    return f"{abspath}_{mtime}"

def load_master_data():
    """加载主数据库到内存"""
    global PHOTO_CACHE
    if os.path.exists(MASTER_JSON_PATH):
        try:
            with open(MASTER_JSON_PATH, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
                for item in data_list:
                    if 'id' in item:
                        PHOTO_CACHE[item['id']] = item
            print(f"✅ 已加载主数据库，包含 {len(PHOTO_CACHE)} 张已有照片信息。")
        except Exception as e:
            print(f"⚠️ 读取主数据库失败: {e}")
            PHOTO_CACHE = {}

def save_master_data():
    """保存主数据库"""
    try:
        data_list = list(PHOTO_CACHE.values())
        with open(MASTER_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, indent=4, ensure_ascii=False)
        print(f"💾 主数据库已保存 ({len(data_list)} 张照片)。")
    except Exception as e:
        print(f"❌ 保存主数据库失败: {e}")

# --- 2. 图像分析与 EXIF 处理 ---

def get_exif_data(image_path):
    """获取原始 EXIF 数据字典"""
    exif_data = {}
    try:
        image = Image.open(image_path)
        if hasattr(image, '_getexif'):
            exif_info = image._getexif()
            if exif_info:
                for tag, value in exif_info.items():
                    decoded_tag = TAGS.get(tag, tag)
                    exif_data[decoded_tag] = value
    except Exception as e:
        print(f"  [EXIF Error] {os.path.basename(image_path)}: {e}")
    return exif_data

def get_decimal_from_dms(dms, ref):
    try:
        degrees, minutes, seconds = dms
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal
    except:
        return 0.0

def get_gps_coordinates(exif_data):
    """提取 GPS 坐标"""
    try:
        gps_info = exif_data.get('GPSInfo')
        if gps_info:
            gps_latitude = gps_info.get(2)
            gps_latitude_ref = gps_info.get(1)
            gps_longitude = gps_info.get(4)
            gps_longitude_ref = gps_info.get(3)
            
            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = get_decimal_from_dms(gps_latitude, gps_latitude_ref)
                lon = get_decimal_from_dms(gps_longitude, gps_longitude_ref)
                return lat, lon
    except:
        pass
    return None, None

def analyze_color_theme(image_path):
    """分析颜色与氛围 (核心耗时函数)"""
    tags = set()
    try:
        img = Image.open(image_path).convert('RGB')
        img_small = img.resize((100, 100))
        hsv_img = img_small.convert('HSV')
        hsv_arr = np.array(hsv_img)
        
        h, s, v = hsv_arr[:,:,0], hsv_arr[:,:,1], hsv_arr[:,:,2]
        avg_s, avg_v, std_v = np.mean(s), np.mean(v), np.std(v)

        # 饱和度
        if avg_s < 20: 
            tags.add("B&W"); tags.add("Monochrome")
            return list(tags)
        elif avg_s < 60: tags.add("Muted")
        elif avg_s > 150: tags.add("Vivid")

        # 亮度
        if avg_v > 180: tags.add("High Key")
        elif avg_v < 80: tags.add("Low Key"); tags.add("Dark")

        # 对比度
        if std_v > 60: tags.add("High Contrast")
        elif std_v < 30: tags.add("Soft")

        # 主色调
        valid_pixels = (s > 40) & (v > 40)
        if np.sum(valid_pixels) > 0:
            valid_h = h[valid_pixels]
            hist, _ = np.histogram(valid_h, bins=[0, 20, 40, 70, 105, 135, 175, 215, 235, 256])
            color_map = ['Red', 'Orange', 'Yellow', 'Green', 'Cyan', 'Blue', 'Purple', 'Magenta', 'Red']
            
            # 合并两头的红色
            counts = {color: 0 for color in set(color_map)}
            counts['Red'] = hist[0] + hist[8]
            counts['Orange'] = hist[1]; counts['Yellow'] = hist[2]; counts['Green'] = hist[3]
            counts['Cyan'] = hist[4]; counts['Blue'] = hist[5]; counts['Purple'] = hist[6]; counts['Magenta'] = hist[7]

            primary = max(counts, key=counts.get)
            if counts[primary] / np.sum(valid_pixels) > 0.25:
                tags.add(primary)
                if primary in ['Blue', 'Cyan', 'Green', 'Purple']: tags.add('Cool')
                elif primary in ['Red', 'Orange', 'Yellow']: tags.add('Warm')

    except Exception as e:
        print(f"  [Color Error] {e}")
    
    return list(tags)

# --- 3. 核心处理逻辑 (增量更新) ---

def process_single_photo(file_path):
    """
    处理单张照片：先查缓存，没有再分析
    """
    file_id = get_file_id(file_path)
    
    # 1. 缓存命中
    if file_id in PHOTO_CACHE:
        return PHOTO_CACHE[file_id]
    
    # 2. 新照片分析
    print(f"  ⚡ 分析新照片: {os.path.basename(file_path)}")
    
    # 基础信息
    width, height = 0, 0
    try:
        with Image.open(file_path) as img:
            width, height = img.size
    except: pass
    
    color_tags = analyze_color_theme(file_path)
    exif_raw = get_exif_data(file_path)
    lat, lon = get_gps_coordinates(exif_raw)
    
    # 默认值处理
    if lat is None: lat = 48.8481
    if lon is None: lon = 2.3958
    
    # 安全获取 EXIF 字符串
    def get_safe(key, default=""):
        val = exif_raw.get(key, default)
        return str(val) if val else default

    # 构造数据
    photo_data = {
        "id": file_id,
        "filename": os.path.basename(file_path),
        "width": width,
        "height": height,
        "title": os.path.basename(file_path),
        "tags": color_tags,
        "Link": f"https://www.google.com/maps?q={lat},{lon}",
        
        # EXIF 字段 (保留你原来的格式需求)
        "CameraModel": f"{get_safe('Model', 'Unknown Camera')}\n",
        "ISO": f"{get_safe('ISOSpeedRatings', '')}\n",
        "FocalLength": f"{get_safe('FocalLength', '')}\n",
        "ExposureBiasValue": f"{get_safe('ExposureBiasValue', '')}\n",
        # 这里简化了 Aperture/Shutter 计算，如果需要极高精度可把那部分逻辑贴回来
        "Aperture": f"f/{get_safe('FNumber', '')}\n", 
        "ExposureTime": f"{get_safe('ExposureTime', '')}\n",
        "ai_analysis": None
    }
    
    # 存入缓存
    PHOTO_CACHE[file_id] = photo_data
    return photo_data

def generate_folder_json(folder_name, files_list):
    """
    为当前子文件夹生成 photos_info.json
    """
    photos_data_list = []
    location_name = os.path.basename(folder_name) # 用文件夹名作为 Location
    
    for file_path in files_list:
        data = process_single_photo(file_path)
        # 复制一份数据，注入当前文件夹特有的 Location
        # (因为 master json 里可能不包含 Location，或者是旧的)
        folder_specific_data = data.copy()
        folder_specific_data['Location'] = location_name
        photos_data_list.append(folder_specific_data)
        
    json_path = os.path.join(folder_name, 'photos_info.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(photos_data_list, f, indent=4, ensure_ascii=False)
    
    # print(f"  -> JSON OK: {len(photos_data_list)} items")
    return photos_data_list

# --- 4. HTML 生成函数 ---

def create_index_html(photos_list, output_folder):
    """生成简单的 index.html (缩略图列表)"""
    output_html = os.path.join(output_folder, "index.html")
    imgs_html = '\n'.join([f'<img src="{os.path.basename(p)}" alt="">' for p in photos_list[:20]]) # 只展示前20张预览
    
    html = f"""<!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Index</title>
    <style>body{{display:flex;flex-wrap:wrap;gap:10px}} img{{height:100px}}</style>
    </head>
    <body><h1>Preview</h1><div>{imgs_html}</div></body>
    </html>"""
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)

def create_photo_html(photos_list, output_folder, relative_level):
    """生成瀑布流页面 photo.html"""
    if not photos_list: return
    
    output_html = os.path.join(output_folder, "photo.html")
    location = os.path.basename(output_folder)
    
    # 计算相对路径前缀 (例如 "../" 或 "../../")
    rel_prefix = "../" * relative_level
    
    # 第一张图作为 Banner 背景
    first_img = os.path.basename(photos_list[0])
    
    # 读取菜单 (如果文件存在)
    menu_html = ""
    if os.path.exists("html_menu.txt"):
        with open("html_menu.txt", 'r', encoding='utf-8') as f:
            menu_html = f.read()

    # 你的 HTML 模板
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="{rel_prefix}img.css">
    <link rel="stylesheet" type="text/css" href="{rel_prefix}st.css">
    <link rel="stylesheet" type="text/css" href="{rel_prefix}menus.css">
    <link rel="stylesheet" type="text/css" href="{rel_prefix}stylesheet.css">
    <title>{location} - Portfolio</title>
</head>
<body>

{menu_html}

<div class="navbar"></div>

   <div class="banner" style="background-image: url('{level * "../"}photos/{first_img}');">
    <h1>Welcome to {location}</h1>
</div>

<div id="myModal" class="modal">
    <span class="close">×</span>
    <img class="modal-content" id="img01">
    <div id="caption"></div>
</div>

<div class="gallery" id="gallery"></div>

<div id="loading"><p>Loading...</p></div>

<footer><p>&copy; 2026 Photography</p></footer>

<script>
    // 使用相对路径，自动适配
    const photosJsonUrl = './photos_info.json';
</script>
<script src="{rel_prefix}img_random.js"></script>

</body>
</html>
"""
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

# --- 5. 主程序 ---

if __name__ == "__main__":
    print("🚀 启动生成程序...")
    
    # 1. 加载主数据库 (关键优化)
    load_master_data()
    
    try:
        # 2. 遍历目录
        for dirpath, dirnames, filenames in os.walk(ROOT_FOLDER):
            # 计算当前文件夹相对于 ROOT_FOLDER 的层级
            rel_path = os.path.relpath(dirpath, ROOT_FOLDER)
            
            # 跳过根目录本身，或者隐藏目录
            # if rel_path == '.' or rel_path.startswith('.'):
            #     continue
            
            # 跳过 raw 目录 (如果你有原始图文件夹不想处理)
            # if 'raw' in rel_path.lower(): continue

            # 构建目标文件夹路径 (这里逻辑稍微调整，直接在原目录生成)
            # 你的原逻辑是把生成的 web 文件放在另一个结构里？
            # 假设目前是在原图目录下直接生成 JSON 和 HTML
            
            current_folder = dirpath
            
            # 获取当前目录下的图片
            image_files = list_image_files(current_folder)

            folder_names = dirpath.split("\\")
            folder_name = "\\".join(folder_names[2:])
            
            if not image_files:
                continue
                
            print(f"\n📂 处理目录: {rel_path} ({len(image_files)} 张)")
            
            # 生成 JSON (复用主数据库)
            generate_folder_json(folder_name, image_files)
            
            # 生成 HTML
            level = len(rel_path.split(os.sep)) # 计算深度
            create_index_html(image_files, folder_name)
            create_photo_html(image_files, folder_name, level)
            
    except KeyboardInterrupt:
        print("\n🛑 用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 3. 必须保存主数据库
        save_master_data()
        print("\n✨ 全部完成！")