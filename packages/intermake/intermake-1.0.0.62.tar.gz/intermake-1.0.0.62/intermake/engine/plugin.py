import warnings
from typing import Callable, List, Optional, Union, cast

from intermake.engine.constants import EThread
from intermake.engine.mandate import ArgsKwargs
from intermake.engine.plugin_manager import PluginFolder
from intermake.engine.progress_reporter import ProgressReporter
from intermake.plugins import visibilities
from intermake.plugins.visibilities import VisibilityClass
from intermake.visualisables.visualisable import EColour, IVisualisable, UiInfo
from mhelper import abstract, array_helper, exception_helper, override, protected, string_helper, virtual
from mhelper.reflection_helper import FnArg, AnnotationInspector


__author__ = "Martin Rusilowicz"


class NoCallError( Exception ):
    pass


class PartialSuccess( Exception ):
    """
    A plugin may circumnavigate the normal return procedure and return a successful result via an exception.
    """
    
    
    def __init__( self, message = None, result = None ):
        self.result = result
        
        if not message:
            message = "The thread terminated because it has saved or has already created its workload. The primary thread will pick it up. This is not an error."
        
        super().__init__( message )


_unnamed_count = 0


@abstract
class Plugin( IVisualisable ):
    """
    Plugins are things that can be run by the user.
    They appear in the "Plugins" section of the main screen in the GUI and can also be invoked from the command line.
    See readme.md in this directory for details.
    """
    
    FOLDER_DELIMITER = "/"
    
    
    def __init__( self,
                  *,
                  names: Optional[Union[str, List[str]]] = None,
                  description: Optional[str] = None,
                  threading: Optional[EThread] = None,
                  visibility: Optional[VisibilityClass] = None,
                  highlight: bool = False,
                  folder: Optional[str] = None ):
        """
        CONSTRUCTOR
        :param names:           Name or names of the plugin. Mandatory.
        :param description:     Description of the plugin. Mandatory.
        :param threading:       Threading hint for the plugin. Defaults to `EThread.SINGLE`. 
        :param visibility:      Visibility of the plugin (see `VisibilityClass`).
        :param highlight:       Highlight plugin.
        :param folder:          Optional folder where the plugin resides.
                                Esoteric use - plugins automatically collect this from the module anyway.
        """
        
        names = array_helper.as_sequence( names or None, cast = list )
        
        if not names:
            raise ValueError( "A plugin must have at least one name." )
        
        if threading is None:
            threading = EThread.SINGLE
        
        if visibility is None:
            visibility = visibilities.COMMON
        elif not isinstance( visibility, VisibilityClass ):
            raise exception_helper.type_error( "visibility", visibility, VisibilityClass )
        
        if not description:
            # Not having a description is probably a mistake
            description = "Not documented :("
            warnings.warn( "A plugin «{}» has no description.".format( names ) )
        
        exception_helper.assert_instance( "description", description, str )
        exception_helper.assert_instance( "threading", threading, EThread )
        
        self.names: List[str] = names
        self.__description = string_helper.fix_indents( description )
        self.__children: List[Plugin] = []
        self.__args: List[FnArg] = []
        self.__threading = threading
        self.parent: Union[Plugin, PluginFolder] = None
        self.visibility_class: VisibilityClass = visibility
        self.__dict__["__doc__"] = description
        self.folder = folder
        self.__highlight = highlight
    
    
    @property
    def name( self ) -> str:
        return self.names[0]
    
    
    @property
    def __name__( self ):
        """
        __name__ property for compatibility with functions.
        """
        return self.name
    
    
    @property
    def display_name( self ):
        from intermake.engine.environment import MENV
        return MENV.host.translate_name( self.name )
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self.name,
                       doc = self.get_description(),
                       type_name = "Plugin",
                       value = "",
                       colour = EColour.RED,
                       icon = "command",
                       extra = { "arguments": self.__args,
                                 "children" : self.__children } )
    
    
    @property
    def is_visible( self ) -> bool:
        return self.visibility_class.is_visible
    
    
    @property
    def is_highlighted( self ) -> bool:
        return self.__highlight
    
    
    @property
    def visibility( self ) -> bool:
        warnings.warn( "deprecated, use is_visible", DeprecationWarning )
        return self.visibility_class()
    
    
    @override
    def __call__( self, *args, **kwargs ):
        """
        INHERITED
        This method exists to allow a function decorated by encapsulation in this class (i.e. using `@command()`) to be called as if the decorator had never been added.
        It has now been added to the base Plugin class to allow all plugins to be called in this manner.
        """
        return self.run( *args, **kwargs )
    
    
    @virtual
    @property
    def args( self ) -> List[FnArg]:
        """
        Returns the set of arguments for this plugin. See `FnArg`.
        
        Derived classes may override this method, if providing arguments dynamically.
        """
        return self.__args
    
    
    def find_arg( self, name: str ) -> FnArg:
        """
        Returns the specified argument. See `FnArg`.
        """
        from intermake.engine.environment import MENV
        
        host = MENV.host
        friendly_name = host.translate_name( name )
        
        for arg in self.args:
            if host.translate_name( arg.name ) == friendly_name:
                return arg
        
        raise KeyError( "There is no argument named «{}» in «{}».".format( name, self ) )
    
    
    @protected
    def _add_argument( self, argument: FnArg ) -> None:
        """
        Adds a user-controllable argument to the plugin.
        See also _add_arg().
        """
        self.__args.append( argument )
    
    
    @protected
    def _add_arg( self, name: str, type, default, description ) -> FnArg:
        """
        Adds a user-controllable argument to the plugin.
        """
        result = FnArg( name, AnnotationInspector( type ), default, description )
        self.__args.append( result )
        return result
    
    
    @override
    def __str__( self ) -> str:
        """
        String representation
        """
        return self.name
    
    
    @override
    def __repr__( self ):
        if self.name.endswith( "help" ):  # TODO: Magic
            return "This is a function named «{0}». Please type '{0}()' to run this function.".format( self.name )
        else:
            return "This is a function named «{0}». Please type '{0}()' to run this function, or type '{0}.help()' for more information.".format( self.name )
    
    
    def help( self ):
        """
        For Python interface - shows the help on this plugin.
        """
        _intermake_internal_show_help( self )
    
    
    @virtual
    def get_description( self ) -> str:
        """
        Description of the executable
        
        Derived classes may override this to provide a dynamic description
        """
        return self.__description
    
    
    def children( self ) -> "List[Plugin]":
        """
        Executables can nest each other if they are related in some way, this is a list of this one's children
        """
        return self.__children
    
    
    def args_to_kwargs( self, *args ):
        """
        Given a set of arguments appearing in the same order as the arguments for this executable, produces
        a kwargs dictionary compatible with Plugin.run(), Plugin.modify(), Plugin.copy() etc.
        """
        result = { }
        
        if not args:
            return result
        
        arg_list = list( self.args )
        
        if len( args ) > len( arg_list ):
            raise KeyError( "Cannot convert a positional argument list of length {0} to a key-value argument list of length {1}.".format( len( args ), len( arg_list ) ) )
        
        for i, v in enumerate( args ):
            if v is not None:
                result[arg_list[i].name] = v
        
        return result
    
    
    def run( self, *args, **kwargs ) -> Optional[object]:
        """
        Finds the host and runs the Plugin.
        
        :param kwargs: Arguments to pass to the plugin. Values specified here override those in args, if provided.
        :return Ignore. This returns the result from the host after being told to execute the plugin (this is NOT the same as the result of the execution).
                    For GuiHost this is normally `None` (because it is async, but could be a wait handle, etc.)
                    For ConsoleHost this is indeed the result (because it actually runs synchronously). Use cautiously.
        """
        argskwargs = ArgsKwargs( *args, **kwargs )
        from intermake.engine.environment import MENV
        return MENV.host.call_virtual_run( self, argskwargs )  # ---> self.call_run()
    
    
    def call_run( self ) -> Optional[object]:
        """
        Called by the host to run the plugin's actual functionality.
        :return: Result of on_run(). 
        """
        try:
            result = self.on_run()
        except PartialSuccess as ex:
            from intermake.engine.environment import MCMD
            MCMD.progress( "The operation has ended early with partial success: {}".format( ex ) )
            return ex.result
        
        return result
    
    
    @abstract
    def on_run( self ) -> Optional[object]:
        """
        Implemented by the derived class, implements the Plugin's main functionality
        
        :return: A plugin specific value.
                 
                 For user-invoked plugins this should generally be something the plugin host (GUI or CLI) can handle.  
                 Types generally handled are:
                    Simple types (`str`, `int`, `float`, `bool`, etc.), that can be displayed to std.out. or in a message-box.
                    `DocketFolder` or `Docket` items, that are created from database queries and can be saved to the user's dockets.
                     
                 For internal plugins, the return type can be any information relayed from one plugin to another.
        """
        raise NotImplementedError( "Abstract" )
    
    
    def set_description( self, value: str ):
        """
        Changes the description() of this plugin.
        """
        self.__description = value
    
    
    def add_child( self, child_plugin: "Union[Plugin, PluginFolder]" ) -> None:
        """
        Adds a "child" plugin (a related plugin)
        """
        child_plugin.__parent = self
        self.__children.append( child_plugin )
    
    
    def remove_child( self, child_plugin: "Union[Plugin, PluginFolder]" ):
        self.__children.remove( child_plugin )
    
    
    def threading( self ) -> EThread:
        """
        Threading model, used by `PluginHost` derivatives to manage threads. See `EThread` for details.
        """
        return self.__threading


class FunctionPlugin( Plugin ):
    """
    A plugin that wraps a function.
    For internal use only (never visible to user).
    """
    
    
    def __init__( self, title: Optional[str], function: Callable[[], object] ):
        super().__init__( names = title, visibility = visibilities.INTERNAL )
        self.__function = function  # type: Callable[ [ ProgressReporter ], object ]
    
    
    def on_run( self ) -> Optional[object]:
        return self.__function()


class SecondaryError( Exception ):
    pass


class __intermake_internal_show_help_type( Plugin ):
    """
    Help (internal)
    """
    
    
    def on_run( self ) -> Optional[object]:
        from intermake.engine import cli_helper
        from intermake.engine.environment import MCMD
        
        command = MCMD.args[self.arg]
        MCMD.print( cli_helper.get_details_text( cast( Plugin, command ) ) )
        return None
    
    
    def __init__( self ) -> None:
        super().__init__( names = type( self ).__name__,
                          description = "Shows help",
                          visibility = visibilities.INTERNAL )
        self.arg = self._add_arg( "plugin", Optional[Plugin], None, "command to show help for" )


_intermake_internal_show_help = __intermake_internal_show_help_type()
