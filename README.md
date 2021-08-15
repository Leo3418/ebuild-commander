# ebuild-commander

ebuild-commander is a tool designed for installation tests of
[ebuilds][gentoo-wiki-ebuild] on Gentoo.  Inspired by
[ebuildtester][ebuildtester], ebuild-commander tests ebuilds in a
[Docker][docker] container derived from [Gentoo stage3
images][docker-gentoo-stage3] but allows for finer granularity of control over
the tests:

- Instead of taking merely a single [package atom][gentoo-wiki-ver-spec],
  ebuild-commander accepts a list of shell commands that need to be executed
  during the test.  It is still possible to install a single package with
  `emerge`, but multiple packages can be installed together in either one or
  many `emerge` invocations.  Other commands, like `cp`, `rm`, etc., can also
  be run similarly.

- ebuild-commander supports full Portage configuration customization.  It can
  use the contents of one or multiple directories on the host machine's file
  system as the contents of `/etc/portage` in the Docker container used for the
  test.  `package.accept_keywords`, `package.env`, `env` and `package.use` can
  all be fully customized with this method.

- ebuild-commander supports any alternative container engine whose command-line
  interface is compatible with Docker (e.g. [Podman][podman]).  Alternative
  container engines may have advantages over Docker, like the ability to use
  containers with a non-root user account.

[gentoo-wiki-ebuild]: https://wiki.gentoo.org/wiki/Ebuild
[ebuildtester]: https://github.com/nicolasbock/ebuildtester
[docker]: https://docs.docker.com/get-started/overview/
[docker-gentoo-stage3]: https://hub.docker.com/r/gentoo/stage3
[gentoo-wiki-ver-spec]: https://wiki.gentoo.org/wiki/Version_specifier
[podman]: http://docs.podman.io/en/latest/

## Usage

### Basics

The main executable of ebuild-commander is `ebuild-cmder`, which can read the
list of commands to execute for a test from files and/or standard input.  For
example, this command can be used to install a single package
`sys-apps/portage` using `emerge` for a test:

```console
# ebuild-cmder <<< "emerge sys-apps/portage"
```

Note: ebuild-commander may invoke Docker commands like `docker create`, `docker
start` and `docker exec` directly, so any user account used to run the
`ebuild-cmder` command should have the permission to run those Docker commands.
By default, those Docker commands can only be executed using `root`, so
`ebuild-cmder` should also be started with `root`.  However, under any of these
circumstances, `ebuild-cmder` can be run with a non-root user account:

- The non-root account is in the `docker` group.
- The Docker daemon is running in the [rootless mode][docker-rootless].
- An alternative container engine that does not require `root` privileges, like
  Podman, is used (see a section down below for more details).
- A command-line option which causes ebuild-commander to not interact with
  Docker, like `--help` and `--version`, is set.

[docker-rootless]: https://docs.docker.com/engine/security/rootless/

### Using Multiple `emerge` Commands

Some packages' installation may require multiple `emerge` commands for
bootstrapping, breaking circular dependencies, or other purposes.  For example,
`media-libs/freetype-2.10.4[harfbuzz]` requires
`media-libs/harfbuzz[truetype]`, but `media-libs/harfbuzz-2.8.1[truetype]`
depends on `media-libs/freetype`, producing a circular dependency.  To install
`media-libs/freetype[harfbuzz]`, two `emerge` invocations are needed: the first
one builds `media-libs/freetype` with the `harfbuzz` USE flag disabled, and the
second one rebuilds it with `USE="harfbuzz"`.

For situations like this, ebuild-commander supports running more than one
command in a Docker container.  Commands should be separated by a newline, such
as:

```console
# cat << _EOC_ | ebuild-cmder
> emerge media-libs/freetype
> env USE="harfbuzz" emerge media-libs/freetype
> _EOC_
```

### Customizing Portage Configuration

ebuild-commander has a `--portage-config` option for specifying directories
containing Portage configuration files that should be used during the test.
This option can be set any arbitrary number of times:

- If this option is not used at all, then the contents of `/etc/portage` on the
  host machine's file system will be used as the Portage configuration for the
  test.

- If this option is set exactly once, then the contents of the directory at the
  path specified by the option's value will be used as the Portage
  configuration for the test.

- If this option is set more than once, then all specified directories will be
  used to form a layered Portage configuration.  ebuild-commander will copy the
  contents of each directory into `/etc/portage` in the Docker container used
  for the test, in the same order as how they are listed in the command-line
  arguments.

Note: `make.profile` and `repos.conf` will always be ignored.  `make.profile`
can be controlled with the `--profile` option of `ebuild-cmder`.  `repos.conf`
is automatically populated by ebuild-commander according to the settings for
the `--gentoo-repo` and `--custom-repo` options.

### Using an Alternative Container Engine

ebuild-commander uses Docker as the default container engine and thus calls the
`docker` executable for container operations and other Docker functionalities.
However, any container engine which provides a command-line interface that is
equivalent to Docker's can be used with ebuild-commander.

To specify an alternative container engine, please set the value of environment
variable `EBUILD_CMDER_DOCKER` to the name of the container engine's main
executable.  For example, the following command runs ebuild-commander with
Podman, whose executable is called `podman`:

```console
$ env EBUILD_CMDER_DOCKER="podman" ebuild-cmder
```

### More Information

For a comprehensive list of command-line arguments recognized by
ebuild-commander, please refer to the output of command `ebuild-cmder --help`.

## Dependencies

- Python 3.9 or above
- Any container engine whose command-line interface is compatible with Docker,
  including but not limited to:
  - Docker
  - Podman (requires environment variable setting
    `EBUILD_CMDER_DOCKER="podman"`)

## Installation

The ebuild-commander project employs setuptools as the build automation tool
and has a `setup.py` script for building and installing this project, just like
many other Python projects.

All of the following commands assume that the working directory is the root of
ebuild-commander's source tree.

- To build this project, please run `./setup.py build`.

- To install ebuild-commander only for the current user, please run `./setup.py
  install --user`.

- To install ebuild-commander to the system globally so every user can use it,
  please run `./setup.py install` as `root`.

- For more information about using `setup.py`, please run `./setup.py --help`.

## Testing

The ebuild-commander project uses [tox][tox] as the test runner.  To launch
tests, please run command `tox` from any directory under this project's source
tree.

[tox]: https://tox.readthedocs.io/en/latest/
