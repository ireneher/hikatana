import logging

from Katana import Utils

import Constants


def upgrade(node):
    Utils.UndoStack.DisableCapture()
    try:
        # Detect out-of-date version and upgrade the internal network.
        if (
            node.getParameter(Constants.VERSION_PARAM).getValue(0.0)
            != Constants.CURRENT_VERSION
        ):
            # No versions beyond 1 yet, so nothing to do here
            return

    except Exception as exception:
        logging.error(
            "Error upgrading HIMeshLights node {}: {}".format(
                node.getName(), str(exception)
            )
        )
    finally:
        Utils.UndoStack.EnableCapture()
