import subprocess
import os, glob
from datetime import datetime

import pulumi
import pulumi_docker as docker

VERSION_FILE = "VERSION"

def get_latest_commit_message():
    return subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode().strip()

def read_current_version():
    if not os.path.exists(VERSION_FILE):
        return "0.0.0"
    with open(VERSION_FILE, "r") as f:
        return f.read().strip()

def bump_version(current_version, commit_msg):
    major, minor, patch = map(int, current_version.split("."))
    if "[BREAKING-CHANGE]" in commit_msg:
        major += 1
        minor = 0
        patch = 0
    elif "[FEATURE]" in commit_msg:
        minor += 1
        patch = 0
    elif "[FIX]" in commit_msg:
        patch += 1
    else:
        patch += 1 
    return f"{major}.{minor}.{patch}"

def write_new_version(version):
    with open(VERSION_FILE, "w") as f:
        f.write(version)

commit_msg = get_latest_commit_message()
current_version = read_current_version()
new_version = bump_version(current_version, commit_msg)
write_new_version(new_version)       

user = os.getenv("DOCKER_USERNAME")
pw   = os.getenv("DOCKER_PASSWORD")

for context in glob.glob("../build-*"):
    name = os.path.basename(context)

    img = docker.Image(
        resource_name=name,
        image_name=f"docker.io/tankengine/{name}:{new_version}",
        build=docker.DockerBuildArgs(
            context=context,
            platform="linux/amd64,linux/arm64",
            args={
                "BASE_IMAGE": os.getenv("BASE_IMAGE", "alpine:3.18"),
                "TF_VERSION":  os.getenv("TF_VERSION", "1.5.0"),
            },
        ),
        registry=docker.RegistryArgs(
            server="docker.io",
            username=user,
            password=pw,
        ),
    )

    pulumi.export(f"{name}_image", img.image_name)
