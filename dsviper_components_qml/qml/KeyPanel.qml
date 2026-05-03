import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Key panel — View+Delegate for key_model.py
// keyModel accessed via context property.

Rectangle {
    id: root
    color: DSTheme.window

    // Signals up — parent assembly handles dialog opening
    signal addAttachmentsRequested(int row)

    // Called by parent when abstraction changes (reset visual selection)
    function resetSelection() {
        keyTable.selectedRow = -1
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Keys header
        HorizontalHeaderView {
            id: keyHeader
            Layout.fillWidth: true
            syncView: keyTable
            clip: true

            delegate: Rectangle {
                implicitWidth: 100
                implicitHeight: 22
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
            }
        }

        // Keys table
        TableView {
            id: keyTable
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: keyModel
            resizableColumns: true

            readonly property var initialColumnWidths: [300, 400]
            property int selectedRow: -1

            columnWidthProvider: function(column) {
                var w = explicitColumnWidth(column)
                if (w >= 0)
                    return w
                return initialColumnWidths[column] ?? 100
            }

            delegate: Rectangle {
                implicitWidth: 100
                implicitHeight: 26

                color: row === keyTable.selectedRow
                       ? DSTheme.highlight
                       : mouseKey.containsMouse
                         ? DSTheme.hoverBackground
                         : row % 2 === 0 ? "transparent" : DSTheme.alternateBase

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    anchors.rightMargin: 4
                    spacing: 4

                    Label {
                        text: model.display
                        font.family: column === 0 ? DSTheme.fontMono : font.family
                        color: row === keyTable.selectedRow
                               ? DSTheme.highlightedText
                               : column === 0 ? DSTheme.tertiaryText : DSTheme.text
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }

                    // Action buttons — visible on selected row, column 0 only
                    Row {
                        visible: column === 0 && (row === keyTable.selectedRow || mouseKey.containsMouse)
                        spacing: -4

                        ToolButton {
                            icon.source: "../images/doc.on.doc" + DSTheme.iconSuffix + ".png"
                            icon.width: 22; icon.height: 22
                            implicitWidth: 26; implicitHeight: 26
                            background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                            onClicked: keyModel.executeContextAction(row, "copy_key_id")
                            ToolTip.visible: hovered; ToolTip.text: "Copy Key Instance ID"; ToolTip.delay: 500
                        }
                        ToolButton {
                            icon.source: "../images/plus.circle.dashed" + DSTheme.iconSuffix + ".png"
                            icon.width: 22; icon.height: 22
                            implicitWidth: 26; implicitHeight: 26
                            background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                            onClicked: root.addAttachmentsRequested(row)
                            ToolTip.visible: hovered; ToolTip.text: "Add Attachments"; ToolTip.delay: 500
                        }
                        ToolButton {
                            icon.source: "../images/arrow.right.circle.fill" + DSTheme.iconSuffix + ".png"
                            icon.width: 22; icon.height: 22
                            implicitWidth: 26; implicitHeight: 26
                            background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                            onClicked: keyModel.executeContextAction(row, "find_key_id")
                            ToolTip.visible: hovered; ToolTip.text: "Find Key Instance ID"; ToolTip.delay: 500
                        }
                    }
                }

                MouseArea {
                    id: mouseKey
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.LeftButton
                    z: -1
                    onClicked: {
                        keyTable.selectedRow = row
                        keyModel.select(row)
                    }
                }
            }
        }
    }

    // Navigation signal — jump-to-key updates table selection
    Connections {
        target: keyModel
        function onKeyIndexChanged(row) {
            keyTable.selectedRow = row
        }
    }
}
