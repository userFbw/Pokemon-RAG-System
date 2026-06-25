[readme.md](https://github.com/user-attachments/files/29332132/readme.md)
# 基于 RAG 的宝可梦图像知识库检索系统

## 项目简介
本项目基于阿里云 ECS 部署，采用 Docker 容器化技术与 Nginx 反向代理，底层使用 Dify 平台构建了包含“意图识别-混合检索-多模态生成”的 Agent 工作流。

## 目录结构说明
* `1_Data_Engineering/`: 包含 Python 自动化清洗脚本，用于调用 DeepSeek API 实现双语知识库的自动化重构。
* `2_Cloud_Infrastructure/`: 包含 Nginx 网关配置文件与 Docker 部署参考，实现了应用服务与静态媒体资源的端口级解耦。
* `3_Dify_Agent_Workflow/`: 包含了从 Dify 导出的 Agent 工作流 DSL 配置文件，记录了所有 Prompt 设计、节点连接与大模型参数。

## 开发成员
方博闻、林灿仰、卜仕、蔡智杰、罗梓浩
