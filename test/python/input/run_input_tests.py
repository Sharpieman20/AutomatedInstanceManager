from pathlib import Path
import shutil
from inspect import getmembers, isfunction
from .input_test_utils import InputEvent

def parse_line(line):
    line = line.rstrip()
    keytype = KeyType[line[1]]
    timemillis = int(line[0])

    return (keytype, timemillis)

def get_fil_results(fil):
    results = []
    for ln in fil.getlines():
        results.append(parse_line(ln))
    return results

def setup():
    from ..build_test_env import init_test_env
    init_test_env()
    aimlogdir = Path.home() / '.aimlog'
    if aimlogdir.exists():
        shutil.rmtree(aimlogdir)
    aimlogdir.mkdir()

    # run test

def do_results_match(actual, expected):
    if actual is None:
        if expected is None:
            return True
        return False
    if expected is None:
        return False
    if len(actual) != len(expected):
        return False
    ind = 0
    for i in range(len(actual)):
        actual_item = actual[i]
        expected_item = expected[i]

        if actual_item.inst != expected_item.inst:
            return False
        if actual_item.key != expected_item.key:
            return False
    return True
    

def getresults():
    full_results = []

    aimlogdir = Path.home() / '.aimlog'

    for fil in aimlogdir.iterdir():
        instance_results = get_fil_results(fil)

        for result in instance_results:
            full_results.append(InputEvent(int(fil.stem), result[0], result[1]))
    
    full_results.sort(key=lambda x: x.time)

    return full_results

def teardown():
    aimlogdir = Path.home() / '.aimlog'
    if aimlogdir.exists():
        shutil.rmtree(aimlogdir)

def wrap_test(test):
    setup()
    test_expected = test()
    test_actual = getresults()
    did_test_pass = do_results_match(test_actual, test_expected)
    teardown()
    print(test_actual)
    assert did_test_pass 


if __name__ == '__main__':
    from . import input_tests
    for func in getmembers(input_tests, isfunction):
        if func[0].startswith('test'):
            wrap_test(func[1])
            # print(func[0])
    # print()?
