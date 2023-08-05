"""
Contains the `CommandPlugin` class, as well as the related decorator `command`.
Also contains the derived `HelpPlugin` and the `help_command` decorator.
"""

import sys
import inspect
import warnings
from typing import List, Optional, Union, Iterator

from intermake.engine.constants import EThread
from intermake.engine.environment import MENV
from intermake.engine.mandate import Mandate
from intermake.engine.plugin import NoCallError, Plugin
from intermake.engine.theme import Theme
from intermake.plugins import visibilities
from intermake.plugins.visibilities import VisibilityClass
from intermake.visualisables.visualisable import UiInfo
from mhelper import override, ansi_helper
from mhelper.reflection_helper import FnArg, IFunction, FnInspect


__author__ = "Martin Rusilowicz"


def command( _fn = None,
             *,
             names: Optional[Union[str, List[str]]] = None,
             description: Optional[str] = None,
             threading: Optional[EThread] = None,
             visibility: Optional[VisibilityClass] = None,
             true_function = None,
             highlight: bool = False,
             register: bool = True ):
    """
    DECORATOR FOR FUNCTION OR CLASS.
    
    *** PLEASE SEE `CommandPlugin.__init__` for parameter descriptions ***
    
    For a function:
        The function is wrapped in the `CommandPlugin` class, below.
        See `Plugin.__init__` for argument descriptions, with the exception of the `register` argument, that automatically registers the plugin with the host when set.
    
        This decorator is primarily used to allow the user to access functions as "plugins", but can also be used to quickly add support for asynchronous support to a function.
        
        ```
        @command()
        def spam( a : int ) -> None:
            . . .
            
        @command(names = ["eggs", "beans"]):
        def beans( a : str ) -> None:
            . . .
        ```
        
    For a class:
        An _instance_ of the class is registered with the host.
        Since the classes constructor call `Plugin.__init__`, no other arguments should be passed to the `command` decorator.
        If constructor arguments need to be passed, the caller should instead create their instance manually and call `MENV.plugins.register` on that instance.
    """
    
    
    def ___command( fn ):
        from intermake.engine.environment import MENV
        
        if not inspect.isfunction( fn ):
            plugin = fn()
            fn.instance = plugin
        else:
            plugin = CommandPlugin( names = names,
                                    description = description,
                                    threading = threading,
                                    visibility = visibility,
                                    function = fn,
                                    highlight = highlight,
                                    true_function = true_function )
        
        if register:
            if hasattr( sys, "_getframe" ):
                # inspect.stack is immensely slow so we prefer to use sys._getframe instead
                frame_ = sys._getframe( 1 )
            else:
                frame_ = inspect.stack()[1]
            
            module_ = inspect.getmodule( frame_ )
            MENV.plugins.register( plugin, module_ )
        
        if not inspect.isfunction( fn ):
            return fn
        else:
            return plugin
    
    
    if _fn is not None:
        return ___command( _fn )
    else:
        return ___command


