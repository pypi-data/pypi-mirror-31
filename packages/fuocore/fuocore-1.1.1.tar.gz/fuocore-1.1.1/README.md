# feeluown-core 1.x

**WARNING**: 这个版本不会加入更多 feature，只会修复一些 bug，主要为 feeluown 1.x 服务。

[![Documentation Status](https://readthedocs.org/projects/feeluown-core/badge/?version=latest)](http://feeluown-core.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/cosven/feeluown-core.svg?branch=master)](https://travis-ci.org/cosven/feeluown-core)
[![Coverage Status](https://coveralls.io/repos/github/cosven/feeluown-core/badge.svg?branch=master)](https://coveralls.io/github/cosven/feeluown-core?branch=master)
[![PyPI](https://img.shields.io/pypi/v/fuocore.svg)](https://pypi.python.org/pypi/fuocore)
[![python](https://img.shields.io/pypi/pyversions/fuocore.svg)](https://pypi.python.org/pypi/fuocore)

录了个几分钟的简短的演示视频 👇

[![Video Show](http://img.youtube.com/vi/-JFXo0J5D9E/0.jpg)](https://youtu.be/-JFXo0J5D9E)

## Features

1. C/S 架构，客户端和服务端基于 TCP 进行通信
   [protocol](http://feeluown-core.readthedocs.io/en/latest/protocol.html#fuo-protocol)
2. 输出为 text stream，能被 grep/awk/cut 等工具方便的处理
3. 抽象 netease/xiami 相关三方资源
4. 像管理 dotfile 一样管理播放列表、喜欢的歌手等音乐资源
   [for example](https://github.com/cosven/cosven.github.io/blob/master/music/mix.fuo)
5. 代码对新手友好，开发者可以快速的开发小功能或者修复 bug

## TODOs

- [ ] (✭✭✭) 提供命令可以展示 歌曲/歌手/专辑 相关有趣的故事 [0%]
  网易云音乐评论？豆瓣音乐信息？AI?
- [ ] (✭✭✭) 代码优化和文档补全 [0%]
- [ ] (✭) p2p like? [0%]
- [ ] (✭) qq music resources [0%]

## Install

```sh
sudo apt-get install libmpv1  # Debian or Ubuntu
brew install mpv  # mac osx

# please always use the latest release
pip3 install fuocore --upgrade
pip3 install fuocli --upgrade
```

## Simple Usage

```
# start daemon
fuo --debug
# nohup fuo &  # 后台运行

# use fuocli
fuocli search '谢春花' | grep songs | head -n 10 | awk '{print $1}' | fuocli add
fuocli add fuo://netease/songs/45849608
fuocli remove fuo://netease/songs/45849608
fuocli play fuo://netease/songs/458496082
fuocli list
fuocli next
fuocli status
fuocli pause
fuocli resume
```

## FQA

## Contributing to fuocore
请参考文档 [Development](http://feeluown-core.readthedocs.io/en/latest/development.html)
