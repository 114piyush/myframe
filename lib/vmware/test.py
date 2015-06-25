from vm import VirtualMachine
from vcenter import VirtualCenter
from framework.log import Log
logObj = Log(logDir='.', consoleOutput=True)
log = logObj.log

vc = VirtualCenter(log, IP='10.128.8.39')
vm = VirtualMachine(log, vc.si, 'dummyvm')
vm.GetVMMor(vm.name)
#vm.LinkCloneVM('test-1')
#vm.CloneManyVM(2,clonePrefix='dummyvm-1')
vm.LinkCloneManyVM(2)

