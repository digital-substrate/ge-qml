import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import DS 1.0
import "CodeEditorLogic.js" as Logic

/**
 * DSCodeEditor - Python code editor with syntax highlighting and line numbers.
 * SyntaxHighlighter is a registered QML type — the editor owns its own instance.
 */
Rectangle {
    id: root
    color: DSTheme.window

    property alias text: textEdit.text
    property alias selectionStart: textEdit.selectionStart
    property alias selectionEnd: textEdit.selectionEnd

    // Model — set by parent (context property pythonEditorModel)
    property var editorModel: null

    // --- Edit actions

    // --- Edit actions (delegated to CodeEditorLogic.js) ---
    function commentSelection() { Logic.commentSelection(textEdit) }
    function shiftRight() { Logic.shiftRight(textEdit) }
    function shiftLeft() { Logic.shiftLeft(textEdit) }
    function moveLineUp() { Logic.moveLineUp(textEdit) }
    function moveLineDown() { Logic.moveLineDown(textEdit) }

    // --- Jump to Line
    function jumpToLine() {
        jumpToLineDialog.open()
        jumpToLineField.text = ""
        jumpToLineField.forceActiveFocus()
    }

    Dialog {
        id: jumpToLineDialog
        title: "Jump to Line"
        anchors.centerIn: parent
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
        onAccepted: root.gotoLine(parseInt(jumpToLineField.text) || 1)

        Row {
            spacing: 8
            Label { text: "Line:"; anchors.verticalCenter: parent.verticalCenter }
            TextField {
                id: jumpToLineField
                width: 100
                validator: IntValidator { bottom: 1 }
                onAccepted: jumpToLineDialog.accept()
            }
        }
    }

    // --- Jump to Definition
    function jumpToDefinition() {
        var expr = Logic.expressionUnderCursor(textEdit)
        if (!expr) return
        var re = new RegExp("(?:def|class)\\s+" + expr + "\\b")
        var match = re.exec(textEdit.text)
        if (match) {
            textEdit.cursorPosition = match.index
            textEdit.forceActiveFocus()
        }
    }

    // --- Document Items
    function showDocumentItems() {
        var items = Logic.parseDocumentItems(textEdit.text)
        documentItemsModel.clear()
        for (var i = 0; i < items.length; i++)
            documentItemsModel.append(items[i])
        documentItemsPopup.open()
    }

    ListModel { id: documentItemsModel }

    Popup {
        id: documentItemsPopup
        x: root.width - width - 20
        y: toolbar.height + 10
        width: 250
        height: Math.min(300, documentItemsList.contentHeight + 16)
        modal: false
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        background: Rectangle {
            color: DSTheme.window
            border.color: DSTheme.border
            border.width: 1
            radius: 8
        }

        ListView {
            id: documentItemsList
            anchors.fill: parent
            anchors.margins: 4
            model: documentItemsModel
            clip: true

            delegate: Rectangle {
                width: documentItemsList.width
                height: 24
                color: mouseDocItem.containsMouse ? DSTheme.hoverBackground : "transparent"
                radius: 4

                Row {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    spacing: 6

                    Text {
                        text: model.isClass ? "C" : "f"
                        font.bold: true
                        color: model.isClass ? DSTheme.typeRef : DSTheme.typeString
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    Text {
                        text: model.name
                        color: DSTheme.text
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }

                MouseArea {
                    id: mouseDocItem
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        var before = textEdit.text.substring(0, model.position)
                        var lineNumber = before.split('\n').length
                        // position is at start of line, so we're ON line N, not after it
                        root.gotoLine(lineNumber)
                    }
                    onDoubleClicked: documentItemsPopup.close()
                }
            }
        }
    }

    // --- Refresh Syntax Coloring ---
    function refreshSyntax() {
        highlighter.setDocument(null)
        highlighterTimer.start()
    }

    // --- Font size
    function biggerFont() {
        if (textEdit.font.pixelSize < 28) {
            textEdit.font.pixelSize += 1
            if (root.editorModel) root.editorModel.setFontSize(textEdit.font.pixelSize)
        }
    }
    function smallerFont() {
        if (textEdit.font.pixelSize > 8) {
            textEdit.font.pixelSize -= 1
            if (root.editorModel) root.editorModel.setFontSize(textEdit.font.pixelSize)
        }
    }

    function expressionUnderCursor() { return Logic.expressionUnderCursor(textEdit) }
    function gotoLine(lineNumber) { Logic.gotoLine(textEdit, flickable, lineNumber) }

    // Load source from model when it changes (open script, etc.)
    Connections {
        target: root.editorModel
        function onSourceChanged() {
            textEdit.text = root.editorModel.source
        }
        function onErrorLineChanged() {
            root.gotoLine(root.editorModel.errorLine)
        }
    }
    // Load initial source — model loads before QML, so signal was already emitted
    Component.onCompleted: {
        if (root.editorModel) {
            textEdit.text = root.editorModel.source
            textEdit.font.pixelSize = root.editorModel.fontSize
        }
    }

    // Toolbar
    Rectangle {
        id: toolbar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 60
        color: DSTheme.alternateBase

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 12
            anchors.rightMargin: 12
            spacing: 8

            // Title
            Column {
                spacing: 0

                Text {
                    text: "Python Editor"
                    color: DSTheme.text
                    font.pixelSize: DSTheme.fontHeading
                    font.bold: true
                }

                Text {
                    text: root.editorModel ? root.editorModel.fileName : ""
                    color: scriptMouseArea.containsMouse ? DSTheme.text : DSTheme.labelText
                    visible: text !== ""

                    MouseArea {
                        id: scriptMouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            while (scriptsMenu.count > 0)
                                scriptsMenu.removeItem(scriptsMenu.itemAt(0))
                            var scripts = root.editorModel.scriptList()
                            for (var i = 0; i < scripts.length; i++) {
                                var item = scriptMenuComponent.createObject(null, {
                                    "text": scripts[i],
                                    "scriptName": scripts[i]
                                })
                                scriptsMenu.addItem(item)
                            }
                            scriptsMenu.popup()
                        }
                    }
                }

                Menu {
                    id: scriptsMenu
                }

                Component {
                    id: scriptMenuComponent
                    MenuItem {
                        property string scriptName: ""
                        onTriggered: {
                            var folder = root.editorModel.scriptsFolder()
                            root.editorModel.saveSource(textEdit.text)
                            root.editorModel.openScript(folder + "/" + scriptName)
                        }
                    }
                }
            }

            Item { Layout.fillWidth: true }

            // Evaluation group — applescript + bolt
            ColumnLayout {
                spacing: 2
                Rectangle {
                    Layout.alignment: Qt.AlignHCenter
                    implicitWidth: evalRow.implicitWidth + 12
                    implicitHeight: evalRow.implicitHeight + 8
                    radius: height / 2
                    color: DSTheme.midlight
                    border.color: DSTheme.inputBorder
                    border.width: 0.5

                    Row {
                        id: evalRow
                        anchors.centerIn: parent
                        spacing: 2

                        ToolButton {
                            display: AbstractButton.IconOnly
                            icon.source: "../images/applescript" + DSTheme.iconSuffix + ".png"
                            icon.width: 22; icon.height: 22
                            background: Item {}
                            ToolTip.visible: hovered; ToolTip.text: "Run Script"; ToolTip.delay: 500
                            onClicked: if (root.editorModel) root.editorModel.evalBuffer(textEdit.text)
                        }
                        ToolButton {
                            display: AbstractButton.IconOnly
                            icon.source: "../images/bolt" + DSTheme.iconSuffix + ".png"
                            icon.width: 22; icon.height: 22
                            background: Item {}
                            ToolTip.visible: hovered; ToolTip.text: "Eval Selection"; ToolTip.delay: 500
                            onClicked: if (root.editorModel) root.editorModel.evalSelection(textEdit.text, textEdit.selectionStart, textEdit.selectionEnd)
                        }
                    }
                }
                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: "Evaluation"
                    color: DSTheme.labelText
                    font.pixelSize: DSTheme.fontCaption
                }
            }

            // Information group — questionmark.circle + p.circle + eye.circle + eyeglasses
            ColumnLayout {
                spacing: 2
                Rectangle {
                    Layout.alignment: Qt.AlignHCenter
                    implicitWidth: infoRow.implicitWidth + 12
                    implicitHeight: infoRow.implicitHeight + 8
                    radius: height / 2
                    color: DSTheme.midlight
                    border.color: DSTheme.inputBorder
                    border.width: 0.5

                    Row {
                        id: infoRow
                        anchors.centerIn: parent
                        spacing: 2

                        ToolButton {
                            display: AbstractButton.IconOnly
                            icon.source: "../images/questionmark.circle" + DSTheme.iconSuffix + ".png"
                            icon.width: 22; icon.height: 22
                            background: Item {}
                            ToolTip.visible: hovered; ToolTip.text: "Help"; ToolTip.delay: 500
                            onClicked: if (root.editorModel) root.editorModel.showHelp(expressionUnderCursor())
                        }
                        ToolButton {
                            display: AbstractButton.IconOnly
                            icon.source: "../images/p.circle" + DSTheme.iconSuffix + ".png"
                            icon.width: 22; icon.height: 22
                            background: Item {}
                            ToolTip.visible: hovered; ToolTip.text: "Print"; ToolTip.delay: 500
                            onClicked: if (root.editorModel) root.editorModel.showRepr(expressionUnderCursor())
                        }
                        ToolButton {
                            display: AbstractButton.IconOnly
                            icon.source: "../images/eye.circle" + DSTheme.iconSuffix + ".png"
                            icon.width: 22; icon.height: 22
                            background: Item {}
                            ToolTip.visible: hovered; ToolTip.text: "Type"; ToolTip.delay: 500
                            onClicked: if (root.editorModel) root.editorModel.showType(expressionUnderCursor())
                        }
                        ToolButton {
                            display: AbstractButton.IconOnly
                            icon.source: "../images/eyeglasses" + DSTheme.iconSuffix + ".png"
                            icon.width: 22; icon.height: 22
                            background: Item {}
                            ToolTip.visible: hovered; ToolTip.text: "Description"; ToolTip.delay: 500
                            onClicked: if (root.editorModel) root.editorModel.showDescription(expressionUnderCursor())
                        }
                    }
                }
                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: "Information"
                    color: DSTheme.labelText
                    font.pixelSize: DSTheme.fontCaption
                }
            }

            // Error group — arrow.left + arrow.right
            ColumnLayout {
                spacing: 2
                Rectangle {
                    Layout.alignment: Qt.AlignHCenter
                    implicitWidth: errorRow.implicitWidth + 12
                    implicitHeight: errorRow.implicitHeight + 8
                    radius: height / 2
                    color: DSTheme.midlight
                    border.color: DSTheme.inputBorder
                    border.width: 0.5

                    Row {
                        id: errorRow
                        anchors.centerIn: parent
                        spacing: 2

                        ToolButton {
                            display: AbstractButton.IconOnly
                            icon.source: "../images/arrow.left" + DSTheme.iconSuffix + ".png"
                            icon.width: 22; icon.height: 22
                            background: Item {}
                            ToolTip.visible: hovered; ToolTip.text: "Previous Error"; ToolTip.delay: 500
                            onClicked: if (root.editorModel) root.editorModel.previousError()
                        }
                        ToolButton {
                            display: AbstractButton.IconOnly
                            icon.source: "../images/arrow.right" + DSTheme.iconSuffix + ".png"
                            icon.width: 22; icon.height: 22
                            background: Item {}
                            ToolTip.visible: hovered; ToolTip.text: "Next Error"; ToolTip.delay: 500
                            onClicked: if (root.editorModel) root.editorModel.nextError()
                        }
                    }
                }
                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: "Error"
                    color: DSTheme.labelText
                    font.pixelSize: DSTheme.fontCaption
                }
            }
        }

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: DSTheme.light
        }
    }

    // --- Find bar ---
    property int _findIndex: -1
    property var _findMatches: []

    function showFind() {
        findBar.visible = true
        replaceRow.visible = false
        findField.forceActiveFocus()
        findField.selectAll()
    }

    function useSelectionForFind() {
        var expr = expressionUnderCursor()
        if (!expr) return
        findField.text = expr
        showFind()
    }

    function showReplace() {
        findBar.visible = true
        replaceRow.visible = true
        findField.forceActiveFocus()
        findField.selectAll()
    }

    function hideFind() {
        findBar.visible = false
        _findMatches = []
        _findIndex = -1
        textEdit.forceActiveFocus()
    }

    function _doFind() {
        _findMatches = Logic.findAll(textEdit.text, findField.text)
        _findIndex = _findMatches.length > 0 ? 0 : -1
        if (_findIndex >= 0)
            Logic.selectMatch(textEdit, flickable, _findMatches, _findIndex, findField.text.length)
    }

    function findNext() {
        if (_findMatches.length === 0) return
        _findIndex = (_findIndex + 1) % _findMatches.length
        Logic.selectMatch(textEdit, flickable, _findMatches, _findIndex, findField.text.length)
    }

    function findPrevious() {
        if (_findMatches.length === 0) return
        _findIndex = (_findMatches.length + _findIndex - 1) % _findMatches.length
        Logic.selectMatch(textEdit, flickable, _findMatches, _findIndex, findField.text.length)
    }

    function replaceCurrent() {
        Logic.replaceCurrent(textEdit, _findMatches, _findIndex, findField.text, replaceField.text)
        _doFind()
    }

    function replaceAll() {
        Logic.replaceAll(textEdit, _findMatches, findField.text, replaceField.text)
        _doFind()
    }

    Rectangle {
        id: findBar
        visible: false
        anchors.top: toolbar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: replaceRow.visible ? 64 : 34
        color: DSTheme.midlight

        ColumnLayout {
            anchors.fill: parent
            anchors.leftMargin: 8
            anchors.rightMargin: 8
            anchors.topMargin: 4
            anchors.bottomMargin: 4
            spacing: 2

            // Find row
            RowLayout {
                spacing: 4

                TextField {
                    id: findField
                    Layout.fillWidth: true
                    placeholderText: "Find..."
                    onTextChanged: _doFind()
                    onAccepted: findNext()
                    Keys.onEscapePressed: hideFind()
                }

                Label {
                    text: _findMatches.length > 0
                        ? (_findIndex + 1) + "/" + _findMatches.length
                        : "0/0"
                    color: DSTheme.labelText
                    font.pixelSize: DSTheme.fontCaption
                    Layout.preferredWidth: 40
                    horizontalAlignment: Text.AlignHCenter
                }

                ToolButton { text: "\u25B2"; implicitWidth: 24; implicitHeight: 24; onClicked: findPrevious() }
                ToolButton { text: "\u25BC"; implicitWidth: 24; implicitHeight: 24; onClicked: findNext() }
                ToolButton { text: "\u2715"; implicitWidth: 24; implicitHeight: 24; onClicked: hideFind() }
            }

            // Replace row
            RowLayout {
                id: replaceRow
                spacing: 4

                TextField {
                    id: replaceField
                    Layout.fillWidth: true
                    placeholderText: "Replace..."
                    Keys.onEscapePressed: hideFind()
                }

                Button {
                    text: "Replace"
                    implicitHeight: 24
                    enabled: _findMatches.length > 0
                    onClicked: replaceCurrent()
                }
                Button {
                    text: "All"
                    implicitHeight: 24
                    enabled: _findMatches.length > 0
                    onClicked: replaceAll()
                }
            }
        }
    }

    // Editor + output split
    SplitView {
        anchors.top: findBar.visible ? findBar.bottom : toolbar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        orientation: Qt.Vertical

        // Code area
        Rectangle {
            SplitView.fillHeight: true
            SplitView.minimumHeight: 100
            color: DSTheme.codeBackground

            RowLayout {
                anchors.fill: parent
                spacing: 0

                // Line numbers — TextEdit with same font for pixel-perfect alignment
                Rectangle {
                    Layout.preferredWidth: 45
                    Layout.fillHeight: true
                    color: DSTheme.codeLine

                    Flickable {
                        anchors.fill: parent
                        clip: true
                        contentY: flickable.contentY
                        interactive: false

                        // Current line highlight
                        Rectangle {
                            y: textEdit.cursorRectangle.y
                            width: parent.width
                            height: textEdit.cursorRectangle.height
                            color: DSTheme.hoverBackground
                            opacity: 0.5
                        }

                        TextEdit {
                            id: lineNumbersEdit
                            width: parent.width
                            padding: textEdit.padding
                            topPadding: textEdit.topPadding
                            rightPadding: 12
                            readOnly: true
                            color: DSTheme.codeComment
                            font: textEdit.font
                            horizontalAlignment: Text.AlignRight
                            text: {
                                var lines = []
                                for (var i = 1; i <= textEdit.lineCount; i++)
                                    lines.push(i)
                                return lines.join('\n')
                            }
                        }
                    }

                    Rectangle {
                        anchors.right: parent.right
                        width: 1
                        height: parent.height
                        color: DSTheme.dark
                    }
                }

                // Code area
                Flickable {
                    id: flickable
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    contentWidth: textEdit.width
                    contentHeight: textEdit.height
                    clip: true

                    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                    ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded }

                    // Current line highlight
                    Rectangle {
                        id: currentLineHighlight
                        y: textEdit.cursorRectangle.y
                        width: flickable.contentWidth
                        height: textEdit.cursorRectangle.height
                        color: DSTheme.hoverBackground
                        opacity: 0.3
                    }

                    TextEdit {
                        id: textEdit
                        width: Math.max(flickable.width, contentWidth + 20)
                        padding: 8
                        leftPadding: 12
                        color: DSTheme.highlightedText
                        selectionColor: DSTheme.codeSelection
                        selectedTextColor: DSTheme.highlightedText
                        font.pixelSize: DSTheme.fontHeading
                        font.family: DSTheme.fontMono
                        wrapMode: TextEdit.NoWrap
                        selectByMouse: true

                        // Context menu
                        MouseArea {
                            anchors.fill: parent
                            acceptedButtons: Qt.RightButton
                            onClicked: function(mouse) {
                                editorContextMenu.popup()
                            }
                        }

                        Menu {
                            id: editorContextMenu

                            MenuItem {
                                text: "Cut"
                                enabled: textEdit.selectedText.length > 0
                                onTriggered: textEdit.cut()
                            }
                            MenuItem {
                                text: "Copy"
                                enabled: textEdit.selectedText.length > 0
                                onTriggered: textEdit.copy()
                            }
                            MenuItem {
                                text: "Paste"
                                onTriggered: textEdit.paste()
                            }
                            MenuItem {
                                text: "Select All"
                                onTriggered: textEdit.selectAll()
                            }
                            DSMenuSeparator {}
                            MenuItem {
                                text: "Run Script"
                                onTriggered: if (root.editorModel) root.editorModel.evalBuffer(textEdit.text)
                            }
                            MenuItem {
                                text: "Eval"
                                onTriggered: if (root.editorModel) root.editorModel.evalSelection(textEdit.text, textEdit.selectionStart, textEdit.selectionEnd)
                            }
                            DSMenuSeparator {}
                            MenuItem {
                                text: "Help"
                                enabled: expressionUnderCursor().length > 0
                                onTriggered: if (root.editorModel) root.editorModel.showHelp(expressionUnderCursor())
                            }
                            MenuItem {
                                text: "Type"
                                enabled: expressionUnderCursor().length > 0
                                onTriggered: if (root.editorModel) root.editorModel.showType(expressionUnderCursor())
                            }
                            MenuItem {
                                text: "Print"
                                enabled: expressionUnderCursor().length > 0
                                onTriggered: if (root.editorModel) root.editorModel.showRepr(expressionUnderCursor())
                            }
                            MenuItem {
                                text: "Description"
                                enabled: expressionUnderCursor().length > 0
                                onTriggered: if (root.editorModel) root.editorModel.showDescription(expressionUnderCursor())
                            }
                            DSMenuSeparator {}
                            MenuItem {
                                text: "Jump to Module"
                                enabled: textEdit.selectedText.length > 0
                                onTriggered: if (root.editorModel) root.editorModel.jumpToModule(textEdit.selectedText)
                            }
                            MenuItem {
                                text: "Document Items"
                                onTriggered: root.showDocumentItems()
                            }
                        }

                        // Auto-scroll to follow cursor
                        onCursorRectangleChanged: {
                            var r = cursorRectangle
                            if (r.y < flickable.contentY)
                                flickable.contentY = r.y
                            else if (r.y + r.height > flickable.contentY + flickable.height)
                                flickable.contentY = r.y + r.height - flickable.height
                        }

                        // Tab → completion or 4 spaces
                        Keys.onTabPressed: {
                            if (!root.editorModel) {
                                textEdit.insert(textEdit.cursorPosition, "    ")
                                return
                            }
                            // Check if there's a partial word before cursor
                            var pos = textEdit.cursorPosition
                            var text = textEdit.text
                            var lineStart = text.lastIndexOf('\n', pos - 1) + 1
                            var before = text.substring(lineStart, pos).replace(/^\s+/, '')
                            if (before.length === 0) {
                                textEdit.insert(pos, "    ")
                                return
                            }
                            var result = root.editorModel.complete(text, pos)
                            if (!result.completions || result.completions.length === 0) {
                                // No completion found
                                textEdit.insert(pos, "    ")
                            } else if (result.completion && result.completion !== result.context) {
                                // Insert the completion
                                var toInsert = result.completion.substring(result.context.length)
                                textEdit.insert(pos, toInsert)
                                if (result.completions.length > 1) {
                                    root.editorModel.setCompletionOutput(result.completions, Math.floor(outputTextEdit.width / outputTextEdit.font.pixelSize * 1.7))
                                }
                            } else if (result.completions.length > 1) {
                                // Already at longest common prefix — show candidates
                                root.editorModel.setCompletionOutput(result.completions, Math.floor(outputTextEdit.width / outputTextEdit.font.pixelSize * 1.7))
                            }
                        }

                        property int lineCount: text.split('\n').length

                        SyntaxHighlighter {
                            id: highlighter
                        }

                        Timer {
                            id: highlighterTimer
                            interval: 100
                            onTriggered: highlighter.setDocument(textEdit.textDocument)
                        }

                        Component.onCompleted: highlighterTimer.start()
                    }
                }
            }
        }

        // Output panel
        Rectangle {
            SplitView.preferredHeight: 150
            SplitView.minimumHeight: 100
            color: DSTheme.codeBackground

            Flickable {
                id: outputFlickable
                anchors.fill: parent
                anchors.margins: 4
                contentHeight: outputTextEdit.height
                clip: true

                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                TextEdit {
                    id: outputTextEdit
                    width: outputFlickable.width
                    readOnly: true
                    selectByMouse: true

                    MouseArea {
                        anchors.fill: parent
                        acceptedButtons: Qt.RightButton
                        onClicked: outputContextMenu.popup()
                    }

                    Menu {
                        id: outputContextMenu
                        MenuItem {
                            text: "Copy"
                            enabled: outputTextEdit.selectedText.length > 0
                            onTriggered: outputTextEdit.copy()
                        }
                        MenuItem {
                            text: "Select All"
                            onTriggered: outputTextEdit.selectAll()
                        }
                    }
                    text: root.editorModel ? root.editorModel.output : ""
                    color: DSTheme.secondaryText
                    font.family: DSTheme.fontMono
                    font.pixelSize: textEdit.font.pixelSize
                    padding: 4
                    wrapMode: TextEdit.Wrap

                    SyntaxHighlighter {
                        id: outputHighlighter
                    }

                    onTextChanged: {
                        if (text.length > 0)
                            outputHighlighterTimer.restart()
                    }

                    Connections {
                        target: root.editorModel
                        function onOutputChanged() {
                            outputTextEdit.cursorPosition = 0
                            outputFlickable.contentY = 0
                        }
                        function onOutputModeChanged() {
                            outputHighlighter.setMode(root.editorModel.outputMode)
                        }
                    }

                    Timer {
                        id: outputHighlighterTimer
                        interval: 50
                        onTriggered: outputHighlighter.setDocument(outputTextEdit.textDocument)
                    }
                }
            }
        }
    }
}
