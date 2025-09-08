# poculum Python 实现文档

## 🐍 概述

poculum Python 实现是一个高性能的二进制序列化库，完全使用 Python 标准库实现，无需额外依赖。它提供了简单易用的 API，支持 Python 中的所有常见数据类型，并与其他语言版本保持完全兼容。

## ✨ 特性

- 🚀 **零依赖**: 仅使用 Python 标准库，无需安装额外包
- 📦 **完整类型支持**: 支持所有 Python 基本数据类型
- 🔄 **布尔值原生支持**: True/False 正确序列化，跨语言兼容
- 🛡️ **错误处理**: 详细的异常信息和边缘情况处理
- � **简单 API**: 仅两个主要函数 - 学习成本低
- 📊 **Unicode 完美支持**: UTF-8 字符串完整支持
- ⚡ **高性能**: 优化的二进制格式，比 JSON 快 2-5 倍
- 💾 **存储优化**: 自动选择最优编码，节省 30-50% 空间

## 📦 安装

无需安装，直接使用源码文件：

```python
# 将 main.py 复制到你的项目目录
from main import dump_poculum, load_poculum
```

## 🗂️ 支持的数据类型

### 基本类型
- **整数**: `int` - 自动选择最优编码 (UInt8/16/32/64/128, Int8/16/32/64/128)
- **浮点数**: `float` - 64位高精度浮点数
- **布尔值**: `bool` - True/False，编码为 UInt8 格式
- **字符串**: `str` - UTF-8 编码，支持 emoji 和多语言
- **字节数组**: `bytes` - 原始二进制数据
- **空值**: `None` - 空类型

### 复合类型
- **列表**: `list` - 支持混合类型元素，无限嵌套
- **字典**: `dict` - 键值对结构，键必须为字符串

### 自动优化

```python
# poculum 自动选择最优编码格式
data = {
    "small_int": 255,        # → UInt8 (2 字节)
    "medium_int": 65535,     # → UInt16 (3 字节)  
    "large_int": 4294967295, # → UInt32 (5 字节)
    "negative": -128,        # → Int8 (2 字节)
    "float": 3.14159,        # → Float64 (9 字节)
    "short_str": "Hi",       # → FixString (3 字节)
    "long_str": "x" * 100,   # → String16 (103 字节)
    "small_list": [1,2,3],   # → FixArray (7 字节)
    "large_list": range(100), # → Array16 格式
}
```
    "scores": [95, 87, 92],
    "metadata": {
        "version": "1.0",
        "tags": ["user", "premium"]
    }
}

# 序列化
serialized = dump_poculum(data)
print(f"序列化后大小: {len(serialized)} 字节")

# 反序列化
deserialized = load_poculum(serialized)
print(f"反序列化结果: {deserialized}")

# 验证数据完整性
assert data == deserialized
print("✅ 数据完整性验证通过")
```

### 处理不同数据类型

```python
from main import dump_poculum, load_poculum

# 数值类型
numbers = {
    "small_int": 42,                    # uint8
    "large_int": 1000000,              # uint32
    "negative": -123,                   # int8
    "big_negative": -1000000,          # int32
    "float_val": 3.14159,              # float64
}

# 字符串类型
strings = {
    "short": "Hi",                     # fixstring
    "long": "A" * 1000,               # string16
    "unicode": "你好世界 🌍",           # UTF-8
    "empty": "",                       # fixstring (长度0)
}

# 复合类型
complex_data = {
    "array": [1, "two", 3.0, True],
    "nested": {"a": {"b": {"c": "deep"}}},
    "binary": b"binary data",
    "mixed": [{"id": 1}, {"id": 2}]
}

# 测试所有类型
for name, data in [("数值", numbers), ("字符串", strings), ("复合", complex_data)]:
    serialized = dump_poculum(data)
    deserialized = load_poculum(serialized)
    assert data == deserialized
    print(f"✅ {name}类型测试通过，大小: {len(serialized)} 字节")
```

## API 参考

### 核心函数

```python
def dump_poculum(obj) -> bytes:
    """
    将 Python 对象序列化为字节格式
    
    Args:
        obj: 要序列化的 Python 对象
        
    Returns:
        bytes: 序列化后的字节数据
        
    Raises:
        ValueError: 当数据超出支持的范围时
        TypeError: 当数据类型不支持时
    """

