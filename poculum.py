import struct


def dump_poculum(obj):
    """
    将 Python 对象序列化为字节格式

    支持的数据类型：
    - int: 根据值的范围自动选择 uint8/16/32/64/128 或 int8/16/32/64/128
    - float: 使用 float64 编码
    - str: 根据长度自动选择 fixstring/string16/string32
    - bool: 使用 uint8 编码（True=1, False=0）
    - list: 根据长度自动选择 fixlist/list16/list32
    - dict: 根据长度自动选择 fixmap/map16/map32
    - bytes: 根据长度自动选择 bytes8/bytes16/bytes32

    Args:
        obj: 要序列化的 Python 对象

    Returns:
        bytes: 序列化后的字节数据

    Raises:
        ValueError: 当数据超出支持的范围时
        TypeError: 当数据类型不支持时
    """
    if obj is None:
        return b""

    # 处理布尔类型（必须在 int 之前检查，因为 bool 是 int 的子类）
    elif isinstance(obj, bool):
        if obj:
            return b"\x01\x01"  # True -> uint8(1)
        else:
            return b"\x01\x00"  # False -> uint8(0)

    # 处理整数类型
    if isinstance(obj, int):
        if obj >= 0:  # 无符号整数
            if obj <= 255:  # uint8
                return b"\x01" + obj.to_bytes(1, "big")
            elif obj <= 65535:  # uint16
                return b"\x02" + obj.to_bytes(2, "big")
            elif obj <= 4294967295:  # uint32
                return b"\x03" + obj.to_bytes(4, "big")
            elif obj <= 18446744073709551615:  # uint64
                return b"\x04" + obj.to_bytes(8, "big")
            elif obj <= 340282366920938463463374607431768211455:  # uint128
                return b"\x05" + obj.to_bytes(16, "big")
            else:
                raise ValueError("Integer too large for uint128")
        else:  # 有符号整数
            if -128 <= obj <= 127:  # int8
                return b"\x11" + obj.to_bytes(1, "big", signed=True)
            elif -32768 <= obj <= 32767:  # int16
                return b"\x12" + obj.to_bytes(2, "big", signed=True)
            elif -2147483648 <= obj <= 2147483647:  # int32
                return b"\x13" + obj.to_bytes(4, "big", signed=True)
            elif -9223372036854775808 <= obj <= 9223372036854775807:  # int64
                return b"\x14" + obj.to_bytes(8, "big", signed=True)
            elif (
                -170141183460469231731687303715884105728
                <= obj
                <= 170141183460469231731687303715884105727
            ):  # int128
                return b"\x15" + obj.to_bytes(16, "big", signed=True)
            else:
                raise ValueError("Integer too large for int128")

    # 处理浮点数类型
    elif isinstance(obj, float):
        # 直接使用 float64 确保精度
        return b"\x22" + struct.pack(">d", obj)

    # 处理字符串类型
    elif isinstance(obj, str):
        utf8_bytes = obj.encode("utf-8")
        length = len(utf8_bytes)

        if length <= 15:  # fixstring
            return bytes([0x30 + length]) + utf8_bytes
        elif length <= 65535:  # string16
            return b"\x41" + length.to_bytes(2, "big") + utf8_bytes
        elif length <= 4294967295:  # string32
            return b"\x42" + length.to_bytes(4, "big") + utf8_bytes
        else:
            raise ValueError("String too long")

    # 处理列表类型
    elif isinstance(obj, list):
        length = len(obj)

        # 防止过深的递归和过大的数据结构
        if length > 1000000:  # 限制列表大小
            raise ValueError(f"List too long: {length} items (max 1000000)")

        if length <= 15:  # fixlist
            result = bytes([0x50 + length])
            for item in obj:
                try:
                    result += dump_poculum(item)
                except RecursionError:
                    raise ValueError(
                        "Maximum recursion depth exceeded while serializing nested structure"
                    )
            return result
        elif length <= 65535:  # list16
            result = b"\x61" + length.to_bytes(2, "big")
            for item in obj:
                try:
                    result += dump_poculum(item)
                except RecursionError:
                    raise ValueError(
                        "Maximum recursion depth exceeded while serializing nested structure"
                    )
            return result
        elif length <= 4294967295:  # list32
            result = b"\x62" + length.to_bytes(4, "big")
            for item in obj:
                try:
                    result += dump_poculum(item)
                except RecursionError:
                    raise ValueError(
                        "Maximum recursion depth exceeded while serializing nested structure"
                    )
            return result
        else:
            raise ValueError("List too long")

    # 处理字典类型
    elif isinstance(obj, dict):
        length = len(obj)

        # 防止过大的数据结构
        if length > 1000000:  # 限制字典大小
            raise ValueError(f"Map too long: {length} items (max 1000000)")

        if length <= 15:  # fixmap
            result = bytes([0x70 + length])
            for key, value in obj.items():
                try:
                    result += dump_poculum(key)
                    result += dump_poculum(value)
                except RecursionError:
                    raise ValueError(
                        "Maximum recursion depth exceeded while serializing nested structure"
                    )
            return result
        elif length <= 65535:  # map16
            result = b"\x81" + length.to_bytes(2, "big")
            for key, value in obj.items():
                try:
                    result += dump_poculum(key)
                    result += dump_poculum(value)
                except RecursionError:
                    raise ValueError(
                        "Maximum recursion depth exceeded while serializing nested structure"
                    )
            return result
        elif length <= 4294967295:  # map32
            result = b"\x82" + length.to_bytes(4, "big")
            for key, value in obj.items():
                try:
                    result += dump_poculum(key)
                    result += dump_poculum(value)
                except RecursionError:
                    raise ValueError(
                        "Maximum recursion depth exceeded while serializing nested structure"
                    )
            return result
        else:
            raise ValueError("Map too long")

    # 处理字节类型
    elif isinstance(obj, bytes):
        length = len(obj)

        if length <= 255:  # bytes8
            return b"\x91" + bytes([length]) + obj
        elif length <= 65535:  # bytes16
            return b"\x92" + length.to_bytes(2, "big") + obj
        elif length <= 4294967295:  # bytes32
            return b"\x93" + length.to_bytes(4, "big") + obj
        else:
            raise ValueError("Bytes too long")

    else:
        raise TypeError(f"Unsupported type: {type(obj)}")


