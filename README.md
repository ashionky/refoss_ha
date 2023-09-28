# refoss_ha
- Refoss to support for  Home Assistant
- 安装setuptools和wheel
  - python3 -m pip install  --upgrade setuptools wheel
- 打包
  - python3 setup.py bdist_wheel
  - python3 -m twine upload dist/refoss_ha-1.1.6-py3-none-any.whl
