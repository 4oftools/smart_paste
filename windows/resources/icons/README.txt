图标文件说明
====================

请在此目录放置应用图标文件：app.ico

如果没有图标文件，可以使用以下方法创建：

1. 使用在线工具：
   - https://www.icoconverter.com/
   - https://icoconvert.com/

2. 使用 Python 脚本生成（需要安装 pillow）：
   ```python
   from PIL import Image, ImageDraw
   import os

   # 创建一个简单的图标
   size = 256
   img = Image.new('RGBA', (size, size), (94, 129, 172, 255))  # #5E81AC
   draw = ImageDraw.Draw(img)

   # 画一个简单的剪贴板形状
   padding = 30
   draw.rectangle([padding, padding, size-padding, size*0.8],
                 fill=(30, 30, 46, 255), outline=(216, 222, 233, 255), width=8)
   draw.line([size//2, size*0.3, size//2, size*0.65], fill=(216, 222, 233, 255), width=8)

   # 保存为 ICO
   img.save('app.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
   ```

3. 跳过图标（不推荐）：
   在打包命令中移除 --icon 参数：
   pyinstaller --onefile --windowed --name=SmartPaste --add-data="resources;resources" main.py
