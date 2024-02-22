import pytest
from unittest.mock import patch
from your_dag_file import run_strategy

def test_run_strategy_success():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        try:
            run_strategy("ETF.py")
            assert True
        except:
            assert False

def test_run_strategy_failure():
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, ['python', '/path/to/script'])
        with pytest.raises(Exception) as excinfo:
            run_strategy("ETF.py")
        assert "Script failed" in str(excinfo.value)


if name == "main":
    pytest.main()