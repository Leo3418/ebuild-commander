#  Docker Abstraction for ebuild-commander
#
#  Copyright (C) 2021-2022 Yuan Liao
#
#  This file is part of ebuild-commander.
#
#  ebuild-commander is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  ebuild-commander is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ebuild-commander.  If not, see
#  <https://www.gnu.org/licenses/>.

import math
import os
import pathlib
import subprocess
import sys

from ebuild_commander.out_fmt import warn, error

_CONTAINER_PORTAGE_CONFIGS_PATH = '/var/tmp/portage-configs'


class Commandocker:
    def __init__(
            self,
            program_name: str,
            container_name: str,
            portage_configs: list[pathlib.Path],
            profile: str,
            gentoo_repo: pathlib.Path,
            custom_repos: list[pathlib.Path],
            num_threads: int,
            emerge_opts: str,
            docker_image: str,
            should_pull_image: bool,
            storage_opt: str,
            docker_cmd: str
    ):
        self._program_name = program_name
        self._container_name = container_name
        self._portage_configs = portage_configs
        self._profile = profile
        self._gentoo_repo = gentoo_repo
        self._custom_repos = custom_repos
        self._emerge_opts = emerge_opts
        self._num_threads = num_threads
        self._docker_image = docker_image
        self._should_pull_image = should_pull_image
        self._storage_opt = storage_opt
        self._docker_cmd = docker_cmd

        self._custom_repo_names = self._get_repo_names()

    def start(self) -> bool:
        """
        Pull the specified Docker image if requested, then initialize and start
        a Docker container, with custom Portage settings applied.

        If image pull failed, the function will continue with any local copy of
        the image, or it will exit with a status indicating the failure if no
        local copy of the image is available.

        This function will return `False` if a container has already been
        started by it and has not been removed.

        :return: whether or not the Docker container is successfully started
        """
        if self._should_pull_image:
            if not self._pull_image():
                print(f"{warn(self._program_name)}: Proceeding with any local "
                      f"copy of image {self._docker_image} -- will exit with "
                      f"failure if the image is not available locally",
                      file=sys.stderr)
        if not self._run_container():
            return False
        self._config_portage()
        return True

    def execute(self, cmd: str, fatal_on_failure: bool = True) -> bool:
        """
        Run a command in the Docker container.  The container must be running.
        The container's standard output and standard error will be redirected
        to this program's standard output and standard error respectively.

        :param cmd: the command to be run
        :param fatal_on_failure: whether a failure to run the command indicates
            a fatal error; used for determining error message format
            (default: `True`)
        :return: whether or not the Docker process exited with a successful
            status
        """
        args = [self._docker_cmd, 'exec', '--interactive',
                self._container_name, '/bin/bash', '-c', cmd]
        try:
            subprocess.run(args, check=True, stdin=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as err:
            if fatal_on_failure:
                program_name = error(self._program_name)
            else:
                program_name = warn(self._program_name)
            print(f"{program_name}: Exit status {err.returncode} encountered "
                  f"during execution of the following command in container "
                  f"{self._container_name}: \n"
                  f"\t{cmd}",
                  file=sys.stderr)
            return False

    def cleanup(self) -> bool:
        """
        Remove the container.  If the container cannot be properly removed,
        `False` will be returned.

        :return: whether or not the Docker container is successfully removed
        """
        try:
            subprocess.run([self._docker_cmd, 'rm', '-f',
                            self._container_name],
                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as err:
            print(f"{error(self._program_name)}: Command {err.cmd} failed "
                  f"with exit status {err.returncode}", file=sys.stderr)
            return False

    def _get_repo_names(self) -> list:
        repo_names = []
        for repo in self._custom_repos:
            try:
                with open(os.path.join(repo, 'profiles', 'repo_name'),
                          "r") as f:
                    for repo_name in f:
                        repo_names.append(repo_name.replace("\n", ""))
            except OSError as err:
                print(f"{warn(self._program_name)}: "
                      f"{err.filename}: {err.strerror}", file=sys.stderr)
        return repo_names

    def _pull_image(self) -> bool:
        try:
            subprocess.run([self._docker_cmd, 'pull', self._docker_image],
                           check=True, stdin=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as err:
            print(f"{warn(self._program_name)}: Command {err.cmd} failed with "
                  f"exit status {err.returncode}", file=sys.stderr)
            return False

    def _run_container(self) -> bool:
        docker_args = [
            self._docker_cmd, 'run', '--detach',
            '--name', self._container_name,
            '--tty',
            '--cap-add', 'CAP_MKNOD',
            '--cap-add', 'CAP_NET_ADMIN',
            '--cap-add', 'CAP_SYS_ADMIN',
            '--cap-add', 'CAP_SYS_PTRACE',
            # Needed on host systems with SELinux enabled
            '--security-opt', 'label=disable',
            # https://github.com/moby/moby/issues/16429
            # Use equal sign instead of colon for compatibility with Podman
            '--security-opt', 'apparmor=unconfined',
            # Needed to build packages like x11-libs/gdk-pixbuf with
            # glibc >=2.34 on GitHub Actions runners as of March 2022
            # https://github.com/actions/virtual-environments/issues/3812
            '--security-opt', 'seccomp=unconfined',
            '--workdir', '/root',
            # Docker needs all paths on the host machine to be absolute ones
            '--volume', f'{self._gentoo_repo.resolve()}:'
                        f'/var/db/repos/gentoo:ro'
        ]

        # Bind each config directory to a path whose base name is the
        # directory's index in the array; pad each index with enough digits to
        # ensure iteration order in Bash shell expansion is desired, or else
        # the iteration order would be like [0, 10, 1, 2, ...]
        num_configs = len(self._portage_configs)
        padding = math.ceil(math.log10(num_configs))
        for i in range(len(self._portage_configs)):
            portage_config = self._portage_configs[i]
            padded_i = f'{i:0{padding}}'
            docker_args.append('--volume')
            docker_args.append(f'{portage_config.resolve()}:'
                               f'{_CONTAINER_PORTAGE_CONFIGS_PATH}/'
                               f'{padded_i}:ro')

        custom_repo_info = zip(self._custom_repos, self._custom_repo_names)
        for repo_path, repo_name in custom_repo_info:
            docker_args.append('--volume')
            docker_args.append(f'{repo_path.resolve()}:'
                               f'/var/db/repos/{repo_name}:ro')

        if self._storage_opt is not None:
            docker_args.append('--storage-opt')
            docker_args.append(self._storage_opt)

        docker_args.append(self._docker_image)
        try:
            subprocess.run(docker_args, check=True,
                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as err:
            print(f"{error(self._program_name)}: Command {err.cmd} failed "
                  f"with exit status {err.returncode}", file=sys.stderr)
            return False

    def _config_portage(self) -> None:
        self._copy_portage_config()
        self._add_comment_to_make_conf()
        self._set_makeopts_num_jobs()
        self._set_emerge_opts()
        self._enable_custom_repos()
        self._set_profile()

    def _copy_portage_config(self) -> None:
        self.execute(f'rm -rf /etc/portage/*',
                     fatal_on_failure=False)
        self.execute(f'for dir in "{_CONTAINER_PORTAGE_CONFIGS_PATH}"/*; do '
                     f'cp -r "$dir"/* /etc/portage; done',
                     fatal_on_failure=False)
        self.execute(f'rm -f /etc/portage/make.profile',
                     fatal_on_failure=False)
        self.execute(f'rm -rf /etc/portage/repos.conf',
                     fatal_on_failure=False)

    def _add_comment_to_make_conf(self) -> None:
        self.execute('echo -e "\\n# Settings added by ebuild-commander" '
                     '>> /etc/portage/make.conf',
                     fatal_on_failure=False)

    def _set_makeopts_num_jobs(self) -> None:
        self.execute('echo \'MAKEOPTS="${MAKEOPTS} '
                     f'-j{self._num_threads}"\' '
                     '>> /etc/portage/make.conf',
                     fatal_on_failure=False)

    def _set_emerge_opts(self) -> None:
        self.execute('echo \'EMERGE_DEFAULT_OPTS="${EMERGE_DEFAULT_OPTS} '
                     f'{self._emerge_opts}"\' '
                     '>> /etc/portage/make.conf',
                     fatal_on_failure=False)

    def _enable_custom_repos(self) -> None:
        self.execute('mkdir /etc/portage/repos.conf', fatal_on_failure=False)
        for repo in self._custom_repo_names:
            self.execute(
                f'echo -e "'
                f'[{repo}]\n'
                f'location = /var/db/repos/{repo}\n'
                f'master = gentoo" > /etc/portage/repos.conf/{repo}.conf',
                fatal_on_failure=False
            )

    def _set_profile(self) -> None:
        self.execute(f'eselect profile set {self._profile}',
                     fatal_on_failure=False)
