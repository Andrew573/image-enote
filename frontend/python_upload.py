import requests

def upload_multiple_files(server_url, file_paths, script_name=None):
    """
    向 Flask 后端上传多个文件
    :param server_url: Flask 服务地址（如 http://192.168.1.100:5000/upload）
    :param file_paths: 本地图片路径列表（如 ['/home/user/1.png', 'D:/pic/2.jpg']）
    :param script_name: 可选，要执行的后端脚本名称
    :return: 上传结果
    """
    # 构造多文件请求体：键名固定为 'files'，值为文件对象列表
    files = []
    for file_path in file_paths:
        try:
            # 以二进制模式打开文件
            files.append(('files', open(file_path, 'rb')))
        except FileNotFoundError:
            print(f"警告：文件 {file_path} 不存在，跳过")
            continue
    
    if not files:
        print("没有有效文件可上传")
        return None
    
    # 构造脚本参数（可选）
    data = {}
    if script_name:
        data['script'] = script_name
    
    try:
        # 发送 POST 请求
        response = requests.post(
            server_url,
            files=files,
            data=data,
            timeout=60  # 超时时间 60 秒（多文件上传可适当延长）
        )
        
        # 关闭所有打开的文件
        for _, file_obj in files:
            file_obj.close()
        
        # 解析响应
        if response.status_code == 200:
            result = response.json()
            print("上传成功！结果：")
            print(result)
            return result
        else:
            print(f"上传失败，状态码：{response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.ConnectionError:
        print(f"连接失败！请检查：1. Flask 服务是否运行 2. 服务器 IP/端口是否正确 3. 防火墙是否开放端口")
        return None
    except Exception as e:
        print(f"上传异常：{str(e)}")
        # 确保文件关闭
        for _, file_obj in files:
            file_obj.close()
        return None

# -------------------------- 测试示例 --------------------------
if __name__ == '__main__':
    # 替换为你的 Flask 服务器 IP 和端口（Ubuntu 机器的局域网 IP）
    SERVER_URL = "http://10.160.83.133:5000/upload"
    
    # 替换为你要上传的多个本地图片路径
    FILE_PATHS = [
        "H:/2026/note_hua/images/1.jpg",
        "H:/2026/note_hua/images/2.jpg",
        "H:/2026/note_hua/images/3.jpg"
    ]
    
    # 可选：指定要执行的后端脚本
    SCRIPT_NAME = "process_image.py"
    
    # 执行上传
    upload_multiple_files(SERVER_URL, FILE_PATHS, SCRIPT_NAME)



