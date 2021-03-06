# Copyright 2014 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_concurrency import lockutils

from neutron.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class AdvancedService(object):
    """Observer base class for Advanced Services.

    Base class for service types. This should not be instantiated normally.
    Instead, a child class is defined for each service type and instantiated
    by the corresponding service agent. The instances will have a back
    reference to the L3 agent, and will register as an observer of events.
    A singleton is used to create only one service object per service type.

    This base class provides a definition for all of the L3 event handlers
    that a service could "observe". A child class for a service type will
    implement handlers, for events of interest.
    """

    _instance = None

    def __init__(self, l3_agent):
        """Base class for an advanced service.

        Do not directly instantiate objects of this class. Should only be
        called indirectly by a child class's instance() invocation.
        """
        self.l3_agent = l3_agent
        # NOTE: Copying L3 agent attributes, so that they are accessible
        # from device drivers, which are now provided a service instance.
        # TODO(pcm): Address this in future refactorings.
        self.conf = l3_agent.conf
        self.root_helper = l3_agent.root_helper

    @classmethod
    def instance(cls, l3_agent):
        """Creates instance (singleton) of service.

        Do not directly call this for the base class. Instead, it should be
        called by a child class, that represents a specific service type.

        This ensures that only one instance is created for all agents of a
        specific service type.
        """
        if not cls._instance:
            with lockutils.lock('instance'):
                if not cls._instance:
                    cls._instance = cls(l3_agent)

        return cls._instance

    # NOTE: Handler definitions for events generated by the L3 agent.
    # Subclasses of AdvancedService can override these to perform service
    # specific actions. Unique methods are defined for add/update, as
    # some services may want to take different actions.
    def before_router_added(self, ri):
        """Actions taken before router_info created."""
        pass

    def after_router_added(self, ri):
        """Actions taken after router_info created."""
        pass

    def before_router_updated(self, ri):
        """Actions before processing for an updated router."""
        pass

    def after_router_updated(self, ri):
        """Actions add processing for an updated router."""
        pass

    def before_router_removed(self, ri):
        """Actions before removing router."""
        pass

    def after_router_removed(self, ri):
        """Actions after processing and removing router."""
        pass
