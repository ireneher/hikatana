import logging

from Katana import NodegraphAPI, Utils

import Constants


def upgrade(node):
    Utils.UndoStack.DisableCapture()
    try:
        # Detect out-of-date version and upgrade the internal network.
        if (
            node.getParameter(Constants.VERSION_PARAM).getValue(0.0)
            != Constants.CURRENT_VERSION
        ):
            return

    except Exception as exception:
        logging.warning(
            "Error upgrading HIColourCollections node {}: {}".format(
                node.getName(), str(exception)
            )
        )
    finally:
        Utils.UndoStack.EnableCapture()
