# Debugging a Unity Play Mode session in VS Code

Open the **`DeFurnius/`** folder in VS Code (the folder with `Assets/`, `Packages/` and `ProjectSettings/`), not the
repo root. The `.vscode/` config lives there. Unity and VS Code both run on your normal desktop, not in the Virgil container.

## One-time setup

1. **Install the extensions.** VS Code will offer them from `.vscode/extensions.json`. You need
   **Unity** (`visualstudiotoolsforunity.vstuc`); **C# Dev Kit** comes with it. The project already has the
   `com.unity.ide.visualstudio` package (2.0.27), which is what Unity uses to talk to VS Code.
2. **Tell Unity to use VS Code.** In Unity: *Edit > Preferences > External Tools > External Script Editor* and pick
   **Visual Studio Code**. This is a per-user setting, so it is not stored in the repo.
3. **Generate project files.** On the same page, press **Regenerate project files** (with nothing checked
   except what you normally use). This creates `DeFurnius.sln` and the `.csproj` files, which are git-ignored.
4. Leave **Editor Attaching** ticked on that page so the debugger is allowed to connect.

## Each debugging session

1. In Unity, open a script with a double-click (or *Assets > Open C# Project*) so VS Code opens the right folder.
2. Set a breakpoint by clicking in the gutter.
3. In VS Code, press **F5** (or *Run and Debug > Attach to Unity*). If several Unity instances are running, pick this
   project from the list.
4. In Unity, press **Play**. Execution stops on your breakpoint and you can use the usual VS Code controls (step over,
   step into, watch, call stack, debug console, conditional breakpoints and logpoints).
5. Detach with the red square in the debug toolbar. Unity keeps running.

## Things that commonly go wrong

- **Breakpoints are hollow / "unbound".** Unity has not loaded your latest compile. Let it finish recompiling (spinner
  bottom right), then re-attach. Also check the Editor's **Code Optimization** is in **Debug** mode (button in the
  bottom-right status bar, or *Edit > Preferences > External Tools*); Release mode inlines code and skips breakpoints.
- **"Attach" shows nothing.** Unity is not running, or the project is not open in it, or Editor Attaching is off.
- **Play Mode options.** This project has *Enter Play Mode Options* enabled in `ProjectSettings/EditorSettings.asset`
  (`m_EnterPlayModeOptionsEnabled: 1`). Debugging works either way, but with **Reload Domain** off, static fields keep
  their values between Play sessions, which can look like a bug in the debugger.
- **Optimisation in packages.** You can only step into your own scripts and packages that ship source. Unity engine
  code appears as decompiled or metadata-only.

## Debugging a built player instead of the Editor

1. *File > Build Profiles* (or *Build Settings*): tick **Development Build** and **Script Debugging**, optionally
   **Wait For Managed Debugger** so the player pauses at startup until you attach.
2. Build and run it on the same network (or machine).
3. In VS Code, press F5 on **Attach to Unity** and choose the player from the list.

IL2CPP players need the same two checkboxes; managed debugging over the network also needs the firewall to allow Unity.

## What is in `DeFurnius/.vscode/`

| File | Purpose |
| --- | --- |
| `launch.json` | The **Attach to Unity** configuration (`type: vstuc`). |
| `extensions.json` | Recommends the Unity and C# extensions. |
| `settings.json` | Points C# Dev Kit at `DeFurnius.sln` and keeps `Library/`, `Temp/` and `Logs/` out of search and file watching. |

None of this runs by itself. VS Code only uses it when you open the folder or press F5.

*Not tested:* Virgil wrote this in a container with no Unity or VS Code, from the extension's documented setup.
If a step differs on your machine (the extension has been renamed and re-versioned before), say so and I will correct it.
