"""
Contains the `LocalData` class.
"""
import os
import warnings
from os import path
from typing import Optional, TypeVar, cast

from intermake.engine import constants
from mhelper import Logger, PropertySetInfo, SimpleProxy, exception_helper, file_helper, io_helper


__author__ = "Martin Rusilowicz"

T = TypeVar( "T" )

_AUTOSTORE_EXTENSION = ".pickle"

autostore_warnings = []

_LOG = Logger( "autostore", False )


class _AutoStore:
    """
    Manages a local data store, loading and saving the keys to and from files in the specified folder.
    """
    
    
    def __init__( self, directory ):
        """
        CONSTRUCTOR
        :param directory:   Directory to use 
        """
        self.__directory = directory
        self.__cache = { }
        self.__bound = { }
        file_helper.create_directory( directory )
        
        # for file in os.listdir( directory ):
        #     if file.endswith( _AUTOSTORE_EXTENSION ):
        #         key = file_helper.get_filename_without_extension( file )
        #         self.__data[key] = self.__read_item( key )
    
    
    def bind( self, key: str, value: T ) -> T:
        """
        Binds to the specified setting object.
        If any changes have been made on disk, these will be propagated into the `value`.
        
        :param key:         Key to use to get and set the value
        :param value:       Object to wrap in the proxy
                            The `__dict__` is accessed to marshal the attributes, hence this must be a _simple_ object
        :return:            `value`, wrapped in a proxy which detects changes, and commits those changes to disk.
                            Note only attribute changes are registered, not changes to attributes of attributes, etc.
        """
        existing = self.retrieve( key, value )
        
        if existing is None:
            self[key] = value
        else:
            updates = { }
            
            for pk, pv in value.__dict__.items():
                if pk.startswith( "_" ):
                    continue
                
                if pk in existing.__dict__:
                    epv = existing.__dict__[pk]
                    
                    updates[pk] = epv
            
            value.__dict__.update( updates )
            
            self.__cache[key] = value
        
        self.__bound[id( value )] = key
        
        return cast( T, SimpleProxy( source = value, watch = self.__proxy_changed ) )
    
    
    def __proxy_changed( self, e: PropertySetInfo ):
        """
        Responds to a change in a value accessed via `bind`.
        """
        self.commit( e.source )
    
    
    def retrieve( self, key: str, default: object ) -> T:
        """
        Retrieves a setting.
        
        :param key:     Setting key 
        :param default: Default 
        :return:        Setting 
        """
        result = self.__cache.get( key )
        
        if result is None:
            # Not in cache, load from disk
            result = self.__read_item( key, expected_type = type( default ) )
            
            # Apply defaults from `default`
            result = io_helper.default_values( result, default )
            
            # Save to cache
            self.__cache[key] = result
        
        return result
    
    
    def commit( self, key: object ):
        """
        Saves the setting
        
        :param key: Key or bound instance.
        """
        if not isinstance( key, str ):
            key = self.__bound[id( key )]
        
        value = self.__cache.get( key )
        
        if value is None:
            raise ValueError( "Cannot commit a setting because that setting was never retrieved!" )
        
        self.__write_item( key, value )
    
    
    def drop( self, key: str ):
        """
        Removes a setting
        """
        value = self.__cache.get( key )
        
        if value is None:
            raise ValueError( "Cannot delete a setting because that setting was never retrieved!" )
        
        del self.__cache[key]
        self.__write_item( key, None )
    
    
    def __read_item( self, key: str, expected_type ):
        """
        Reads the specified setting from disk.
        """
        file_name = path.join( self.__directory, key + _AUTOSTORE_EXTENSION )
        
        if not path.isfile( file_name ):
            _LOG( "read {} = absent", key )
            return None
        
        try:
            result = io_helper.load_binary( file_name, type_ = expected_type )
            _LOG( "read {} = success", key )
        except Exception as ex:
            # Data cannot be restored - ignore it
            autostore_warnings.append( exception_helper.get_traceback() )
            _LOG( "read {} = failure", key )
            file_helper.recycle_file( file_name )
            warnings.warn( "Failed to restore settings from «{}» due to the error «{}: {}». This is probably due to a version incompatibility, if so please recreate your settings using the new version and disregard this warning. Otherwise, use the `autostore_warnings` function to obtain the full error traceback. The problematic file has been automatically sent to the recycle bin to avoid this problem in future. If it is important, please retrieve it now.".format( file_name, type( ex ).__name__, ex ), UserWarning )
            return None
        
        return result
    
    
    def __write_item( self, key: str, value: Optional[object] ) -> None:
        """
        Saves the settings to disk
        """
        file_name = path.join( self.__directory, key + _AUTOSTORE_EXTENSION )
        
        if value is not None:
            _LOG( "write {}", key )
            io_helper.save_binary( file_name, value )
        else:
            _LOG( "delete {}", key )
            os.remove( file_name )
    
    
    def __contains__( self, key ):
        """
        Returns if the specified setting exists.
        """
        return key in self.__cache
    
    
    def keys( self ):
        """
        Returns saved settings
        """
        return self.__cache.keys()
    
    
    def cached( self, key: str ) -> object:
        """
        Retrieves an item from the cache.
        """
        return self.__cache[key]
    
    
    def get( self, settings_key, default_value ):
        warnings.warn( "Deprecated, use retrieve", DeprecationWarning )
        return self.retrieve( settings_key, default_value )
    
    
    def get_and_init( self, settings_key: str, default_value: T ) -> T:
        warnings.warn( "Deprecated, use retrieve", DeprecationWarning )
        return self.retrieve( settings_key, default_value )


