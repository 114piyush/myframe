# This test is for cloning multiple vms in datastream datastore
from vmware.vm import VirtualMachine
from pyVmomi import vim, vmodl
from vmware.vimutils import WaitForTasks, GetObject
import os

# Global Information
log = None

# Help
# ./test-coho -t clonevms --debug-mode --test-option=vmname:dummyvm,vcip:10.128.8.39,clonetype:link,datastore:micron-root,num:2 --vc-hosts=10.128.8.39

def CheckOption(args):
    testOption = args['testOption']
    if testOption.has_key('vcip'):
        testOption['vmVC'] = filter(lambda x: x.IP == testOption['vcip'], args['vc'])[0]
    else:
        log.error('test option vcip is not defined')
	raise
    if not testOption.has_key('clonetype'):
        log.error('test option clonetype is not defined')
        raise Exception('clonetype is not defined')
    if not testOption.has_key('datastore'):
        log.error('test option datastore is not defined')
        raise Exception('datastore is not defined')
    vm = VirtualMachine(log, testOption['vmVC'].si, testOption['vmname'])
    vm.GetVMMor(vm.name)
    testOption['vm'] = vm

def Run(args):
    global log
    log = args['logObj'].log
    testOption = args['testOption']
    CheckOption(args)
    num = testOption['num']
    # Create base vm first
    datastore = GetObject(testOption['vmVC'].si, [vim.Datastore], testOption['datastore'])
    clonedvm = testOption['vm'].CloneVM('clonevm-base%s' % os.getpid(), datastore=datastore)
    if testOption['clonetype'] == 'full':
        if num:
	    clonedvm.CloneManyVM(num)
	else:
	    clonedvm.CloneVM('testvm-1')
    elif testOption['clonetype'] == 'link':
        if num:
	    clonedvm.LinkCloneManyVM(num)
	else:
	    clonedvm.LinkCloneVM('testvm-1')
