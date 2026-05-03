import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Key selection dialog — used by "Set Key" and "Insert Key" context actions.

Dialog {
    id: keyDialog
    title: "Select Key"
    width: 500
    height: 350
    anchors.centerIn: parent
    modal: true
    standardButtons: Dialog.Ok | Dialog.Cancel

    // documentModel and documentView accessed via context properties
    property int targetRow: -1
    property string mode: "key_set"  // "key_set" or "set_insert_key"

    function loadKeys() {
        keyListModel.clear()
        var idx = documentView.index(targetRow, 0)
        var keys = documentModel.getAvailableKeys(idx)
        for (var i = 0; i < keys.length; i++) {
            keyListModel.append(keys[i])
        }
        keyListView.currentIndex = -1
    }

    function loadSetInsertKeys() {
        keyListModel.clear()
        var idx = documentView.index(targetRow, 0)
        var keys = documentModel.getSetInsertKeyCandidates(idx)
        for (var i = 0; i < keys.length; i++) {
            keyListModel.append(keys[i])
        }
        keyListView.currentIndex = -1
    }

    onAccepted: {
        if (keyListView.currentIndex >= 0) {
            var uuid = keyListModel.get(keyListView.currentIndex).uuid
            var idx = documentView.index(targetRow, 0)
            if (mode === "set_insert_key") {
                documentModel.setInsertKey(idx, uuid)
            } else {
                documentModel.trySetKey(idx, uuid)
            }
        }
    }

    ListModel { id: keyListModel }

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        Rectangle {
            Layout.fillWidth: true
            height: 24
            color: DSTheme.midlight

            RowLayout {
                anchors.fill: parent
                spacing: 0
                Label {
                    text: "  Key Instance ID"
                    font.bold: true; color: DSTheme.secondaryText
                    Layout.preferredWidth: 300
                }
                Rectangle { width: 1; Layout.fillHeight: true; color: DSTheme.separator }
                Label {
                    text: "  Name"
                    font.bold: true; color: DSTheme.secondaryText
                    Layout.fillWidth: true
                }
            }
        }

        ListView {
            id: keyListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: keyListModel
            currentIndex: -1

            delegate: Rectangle {
                width: keyListView.width
                height: 28
                color: keyListView.currentIndex === index
                       ? DSTheme.highlight
                       : index % 2 === 0 ? "transparent" : DSTheme.alternateBase

                RowLayout {
                    anchors.fill: parent
                    spacing: 0

                    Label {
                        text: model.uuid
                        font.family: DSTheme.fontMono
                        color: keyListView.currentIndex === index ? DSTheme.highlightedText : DSTheme.tertiaryText
                        Layout.preferredWidth: 300
                        leftPadding: 8
                        elide: Text.ElideRight
                    }
                    Rectangle { width: 1; Layout.fillHeight: true; color: DSTheme.separator }
                    Label {
                        text: model.name
                        color: keyListView.currentIndex === index ? DSTheme.highlightedText : DSTheme.text
                        Layout.fillWidth: true
                        leftPadding: 8
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: keyListView.currentIndex = index
                    onDoubleClicked: {
                        keyListView.currentIndex = index
                        keyDialog.accept()
                    }
                }
            }
        }
    }
}
