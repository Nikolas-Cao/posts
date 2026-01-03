---
title: "ComfyUI 使用与实践"
date: 2026-01-03
tags: [ComfyUI, 工作流, 教程]
draft: true
---

# ComfyUI 使用与实践

如果你对搭建一个自己的ai网站(类似grok)感兴趣，那么推荐你阅读本文，阅后，你应该能够理解
 - 什么是comfyui
 - 怎么把comfyui生成的“工作流”提供成Http API接口
 - 怎么在前端调用这个接口

完整效果如下：
![最终效果](../../images/comfyui/home_page_demo.gif)

调用流程如下：
![调用流程](images/comfyui/call-flow.png)


## 快速启动
---

#### 环境与依赖
- 推荐 OS：Windows
- Python 版本：3.12.7
- GPU：NVIDIA + CUDA

```bash
# 下载comfyui源码
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 创建python虚拟环境
cd ./source
py -m venv .venv
.venv\Scripts\activate

# 安装依赖
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```


#### 安装与启动
1. 将模型下载到ComfyUI/models/checkpoints 目录下 (ps. 我的示例中所使用的是 [v1-5-pruned-emaonly.ckpt](https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.ckpt) 模型)
2. 在ComfyUI根目录下执行 `python main.py` , 如果一切正常应该可以在浏览器中访问`http://localhost:8188`看到如下画面 (**这个web页面和演示无关，详细作用参考 [创建comfyui工作流](#创建comfyui工作流) ; 能看到页面正常展示表示comfyui运行成功，如果在运行命令过程中遇到任何问题(依赖版本...)，可以通过咨询AI解决**)
    ![ComfyUI首页](../../images/comfyui/comfyui_website.png)
3. 下载本repo，执行以下命令，然后浏览器中打开`http://127.0.0.1:7627/`
    ``` bash
    cd posts/comfyui/source
    # 进入python虚拟环境 (省略)
    pip install -r requirements.txt
    python server.py
    ```
    ![demo home 页面](../../images/comfyui/demo_home_page.png)


## 详细解释
---
#### 一. 创建comfyui工作流
打开ComfyUI的web页面，创建一个新的工作流 (也可以导入一些别人创建好的模板) ，本篇仅从大体上介绍comfyui的整个使用流程。并不涉及创建工作流的细节，感兴趣的读者可以参考[ComfyUI官方文档](https://docs.comfy.org/)。


> 下面是本文所使用的工作流的`节点结构`：
![comfyui工作流](../../images/comfyui/comfyui_workflow.png)

> 实际调试运行demo效果:
![comfyui工作流 Demo](../../images/comfyui/comfyui_workflow_demo.gif)

可以看出，我修改了`正向提示词`和`反向提示词`，点击`运行`并查看生成的图片效果。在实际的使用中，可以`修改节点的参数`，`增加/删除节点`并点击运行查看效果。（挖个坑，关于comfyui的节点的类型，节点的参数等，以后专门写一篇文章）

#### 二. 将comfyui工作流，通过Http API接口调用
1. 在comfyui中，导出为workflow json文件 [simple_workflow.json](./source/simple_workflow.json) 

> (可以看到 simple_workflow.json中，`6 > inputs > text` 对应我们在comfyui中写的正向提示词，`7 > inputs > text` 对应反向提示词)

2. 编写 [server.py](./source/server.py)
> 主要逻辑是
> - 接受前端传来的请求参数（正向提示词）
> - 加载comfyui工作流json文件
> - 设置工作流中的节点参数（正向提示词）
> - http post调用comfyui的本地接口，获取生成的图片(此处是异步，post接口返回的是prompt_id，需要轮询获取最终结果)
> - 将生成的图片返回给前端展示


## 参考与资源
---
- ComfyUI 项目主页与文档链接
- 相关教程、论文与工具链接


## 下一步工作


## 贡献与许可证
- 如果你希望贡献该博客，请发起 Pull Request。
- 如果你发现错误或有改进建议，请通过 Issue 联系我。
- 如果你希望讨论更深层次的技术细节，也欢迎邮件联系我。
  - 邮箱：291225153@qq.com / hao1997.cao@gmail.com
