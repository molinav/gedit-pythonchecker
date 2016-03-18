from . main.controller import CheckerController


class PythonCheckerPluginAppActivatable(object):
    
    def do_activate(self):
        pass
    
    def do_deactivate(self):
        pass


class PythonCheckerWindowActivatable(CheckerController):
    
    def do_activate(self):
        self.enable()
    
    def do_deactivate(self):
        self.disable()
    
    def do_update_state(self):
        pass

    def do_create_configure_widget(self):
        return self.configure()

