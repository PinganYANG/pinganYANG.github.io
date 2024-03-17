import os
from collections import Counter

LOCATION_MAPPING = {
"Danmark":"丹麦",
"Kobenhaven":"哥本哈根",
"Church":"教堂",
"Church_organ":"风琴教堂",
"Design_Museum":"设计博物馆",
"Louisanna":"路易斯安娜博物馆",
"New_Museum":"新艺术博物馆",
"New_Quai":"新港",
"Sea":"海边",
"France":"法国",
"Dijon":"第戎",
"Dunkerque":"敦刻尔克",
"Paris":"巴黎",
"Arc":"凯旋门",
"Caodong":"草东",
"centre":"市中心",
"champs-sur-marnes":"田野马恩河",
"chatelet":"夏特雷",
"Eiffel_Tower":"埃菲尔铁塔",
"ens":"巴黎高师",
"Hotel_de_Ville":"市政厅",
"Lib_de_paris":"巴黎图书馆",
"Musee_Orsay":"奥赛博物馆",
"Notre_dame":"巴黎圣母院",
"Pere_lachaise":"拉夫雪兹神父墓地",
"Sacre_coeur":"圣心大教堂",
"Seine":"塞纳河",
"Tullerie":"杜乐丽公园",
"Sweden":"瑞典",
"Goteborg":"哥德堡",
"Stok":"斯德哥尔摩",
"Centre":"市中心",
"photo_museum":"照片博物馆",
"Subway":"地铁"
}

def create_menu_item(path, name):
    """ 根据给定的路径和名称创建一个HTML菜单项 """
    p = "/".join(path.split("\\")[2:])
    return f'<a href="/{p}/photo.html">{name}</a>'

def list_all_files(root_folder):
    files = []
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            # 构建文件的完整路径
            file_path = os.path.join(dirpath, filename)
            files.append(file_path)
            print(file_path)
    return files

def build_html_menu(root_folder):
    html_menu = '<nav>\n  <ul class="top-level-menu">\n    <li><a href="/index.html">首页</a></li>\n    <li><a href="/My_Gallery/photo.html">国家</a>\n'
    previous_level = 0
    previous_dirs = ['1']

    for root, dirs, files in os.walk(root_folder, topdown=True):
        level = root.count(os.sep) - root_folder.count(os.sep)
        if level == 0:  # 跳过根目录
            continue

        indent = '  ' * (level + 1)
        path_parts = root.split(os.sep)
        name = path_parts[-1]  # 文件夹名称
        name = LOCATION_MAPPING[name]
        menu_item = create_menu_item(root, name)

        # 检查是否需要关闭之前的菜单项
        while level < previous_level:
            html_menu += '  ' * previous_level + '</ul>\n' + '  ' * (previous_level - 1) + '</li>\n'
            previous_level -= 1

        if level == 1:  # 一级菜单
            if level != previous_level:
                html_menu += f'<ul class="second-level-menu">\n {indent}<li>{menu_item}\n{indent}  '
            else:
                html_menu += f'{indent}<li>{menu_item}\n{indent}  '
        elif level == 2:  # 二级及以下菜单
            if level != previous_level:
                html_menu += f'<ul class="third-level-menu">\n {indent}<li>{menu_item}'
            else:
                html_menu += f'</li>\n{indent}<li>{menu_item}\n{indent}'
        else:
            if level != previous_level:
                html_menu += f'\n{indent}<ul class="fourth-level-menu">\n {indent}<li>{menu_item}</li>\n'
            else:
                html_menu += f'{indent}<li>{menu_item}</li>\n'


        previous_level = level  # 更新层级

    # 遍历完成后，关闭所有未关闭的标签
    for i in range(previous_level, 0, -1):
        html_menu += '  ' * i + '</ul>\n' + '  ' * (i - 1) + '</li>\n'

    html_menu += '  </ul>\n</nav>'
    return html_menu



root_folder = "D:\\Lr\\My_Gallery"
html_menu = build_html_menu(root_folder)
# 将HTML内容写入到index.html文件
with open("html_menu.txt", 'w', encoding='utf-8') as file:
    file.write(html_menu)