def load_poculum(box: bytes):
    """
    将字节格式反序列化为 Python 对象

    支持解析的格式：
    - 整数类型: uint8/16/32/64/128, int8/16/32/64/128
    - 浮点类型: float32/64
    - 字符串类型: fixstring/string16/string32
    - 列表类型: fixlist/list16/list32
    - 字典类型: fixmap/map16/map32
    - 字节类型: bytes8/bytes16/bytes32

    Args:
        box: 要反序列化的字节数据

    Returns:
        反序列化后的 Python 对象

    Raises:
        ValueError: 当输入不是 bytes 类型时
        IndexError: 当数据长度不足时
        UnicodeDecodeError: 当字符串编码无效时
    """
    if not box:
        return None
    if not isinstance(box, bytes):
        raise ValueError("Input must be of type bytes")

    if len(box) < 1:
        raise IndexError("Insufficient data: need at least 1 byte for type indicator")

    type_byte = box[0]

    # uint8:0~255
    if type_byte == 0x01:
        if len(box) < 2:
            raise IndexError("Insufficient data for uint8: need 2 bytes")
        return int.from_bytes(box[1:2], "big")

    # uint16:0~65535
    if type_byte == 0x02:
        if len(box) < 3:
            raise IndexError("Insufficient data for uint16: need 3 bytes")
        return int.from_bytes(box[1:3], "big")

    # uint32:0~4294967295
    if type_byte == 0x03:
        if len(box) < 5:
            raise IndexError("Insufficient data for uint32: need 5 bytes")
        return int.from_bytes(box[1:5], "big")

    # uint64:0~18446744073709551615
    if type_byte == 0x04:
        if len(box) < 9:
            raise IndexError("Insufficient data for uint64: need 9 bytes")
        return int.from_bytes(box[1:9], "big")

    # uint128:0~340282366920938463463374607431768211455
    if type_byte == 0x05:
        if len(box) < 17:
            raise IndexError("Insufficient data for uint128: need 17 bytes")
        return int.from_bytes(box[1:17], "big")

    # int8: -128~127
    if type_byte == 0x11:
        if len(box) < 2:
            raise IndexError("Insufficient data for int8: need 2 bytes")
        return int.from_bytes(box[1:2], "big", signed=True)

    # int16: -32768~32767
    if type_byte == 0x12:
        if len(box) < 3:
            raise IndexError("Insufficient data for int16: need 3 bytes")
        return int.from_bytes(box[1:3], "big", signed=True)

    # int32: -2147483648~2147483647
    if type_byte == 0x13:
        if len(box) < 5:
            raise IndexError("Insufficient data for int32: need 5 bytes")
        return int.from_bytes(box[1:5], "big", signed=True)

    # int64: -9223372036854775808~9223372036854775807
    if type_byte == 0x14:
        if len(box) < 9:
            raise IndexError("Insufficient data for int64: need 9 bytes")
        return int.from_bytes(box[1:9], "big", signed=True)

    # int128: -170141183460469231731687303715884105728~170141183460469231731687303715884105727
    if type_byte == 0x15:
        if len(box) < 17:
            raise IndexError("Insufficient data for int128: need 17 bytes")
        return int.from_bytes(box[1:17], "big", signed=True)

    # float32: -3.402823466e+38~3.402823466e+38
    if type_byte == 0x21:
        if len(box) < 5:
            raise IndexError("Insufficient data for float32: need 5 bytes")
        return struct.unpack(">f", box[1:5])[0]

    # float64: -1.7976931348623157e+308~1.7976931348623157e+308
    if type_byte == 0x22:
        if len(box) < 9:
            raise IndexError("Insufficient data for float64: need 9 bytes")
        return struct.unpack(">d", box[1:9])[0]

    # fixstring：第一个字节的低位表示字符串的字节个数
    if 0x30 <= type_byte <= 0x3F:
        length = type_byte - 0x30
        if len(box) < 1 + length:
            raise IndexError(
                f"Insufficient data for fixstring: need {1 + length} bytes, got {len(box)}"
            )
        try:
            return box[1 : 1 + length].decode("utf-8")
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                e.encoding,
                e.object,
                e.start,
                e.end,
                f"Invalid UTF-8 in fixstring: {e.reason}",
            )

    # string16: 1~65535 bytes
    if type_byte == 0x41:
        if len(box) < 3:
            raise IndexError("Insufficient data for string16 length: need 3 bytes")
        length = int.from_bytes(box[1:3], "big")
        if len(box) < 3 + length:
            raise IndexError(
                f"Insufficient data for string16: need {3 + length} bytes, got {len(box)}"
            )
        try:
            return box[3 : 3 + length].decode("utf-8")
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                e.encoding,
                e.object,
                e.start,
                e.end,
                f"Invalid UTF-8 in string16: {e.reason}",
            )

    # String32: 1~4294967295 bytes
    if type_byte == 0x42:
        if len(box) < 5:
            raise IndexError("Insufficient data for string32 length: need 5 bytes")
        length = int.from_bytes(box[1:5], "big")
        # 防止过大的长度声明导致内存耗尽
        if length > len(box) - 5:
            raise ValueError(
                f"Invalid string32 length: declared {length}, available {len(box) - 5}"
            )
        if length > 100 * 1024 * 1024:  # 限制为100MB
            raise ValueError(f"String32 length too large: {length} bytes (max 100MB)")
        try:
            return box[5 : 5 + length].decode("utf-8")
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                e.encoding,
                e.object,
                e.start,
                e.end,
                f"Invalid UTF-8 in string32: {e.reason}",
            )

    # fixlist: 0~15 items，高位表示列表长度
    if 0x50 <= type_byte <= 0x5F:
        length = type_byte - 0x50
        if length > 1000:  # 防止过大的列表导致性能问题
            raise ValueError(f"Fixlist length too large: {length} items (max 1000)")
        result = []
        offset = 1
        for i in range(length):
            if offset >= len(box):
                raise IndexError(
                    f"Insufficient data for fixlist item {i}: reached end of data"
                )
            item_box = box[offset:]
            try:
                item = load_poculum(item_box)
                result.append(item)
                # 计算已消耗的字节数并更新偏移量
                item_bytes = dump_poculum(item)
                offset += len(item_bytes)
            except RecursionError:
                raise ValueError(
                    "Maximum recursion depth exceeded while parsing nested structure"
                )
        return result

    # list16: 1~65535 items
    if type_byte == 0x61:
        if len(box) < 3:
            raise IndexError("Insufficient data for list16 length: need 3 bytes")
        length = int.from_bytes(box[1:3], "big")
        if length > 10000:  # 防止过大的列表
            raise ValueError(f"List16 length too large: {length} items (max 10000)")
        result = []
        offset = 3
        for i in range(length):
            if offset >= len(box):
                raise IndexError(
                    f"Insufficient data for list16 item {i}: reached end of data"
                )
            item_box = box[offset:]
            try:
                item = load_poculum(item_box)
                result.append(item)
                item_bytes = dump_poculum(item)
                offset += len(item_bytes)
            except RecursionError:
                raise ValueError(
                    "Maximum recursion depth exceeded while parsing nested structure"
                )
        return result

    # list32: 1~4294967295 items
    if type_byte == 0x62:
        if len(box) < 5:
            raise IndexError("Insufficient data for list32 length: need 5 bytes")
        length = int.from_bytes(box[1:5], "big")
        if length > 100000:  # 防止过大的列表
            raise ValueError(f"List32 length too large: {length} items (max 100000)")
        result = []
        offset = 5
        for i in range(length):
            if offset >= len(box):
                raise IndexError(
                    f"Insufficient data for list32 item {i}: reached end of data"
                )
            item_box = box[offset:]
            try:
                item = load_poculum(item_box)
                result.append(item)
                item_bytes = dump_poculum(item)
                offset += len(item_bytes)
            except RecursionError:
                raise ValueError(
                    "Maximum recursion depth exceeded while parsing nested structure"
                )
        return result

    # fixmap: 0~15 items，高位表示映射长度
    if 0x70 <= type_byte <= 0x7F:
        length = type_byte - 0x70
        if length > 1000:  # 防止过大的字典
            raise ValueError(f"Fixmap length too large: {length} items (max 1000)")
        result = {}
        offset = 1
        for i in range(length):
            if offset >= len(box):
                raise IndexError(
                    f"Insufficient data for fixmap key {i}: reached end of data"
                )

            # 解析键
            key_box = box[offset:]
            try:
                key = load_poculum(key_box)
                key_bytes = dump_poculum(key)
                offset += len(key_bytes)
            except RecursionError:
                raise ValueError(
                    "Maximum recursion depth exceeded while parsing nested structure"
                )

            if offset >= len(box):
                raise IndexError(
                    f"Insufficient data for fixmap value {i}: reached end of data"
                )

            # 解析值
            value_box = box[offset:]
            try:
                value = load_poculum(value_box)
                value_bytes = dump_poculum(value)
                offset += len(value_bytes)
            except RecursionError:
                raise ValueError(
                    "Maximum recursion depth exceeded while parsing nested structure"
                )

            result[key] = value
        return result

    # map16: 1~65535 items
    if type_byte == 0x81:
        if len(box) < 3:
            raise IndexError("Insufficient data for map16 length: need 3 bytes")
        length = int.from_bytes(box[1:3], "big")
        if length > 10000:  # 防止过大的字典
            raise ValueError(f"Map16 length too large: {length} items (max 10000)")
        result = {}
        offset = 3
        for i in range(length):
            if offset >= len(box):
                raise IndexError(
                    f"Insufficient data for map16 key {i}: reached end of data"
                )

            # 解析键
            key_box = box[offset:]
            try:
                key = load_poculum(key_box)
                key_bytes = dump_poculum(key)
                offset += len(key_bytes)
            except RecursionError:
                raise ValueError(
                    "Maximum recursion depth exceeded while parsing nested structure"
                )

            if offset >= len(box):
                raise IndexError(
                    f"Insufficient data for map16 value {i}: reached end of data"
                )

            # 解析值
            value_box = box[offset:]
            try:
                value = load_poculum(value_box)
                value_bytes = dump_poculum(value)
                offset += len(value_bytes)
            except RecursionError:
                raise ValueError(
                    "Maximum recursion depth exceeded while parsing nested structure"
                )

            result[key] = value
        return result

    # map32: 1~4294967295 items
    if type_byte == 0x82:
        if len(box) < 5:
            raise IndexError("Insufficient data for map32 length: need 5 bytes")
        length = int.from_bytes(box[1:5], "big")
        if length > 100000:  # 防止过大的字典
            raise ValueError(f"Map32 length too large: {length} items (max 100000)")
        result = {}
        offset = 5
        for i in range(length):
            if offset >= len(box):
                raise IndexError(
                    f"Insufficient data for map32 key {i}: reached end of data"
                )

            # 解析键
            key_box = box[offset:]
            try:
                key = load_poculum(key_box)
                key_bytes = dump_poculum(key)
                offset += len(key_bytes)
            except RecursionError:
                raise ValueError(
                    "Maximum recursion depth exceeded while parsing nested structure"
                )

            if offset >= len(box):
                raise IndexError(
                    f"Insufficient data for map32 value {i}: reached end of data"
                )

            # 解析值
            value_box = box[offset:]
            try:
                value = load_poculum(value_box)
                value_bytes = dump_poculum(value)
                offset += len(value_bytes)
            except RecursionError:
                raise ValueError(
                    "Maximum recursion depth exceeded while parsing nested structure"
                )

            result[key] = value
        return result

    # bytes8: 1~255 bytes
    if type_byte == 0x91:
        if len(box) < 2:
            raise IndexError("Insufficient data for bytes8 length: need 2 bytes")
        length = box[1]
        if len(box) < 2 + length:
            raise IndexError(
                f"Insufficient data for bytes8: need {2 + length} bytes, got {len(box)}"
            )
        return box[2 : 2 + length]

    # bytes16: 1~65535 bytes
    if type_byte == 0x92:
        if len(box) < 3:
            raise IndexError("Insufficient data for bytes16 length: need 3 bytes")
        length = int.from_bytes(box[1:3], "big")
        if len(box) < 3 + length:
            raise IndexError(
                f"Insufficient data for bytes16: need {3 + length} bytes, got {len(box)}"
            )
        return box[3 : 3 + length]

    # bytes32: 1~4294967295 bytes
    if type_byte == 0x93:
        if len(box) < 5:
            raise IndexError("Insufficient data for bytes32 length: need 5 bytes")
        length = int.from_bytes(box[1:5], "big")
        # 防止过大的长度声明导致内存耗尽
        if length > len(box) - 5:
            raise ValueError(
                f"Invalid bytes32 length: declared {length}, available {len(box) - 5}"
            )
        if length > 100 * 1024 * 1024:  # 限制为100MB
            raise ValueError(f"Bytes32 length too large: {length} bytes (max 100MB)")
        return box[5 : 5 + length]

    # 未知类型标识符
    raise ValueError(f"Unknown type identifier: 0x{type_byte:02x}")


