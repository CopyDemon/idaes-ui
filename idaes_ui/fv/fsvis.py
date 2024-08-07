#################################################################################
# The Institute for the Design of Advanced Energy Systems Integrated Platform
# Framework (IDAES IP) was produced under the DOE Institute for the
# Design of Advanced Energy Systems (IDAES).
#
# Copyright (c) 2018-2023 by the software owners: The Regents of the
# University of California, through Lawrence Berkeley National Laboratory,
# National Technology & Engineering Solutions of Sandia, LLC, Carnegie Mellon
# University, West Virginia University Research Corporation, et al.
# All rights reserved.  Please see the files COPYRIGHT.md and LICENSE.md
# for full copyright and license information.
#################################################################################
# TODO: Missing doc strings
# pylint: disable=missing-module-docstring

# stdlib
from collections import namedtuple
from pathlib import Path
import os
import sys
import time
from typing import Optional, Union, Dict, Tuple
import webbrowser
import io

# package
from idaes import logger
from .model_server import FlowsheetServer
from . import persist, errors
from IPython.display import Image as IPythonImage, display
from IPython.display import SVG

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from PIL import Image


# Logging
_log = logger.getLogger(__name__)

# Module globals
web_server = None

#: Maximum number of saved versions of the same `save` file.
#: Set to zero if you want to allow any number.
MAX_SAVED_VERSIONS = 100


# Classes and functions

#: Return value for `visualize()` function. This namedtuple has three
#: attributes that can be accessed by position or name:
#:
#: - store = :class:`idaes.core.ui.fv.persist.DataStore` object (with a ``.filename`` attribute)
#: - port = Port number (integer) where web server is listening
#: - server = :class:`idaes.core.ui.fv.model_server.FlowsheetServer` object for the web server thread
#:
VisualizeResult = namedtuple("VisualizeResult", ["store", "port", "server"])


def visualize(
    flowsheet,
    name: str = "flowsheet",
    save: Optional[Union[Path, str, bool]] = None,
    load_from_saved: bool = True,
    save_dir: Optional[Path] = None,
    save_time_interval=5000,  # 5 seconds
    overwrite: bool = False,
    browser: bool = True,
    port: Optional[int] = None,
    log_level: int = logger.WARNING,
    quiet: bool = False,
    loop_forever: bool = False,
    screenshot: bool = True,
) -> VisualizeResult:
    """Visualize the flowsheet in a web application.

    The web application is started in a separate thread and this function returns immediately.

    Also open a browser window to display the visualization app. The URL is printed unless ``quiet`` is True.

    Args:
        flowsheet: IDAES flowsheet to visualize
        name: Name of flowsheet to display as the title of the visualization
        load_from_saved: If True load from saved file if any. Otherwise create
          a new file or overwrite it (depending on 'overwrite' flag).
        save: Where to save the current flowsheet layout and values. If this argument is not specified,
          "``name``.json" will be used (if this file already exists, a "-`<version>`" number will be added
          between the name and the extension). If the value given is the boolean 'False', then nothing
          will be saved. The boolean 'True' value is treated the same as unspecified.
        save_dir: If this argument is given, and ``save`` is not given or a relative path, then it will
           be used as the directory to save the default or given file. The current working directory is
           the default. If ``save`` is given and an absolute path, this argument is ignored.
        save_time_interval: The time interval that the UI application checks if any changes has occurred
            in the graph for it to save the model. Default is 5 seconds
        overwrite: If True, and the file given by ``save`` exists, overwrite instead of creating a new
          numbered file.
        browser: If true, open a browser
        port: Start listening on this port. If not given, find an open port.
        log_level: An IDAES logging level, which is a superset of the built-in :mod:`logging` module levels.
          See the :mod:`idaes.logger` module for details
        quiet: If True, suppress printing any messages to standard output (console)
        loop_forever: If True, don't return but instead loop until a Control-C is received. Useful when
           invoking this function at the end of a script.

    Returns:
        See :data:`VisualizeResult`

    Raises:
        :mod:`idaes.core.ui.fv.errors.VisualizerSaveError`: if the data storage at 'save_as' can't be opened
        :mod:`idaes.core.ui.fv.errors.VisualizerError`: Any other errors
        RuntimeError: If too many versions of the save file already exist. See :data:`MAX_SAVED_VERSIONS`.
    """
    global web_server  # pylint: disable=global-statement

    # Initialize IDAES logging
    _init_logging(log_level)

    # Start the web server
    if web_server is None:
        web_server = FlowsheetServer(port=port)
        web_server.add_setting("save_time_interval", save_time_interval)
        web_server.start()
        if not quiet:
            _log.info("Started visualization server")
    else:
        _log.info(f"Using HTTP server on localhost, port {web_server.port}")

    # Set up save location
    use_default = False
    if save is None or save is True:
        save_path = _pick_default_save_location(name, save_dir)
        use_default = True
    elif save is False:
        save_path = None
    else:
        try:
            save_path = Path(save)
        except TypeError as err:
            raise errors.VisualizerSaveError(
                save, f"Cannot convert 'save' value to Path object: {err}"
            )
        if save_dir is not None and not save_path.is_absolute():
            save_path = save_dir / save_path
    # Create datastore for save location
    if save_path is None:
        datastore = persist.MemoryDataStore()
    else:
        if save_path.exists() and load_from_saved:
            # Load from saved
            datastore = persist.DataStore.create(save_path)
            _log.info(f"Loading saved flowsheet from '{save_path}'")
            datastore.load()
        else:
            # Create new file
            # deal with duplicate names
            try:
                save_path = _handle_existing_save_path(
                    name,
                    save_path,
                    max_versions=MAX_SAVED_VERSIONS,
                    overwrite=overwrite,
                )
            except errors.TooManySavedVersions as err:
                raise RuntimeError(f"In visualize(): {err}")
            datastore = persist.DataStore.create(save_path)

        if use_default:
            if not quiet:
                cwd = save_path.parent.absolute()
                _log.info(
                    f"Saving flowsheet to default file '{save_path.name}' in current"
                    f" directory ({cwd})"
                )
        else:
            if not quiet:
                print(f"Saving flowsheet to {str(datastore)}")

    # Add our flowsheet to it
    try:
        new_name = web_server.add_flowsheet(name, flowsheet, datastore)
    except (errors.ProcessingError, errors.DatastoreError) as err:
        raise errors.VisualizerError(f"Cannot add flowsheet: {err}")

    if new_name != name:
        _log.warning(f"Flowsheet name changed: old='{name}' new='{new_name}'")
        if not quiet:
            print(f"Flowsheet name changed to '{new_name}'")
        name = new_name

    # Open a browser window for the UI
    url = f"http://localhost:{web_server.port}/app?id={name}"
    if browser:
        success = webbrowser.open(url)
        if success:
            _log.debug("Flowsheet opened in browser window")
        else:
            _log.warning(f"Could not open flowsheet URL '{url}' in browser")

    if not quiet:
        _log.info(f"Flowsheet visualization at: {url}")

    if loop_forever:
        _loop_forever(quiet)

    if screenshot:
        print("Generating Screenshot......")
        get_screenshot(flowsheet_name=name, port=web_server.port)

    return VisualizeResult(
        store=datastore,
        port=web_server.port,
        server=web_server,
    )


