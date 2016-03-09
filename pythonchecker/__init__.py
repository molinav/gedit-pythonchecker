from . import controller


class PythonCheckerPluginAppActivatable(object):
    
    def do_activate(self):
        pass
    
    def do_deactivate(self):
        pass


class PythonCheckerWindowActivatable(controller.CheckerController):
    
    def do_activate(self):
        self.enable()
    
    def do_deactivate(self):
        self.disable()
    
    def do_update_state(self):
        pass

