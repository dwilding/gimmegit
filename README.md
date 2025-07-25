# gimmegit

gimmegit is a command-line tool for cloning GitHub repos. You might find gimmegit interesting if:

  - You usually work within forks of upstream repos
  - You want several branches of the same fork checked out in parallel (as with [git-worktree](https://git-scm.com/docs/git-worktree))
  - You frequently review branches from the forks of other contributors

> [!WARNING]  
> gimmegit is in early development. Expect bugs and breaking changes!

In this README:

  - [Examples](#examples)
  - [Install gimmegit](#install-gimmegit)
  - [Specify the base branch](#specify-the-base-branch)
  - [Customize gimmegit](#customize-gimmegit)

## Examples

### Review a branch

To clone dwilding's fork of `operator` and check out the `fix-something` branch:

```text
gimmegit https://github.com/dwilding/operator/tree/fix-something
```
gimmegit clones the fork into a directory called *operator/dwilding-fix-something*.

If you're reviewing dwilding's branch, this is probably the only command you'll need to use!

### Work on an existing branch

If you are dwilding, and you're working on the `fix-something` branch, you should use `-u` to specify the upstream owner when cloning your fork:

```text
gimmegit -u canonical https://github.com/dwilding/operator/tree/fix-something
```

In addition to cloning your fork, gimmegit creates a git alias called `update-branch`. You can use `git update-branch` to merge the latest changes from `canonical/operator` into your local copy of `fix-something`.

### Create a branch

To clone your fork of `operator` and create a branch:

```text
gimmegit -u canonical https://github.com/dwilding/operator new-feature
```

Or equivalently:

```text
gimmegit -u canonical dwilding/operator new-feature
```

gimmegit clones the fork into a directory called *operator/dwilding-new-feature* and checks out a new branch called `new-feature`. gimmegit doesn't push the new branch to GitHub.

The new branch is based on `canonical:main`. You don't need to update `dwilding:main` before running gimmegit. To merge `canonical:main` into `dwilding:new-feature` in the future, run `git update-branch`.

If you want an experimental branch and don't care about the branch name, use:

```text
gimmegit -u canonical dwilding/operator
```

gimmegit generates a branch name based on the date. For example, `snapshot0801` on August 1.

If you get tired of typing `-u canonical` and your GitHub username, create a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) and put the token in an environment variable called `GIMMEGIT_GITHUB_TOKEN`. Then, to clone your fork and create a branch:

```text
gimmegit operator new-feature
```

## Install gimmegit

 1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/). On Ubuntu, you can run:

    ```text
    sudo snap install astral-uv --classic
    ```

 2. Run:

    ```text
    uv tool update-shell
    ```

 3. Restart your shell.

 4. Run:

    ```text
    uv tool install gimmegit
    ```

## Specify the base branch

TODO

## Customize gimmegit

TODO
