# -*- coding: utf-8 -*-

from copy import deepcopy

def get_stdout(commandline):
    import subprocess
    return subprocess.check_output(commandline, shell=True)

class Service:
    def __init__(self, service_name_line, display_name_line):
        # SERVICE_NAME: AdobeARMservice
        # DISPLAY_NAME: Adobe Acrobat Update Service
        #               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        self._service_name = service_name_line.split(':')[1].strip()
        self._display_name = display_name_line.split(':')[1].strip()

    @property
    def service_name(self):
        return self._service_name

    @property
    def display_name(self):
        return self._display_name

    @property
    def properties(self):
        return self._properties

    def be_matched(self, query):
        q = query.lower()
        if self._service_name.lower().find(q)!=-1:
            return True
        if self._display_name.lower().find(q)!=-1:
            return True
        return False

    def update_detail(self):
        outstr = get_stdout('sc query "{:}"'.format(self._service_name))
        query_dict = scquery_to_dict(outstr)
        outstr = get_stdout('sc qc "{:}"'.format(self._service_name))
        qc_dict = scquery_to_dict(outstr)

        # マージする.
        # update() は破壊的なので deepcopy で最初に clone しとく.
        self._properties = deepcopy(query_dict)
        self._properties.update(qc_dict)

    def __str__(self):
        return self._service_name

def scquery_to_dict(raw_output):
    # [Output Sample]
    # SERVICE_NAME: Service1
    #      TYPE               : 20  WIN32_SHARE_PROCESS
    #      START_TYPE         : 3   DEMAND_START
    #      STATE              : 4   RUNNING
    #                               (STOPPABLE, NOT_PAUSABLE, IGNORES_SHUTDOWN)
    #      ....

    ret = {}
    lines = raw_output.split('\n')
    for i, line in enumerate(lines):
        if len(line.strip())==0:
            continue

        if line[0]!=' ':
            continue

        if line.find(':')==-1:

            if len(line.split(','))>=3:
                #   (STOPPABLE, NOT_PAUSABLE, IGNORES_SHUTDOWN)
                #    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                stop, pause, shutdown = line.strip()[1:-1].split(',')
                ret['operation_stop']     = stop
                ret['operation_pause']    = pause.strip()
                ret['operation_shutdown'] = shutdown.strip()
                continue

            continue

        # BINARY_PATH_NAME : C:\Windows\system32\svchost.exe -k netsvcs
        #                  |  |
        #                  OK |
        #                     NG(ここは split のデリミタとして扱わない.)
        key, value = line.split(':', 1)
        key = key.lower().strip()
        value = value.strip()
        ret[key] = value

    return ret


def parse_arguments():
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('queries', nargs='*')

    parser.add_argument('-l','--line', default=False, action='store_true',
        help='Output as one line for grep.')
    parser.add_argument('-s','--short', default=False, action='store_true',
        help='Use simple format, service name and display name only.')

    parsed_args = parser.parse_args()
    return parsed_args
args = parse_arguments()

queries = args.queries
use_short_format = args.short
use_oneline = args.line

# SERVICE_NAME: AdobeARMservice
# DISPLAY_NAME: Adobe Acrobat Update Service
# SERVICE_NAME: AeLookupSvc
# DISPLAY_NAME: Application Experience
# ...
# こんな行が並ぶ.
# 一応空行を除いといて, 実エントリ数は総行数のちょうど半分になるはず.
lines = get_stdout('sc query | findstr /i "SERVICE_N DISPLAY"').split('\n')
lines = [line for line in lines if len(line.strip())!=0]
totalnum = len(lines)/2

services = []
for i in range(totalnum):
    baseidx = i*2
    service_name = lines[baseidx]
    display_name = lines[baseidx+1]
    service = Service(service_name, display_name)
    services.append(service)

def print_service(service_inst, use_oneline=False):
    outlines = []

    if use_oneline==False:
        outlines.append('{:}({:})'.format(service_inst.service_name, service_inst.display_name))

        propertylist = []
        for k in service_inst.properties:
            v = service_inst.properties[k]
            propertylist.append('{:<18} : {:}'.format(k, v))

        propertylist.sort()
        for line in propertylist:
            outlines.append(line)

        outlines.append('')

    else:
        outline = '* {:}({:})'.format(service_inst.service_name, service_inst.display_name)
        outline += ' -> '

        propertylist = []
        for k in service_inst.properties:
            v = service_inst.properties[k]
            propertylist.append('{:}={:}'.format(k, v))

        propertylist.sort()
        for i, line in enumerate(propertylist):
            if i!=0:
                outline += ', '
            outline += line

        outlines = [outline]

    for line in outlines:
        print line

target_services = []
if len(queries)==0:
    target_services = services
else:
    for _, service in enumerate(services):
        matched = True
        for _, query in enumerate(queries):
            if service.be_matched(query) == False:
                matched = False
                break
        if matched:
            target_services.append(service)

for i, service in enumerate(target_services):
    if use_short_format:
        print '* {:}({:})'.format(service.service_name, service.display_name)
    else:
        service.update_detail()
        print_service(service, use_oneline)

print 'ALL {:} entries.'.format(len(target_services))
