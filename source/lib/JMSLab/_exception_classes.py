class ExecCallError(Exception):
	def __init__(self, message = ''):
		print 'Error: ' + message

class BadExtensionError(Exception):
    pass

class LFSError(Exception):
    pass

class ReleaseError(Exception):
    pass

class PrerequisiteError(Exception):
    pass

class TargetNonexistenceError(Exception):
    pass