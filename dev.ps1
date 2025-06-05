param(
    [Parameter(Position=0)]
    [ValidateSet("help", "frontend", "backend", "dev", "stop")]
    [string]$Command = "help"
)

# 颜色输出函数
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

# 显示帮助信息
function Show-Help {
    Write-ColorOutput "=== 开发环境管理脚本 ===" "Cyan"
    Write-ColorOutput ""
    Write-ColorOutput "用法: .\dev.ps1 [命令]" "Yellow"
    Write-ColorOutput ""
    Write-ColorOutput "可用命令:" "Green"
    Write-ColorOutput "  help      - 显示此帮助信息" "White"
    Write-ColorOutput "  frontend  - 启动前端开发服务器 (http://localhost:5173/app)" "White"
    Write-ColorOutput "  backend   - 启动后端开发服务器 (http://localhost:2024)" "White"
    Write-ColorOutput "  dev       - 同时启动前端和后端 (推荐)" "White"
    Write-ColorOutput "  stop      - 停止所有开发服务器" "White"
    Write-ColorOutput ""
    Write-ColorOutput "环境要求:" "Yellow"
    Write-ColorOutput "  - Node.js 和 npm (前端)" "Gray"
    Write-ColorOutput "  - Python 3.8+ (后端)" "Gray"
    Write-ColorOutput "  - GEMINI_API_KEY 环境变量 (必需)" "Gray"
    Write-ColorOutput ""
    Write-ColorOutput "示例:" "Yellow"
    Write-ColorOutput "  .\dev.ps1 dev" "Gray"
    
    # 检查环境变量
    Test-Environment
}

# 检查环境配置
function Test-Environment {
    Write-ColorOutput ""
    Write-ColorOutput "=== 环境检查 ===" "Cyan"
    
    # 检查 GEMINI_API_KEY
    if ($env:GEMINI_API_KEY) {
        Write-ColorOutput "✅ GEMINI_API_KEY 已设置" "Green"
    } elseif (Test-Path "backend/.env") {
        Write-ColorOutput "✅ 发现 backend/.env 文件" "Green"
    } else {
        Write-ColorOutput "❌ GEMINI_API_KEY 未设置，且未找到 backend/.env 文件" "Red"
        Write-ColorOutput "💡 请创建 backend/.env 文件并添加 GEMINI_API_KEY" "Yellow"
    }
    
    # 检查代理配置
    if ($env:HTTP_PROXY -or $env:HTTPS_PROXY) {
        Write-ColorOutput "🔒 检测到代理配置" "Blue"
        if ($env:HTTP_PROXY) { Write-ColorOutput "   HTTP_PROXY: $env:HTTP_PROXY" "Gray" }
        if ($env:HTTPS_PROXY) { Write-ColorOutput "   HTTPS_PROXY: $env:HTTPS_PROXY" "Gray" }
    }
    
    # 检查 Node.js
    try {
        $nodeVersion = node --version 2>$null
        Write-ColorOutput "✅ Node.js: $nodeVersion" "Green"
    } catch {
        Write-ColorOutput "❌ Node.js 未安装或不在 PATH 中" "Red"
    }
    
    # 检查 Python
    try {
        $pythonVersion = python --version 2>$null
        Write-ColorOutput "✅ Python: $pythonVersion" "Green"
    } catch {
        Write-ColorOutput "❌ Python 未安装或不在 PATH 中" "Red"
    }
}

# 启动前端
function Start-Frontend {
    Write-ColorOutput "🚀 启动前端开发服务器..." "Green"
    if (Test-Path "frontend") {
        Set-Location frontend
        try {
            # 检查是否已安装依赖
            if (-not (Test-Path "node_modules")) {
                Write-ColorOutput "📦 检测到未安装依赖，正在安装..." "Yellow"
                npm install
            }
            npm run dev
        }
        catch {
            Write-ColorOutput "❌ 前端启动失败: $_" "Red"
            Write-ColorOutput "💡 请确保已安装依赖: cd frontend && npm install" "Cyan"
        }
        finally {
            Set-Location ..
        }
    } else {
        Write-ColorOutput "❌ 找不到 frontend 目录" "Red"
    }
}

