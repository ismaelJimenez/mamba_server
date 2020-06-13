import pytest
import os
from tempfile import NamedTemporaryFile

from mamba.core.compose_parser import compose_parser
from mamba.core.exceptions import ComposeFileException


class TestClass:
    project_name = 'test_compose_parser'

    mamba_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'mamba')

    def test_compose_parser(self):
        f = NamedTemporaryFile(delete=False)
        f.write(b"version: '0.1'\n")
        f.write(b"services:\n")
        f.write(b"  logger:\n")
        f.write(b"    component: logger\n")
        f.close()

        assert compose_parser(compose_file=f.name,
                              mamba_dir=self.mamba_dir) == 0

    def test_compose_parser_errors(self):
        f = NamedTemporaryFile(delete=False)
        f.close()

        assert compose_parser(compose_file=f.name,
                              mamba_dir=self.mamba_dir) == 1

        f = NamedTemporaryFile(delete=False)
        f.write(b"version: '0.1'\n")
        f.write(b"services:\n")
        f.close()

        assert compose_parser(compose_file=f.name,
                              mamba_dir=self.mamba_dir) == 1

        f = NamedTemporaryFile(delete=False)
        f.write(b"version: '0.1'\n")
        f.write(b"services:\n")
        f.write(b"  logger:\n")
        f.close()

        with pytest.raises(ComposeFileException) as excinfo:
            compose_parser(compose_file=f.name, mamba_dir=self.mamba_dir)

        assert 'logger: missing component property' in str(excinfo.value)

        f = NamedTemporaryFile(delete=False)
        f.write(b"version: '0.1'\n")
        f.write(b"services:\n")
        f.write(b"  logger:\n")
        f.write(b"    component: wrong\n")
        f.close()

        with pytest.raises(ComposeFileException) as excinfo:
            compose_parser(compose_file=f.name, mamba_dir=self.mamba_dir)

        assert "logger: component wrong' is not a valid component identifier" in str(
            excinfo.value)
