"""
Repository module

Contains the add-ons repository representation / configuration
and handles the automated maintenance / updating of it.
"""
import os
import shutil
import sys
import tempfile
from typing import List

import click
import crayons
import yaml
from git import Repo
from github.GithubException import UnknownObjectException
from github.Repository import Repository as GitHubRepository
from jinja2 import Environment, FileSystemLoader

from .addon import Addon
from .const import CHANNELS
from .github import GitHub


class Repository:
    """Represents an Hass.io add-ons repository"""
    addons: List[Addon]
    github: GitHub
    github_repository: GitHubRepository
    git_repo: Repo
    force: bool

    def __init__(self, github: GitHub, repository: str, addon: str,
                 force: bool):
        """"Initialize new add-on Repository object"""
        self.github = github
        self.force = force
        self.addons = []

        click.echo(
            'Locating add-on repository "%s"...' % crayons.yellow(repository),
            nl=False)
        self.github_repository = github.get_repo(repository)
        click.echo(crayons.green('Found!'))

        self.clone_repository()
        self.load_repository(addon)

    def update(self):
        """Update this repository using configuration and data gathered"""
        self.generate_readme()
        needs_push = self.commit_changes(':books: Updated README')

        for addon in self.addons:
            if addon.needs_update(self.force):
                click.echo(crayons.green('-' * 50, bold=True))
                click.echo(crayons.green(
                    f"Updating add-on {addon.repository_target}"))
                needs_push = (self.update_addon(addon) or needs_push)

        if needs_push:
            click.echo(crayons.green('-' * 50, bold=True))
            click.echo('Pushing updates onto Git add-ons repository...',
                       nl=False)
            self.git_repo.git.push()
            click.echo(crayons.green('Done'))

    def commit_changes(self, message):
        """Commit current Repository changes"""
        click.echo('Committing changes...', nl=False)

        if not self.git_repo.is_dirty():
            click.echo(crayons.yellow('Skipped, no changes.'))
            return False

        author = '%s <%s>' % (
            self.github.get_user().name,
            self.github.get_user().email
        )
        self.git_repo.git.add('.')
        self.git_repo.git.commit('--no-gpg-sign', '-m', message, author=author)
        click.echo(crayons.green('Done: ') + crayons.cyan(message))
        return True

    def update_addon(self, addon):
        """Update repository for a specific add-on"""
        addon.update(self.force)
        self.generate_readme()

        if addon.latest_is_release:
            message = ':tada: Release of add-on %s %s' % (
                addon.name,
                addon.current_version
            )
        else:
            message = ':arrow_up: Updating add-on %s to %s' % (
                addon.name,
                addon.current_version
            )
        if self.force:
            message += ' (forced update)'

        return self.commit_changes(message)

    def load_repository(self, addon: str):
        """""Loads repository configuration from remote repository and
        add-ons"""
        click.echo('Locating repository add-on list...', nl=False)
        try:
            config = self.github_repository.get_file_contents(
                '.hassio-addons.yml')
        except UnknownObjectException:
            print(
                "Seems like the repository does not contain an "
                ".hassio-addons.yml file")
            sys.exit(1)

        config = yaml.safe_load(config.decoded_content)
        click.echo(crayons.green('Loaded!'))

        if not config['channel'] in CHANNELS:
            click.echo(
                crayons.red(
                    'Channel "%s" is not a valid channel identifier' % config[
                        'channel']))
            sys.exit(1)

        click.echo(
            'Repository channel: %s' % crayons.magenta(config['channel']))

        if addon:
            click.echo(
                crayons.yellow('Only updating addon "%s" this run!' % addon))

        click.echo('Start loading repository add-ons:')
        for target, addon_config in config['addons'].items():
            click.echo(crayons.cyan('-' * 50, bold=True))
            click.echo(crayons.cyan(f"Loading add-on {target}"))
            self.addons.append(
                Addon(
                    self.git_repo, target, addon_config['image'],
                    self.github.get_repo(addon_config['repository']),
                    addon_config['target'],
                    config['channel'],
                    (not addon or
                     addon_config['repository'] == addon or
                     target == addon)
                )
            )
        click.echo(crayons.cyan('-' * 50, bold=True))
        click.echo('Done loading all repository add-ons')

    def clone_repository(self):
        """"Clones the add-on repository to a local working directory"""
        click.echo('Cloning add-on repository...', nl=False)
        self.git_repo = self.github.clone(self.github_repository,
                                          tempfile.mkdtemp(
                                              prefix="repoupdater"))
        click.echo(crayons.green('Cloned!'))

    def generate_readme(self):
        """Re-generates the repository readme based on a template"""
        click.echo('Re-generating add-on repository README.md file...',
                   nl=False)
        addon_data = []
        for addon in self.addons:
            addon_data.append(addon.get_template_data())

        addon_data = sorted(addon_data, key=lambda x: x['name'])

        jinja = Environment(loader=FileSystemLoader(self.git_repo.working_dir),
                            trim_blocks=True,
                            extensions=['jinja2.ext.loopcontrols'])

        with open(os.path.join(self.git_repo.working_dir, 'README.md'),
                  'w') as outfile:
            outfile.write(
                jinja.get_template('.README.j2').render(addons=addon_data))

        click.echo(crayons.green('Done'))

    def cleanup(self):
        """Cleanup after you leave"""
        click.echo('Cleanup...', nl=False)
        shutil.rmtree(self.git_repo.working_dir, True)
        click.echo(crayons.green('Done'))
