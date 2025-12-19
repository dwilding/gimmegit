# gimmegit — Isolated directories for Git branches

gimmegit is a command-line tool for cloning GitHub repos and creating branches.

[![Demo of gimmegit](https://asciinema.org/a/761708.svg)](https://asciinema.org/a/761708)

You might find gimmegit interesting if:

  - You want several branches of the same repo checked out in parallel (as with [git-worktree](https://git-scm.com/docs/git-worktree))
  - You often review branches for other contributors
  - You often work within forks of upstream repos

Each time you clone a repo, gimmegit creates a dedicated directory for the clone, based on the repo owner and branch name. For example, my clones of [Frogtab](https://github.com/dwilding/frogtab) might be organized like this:

```text
.
└── frogtab
    ├── dwilding-my-feature   A clone of the Frogtab repo, on a new branch. Created with
    │   │                     gimmegit dwilding/frogtab my-feature
    │   ├── ...
    │
    └── <buddy>-custom-feat   A clone of <buddy>'s fork, on their feature branch. Created with
        │                     gimmegit https://github.com/<buddy>/frogtab/tree/custom-feat
        ├── ...
```

In this README:

  - [Install gimmegit](#install-gimmegit)
  - [Clone a repo and create a branch](#clone-a-repo-and-create-a-branch)
  - [Clone a repo on an existing branch](#clone-a-repo-on-an-existing-branch)
  - [Clone a fork and create a branch](#clone-a-fork-and-create-a-branch)
  - [Clone a fork on an existing branch](#clone-a-fork-on-an-existing-branch)
  - [Provide clone options](#provide-clone-options)
  - [Command reference](#command-reference)

## Install gimmegit

| Using [uv](https://docs.astral.sh/uv/)<br/>`uv tool install gimmegit` | | Using [pipx](https://pipx.pypa.io/stable/)<br/>`pipx install gimmegit` |
|-|-|-|
| To run gimmegit without installing it,<br/>use `uvx gimmegit <args>` instead. | | To run gimmegit without installing it,<br/>use `pipx run gimmegit <args>` instead. |

## Clone a repo and create a branch

```text
gimmegit <owner>/<project> <new-branch>
```

This clones the repo `<owner>/<project>` into a directory called `<project>/<owner>-<new-branch>` and checks out a new branch called `<new-branch>`. gimmegit doesn't push the new branch to GitHub.

If you omit `<new-branch>`, gimmegit generates a branch name based on the date. For example, `snapshot0801` on August 1. This is handy for creating experimental branches.

The new branch is based on the repo's main branch. To specify the base branch, use `-b`:

```text
gimmegit -b <base-branch> <owner>/<project> <new-branch>
```

After working on the new branch for a while, you might want to merge remote changes from the base branch. To merge remote changes, run `git update-branch` in the clone directory. `update-branch` is a Git alias that gimmegit created.

### Example

```sh
# Clone https://github.com/canonical/postgresql-operator and
# create a branch called update-docs
gimmegit canonical/postgresql-operator update-docs

# Change to the clone directory
cd postgresql-operator/canonical-update-docs

# Start your work…

# Merge remote changes from main
git update-branch

# Realize that you need to work on something else too…

# Clone the repo again, creating a branch called update-docs-16,
# this time based on 16/edge instead of main
cd ../..
gimmegit -b 16/edge canonical/postgresql-operator update-docs-16

# Change to the second clone directory
cd postgresql-operator/canonical-update-docs-16

# Start your work…

# Merge remote changes from 16/edge
git update-branch
```

## Clone a repo on an existing branch

```text
gimmegit https://github.com/<owner>/<project>/tree/<branch>
```

This clones the repo `<owner>/<project>` into a directory called `<project>/<owner>-<branch>` and checks out the branch `<branch>`.

After working on the branch for a while, you might want to merge remote changes from the repo's main branch. To merge remote changes, run `git update-branch` in the clone directory. `update-branch` is a Git alias that gimmegit created.

### Example

```sh
# Clone https://github.com/canonical/postgresql-operator and
# check out the branch fix-something
gimmegit https://github.com/canonical/postgresql-operator/tree/fix-something

# Change to the clone directory
cd postgresql-operator/canonical-fix-something

# Review the branch or work on the branch…

# Merge remote changes from main
git update-branch
```

### Example with a base branch

If the branch wasn't based on the repo's main branch, use `-b` to set the base branch when cloning the repo.

```sh
# Clone https://github.com/canonical/postgresql-operator and
# check out the branch fix-something-16, setting the base branch to 16/edge
gimmegit -b 16/edge https://github.com/canonical/postgresql-operator/tree/fix-something-16

# Change to the clone directory
cd postgresql-operator/canonical-fix-something-16

# Review the branch or work on the branch…

# Merge remote changes from 16/edge
git update-branch
```

## Clone a fork and create a branch

```text
gimmegit -u <upstream-owner> <owner>/<project> <new-branch>
```

This clones `<owner>`'s fork of `<upstream-owner>/<project>` into a directory called `<project>/<owner>-<new-branch>` and checks out a new branch called `<new-branch>`. gimmegit doesn't push the new branch to GitHub.

If you omit `<new-branch>`, gimmegit generates a branch name based on the date. For example, `snapshot0801` on August 1. This is handy for creating experimental branches.

The new branch is based on the upstream repo's main branch. (Technically, it's based on the upstream version of the fork's main branch, which is normally the same thing.) To specify the upstream base branch, use `-b`:

```text
gimmegit -b <upstream-base-branch> -u <upstream-owner> <owner>/<project> <new-branch>
```

After working on the new branch for a while, you might want to merge changes from the upstream base branch. To merge changes from upstream, run `git update-branch` in the clone directory. `update-branch` is a Git alias that gimmegit created.

### Example

```sh
# Clone dwilding's fork of https://github.com/canonical/operator and
# create a branch called update-docs
gimmegit -u canonical dwilding/operator update-docs

# Change to the clone directory
cd operator/dwilding-update-docs

# Start your work…

# Merge changes from canonical:main
git update-branch

# Realize that you need to work on something else too…

# Clone dwilding's fork again, creating a branch called backport-docs,
# this time based on canonical:2.23-maintenance instead of canonical:main
cd ../..
gimmegit -b 2.23-maintenance -u canonical dwilding/operator backport-docs

# This does the same thing:
# gimmegit -b https://github.com/canonical/operator/tree/2.23-maintenance \
#   dwilding/operator backport-docs

# Change to the second clone directory
cd operator/dwilding-backport-docs

# Start your work…

# Merge changes from canonical:2.23-maintenance
git update-branch
```

### Example with a GitHub token

If you create a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) and put the token in an environment variable called `GIMMEGIT_GITHUB_TOKEN`, gimmegit can automatically find upstream repos and your GitHub username. Here's the same example with `GIMMEGIT_GITHUB_TOKEN` set:

```sh
# Clone your fork of https://github.com/canonical/operator and
# create a branch called update-docs (assuming you are dwilding)
gimmegit operator update-docs

# Change to the clone directory
cd operator/dwilding-update-docs

# Start your work…

# Merge changes from canonical:main
git update-branch

# Realize that you need to work on something else too…

# Clone your fork again, creating a branch called backport-docs,
# this time based on canonical:2.23-maintenance instead of canonical:main
cd ../..
gimmegit -b 2.23-maintenance operator backport-docs

# Change to the second clone directory
cd operator/dwilding-backport-docs

# Start your work…

# Merge changes from canonical:2.23-maintenance
git update-branch
```

## Clone a fork on an existing branch

```text
gimmegit -u <upstream-owner> https://github.com/<owner>/<project>/tree/<branch>
```

This clones `<owner>`'s fork of `<upstream-owner>/<project>` into a directory called `<project>/<owner>-<branch>` and checks out the branch `<branch>`.

After working on the branch for a while, you might want to merge changes from the upstream repo's main branch. To merge changes from upstream, run `git update-branch` in the clone directory. `update-branch` is a Git alias that gimmegit created.

### Example

```sh
# Clone dwilding's fork of https://github.com/canonical/operator and
# check out the branch fix-something
gimmegit -u canonical https://github.com/dwilding/operator/tree/fix-something

# Change to the clone directory
cd operator/dwilding-fix-something

# Review the branch or work on the branch…

# Merge changes from canonical:main
git update-branch
```

### Example with a GitHub token

If you create a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) and put the token in an environment variable called `GIMMEGIT_GITHUB_TOKEN`, gimmegit can automatically find upstream repos. Here's the same example with `GIMMEGIT_GITHUB_TOKEN` set:

```sh
# Clone dwilding's fork of https://github.com/canonical/operator and
# check out the branch fix-something
gimmegit https://github.com/dwilding/operator/tree/fix-something

# Change to the clone directory
cd operator/dwilding-fix-something

# Review the branch or work on the branch…

# Merge changes from canonical:main
git update-branch
```

### Example with a base branch

If the branch wasn't based on the upstream repo's main branch, use `-b` to set the upstream base branch when cloning the repo.

```sh
# Clone dwilding's fork of https://github.com/canonical/operator and
# check out the branch backport-fix, setting the base branch to canonical:2.23-maintenance
gimmegit -b 2.23-maintenance -u canonical https://github.com/dwilding/operator/tree/backport-fix

# This does the same thing:
# gimmegit -b https://github.com/canonical/operator/tree/2.23-maintenance \
#   https://github.com/dwilding/operator/tree/backport-fix

# If GIMMEGIT_GITHUB_TOKEN is set, this also does the same thing:
# gimmegit -b 2.23-maintenance https://github.com/dwilding/operator/tree/backport-fix

# Change to the clone directory
cd operator/dwilding-backport-fix

# Review the branch or work on the branch…

# Merge changes from canonical:2.23-maintenance
git update-branch
```

## Provide clone options

To provide [clone options](https://git-scm.com/docs/git-clone#_options) to gimmegit, list the options after `--`. For example:

```sh
# Clone dwilding's fork of https://github.com/canonical/charmcraft and
# create a branch called update-profile, cloning with --recurse-submodules
gimmegit -u canonical dwilding/charmcraft update-profile -- --recurse-submodules
```

# Command reference

```text
gimmegit is a tool for cloning GitHub repos and creating branches. gimmegit puts each clone
in a dedicated directory, based on the project, owner, and branch name.

▶ USAGE

gimmegit [<options>] <repo> [<new-branch>] [-- <git-options>]   (1)
gimmegit [<options>] <branch-url> [-- <git-options>]            (2)

1. Clone a GitHub repo and check out a new branch.
   <repo> is one of:
    • <owner>/<project>. For example, 'dwilding/frogtab'. <owner> is optional if the
      GIMMEGIT_GITHUB_TOKEN environment variable contains a personal access token.
    • A repo URL. For example, 'https://github.com/dwilding/frogtab'.
   <new-branch> is the name of a branch that doesn't already exist. gimmegit generates a
   branch name if you omit <new-branch>. For example, 'snapshot0801' on August 1.

2. Clone a GitHub repo and check out an existing branch.
   <branch-url> is a URL such as 'https://github.com/dwilding/frogtab/tree/fix-something'.

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

▶ GIT OPTIONS

gimmegit sets --no-tags when cloning. Use '-- <git-options>' to provide extra clone options.
For example, use '-- --tags' to clone tags.

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
gimmegit -b https://github.com/canonical/operator/tree/2.23-maintenance \   (6)
  dwilding/operator backport-docs

1. Clone https://github.com/dwilding/frogtab and check out a new branch, branching off main.
2. Clone the same repo and check out a new branch, branching off a dev branch.
3. Clone the same repo and check out an existing branch.
4. Clone dwilding's fork of https://github.com/canonical/operator and check out a new branch,
   branching off upstream main.
5. Clone the same fork and check out a new branch, branching off an upstream dev branch.
6. Equivalent to (5).
```
