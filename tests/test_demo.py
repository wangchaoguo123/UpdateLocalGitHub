import pytest

# ---------------------- 待测试的业务函数 ----------------------
def add(a, b):
    """简单的加法函数（待测试）"""
    return a + b

def read_file(file_path):
    """读取文件内容（待测试）"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# ---------------------- 基础测试用例 ----------------------
def test_add_basic():
    """基础断言测试"""
    # pytest直接使用Python原生assert，语法更自然
    assert add(1, 2) == 3
    assert add(0, 0) == 0
    assert add(-1, 1) == 0

# ---------------------- 使用全局Fixture ----------------------
def test_global_fixture(global_fixture):
    """使用conftest.py中的全局Fixture"""
    # 验证全局资源的正确性
    assert global_fixture["env"] == "test"
    assert global_fixture["version"] == "1.0.0"

def test_temp_file_fixture(temp_file):
    """使用临时文件Fixture"""
    # 读取临时文件内容并验证
    content = read_file(temp_file)
    assert content == "test content"

# ---------------------- 参数化测试（高频使用） ----------------------
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),       # 正常场景
    (3, 5, 8),       # 正常场景
    (-1, -2, -3),    # 负数场景
    (0, 99, 99),     # 含0场景
    (1.5, 2.5, 4.0)  # 浮点数场景
], ids=["positive", "another_positive", "negative", "zero", "float"])
def test_add_parametrize(a, b, expected):
    """参数化测试：一次运行多组数据"""
    assert add(a, b) == expected

# ---------------------- 标记测试（跳过/预期失败） ----------------------
@pytest.mark.skip(reason="该功能尚未实现，暂时跳过测试")
def test_unimplemented_feature():
    assert False

@pytest.mark.xfail(reason="已知浮点数精度问题，预期测试失败")
def test_float_precision():
    # 这个断言会失败，但pytest会标记为xfail（预期失败），不会影响测试结果
    assert add(0.1, 0.2) == 0.3