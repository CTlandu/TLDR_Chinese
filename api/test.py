from http.server import BaseHTTPRequestHandler
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # 测试导入
        try:
            from api import create_app
            from config import get_config
            
            config = get_config()
            app = create_app(config)
            
            response = {
                'message': 'Flask app 初始化成功！',
                'status': 'success',
                'app_name': app.name
            }
        except Exception as e:
            response = {
                'message': 'Flask app 初始化失败',
                'status': 'error',
                'error': str(e),
                'error_type': type(e).__name__
            }
        
        self.wfile.write(json.dumps(response).encode())
        return

