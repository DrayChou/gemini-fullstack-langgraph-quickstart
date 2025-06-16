# DeepSeek-V3 配置使用指南

## 当前配置状态 ✅

您的项目已经成功配置为使用 DeepSeek-V3 模型！

## 配置方法说明

### 方法1：使用 OPENAI_MODEL 统一配置（推荐）

在 `.env` 文件中设置：
```bash
API_PROVIDER=openai
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://your-proxy-url.com/v1
OPENAI_MODEL=deepseek-v3
```

这会让所有任务（查询生成、反思、回答）都使用 DeepSeek-V3 模型。

### 方法2：分别配置不同任务的模型

如果您想为不同任务使用不同模型：
```bash
API_PROVIDER=openai
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://your-proxy-url.com/v1

# 为不同任务分别配置
QUERY_GENERATOR_MODEL=deepseek-v3
REFLECTION_MODEL=gpt-4
ANSWER_MODEL=deepseek-v3
```

### 方法3：快速切换模型

想要切换到其他模型时，只需修改环境变量：

```bash
# 切换到 GPT-4
OPENAI_MODEL=gpt-4

# 切换到 GPT-3.5
OPENAI_MODEL=gpt-3.5-turbo

# 切换回 DeepSeek-V3
OPENAI_MODEL=deepseek-v3
```

## 如何启动项目

### 1. 启动后端服务

```bash
cd backend
uv run python -m agent.app
```

### 2. 启动前端服务

```bash
cd frontend
npm install  # 或 pnpm install
npm run dev  # 或 pnpm dev
```

### 3. 使用 Docker 启动

```bash
# 使用 OpenAI 配置
docker-compose -f docker-compose-openai.yml up --build
```

## 验证配置

运行测试确认配置正确：

```bash
# 测试 API 连接
uv run python test_api_connection.py

# 测试 DeepSeek-V3 配置
uv run python test_deepseek.py

# 完整集成测试
uv run python test_integration.py
```

## 支持的模型列表

通过设置 `OPENAI_MODEL` 环境变量，您可以使用任何兼容 OpenAI API 的模型：

- `deepseek-v3` - DeepSeek V3 (当前配置)
- `gpt-4` - GPT-4
- `gpt-4-turbo` - GPT-4 Turbo
- `gpt-3.5-turbo` - GPT-3.5 Turbo
- `claude-3-sonnet` - Claude 3 Sonnet (如果您的代理支持)
- 其他兼容模型...

## 费用说明

不同模型的费用不同：
- **DeepSeek-V3**: 相对便宜，性能优秀
- **GPT-4**: 费用较高，但质量最好
- **GPT-3.5**: 费用较低，适合大量测试

## 故障排除

如果遇到问题：

1. **检查 API 密钥**：确保 `OPENAI_API_KEY` 正确
2. **检查代理 URL**：确保 `OPENAI_BASE_URL` 可访问
3. **检查模型名称**：确保模型名称正确拼写
4. **查看日志**：运行测试时查看错误信息

## 当前配置总结

✅ **API 提供商**: OpenAI 兼容接口  
✅ **模型**: DeepSeek-V3  
✅ **代理**: 已配置  
✅ **搜索**: DuckDuckGo  
✅ **配置方式**: 环境变量驱动，无需修改代码  

现在您可以直接启动项目并享受 DeepSeek-V3 的强大功能！
