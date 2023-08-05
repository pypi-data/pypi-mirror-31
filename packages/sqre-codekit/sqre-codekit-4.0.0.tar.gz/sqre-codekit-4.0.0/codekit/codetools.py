"""Assorted codetools utility functions."""
# technical debt
# --------------
# - package
# - check explictly for github3 version

import logging
import os
import sys
import shutil
import tempfile
# import re # Only used in SHA-sanity-check unreachable code
import certifi
import urllib3
from github3 import login
import gitconfig
import functools


__all__ = ['login_github', 'eups2git_ref', 'repos_for_team',
           'github_2fa_callback', 'TempDir', 'gitusername', 'gituseremail',
           'get_team_id_by_name', 'get_git_credential_helper', 'eprint',
           'debug', 'warn', 'error']

logging.basicConfig()
logger = logging.getLogger('codekit')


def login_github(token_path=None, token=None):
    """Log into GitHub using an existing token.

    Parameters
    ----------
    token_path : str, optional
        Path to the token file. The default token is used otherwise.

    token: str, optional
        Literial token string. If specifified, this value is used instead of
        reading from the token_path file.

    Returns
    -------
    gh : :class:`github3.GitHub` instance
        A GitHub login instance.
    """
    if token is None:
        if token_path is None:
            # Try the default token
            token_path = '~/.sq_github_token'
        token_path = os.path.expandvars(os.path.expanduser(token_path))

        if not os.path.isfile(token_path):
            print("You don't have a token in {0} ".format(token_path))
            print("Have you run github-auth?")
            raise EnvironmentError("No token in %s" % token_path)

        with open(token_path, 'r') as fdo:
            token = fdo.readline().strip()

    ghb = login(token=token, two_factor_callback=github_2fa_callback)

    return ghb


def gitusername():
    """
    Returns the user's name from .gitconfig if available
    """
    try:
        mygitconfig = gitconfig.GitConfig()
        return mygitconfig['user.name']
    except:
        return None


def gituseremail():
    """
    Returns the user's email from .gitconfig if available
    """

    try:
        mygitconfig = gitconfig.GitConfig()
        return mygitconfig['user.email']
    except:
        return None


def github_2fa_callback():
    """
    Prompt for two-factor code
    """
    # http://github3py.readthedocs.org/en/master/examples/two_factor_auth.html
    code = ''
    while not code:
        # The user could accidentally press Enter before being ready,
        # let's protect them from doing that.
        code = input('Enter 2FA code: ')
    return code


def repos_for_team(org, teams=None):
    """Iterate over repos in a GitHub organization that are in the given
    set of teams.

    Parameters
    ----------
    org : class:`github3.github3.orgs.Organization` instance
        The GitHub organization to operate in. Usually created with the
        :meth:`github3.GitHub.organization` method.
    teams : iterable
        A sequence of team names (as strings). If `None` (default) then
        team identity will be ignored and all repos in the organization
        will be iterated over.

    Yields
    ------
    repo : :class:`github3.repos.repo.Repository`
        Yields repositiory instances that pass organization and team criteria.
    """
    if teams is not None:
        teams = set(teams)
    for repo in org.repositories():
        repo_teams = set([t.name for t in repo.teams()])
        if teams is None:
            yield repo
        elif repo_teams.isdisjoint(teams) is False:
            yield repo


def open_repo(org, repo_name):
    """Open a :class:`github3.repos.repo.Repository` instance by name
    in a GitHub organization.

    Parameters
    ----------
    org : class:`github3.github3.orgs.Organization` instance
        The GitHub organization to operate in. Usually created with the
        :meth:`github3.GitHub.organization` method.
    repo_name : str
        Name of the repository (without the organization namespace).
        E.g. `'afw'`.

    Returns
    -------
    repo : :class:`github3.repos.repo.Repository`
        The repository instance.
    """
    for repo in org.repositories():
        if repo.name == repo_name:
            return repo


