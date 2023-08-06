"""
pygithub based help functions for interacting with the github api.
"""

from github import Github
from public import public
import codekit.codetools as codetools
import github
import logging
import textwrap

logging.basicConfig()
logger = logging.getLogger('codekit')


class CaughtGitError(Exception):
    """Simple exception class intended to bundle together a github.Repository
    object and a thrown exception
    """
    def __init__(self, repo, caught):
        self.repo = repo
        self.caught = caught

    def __str__(self):
        return textwrap.dedent("""\
            Caught: {name}
              In repo: {repo}
              Message: {e}\
            """.format(
            name=type(self.caught),
            repo=self.repo.full_name,
            e=str(self.caught)
        ))


@public
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
    gh : :class:`github.GitHub` instance
        A GitHub login instance.
    """

    token = codetools.github_token(token_path=token_path, token=token)
    return Github(token)


@public
def find_tag_by_name(repo, tag_name, safe=True):
    """Find tag by name in a github Repository

    Parameters
    ----------
    repo: :class:`github.Repository` instance

    tag_name: str
        Short name of tag (not a fully qualified ref).

    safe: bool, optional
        Defaults to `True`. When `True`, `None` is returned on failure. When
        `False`, an exception will be raised upon failure.

    Returns
    -------
    gh : :class:`github.GitRef` instance or `None`

    Raises
    ------
    github.UnknownObjectException
        If git tag name does not exist in repo.
    """
    tagfmt = 'tags/{ref}'.format(ref=tag_name)

    try:
        ref = repo.get_git_ref(tagfmt)
        if ref and ref.ref:
            return ref
    except github.UnknownObjectException:
        if not safe:
            raise

    return None
