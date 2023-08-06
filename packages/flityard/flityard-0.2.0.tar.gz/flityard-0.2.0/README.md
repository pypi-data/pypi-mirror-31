# flityard

Test project for better understanding of the
[PEP 518](https://www.python.org/dev/peps/pep-0518/) (a.k.a. pyproject.toml)
and release process with [flit](https://github.com/takluyver/flit/)

## Installation

You need to have [`flit` installed](https://github.com/takluyver/flit#install).
You also need to have `.pypirc` file
[configured](https://docs.python.org/3.6/distutils/packageindex.html#pypirc).



## How to do a release

In `__init__.py` we have version number in a `__version__` attribute at the top.
Once we do a release we immediately bump the version number by a patch/bugfix
level and append .dev to it. We follow
[semantic versioning](https://semver.org/).

When it comes time to release we can just drop the .dev from `__version__` and
the `CHANGELOG.md`, commit, and run flit publish.


When you drop the .dev from `__version__` creata a commit with the following
message: `Preparing release <version>`

Then publish the release:

```bash
$ flit publish
```

Then "go back to development":
  - add the `.dev` to `__version__`
  - create a commit with the following message: `Back to development: <new_version>`

To `CHANGELOG.md` add new unreleased section:

```
<new_version> (unreleased)
------------------

- Nothing changed yet.
```

## Usage

```bash
$ pip install flintyard
$ python
>>> from flintyard import main
>>> main.hello_world()
Hello world

```

## Further read

- https://flit.readthedocs.io/en/latest/
- https://snarky.ca/clarifying-pep-518/
- https://snarky.ca/how-i-manage-package-version-numbers/


## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request
