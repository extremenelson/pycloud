__author__ = 'jdroot'

controllers = {}

#Return a controller by name, error if no controller is found
def get_controller(name):
    name = name.lower() + 'controller'
    if name in controllers:
        return controllers[name]
    else:
        raise KeyError('Controller ' + name + ' was not found.')

# Define all of our controllers by importing them
def load_controllers():

    # Import All Controllers Here

    from pycloud.manager.controllers.api import ApiController
    from pycloud.manager.controllers.services import ServicesController


    # Cache the controllers in a look up map
    controllers.update((name.lower(), obj) for name, obj in locals().iteritems())