def get_screenshot(flowsheet_name, port) -> str:
    # live server url
    url = f"http://localhost:{port}/app?id={flowsheet_name}"

    # Set up Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080 ")

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for the SVG element to be present
        svg_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "svg[joint-selector='svg'][id='v-2']")
            )
        )

        # Get the outer HTML of the SVG element
        svg_content = svg_element.get_attribute("outerHTML")

        # Save the SVG content to a file
        with open(f"{flowsheet_name}_svg.svg", "w", encoding="utf-8") as f:
            f.write(svg_content)

        print(f"SVG saved as {flowsheet_name}_svg.svg")

        current_path = os.getcwd()
        files_and_dirs = os.listdir(current_path)
        for item in files_and_dirs:
            print(item)

        # debug
        # with open(f"{flowsheet_name}.svg", "r") as f:
        #     svg_content = f.read()
        # print(svg_content[:500])

        # Display the SVG
        display(SVG(filename=f"{flowsheet_name}_svg.svg"))

        from IPython.display import HTML

        html_content = f'<div style="width:100%;height:600px">{svg_content}</div>'
        display(HTML(html_content))

        return svg_content

    finally:
        # Close the browser
        driver.quit()

    # here generate png ok but size is odd
    # try:
    #     # Navigate to the URL
    #     driver.get(url)

    #     # Wait for the element to be present
    #     element = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.ID, "v-2"))
    #     )

    #     # Scroll element into view
    #     driver.execute_script("arguments[0].scrollIntoView();", element)

    #     # Take screenshot of the specific element
    #     element_png = element.screenshot_as_png

    #     # Create an image from the screenshot
    #     image = Image.open(io.BytesIO(element_png))

    #     # Save or return the image
    #     image.save(f"{flowsheet_name}_screenshot.png")
    #     print(f"Screenshot saved as {flowsheet_name}_screenshot.png")
    #     display(IPythonImage(filename=f"{flowsheet_name}_screenshot.png"))

    #     return image

    # finally:
    #     # Close the browser
    #     driver.quit()


def _loop_forever(quiet):
    try:
        if not quiet:
            print("Type ^C to stop the program")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        if not quiet:
            print("Program stopped")


def _pick_default_save_location(name, save_dir):
    """Pick a default save location."""
    if not save_dir:
        save_dir = Path(".")
    save_path = save_dir / f"{name}.json"
    return save_path


def _handle_existing_save_path(name, save_path, max_versions=10, overwrite=None):
    """Set up for overwrite/versioning for existing save paths."""
    save_dir = save_path.parent
    # Handle simple cases: overwrite, and no existing file
    if overwrite:
        if save_path.exists():
            _log.warning(f"Overwriting existing save file '{save_path}'")
            save_path.open("w")  # blank file
        return save_path
    elif not save_path.exists():
        return save_path
    # Find the next version that does not exist
    _log.info(f"Save file {save_path} exists. Creating new version")
    counter = 0
    if max_versions == 0:
        max_versions = sys.maxsize  # millions of years of file-creating fun
    while save_path.exists() and counter < max_versions:
        counter += 1
        save_file = f"{name}-{counter}.json"
        save_path = save_dir / save_file
    # Edge case: too many NAME-#.json files for this NAME
    if counter == max_versions:
        why = (
            f"Found {max_versions} numbered files of form '{name}-<num>.json'. That's"
            " too many."
        )
        _log.error(why)
        raise errors.TooManySavedVersions(why)
    # Return new (versioned) path
    _log.info(f"Created new version for save file: {save_path}")
    return save_path


def _init_logging(lvl):
    ui_logger = logger.getIdaesLogger("ui", level=lvl, tag="ui")
    ui_logger.setLevel(lvl)
