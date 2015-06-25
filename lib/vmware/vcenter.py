from framework.exceptions import VCError
from pyVmomi import vim
import pyVim.connect
import securities

class VirtualCenter:
    def __init__(self, log, IP=None, user=None, password=None):
        self.log = log
	self.IP = IP
	self.user = user
	self.password = password
	self.si = self.GetVCServiceInstance()

    def DisconnectVC(self):
        self.log.info('Disconnecting VC %s...' % self.IP)
        try:
            pyVim.connect.Disconnect(self.si)
        except vim.fault.HostConnectFault:
	    raise VCError('Unable to disconnect to VC %s' % self.IP)

    def GetVCServiceInstance(self):
        si = None
	credential = []
	if self.user:
	   credential.append({'user' : self.user, 'password' : self.password})
	else:
	   credential = securities.VCPASS
	for cred in credential:
	    user = cred['user']
	    password = cred['password']
	    self.log.info('Connecting to VC %s using user=%s password=%s' %
	                  (self.IP, user, password))
            try:
                si = pyVim.connect.Connect(host=self.IP, user=user,
		                           pwd=password)
            except vim.fault.HostConnectFault:
	        raise VCError('Unable to connect to VC %s' % self.IP)
            except vim.fault.InvalidLogin:
	        self.log.debug('Invalid login to VC %s' % self.IP)
		continue
            # Successful login
	    self.user = user
	    self.password = password
            return si
	if not si:
	    raise VCError('Not able to login VC %s' % self.IP)