def get_team_id_by_name(org, team_name, debug=False):
    """Get the ID of a team in a GitHub organization.

    Parameters
    ----------
    org : class:`github3.github3.orgs.Organization` instance
        The GitHub organization to operate in. Usually created with the
        :meth:`github3.GitHub.organization` method.
    team_name : `str`
        Name of the team to find
    debug : `bool`, optional
        Enable debug output.

    Returns
    -------
    team_id : `int` or `None`
        The team ID as an integer, or `None` if `team_name` is the empty
        string.

    Raises
    ------
    `NameError`
        If there is no team with the given name in the supplied organization.
    """

    if team_name == '':
        if debug:
            print("Searching for empty teamname -> None")
        return None  # Special case for empty teams
    teams = org.teams()
    try:
        while True:
            team = teams.next()
            if debug:
                print("Considering team %s with ID %i" % (team.name, team.id))
            if team.name == team_name:
                if debug:
                    print("Match found.")
                return team.id
    except StopIteration:
        raise NameError("No team '%s' in organization '%s'" % (team_name,
                                                               org.login))


def get_git_credential_helper(username, token):
    """Get a string suitable for inclusion in a git config as a credential
    helper, allowing authenticated access without prompting for a password.

    Useful for, e.g., doing a push to Github from a local repo.

    Parameters
    ----------
    username: `str`
        The GitHub username for the authenticated action.
    token: `str`
        The corresponding access token.

    Returns
    -------
    helper : `str`
        A string which is a runnable shell fragment for use in a git config.
    """
    # The initial bang tells git it's about to run a shell fragment.
    #  The rest is a string, which will be evaluated in the shell (so don't
    #  take unsanitized input from the outside world!)
    # It defines a function to swallow any input and put username and password
    #  on separate lines: it substitutes its parameter values into the
    #  username/password values.
    # This means it will work under `git credential fill`, which is the
    #  entire point.
    helper = '!"f() { cat > /dev/null ; echo username=' + username
    helper += ' ; echo password=' + token + ' ; } ; f"'
    return helper


@functools.lru_cache(maxsize=1024)
def fetch_manifest_file(
    build_id,
    versiondb='https://raw.githubusercontent.com'
              '/lsst/versiondb/master/manifests',
    debug=False
):
    # eg. https://raw.githubusercontent.com/lsst/versiondb/master/manifests/b1108.txt  # NOQA
    shafile = versiondb + '/' + build_id + '.txt'
    logger.debug("fetching: {url}".format(url=shafile))

    # Get the file tying shas to eups versions
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where()
    )

    manifest = http.request('GET', shafile)
    if manifest.status >= 300:
        raise RuntimeError('Failed GET with HTTP code', manifest.status)

    return manifest.data


@functools.lru_cache(maxsize=1024)
def parse_manifest_file(data):
    products = {}

    for line in data.splitlines():
        if not isinstance(line, str):
            line = str(line, 'utf-8')
        # skip commented out and blank lines
        if line.startswith('#'):
            continue
        if line.startswith('BUILD'):
            continue
        if line == '':
            continue

        (product, sha, eups_version) = line.split()[0:3]

        products[product] = {
            'name': product,
            'sha': sha,
            'eups_version': eups_version,
        }

    return products


@functools.lru_cache(maxsize=1024)
def eups2git_ref(
    product,
    eups_version,
    build_id,
    debug=False
):
    """Provide the sha1 for an EUPS product."""

    manifest = fetch_manifest_file(build_id, debug=debug)
    products = parse_manifest_file(manifest)

    entry = products[product]
    if entry['eups_version'] == eups_version:
        return entry['sha']
    else:
        raise RuntimeError(
            "failed to find record in manifest {build_id} for:\n"
            "  {name} {version}".format(
                build_id=build_id,
                product=product,
                eups_version=eups_version
            )
        )


def debug(*args):
    logger.debug(*args)


def warn(*args):
    logger.warn(*args)


def error(*args):
    logger.error(*args)


# https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
def eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


class TempDir(object):
    """ContextManager for temporary directories.

    For example::

        import os
        with TempDir() as temp_dir:
            assert os.path.exists(temp_dir)
        assert os.path.exists(temp_dir) is False
    """

    def __init__(self):
        super(TempDir, self).__init__()
        self._temp_dir = tempfile.mkdtemp()

    def __enter__(self):
        return self._temp_dir

    def __exit__(self, ttype, value, traceback):
        shutil.rmtree(self._temp_dir)
        self._temp_dir = None
