### 支持的认证方式
> 1,basic认证  
> 2,基于kong api gateway 的JWT认证 ，[认证服务器源码](https://bitbucket.org/maxwin-inc/auth_kong/src/master/) 
> 3,cookie 的session认证  ，[session认证服务器源码](https://bitbucket.org/maxwin-inc/auth_service3/src/master/)
###产生分发包
```
python setup.py sdist
```
###上传分发包
```
twine upload dist/*
```

###安装方式
1. pip install mwauth
2. python setup.py install



