from PIL import Image
import os

# 要压缩图片的文件夹路径
input_folder = 'photos/'

# 压缩后的图片将保存的文件夹路径
output_folder = 'compressed/'

# 创建输出文件夹，如果它不存在的话
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 遍历文件夹中的所有文件
for file_name in os.listdir(input_folder):
    if file_name.lower().endswith('.jpg'):  # 检查文件扩展名
        file_path = os.path.join(input_folder, file_name)
        img = Image.open(file_path)
        
        # 计算新的尺寸（宽度和高度减半）
        new_size = (img.width // 3, img.height // 3)
        
        # 调整图片到新的尺寸
        compressed_img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # 构建输出文件路径
        output_file_path = os.path.join(output_folder, file_name)
        
        # 保存压缩后的图片
        compressed_img.save(output_file_path)

print("所有图片压缩完成，并保存到了 '{}' 文件夹中。".format(output_folder))
