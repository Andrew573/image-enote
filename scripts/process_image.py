import sys
import os

def process_image(image_path):
    """示例：处理上传的图片，这里仅打印图片信息"""
    if not os.path.exists(image_path):
        print(f"错误：图片文件不存在 - {image_path}", file=sys.stderr)
        sys.exit(1)
    
    # 获取图片基本信息
    file_size = os.path.getsize(image_path) / 1024  # 转换为 KB
    print(f"图片路径: {image_path}")
    print(f"图片大小: {file_size:.2f} KB")
    print(f"图片处理完成（示例逻辑）")
    sys.exit(0)

if __name__ == '__main__':
    # 接收 Flask 传递的图片路径参数
    if len(sys.argv) < 2:
        print("错误：未传入图片路径", file=sys.stderr)
        sys.exit(1)
    image_path = sys.argv[1]
    process_image(image_path)



