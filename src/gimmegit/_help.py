help = """\
gimmegit is a tool for cloning GitHub repos and creating branches. gimmegit puts each clone in a
dedicated directory, based on the project, owner, and branch name.

▶ USAGE
gimmegit [<options>] <repo> [<new-branch>] [-- <git-options>]   Clone a GitHub repo and check out
                                                                a new branch.
gimmegit [<options>] <branch-url> [-- <git-options>]            Clone a GitHub repo and check out
                                                                an existing branch.

▶ POSITIONAL ARGUMENTS
<repo>         One of:
                 • <owner>/<project>. For example, 'dwilding/frogtab'. <owner> is optional if the
                   GIMMEGIT_GITHUB_TOKEN environment variable contains a personal access token.
                 • A repo URL. For example, 'https://github.com/dwilding/frogtab'.
<new-branch>   The name of a branch that doesn't already exist. gimmegit generates a branch name
               if you omit <new-branch>. For example, 'snapshot0801' on August 1.
<branch-url>   A URL such as 'https://github.com/dwilding/frogtab/tree/fix-something'.

▶ DIRECTORY STRUCTURE
When you clone a repo, gimmegit creates a dedicated directory for the clone:
  .
  └── <project>              The project directory. For example, 'frogtab'.
      └── <owner>-<branch>   The clone directory. For example, 'dwilding-my-feature'.

If the clone directory already exists, gimmegit skips cloning. If the clone directory would be
inside an existing repo, gimmegit exits with an error. gimmegit also exits with an error if it
detects that the working directory is a project directory (specifically, if the latest modified
subdirectory is a gimmegit clone).

▶ BRANCH MAPPING
When you clone a repo, gimmegit creates a Git alias 'update-branch' that merges remote changes
from the base branch. The base branch is the repo's main branch. If the repo is a fork and
GIMMEGIT_GITHUB_TOKEN is set, the base branch is the upstream version of the repo's main branch.

For new branches:
• gimmegit branches off the base branch.
• gimmegit doesn't push the branch to GitHub.

▶ OPTIONS
-u, --upstream-owner <owner>   Owner of the base branch. For example, if you're cloning a fork of
                               a repo from github.com/canonical, provide '-u canonical'. If you
                               provide -u, gimmegit doesn't try to use GIMMEGIT_GITHUB_TOKEN to
                               look for an upstream repo.
-b, --base-branch <name|url>   Name or URL of the base branch. If '-b <name>', gimmegit uses
                               <name> instead of the repo's main branch (or upstream main).
                               If '-b https://github.com/<upstream-owner>/<project>/tree/<name>',
                               gimmegit sets the owner & name of the base branch, overriding -u.
--no-pre-commit                Don't try to install a pre-commit hook after cloning the repo.
--allow-outer-repo             Clone the repo even if the clone directory will be inside a repo.
--force-project-dir            Create the project directory even if gimmegit finds a gimmegit
                               clone in the working directory.
--ssh auto|always|never        Controls whether Git remotes use SSH or HTTPS.
                               Default: auto - use SSH if ~/.ssh contains an SSH key.
--color auto|always|never      Controls whether the output has colored text.
                               Default: auto - use colors if the NO_COLOR environment variable is
                               empty and the output is going to a terminal.
--return-dir                   Output the clone directory path to stdout and send full progress
                               to stderr.

▶ GIT OPTIONS
gimmegit sets --no-tags when cloning. To provide extra git-clone options, use '-- <git-options>'.
For example, to clone tags, use '-- --tags'.

▶ PRE-COMMIT
If the repo contains a file '.pre-commit-config.yaml', gimmegit installs a pre-commit hook after
cloning the repo. For more information, see https://pre-commit.com/.

▶ ADDITIONAL COMMANDS
gimmegit [--color auto|always|never]                   Display the branch mapping if the working
                                                       directory is inside a gimmegit clone.
gimmegit -c | --compare                                Compare branches in GitHub if the working
                                                       directory is inside a gimmegit clone.
gimmegit -h | --help                                   Display a summary of how to use gimmegit.
gimmegit --version                                     Display the installed version of gimmegit.
gimmegit [--ssh auto|always|never] --parse-url <url>   Display a JSON representation of a GitHub
                                                       URL. Intended for extensions to gimmegit.

▶ EXAMPLES
# Clone https://github.com/dwilding/frogtab and check out a new branch
gimmegit dwilding/frogtab my-feature                 # branching off main
gimmegit -b candidate dwilding/frogtab bump-version  # branching off a dev branch

# Clone the same repo and check out an existing branch
gimmegit https://github.com/dwilding/frogtab/tree/fix-something

# Clone dwilding's fork of https://github.com/canonical/operator and check out a new branch
gimmegit -u canonical dwilding/operator update-docs  # branching off upstream main
gimmegit -b 2.23-maintenance -u canonical \\          # branching off an upstream dev branch
  dwilding/operator backport-docs
gimmegit -b https://github.com/canonical/operator/tree/2.23-maintenance \\  # same as previous
  dwilding/operator backport-docs"""
