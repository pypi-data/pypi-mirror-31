import sys
import threading
import intermake
from typing import Optional, cast
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QProxyStyle, QStyle
from intermake import Result, EDisplay, EThread, MENV, Mandate, IProgressReceiver, QueryInfo, TaskCancelledError, UpdateInfo, ERunMode, PluginHost, RunHost, Plugin, EStream, Message
from mhelper import Logger, SwitchError, ansi_format_helper, override, string_helper, virtual, ArgsKwargs, exception_helper

from intermake_qt.forms.frm_maintenance import FrmMaintenance
from intermake_qt.utilities.interfaces import IGuiPluginHostWindow


__author__ = "Martin Rusilowicz"

_SIGLOG = Logger( "gui host signals" )


class _FnWrapper:
    """
    Wraps a function, we need to do this because QT won't let us send raw functions across threads, but we can send an object that behaves like a function.
    """
    
    
    def __init__( self, fn ) -> None:
        self.__fn = fn
    
    
    def __call__( self, *args, **kwargs ) -> Optional[object]:
        return self.__fn( *args, **kwargs )
    
    
    def __str__( self ) -> str:
        return str( self.__fn )


class BrowserInvoke:
    """
    If a plugin returns this, the host runs it in the browser.
    This should be used if the host replies `True` to `has_form`.
    """
    
    
    def __init__( self, cypher: str ) -> None:
        self.cypher = cypher


class _GuiHostSettings:
    """
    :attr number_of_threads: Number of threads to use in plugins supporting multi-threading.
    :attr gui_auto_close_progress: Automatically close the progress dialogue.
    :attr gui_css: CSS stylesheet. Takes a full path or a name of an Intermake style sheet (with or without the `.css` extension). If not specified uses `main.css`.
    :attr gui_auto_scroll_progress: GUI option
    :attr gui_progress_display: GUI option 
    """
    
    
    def __init__( self ) -> None:
        super().__init__()
        self.number_of_threads = 1
        self.gui_auto_close_progress = True
        self.gui_auto_scroll_progress = True
        self.gui_progress_display = EDisplay.TIME_REMAINING
        self.gui_css = ""


class CreateWindowArgs:
    def __init__( self, can_return_to_cli: bool ):
        self.can_return_to_cli = can_return_to_cli


class _NullReceiver( IProgressReceiver ):
    def progress_update( self, info: UpdateInfo ) -> None:
        pass
    
    
    def was_cancelled( self ) -> bool:
        return False
    
    
    def question( self, query: QueryInfo ) -> Optional[object]:
        raise ValueError( "Cannot question the user when a plugin is being run in the main thread! The main thread is already being used to host the GUI." )


