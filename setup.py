import json
import os
import requests
import setuptools
import subprocess
import sys


def get_version(release_override="0.0.1"):
    def get_last_version_root(last_version):
        if ".post" in last_version or ".dev" in last_version:
            last_version_root = ".".join(last_version.split(".")[:-1])
        else:
            last_version_root = last_version
        return last_version_root
    
    cwd = os.path.dirname(os.path.realpath(__file__))
    git_version = subprocess.check_output(
        ["git", "describe", "--always", "--tags"], stderr=None, cwd=cwd
    ).strip().decode("utf-8")

    if "." not in git_version:
        # Git doesn't know about a tag yet, so set the version root to release_override
        version_root = release_override
    else:
        version_root = git_version.split("-")[0]

    if "." not in git_version or "-" in git_version:
        # This commit doesn't correspond to a tag, so mark it as post or dev
        response = requests.get(
            "https://test.pypi.org/pypi/ds-py-version-demo/json"
        )
        if response.status_code == 200:
            # Response from TestPyPI was successful - get latest version and increment
            last_version = json.loads(response.content)["info"]["version"]
            last_version_root = get_last_version_root(last_version)

            if last_version_root == version_root:
                # We're still on the same released version, so increment the 'post'
                post_count = 1
                if "post" in last_version:
                    post_index = last_version.rfind("post") + 4
                    post_count = int(last_version[post_index:])
                    post_count += 1
                version = version_root + ".post" + str(post_count)
            else:
                response = requests.get(
                    "https://pypi.org/pypi/ds-py-version-demo/json"
                )
                dev_count = 1
                if response.status_code == 200:
                    # Response from PyPI was successful - get dev version and increment
                    last_version = json.loads(response.content)["info"]["version"]
                    last_version_root = get_last_version_root(last_version)

                    if last_version_root == version_root:
                        if "dev" in last_version:
                            dev_index = last_version.rfind("dev") + 3
                            dev_count = int(last_version[dev_index:])
                            dev_count += 1
                version = version_root + ".dev" + str(dev_count)
        else:
            # Bad response from TestPyPI, so use git commits (requires git history)
            # NOTE: May cause version clashes on mutliple branches - use test.pypi
            # to avoid this.
            num_commits = subprocess.check_output(
                ["git", "rev-list", "--count", "HEAD"], stderr=None, cwd=cwd
            ).strip().decode("utf-8")
            version = release_override + ".post" + num_commits
    else:
        version = version_root
    return version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ds_py_version_demo",
    version=get_version(),
    author="Dan Short",
    author_email="dan.short@ukaea.uk",
    description="Example of getting versions from PyPI and git",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/danshort12/ds-py-version-demo/",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
