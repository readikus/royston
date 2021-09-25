import subprocess

def test():
    """
    Run all unittests
    """
    subprocess.call('coverage run -m unittest discover -p "*_test.py"', shell=True)

def coverage():
    """
    Run coverage report
    """
    subprocess.call('coverage report -m  royston/royston.py', shell=True)

