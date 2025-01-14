from PIL import Image, ExifTags
import os
from tqdm import tqdm

# 要压缩图片的文件夹路径
input_folder = 'D:/Lr/up_to_web'

day_of_pics = "2024_05_06"

# 压缩后的图片将保存的文件夹路径
output_folder = 'compressed/'


# 创建输出文件夹，如果它不存在的话
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 遍历文件夹中的所有文件
for file_name in tqdm(os.listdir(input_folder)):
    if file_name.lower().endswith('.jpg'):  # 检查文件扩展名
        file_path = os.path.join(input_folder, file_name)
        img = Image.open(file_path)

        # 保留原始图片的 EXIF 数据
        if hasattr(img, '_getexif'):
            exif = img._getexif()
        else:
            exif = None

        # 计算新的尺寸（宽度和高度减半）
        if img.width <= 1000 or img.width <= 1000:
            new_size = (img.width, img.height)
        else:
            new_size = (img.width // 3, img.height // 3)
        
        # 调整图片到新的尺寸
        compressed_img = img.resize(new_size, Image.Resampling.LANCZOS)

        # 如果有 EXIF 数据，添加到新图片
        if exif:
            exif_data = { ExifTags.TAGS[k]: v for k, v in exif.items() if k in ExifTags.TAGS }
            compressed_img.info['exif'] = exif

        # 构建输出文件路径
        output_file_path = os.path.join(output_folder, day_of_pics+'_'+file_name)
        
        # 保存压缩后的图片
        if img.info.get('exif'):
            compressed_img.save(output_file_path,"JPEG", exif=img.info.get('exif'))

        else:
            compressed_img.save(output_file_path, "JPEG")


print("所有图片压缩完成，并保存到了 '{}' 文件夹中。".format(output_folder))
