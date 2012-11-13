# Copyright (c) 2012 Mitch Garnaat http://garnaat.org/
# Copyright 2012 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
from .endpoint import get_endpoint
from .base import get_service_data


class Service(object):
    """
    A service, such as Elastic Compute Cloud (EC2).

    :ivar api_version: A string containing the API version this service
        is using.
    :ivar endpoints: A list of Endpoint objects for each region in which
        the service is supported.
    :ivar name: The full name of the service.
    :ivar service_name: The canonical name of the service.
    :ivar regions: A dict where each key is a region name and the
        optional value is an endpoint for that region.
    :ivar protocols: A list of protocols supported by the service.
    """

    def __init__(self, provider_name, service_name, path='/', port=None):
        self.__dict__.update(get_service_data(service_name, provider_name))
        self.provider_name = provider_name
        self.path = path
        self.port = port
        self.cli_name = self.short_name
        self.endpoints = [self.get_endpoint(rn) for rn in self.regions]

    def __repr__(self):
        return 'Service(%s)' % self.name

    def get_endpoint(self, region_name, is_secure=True,
                     profile=None, endpoint_url=None):
        """
        Return the Endpoint object for this service in a particular
        region.

        :type region_name: str
        :param region_name: The name of the region.

        :type is_secure: bool
        :param is_secure: True if you want the secure (HTTPS) endpoint.
        """
        if region_name not in self.regions:
            raise ValueError('Service: %s not available in region: %s' %
                             (self.service_name, region_name))
        endpoint_url = endpoint_url or self.regions[region_name]
        if endpoint_url is None:
            if is_secure:
                scheme = 'https'
            else:
                scheme = 'http'
            if scheme not in self.protocols:
                raise ValueError('Unsupported protocol: %s' % scheme)
            host = '%s.%s.amazonaws.com' % (self.short_name, region_name)
            endpoint_url = '%s://%s%s' % (scheme, host, self.path)
            if self.port:
                endpoint_url += ':%d' % self.port
        return get_endpoint(self, region_name, endpoint_url, profile)


def get_service(service_name, provider_name='aws'):
    """
    Return a Service object for a given provider name and service name.

    :type service_name: str
    :param service_name: The name of the service.

    :type provider_name: str
    :param provider_name: The name of the provider.
    """
    return Service(provider_name, service_name)
