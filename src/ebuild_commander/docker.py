#  Docker Abstraction for ebuild-commander
#
#  Copyright (C) 2021 Yuan Liao
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

import os
import pathlib
import subprocess
import sys
import time

import ebuild_commander.utils

from ebuild_commander.out_fmt import warn, error

_CONTAINER_PORTAGE_CONFIG_PATH = '/var/tmp/portage-config'


class Commandocker:
    def __init__(self,
                 program_name: str,
                 portage_config: pathlib.Path,
                 profile: str,
                 gentoo_repo: pathlib.Path,
                 custom_repos: list[pathlib.Path],
                 num_threads: int,
                 emerge_opts: str,
                 docker_image: str,
                 should_pull_image: bool,
                 storage_opt: str):
        self._program_name = program_name
        self._portage_config = portage_config
        self._profile = profile
        self._gentoo_repo = gentoo_repo
        self._custom_repos = custom_repos
        self._emerge_opts = emerge_opts
        self._docker_image = docker_image
        self._num_threads = num_threads
        self._should_pull_image = should_pull_image
        self._storage_opt = storage_opt

        self._custom_repo_names = self._get_repo_names()
        # Use a canonical container name for this instance to avoid the
        # container from being created twice
        self._container_name = f'ebuild-cmder-{time.strftime("%Y%m%d-%H%m%S")}'

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
        if not self._create_container():
            return False
        if not self._start_container():
            return False
        self._config_portage()
        return True

    def execute(self, cmd: str, fatal_on_failure: bool = True) -> bool:
        """
        Run a command in the Docker container.  The container must be running.
        The container's standard output and standard error will be redirected
        to this program's standard output and standard error respectively, but
        standard output can be optionally suppressed.

        :param cmd: the command to be run
        :param fatal_on_failure: whether a failure to run the command indicates
            a fatal error; used for determining error message format
            (default: `True`)
        :return: whether or not the Docker process exited with a successful
            status
        """
        args = ['docker', 'exec', '--interactive', self._container_name,
                '/bin/bash', '-c', cmd]
        try:
            subprocess.run(args, check=True)
            return True
        except subprocess.CalledProcessError as err:
            if fatal_on_failure:
                program_name = error(self._program_name)
            else:
                program_name = warn(self._program_name)
            print(f"{program_name}: Exit status {err.returncode} encountered "
                  f"for execution of following command in Docker container "
                  f"{self._container_name}: \n"
                  f"\t{cmd}",
                  file=sys.stderr)
            return False

    def cleanup(self) -> bool:
        """
        Remove the container.  If the container has already been removed,
        `False` will be returned.

        :return: whether or not the Docker container is successfully removed
        """
        try:
            subprocess.run(['docker', 'kill', self._container_name],
                           stdout=subprocess.DEVNULL)
            subprocess.run(['docker', 'rm', self._container_name],
                           stdout=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as err:
            print(f"{error(self._program_name)}: Command {err.cmd} failed "
                  f"with exit status {err.returncode}")
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
            subprocess.run(['docker', 'pull', self._docker_image], check=True)
            return True
        except subprocess.CalledProcessError as err:
            print(f"{warn(self._program_name)}: Command {err.cmd} failed with "
                  f"exit status {err.returncode}")
            return False

    def _create_container(self) -> bool:
        docker_args = [
            'docker', 'create',
            '--name', self._container_name,
            '--tty',
            '--cap-add', 'CAP_SYS_ADMIN',
            '--cap-add', 'CAP_MKNOD',
            '--cap-add', 'CAP_NET_ADMIN',
            # https://github.com/moby/moby/issues/16429
            '--security-opt', 'apparmor:unconfined',
            '--device', '/dev/fuse',
            '--workdir', '/root',
            '--volume', f'{self._portage_config}:'
                        f'{_CONTAINER_PORTAGE_CONFIG_PATH}:ro',
            '--volume', f'{self._gentoo_repo}:/var/db/repos/gentoo:ro']

        custom_repo_info = zip(self._custom_repos, self._custom_repo_names)
        for repo_path, repo_name in custom_repo_info:
            docker_args.append('--volume')
            docker_args.append(f'{repo_path}:/var/db/repos/{repo_name}:ro')

        if self._storage_opt is not None:
            docker_args.append('--storage-opt')
            docker_args.append(self._storage_opt)

        docker_args.append(self._docker_image)
        try:
            subprocess.run(docker_args, check=True, stdout=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as err:
            print(f"{error(self._program_name)}: Command {err.cmd} failed "
                  f"with exit status {err.returncode}")
            return False

    def _start_container(self) -> bool:
        try:
            subprocess.run(['docker', 'start', self._container_name],
                           check=True, stdout=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as err:
            print(f"{error(self._program_name)}: Command {err.cmd} failed "
                  f"with exit status {err.returncode}")
            return False

    def _config_portage(self) -> None:
        self._copy_portage_config()
        if not self._set_makeopts_num_jobs():
            print(f"{warn(self._program_name)}: Failed to set MAKEOPTS; "
                  f"the original value for this variable will be used",
                  file=sys.stderr)
        self._enable_custom_repos()
        self._set_profile()
        self._set_emerge_opts()

    def _copy_portage_config(self) -> None:
        self.execute(f'rm -r /etc/portage/*', fatal_on_failure=False)
        self.execute(f'cp -r {_CONTAINER_PORTAGE_CONFIG_PATH}/* /etc/portage',
                     fatal_on_failure=False)
        self.execute(f'rm /etc/portage/make.profile', fatal_on_failure=False)
        self.execute(f'rm -r /etc/portage/repos.conf', fatal_on_failure=False)

    def _set_makeopts_num_jobs(self) -> bool:
        try:
            proc = subprocess.run(
                ['docker', 'exec', '--interactive',
                 self._container_name, '/bin/bash', '-c',
                 f'grep --color=never MAKEOPTS= /etc/portage/make.conf'],
                check=True, capture_output=True
            )
        except subprocess.CalledProcessError:
            return False
        orig_makeopts = proc.stdout.decode()
        new_makeopts = ebuild_commander.utils.set_makeopts_num_jobs(
            orig_makeopts, self._num_threads)
        # Appending new MAKEOPTS to make.conf works because when an option is
        # defined more than once, the last definition takes effect
        if new_makeopts.endswith("'"):
            return self.execute(
                f'echo "{new_makeopts}" >> /etc/portage/make.conf')
        else:
            return self.execute(
                f"echo '{new_makeopts}' >> /etc/portage/make.conf")

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

    def _set_emerge_opts(self) -> None:
        self.execute(f'echo \'#!/usr/bin/env bash\n'
                     f'/usr/bin/emerge {self._emerge_opts} "$@"\''
                     f' > /usr/local/bin/emerge', fatal_on_failure=False)
        self.execute('chmod +x /usr/local/bin/emerge', fatal_on_failure=False)