class NotReadyError( Exception ):
    pass


class LocalData:
    """
    Manages $(APPNAME)'s primary working directory, usually "~/$(ABVNAME)-data" (UNIX) or "%user%/$(ABVNAME)-data" (Windows).
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self.__workspace: Optional[str] = None
        self.__workspace_in_use: bool = False
        self.__store: _AutoStore = None
    
    
    def get_workspace( self ) -> str:
        """
        Obtains the workspace folder.
        Once this is called, `set_workspace` no longer functions.
        """
        if self.__workspace is None:
            self.set_workspace( None )
        
        self.__workspace_in_use = True
        
        assert isinstance( self.__workspace, str )
        return self.__workspace
    
    
    def set_workspace( self, value: Optional[str] ) -> None:
        """
        Overrides the default workspace folder.
        This can only be done before settings, etc. are loaded and saved.
        To set the workspace permanently, `set_redirect` should be called instead.
        
        Nb. If this is set to `None` the default workspace or redirection is used.
        
        :param value:   New workspace. You can use "~" for the user's home directory. 
        """
        if self.__workspace_in_use:
            raise ValueError( "Cannot change the workspace to «{}» because the existing workspace «{}» is already in use.".format( value, self.__workspace ) )
        
        # Working folder
        if value is None:
            value = self.get_redirect() or self.default_workspace()
        else:
            value = value
        
        if not value or path.sep not in value:
            raise ValueError( "A complete workspace path is required, «{}» is not valid.".format( self.__workspace ) )
        
        if "~" in value:
            value = path.expanduser( value )
        
        self.__workspace = value
    
    
    def set_redirect( self, content: Optional[str] ) -> None:
        """
        Sets or clears the workspace redirection.
        """
        r = self.__get_redirect_file_name()
        
        if content:
            file_helper.write_all_text( r, content )
        else:
            file_helper.delete_file( r )
    
    
    def get_redirect( self ) -> Optional[str]:
        """
        Gets the current redirection.
        """
        redirect = self.__get_redirect_file_name()
        
        if path.isfile( redirect ):
            return file_helper.read_all_text( redirect ).strip()
        else:
            return None
    
    
    @classmethod
    def default_workspace( cls ) -> str:
        from intermake.engine.environment import MENV
        abv = MENV.abv_name
        
        if not LocalData.is_ready():
            raise NotReadyError(
                    "Attempt to the obtain default workspace without setting the application name."
                    + " Possible cause: The programmer has attempted to get or set an application setting stored in the local data store before setting the application name."
                    + " Maybe they tried to register plugins setting before calling MENV.configure?"
                    + " Make sure MENV.configure is called before importing the plugins in the package's __init__.py." )
        
        return path.join( "~", ".intermake-data", abv.lower() )
    
    
    @staticmethod
    def is_ready():
        from intermake.engine.environment import MENV
        return MENV.abv_name != constants.DEFAULT_NAME
    
    
    @property
    def store( self ) -> _AutoStore:
        """
        Obtains the settings store.
        """
        if self.__store is None:
            self.__store = _AutoStore( self.local_folder( constants.FOLDER_SETTINGS ) )
        
        # noinspection PyTypeChecker
        return self.__store
    
    
    @classmethod
    def __get_redirect_file_name( cls ) -> str:
        """
        Obtains the name of the file used to redirect the default workspace.
        """
        return cls.default_workspace() + ".dir"
    
    
    def local_folder( self, name: str ) -> str:
        """
        Obtains a folder in the workspace. See `intermake.engine.constants.FOLDER_*` for suggested defaults.
        """
        folder_name = path.join( self.get_workspace(), name )
        file_helper.create_directory( folder_name )
        return folder_name
