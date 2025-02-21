# austriadownloader

[![Release](https://img.shields.io/github/v/release/Zerhigh/austriadownloader)](https://img.shields.io/github/v/release/Zerhigh/austriadownloader)
[![Build status](https://img.shields.io/github/actions/workflow/status/Zerhigh/austriadownloader/main.yml?branch=main)](https://github.com/Zerhigh/austriadownloader/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/Zerhigh/austriadownloader/branch/main/graph/badge.svg)](https://codecov.io/gh/Zerhigh/austriadownloader)
[![Commit activity](https://img.shields.io/github/commit-activity/m/Zerhigh/austriadownloader)](https://img.shields.io/github/commit-activity/m/Zerhigh/austriadownloader)
[![License](https://img.shields.io/github/license/Zerhigh/austriadownloader)](https://img.shields.io/github/license/Zerhigh/austriadownloader)

This is a template repository for Python projects that use Poetry for their dependency management.

- **Github repository**: <https://github.com/Zerhigh/austriadownloader/>
- **Documentation** <https://Zerhigh.github.io/austriadownloader/>

## Getting started with your project

First, create a repository on GitHub with the same name as this project, and then run the following commands:

```bash
git init -b main
git add .
git commit -m "init commit"
git remote add origin git@github.com:Zerhigh/austriadownloader.git
git push -u origin main
```

Finally, install the environment and the pre-commit hooks with

```bash
make install
```

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

To finalize the set-up for publishing to PyPI or Artifactory, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/publishing/#set-up-for-pypi).
For activating the automatic documentation with MkDocs, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/mkdocs/#enabling-the-documentation-on-github).
To enable the code coverage reports, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/codecov/).

## Releasing a new version

- Create an API Token on [PyPI](https://pypi.org/).
- Add the API Token to your projects secrets with the name `PYPI_TOKEN` by visiting [this page](https://github.com/Zerhigh/austriadownloader/settings/secrets/actions/new).
- Create a [new release](https://github.com/Zerhigh/austriadownloader/releases/new) on Github.
- Create a new tag in the form `*.*.*`.
- For more details, see [here](https://fpgmaas.github.io/cookiecutter-poetry/features/cicd/#how-to-trigger-a-release).

---

## Available Classes

| **Category**       | **Code** | **Subcategory**                               |
|--------------------|----------|-----------------------------------------------|
| Building areas      | 41       | Buildings                                     |
|                    | 83       | Adjacent building areas                       |
| Water body         | 59       | Flowing water                                 |
|                    | 60       | Standing water                                |
|                    | 61       | Wetlands                                      |
|                    | 64       | Waterside areas                               |
| Agricultural       | 40       | Permanent crops or gardens                    |
|                    | 48       | Fields, meadows or pastures                  |
|                    | 57       | Overgrown areas                               |
| Forest             | 55       | Krummholz                                     |
|                    | 56       | Forests                                       |
|                    | 58       | Forest roads                                  |
| Other              | 42       | Car parks                                     |
|                    | 62       | Low vegetation areas                          |
|                    | 63       | Operating area                                |
|                    | 65       | Roadside areas                                |
|                    | 72       | Cemetery                                      |
|                    | 84       | Mining areas, dumps and landfills            |
|                    | 87       | Rock and scree surfaces                       |
|                    | 88       | Glaciers                                      |
|                    | 92       | Rail transport areas                          |
|                    | 95       | Road traffic areas                            |
|                    | 96       | Recreational area                             |
| Gardens            | 52       | Gardens                                       |
| Alps               | 54       | Alps                                          |


Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
