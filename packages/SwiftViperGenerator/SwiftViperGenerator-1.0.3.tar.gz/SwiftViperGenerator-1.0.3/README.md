# SWIFT VIPER GENERATOR aka SWIVIGEN

## Installation

Requirements:
* python3
* pip3
* XCode that supports recent versions of Swift

To install run 
`pip3 install SwiftViperGenerator`

## Usage

`usage: swivigen [-h] [--init] [-c CONFIG] [-m] [-s STORYBOARD]
                [-t TARGETS [TARGETS ...]]
                project module`

* `project` is XCode project that should be modified (specify with .xcodeproj extension)
* `module` is name for new VIPER module, for example, Login or Options
* ` -h` or ` --help` will show help (actually this paragraph)
* `--init` will add base swivigen Swift files into project
* `-c` or `--config` is path to YAML config file; if not specified, swivigen will try to use viper.yml file in current folder
* `-m`, `--makedirs` will create needed folders inside project directory (Views, Interactors, Presenters, Routers, Controllers)
* `-s`,`--storyboard` specifies name of storyboard where newly created view controller will be placed by user
* `-t`, `--targets` specifies list of targets where created files will be included; if not specified, all targets will include new files

## Config file

YAML config file has next structure:

	project_dir: PROJECT_DIR
	templates_dir: TEMPLATES_DIR
	uikit_controllers_group: XCODEPROJ_GROUP
	author: AUTHOR
	targets: [TARGETS_LIST]

where
* PROJECT_DIR is a directory of project that should be used (useful in case it has different name with project itself); should be relative to project file e.g. `ProjectFolder` but not `./ProjectFolder`
* TEMPLATES_DIR is a directory with Swift templates; type `$TEMPLATES` to use swivigen default templates
* XCODEPROJ_GROUP is project group under which generated ViewControllers should be stored
* AUTHOR is a name of project developer or maintainer to use in docucomments
* TARGETS_LIST is a list of targets in which created files will be included; this value will be overwritten by list provided with `-t` cli option

### Note

Sometimes XCode project should be re-opened for changes to take place.

## Structure

swivigen has common files that should be present in project that should use generated sources. You can add common files into project by specifying `--init` option while calling swivigen.

After you run tool with desired module name, you will have router, interactor, presenter and view classes named after that module inside your project (entities currently are not covered). Feel free to rearrange them inside project if you need.\
Also you will have ViewController that is inherited from ViperController that is basically subclass of UIViewController with minor enhancements. You can connect this ViewController with XIB or Storyboard.

Basic example of usage of these classes will come soon.

## License 

MIT License

## Contact

bogdanivanov at live.com
