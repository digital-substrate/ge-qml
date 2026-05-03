import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * Blobs Dialog
 * Shared between cdbe, graph_editor.
 * Requires context property: blobModel
 */
Window {
    id: root
    title: "Blobs"
    width: 800
    height: 500
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

        // Statistics
        DSGroupBox {
            title: "Statistics"
            Layout.fillWidth: true

            RowLayout {
                anchors.fill: parent
                spacing: 12

                Label { text: "Count:"; color: DSTheme.labelText }
                Label { text: blobModel.statCount; font.family: DSTheme.fontMono; color: DSTheme.text }
                Item { Layout.fillWidth: true }
                Label { text: "Total:"; color: DSTheme.labelText }
                Label { text: blobModel.statTotal; font.family: DSTheme.fontMono; color: DSTheme.text }
                Label { text: "Min:"; color: DSTheme.labelText }
                Label { text: blobModel.statMin; font.family: DSTheme.fontMono; color: DSTheme.text }
                Label { text: "Max:"; color: DSTheme.labelText }
                Label { text: blobModel.statMax; font.family: DSTheme.fontMono; color: DSTheme.text }
            }
        }

        // --- Blobs TableView with sortable header ---
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            readonly property var initialColumnWidths: [380, 80, 100, 80, 60]

            // Track sort state
            property int sortColumn: -1
            property bool sortAscending: true

            HorizontalHeaderView {
                id: blobHeader
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                syncView: blobTable
                clip: true

                delegate: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 22
                    color: DSTheme.midlight
                    border.color: DSTheme.separator
                    border.width: 0.5

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 4
                        anchors.rightMargin: 4
                        spacing: 2

                        Label {
                            text: model.display
                            font.pixelSize: DSTheme.fontCaption
                            font.bold: true
                            color: DSTheme.secondaryText
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }

                        // Sort indicator
                        Label {
                            visible: blobTable.parent.sortColumn === index
                            text: blobTable.parent.sortAscending ? "▲" : "▼"
                            font.pixelSize: DSTheme.fontCaption
                            color: DSTheme.labelText
                        }
                    }

                    TapHandler {
                        onTapped: {
                            var container = blobTable.parent
                            if (container.sortColumn === index) {
                                container.sortAscending = !container.sortAscending
                            } else {
                                container.sortColumn = index
                                container.sortAscending = true
                            }
                            blobModel.sort(container.sortColumn,
                                container.sortAscending ? Qt.AscendingOrder : Qt.DescendingOrder)
                        }
                    }
                }
            }

            TableView {
                id: blobTable
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: blobHeader.bottom
                anchors.bottom: parent.bottom
                clip: true
                model: blobModel
                resizableColumns: true

                columnWidthProvider: function(column) {
                    var w = explicitColumnWidth(column)
                    if (w >= 0)
                        return w
                    return parent.initialColumnWidths[column] ?? 100
                }

                delegate: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 22

                    color: row % 2 === 0 ? DSTheme.window : DSTheme.alternateBase

                    Label {
                        anchors.fill: parent
                        anchors.leftMargin: 4
                        text: model.display
                        font.family: column === 0 ? DSTheme.fontMono : font.family
                        color: column === 0 ? DSTheme.tertiaryText : DSTheme.text
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }
                }
            }
        }

        // Refresh button
        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }
            Button {
                text: "Refresh"
                onClicked: blobModel.refresh()
            }
        }
    }
}
