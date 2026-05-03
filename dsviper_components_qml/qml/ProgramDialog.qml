import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * Program Panel
 * Shared between cdbe, graph_editor.
 * Requires context property: programModel
 *
 * Uses TableView + HorizontalHeaderView for resizable columns.
 * Selection via ItemSelectionModel + required property bool selected.
 */
Window {
    id: root
    title: "Commit Program"
    width: 900; height: 600
    color: DSTheme.window
    palette {
        window: DSTheme.window
        windowText: DSTheme.windowText
        base: DSTheme.base
        alternateBase: DSTheme.alternateBase
        text: DSTheme.text
        button: DSTheme.button
        buttonText: DSTheme.buttonText
        highlight: DSTheme.highlight
        highlightedText: DSTheme.highlightedText
        mid: DSTheme.mid
        midlight: DSTheme.midlight
        light: DSTheme.light
        dark: DSTheme.dark
        placeholderText: DSTheme.placeholderText
        toolTipBase: DSTheme.toolTipBase
        toolTipText: DSTheme.toolTipText
    }
    flags: Qt.Window

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 4

        // Header — commit info
        GridLayout {
            columns: 6
            columnSpacing: 8
            rowSpacing: 2
            Layout.fillWidth: true

            Label { text: "Label:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
            Label { text: programModel.commitLabel; color: DSTheme.text; Layout.columnSpan: 5 }

            Label { text: "Date:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
            Label { text: programModel.commitDate; color: DSTheme.text; Layout.columnSpan: 5 }

            Label { text: "Type:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
            Label { text: programModel.commitType; color: DSTheme.text; Layout.columnSpan: 5 }

            Label { text: "Commit:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
            Label { text: programModel.commitId; font.family: DSTheme.fontMono; font.pixelSize: DSTheme.fontCaption; color: DSTheme.tertiaryText; Layout.fillWidth: true }
            ToolButton { icon.source: "../images/doc.on.doc" + DSTheme.iconSuffix + ".png"; icon.width: 22; icon.height: 22; implicitWidth: 26; implicitHeight: 26; background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                ToolTip.visible: hovered; ToolTip.text: "Copy to Clipboard"; ToolTip.delay: 500; onClicked: programModel.copyToClipboard(programModel.commitId) }

            Label { text: "Parent:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
            Label { text: programModel.parentId; font.family: DSTheme.fontMono; font.pixelSize: DSTheme.fontCaption; color: DSTheme.tertiaryText; Layout.fillWidth: true }
            ToolButton { icon.source: "../images/doc.on.doc" + DSTheme.iconSuffix + ".png"; icon.width: 22; icon.height: 22; implicitWidth: 26; implicitHeight: 26; background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                ToolTip.visible: hovered; ToolTip.text: "Copy to Clipboard"; ToolTip.delay: 500; onClicked: programModel.copyToClipboard(programModel.parentId) }

            Label { text: "Target:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
            Label { text: programModel.targetId; font.family: DSTheme.fontMono; font.pixelSize: DSTheme.fontCaption; color: DSTheme.tertiaryText; Layout.fillWidth: true }
            ToolButton { icon.source: "../images/doc.on.doc" + DSTheme.iconSuffix + ".png"; icon.width: 22; icon.height: 22; implicitWidth: 26; implicitHeight: 26; background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                ToolTip.visible: hovered; ToolTip.text: "Copy to Clipboard"; ToolTip.delay: 500; onClicked: programModel.copyToClipboard(programModel.targetId) }
        }

        // Toggle buttons
        RowLayout {
            spacing: 8
            CheckBox {
                id: useTraceCheck
                text: "Use Commit State Trace"
                checked: programModel.useTrace
                onToggled: programModel.useTrace = checked
            }
            CheckBox {
                id: useDescCheck
                text: "Use Description"
                onToggled: {
                    programModel.setUseDescription(checked)
                    if (opcodeTable.currentRow >= 0)
                        programModel.showValue(opcodeTable.currentRow)
                }
            }
        }

        // --- Opcodes TableView with header ---
        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 200

            readonly property var initialColumnWidths: [100, 100, 180, 80, 200, 120, 120]

            HorizontalHeaderView {
                id: opcodeHeader
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                syncView: opcodeTable
                clip: true

                delegate: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 22
                    color: DSTheme.midlight
                    border.color: DSTheme.separator
                    border.width: 0.5

                    Label {
                        anchors.fill: parent
                        anchors.leftMargin: 4
                        text: model.display
                        font.pixelSize: DSTheme.fontCaption
                        font.bold: true
                        color: DSTheme.secondaryText
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }
                }
            }

            TableView {
                id: opcodeTable
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: opcodeHeader.bottom
                anchors.bottom: parent.bottom
                clip: true
                model: programModel
                resizableColumns: true
                selectionBehavior: TableView.SelectRows
                selectionMode: TableView.SingleSelection

                selectionModel: ItemSelectionModel {
                    id: opcodeSelectionModel
                    model: programModel
                    onCurrentChanged: (current, previous) => {
                        programModel.showValue(current.row)
                    }
                }

                // Initial widths + respect user resize via explicitColumnWidth
                columnWidthProvider: function(column) {
                    var w = explicitColumnWidth(column)
                    if (w >= 0)
                        return w
                    return parent.initialColumnWidths[column] ?? 100
                }

                delegate: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 22

                    readonly property bool isSelectedRow: row === opcodeTable.currentRow

                    color: isSelectedRow ? DSTheme.highlight
                         : (row % 2 === 0 ? DSTheme.window : DSTheme.alternateBase)

                    Label {
                        anchors.fill: parent
                        anchors.leftMargin: 4
                        text: model.display
                        font.pixelSize: DSTheme.fontCaption
                        font.family: (column === 2 || column === 5 || column === 6) ? DSTheme.fontMono : font.family
                        color: isSelectedRow ? DSTheme.highlightedText
                             : (column === 2 || column === 5 || column === 6) ? DSTheme.tertiaryText
                             : column === 3 ? DSTheme.text
                             : DSTheme.secondaryText
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }

                    TapHandler {
                        onTapped: opcodeTable.selectionModel.setCurrentIndex(
                            opcodeTable.model.index(row, 0),
                            ItemSelectionModel.ClearAndSelect | ItemSelectionModel.Rows)
                    }
                }
            }
        }

        // Value HTML display
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: DSTheme.codeBackground
            border.color: DSTheme.separator; border.width: 1

            ScrollView {
                anchors.fill: parent
                anchors.margins: 2

                TextArea {
                    readOnly: true
                    textFormat: TextEdit.RichText
                    text: programModel.valueHtml
                    color: DSTheme.secondaryText
                    background: Item {}
                    wrapMode: TextEdit.Wrap
                }
            }
        }
    }
}