# 启动后端
function Start-Backend {
    Write-ColorOutput "🚀 启动后端开发服务器..." "Green"
    if (Test-Path "backend") {
        Set-Location backend
        try {
            # 检查虚拟环境是否存在
            if (Test-Path ".venv\Scripts\Activate.ps1") {
                Write-ColorOutput "📦 激活虚拟环境..." "Yellow"
                & ".\.venv\Scripts\Activate.ps1"
                langgraph dev
            } elseif (Test-Path ".venv\bin\activate") {
                Write-ColorOutput "📦 激活虚拟环境 (Unix风格)..." "Yellow"
                # 对于 WSL 或其他类Unix环境
                bash -c "source .venv/bin/activate && langgraph dev"
            } else {
                Write-ColorOutput "⚠️  未找到虚拟环境，尝试直接运行..." "Yellow"
                Write-ColorOutput "💡 如果失败，请先运行: cd backend && pip install ." "Cyan"
                langgraph dev
            }
        }
        catch {
            Write-ColorOutput "❌ 后端启动失败: $_" "Red"
            Write-ColorOutput "💡 请确保已安装依赖: cd backend && pip install ." "Cyan"
        }
        finally {
            Set-Location ..
        }
    } else {
        Write-ColorOutput "❌ 找不到 backend 目录" "Red"
    }
}

# 同时启动前端和后端
function Start-Dev {
    Write-ColorOutput "🚀 启动完整开发环境..." "Cyan"
    Write-ColorOutput "📝 将在新窗口中启动前端和后端服务" "Yellow"
    
    $currentPath = $PWD.Path
    
    # 启动前端（新窗口）
    $frontendCmd = "cd '$currentPath\frontend'; if (-not (Test-Path 'node_modules')) { npm install }; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd
    
    # 启动后端（新窗口）
    $backendCmd = "cd '$currentPath\backend'; if (Test-Path '.\.venv\Scripts\Activate.ps1') { & '.\.venv\Scripts\Activate.ps1' }; langgraph dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd
    
    Write-ColorOutput "✅ 开发服务器已在新窗口中启动" "Green"
    Write-ColorOutput "📍 前端: http://localhost:5173/app" "Cyan"
    Write-ColorOutput "📍 后端: http://localhost:2024 (LangGraph Studio)" "Cyan"
    Write-ColorOutput "📍 后端API: http://127.0.0.1:2024" "Cyan"
    Write-ColorOutput "💡 使用 .\dev.ps1 stop 来停止所有服务" "Yellow"
}

# 停止所有相关进程
function Stop-DevServers {
    Write-ColorOutput "🛑 停止开发服务器..." "Yellow"
    
    $stopped = $false
    
    # 停止 node 进程（前端）
    try {
        $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
        if ($nodeProcesses) {
            $nodeProcesses | Stop-Process -Force
            Write-ColorOutput "✅ 已停止前端服务器 ($($nodeProcesses.Count) 个进程)" "Green"
            $stopped = $true
        }
    }
    catch {
        Write-ColorOutput "⚠️  停止前端服务器时出错: $_" "Yellow"
    }
    
    # 停止 python 进程（后端）
    try {
        $pythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue
        if ($pythonProcesses) {
            # 尝试找到包含 langgraph 的进程
            $langraphProcesses = $pythonProcesses | Where-Object { 
                try { 
                    $_.ProcessName -like "*python*" -and $_.MainWindowTitle -like "*langgraph*" 
                } catch { 
                    $false 
                }
            }
            
            if ($langraphProcesses) {
                $langraphProcesses | Stop-Process -Force
                Write-ColorOutput "✅ 已停止后端服务器 ($($langraphProcesses.Count) 个进程)" "Green"
                $stopped = $true
            } else {
                # 如果找不到特定的 langgraph 进程，列出所有 python 进程让用户选择
                Write-ColorOutput "⚠️  找到 $($pythonProcesses.Count) 个 Python 进程，但无法确定哪个是后端服务器" "Yellow"
                Write-ColorOutput "💡 你可能需要手动关闭后端窗口" "Cyan"
            }
        }
    }
    catch {
        Write-ColorOutput "⚠️  停止后端服务器时出错: $_" "Yellow"
    }
    
    if ($stopped) {
        Write-ColorOutput "🏁 开发服务器已停止" "Cyan"
    } else {
        Write-ColorOutput "ℹ️  没有找到正在运行的开发服务器" "Blue"
    }
}

# 主逻辑
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "frontend" { Start-Frontend }
    "backend" { Start-Backend }
    "dev" { Start-Dev }
    "stop" { Stop-DevServers }
    default { 
        Write-ColorOutput "❌ 未知命令: $Command" "Red"
        Show-Help 
    }
}