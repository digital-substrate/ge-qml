import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../dsviper_components_qml/qml" as DS

// Select Graph dialog
// selectGraphModel accessed via context property.

Dialog {
    id: selectGraphDialog
    title: "Select a Graph"
    width: 300; height: 250
    anchors.centerIn: parent
    modal: true

    onRejected: selectGraphModel.cancel()

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        RowLayout {
            Layout.fillWidth: true
            Label { text: "Graphs"; font.bold: true; color: DS.DSTheme.secondaryText }
            Label { text: selectGraphModel.count; color: DS.DSTheme.text }
            Item { Layout.fillWidth: true }
        }

        ListView {
            id: selectGraphListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: selectGraphModel
            currentIndex: selectGraphModel.currentIndex

            delegate: Rectangle {
                width: selectGraphListView.width
                height: 28
                color: ListView.isCurrentItem ? DS.DSTheme.highlight : (index % 2 === 0 ? "transparent" : DS.DSTheme.alternateBase)

                Label {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    verticalAlignment: Text.AlignVCenter
                    text: model.name
                    color: DS.DSTheme.text
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        selectGraphListView.currentIndex = index
                        selectGraphModel.select(index)
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }
            Button {
                text: "Cancel"
                onClicked: { selectGraphModel.cancel(); selectGraphDialog.close() }
            }
            Button {
                text: "Select"
                onClicked: { selectGraphModel.accept(); selectGraphDialog.close() }
            }
        }
    }
}
