# OpenAI 版本迁移指南

## 概述

此项目已从 Google Gemini API 迁移到 OpenAI GPT-4 API。以下是主要的变更和配置步骤。

## 主要变更

### 1. 依赖项变更
- 添加了 `langchain-openai` 和 `openai` 包
- 添加了 `duckduckgo-search` 用于替代 Google Search API
- 保留了原有的 `langchain-google-genai` 包以保持向后兼容性

### 2. 环境变量
- 新增：`OPENAI_API_KEY` - OpenAI API 密钥
- 保留：`GEMINI_API_KEY` - 向后兼容（可选）

### 3. 模型配置
默认模型已更改：
- 查询生成器：`gpt-3.5-turbo`（原：`gemini-2.0-flash`）
- 反思模型：`gpt-4`（原：`gemini-2.5-flash-preview-04-17`）
- 答案模型：`gpt-4`（原：`gemini-2.5-pro-preview-05-06`）

### 4. 搜索API替换
- 从 Google Search API 迁移到 DuckDuckGo Search API
- 不再需要 Google Search API 凭据

## 配置步骤

### 1. 获取 OpenAI API 密钥
1. 访问 [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. 登录或创建账户
3. 生成新的 API 密钥

### 2. 设置环境变量
复制 `.env-openai` 文件为 `.env`：
```bash
cp .env-openai .env
```

编辑 `.env` 文件，设置你的 OpenAI API 密钥：
```
OPENAI_API_KEY=your-actual-openai-api-key-here
```

### 3. 安装依赖
```bash
cd backend
pip install -e .
```

### 4. 运行项目

#### 使用 Docker Compose
```bash
# 使用 OpenAI 版本
docker-compose -f docker-compose-openai.yml up --build
```

#### 本地运行
```bash
cd backend
python -m agent.app
```

## 新增文件

### `backend/src/agent/openai_adapter.py`
OpenAI 模型的适配器，提供与原 ChatGoogleGenerativeAI 类似的接口。

### `backend/src/agent/search_adapter.py`
DuckDuckGo 搜索适配器，替代 Google Search API。

### `backend/src/agent/utils_openai.py`
OpenAI 特定的工具函数，用于处理引用和 URL 解析。

## 成本考虑

使用 OpenAI API 会产生费用，建议：

1. 设置使用限制
2. 监控 API 使用情况
3. 考虑使用更便宜的模型（如 `gpt-3.5-turbo`）进行开发测试

## 功能差异

### 优势
- 更强的推理能力（GPT-4）
- 更好的结构化输出支持
- 不需要 Google Search API 配置

### 限制
- API 调用成本
- 没有原生的搜索集成（使用 DuckDuckGo 替代）
- 引用系统需要重新实现

## 故障排除

### 常见问题

1. **API 密钥错误**
   - 确保 `OPENAI_API_KEY` 正确设置
   - 检查 API 密钥是否有效且有足够的额度

2. **模型不存在错误**
   - 确保你的 OpenAI 账户可以访问指定的模型
   - 可以尝试使用 `gpt-3.5-turbo` 替代 `gpt-4`

3. **搜索结果问题**
   - DuckDuckGo 搜索可能返回不同的结果
   - 可以调整 `search_adapter.py` 中的搜索参数

### 调试

启用详细日志：
```bash
export LANGCHAIN_VERBOSE=true
export LANGCHAIN_DEBUG=true
```

## 向后兼容

如果需要切换回 Gemini API：
1. 设置 `GEMINI_API_KEY` 环境变量
2. 使用原始的 `docker-compose.yml` 文件
3. 恢复原始的 `graph.py` 文件（从 git 历史）

## 测试

运行集成测试：
```bash
cd backend
python test_integration.py
```

## 贡献

如果你发现问题或有改进建议，请提交 issue 或 pull request。