class GuiHost( PluginHost ):
    """
    Manages a set of asynchronous workers and their progress dialogue
    
    :attr __settings:       These settings used by the GUI which can be configured by the user through the `set` command.
    :attr __owner_window:   The main window
    :attr __beehives:       Each plugin gets its own "bee hive", which manages the threads ("busy bees") for that plugin.
    :attr thread_local:     Thread-local data store. Each thread gets its own version of this, including the main thread.
    :attr thread_local.tag_receiver:     The progress receiver for a particular thread.
    :attr thread_local.tag_mandate:      The stack of plugins called on a particular thread.
    :attr __base_mandate:   This is the mandate used at the bottom of the main thread, when no plugins are running this is what `MCMD` returns. 
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        super().__init__()
        self.__settings: _GuiHostSettings = None
        self.__owner_window = cast( IGuiPluginHostWindow, None )
        self.__beehives = []
        self.thread_local = threading.local()
        self.thread_local.tag_receiver = _NullReceiver()
        self.__base_mandate = Mandate( self, None, None, self.thread_local.tag_receiver, "Base" )
        self.thread_local.tag_mandate = [self.__base_mandate]
        
        threading.currentThread().name = "main_intermake_gui_thread"
    
    
    def _is_cli( self ):
        return False
    
    
    def register_thread( self, mandate: Mandate ):
        if hasattr( self.thread_local, "tag_mandate" ):
            raise ValueError( "Attempt to register a thread with the GuiHost but that thread has already been registered. This is probably an error." )
        
        self.thread_local.tag_receiver = mandate._get_receiver()
        self.thread_local.tag_mandate = [mandate]
    
    
    def __str__( self ) -> str:
        return "GuiHost(QT)"
    
    
    def translate_name( self, name: str ) -> str:
        return string_helper.capitalise_first_and_fix( name, "_-." )
    
    
    def _PLUGINHOST_get_run_mode( self ) -> ERunMode:
        return ERunMode.GUI
    
    
    @override
    def get_mandate( self ) -> Mandate:
        """
        Obtains the mandate, stored in the thread-local pool for the plugin
        This doesn't work for unmanaged plugins, they need to take the mandate as a parameter.
        :return: 
        """
        try:
            return self.thread_local.tag_mandate[-1]
        except AttributeError as ex:
            raise ValueError( "Attempt to get the mandate from a thread «{}» that is neither the main thread nor a thread running a plugin.".format( threading.currentThread().name ) ) from ex
    
    
    def on_get_help_message( self ) -> str:
        return """
            You are in GUI mode.
            Double-click plugins to run them.
            Try running the sample `eggs` plugin, which can be found in the `Default/Commands` folder."""
    
    
    def __is_in_plugin( self ):
        return self.thread_local.tag_mandate[0] is not self.__base_mandate
    
    
    @virtual
    def on_create_window( self, args: CreateWindowArgs ):
        from intermake_qt.forms.frm_intermake_main import FrmIntermakeMain
        frm_main = FrmIntermakeMain( args.can_return_to_cli )
        return frm_main
    
    
    @override
    def on_run_host( self, args: RunHost ) -> None:
        """
        Helper function to start the GUI
        """
        # Unfortunate notice: If the GUI fails to initialise with a segmentation fault this is probably a bad QT
        # installation. The user will need to reinstall QT/PyQt5. TODO: Detect this scenario and inform the user.
        from intermake.engine import cli_helper
        print( cli_helper.format_banner( "GUI-Frontend. The GUI is now active. Input will not be accepted in this terminal until the GUI completes.", None, None ) )
        
        import sys
        from PyQt5.QtWidgets import QApplication
        
        # Read the CSS
        from intermake_qt.utilities import intermake_gui
        style = intermake_gui.parse_style_sheet().get( 'QApplication.style', "" )
        small_icon_size = int( intermake_gui.parse_style_sheet().get( 'QApplication.smallIconSize', "16" ) )
        
        # Start the GUI
        if style:
            QApplication.setStyle( ProxyStyle( style, small_icon_size ) )
        
        app = QApplication( sys.argv )
        app.setStyleSheet( intermake_gui.default_style_sheet() )
        main_window = self.on_create_window( CreateWindowArgs( can_return_to_cli = args.can_return ) )
        self.set_window( main_window )
        main_window.show()
        
        app.exec_()
        print (  intermake.constants.INFOLINE_SYSTEM+"The GUI has closed." )
        
        if not main_window.return_to_console():
            args.exit = True
    
    
    def set_window( self, window: IGuiPluginHostWindow ):
        self.__owner_window = window
    
    
    @property
    def gui_settings( self ) -> _GuiHostSettings:
        if self.__settings is None:
            self.__settings = MENV.local_data.store.bind( "gui", _GuiHostSettings() )
        
        # noinspection PyTypeChecker
        return self.__settings
    
    
    @override
    def call_virtual_run( self, plugin: Plugin, args: ArgsKwargs ) -> Optional[object]:
        """
        IMPLEMENTATION
        """
        if self.__is_in_plugin() or plugin.threading() == EThread.UNMANAGED:
            return self.__invoke_unmanaged( plugin, args )
        elif plugin.threading() == EThread.SINGLE:
            self.__invoke_threaded( plugin, args, 1 )
            return None
        elif plugin.threading() == EThread.MULTI:
            self.__invoke_threaded( plugin, args, self.settings.number_of_threads )
            return None
        else:
            raise SwitchError( "plugin.threading( )", plugin.threading() )
    
    
    def __invoke_unmanaged( self, plugin: Plugin, args: ArgsKwargs ) -> Optional[object]:
        self.thread_local.tag_mandate.append( Mandate( self, plugin, args, self.thread_local.tag_receiver, plugin.name ) )
        
        async_result = None
        
        try:
            result = plugin.call_run()
            async_result = Result( plugin.name, result, None, exception_helper.get_traceback(), None, plugin )
            return result
        except Exception as ex:
            async_result = Result( plugin.name, None, ex, exception_helper.get_traceback(), None, plugin )
            raise
        finally:
            self.thread_local.tag_mandate.pop()
            
            if not self.__is_in_plugin():  # don't callback to the main thread if we are in another plugin's thread
                self.__owner_window.plugin_completed( async_result )
    
    
    def __invoke_threaded( self, plugin: Plugin, args: ArgsKwargs, num_threads: int ) -> None:
        self.__beehives.append( self.__BeeHive( self, self.__owner_window, plugin, args, num_threads ) )
    
    
    @override
    def set_last_result( self, result ):
        super().set_last_result( result )
        self.__owner_window.plugin_completed( result )
    
    
    class __BeeHive:
        def __init__( self, host, window, plugin: Plugin, args: ArgsKwargs, num_threads: int ):
            if window is None:
                raise ValueError( "__BeeHive expects a Window." )
            
            self._dialogue = FrmMaintenance( window, MENV.host.translate_name( plugin.name ) )
            self._dialogue.setModal( True )
            self._dialogue.show()
            
            self._host = host
            self.__plugin = plugin
            
            self.__bees = set()
            
            for i in range( num_threads ):
                try:
                    bee = self.__BusyBee( self, plugin, args, self._dialogue, i, num_threads )
                    bee.start()
                    self.__bees.add( bee )
                except Exception as ex:
                    # Bee failed to start
                    self.bee_finished( None, Result( str( plugin ), None, ex, exception_helper.get_traceback(), [Message( "Worker thread failed to start.", EStream.PROGRESS )], plugin ) )
        
        
        def bee_finished( self, bee: "__BusyBee", result: Result ) -> None:
            """
            Called when a thread finishes (back in the main thread)
            """
            if bee is not None:
                self.__bees.remove( bee )
            
            if self.__bees:
                return
            
            # Close the dialogue
            self._dialogue.worker_finished( result )
            
            # Tell the caller we are done (they only get the last result)
            self._host.set_last_result( result )
        
        
        class __BusyBee( QThread, IProgressReceiver ):
            """
            Actual thread
            """
            __callback = pyqtSignal( _FnWrapper )
            
            
            @override  # IProgressReceiver
            def was_cancelled( self ) -> bool:
                return self.__dialogue.was_cancelled()
            
            
            @override  # IProgressReceiver
            def question( self, query: QueryInfo ) -> Optional[object]:
                raise NotImplementedError( "This feature (question user) has not been implemented in the GUI, please run in the CLI." )  # TODO!!!
            
            
            @override  # IProgressReceiver
            def progress_update( self, info ) -> None:
                self.invoke_in_main_thread( lambda: self.__dialogue.worker_update( info ) )
            
            
            def __init__( self, hive: "GuiHost.__BeeHive", plugin: Plugin, args: ArgsKwargs, dialogue, my_index, num_threads ):  # MAIN
                """
                Creates the thread object
                """
                QThread.__init__( self )
                
                self.__callback.connect( self.__invoke_returned )
                
                self.__args = args
                self.__plugin = plugin  # type: Plugin
                
                self.__dialogue = dialogue
                
                self.__result = None  # type:Optional[object]
                self.__exception = None  # type:Optional[Exception]
                self.__exception_trace = None  # type: Optional[str]
                
                self.__was_cancelled = False
                self.__hive = hive
                
                self.__mandate = Mandate( self.__hive._host, self.__plugin, self.__args, self, plugin.name, my_index, num_threads, 0.2 )
            
            
            @override  # QThread
            def run( self ) -> None:  # WORKER
                """
                QThread Implementation
                """
                
                threading.currentThread().name = "intermake_busybee_{}_hive_{}_running_{}".format( id( self ), id( self.__hive ), self.__plugin.name.replace( " ", "_" ) )
                
                try:
                    self.__hive._host.thread_local.tag_mandate = [self.__mandate]
                    self.__hive._host.thread_local.tag_receiver = self
                    true_result = self.__plugin.call_run()
                    result = Result( self.__plugin.name, true_result, None, None, self.__mandate.get_message_records(), self.__plugin )
                except TaskCancelledError as ex:
                    result = Result( self.__plugin.name, None, ex, exception_helper.get_traceback(), self.__mandate.get_message_records(), self.__plugin )
                except Exception as ex:
                    result = Result( self.__plugin.name, None, ex, exception_helper.get_traceback(), self.__mandate.get_message_records(), self.__plugin )
                    
                    # Print a message for the debugger
                    print( "EXCEPTION IN __BusyBee.run:", file = sys.stderr )
                    print( ansi_format_helper.format_traceback( ex ), file = sys.stderr )
                
                self.invoke_in_main_thread( lambda: self.__hive.bee_finished( self, result ) )
            
            
            def invoke_in_main_thread( self, where ) -> None:  # WORKER
                """
                Calls "where" back in the main thread
                """
                where = _FnWrapper( where )
                _SIGLOG( "S __invoke_emit --> {}".format( where ) )
                self.__callback.emit( where )  # --> MAIN (via signal)
                _SIGLOG( "E __invoke_emit --> {}".format( where ) )
            
            
            @staticmethod
            def __invoke_returned( where ) -> None:  # <- MAIN (via signal)
                """
                The callback from invoke_in_main_thread - just calls "where".
                """
                _SIGLOG( "S __invoke_returned --> {}".format( where ) )
                where()
                _SIGLOG( "E __invoke_returned --> {}".format( where ) )
    
    
    @override
    def has_form( self ):
        return True
    
    
    @override
    def get_form( self ):
        return self.__owner_window


class ProxyStyle( QProxyStyle ):
    def __init__( self, style: Optional[str], small_icon_size: int ):
        if style != "default":
            super().__init__( style )
        else:
            super().__init__()
        
        self.__small_icon_size = small_icon_size
    
    
    def pixelMetric( self, QStyle_PixelMetric, option = None, widget = None ):
        if QStyle_PixelMetric == QStyle.PM_SmallIconSize:
            return self.__small_icon_size
        else:
            return QProxyStyle.pixelMetric( self, QStyle_PixelMetric, option, widget )
