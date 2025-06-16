# Gemini 到 OpenAI API 迁移总结

## 修改概述

本项目已成功实现从单一的 Google Gemini API 到支持多 API 提供商的架构，用户可以选择使用 Gemini 或 OpenAI 的模型。

## 主要修改

### 1. 配置系统重构

**文件**: `backend/src/agent/configuration.py`

- 添加了 `api_provider` 字段，支持 "gemini", "openai", "auto" 选择
- 添加了 `search_provider` 字段，支持 "duckduckgo", "google" 选择
- 实现了 `get_default_models()` 方法，根据 API 提供商返回默认模型配置
- 实现了 `get_model()` 方法，动态获取配置的模型或使用默认值

### 2. LLM 工厂模式

**文件**: `backend/src/agent/llm_factory.py`

- 创建了 `LLMFactory` 类来统一管理不同 API 提供商的模型创建
- 支持条件导入，避免在缺少依赖时出错
- 实现了 API 密钥验证和错误处理

### 3. OpenAI 适配器

**文件**: `backend/src/agent/openai_adapter.py`

- 创建了 `CustomOpenAIChat` 类，提供与 `ChatGoogleGenerativeAI` 兼容的接口
- 实现了结构化输出功能，支持 JSON Schema 解析
- 处理了 OpenAI 和 Gemini API 的参数差异

### 4. 搜索系统重构

**文件**: `backend/src/agent/search_factory.py`

- 创建了 `SearchFactory` 类来管理不同搜索提供商
- 支持 DuckDuckGo 搜索（免费，无需 API 密钥）
- 保留了 Google 搜索支持（需要 Gemini API）

**文件**: `backend/src/agent/search_adapter.py`

- 实现了 DuckDuckGo 搜索适配器
- 提供了统一的搜索结果格式化

### 5. 主要图形逻辑更新

**文件**: `backend/src/agent/graph.py`

- 重构了所有主要函数以使用工厂模式
- 移除了硬编码的 Gemini 客户端依赖
- 实现了提供商无关的模型调用

### 6. 环境配置

**文件**: `backend/.env.template`

- 提供了完整的环境变量模板
- 支持两种 API 提供商的配置
- 包含了模型配置选项

**文件**: `backend/docker-compose-openai.yml`

- 创建了专门的 OpenAI Docker 配置

## API 协议差异处理

### 1. 模型调用差异

| 方面 | Gemini | OpenAI |
|------|--------|--------|
| 客户端 | `google.genai.Client` | `openai.OpenAI` |
| 模型调用 | `generate_content()` | `chat.completions.create()` |
| 返回结构 | `response.text` | `response.choices[0].message.content` |
| 结构化输出 | 内置支持 | 需要 JSON 解析 |

### 2. 搜索集成差异

| 方面 | Gemini | OpenAI |
|------|--------|--------|
| 搜索API | 原生 Google Search | 外部 DuckDuckGo |
| 引用数据 | `grounding_metadata` | 手动构建 |
| URL解析 | 自动处理 | 需要自定义逻辑 |

### 3. 错误处理差异

- Gemini: 地区限制错误处理
- OpenAI: API 配额和密钥验证
- 统一错误消息格式

## 使用方法

### 1. 环境配置

```bash
# 复制模板文件
cp .env.template .env

# 编辑配置
# 设置 API_PROVIDER=openai 或 gemini
# 设置对应的 API 密钥
```

### 2. 依赖安装

```bash
# 使用 UV 同步依赖
uv sync
```

### 3. 运行测试

```bash
# 测试基本配置
uv run python test_config.py

# 测试 OpenAI 特定功能
uv run python test_openai_config.py

# 测试搜索功能
uv run python test_api_connection.py
```

### 4. 运行应用

```bash
# 本地运行
uv run python -m agent.app

# 或使用 Docker
docker-compose -f docker-compose-openai.yml up --build
```

## 测试结果

当前测试状态：

✅ **工作正常**:
- OpenAI API 集成
- DuckDuckGo 搜索
- 配置系统
- 多提供商支持

❌ **存在问题**:
- Gemini API（地区限制）

⚠️ **需要注意**:
- OpenAI API 会产生费用
- DuckDuckGo 搜索结果可能与 Google 不同
- 需要有效的 API 密钥才能运行完整功能

## 向后兼容性

- 保留了所有原始的 Gemini 相关代码
- 原始配置仍然有效
- 可以轻松切换回 Gemini（如果地区支持）

## 未来改进建议

1. **添加更多搜索提供商**: Bing, Yahoo 等
2. **实现模型性能对比**: 不同提供商的效果评估
3. **添加成本监控**: API 调用费用跟踪
4. **优化错误恢复**: 自动切换到可用的提供商
5. **支持混合模式**: 不同任务使用不同提供商
