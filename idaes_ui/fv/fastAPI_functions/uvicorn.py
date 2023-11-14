"""
Define how to use uvicorn to serve fastAPI app
"""

import sys
import asyncio
import uvicorn
import webbrowser
import threading


class WebUvicorn:
    def __init__(self, fastAPIApp, port):
        self.app = fastAPIApp
        self.port = port

        # run uvicorn serve web app
        self.run()

    def open_browser(self, port: int):
        """When FastAPI run, open browser on localhost with port.

        Args:
            port: the port FastAPI app running on, will open browser window with this port.
        """
        webbrowser.open(f"http://127.0.0.1:{self.port}")

    async def serve(self):
        """Setup uvicorn server loop with asyncio

        Args:
            port: the port FastAPI app running on.

        Returns:
            server: configed uvicorn server
        """
        # Replace 'config' with the appropriate uvicorn configuration
        config = uvicorn.Config(
            self.app, host="127.0.0.1", port=self.port, loop="asyncio"
        )
        server = uvicorn.Server(config)
        await server.serve()
        return server

    def run(self):
        """Run FastAPI server with uvicorn, also call open browser but delay 1.5s

        Args:
            port: the port FastAPI app running on.
        """
        loop = asyncio.get_event_loop()

        # Check if we are in a Jupyter notebook environment & not has nest_asyncio we need import it or error: event already running
        if "ipykernel" in sys.modules and "nest_asyncio" not in sys.modules:
            import nest_asyncio

            nest_asyncio.apply()

        # Open the browser after a delay
        threading.Timer(1.5, self.open_browser, args=(self.port,)).start()

        # Run the uvicorn server
        loop.run_until_complete(self.serve())