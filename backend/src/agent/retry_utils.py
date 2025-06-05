"""
提供重试机制的实用工具函数，特别是用于处理API配额限制问题。
"""

import time
import random
from functools import wraps
from google.genai.errors import ClientError

# 指数退避重试配置
MAX_RETRIES = 5  # 最大重试次数
BASE_DELAY = 1  # 基础延迟时间（秒）
MAX_DELAY = 30  # 最大延迟时间（秒）


def retry_with_exponential_backoff(func):
    """
    实现指数退避重试的装饰器，专门用于处理Google Generative AI API的配额限制。
    
    Args:
        func: 需要装饰的函数
        
    Returns:
        装饰后的函数，在遇到配额限制时自动重试
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except ClientError as e:
                # 检查是否是配额限制错误
                if e.status_code == 429:
                    retries += 1
                    if retries >= MAX_RETRIES:
                        raise  # 达到最大重试次数，抛出异常
                    
                    # 计算延迟时间，使用指数退避策略
                    delay = min(BASE_DELAY * (2 ** (retries - 1)) + random.uniform(0, 1), MAX_DELAY)
                    print(f"API配额限制，等待{delay:.2f}秒后重试 ({retries}/{MAX_RETRIES})")
                    time.sleep(delay)
                else:
                    # 其他类型的错误直接抛出
                    raise
            except Exception as e:
                # 处理其他类型的异常
                raise
    
    return wrapper


# 异步版本的重试装饰器
async def async_retry_with_exponential_backoff(func):
    """
    实现异步指数退避重试的装饰器，专门用于处理Google Generative AI API的配额限制。
    
    Args:
        func: 需要装饰的异步函数
        
    Returns:
        装饰后的异步函数，在遇到配额限制时自动重试
    """
    import asyncio
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                return await func(*args, **kwargs)
            except ClientError as e:
                # 检查是否是配额限制错误
                if e.status_code == 429:
                    retries += 1
                    if retries >= MAX_RETRIES:
                        raise  # 达到最大重试次数，抛出异常
                    
                    # 计算延迟时间，使用指数退避策略
                    delay = min(BASE_DELAY * (2 ** (retries - 1)) + random.uniform(0, 1), MAX_DELAY)
                    print(f"API配额限制，等待{delay:.2f}秒后重试 ({retries}/{MAX_RETRIES})")
                    await asyncio.sleep(delay)
                else:
                    # 其他类型的错误直接抛出
                    raise
            except Exception as e:
                # 处理其他类型的异常
                raise
    
    return wrapper
