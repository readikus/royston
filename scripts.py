import subprocess


def test():
    """
    Run all unittests
    """
    subprocess.call('pytest -vv ', shell=True)


def coverage():
    """
    Run coverage report
    """
    subprocess.call(
        "pytest --cov=royston --cov-report term-missing tests/", shell=True
    )


def test_focused():
    """
    Run coverage report
    """
    subprocess.call("pytest", shell=True)
