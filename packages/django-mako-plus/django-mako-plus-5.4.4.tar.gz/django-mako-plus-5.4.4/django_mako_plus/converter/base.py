from django.http import Http404
from django.core.exceptions import ImproperlyConfigured

from ..decorators import OptionsDecorator
from ..util import log
from .parameter import ViewParameter
from .info import ConverterFunctionInfo

import logging
import inspect
from collections import namedtuple
from operator import attrgetter



class view_function(OptionsDecorator):
    '''
    A decorator to signify which view functions are "callable" by web browsers.
    and to convert parameters using type hints, if provided.

    All endpoint functions, such as process_request, must be decorated as:

        @view_function
        function process_request(request):
            ...

    Or:

        @view_function(...)
        function process_request(request):
            ...

    PARAMETER CONVERSION:

    The other purpose of this decorator is to convert URL parameters.
    See the convert_value() function docs below for more info on this.

    CUSTOMIZING THE DECORATOR:

    This decorator is programmed as a class-based decorator so you can
    subclass it with custom behavior.  You can customize how view functions are
    called and how parameters are converted.

        __init__(): you probably don't need to customize this method because it
        already takes any kwargs and sets them as the self.options dictionary.
        If you override __init__, do NOT add positional parameters.  Use only
        keyword parameters.  Positional parameters may mess up the ability
        of the decorator to be call with/without arguments.

        __call__(): this is triggered on each request.  It iterates the parameters
        (for conversion) and then calls the endpoint.  Override this method if
        you want to add or modify the endpoint calling process.

    Customizing Parameter Conversion:

    The primary way to customize conversion is to create new @parameter_converter
    functions in your codebase.  This allows you to add new type converters.
    You can even create functions for types already handled by the built-in
    converters.  Your functions will override the built-in ones.

    If you need to customize more than just a few types, override:

        convert_value(): where individual parameters are converted.

        __call__(): the controller that iterates the parameter values
        and calls convert_value().
    '''
    DECORATED_KEY = '_dmp_view_function_'
    # the list of converters (populated by the @converter_function decorator)
    converters = []
    convert_sorting_enabled = False

    def __init__(self, decorated_function, **options):
        '''Create a new wrapper around the decorated function'''
        super().__init__(decorated_function, **options)

        # flag the function as an endpoint
        setattr(self.decorated_function, self.DECORATED_KEY, self)

        # inspect the parameters on the function
        self.signature = inspect.signature(self.decorated_function)
        param_types = getattr(self.decorated_function, '__annotations__', {})  # not using typing.get_type_hints because it adds Optional() to None defaults, and we don't need to follow mro here
        params = []
        for i, p in enumerate(self.signature.parameters.values()):
            params.append(ViewParameter(
                name=p.name,
                position=i,
                kind=p.kind,
                type=param_types.get(p.name) or inspect.Parameter.empty,
                default=p.default,
            ))
        self.parameters = tuple(params)


    @classmethod
    def _is_decorated(cls, f):
        '''Returns True if the given function is decorated with @view_function'''
        return hasattr(f, cls.DECORATED_KEY)


    @classmethod
    def _register_converter(cls, conv_func, conv_type):
        '''Triggered by the @converter_function decorator'''
        cls.converters.append(ConverterFunctionInfo(conv_func, conv_type, len(cls.converters)))
        cls._sort_converters()


    @classmethod
    def _sort_converters(cls, convert_sorting_enabled=False):
        '''Sorts the converter functions'''
        # convert_sorting_enabled is triggered in DMP's AppConfig.ready()
        # we can't sort before then because models aren't ready
        cls.convert_sorting_enabled = cls.convert_sorting_enabled or convert_sorting_enabled
        if cls.convert_sorting_enabled:
            for converter in cls.converters:
                converter.prepare_sort_key()
            cls.converters.sort(key=attrgetter('sort_key'))


    def __call__(self, *args, **kwargs):
        '''
        Called for every request.  This method runs the converters and then
        calls the actual site view function.

        See the docs for this class on customizing this method.
        '''
        # convert the urlparams
        args, kwargs = self.convert_parameters(*args, **kwargs)

        # call the decorated view function!
        return self.decorated_function(*args, **kwargs)


    def convert_parameters(self, *args, **kwargs):
        '''
        Iterates the urlparams and converts them according to the
        type hints in the current view function.

        Note that args[0] is the request object.  We leave it in args
        so it can convert like everything else (and so parameter
        indices aren't off by one).
        '''
        request = kwargs.get('request', args[0])
        args = list(args)
        urlparam_i = 0
        # add urlparams into the arguments and convert the values
        for parameter_i, parameter in enumerate(self.parameters):
            # skip *args, **kwargs
            if parameter.kind is inspect.Parameter.VAR_POSITIONAL or parameter.kind is inspect.Parameter.VAR_KEYWORD:
                pass
            # value in kwargs?
            elif parameter.name in kwargs:
                kwargs[parameter.name] = self.convert_value(kwargs[parameter.name], parameter, request)
            # value in args?
            elif parameter_i < len(args):
                args[parameter_i] = self.convert_value(args[parameter_i], parameter, request)
            # urlparam value?
            elif urlparam_i < len(request.dmp.urlparams):
                kwargs[parameter.name] = self.convert_value(request.dmp.urlparams[urlparam_i], parameter, request)
                urlparam_i += 1
            # can we assign a default value?
            elif parameter.default is not inspect.Parameter.empty:
                kwargs[parameter.name] = self.convert_value(parameter.default, parameter, request)
            # fallback is None
            else:
                kwargs[parameter.name] = self.convert_value(None, parameter, request)
        return args, kwargs


    def convert_value(self, value, parameter, request):
        '''
        Converts a parameter value in the view function call.

            value:      value from request.dmp.urlparams to convert
                        The value will always be a string, even if empty '' (never None).

            parameter:  an instance of django_mako_plus.ViewParameter that holds this parameter's
                        name, type, position, etc.

            request:    the current request object.

        "converter functions" register with this class using the @parameter_converter
        decorator.  See converters.py for the built-in converters.

        This function goes through the list of registered converter functions,
        selects the most-specific one that matches the parameter.type, and
        calls it to convert the value.

        If the converter function raises a ValueError, it is caught and
        switched to an Http404 to tell the browser that the requested URL
        doesn't resolve to a page.

        Other useful exceptions that converter functions can raise are:

            RedirectException: redirects the browser (see DMP docs)
            InternalRedirectException: redirects processing internally (see DMP docs)
            Http404: returns a Django Http404 response
        '''
        try:
            # we don't convert anything without type hints
            if parameter.type is inspect.Parameter.empty:
                if log.isEnabledFor(logging.DEBUG):
                    log.debug('skipping conversion of parameter `%s` because it has no type hint', parameter.name)
                return value

            # find the converter method for this type
            # I'm iterating through the list to find the most specific match first
            # The list is sorted by specificity so subclasses come before their superclasses
            for ci in self.converters:
                if issubclass(parameter.type, ci.convert_type):
                    if log.isEnabledFor(logging.DEBUG):
                        log.debug('converting parameter `%s` using %s', parameter.name, ci.convert_func)
                    return ci.convert_func(value, parameter)

            # if we get here, there wasn't a converter or this type
            raise ImproperlyConfigured(message='No parameter converter exists for type: {}. Do you need to add an @parameter_converter function for the type?'.format(parameter.type))

        except ValueError as e:
            log.info('ValueError raised during conversion of parameter %s (%s): %s', parameter.position, parameter.name, e)
            raise Http404('Parameter could not be converted')

        except Exception as e:
            log.info('Exception raised during conversion of parameter %s (%s): %s', parameter.position, parameter.name, e)
            raise



# import the default converters
# this must come at the end of the file so view_function above is loaded
# it doesn't matter what's imported -- the file just needs to load
from .converters import __name__ as _
