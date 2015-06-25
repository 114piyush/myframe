from pyVmomi import vim, vmodl
from vimutils import WaitForTasks, GetObject
import os

SI = None

class VirtualMachine:
    def __init__(self, log, si, name, IP=None, user=None, password=None):
        self.log = log
	self.name = name
	self.IP = IP
	self.user = user
	self.password = password
	self.si = si
	self.vmRef = None

    def GetVMMor(self, vmName):
        self.log.info('Getting vmMor for vm %s' % vmName)
	if not self.vmRef:
            self.vmRef = GetObject(self.si, [vim.VirtualMachine], vmName)
	return self.vmRef

    def CloneVM(self, cloneName, datastore=None, isPowerOn=False,
                isTemplate=False, snapshotRef=None, isMemory=False):
        relocateSpec = vim.vm.RelocateSpec()
        if datastore:
	    relocateSpec.datastore = datastore
        #relocateSpec.diskMoveType = 'moveAllDiskBackingsAndDisallowSharing'
        cloneSpec = vim.vm.CloneSpec(location=relocateSpec, powerOn=isPowerOn,
                                     template=isTemplate, snapshot=snapshotRef,
                                     memory=isMemory)
	self.log.info('Creating clone of vm %s to %s' % (self.name, cloneName)) 
        task = self.vmRef.CloneVM_Task(self.vmRef.parent, cloneName, cloneSpec)
        status = WaitForTasks(self.si, [task])
	cloneVM = VirtualMachine(self.log, self.si, cloneName)
	cloneVM.vmRef = task.info.result
	return cloneVM

    def CloneManyVM(self, num, clonePrefix=None, datastore=None,
                    isPowerOn=False, isTemplate=False, snapshotRef=None,
    		    isMemory=False):
        if not clonePrefix:
            clonePrefix = 'test-coho-' + str(os.getpid())
        cloneRef = []
        tasks = []
	self.log.info('Creating %s full clone vms from vm %s' % (num, self.name))
        for i in xrange(1, num+1):
            cloneName = clonePrefix + '-' + str(i)
            relocateSpec = vim.vm.RelocateSpec()
            if datastore:
	        relocateSpec.datastore = datastore
            #relocateSpec.diskMoveType = 'moveAllDiskBackingsAndDisallowSharing'
            cloneSpec = vim.vm.CloneSpec(location=relocateSpec, powerOn=isPowerOn,
                                         template=isTemplate, snapshot=snapshotRef,
                                         memory=isMemory)
	    self.log.info('Creating clone of vm %s to %s' % (self.name, cloneName)) 
            task = self.vmRef.CloneVM_Task(self.vmRef.parent, cloneName, cloneSpec)
            tasks.append(task)
        WaitForTasks(self.si, tasks)
	vms = []
	for task in tasks:
	    vm = task.info.result
	    cloneVM = VirtualMachine(self.log, self.si, vm.name)
	    cloneVM.vmRef = vm
	    vms.append(cloneVM)
	return vms

    def LinkCloneVM(self, cloneName, datastore=None, isPowerOn=False,
                    isTemplate=False, snapshotRef=None, isMemory=False):
        relocateSpec = vim.vm.RelocateSpec()
        if datastore:
	    relocateSpec.datastore = datastore
        relocateSpec.diskMoveType = 'createNewChildDiskBacking'
        if not self.vmRef.snapshot:
	    self.TakeSnapshot()
        snapshotRef = self.vmRef.snapshot.currentSnapshot
        cloneSpec = vim.vm.CloneSpec(location=relocateSpec, powerOn=isPowerOn,
                                     template=isTemplate, snapshot=snapshotRef,
                                     memory=isMemory)
	self.log.info('Creating Linked clone of vm %s to %s' % (self.name, cloneName)) 
        task = self.vmRef.CloneVM_Task(self.vmRef.parent, cloneName, cloneSpec)
        status = WaitForTasks(self.si, [task])
	cloneVM = VirtualMachine(self.log, self.si, cloneName)
	cloneVM.vmRef = task.info.result
	return cloneVM

    def LinkCloneManyVM(self, num, clonePrefix=None, datastore=None,
                    isPowerOn=False, isTemplate=False, snapshotRef=None,
    		    isMemory=False):
        if not clonePrefix:
            clonePrefix = 'test-coho-' + str(os.getpid())
        cloneRef = []
        tasks = []
	self.log.info('Creating %s linked clone vms from vm %s' % (num, self.name))
        for i in xrange(1, num+1):
            cloneName = clonePrefix + '-' + str(i)
            relocateSpec = vim.vm.RelocateSpec()
            if datastore:
	        relocateSpec.datastore = datastore
            relocateSpec.diskMoveType = 'createNewChildDiskBacking'
            if not self.vmRef.snapshot:
	        self.TakeSnapshot()
            snapshotRef = self.vmRef.snapshot.currentSnapshot
            cloneSpec = vim.vm.CloneSpec(location=relocateSpec, powerOn=isPowerOn,
                                         template=isTemplate, snapshot=snapshotRef,
                                         memory=isMemory)
	    self.log.info('Creating link clone of vm %s to %s' % (self.name, cloneName)) 
            task = self.vmRef.CloneVM_Task(self.vmRef.parent, cloneName, cloneSpec)
            tasks.append(task)
        WaitForTasks(self.si, tasks)
	vms = []
	for task in tasks:
	    vm = task.info.result
	    cloneVM = VirtualMachine(self.log, self.si, vm.name)
	    cloneVM.vmRef = vm
	    vms.append(cloneVM)
	return vms

    def TakeSnapshot(self, name=None, description=None, memory=False, quiesce=False):
        if not name:
	    name = 'test-coho-snapshot-' + str(os.getpid())
	task = self.vmRef.CreateSnapshot_Task(name, description, memory, quiesce)
	status = WaitForTasks(self.si, [task])
