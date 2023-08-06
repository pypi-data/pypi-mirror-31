###产生分发包
``
python setup.py sdist
twine upload dist/*
``
###产生分发包
``
python setup.py build
``

###安装方式
1. pip install dist\\mwutils-0.1.1.zip
2. python setup.py install