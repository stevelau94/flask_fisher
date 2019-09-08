from flask import make_response

from app import create_app

app = create_app()

if __name__ == '__main__':
    # 生产环节不使用flask服务器，使用nginx+uwsgi
    # 所以需要if __name__ == '__main__'判断
    app.run(host='0.0.0.0', debug=app.config['DEBUG'], threaded=True)
