r"""IO and Model drivers."""
import importlib


def import_driver(driver=None):
    r"""Dynamically import a driver based on a string.

    Args:
        driver (str): Name of the driver that should be imported.

    """
    if driver is None:
        driver = 'Driver'
    drv = importlib.import_module('cis_interface.drivers.%s' % driver)
    class_ = getattr(drv, driver)
    return class_
                    

def create_driver(driver=None, name=None, args=None, **kwargs):
    r"""Dynamically create a driver based on a string and other driver
    properties.

    Args:
        driver (str): Name of the driver that should be created.
        name (str): Name to give the driver.
        args (object, optional): Second argument for drivers which take a
            minimum of two arguments. If None, the driver is assumed to take a
            minimum of one argument. Defaults to None.
        **kwargs: Additional keyword arguments are passed to the driver
            class.

    Returns:
        object: Instance of the requested driver.

    """
    class_ = import_driver(driver)
    if args is None:
        instance = class_(name, **kwargs)
    else:
        instance = class_(name, args, **kwargs)
    return instance


__all__ = ['import_driver', 'create_driver', 'Driver',
           'ModelDriver', 'PythonModelDriver', 'GCCModelDriver',
           'MakeModelDriver', 'MatlabModelDriver',
           'IODriver', 'FileInputDriver', 'FileOutputDriver',
           'AsciiFileInputDriver', 'AsciiFileOutputDriver',
           'AsciiTableInputDriver', 'AsciiTableOutputDriver',
           'RPCDriver', 'RMQDriver', 'RMQInputDriver', 'RMQOutputDriver',
           'RMQClientDriver', 'RMQServerDriver']
