"""
@author: lihang
@time: 2017/12/26 11:30
@describe:
"""
from web import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)
