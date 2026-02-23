import os
import json
import logging
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify

# 初始化 Flask 应用
app = Flask(__name__)

# -------------------------- 配置项 --------------------------
# 上传文件存储路径（绝对路径更稳定，替换为你的实际路径）
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads/images')
# 允许上传的图片格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
# 最大上传文件大小（50MB）
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
# 后端脚本目录
SCRIPT_FOLDER = os.path.join(os.path.dirname(__file__), 'scripts')
# 日志配置
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'logs/app.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# -------------------------- 工具函数 --------------------------
def allowed_file(filename):
    """验证文件是否为允许的图片格式"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def run_backend_script(script_name, image_path):
    """运行后端脚本，返回执行结果"""
    script_path = os.path.join(SCRIPT_FOLDER, script_name)
    # 检查脚本是否存在
    if not os.path.exists(script_path):
        return {
            'status': 'error',
            'message': f'脚本 {script_name} 不存在'
        }
    
    try:
        # 执行脚本（这里以 Python 脚本为例，可根据需要修改为 bash/sh 等）
        result = subprocess.run(
            ['python3', script_path, image_path],  # 脚本参数：图片路径
            capture_output=True,
            text=True,
            timeout=30  # 超时时间 30 秒
        )
        
        # 解析执行结果
        if result.returncode == 0:
            return {
                'status': 'success',
                'message': '脚本执行成功',
                'output': result.stdout
            }
        else:
            return {
                'status': 'error',
                'message': '脚本执行失败',
                'error': result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'message': '脚本执行超时'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'脚本执行异常: {str(e)}'
        }

# -------------------------- 路由 --------------------------
'''
@app.route('/upload', methods=['POST'])
def upload_image():
    """
    图片上传接口
    请求方式：POST
    请求格式：multipart/form-data
    参数：
        file: 图片文件
        script: 可选，要运行的后端脚本名称（如 process_image.py）
    返回：JSON 格式响应
    """
    # 检查请求是否包含文件
    if 'file' not in request.files:
        logging.error('上传请求中无文件')
        return jsonify({
            'code': 400,
            'msg': '请选择要上传的图片文件'
        }), 400
    
    file = request.files['file']
    # 检查文件名是否为空
    if file.filename == '':
        logging.error('上传文件名为空')
        return jsonify({
            'code': 400,
            'msg': '文件名不能为空'
        }), 400
    
    # 验证文件格式
    if file and allowed_file(file.filename):
        try:
            # 生成唯一文件名（避免重复）
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # 保存文件
            file.save(file_path)
            logging.info(f'图片上传成功: {file_path}')
            
            # 检查是否需要运行后端脚本
            script_name = request.form.get('script')
            script_result = None
            if script_name:
                script_result = run_backend_script(script_name, file_path)
                logging.info(f'脚本 {script_name} 执行结果: {script_result}')
            
            # 返回成功响应
            return jsonify({
                'code': 200,
                'msg': '图片上传成功',
                'data': {
                    'file_path': file_path,
                    'filename': filename,
                    'script_result': script_result if script_result else '未执行脚本'
                }
            }), 200
        
        except Exception as e:
            logging.error(f'图片上传失败: {str(e)}')
            return jsonify({
                'code': 500,
                'msg': f'上传失败: {str(e)}'
            }), 500
    else:
        logging.error(f'不支持的文件格式: {file.filename}')
        return jsonify({
            'code': 400,
            'msg': f'仅支持 {", ".join(ALLOWED_EXTENSIONS)} 格式的图片'
        }), 400
'''

@app.route('/upload', methods=['POST'])
def upload_image():
    """
    多图片上传接口（兼容单文件）
    请求方式：POST
    请求格式：multipart/form-data
    参数：
        files: 多个图片文件（键名统一用 files，可传多个）
        script: 可选，要运行的后端脚本名称（如 process_image.py）
    返回：JSON 格式响应
    """
    # 检查请求是否包含文件
    if 'files' not in request.files:
        logging.error('上传请求中无文件')
        return jsonify({
            'code': 400,
            'msg': '请选择要上传的图片文件'
        }), 400
    
    # 获取所有上传的文件
    files = request.files.getlist('files')
    if len(files) == 0 or all(file.filename == '' for file in files):
        logging.error('上传文件名为空')
        return jsonify({
            'code': 400,
            'msg': '文件名不能为空'
        }), 400
    
    # 存储每个文件的上传结果
    upload_results = []
    script_name = request.form.get('script')
    
    for file in files:
        file_result = {}
        # 跳过空文件名的文件
        if file.filename == '':
            file_result['filename'] = '空文件'
            file_result['status'] = 'failed'
            file_result['msg'] = '文件名不能为空'
            upload_results.append(file_result)
            continue
        
        # 验证文件格式
        if allowed_file(file.filename):
            try:
                # 生成唯一文件名
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S_%f')  # 加微秒避免重复
                filename = f"{timestamp}_{file.filename}"
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                
                # 保存文件
                file.save(file_path)
                logging.info(f'图片上传成功: {file_path}')
                
                # 执行脚本（如果指定）
                script_result = None
                if script_name:
                    script_result = run_backend_script(script_name, file_path)
                    logging.info(f'脚本 {script_name} 执行结果: {script_result}')
                
                # 记录成功结果
                file_result['filename'] = file.filename
                file_result['status'] = 'success'
                file_result['saved_filename'] = filename
                file_result['file_path'] = file_path
                file_result['script_result'] = script_result if script_result else '未执行脚本'
                upload_results.append(file_result)
            except Exception as e:
                logging.error(f'图片 {file.filename} 上传失败: {str(e)}')
                file_result['filename'] = file.filename
                file_result['status'] = 'failed'
                file_result['msg'] = str(e)
                upload_results.append(file_result)
        else:
            logging.error(f'不支持的文件格式: {file.filename}')
            file_result['filename'] = file.filename
            file_result['status'] = 'failed'
            file_result['msg'] = f'仅支持 {", ".join(ALLOWED_EXTENSIONS)} 格式的图片'
            upload_results.append(file_result)
    
    # 返回批量上传结果
    return jsonify({
        'code': 200,
        'msg': f'批量上传完成，成功 {len([r for r in upload_results if r["status"]=="success"])} / 总 {len(upload_results)}',
        'data': upload_results
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口，用于验证服务是否正常运行"""
    return jsonify({
        'code': 200,
        'msg': '服务正常运行',
        'data': {
            'upload_folder': UPLOAD_FOLDER,
            'script_folder': SCRIPT_FOLDER,
            'allowed_extensions': list(ALLOWED_EXTENSIONS)
        }
    }), 200

# -------------------------- 启动服务 --------------------------
if __name__ == '__main__':
    # 确保上传目录和脚本目录存在
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(SCRIPT_FOLDER, exist_ok=True)
    # 启动 Flask 服务（Ubuntu 下允许外部访问，端口 5000）
    app.run(debug=True, host='0.0.0.0', port=5000)



