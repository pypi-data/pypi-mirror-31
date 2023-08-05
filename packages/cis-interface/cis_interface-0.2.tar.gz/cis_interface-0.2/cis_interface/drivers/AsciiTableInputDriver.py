from cis_interface import serialize
from cis_interface.tools import eval_kwarg
from cis_interface.drivers.AsciiFileInputDriver import AsciiFileInputDriver


class AsciiTableInputDriver(AsciiFileInputDriver):
    r"""Class to handle input from an ASCII table.

    Args:
        name (str): Name of the input queue to send messages to.
        args (str or dict): Path to the file that messages should be read from
            or dictionary containing the filepath and other keyword arguments
            to be passed to the created AsciiTable object.
        format_str (str): Format string that should be used to format
            output in the case that the io_mode is 'w' (write). It is not
            required if the io_mode is any other value.
        field_names (list, optional): List of column names. Defaults to None.
        field_units (list, optional): List of column units. Defaults to None.
        use_astropy (bool, optional): If True, astropy is used to determine
            a table's format if it is installed. If False, a format string
            must be contained in the table. Defaults to False.
        delimiter (str, optional): String that should be used to separate
            columns. Default set by serialize._default_delimiter.
        comment (str, optional): String that should be used to identify
            comments. Default set by serialize._default_comment.
        newline (str, optional): String that should be used to identify
            the end of a line. Default set by serialize._default_newline.
        as_array (bool, optional): If True, the table contents are sent all at
            once as an array. Defaults to False.
        **kwargs: Additional keyword arguments are passed to parent class.

    """
    def __init__(self, name, args, **kwargs):
        file_keys = ['format_str', 'field_names', 'field_units',
                     'use_astropy', 'delimiter', 'as_array']
        alias_keys = [('column_names', 'field_names'),
                      ('column_units', 'field_units'),
                      ('column', 'delimiter')]
        for old, new in alias_keys:
            if kwargs.get(old, None) is not None:
                kwargs.setdefault(new, kwargs.pop(old))
        icomm_kws = kwargs.get('icomm_kws', {})
        icomm_kws.setdefault('comm', 'AsciiTableComm')
        for k in file_keys:
            if k in kwargs:
                icomm_kws[k] = kwargs.pop(k)
                # Eval commands non-string args from yaml string
                if k in ['field_names', 'field_units']:
                    if isinstance(icomm_kws[k], str):
                        icomm_kws[k] = icomm_kws[k].split(',')
                elif k in ['use_astropy', 'as_array']:
                    icomm_kws[k] = eval_kwarg(icomm_kws[k])
        kwargs['icomm_kws'] = icomm_kws
        super(AsciiTableInputDriver, self).__init__(name, args, **kwargs)
        self.debug('(%s)', args)

    def update_serializer(self, msg):
        r"""Update the serializer for the output comm based on input."""
        sinfo = self.icomm.serializer.serializer_info
        sinfo['stype'] = 0
        self.ocomm.serializer = serialize.get_serializer(**sinfo)
