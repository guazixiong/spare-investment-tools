"""
闲钱永不眠管理计算器 - 启动脚本

运行此脚本启动 Flask 应用服务器。
"""

from src.app import app

if __name__ == '__main__':
    print("=" * 60)
    print("闲钱永不眠管理计算器正在启动...")
    print("=" * 60)
    print("\n访问地址: http://localhost:5000")
    print("API 文档: http://localhost:5000/api/config")
    print("\n按 Ctrl+C 停止服务器\n")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
