# py-common-util


### Specifics
- init version: 0.0.1

### Dependencies
- datetime

### ENV
1. 本地开发环境：pycharm + python3.6.1 + local cpu
2. 远程测试环境：pycharm + remote ssh + gpu
3. 线上环境：待定

### 相关链接
如何将自己的Python代码打包发布到pypi上 https://blog.csdn.net/wdxin1322/article/details/56685094
发布你自己的轮子 - PyPI 打包上传实践 https://juejin.im/entry/58c612e2128fe100603dfc9c

### 上传到pypi的相关命令
1. 升级__version__
1. $ python3 setup.py install (生成build)
2. 打包 $ python3 setup.py sdist （生成dist,egg-info目录）
#3. 安装twine $ sudo pip3 install twine
#注册包 $ twine register dist/py-common-util-0.0.1.tar.gz -r pypi
#上传 $ python3 setup.py sdist upload -r pypi
4. 上传到pypi $ twine upload dist/*
$ pip3 search py-common-util
其它项目安装py-common-util依赖 $ sudo pip3 install py-common-util
或者$ easy_install py-common-util
#### 使用 py-common-util
from common_util import DateUtils
print(DateUtils.now())

### .pypirc
[distutils]
index-servers=pypi
[pypi]
repository=https://upload.pypi.org/legacy/
username=<username>
password=<password>