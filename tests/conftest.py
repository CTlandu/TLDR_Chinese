import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_module(relative_path, name=None):
    """按文件路径加载模块。

    api/__init__.py 会拉起 flask、flask_mongoengine、flaskext.markdown 一整套，
    而这几个纯逻辑模块只依赖 openai 和标准库。走文件路径加载可以让测试不必安装后端全家桶。
    """
    path = REPO_ROOT / relative_path
    module_name = name or path.stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class FakeDeepSeekClient:
    """替身 OpenAI client，记录调用并返回预设内容。"""

    def __init__(self, content=None, error=None, contents=None):
        self.calls = []
        self._contents = list(contents) if contents is not None else None
        self._content = content
        self._error = error
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self._create)
        )

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        if self._error is not None:
            raise self._error
        if self._contents is not None:
            content = self._contents.pop(0) if self._contents else ''
        else:
            content = self._content
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )
