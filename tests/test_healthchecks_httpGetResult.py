from pi_monitor import HttpGetResult


def test_construct_result():
    result = HttpGetResult(True, "message")
    assert result.success
    assert result.message == "message"


def test_construct_result_false():
    result = HttpGetResult(False, "message")
    assert result.success is False
    assert result.message == "message"


def test_construct_result_default():
    result = HttpGetResult(True)
    assert result.success
    assert result.message == ""