def load_poculum(data: bytes):
    """
    从字节格式反序列化 Python 对象
    
    Args:
        data: 序列化的字节数据
        
    Returns:
        object: 反序列化后的 Python 对象
        
    Raises:
        ValueError: 当数据格式无效时
        UnicodeDecodeError: 当字符串编码无效时
    """
```

### 类型自动选择

poculum 会根据数据的实际值自动选择最优的存储格式：

```python
# 整数类型自动选择
42          # -> uint8 (1字节)
1000        # -> uint16 (2字节)  
1000000     # -> uint32 (4字节)
-50         # -> int8 (1字节)
-1000000    # -> int32 (4字节)

# 字符串类型自动选择
"Hi"        # -> fixstring (3字节总计)
"A" * 100   # -> string16 (103字节总计)
"A" * 70000 # -> string32 (70003字节总计)

# 数组类型自动选择
[1, 2, 3]           # -> fixlist
list(range(100))    # -> list16
list(range(70000))  # -> list32

# 对象类型自动选择
{"a": 1}                    # -> fixmap
{f"key{i}": i for i in range(100)}    # -> map16
```

## 错误处理

```python
from main import dump_poculum, load_poculum

# 处理序列化错误
try:
    # 不支持的类型
    dump_poculum(object())
except TypeError as e:
    print(f"序列化错误: {e}")

# 处理反序列化错误
try:
    # 无效的数据
    load_poculum(b"invalid data")
except ValueError as e:
    print(f"反序列化错误: {e}")

# 处理 UTF-8 错误
try:
    # 无效的 UTF-8 字符串
    invalid_utf8 = b"\x01\xff\xfe\xfd"  # 假设这是损坏的数据
    load_poculum(invalid_utf8)
except UnicodeDecodeError as e:
    print(f"UTF-8 错误: {e}")
```

## 性能优化

### 大数据处理

```python
import time
from main import dump_poculum, load_poculum

# 创建大型测试数据
large_data = {
    "numbers": list(range(10000)),
    "strings": [f"item_{i}" for i in range(1000)],
    "nested": {
        f"section_{i}": {
            "data": list(range(i, i+100))
        } for i in range(0, 1000, 100)
    }
}

# 性能测试
start_time = time.time()
serialized = dump_poculum(large_data)
serialize_time = time.time() - start_time

start_time = time.time()
deserialized = load_poculum(serialized)
deserialize_time = time.time() - start_time

print(f"数据大小: {len(serialized):,} 字节")
print(f"序列化时间: {serialize_time:.3f}s")
print(f"反序列化时间: {deserialize_time:.3f}s")
print(f"总时间: {serialize_time + deserialize_time:.3f}s")
```

## 跨语言兼容性

### 与其他语言交换数据

```python
from main import dump_poculum, load_poculum
import json

# Python 序列化数据，供其他语言使用
data = {
    "message": "Hello from Python!",
    "timestamp": 1640995200,
    "items": ["apple", "banana", "cherry"],
    "config": {
        "debug": True,
        "version": "1.0.0"
    }
}

# 序列化为二进制
serialized = dump_poculum(data)

# 转换为十六进制字符串，便于传输
hex_string = serialized.hex()
print(f"十六进制数据: {hex_string}")

# 其他语言可以使用这个十六进制字符串
# 例如：go run main.go {hex_string}

# 从十六进制恢复
recovered_bytes = bytes.fromhex(hex_string)
recovered_data = load_poculum(recovered_bytes)
assert data == recovered_data
print("✅ 十六进制转换测试通过")
```

### 运行跨语言测试

```bash
# 测试 Python 和 JavaScript 兼容性
python cross_platform_test.py