class CommandPlugin( Plugin ):
    """
    Wraps a function into an Plugin object.
    """
    
    
    def __init__( self,
                  *,
                  function: IFunction,
                  true_function = None,
                  names: Optional[Union[str, List[str]]] = None,
                  description: Optional[str] = None,
                  threading: Optional[EThread] = None,
                  visibility: Optional[VisibilityClass] = None,
                  highlight: bool = False,
                  folder: Optional[str] = None ):
        """
        Constructor.
        See `Plugin.__init__` for argument descriptions.
        
        Note that several of the arguments get defaults from the function via reflection, if not provided.
        
        :param function:        Function to call.
                                Plugin arguments are constructed via reflection, hence this must be a fully annotated function.
                                Any argument named `self` is ignored.
        
        :param true_function:   Function to call. `function` is then only used for the reflection stage. If `None`, `function` is used for reflection and calling.
        :param names:           As `Plugin.__init__`, but a default name (the function name) is used if this is `None`.
        :param description:     As `Plugin.__init__`, but a default description (the function documentation) is used if this is `None`.
        :param threading:       As `Plugin.__init__`.
        :param visibility:      As `Plugin.__init__`.
        :param highlight:       As `Plugin.__init__`.
        :param folder:          As `Plugin.__init__`.
        """
        self.function_info = FnInspect( function )
        
        if not names:
            name = function.__name__  # type: str
            name = name.strip( "_" )
            names = [name]
        
        super().__init__( names = names,
                          description = description or self.function_info.description,
                          threading = threading,
                          highlight = highlight,
                          visibility = visibility,
                          folder = folder )
        
        function_info = self.function_info
        
        for arg in function_info.args:
            self._add_argument( arg )
        
        if true_function is not None:
            self.function = true_function  # type: IFunction
        else:
            self.function = function  # type: IFunction
        
        assert hasattr( self.function, "__call__" ), "Command plugin requires a callable object, but this object is not callable. The offending object is «{0}».".format( self.function )
    
    
    def __call__( self, *args, **kwargs ):
        """
        INHERITED
        This method exists to allow a function decorated by encapsulation in this class (i.e. using `@command()`) to be called as if the decorator had never been added.
        """
        
        # Try to run the plugin from within another
        try:
            return super().__call__( *args, **kwargs )
        except NoCallError:
            # noinspection PyCallingNonCallable
            return self.function( *args, **kwargs )
    
    
    @override
    def on_run( self ) -> Optional[object]:
        """
        INHERITED
        """
        from intermake.engine.environment import MCMD
        kwargs_ = MCMD.args.tokwargs()
        # noinspection PyCallingNonCallable
        return self.function( **kwargs_ )


class HelpPlugin( CommandPlugin ):
    """
    Special case of `CommandPlugin` that just shows help.
    
    The help-text is obtained by calling the function itself.
        * Return `None` or `""` to use the documentation of the function (`__doc__`).
        * Use `$(DOC)` in the returned text to include the documentation inline.
        * The function can return any object coercible to `str`.
    
    Since the function is use to obtain the help text, rather than being called by the user, it cannot not take any parameters.
    """
    
    
    def __init__( self, *, names: List[str] = None, function: IFunction ):
        super().__init__( names = names, function = function, visibility = visibilities.HELP )
    
    
    def on_run( self ):
        from intermake.engine.environment import MCMD
        from intermake.engine import cli_helper
        desc = self.function()
        desc = cli_helper.format_doc( desc )
        
        for line in ansi_helper.wrap( desc, MENV.host.console_width ):
            MCMD.print( line + Theme.RESET )
    
    
    # def get_description( self ):
    #     provided = self.function()
    #     
    #     if not provided:
    #         provided = super().get_description()
    #     else:
    #         provided = str( provided )
    #         
    #         if "$(DOC)" in provided:
    #             provided = provided.replace( "$(DOC)", super().get_description() )
    #     
    #     return provided
    
    
    def visualisable_info( self ) -> UiInfo:
        result = super().visualisable_info()
        from intermake_qt.forms.designer.resource_files import resources
        result.icon = resources.whatsthis
        return result


def help_command( register = True, **kwargs ):
    """
    Decorator for help plugins. Help plugins specify the help-text in their doc-comments and/or generate it dynamically.
    See `HelpPlugin` for more details.
    
    :param register: When set, registers the plugin with the `intermake` environment.
    :param kwargs: Passed to `HelpPlugin` constructor.
    """
    
    
    def __command( fn ):
        # noinspection PyArgumentList
        plugin = HelpPlugin( function = fn, **kwargs )
        
        if register:
            frame = inspect.stack()[1]
            module_ = inspect.getmodule( frame[0] )
            MENV.plugins.register( plugin, module_ )
        
        return plugin
    
    
    return __command


def iter_args_as_pluginargs( function_info: FnInspect ) -> Iterator[FnArg]:
    """
    Yields a series of :class:`FnArg`s from a function's parameters.
    """
    warnings.warn("Deprecated - use function_info.args", DeprecationWarning)
    for arg in function_info.args:
        if not arg.description:
            if arg.name == "self":
                arg.description = "internal"
            else:
                warnings.warn( "An argument «{}» on «{}.{}» has no description.".format( arg.name, function_info.function.__module__, function_info.function.__qualname__ ), UserWarning )
        
        if (arg.annotation is Mandate) or (arg.name == "mandate"):
            raise ValueError( "Legacy code detected. Plugins should not take a `mandate` parameter." )
        
        if arg.name != "self":
            yield FnArg( arg.name, arg.annotation, arg.default, arg.description )