# 测试函数
def test_poculum():
    """测试 dump_poculum 和 load_poculum 的互逆性"""
    test_cases = [
        # 整数测试
        42,  # uint8
        1000,  # uint16
        100000,  # uint32
        -50,  # int8
        -1000,  # int16
        -100000,  # int32
        # 浮点数测试
        3.14,  # float32/64
        1.23456789,  # float64
        # 字符串测试
        "hello",  # fixstring
        "a" * 20,  # string16
        # 列表测试
        [1, 2, 3],  # fixlist
        [1, "hello", 3.14],  # 混合类型列表
        # 字典测试
        {"key": "value"},  # fixmap
        {"a": 1, "b": 2, "c": 3},  # fixmap
        # 字节测试
        b"binary data",  # bytes8
    ]

    for i, original in enumerate(test_cases):
        try:
            # 序列化
            serialized = dump_poculum(original)
            print(f"Test {i+1}: {original} -> {serialized.hex()}")

            # 反序列化
            deserialized = load_poculum(serialized)
            print(f"  Deserialized: {deserialized}")

            # 验证
            if original == deserialized:
                print(f"  ✓ PASS")
            else:
                print(f"  ✗ FAIL: {original} != {deserialized}")
            print()

        except Exception as e:
            print(f"Test {i+1} FAILED: {e}")
            print()

def test_size_reduction():
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

if __name__ == "__main__":
    test_poculum()
    print("---test size reduction--")
    test_size_reduction()
    