# Wheelie
- Convert to sh? (and support for non python session)
- Use env variables instead of arguments for calling Ravage

# Ravage
- Multithreaded execution of commands
- Spawning shell sessions
- Support when python is not installed
- Pivoting between users (including when root is obtained) - another executable file in path dir?
- Freezing iptables

## Config file
- Stealth mode (random location, communicates periodically, obfuscuated code, set time created/modified) - http://blog.ablepear.com/2012/10/bundling-python-files-into-stand-alone.html
- Automatic commands/scripts on startup, when lost connection to C2 centre, at regular intervals or keep alive ones, match via username
- Persistance via cron jobs, compiled binaries, .bashrc etc. All in different locations (aggresive mode)

# Soundwave
- Filewatcher for script dir
- Better results management and archiving (including for different users)
- GUI?
