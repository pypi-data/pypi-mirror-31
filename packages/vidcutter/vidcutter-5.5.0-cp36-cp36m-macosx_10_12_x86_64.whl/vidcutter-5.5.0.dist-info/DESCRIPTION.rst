[![Screenshot 3](https://cdn.rawgit.com/ozmartian/vidcutter/gh-pages/images/vidcutter-03-thumb.png)](https://cdn.rawgit.com/ozmartian/vidcutter/gh-pages/images/vidcutter-03.png) 
[![Screenshot 4](https://cdn.rawgit.com/ozmartian/vidcutter/gh-pages/images/vidcutter-04-thumb.png)](https://cdn.rawgit.com/ozmartian/vidcutter/gh-pages/images/vidcutter-04.png)

### VidCutter Flatpak Now Available!

VidCutter will soon be available for installation via Flathub for all you Flatpak enthusiasts out there but a single-file bundle is now available if you don't want to wait for that. Download the Flatpak file from the releases page and open it with your distribution's Software Center app like GNOME / Ubuntu Software, KDE Discover etc..

The recommended install method is via your distribution or desktop environment's software center app which should be configured for Flatpaks. This includes GNOME Software, KDE Discover, Ubuntu Software Center etc. You may need to install a small Flatpak configuration file via your usual package downloading methods in order to support Flatpaks though. Using a software center will keep your app updated with future releases without requiring you to check yourself where as installing via the flatpak terminal command only updates apps when you manually run "flatpak update" yourself.

Click to install via GUI (GNOME Software/KDE Discover etc):

[![Install Flatpak](https://flatpak.org/img/favicon57.png)](https://github.com/ozmartian/vidcutter/releases/download/5.5.0/VidCutter-5.5.0-x64.flatpak)

or install via the terminal:

```
$ wget https://github.com/ozmartian/vidcutter/releases/download/5.5.0/VidCutter-5.5.0-x64.flatpak
$ flatpak install VidCutter-5.5.0-x64.flatpak
```

### VidCutter snap Now Available!

The latest version of VidCutter can now be installed as a snap package via the Ubuntu Snapcraft store at https://snapcraft.io/vidcutter or install it via the terminal as follows:

```
$ snap install vidcutter
```

### Latest DEV Builds Available

Automated deployments from VidCutter CI servers have been setup together with new repos to host the latest builds produced. If you want to check out the very latest DEV builds of VidCutter then follow the links below. Do keep in mind that these are considered unstable so there is a small risk of things not working but care is taken to ensure only complete and working code is pushed to Git, but sometimes mistakes can happen.

&nbsp; | VidCutter DEV Builds |
--- | --- |
**Linux** | https://github.com/ozmartian/vidcutter-appimage/releases/latest |
**Windows** | https://ci.appveyor.com/project/ozmartian/vidcutter/build/artifacts |
**macOS** | https://github.com/ozmartian/vidcutter-osx/releases/latest |

***

### Open Build Service

Prebuilt Linux packages available, click on your distro below.

|[![](https://vidcutter.ozmartians.com/logos/arch.png "Arch Linux")](https://software.opensuse.org/download/package?project=home:ozmartian&package=vidcutter)|  [![](https://vidcutter.ozmartians.com/logos/debian.png)](https://software.opensuse.org/download/package?project=home:ozmartian&package=vidcutter "Debian")|[![](http://vidcutter.ozmartians.com/logos/fedora.png)](https://copr.fedorainfracloud.org/coprs/suspiria/VidCutter "Fedora")|[![](http://vidcutter.ozmartians.com/logos/mageia.png)](https://software.opensuse.org/download/package?project=home:ozmartian&package=vidcutter "Mageia")|[![](http://vidcutter.ozmartians.com/logos/opensuse.png)](https://software.opensuse.org/download/package?project=home:ozmartian&package=vidcutter "openSUSE")|[![](http://vidcutter.ozmartians.com/logos/ubuntu.png)](https://software.opensuse.org/download/package?project=home:ozmartian&package=vidcutter "Ubuntu")
|:---:|:---:|:---:|:---:|:---:|:---:|
|Arch Linux|Debian|Fedora|Mageia|openSUSE|Ubuntu|

***

### Windows + macOS Users

Native installers for Windows and macOS are available on the releases page with every new version, or just click the button below. 

[![Latest Releases](http://tvlinker.ozmartians.com/images/button-latest-release.png)](https://github.com/ozmartian/vidcutter/releases/latest)

#### Homebrew cask

For macOS users of Homebrew, VidCutter can be easily installed as a "cask". With Homebrew already installed, just run the following terminal command:

```
$ brew cask install vidcutter
```

#### Chocolatey package

VidCutter has finally been approved + published in the [Chocolatey](https://chocolatey.org) public repository (its a package manager like in Linux but
for Windows).

  To install VidCutter, run the following command from the command line or from PowerShell:
  ```
  C:\> choco install vidcutter
  ```
  To upgrade VidCutter, run the following command from the command line or from PowerShell:
  ```
  C:\> choco upgrade vidcutter
  ```

***

### Linux Users

#### Arch Linux

Users can install directly from AUR, package is available in both stable and git-latest versions:

    AUR: vidcutter, vidcutter-git

Using an AUR helper like pacaur (replace pacaur with yaourt or other AUR helper):

    LATEST STABLE RELEASE:

        pacaur -S vidcutter

    LATEST DEVELOPMENT RELEASE:

        pacaur -S vidcutter-git

#### Ubuntu/Mint/Debian/KDE Neon and other Ubuntu flavors + derivatives 

Users can install the latest release via:

    ppa:ozmartian/apps

The following set of commands will get you up and running:

    sudo add-apt-repository ppa:ozmartian/apps
    sudo apt update
    sudo apt install vidcutter

#### Fedora

Due to Fedora's restrictive policies on media licensing you'll need to install a VidCutter package from a third-party repository to have all common media formats supported. At the time of writing RPMFusion and UnitedRPMs both contain VidCutter RPMs as well as all the required dependencies so you can simply install the VidCutter RPM package from these sources without needing to do anything else for an up to date version of the app with all common libraries, codecs and formats supported right away.

I also maintain a custom COPR repository at:

    suspiria/VidCutter

I keep this updated myself so it will alwats carry the very latest release version but you will still need to enable one of the third-party repos for the multimedia dependencies. RPMFusion and UnitedRPMs only take a couple of days to update their repos when new versions are released so only bother with COPR if you're "must have the very latest version" type of addict.

Commands for a Fedora install using the COPR repo are:

    sudo dnf copr enable suspiria/VidCutter
    sudo dnf install vidcutter

Check https://copr.fedorainfracloud.org/coprs/suspiria/VidCutter for more detailed instructions on enabling third-party repos for your multimedia dependencies.

#### openSUSE

https://software.opensuse.org/package/vidcutter

VidCutter was recently added to openSUSE Tumbleweed (rolling-build) official repos and should hopefully make its way to release versions in time. 

VidCutter is also available from the always respected Packman third-party repos. Instructions to enable it can be found here:

   https://en.opensuse.org/Additional_package_repositories#Packman

### AppImage

An AppImage portable Linux binary is also available via the releases page for Linux users. AppImages are tested and confirmed to work on most Linux distributions. My personal testing includes Ubuntu (Trusty through to Artful), and current stable releases of  Mint, KDE Neon, Arch Linux, Manjaro, Antergos, Fedora, openSUSE, Debian, and Mageia.

### snap

Available on the Ubuntu Snapcraft store at https://snapcraft.io/vidcutter or install it via the terminal as follows:

```
$ snap install vidcutter
```

### FlatPak

A FlatPak will soon be available via FlatHub for all you GNOME users. In the meantime, the AppImage or snap package should work as an alternative. 

***

### PyPi

If you're familiar with Python and PyPi then you can always try that option too but avoid installing PyQt5 from through pip and instead run with your distributions own PyQt5 offering. PyQt5 is known as some of the following names under various distros: python-pyqt5, python3-pyqt5, python3-qt5 etc. Using your distro's version ensures a more seamless look & feel with the app integrating with your distro's look & feel + widget sets. Installing all via PyPi will still work, but won't look as nice..

If installing via PyPi, be aware to also ensure you have the following tools also installed via your package manager or any other means it doesn't matter so long as they are installed:

    - libmpv (Arch: mpv, Ubuntu: libmpv1, Fedora: mpv-libs via RPMFusion, openSUSE: libmpv1)
    - FFmpeg (ffmpeg in all places, if on older Linux then you may have libav-tools instead which will also work)
    - mediainfo (mediainfo in all/most places. mainly needs to be the CLI version)

Fedora and RedHat users need to enable the RPMFusion repository in order to access mpv packages and just about anything multimedia-wise. Chances are you know what I'm talking about here but if not here are some simple steps to get VidCutter working in Fedora 25, the same should apply for any other RPM based distro... until I get off my lazy butt and try to learn RPM packaging (oh how horrible it looks though).... if anyone wants to help in this area by all means do!

***

## Command-line for debugging (Linux/macOS only)
  ```
  $ vidcutter --help

Usage: vidcutter [options] [video] [project]

VidCutter - the simplest + fastest video cutter & joiner

Options:
  --debug        debug mode; verbose console output & logging. This will
                 basically output what is being logged to file to the console
                 stdout. Mainly useful for debugging problems with your system
                 video and/or audio stack and codec configuration.
  --dev          developer mode; disables the use of compiled resource files so
                 that all app resources & assets are accessed directly from the
                 file system allowing you to see UI changes immediately. this
                 typically relates to changes made to Qt stylesheets (.qss),
                 layout/templates, content includes and images. basically all
                 assets defined in .qrc files throughout the codebase.
  -v, --version  Displays version information.
  -h, --help     Displays this help.

Arguments:
  video          Preload video file
  project        Open VidCutter project file (.vcp)
  ```


