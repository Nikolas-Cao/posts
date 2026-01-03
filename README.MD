# 技术博客（Technical Blog）

这是一个用于撰写和维护技术博客文章的轻量级仓库。仓库只用于存放博客原始 Markdown 源文件、配套资源以及发布/预览相关的说明。

## 目的
- 集中管理技术文章与笔记。
- 以 Markdown 为主，便于阅读、版本控制与迁移到静态站点生成器。

## 仓库结构（推荐）
- `posts/` —— 所有博客文章的 Markdown 文件（例如：posts/2026-01-03-article.md）。
- `images/` —— 文章中使用的图片或媒体资源。
- `README.MD` —— 本文件，介绍仓库用途与协作规范。

## 写作规范（建议）
- 使用 UTF-8 编码与标准 Markdown 格式。
- 每篇文章顶部建议包含 Front Matter（YAML），例如：

	---
	title: "文章标题"
	date: 2026-01-03
	tags: [tag1, tag2]
	draft: false
	---

- 文件名建议使用日期前缀加短横线（YYYY-MM-DD-short-title.md），便于排序与管理。

## 预览与发布
- 如果需要在本地预览，建议使用支持 Markdown 实时预览的编辑器（VS Code 等），或用静态站点生成器（如 Hugo、Jekyll、Hexo）构建站点。

## 许可与作者
- 本仓库内容默认归作者所有。若希望公开许可，请在仓库根目录添加 LICENSE 文件并说明许可类型。

欢迎投稿与讨论：如需协作，请发起 Pull Request 或通过 Issue 联系。