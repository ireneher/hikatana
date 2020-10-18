# Import PyQt5 or PyQt4 (depends on Katana version)
try:
    import PyQt5

except ImportError:
    print("PyQt5 not available")
    try:
        import PyQt4

    except ImportError:
        print("PyQt4 not available")
        raise
    else:
        from Katana import QtCore, QtGui

        class QtModuleCompatibility(object):
            def __getattr__(self, attr):
                return getattr(QtGui, attr)

        QtWidgets = QtModuleCompatibility()
else:
    from Katana import QtCore, QtGui, QtWidgets

from Katana import NodegraphAPI, UI4, RenderManager, Qt


class NodesTableWidget(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super(NodesTableWidget, self).__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_E:
            if self.currentItem():
                node = NodegraphAPI.GetNode(str(self.currentItem().text()))
                NodegraphAPI.SetNodeEdited(node, True, exclusive=True)
        else:
            super(NodesTableWidget, self).keyPressEvent(event)


class NodeControlPanel(UI4.Tabs.BaseTab):
    def __init__(self, parent):
        UI4.Tabs.BaseTab.__init__(self, parent)

        self.h_layout = QtWidgets.QHBoxLayout()
        self.mode = QtWidgets.QComboBox(self)
        self.mode.addItem("Type")
        self.mode.addItem("Name")
        self.mode.addItem("Selection")
        self.h_layout.addWidget(self.mode)

        self.input = QtWidgets.QLineEdit()
        self.input.setText("Render")
        self.h_layout.addWidget(self.input)

        self.checkbox_enable = QtWidgets.QCheckBox("Enabled nodes only")
        self.h_layout.addWidget(self.checkbox_enable)

        self.checkbox_add = QtWidgets.QCheckBox("Add")
        self.h_layout.addWidget(self.checkbox_add)

        self.button = QtWidgets.QPushButton("Get nodes")
        self.button.clicked.connect(self._process_input)
        self.h_layout.addWidget(self.button)

        self.node_list = NodesTableWidget()
        self.node_list.verticalHeader().setVisible(False)
        self.node_list.horizontalHeader().setVisible(False)

        self.node_list.setColumnCount(3)
        self._populate_ui(NodegraphAPI.GetAllNodesByType("Render"))

        self.v_layout = QtWidgets.QVBoxLayout()
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(self.node_list)
        self.setLayout(self.v_layout)
        self.node_list.itemClicked.connect(self._on_render_clicked)

    def _populate_ui(self, collected_nodes):
        if not self.checkbox_add.isChecked():
            self.node_list.clear()
            self.node_list.setRowCount(0)

        offset = self.node_list.rowCount()

        self.node_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        for row, node in enumerate(collected_nodes):
            # Add row
            self.node_list.insertRow(row + offset)

            # Create table items
            node_item = QtWidgets.QTableWidgetItem(node.getName())
            live_button = QtWidgets.QTableWidgetItem("Live")
            preview_button = QtWidgets.QTableWidgetItem("Preview")

            # Set item styles
            self.set_item_style(live_button, "#FFFFFF", "#007f00")
            self.set_item_style(preview_button, "#FFFFFF", "#0000b2")
            self.set_item_style(node_item)

            # Add items to table
            self.node_list.setItem(row + offset, 0, live_button)
            self.node_list.setItem(row + offset, 1, node_item)
            self.node_list.setItem(row + offset, 2, preview_button)

        if Qt.PYQT_VERSION_STR.split(".")[0] < "5":
            self.node_list.horizontalHeader().setResizeMode(
                1, QtWidgets.QHeaderView.Stretch
            )
        else:
            self.node_list.horizontalHeader().setSectionResizeMode(
                1, QtWidgets.QHeaderView.Stretch
            )

    def set_item_style(self, item, colour=None, bg=None):
        if colour:
            item.setForeground(QtGui.QBrush(QtGui.QColor(colour)))
        if bg:
            item.setBackground(QtGui.QBrush(QtGui.QColor(bg)))
        item.setTextAlignment(QtCore.Qt.AlignCenter)

    def _process_input(self):
        mode = str(self.mode.currentText())
        user_input = str(self.input.text())
        collected_nodes = []
        if mode == "Type":
            collected_nodes = NodegraphAPI.GetAllNodesByType(user_input)
        elif mode == "Name":
            collected_nodes = find_partially_matching_nodes(user_input)
        elif mode == "Selection":
            collected_nodes = NodegraphAPI.GetAllSelectedNodes()

        if self.checkbox_enable.isChecked():
            collected_nodes = [
                node for node in collected_nodes if not node.isBypassed()
            ]

        self._populate_ui(collected_nodes)

    def _on_render_clicked(self, item):
        node_name = str(self.node_list.item(item.row(), 1).text())
        render_node = NodegraphAPI.GetNode(node_name)
        if item.column() == 0:
            RenderManager.StartRender(
                renderMethodName="liveRender",
                node=render_node,
                renderMethodType="liveRender",
                renderer="arnold",
            )
        elif item.column() == 2:
            RenderManager.StartRender(
                renderMethodName="previewRender",
                node=render_node,
                renderMethodType="previewRender",
                renderer="arnold",
            )

        elif item.column() == 1:
            NodegraphAPI.SetNodeViewed(render_node, True, exclusive=True)
            NodegraphAPI.SetAllSelectedNodes([render_node])


def find_partially_matching_nodes(input):
    """
    Partial Nodegraph search. Non-cap sensitive.
    :param input: user input
    :type C{str}
    :return: Nodes that match input
    """
    input = input.lower()
    return [
        node for node in NodegraphAPI.GetAllNodes() if input in node.getName().lower()
    ]


PluginRegistry = [
    ("KatanaPanel", 2.0, "Node Control Panel", NodeControlPanel)
]