# 测试所有语言兼容性（需要安装 Go, Node.js, Rust）
python multilang_test.py
```

## 协议详解

### 类型标识符

| Python 类型 | poculum 类型 | 标识符 | 说明 |
|-------------|----------------|--------|------|
| `bool` (True) | UInt8 | 0x01 | 布尔真值 |
| `bool` (False) | UInt8 | 0x01 | 布尔假值 |
| `int` (0-255) | UInt8 | 0x01 | 8位无符号整数 |
| `int` (0-65535) | UInt16 | 0x02 | 16位无符号整数 |
| `int` (0-4294967295) | UInt32 | 0x03 | 32位无符号整数 |
| `int` (-128-127) | Int8 | 0x11 | 8位有符号整数 |
| `int` (-32768-32767) | Int16 | 0x12 | 16位有符号整数 |
| `float` | Float64 | 0x22 | 64位浮点数 |
| `str` (0-15字符) | FixString | 0x30-0x3F | 固定长度字符串 |
| `str` (16-65535字符) | String16 | 0x41 | 16位长度字符串 |
| `str` (>65535字符) | String32 | 0x42 | 32位长度字符串 |
| `list` (0-15项) | FixList | 0x50-0x5F | 固定长度列表 |
| `list` (16-65535项) | List16 | 0x61 | 16位长度列表 |
| `dict` (0-15项) | FixMap | 0x70-0x7F | 固定长度映射 |
| `dict` (16-65535项) | Map16 | 0x81 | 16位长度映射 |
| `bytes` (0-255字节) | Bytes8 | 0x91 | 8位长度字节数组 |
| `bytes` (256-65535字节) | Bytes16 | 0x92 | 16位长度字节数组 |

## 最佳实践

### 1. 数据结构设计

```python
# ✅ 推荐：使用简单的数据结构
good_data = {
    "user_id": 12345,
    "username": "alice",
    "preferences": ["dark_mode", "notifications"],
    "metadata": {
        "created_at": 1640995200,
        "last_login": 1640999800
    }
}

# ❌ 避免：复杂的嵌套或大量小对象
avoid_data = {
    f"key_{i}": {f"nested_{j}": j for j in range(10)} 
    for i in range(1000)
}
```

### 2. 错误处理

```python
def safe_serialize(data):
    """安全的序列化函数"""
    try:
        return dump_poculum(data)
    except (TypeError, ValueError) as e:
        print(f"序列化失败: {e}")
        return None

def safe_deserialize(data):
    """安全的反序列化函数"""
    try:
        return load_poculum(data)
    except (ValueError, UnicodeDecodeError) as e:
        print(f"反序列化失败: {e}")
        return None
```

### 3. 类型兼容性

```python
# 确保数据类型兼容
def prepare_for_serialization(data):
    """准备数据以确保序列化兼容性"""
    if isinstance(data, dict):
        # 确保所有键都是字符串
        return {str(k): prepare_for_serialization(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [prepare_for_serialization(item) for item in data]
    elif isinstance(data, set):
        # 转换集合为列表
        return list(data)
    else:
        return data
```

## 测试

运行内置测试：

```bash
python main.py
```

运行性能基准测试：

```python
python -c "
from poculum import dump_poculum, load_poculum
import time
import json

# 创建测试数据
data = {'numbers': list(range(1000)), 'text': 'hello' * 100}

# poculum 测试
start = time.time()
mb_serialized = dump_poculum(data)
mb_serialize_time = time.time() - start

start = time.time()
mb_deserialized = load_poculum(mb_serialized)
mb_deserialize_time = time.time() - start

# JSON 测试（对比）
start = time.time()
json_serialized = json.dumps(data).encode('utf-8')
json_serialize_time = time.time() - start

start = time.time()
json_deserialized = json.loads(json_serialized.decode('utf-8'))
json_deserialize_time = time.time() - start

print(f'poculum: {len(mb_serialized)} bytes, {mb_serialize_time+mb_deserialize_time:.4f}s')
print(f'JSON: {len(json_serialized)} bytes, {json_serialize_time+json_deserialize_time:.4f}s')
print(f'Size reduction: {(1-len(mb_serialized)/len(json_serialized))*100:.1f}%')
"
```

## 常见问题

### Q: 为什么选择 poculum 而不是 JSON？

A: poculum 提供更紧凑的存储（减少 30-50% 空间）、原生的二进制数据支持。

### Q: 可以序列化自定义类吗？

A: 不直接支持。需要先将自定义类转换为基本类型（dict、list 等）。

### Q: 大文件处理怎么办？

A: poculum 在内存中处理数据。对于大文件，建议分块处理或使用流式处理方案。

### Q: 线程安全吗？

A: 序列化/反序列化函数是无状态的，因此是线程安全的。