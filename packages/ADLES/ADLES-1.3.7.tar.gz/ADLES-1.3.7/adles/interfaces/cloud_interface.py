# -*- coding: utf-8 -*-

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

import logging

from adles.interfaces.libcloud_interface import LibcloudInterface


class CloudInterface(LibcloudInterface):
    """Generic interface for all cloud platforms."""
    __version__ = "0.2.0"

    def __init__(self, infra, spec):
        """
        :param dict infra: Dict of infrastructure information
        :param dict spec: Dict of a parsed specification
        """
        super(self.__class__, self).__init__(infra=infra, spec=spec)
        self._log = logging.getLogger(str(self.__class__))
        self._log.debug("Initializing %s %s", self.__class__, self.__version__)
        self.max_instance_price = float(infra["max-instance-price"])
        self.max_total_price = float(infra["max-total-price"])

        # Cache currently available images and sizes
        self.available_images = self.provider.list_images()
        self.available_sizes = self.provider.list_sizes()
        self._log.debug(self.available_images)
        self._log.debug(self.available_sizes)

    def create_masters(self):
        pass

    def deploy_environment(self):
        pass

    def cleanup_masters(self, network_cleanup=False):
        pass

    def cleanup_environment(self, network_cleanup=False):
        pass

    def __str__(self):
        return str(self.provider_name)

    def __eq__(self, other):
        return super(self.__class__, self).__eq__(other) \
               and self.provider_name == other.provider_name \
               and self.username == other.username \
               and self.api_key == other.api_key
