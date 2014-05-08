__author__ = 'jdroot'

from pycloud.pycloud.mongo import DictObject

class VMImage(DictObject):

    # Create our default attributes but then pass everything up to the super
    def __init__(self, *args, **kwargs):
        self.disk_image = None
        self.state_image = None
        super(VMImage, self).__init__(*args, **kwargs)