import json


def shlex(command=None, shell=None):
    shell = shell or '/bin/sh'
    shlexed = [shell]
    if command:
        shlexed.extend(['-c', command])
    return shlexed
