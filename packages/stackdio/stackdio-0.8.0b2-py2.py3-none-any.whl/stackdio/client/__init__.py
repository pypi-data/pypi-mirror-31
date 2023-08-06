# -*- coding: utf-8 -*-

# Copyright 2014,  Digital Reasoning
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import unicode_literals

import logging

from pkg_resources import parse_version
from .account import AccountMixin
from .blueprint import BlueprintMixin
from .config import StackdioConfig
from .exceptions import (
    BlueprintException,
    StackException,
    IncompatibleVersionException,
    MissingUrlException
)
from .formula import FormulaMixin
from .http import HttpMixin, get, post, patch
from .image import ImageMixin
from .region import RegionMixin
from .settings import SettingsMixin
from .stack import StackMixin
from .snapshot import SnapshotMixin

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class StackdioClient(BlueprintMixin, FormulaMixin, AccountMixin, ImageMixin,
                     RegionMixin, StackMixin, SettingsMixin, SnapshotMixin, HttpMixin):

    def __init__(self, url=None, username=None, password=None, verify=None, cfg_file=None):
        self.config = StackdioConfig(cfg_file)

        self._password = self.config.get_password()

        if url is not None:
            self.config['url'] = url

        if username is not None and password is not None:
            self.config['username'] = username
            self._password = password

        if verify is not None:
            self.config['verify'] = verify

        super(StackdioClient, self).__init__()

        if self.usable():
            try:
                raw_version = self.get_version(raise_for_status=False)
                self.version = parse_version(raw_version)
            except MissingUrlException:
                raw_version = None
                self.version = None

            if self.version and (int(self.version[0]) != 0 or int(self.version[1]) != 8):
                raise IncompatibleVersionException(
                    'Server version {0} not supported.  Please upgrade '
                    'stackdio-cli to {1}.{2}.0 or higher.'.format(raw_version, *self.version)
                )

    @property
    def url(self):
        return self.config.get('url')

    @property
    def username(self):
        return self.config.get('username')

    @property
    def password(self):
        return self._password or self.config.get_password()

    @property
    def verify(self):
        return self.config.get('verify', True)

    def usable(self):
        return self.url and self.username and self.password

    @get('')
    def get_root(self):
        pass

    @get('version/')
    def get_version(self):
        pass

    @get_version.response
    def get_version(self, resp):
        return resp['version']

    @post('cloud/security_groups/')
    def create_security_group(self, name, description, cloud_account, group_id, is_default=True):

        return {
            'name': name,
            'description': description,
            'cloud_account': cloud_account,
            'group_id': group_id,
            'is_default': is_default
        }
