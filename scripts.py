import subprocess

def test():
    """
    Run all unittests
    """
    subprocess.call('pytest --cov=royston tests/', shell=True)

def coverage():
    """
    Run coverage report
    """
    subprocess.call('coverage report -m  royston/royston.py', shell=True)

