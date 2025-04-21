import os
from flask import Flask, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

# 配置文件参数
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'} 
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 最大文件大小（10MB）

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    """检查文件扩展名是否合法"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_image():
    """处理图片上传请求"""
    if 'file' not in request.files:
        return jsonify({"error": "未选择文件"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "文件名为空"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "仅支持PNG、JPG、JPEG、GIF、WEBP格式"}), 400
    
    try:
        # 生成唯一文件名防止冲突
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(filename)
        
        # 保存文件
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # 返回访问URL
        image_url = f"http://8.140.200.27:5000/images/{filename}"
        return jsonify({"url": image_url}), 200
    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

@app.route('/images/<filename>')
def get_image(filename):
    """返回图片文件"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({"error": "图片不存在"}), 404

if __name__ == '__main__':
    # 创建上传目录（如果不存在）
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    # 启动服务（生产环境请勿使用 debug=True）
    app.run(host='0.0.0.0', port=5000, debug=False)
