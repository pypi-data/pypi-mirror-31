"""
Authenticated HTTP proxy for Jupyter Notebooks

Some original inspiration from https://github.com/senko/tornado-proxy
"""
from datetime import datetime
import inspect
import socket
import os
from urllib.parse import urlunparse, urlparse

from tornado import gen, web, httpclient, httputil, process, websocket, ioloop

from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler


class AddSlashHandler(IPythonHandler):
    """Add trailing slash to URLs that need them."""
    @web.authenticated
    def get(self, *args):
        src = urlparse(self.request.uri)
        dest = src._replace(path=src.path + '/')
        self.redirect(urlunparse(dest))

# from https://stackoverflow.com/questions/38663666/how-can-i-serve-a-http-page-and-a-websocket-on-the-same-url-in-tornado
class WebSocketHandlerMixin(websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # since my parent doesn't keep calling the super() constructor,
        # I need to do it myself
        bases = inspect.getmro(type(self))
        assert WebSocketHandlerMixin in bases
        meindex = bases.index(WebSocketHandlerMixin)
        try:
            nextparent = bases[meindex + 1]
        except IndexError:
            raise Exception("WebSocketHandlerMixin should be followed "
                            "by another parent to make sense")

        # undisallow methods --- t.ws.WebSocketHandler disallows methods,
        # we need to re-enable these methods
        def wrapper(method):
            def undisallow(*args2, **kwargs2):
                getattr(nextparent, method)(self, *args2, **kwargs2)
            return undisallow

        for method in ["write", "redirect", "set_header", "set_cookie",
                       "set_status", "flush", "finish"]:
            setattr(self, method, wrapper(method))
        nextparent.__init__(self, *args, **kwargs)

    async def get(self, *args, **kwargs):
        if self.request.headers.get("Upgrade", "").lower() != 'websocket':
            return await self.http_get(*args, **kwargs)
        # super get is not async
        super().get(*args, **kwargs)


class LocalProxyHandler(WebSocketHandlerMixin, IPythonHandler):
    async def open(self, port, proxied_path=''):
        """
        Called when a client opens a websocket connection.

        We establish a websocket connection to the proxied backend &
        set up a callback to relay messages through.
        """
        if not proxied_path.startswith('/'):
            proxied_path = '/' + proxied_path

        client_uri = '{uri}:{port}{path}'.format(
            uri='ws://127.0.0.1',
            port=port,
            path=proxied_path
        )
        if self.request.query:
            client_uri += '?' + self.request.query
        headers = self.request.headers

        def cb(message):
            """
            Callback when the backend sends messages to us

            We just pass it back to the frontend
            """
            # Websockets support both string (utf-8) and binary data, so let's
            # make sure we signal that appropriately when proxying
            self._record_activity()
            if message is None:
                self.close()
            else:
                self.write_message(message, binary=type(message) is bytes)

        async def start_websocket_connection():
            self.log.info('Trying to establish websocket connection to {}'.format(client_uri))
            self._record_activity()
            request = httpclient.HTTPRequest(url=client_uri, headers=headers)
            self.ws = await websocket.websocket_connect(request, on_message_callback=cb)
            self._record_activity()
            self.log.info('Websocket connection established to {}'.format(client_uri))

        ioloop.IOLoop.current().add_callback(start_websocket_connection)

    def on_message(self, message):
        """
        Called when we receive a message from our client.

        We proxy it to the backend.
        """
        self._record_activity()
        if hasattr(self, 'ws'):
            self.ws.write_message(message)

    def on_ping(self, data):
        """
        Called when the client pings our websocket connection.

        We proxy it to the backend.
        """
        self.log.info('on_ping: {}'.format(data))
        self._record_activity()
        if hasattr(self, 'ws'):
            self.ws.ping(data)

    def on_pong(self, data):
        """
        Called when we receive a ping back.
        """
        self.log.info('on_pong: {}'.format(data))

    def on_close(self):
        """
        Called when the client closes our websocket connection.

        We close our connection to the backend too.
        """
        if hasattr(self, 'ws'):
            self.ws.close()

    def _record_activity(self):
        """Record proxied activity as API activity

        avoids proxied traffic being ignored by the notebook's
        internal idle-shutdown mechanism
        """
        self.settings['api_last_activity'] = datetime.utcnow()


    @web.authenticated
    async def proxy(self, port, proxied_path):
        '''
        While self.request.uri is
            (hub)    /user/username/proxy/([0-9]+)/something.
            (single) /proxy/([0-9]+)/something
        This serverextension is given {port}/{everything/after}.
        '''

        if 'Proxy-Connection' in self.request.headers:
            del self.request.headers['Proxy-Connection']

        self._record_activity()

        if self.request.headers.get("Upgrade", "").lower() == 'websocket':
            # We wanna websocket!
            # jupyterhub/nbserverproxy@36b3214
            self.log.info("we wanna websocket, but we don't define WebSocketProxyHandler")
            self.set_status(500)

        body = self.request.body
        if not body:
            if self.request.method == 'POST':
                body = b''
            else:
                body = None

        client_uri = '{uri}:{port}{path}'.format(
            uri='http://localhost',
            port=port,
            path=proxied_path
        )
        if self.request.query:
            client_uri += '?' + self.request.query

        client = httpclient.AsyncHTTPClient()

        req = httpclient.HTTPRequest(
            client_uri, method=self.request.method, body=body,
            headers=self.request.headers, follow_redirects=False)

        response = await client.fetch(req, raise_error=False)
        # record activity at start and end of requests
        self._record_activity()

        # For all non http errors...
        if response.error and type(response.error) is not httpclient.HTTPError:
            self.set_status(500)
            self.write(str(response.error))
        else:
            self.set_status(response.code, response.reason)

            # clear tornado default header
            self._headers = httputil.HTTPHeaders()

            for header, v in response.headers.get_all():
                if header not in ('Content-Length', 'Transfer-Encoding',
                    'Content-Encoding', 'Connection'):
                    # some header appear multiple times, eg 'Set-Cookie'
                    self.add_header(header, v)

            if response.body:
                self.write(response.body)

    # Support all the methods that torando does by default except for GET which
    # is passed to WebSocketHandlerMixin and then to WebSocketHandler.

    async def http_get(self, port, proxy_path=''):
        '''Our non-websocket GET.'''
        return await self.proxy(port, proxy_path)

    def post(self, port, proxy_path=''):
        return self.proxy(port, proxy_path)

    def put(self, port, proxy_path=''):
        return self.proxy(port, proxy_path)

    def delete(self, port, proxy_path=''):
        return self.proxy(port, proxy_path)

    def head(self, port, proxy_path=''):
        return self.proxy(port, proxy_path)

    def patch(self, port, proxy_path=''):
        return self.proxy(port, proxy_path)

    def options(self, port, proxy_path=''):
        return self.proxy(port, proxy_path)

    def check_xsrf_cookie(self):
        '''
        http://www.tornadoweb.org/en/stable/guide/security.html

        Defer to proxied apps.
        '''
        pass

    def select_subprotocol(self, subprotocols):
        '''Select a single Sec-WebSocket-Protocol during handshake.'''
        if type(subprotocols) == list:
            self.log.info('Client sent subprotocols: {}'.format(subprotocols))
            return subprotocols[0]
        return super().select_subprotocol(subprotocols)

class SuperviseAndProxyHandler(LocalProxyHandler):
    '''Manage a given process and requests to it '''

    def initialize(self, state):
        self.state = state

    name = 'process'

    @property
    def port(self):
        """
        Allocate a random empty port for use by application
        """
        if 'port' not in self.state:
            sock = socket.socket()
            sock.bind(('', 0))
            self.state['port'] = sock.getsockname()[1]
            sock.close()
        return self.state['port']

    async def is_running(self, proc):
        '''Check if our proxied process is still running.'''

        # Check if the process is still around
        if proc.proc.poll() == 0:
            self.log.info('Poll failed for', self.name)
            return False

        client = httpclient.AsyncHTTPClient()
        req = httpclient.HTTPRequest('http://localhost:{}'.format(self.port))

        try:
            await client.fetch(req)
            self.log.debug('Got positive response from proxied', self.name)
        except:
            self.log.debug('Got negative response from proxied', self.name)
            return False

        return True


    def get_env(self):
        '''Set up extra environment variables for process. Typically
           overridden in subclasses.'''
        return {}


    async def start_process(self):
        """
        Start the process
        """
        if 'starting' in self.state:
            raise Exception("Process {} start already pending, can not start again".format(self.name))
        if 'proc' in self.state:
            raise Exception("Process {} already running, can not start".format(self.name))
        self.state['starting'] = True
        cmd = self.get_cmd()

        server_env = os.environ.copy()

        # Set up extra environment variables for process
        server_env.update(self.get_env())

        def exit_callback(code):
            """
            Callback when the process dies
            """
            self.log.info('{} died with code {}'.format(self.name, code))
            del self.state['proc']
            if code != 0 and not 'starting' in self.state:
                ioloop.IOLoop.current().add_callback(self.start_process)

        # Runs process in background
        proc = process.Subprocess(cmd, env=server_env)
        self.log.info('Starting process...')
        proc.set_exit_callback(exit_callback)

        for i in range(5):
            if (await self.is_running(proc)):
                self.log.info('{} startup complete'.format(self.name))
                break
            # Simple exponential backoff
            wait_time = max(1.4 ** i, 5)
            self.log.debug('Waiting {} before checking if {} is up'.format(wait_time, self.name))
            await gen.sleep(wait_time)
        else:
            raise web.HTTPError('could not start {} in time'.format(self.name), status_code=500)

        # add proc to state only after we are sure it has started
        self.state['proc'] = proc

        del self.state['starting']

    @web.authenticated
    async def proxy(self, port, path):
        if not path.startswith('/'):
            path = '/' + path

        await self.conditional_start()

        return await super().proxy(self.port, path)

    async def conditional_start(self):
        if 'starting' in self.state:
            self.log.info('{} already starting, waiting for it to start...'.format(self.name))
            for i in range(5):
                if 'proc' in self.state:
                    self.log.info('{} startup complete'.format(self.name))
                    break
                # Simple exponential backoff
                wait_time = max(1.4 ** i, 5)
                self.log.debug('Waiting {} before checking if process is up'.format(wait_time))
                await gen.sleep(wait_time)
            else:
                raise web.HTTPError('{} did not start in time'.format(self.name), status_code=500)
        else:
            if 'proc' not in self.state:
                self.log.info('No existing {} found'.format(self.name))
                await self.start_process()

    async def http_get(self, path):
        return await self.proxy(self.port, path)

    async def open(self, path):
        await self.conditional_start()
        return await super().open(self.port, path)

    def post(self, path):
        return self.proxy(self.port, path)

    def put(self, path):
        return self.proxy(self.port, path)

    def delete(self, path):
        return self.proxy(self.port, path)

    def head(self, path):
        return self.proxy(self.port, path)

    def patch(self, path):
        return self.proxy(self.port, path)

    def options(self, path):
        return self.proxy(self.port, path)

def setup_handlers(web_app):
    host_pattern = '.*$'
    web_app.add_handlers('.*', [
        (url_path_join(web_app.settings['base_url'], r'/proxy/(\d+)(.*)'), LocalProxyHandler)
    ])

# vim: set et ts=4 sw=4:
