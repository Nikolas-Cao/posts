---
title: "ComfyUI 使用与实践"
date: 2026-01-03
tags: [ComfyUI, 工作流, 全栈部署, 教程]
draft: true
---

# ComfyUI 使用与实践

如果你对搭建一个自己的ai网站(类似openai)感兴趣，那么推荐你阅读本文，阅后你应该能够理解

- 什么是comfyui
- 怎么把comfyui生成的“工作流”提供成Http API接口
- 怎么在前端调用这个接口

**完整效果如下：**

<p align="center"><img src="../../images/comfyui/home_page_demo.gif" alt="最终效果" style="max-width:100%;height:auto;display:block;margin:0 auto"></p>

**调用流程如下：**

<p align="center"><img src="../../images/comfyui/comfyui_work_structure.png" alt="调用流程" style="max-width:100%;height:auto;display:block;margin:0 auto"></p>


## 快速启动

### 环境与依赖
- 推荐 OS：Windows
- Python 版本：3.12.7
- GPU：NVIDIA + CUDA

<div style="border-left:4px solid #2196F3;padding:0.5em 1em;background:#f1f8ff;margin:0.75em 0;">
<strong>提示：</strong> 本文以 Windows 为主要演示环境；在 Linux/macOS 上的路径与虚拟环境命令略有不同，请按需调整。
</div>

```bash
# 下载comfyui源码
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 创建python虚拟环境
cd ./source
py -m venv .venv
.venv\Scripts\activate.bat

# 安装依赖
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

### 安装与启动
1. 将模型下载到ComfyUI/models/checkpoints 目录下 (ps. 本文中所使用的是 [v1-5-pruned-emaonly.ckpt](https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.ckpt) 模型)
2. 在ComfyUI根目录下执行 `python main.py` , 如果一切正常，在浏览器中访问`http://localhost:8188` 可以看到如下画面
    <p align="center"><img src="../../images/comfyui/comfyui_website.png" alt="ComfyUI首页" style="max-width:100%;height:auto;display:block;margin:0 auto"></p>
3. 下载本repo，执行以下命令，然后浏览器中打开 `http://127.0.0.1:7627/` ，即可使用纯本地部署的文生图网站
    ```bash
    cd posts/comfyui/source
    # 进入python虚拟环境 (省略)
    pip install -r requirements.txt
    python server.py
    ```
    <p align="center"><img src="../../images/comfyui/demo_home_page.png" alt="demo home 页面" style="max-width:100%;height:auto;display:block;margin:0 auto"></p>

## 技术实现详解

### 一.创建comfyui工作流
打开ComfyUI的web页面，创建一个新的工作流 (也可以导入一些别人创建好的模板)
<div style="border-left:4px solid #4CAF50;padding:0.5em 1em;background:#f6fff6;margin:0.75em 0;">
<strong>说明：</strong>本篇仅从大体上介绍comfyui的整个使用流程。并不涉及创建工作流的细节，感兴趣的读者可以参考 <a href="https://docs.comfy.org/">ComfyUI官方文档</a>
</div>

<p align="center"><img src="../../images/comfyui/comfyui_workflow.png" alt="comfyui工作流" style="max-width:100%;height:auto;display:block;margin:0 auto"></p>

**实际调试运行demo效果(GIF):**
<p align="center"><img src="../../images/comfyui/comfyui_workflow_demo.gif" alt="comfyui工作流 Demo" style="max-width:100%;height:auto;display:block;margin:0 auto"></p>

从demo效果中可以看到，我修改了`正向提示词`和`反向提示词`，然后点击`运行`并查看生成的图片效果。
在实际使用comfyui调试过程中，可以`修改节点的参数`，`增加/删除节点`来修改工作流。（挖个坑，关于comfyui的节点的类型，节点的参数等，以后专门写一篇文章）

### 二.将comfyui工作流，通过Http API接口调用
1. 在comfyui中，将工作流导出为json文件 [simple_workflow.json](./source/simple_workflow.json) 

    > (可以看到导出的 simple_workflow.json中，`6 > inputs > text` 对应我们在comfyui中写的正向提示词，`7 > inputs > text` 对应反向提示词)

2. 编写 [server.py](./source/server.py)

    > `server.py` 的主要逻辑是
    > - 接受前端传来的请求参数（正向提示词）
    > - IO读取 [simple_workflow.json](./source/simple_workflow.json) 
    > - 将json中的`正向提示词`替换为前端发过来的用户输入
    > - http post调用comfyui的本地接口(默认 http://127.0.0.1:8188/prompt )，获取生成的图片(此处是异步，post接口返回的是prompt_id，需要轮询获取最终结果)
    > - 将生成的图片返回给前端展示

### 三.提供一个前端html页面 [index.html](./source/index.html)

在server.py中，使用FastAPI的静态文件功能，提供一个简单的前端页面(index.html)，用户可以在页面中输入提示词，然后点击生成按钮，调用后端接口，获取生成的图片并展示。


## 参考与资源

- [ComfyUI](https://docs.comfy.org/) : 开源的节点式图形界面工具，主要用于 Stable Diffusion 等扩散模型，实现高度自定义的 AI 图像、视频甚至 3D 生成工作流。
- [huggingface](https://huggingface.co) : 一个开源的机器学习平台，被誉为“AI社区构建未来的家园”，主要供全球开发者协作分享、发现和使用海量预训练模型、数据集以及AI应用。


## 下一步工作

- 优化图片获取流程
    > 当前，前端页面发送一个http post图片生成请求后，后端会轮询获取最终生成的图片，并将图片作为http post的响应返回给前端。这部分有待优化，可以调研下目前商业化的图片生成接口是如何实现的。

- 支持更多能力 (图生图，文生视频，图生视频 ...)
    > 目前仅支持最基础的文生图功能，而且模型比较小，工作流中节点参数也没有经过严谨的微调，后续可以支持更多comfyui工作流的功能

- 支持历史记录
    > 目前前端页面仅支持单次生成，后续可以支持用户查看历史生成记录，方便用户对比不同提示词的生成效果

- 支持上下文关联
    > 目前前端页面的每次请求都是独立的，后续可以支持上下文关联，比如用户可以基于之前生成的图片进行修改，或者基于之前的提示词进行扩展（需要重新设计前端交互逻辑）

## 贡献与许可证

- 如果你希望贡献该博客，请发起 Pull Request。
- 如果你发现错误或有改进建议，请通过 Issue 联系。
- 如果你希望讨论更深层次的技术细节，也欢迎邮件联系。
    - 邮箱：291225153@qq.com / hao1997.cao@gmail.com
