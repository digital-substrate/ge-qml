import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Document tree panel — View+Delegate for document_model.py / commit_document_model.py
// documentModel accessed via context property.

Rectangle {
    id: root
    color: DSTheme.window

    // Column visibility
    property bool showPath: false
    property bool showType: false

    // Validation feedback — emitted so parent can display in toolbar/status bar
    signal validationFailed(int row, string expectedType)

    onShowPathChanged: documentView.forceLayout()
    onShowTypeChanged: documentView.forceLayout()

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Column headers — HorizontalHeaderView synced with TreeView
        HorizontalHeaderView {
            id: docHeader
            Layout.fillWidth: true
            syncView: documentView
            clip: true

            delegate: Rectangle {
                implicitWidth: 100
                implicitHeight: 24
                color: DSTheme.midlight
                border.color: DSTheme.separator
                border.width: 0.5

                Label {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    text: model.display
                    font.bold: true
                    color: DSTheme.secondaryText
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }

                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.RightButton
                    onClicked: (mouse) => headerContextMenu.popup()
                }
            }
        }

        // Context menu for column visibility
        Menu {
            id: headerContextMenu
            MenuItem { text: "Component"; checkable: true; checked: true; enabled: false }
            MenuItem { text: "Value"; checkable: true; checked: true; enabled: false }
            MenuItem { text: "Path"; checkable: true; checked: root.showPath; onTriggered: root.showPath = !root.showPath }
            MenuItem { text: "Type"; checkable: true; checked: root.showType; onTriggered: root.showType = !root.showType }
            DSMenuSeparator {}
            MenuItem { text: "Show All"; onTriggered: { root.showPath = true; root.showType = true } }
        }

        // Document TreeView
        TreeView {
            id: documentView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: documentModel
            resizableColumns: true

            property int selectedRow: -1
            property int hoveredRow: -1

            readonly property var initialColumnWidths: [250, 400, 180, 140]

            columnWidthProvider: function(column) {
                if (column === 2 && !root.showPath) return 0
                if (column === 3 && !root.showType) return 0
                var w = explicitColumnWidth(column)
                if (w >= 0)
                    return w
                return initialColumnWidths[column] ?? 100
            }

            delegate: Rectangle {
                id: cellDelegate
                required property int row
                required property int column
                required property int depth
                required property bool expanded
                required property bool hasChildren
                required property bool isTreeNode

                // Model roles exposed for editors (column-independent)
                property string cellValue: model.value ?? ""
                property string cellValueType: model.valueType ?? ""
                property var cellEnumCases: model.enumCases ?? []
                property int cellEnumIndex: model.enumIndex ?? 0
                property bool cellEditable: model.editable ?? false
                property bool cellIsKey: model.isKey ?? false
                property bool flashRed: false

                implicitWidth: 100
                implicitHeight: 30

                color: {
                    if (flashRed) return DSTheme.flashError
                    if (row === documentView.selectedRow) return DSTheme.highlight
                    if (row === documentView.hoveredRow) return DSTheme.hoverBackground
                    return row % 2 === 0 ? "transparent" : DSTheme.alternateBase
                }

                Behavior on color { ColorAnimation { duration: 150 } }

                // Background click handler
                MouseArea {
                    id: mouseDoc
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                    z: -1
                    onContainsMouseChanged: {
                        if (containsMouse)
                            documentView.hoveredRow = cellDelegate.row
                        else if (documentView.hoveredRow === cellDelegate.row)
                            documentView.hoveredRow = -1
                    }
                    onClicked: function(mouse) {
                        documentView.selectedRow = cellDelegate.row
                        documentModel.setSelectedIndex(documentView.index(cellDelegate.row, 0))
                        if (mouse.button === Qt.RightButton) {
                            docContextMenu.showForRow(cellDelegate.row)
                        }
                    }
                    onDoubleClicked: {
                        var idx = documentView.index(cellDelegate.row, 0)
                        if (cellDelegate.cellIsKey)
                            documentModel.tryJumpToKey(idx)
                        else if (cellDelegate.hasChildren) {
                            if (cellDelegate.expanded)
                                documentView.collapse(cellDelegate.row)
                            else
                                documentView.expand(cellDelegate.row)
                        }
                    }
                }

                // ---- Column 0: Component (tree indent + arrow + icon + name) ----
                RowLayout {
                    visible: cellDelegate.column === 0
                    anchors.fill: parent
                    anchors.leftMargin: cellDelegate.depth * 20 + 8
                    spacing: 4

                    Label {
                        text: cellDelegate.hasChildren
                              ? (cellDelegate.expanded ? "\u25BE" : "\u25B8")
                              : ""
                        color: cellDelegate.row === documentView.selectedRow ? DSTheme.highlightedText : DSTheme.tertiaryText
                        Layout.preferredWidth: 14
                        horizontalAlignment: Text.AlignHCenter

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: cellDelegate.hasChildren ? Qt.PointingHandCursor : Qt.ArrowCursor
                            onClicked: {
                                if (cellDelegate.hasChildren) {
                                    if (cellDelegate.expanded)
                                        documentView.collapse(cellDelegate.row)
                                    else
                                        documentView.expand(cellDelegate.row)
                                }
                            }
                        }
                    }

                    Label {
                        text: model.display
                        font.bold: cellDelegate.hasChildren
                        color: cellDelegate.row === documentView.selectedRow ? DSTheme.highlightedText : DSTheme.text
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                        verticalAlignment: Text.AlignVCenter
                    }
                }

                // ---- Column 1: Value editor ----
                Loader {
                    visible: cellDelegate.column === 1
                    active: cellDelegate.column === 1
                    anchors.fill: parent
                    anchors.margins: 2

                    sourceComponent: {
                        if (cellDelegate.hasChildren && !cellDelegate.cellEditable
                            && cellDelegate.cellValue === "") return emptyEditor

                        if (cellDelegate.cellEnumCases
                            && cellDelegate.cellEnumCases.length > 0)
                            return enumEditor

                        if (cellDelegate.cellValueType === "Bool")
                            return boolEditor

                        if (cellDelegate.cellIsKey)
                            return refEditor

                        return textEditor
                    }
                }

                // ---- Column 2: Path ----
                Label {
                    visible: cellDelegate.column === 2
                    anchors.fill: parent
                    text: model.display
                    font.pixelSize: DSTheme.fontCaption
                    font.family: DSTheme.fontMono
                    color: cellDelegate.row === documentView.selectedRow ? DSTheme.selectedText : DSTheme.disabledText
                    leftPadding: 8
                    elide: Text.ElideRight
                    verticalAlignment: Text.AlignVCenter
                }

                // ---- Column 3: Type (syntax-colored) ----
                Label {
                    visible: cellDelegate.column === 3
                    anchors.fill: parent
                    text: model.display
                    font.pixelSize: DSTheme.fontCaption
                    font.family: DSTheme.fontMono
                    color: {
                        if (cellDelegate.row === documentView.selectedRow) return DSTheme.selectedText
                        var t = cellDelegate.cellValueType
                        if (t === "String") return DSTheme.typeString
                        if (t === "Int32" || t === "Double") return DSTheme.typeNumber
                        if (t === "Bool") return DSTheme.typeBool
                        if (t === "Color") return DSTheme.typeColor
                        if (t === "Enum") return DSTheme.typeString
                        if (t === "Ref") return DSTheme.typeRef
                        if (t === "Structure" || t === "Object") return DSTheme.labelText
                        if (t === "Vector" || t === "Set") return DSTheme.typeNumber
                        return DSTheme.disabledText
                    }
                    leftPadding: 8
                    verticalAlignment: Text.AlignVCenter
                }
            }

            // Programmatic expand/scroll signals from model
            Connections {
                target: documentModel
                function onExpandNodes(indices) {
                    for (var i = 0; i < indices.length; i++) {
                        var vr = documentView.rowAtIndex(indices[i])
                        if (vr >= 0)
                            documentView.expand(vr)
                    }
                }
                function onScrollToIndex(modelIndex) {
                    var vr = documentView.rowAtIndex(modelIndex)
                    if (vr >= 0) {
                        documentView.selectedRow = vr
                        documentView.positionViewAtRow(vr, Qt.AlignVCenter)
                    }
                }
            }
        }
    }

    // Validation feedback — forward to parent
    Connections {
        target: documentModel
        function onValidationFailed(row, expectedType) {
            root.validationFailed(row, expectedType)
        }
    }

    // ================================================================
    // EDITOR COMPONENTS
    // Parent chain: component → Loader → cellDelegate
    // ================================================================

    Component {
        id: emptyEditor
        Item {}
    }

    Component {
        id: textEditor

        TextField {
            property var cell: parent ? parent.parent : null
            text: cell ? cell.cellValue : ""
            leftPadding: 8
            readOnly: cell ? !cell.cellEditable : true

            background: Rectangle {
                color: parent.readOnly ? "transparent" : DSTheme.base
                border.color: parent.readOnly ? "transparent" : DSTheme.separator
                border.width: parent.readOnly ? 0 : 1
                radius: 2
            }
            color: cell && !cell.cellEditable ? DSTheme.labelText : DSTheme.text

            onEditingFinished: {
                if (cell && cell.cellEditable) {
                    var idx = documentView.index(cell.row, 0)
                    if (!documentModel.trySetValue(idx, text)) {
                        text = cell.cellValue
                        cell.flashRed = true
                        textFlashTimer.start()
                    }
                }
            }
            Keys.onEscapePressed: {
                if (cell) text = cell.cellValue
                focus = false
            }

            Timer {
                id: textFlashTimer
                interval: 300
                onTriggered: if (parent.cell) parent.cell.flashRed = false
            }
        }
    }

    Component {
        id: boolEditor

        RowLayout {
            property var cell: parent ? parent.parent : null
            spacing: 8

            Switch {
                checked: cell && cell.cellValue !== undefined
                         ? cell.cellValue === "true" : false
                enabled: cell ? cell.cellEditable : false
                onToggled: {
                    if (cell) {
                        var idx = documentView.index(cell.row, 0)
                        documentModel.trySetValue(idx, checked ? "true" : "false")
                    }
                }
            }
            Label {
                text: cell && cell.cellValue !== undefined ? cell.cellValue : ""
                color: (cell && cell.cellValue === "true") ? DSTheme.typeString : DSTheme.labelText
            }
        }
    }

    Component {
        id: enumEditor

        ComboBox {
            property var cell: parent ? parent.parent : null
            model: cell ? cell.cellEnumCases : []
            currentIndex: cell ? cell.cellEnumIndex : 0
            enabled: cell ? cell.cellEditable : false
            onActivated: function(idx) {
                if (cell) {
                    var modelIdx = documentView.index(cell.row, 0)
                    documentModel.trySetEnum(modelIdx, idx)
                }
            }
        }
    }

    Component {
        id: refEditor

        RowLayout {
            property var cell: parent ? parent.parent : null
            spacing: -4

            Label {
                text: cell && cell.cellValue !== undefined ? cell.cellValue : ""
                font.pixelSize: DSTheme.fontCaption
                font.family: DSTheme.fontMono
                color: DSTheme.tertiaryText
                elide: Text.ElideMiddle
                Layout.fillWidth: true
            }

            // Inline action buttons
            ToolButton {
                icon.source: "../images/doc.on.doc" + DSTheme.iconSuffix + ".png"
                icon.width: 22; icon.height: 22
                implicitWidth: 26; implicitHeight: 26
                background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                visible: cell && cell.cellValue !== ""
                onClicked: {
                    if (cell && cell.cellValue)
                        documentModel.copyToClipboard(cell.cellValue)
                }
                ToolTip.visible: hovered; ToolTip.text: "Copy Key ID"; ToolTip.delay: 500
            }
            ToolButton {
                icon.source: "../images/key.viewfinder" + DSTheme.iconSuffix + ".png"
                icon.width: 22; icon.height: 22
                implicitWidth: 26; implicitHeight: 26
                background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                onClicked: {
                    if (cell) {
                        keyDialog.targetRow = cell.row
                        keyDialog.mode = "key_set"
                        keyDialog.loadKeys()
                        keyDialog.open()
                    }
                }
                ToolTip.visible: hovered; ToolTip.text: "Set Key"; ToolTip.delay: 500
            }
            ToolButton {
                icon.source: "../images/arrow.right.circle.fill" + DSTheme.iconSuffix + ".png"
                icon.width: 22; icon.height: 22
                implicitWidth: 26; implicitHeight: 26
                background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                visible: cell && cell.cellValue !== ""
                onClicked: {
                    if (cell) {
                        var idx = documentView.index(cell.row, 0)
                        documentModel.tryJumpToKey(idx)
                    }
                }
                ToolTip.visible: hovered; ToolTip.text: "Jump to Key"; ToolTip.delay: 500
            }
        }
    }

    Component {
        id: colorEditor

        RowLayout {
            property var cell: parent ? parent.parent : null
            spacing: 6

            Rectangle {
                width: 20; height: 20; radius: 3
                color: cell && cell.cellValue !== undefined ? cell.cellValue : "transparent"
                border.color: DSTheme.disabledText
                border.width: 1
            }

            TextField {
                text: cell && cell.cellValue !== undefined ? cell.cellValue : ""
                font.family: DSTheme.fontMono
                Layout.fillWidth: true
                leftPadding: 6

                onEditingFinished: {
                    if (cell) {
                        var idx = documentView.index(cell.row, 0)
                        if (!documentModel.trySetValue(idx, text)) {
                            text = cell.cellValue
                            cell.flashRed = true
                            colorFlashTimer.start()
                        }
                    }
                }
                Keys.onEscapePressed: {
                    if (cell) text = cell.cellValue
                    focus = false
                }

                Timer {
                    id: colorFlashTimer
                    interval: 300
                    onTriggered: {
                        var c = parent.parent.cell
                        if (c) c.flashRed = false
                    }
                }
            }
        }
    }

    // ================================================================
    // DOCUMENT CONTEXT MENU
    // ================================================================
    Menu {
        id: docContextMenu
        property int targetRow: -1

        function showForRow(row) {
            targetRow = row

            while (docContextMenu.count > 0)
                docContextMenu.removeItem(docContextMenu.itemAt(0))

            var actions = documentModel.getContextMenu(documentView.index(row, 0))
            for (var i = 0; i < actions.length; i++) {
                if (actions[i].id === "_sep") {
                    docContextMenu.addItem(menuSepComponent.createObject(null))
                } else {
                    var item = menuItemComponent.createObject(null, {
                        "text": actions[i].label,
                        "actionId": actions[i].id
                    })
                    docContextMenu.addItem(item)
                }
            }
            if (actions.length > 0)
                docContextMenu.popup()
        }
    }

    Component {
        id: menuSepComponent
        DSMenuSeparator {}
    }

    Component {
        id: menuItemComponent
        MenuItem {
            property string actionId: ""
            onTriggered: {
                var idx = documentView.index(docContextMenu.targetRow, 0)
                if (actionId === "key_set") {
                    keyDialog.targetRow = docContextMenu.targetRow
                    keyDialog.mode = "key_set"
                    keyDialog.loadKeys()
                    keyDialog.open()
                } else if (actionId === "set_insert_key") {
                    keyDialog.targetRow = docContextMenu.targetRow
                    keyDialog.mode = "set_insert_key"
                    keyDialog.loadSetInsertKeys()
                    keyDialog.open()
                } else {
                    documentModel.executeContextAction(idx, actionId)
                }
            }
        }
    }

    // Key selection dialog — used by refEditor "Select..." and context menu "key_set"/"set_insert_key"
    KeySelectionDialog {
        id: keyDialog
    }
}
