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
            if not node.getParameter(Constants.TYPE_PARAM):
                typeParam = node.getParameters().createChildString(Constants.TYPE_PARAM, Constants.DEFAULT_TYPE)
                typeParam.setHintString(repr({"widget": "popup",
                                              "options": Constants.TYPE_OPTIONS,
                                              "label": "Light type  ",
                                              }))
            return

    except Exception as exception:
        logging.error(
            "Error upgrading HIMeshLights node {}: {}".format(
                node.getName(), str(exception)
            )
        )
    finally:
        Utils.UndoStack.EnableCapture()
