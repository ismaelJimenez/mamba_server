# -*- coding: utf-8 -*-
"""Minimal XMLRPC vs Dictionary test"""

import xmlrpc.client
import timeit
import subprocess
import time

NUMBER_OF_LOOPS = 1000

proc = subprocess.Popen(['python3', '-u', 'minimal_xmlrpc_server.py'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)

try:
    time.sleep(1)
    xmlrpc_time = timeit.timeit(
        "s.pow(2,3)",
        setup=
        "import xmlrpc.client; s = xmlrpc.client.ServerProxy('http://localhost:8000')",
        number=NUMBER_OF_LOOPS) / NUMBER_OF_LOOPS
    dict_time = timeit.timeit("s['pow'](2,3)",
                              setup="s = {'pow': pow}",
                              number=NUMBER_OF_LOOPS) / NUMBER_OF_LOOPS
    pow_time = timeit.timeit("s(2,3)", setup="s = pow",
                             number=NUMBER_OF_LOOPS) / NUMBER_OF_LOOPS

    rx_time = timeit.timeit(
        "subject.on_next(pow(2,3))",
        setup=
        'from rx.subject import Subject; subject = Subject(); subject.subscribe(on_next=lambda i: None)',
        number=NUMBER_OF_LOOPS) / NUMBER_OF_LOOPS

    mamba_rx_time = timeit.timeit(
        "subject.on_next(pow(2, 3))",
        setup=
        'from mamba.rx_mamba import Subject; subject = Subject(); subject.subscribe(lambda i: None)',
        number=NUMBER_OF_LOOPS) / NUMBER_OF_LOOPS

finally:
    proc.terminate()

    print(f'Time for performing POW operation: {pow_time}')
    print(
        f'Time for looking a function in a dictionary: {dict_time - pow_time}')
    print(
        f'Time for calling a function in a xmlrpc server: {xmlrpc_time - pow_time}'
    )
    print(f'Time for calling a function with a Rx: {rx_time - pow_time}')
    print(
        f'Time for calling a function with a Mamba Rx: {mamba_rx_time - pow_time}'
    )
    print(
        f'Xmlrpc is {int((xmlrpc_time - pow_time) / (dict_time - pow_time))} times slower as a dictionary'
    )
    print(
        f'Rx is {int((rx_time - pow_time) / (dict_time - pow_time))} times slower as a dictionary'
    )
    print(
        f'Mamba Rx is {int((mamba_rx_time - pow_time) / (dict_time - pow_time))} times slower as a dictionary'
    )
    print(
        f'Mamba Rx is {round(((rx_time - pow_time) / (mamba_rx_time - pow_time)), 2)} times faster than RxPy'
    )
