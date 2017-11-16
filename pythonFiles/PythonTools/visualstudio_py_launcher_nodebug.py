# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Starts running a block of code or a python file.
"""

import sys
import os
from os import path
try:
    import visualstudio_py_util as _vspu
except:
    import traceback
    traceback.print_exc()
    print('''
Internal error detected. Please copy the above traceback and report at
https://github.com/Microsoft/vscode-python/issues

Press Enter to close. . .''')
    try:
        raw_input()
    except NameError:
        input()
    import sys
    sys.exit(1)

LAST = _vspu.to_bytes('LAST')
OUTP = _vspu.to_bytes('OUTP')
LOAD = _vspu.to_bytes('LOAD')

def launch():
    # Arguments are:
    # 1. Working directory.
    # 2. VS debugger port to connect to.
    # 3. GUID for the debug session
    # 4. Debug options (as integer - see enum PythonDebugOptions).
    # 5. '-m' or '-c' to override the default run-as mode. [optional]
    # 6. Startup script name.
    # 7. Script arguments.s

    # change to directory we expected to start from
    os.chdir(sys.argv[1])

    port_num = int(sys.argv[2])
    debug_id = sys.argv[3]
    debug_options = parse_debug_options(sys.argv[4])

    del sys.argv[0:5]

    # set run_as mode appropriately
    run_as = 'script'
    if sys.argv and sys.argv[0] == '-m':
        run_as = 'module'
        del sys.argv[0]
    if sys.argv and sys.argv[0] == '-c':
        run_as = 'code'
        del sys.argv[0]

    # preserve filename before we del sys.
    filename = sys.argv[0]

    # fix sys.path to be the script file dir.
    sys.path[0] = ''

    currentPid = os.getpid()

    run(filename, port_num, debug_id, debug_options, currentPid, run_as)

def run(file, port_num, debug_id, debug_options, currentPid, run_as = 'script'):
    attach_process(port_num, currentPid, debug_id, debug_options)

    # now execute main file
    globals_obj = {'__name__': '__main__'}

    try:
        if run_as == 'module':
            _vspu.exec_module(file, globals_obj)
        elif run_as == 'code':
            _vspu.exec_code(file, '<string>', globals_obj)
        else:
            _vspu.exec_file(file, globals_obj)
    except:
        exc_type, exc_value, exc_tb = sys.exc_info()
        handle_exception(debug_options, exc_type, exc_value, exc_tb)

    _vspu.write_bytes(conn, LAST)
    # wait for message to be received by debugger.
    import time
    time.sleep(0.5)

    if 'WaitOnNormalExit' in debug_options:
        do_wait()

def attach_process(port_num, currentPid, debug_id, debug_options):
    import socket
    try:
        xrange
    except:
        xrange = range

    global conn
    for i in xrange(50):
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect(('127.0.0.1', port_num))
            # initial handshake.
            _vspu.write_string(conn, debug_id)
            _vspu.write_int(conn, 0)
            _vspu.write_int(conn, currentPid)

            # notify debugger that process has launched.
            _vspu.write_bytes(conn, LOAD)
            _vspu.write_int(conn, 0)
            break
        except:
            import time
            time.sleep(50./1000)
    else:
        raise Exception('failed to attach')

def handle_exception(debug_options, exc_type, exc_value, exc_tb):
    # Specifies list of files not to display in stack trace.
    global DONT_DEBUG
    DONT_DEBUG = [path.normcase(__file__), path.normcase(_vspu.__file__)]
    if sys.version_info >= (3, 3):
        DONT_DEBUG.append(path.normcase('<frozen importlib._bootstrap>'))
    if sys.version_info >= (3, 5):
        DONT_DEBUG.append(path.normcase('<frozen importlib._bootstrap_external>'))

    wait_on_normal_exit = 'WaitOnNormalExit' in debug_options
    wait_on_abnormal_exit = 'WaitOnAbnormalExit' in debug_options

    # Display the exception and wait on exit.
    if exc_type is SystemExit:
        if (wait_on_abnormal_exit and exc_value.code) or (wait_on_normal_exit and not exc_value.code):
            print_exception(exc_type, exc_value, exc_tb)
            do_wait()
    else:
        print_exception(exc_type, exc_value, exc_tb)
        if wait_on_abnormal_exit:
            do_wait()

def print_exception(exc_type, exc_value, exc_tb):
    import traceback
    import sys
    from os import path
    # remove debugger frames from the top and bottom of the traceback.
    tb = traceback.extract_tb(exc_tb)
    for i in [0, -1]:
        while tb:
            frame_file = path.normcase(tb[i][0])
            if not any(is_same_py_file(frame_file, f) for f in DONT_DEBUG):
                break
            del tb[i]

    # print the traceback.
    if tb:
        print('Traceback (most recent call last):')
        for out in traceback.format_list(tb):
            sys.stderr.write(out)
            sys.stderr.flush()

    # print the exception.
    for out in traceback.format_exception_only(exc_type, exc_value):
        sys.stderr.write(out)
        sys.stderr.flush()

def is_same_py_file(file1, file2):
    """compares 2 filenames accounting for .pyc files"""
    if file1.endswith('.pyc') or file1.endswith('.pyo'):
        file1 = file1[:-1]
    if file2.endswith('.pyc') or file2.endswith('.pyo'):
        file2 = file2[:-1]

    return file1 == file2

def do_wait():
    import sys
    try:
        import msvcrt
    except ImportError:
        sys.__stdout__.write('Press Enter to continue . . . ')
        sys.__stdout__.flush()
        sys.__stdin__.read(1)
    else:
        sys.__stdout__.write('Press any key to continue . . . ')
        sys.__stdout__.flush()
        msvcrt.getch()

def parse_debug_options(s):
    return set([opt.strip() for opt in s.split(',')])

if __name__ == '__main__':
    launch()
