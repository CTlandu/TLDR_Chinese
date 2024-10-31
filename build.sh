#!/bin/bash

# 安装 python 依赖
pip install -r requirements.txt

# 安装 nodejs 和 npm
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# 安装前端依赖
npm install

# 构建前端
npm run build