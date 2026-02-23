help = """\
gimmegit is a tool for cloning GitHub repos and creating branches. gimmegit puts each clone
in a dedicated directory, based on the project, owner, and branch name.

▶ USAGE

gimmegit [<options>] <repo> [<new-branch>] [-- <git-options>]   (1)
gimmegit [<options>] <branch-url> [-- <git-options>]            (2)

1. Clone a GitHub repo and check out a new branch.
2. Clone a GitHub repo and check out an existing branch.

<repo>         One of:
                • <owner>/<project>. For example, 'dwilding/frogtab'. <owner> is optional if
                  the GIMMEGIT_GITHUB_TOKEN environment variable contains an access token.
                • A repo URL. For example, 'https://github.com/dwilding/frogtab'.

<new-branch>   Name of a branch that doesn't already exist in the repo. gimmegit generates a
               branch name if you omit <new-branch>. For example, 'snapshot0801' on August 1.

<branch-url>   A branch URL such as 'https://github.com/dwilding/frogtab/tree/fix-something'.

▶ DIRECTORY STRUCTURE

When you clone a repo, gimmegit creates a dedicated directory for the clone:
   .
   └── <project>              The project directory. For example, 'frogtab'.
       └── <owner>-<branch>   The clone directory. For example, 'dwilding-my-feature'.

If the clone directory already exists, gimmegit skips cloning. If the clone directory would
be inside an existing repo, gimmegit exits with an error. gimmegit also exits with an error
if it detects that the working directory is a project directory (specifically, if the latest
modified subdirectory is a gimmegit clone).

▶ BRANCH MAPPING

gimmegit creates a Git alias 'update-branch' that merges remote changes from the base branch.
The base branch is the repo's main branch. If the repo is a fork and GIMMEGIT_GITHUB_TOKEN is
set, the base branch is the upstream version of the repo's main branch.

For new branches:
 • gimmegit branches off the base branch.
 • gimmegit doesn't push the branch to GitHub.

▶ OPTIONS

-u, --upstream-owner <owner>   Owner of the base branch. For example, provide '-u canonical'
                               to clone a fork of a repo from https://github.com/canonical.
                               If you provide -u, gimmegit doesn't try to use
                               GIMMEGIT_GITHUB_TOKEN to look for an upstream repo.

-b, --base-branch <name|url>   Name or URL of the base branch. If '-b <name>', gimmegit uses
                               <name> instead of the repo's main branch (or upstream main).
                               If '-b https://github.com/<owner>/<project>/tree/<name>',
                               gimmegit sets the base branch and ignores -u.

-j, --jumbo                    Set '--shallow-since <date>' when cloning the repo, where
                               <date> is 3 weeks before the latest commit on the main branch.

--no-pre-commit                Don't try to install a pre-commit hook after cloning the repo.

--allow-outer-repo             Allow the clone directory to be inside a repo.

--force-project-dir            Create the project directory even if gimmegit finds a gimmegit
                               clone in the working directory.

--ssh auto|always|never        Controls whether Git remotes use SSH or HTTPS.
                                • auto (default): Use SSH if ~/.ssh contains an SSH key.

--color auto|always|never      Controls whether the output has colored text.
                                • auto (default): Use colors if the NO_COLOR environment
                                  variable is empty and the output is going to a terminal.

--return-dir                   Output the clone directory path to stdout and send full
                               progress to stderr.

▶ GIT CLONE OPTIONS

gimmegit sets --no-tags and --single-branch when cloning the repo. Use '-- <options>' to
provide extra 'git clone' options. For example, use '-- --tags' to cancel out --no-tags.

▶ PRE-COMMIT

If the repo contains a file '.pre-commit-config.yaml', gimmegit installs a pre-commit hook
after cloning the repo. For more information, see https://pre-commit.com/.

▶ ADDITIONAL COMMANDS

gimmegit [--color auto|always|never]                   (1)
gimmegit -c | --compare                                (2)
gimmegit -h | --help                                   (3)
gimmegit --version                                     (4)
gimmegit [--ssh auto|always|never] --parse-url <url>   (5)

1. Display the branch mapping if the working directory is inside a gimmegit clone.
2. Compare branches in GitHub if the working directory is inside a gimmegit clone.
3. Display a summary of how to use gimmegit.
4. Display the installed version of gimmegit.
5. Display a JSON representation of a GitHub URL. Intended for extensions to gimmegit.

▶ EXAMPLES

gimmegit dwilding/frogtab my-feature                                        (1)
gimmegit -b candidate dwilding/frogtab bump-version                         (2)
gimmegit https://github.com/dwilding/frogtab/tree/fix-something             (3)
gimmegit -u canonical dwilding/operator update-docs                         (4)
gimmegit -b 2.23-maintenance -u canonical dwilding/operator backport-docs   (5)
gimmegit -b https://github.com/canonical/operator/tree/2.23-maintenance \\   (6)
  dwilding/operator backport-docs

1. Clone https://github.com/dwilding/frogtab and check out a new branch, branching off main.
2. Clone the same repo and check out a new branch, branching off a dev branch.
3. Clone the same repo and check out an existing branch.
4. Clone dwilding's fork of https://github.com/canonical/operator and check out a new branch,
   branching off upstream main.
5. Clone the same fork and check out a new branch, branching off an upstream dev branch.
6. Equivalent to (5)."""
