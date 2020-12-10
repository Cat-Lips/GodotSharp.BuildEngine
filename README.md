# GodotSharp.BuildEngine

Builds Godot Game Engine for Windows with support for C#

## Usage
* Run `Build Editor.bat` to build Godot Editor
* Run `Build Export.bat` to build Export Templates (TODO)

## Notes
* First run will perform a local install of Cygwin so as not to impact current system
  * Mono build requires Windows10+Developer Mode to allow Cygwin to create symbolic links
    * (Activate via Settings->Update & Security->For Developers)
