# godot-cli-launcher
CLI written in Python for launching different versions of Godot

This is a tool for easily launching different versions of the Godot game engine and is intended to be flexible and easy to use.

## Syntax
The script exepects either arguments to be passed in, or the script to be given a name tailored to a version of Godot wished.

The script (when not given any version number, release version or whether it is mono or not) will attempt to run the latest, stable, non mono version it can find.

For example in order to run the latest stable version of Godot (`4.2` as of writing), do:
```sh
$ godot.py 4
#... or when specified as a file name
$ godot4
```

### To mono or not to mono
Mono runtime enabled versions can be called for by supplying `mono` as an command line argument or, again, within the file name, prefixed with a dash.
```sh
$ godot.py mono

$ godot3 mono
```

### Extra aguments
any arguments that are not recognized by the script will be carried over to the Godot binary. This can be explicit by specifying `--` in the arguments.

If an argument is not recognized  then all of the remaining arguments (including the encountered argument) will be carried to the Godot binary,
in the case of the `--` argument, the first time it is encountered, it will be excluded from the argument passing.

```sh
# These are equivalent
$ godot.py 4.5.1 rc4 mono -- --help
$ godot.py 4.5.1 rc4 mono --help
```

### Ordering and priority
The order of the arguments do not matter, just as long as they occur before any unrecongized arguments are passed (i.e. `--editor`).

Additionally, the first occurance of a recgonized keyword (such as release version) will take precdence over any that come after.

## Search path
The script will search one directory for binaries. Being which is `$XDG_DATA_HOME/godot-bin`.
