# gimmegit

gimmegit is a command-line tool for cloning GitHub repos and creating branches.

Each time you clone a repo, gimmegit creates a dedicated directory for the clone, based on the repo owner and branch name. For example, my clones of my [Frogtab](https://github.com/dwilding/frogtab) project might be organized like this:

```text
.
└── frogtab
   ├── dwilding-my-feature ◀─ A clone of dwilding/frogtab, on a new branch. Created with
   │   │                        gimmegit dwilding/frogtab my-feature
   │   ├── ...
   │
   └── <buddy>-custom-feat ◀─ A clone of <buddy>'s fork, on their feature branch. Created with
       │                        gimmegit https://github.com/<buddy>/frogtab/tree/custom-feat
       ├── ...
```

> [!WARNING]  
> gimmegit is in early development. Expect bugs and breaking changes!

You might find gimmegit interesting if:

  - You want several branches of the same repo checked out in parallel (as with [git-worktree](https://git-scm.com/docs/git-worktree))
  - You often review branches for other contributors
  - You often work within forks of upstream repos

**Demo**

Clone dwilding's fork of [canonical/jubilant](https://github.com/canonical/jubilant) and create a branch called `my-feature`:

```text
~/work$ gimmegit -u canonical dwilding/jubilant my-feature
Getting repo details
Cloning git@github.com:dwilding/jubilant.git
Setting upstream to git@github.com:canonical/jubilant.git
Checking out a new branch my-feature based on canonical:main
Installing pre-commit using uvx
pre-commit installed at .git/hooks/pre-commit
Cloned repo:
/home/me/work/jubilant/dwilding-my-feature
```

**In this README**

  - [Install gimmegit](#install-gimmegit)
  - [Clone a repo and create a branch](#clone-a-repo-and-create-a-branch)
  - [Clone a repo on an existing branch](#clone-a-repo-on-an-existing-branch)
  - [Clone a fork and create a branch](#clone-a-fork-and-create-a-branch)
  - [Clone a fork on an existing branch](#clone-a-fork-on-an-existing-branch)
  - [Provide clone options](#provide-clone-options)

## Install gimmegit

 1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/). On Ubuntu, you can run:

    ```text
    sudo snap install astral-uv --classic
    ```

 2. Run:

    ```text
    uv tool update-shell
    ```

 3. Restart your terminal.

 4. Run:

    ```text
    uv tool install gimmegit
    ```

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

After working on the new branch for a while, you might want to merge remote changes from the base branch. To merge remote changes, run `git update-branch` in the clone directory. `update-branch` is a git alias that gimmegit created.

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

This clones the repo `<owner>/<project>` into a directory called `<project>/<owner>-<branch>` and checks out the branch `<branch>`. For example:

```sh
# Clone https://github.com/canonical/postgresql-operator and
# check out the branch fix-something
gimmegit https://github.com/canonical/postgresql-operator/tree/fix-something

# Change to the clone directory
cd postgresql-operator/canonical-fix-something

# Review the branch or work on the branch…
```

After working on the branch for a while, you might want to merge remote changes from the repo's main branch. To merge remote changes, run `git update-branch` in the clone directory. `update-branch` is a git alias that gimmegit created.

If the branch wasn't based on the repo's main branch, use `-b` to set the base branch when cloning the repo. For example:

```sh
# Clone https://github.com/canonical/postgresql-operator and
# check out the branch fix-something-16, setting the base branch to 16/edge
gimmegit -b 16/edge https://github.com/canonical/postgresql-operator/tree/fix-something-16

# Change to the clone directory
cd postgresql-operator/canonical-fix-something-16

# Work on the branch…

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

After working on the new branch for a while, you might want to merge changes from the upstream base branch. To merge changes from upstream, run `git update-branch` in the clone directory. `update-branch` is a git alias that gimmegit created.

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

This clones `<owner>`'s fork of `<upstream-owner>/<project>` into a directory called `<project>/<owner>-<branch>` and checks out the branch `<branch>`. For example:

```sh
# Clone dwilding's fork of https://github.com/canonical/operator and
# check out the branch fix-something
gimmegit -u canonical https://github.com/dwilding/operator/tree/fix-something

# Change to the clone directory
cd operator/dwilding-fix-something

# Work on the branch…
```

After working on the branch for a while, you might want to merge changes from the upstream repo's main branch. To merge changes from upstream, run `git update-branch` in the clone directory. `update-branch` is a git alias that gimmegit created.

If the branch wasn't based on the upstream repo's main branch, use `-b` to set the upstream base branch when cloning the repo. For example:

```sh
# Clone dwilding's fork of https://github.com/canonical/operator and
# check out the branch backport-fix, setting the base branch to canonical:2.23-maintenance
gimmegit -b 2.23-maintenance -u canonical https://github.com/dwilding/operator/tree/backport-fix

# Change to the clone directory
cd operator/dwilding-backport-fix

# Work on the branch…

# Merge changes from canonical:2.23-maintenance
git update-branch
```

If you create a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) and put the token in an environment variable called `GIMMEGIT_GITHUB_TOKEN`, you don't need to include `-u <upstream-owner>` because gimmegit can automatically find upstream repos.

## Provide clone options

To provide [clone options](https://git-scm.com/docs/git-clone#_options) to gimmegit, list the options after `--`. For example:

```sh
# Clone dwilding's fork of https://github.com/canonical/charmcraft and
# create a branch called update-profile, cloning with --recurse-submodules
gimmegit -u canonical dwilding/charmcraft update-profile -- --recurse-submodules
```
