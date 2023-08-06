###产生分发包
``
python setup.py sdist
``
###产生分发包
``
python setup.py build
``

###安装方式

1. pip install dist\\mwpermission-0.1.0.zip
2. python setup.py install

### 权限检查
##### 1. 创建
```
from mwpermission.permission import Permission

app = Flask(__name__)
# 设定permission_url 来访问权限资料，推荐在开发模式下使用
app.config['PERMISSION_URL']='http://192.168.101.129:8999/rightmanage/v1.0/permissions?systemname=maxguideweb'
# 没有设定PERMISSION_URL 时，系统使用PERMISSION_ROOT_URL 来自动产生PERMISSION_URL
# permission_url = '%srightmng/%s/permissions?systemname=%s'%(self.permission_root_url,self.version,self.sys)
#app.config['PERMISSION_ROOT_URL'] = '../../'

p = Permission('maxguideweb')
...
p.init_app(app)
...
```
##### 2. 调用权限检查
```
from app import p

# 检查vehicle 是否有 insert，edit的权限
@p.check('vehicle',['insert','edit'])
def vehicle():
    return 'test for insert/edit vehicle'
```

