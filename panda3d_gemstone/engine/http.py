"""
MIT License

Copyright (c) 2024 Jordan Maxwell

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import traceback

from panda3d_gemstone.framework.internal_object import InternalObject
from panda3d_gemstone.framework.singleton import Singleton
from panda3d_gemstone.framework.runnable import Runnable

from panda3d.core import HTTPClient, HTTPChannel, DocumentSpec
from panda3d.core import Ramfile, UniqueIdAllocator, ConfigVariableInt

class HTTPManager(Singleton, Runnable, InternalObject):
    """
    Singleton object for handling GET/POST requests with Panda3D internal
    HTTPClient object
    """

    def __init__(self):
        Singleton.__init__(self)
        Runnable.__init__(self)
        InternalObject.__init__(self)

        self._http_client = HTTPClient()

        max_http_requests = ConfigVariableInt('http-max-requests', 900).value
        self._request_allocator = UniqueIdAllocator(0, max_http_requests)
        self._poll_task = None
        self._requests = {}

        self.activate()

    async def tick(self, dt: float) -> None:
        """
        Called once per frame to update any pending HTTP request
        objects
        """

        for request_id in list(self._requests):

            # Check that this id is still valid
            if request_id not in self._requests:
                continue

            request = self._requests[request_id]
            await request.tick()

    def destroy(self) -> None:
        """
        Destroys the http manager object
        """

        Singleton.destroy(self)
        InternalObject.destroy(self)

        for request_id in list(self._requests):
            self.remove_request(request_id)

        self.deactivate()

    def remove_request(self, request_id: object) -> None:
        """
        Removes the request id form the PandaHTTP request list
        """
        
        if request_id not in self._requests:
            return

        self._request_allocator.free(request_id)
        del self._requests[request_id]

    def get_request_status(self, request_id: object) -> bool:
        """
        Returns the requests current status
        """

        return not request_id in self._requests

    def get_request(self, request_id: object) -> object:
        """
        Returns the requested request if its present
        """

        return self._requests.get(request_id, None)

    def perform_get_request(self, url: str, headers: dict = {}, content_type: str = None, callback: object = None) -> object:
        """
        Performs an HTTP restful GET call and returns the request's unique itentifier
        """

        self.notify.debug('Sending GET request: %s' % url)

        request_channel = self._http_client.make_channel(True)

        if content_type != None:
            request_channel.set_content_type(content_type)

        for header_key in headers:
            header_value = headers[header_key]
            request_channel.send_extra_header(header_key, header_value)

        request_channel.begin_get_document(DocumentSpec(url))

        ram_file = Ramfile()
        request_channel.download_to_ram(ram_file, False)

        request_id = self._request_allocator.allocate()
        http_request = HTTPRequest(self, request_id, request_channel, ram_file, callback)
        self._requests[request_id] = http_request

        return request_id

    def perform_json_get_request(self, url: str, headers: dict = {}, callback: object = None) -> object:
        """
        """

        def json_wrapper(data: str) -> None:
            """
            Wraps the callback to automatically perform json.load
            on the resulting data
            """

            try:
                data = json.loads(data)
            except:
                self.notify.warning('Received invalid JSON results: %s' % data)
                
            callback(data)

        return self.perform_get_request(
            url=url, 
            content_type='application/json',
            headers=headers,
            callback=json_wrapper)

    def perform_post_request(self, url: str, headers: dict = {}, content_type: str = None, post_body: dict = {}, callback: object = None) -> object:
        """
        """

        self.notify.debug('Sending POST request: %s' % url)

        request_channel = self._http_client.make_channel(True)

        if content_type != None:
            request_channel.set_content_type(content_type)

        for header_key in headers:
            header_value = headers[header_key]
            request_channel.send_extra_header(header_key, header_value)

        post_body = json.dumps(post_body)
        request_channel.begin_post_form(DocumentSpec(url), post_body)

        ram_file = Ramfile()
        request_channel.download_to_ram(ram_file, False)

        request_id = self._request_allocator.allocate()
        http_request = HTTPRequest(self, request_id, request_channel, ram_file, callback)
        self._requests[request_id] = http_request

        return request_id

    def perform_json_post_request(self, url: str, headers: dict = {}, post_body: dict = {}, callback: object = None) -> object:
        """
        """

        def json_wrapper(data: str) -> None:
            """
            Wraps the callback to automatically perform json.load
            on the resulting data
            """

            try:
                data = json.loads(data)
            except:
                self.notify.warning('Received invalid JSON results: %s' % data)

            callback(data)

        return self.perform_post_request(
            url=url, 
            content_type='application/json',
            headers=headers,
            post_body=post_body, 
            callback=json_wrapper)

    def get_notify_name(self) -> str:
        """
        Returns this object's notifier name
        """

        return 'http-manager'

class HTTPRequest(InternalObject):
    """
    Represents an inprogres HTTP request
    """

    def __init__(self, rest: HTTPManager, request_id: object, channel: object, ram_file: object, callback: object = None):
        super().__init__()
        self._rest = rest
        self._request_id = request_id
        self._channel = channel
        self._callback = callback
        self._ram_file = ram_file
    
    @property
    def request_id(self) -> object:
        return self._request_id

    @property
    def channel(self) -> object:
        return self._channel

    @property
    def ram_file(self) -> object:
        return self._ram_file

    async def tick(self) -> None:
        """
        Performs the run operations and finishing callbacks
        for the request's channel instance
        """

        if self._channel == None:
            return

        done = not self._channel.run()
        if done:
            self.notify.debug('Completed request: %s' % self._request_id)
            
            if self._callback != None:
                try:
                    self._callback(self._ram_file.get_data())
                except:
                    self.notify.warning('Exception occured processing callback')
                    self.notify.warning(traceback.format_exc())

            self._rest.remove_request(self._request_id)

    def get_notify_name(self) -> str:
        """
        Returns this object's notifier name
        """

        return 'http-request'