#!/usr/bin/env python3
import argparse
import os
import re
import shutil
import subprocess
from pathlib import Path

from registry import (
    download_file,
    extract_tar_gz,
    extract_zip,
    integrity,
    json_dump,
    json_load,
    read,
)


def get_module_name() -> str:
    with open("MODULE.bazel", "r") as f:
        data = f.read()
        o = re.search(r'module\(\s*name = "(?P<name>\S+)"', data)
        if o:
            return o.group("name")
        else:
            raise Exception("Can not found module info")


def get_latest_tag() -> str:
    ret = subprocess.run(
        "git describe --tags --abbrev=0".split(), check=True, capture_output=True, text=True
    )
    return ret.stdout.strip()


def update_metadata(template: Path, target: Path, ver: str) -> tuple[str, str]:
    versions: list[str] = []
    if target.exists():
        data = json_load(target)
        versions = data["versions"]

    if ver not in versions:
        versions.append(ver)

    data = json_load(template)
    data["versions"] = versions
    json_dump(target, data)

    repo: str = data["repository"][0]
    o = re.search(r"github:(?P<ower>\S+)/(?P<repo>\S+)", repo)
    if o:
        return (o.group("ower"), o.group("repo"))

    raise Exception("Can not found owner's name and repo's name")


def update_source(template: Path, module_ver_path: Path, tmp: Path, owner: str, repo: str, tag: str) -> None:
    data = json_load(template)
    url: str = data["url"].format(OWNER=owner, REPO=repo, TAG=tag)
    data["url"] = url

    tmp.mkdir(exist_ok=True)
    pack = tmp.joinpath(url.rsplit("/", maxsplit=1)[1])
    download_file(url, pack)
    data["integrity"] = integrity(read(pack))

    if str(pack).endswith(".zip"):
        extract_zip(pack, tmp)
    else:
        extract_tar_gz(pack, tmp)

    file = list(tmp.glob("**/MODULE.bazel"))[0]
    shutil.copyfile(file, module_ver_path.joinpath("MODULE.bazel"))

    json_dump(module_ver_path.joinpath("source.json"), data)


def publish(tag: str | None) -> None:
    module_repo_path = Path(os.getcwd()).absolute()
    registry_repo_path = Path(__file__).absolute().parent.parent

    module_name = get_module_name()
    if tag is None:
        tag = get_latest_tag()

    ver = tag.replace("v", "")
    print(f"Publishing: {module_name}@{ver}", flush=True)

    os.chdir(registry_repo_path)
    subprocess.run(f"git checkout -b {module_name}-{ver}".split(), check=True)
    os.chdir(module_repo_path)

    module = registry_repo_path.joinpath("modules", module_name)
    module_ver_path = module.joinpath(ver)
    module_ver_path.mkdir(parents=True, exist_ok=True)

    (owner, repo) = update_metadata(
        module_repo_path.joinpath(".br", "metadata.template.json"),
        module.joinpath("metadata.json"),
        ver,
    )
    update_source(
        module_repo_path.joinpath(".br", "source.template.json"),
        module_ver_path,
        registry_repo_path.joinpath("tmp"),
        owner,
        repo,
        tag,
    )

    os.chdir(registry_repo_path)
    subprocess.run("git add .".split(), check=True)
    subprocess.run(f"git commit -m {module_name}@{ver}".split(), check=True)
    # subprocess.run("git push --force".split(), check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tag", type=str)
    opts = parser.parse_args()

    publish(opts.tag)
