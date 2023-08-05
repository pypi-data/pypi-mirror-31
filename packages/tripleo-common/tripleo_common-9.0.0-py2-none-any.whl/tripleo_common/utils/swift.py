# Copyright 2016 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import tempfile

from tripleo_common import constants
from tripleo_common.utils import tarball

LOG = logging.getLogger(__name__)


def empty_container(swiftclient, name):
    container_names = [container["name"] for container
                       in swiftclient.get_account()[1]]

    if name in container_names:
        headers, objects = swiftclient.get_container(name)
        # ensure container is a plan
        if headers.get(constants.TRIPLEO_META_USAGE_KEY) != 'plan':
            error_text = ("The {name} container does not contain a "
                          "TripleO deployment plan and was not "
                          "deleted.".format(name=name))
            raise ValueError(error_text)
        else:
            # FIXME(rbrady): remove delete_object loop when
            # LP#1615830 is fixed.  See LP#1615825 for more info.
            # delete files from plan
            for o in objects:
                swiftclient.delete_object(name, o['name'])
    else:
        error_text = "The {name} container does not exist.".format(name=name)
        raise ValueError(error_text)


def delete_container(swiftclient, name):
    try:
        empty_container(swiftclient, name)
        swiftclient.delete_container(name)
    except ValueError as e:
        # ValueError is raised when we can't find the container, which means
        # that it's already deleted.
        LOG.info(e.message)


def download_container(swiftclient, container, dest):
    """Download the contents of a Swift container to a directory"""

    objects = swiftclient.get_container(container)[1]

    for obj in objects:
        filename = obj['name']
        contents = swiftclient.get_object(container, filename)[1]
        path = os.path.join(dest, filename)
        dirname = os.path.dirname(path)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(path, 'w') as f:
            f.write(contents)


def create_container(swiftclient, container):
    # If the container already exists, it will return 202 and everything will
    # work
    swiftclient.put_container(container)


def create_and_upload_tarball(swiftclient,
                              tmp_dir,
                              container,
                              tarball_name,
                              tarball_options='-czf',
                              delete_after=3600):
    """Create a tarball containing the tmp_dir and upload it to Swift."""
    headers = {'X-Delete-After': delete_after}

    create_container(swiftclient, container)

    with tempfile.NamedTemporaryFile() as tmp_tarball:
        tarball.create_tarball(tmp_dir, tmp_tarball.name, tarball_options)
        swiftclient.put_object(container, tarball_name, tmp_tarball,
                               headers=headers)
