# rdict
A Pythonic tool is used for operating redis commands.

Usage
=====


```python
import rdict
r = rdict.RTypeRedis()
assert not ("a" in r)
r["a"] = "hello"
assert "a" in r
assert r["a"].as_value() == "hello"
r["b"] = [1, 2, 3]
assert "b" in r
r["c"] = {"test": 0, "test_a": "c", 1: 1.1}
assert "c" in r
assert r["c"].as_dict()["test"] == 0
assert r["c"].as_dict()[1] == 1.1
```
