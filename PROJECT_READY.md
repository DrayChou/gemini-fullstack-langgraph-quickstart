# 🎉 项目启动完成！使用DeepSeek-V3

## ✅ 当前状态

您的LangGraph项目已经成功配置并启动！

- **🤖 模型**: DeepSeek-V3
- **🔧 API**: OpenAI兼容接口
- **🌐 服务器**: http://localhost:8000
- **📚 API文档**: http://localhost:8000/docs

## 🚀 如何使用

### 1. 启动服务器

```bash
cd backend
uv run python start_server.py
```

服务器启动后会显示：
```
🤖 LangGraph Agent with DeepSeek-V3
✅ API Provider: openai
✅ OpenAI Model: deepseek-v3
🚀 启动LangGraph代理服务...
📍 访问地址:
   - API: http://localhost:8000
   - 文档: http://localhost:8000/docs
   - 前端: http://localhost:8000/app
```

### 2. 访问API文档

打开浏览器访问: http://localhost:8000/docs

这里您可以：
- 查看所有可用的API端点
- 直接在浏览器中测试API
- 查看请求/响应格式

### 3. 测试API功能

运行测试脚本：
```bash
uv run python test_api.py
```

### 4. 启动前端界面

```bash
cd ../frontend
npm install
npm run dev
```

然后访问: http://localhost:3000

## 🔧 配置说明

当前配置文件 `.env`:
```env
API_PROVIDER=openai
OPENAI_API_KEY=sk-st8GjC8...
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-v3
```

### 切换模型

如果要切换到其他模型，修改 `.env` 文件中的 `OPENAI_MODEL`:

```env
# 使用GPT-4
OPENAI_MODEL=gpt-4

# 使用GPT-3.5
OPENAI_MODEL=gpt-3.5-turbo

# 使用Claude (如果您的代理支持)
OPENAI_MODEL=claude-3-sonnet

# 回到DeepSeek-V3
OPENAI_MODEL=deepseek-v3
```

修改后重启服务器即可生效。

## 📝 API使用示例

### 基本查询

```python
import requests

response = requests.post(
    "http://localhost:8000/agent/invoke",  # 具体端点可能不同
    json={
        "messages": [
            {
                "role": "human", 
                "content": "什么是机器学习？"
            }
        ]
    }
)

result = response.json()
print(result)
```

### 使用curl

```bash
curl -X POST "http://localhost:8000/agent/invoke" \
     -H "Content-Type: application/json" \
     -d '{
       "messages": [
         {
           "role": "human",
           "content": "解释一下人工智能的发展历史"
         }
       ]
     }'
```

## 🛠️ 故障排除

### 1. 服务器启动失败

检查：
- API密钥是否正确
- 网络连接是否正常
- 端口8000是否被占用

### 2. 模型无法调用

检查：
- OPENAI_BASE_URL是否可以访问
- 模型名称是否正确
- API配额是否充足

### 3. 前端无法访问

确保：
- 后端服务器正在运行
- 前端依赖已安装 (`npm install`)
- 前端开发服务器已启动 (`npm run dev`)

## 🎯 下一步

现在您可以：

1. **测试对话功能** - 访问API文档页面进行测试
2. **集成到您的应用** - 使用提供的API端点
3. **自定义配置** - 根据需要调整模型和参数
4. **部署到生产** - 使用Docker或其他部署方式

## 📞 需要帮助？

如果遇到问题，请：
1. 查看控制台输出的错误信息
2. 检查API文档页面是否可以访问
3. 运行测试脚本确认配置

🎉 **恭喜！您的DeepSeek-V3 LangGraph项目已经可以使用了！**
