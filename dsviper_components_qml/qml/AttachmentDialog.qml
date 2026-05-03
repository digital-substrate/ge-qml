import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Attachment dialog — used by "New Instance" and "Add Attachments" actions.

Dialog {
    id: attachmentDialog
    title: mode === "new_instance" ? "Create Attachments" : "Add Attachments"
    width: 500
    height: 400
    anchors.centerIn: parent
    modal: true
    standardButtons: Dialog.Ok | Dialog.Cancel

    // abstractionModel and keyModel accessed via context properties
    property string mode: "new_instance"  // "new_instance" or "add_attachments"
    property int targetRow: -1

    function loadNewInstance(row) {
        attachmentListModel.clear()
        var atts = abstractionModel.getNewInstanceAttachments(row)
        for (var i = 0; i < atts.length; i++) {
            attachmentListModel.append({
                "name": atts[i].name,
                "description": atts[i].description,
                "checked": true
            })
        }
        generateNewUuid()
        uuidField.enabled = true
        generateBtn.enabled = true
    }

    function loadAddAttachments(row) {
        attachmentListModel.clear()
        var atts = keyModel.getAddAttachmentsData(row)
        for (var i = 0; i < atts.length; i++) {
            attachmentListModel.append({
                "name": atts[i].name,
                "description": atts[i].description,
                "checked": true
            })
        }
        uuidField.text = ""
        uuidField.enabled = false
        generateBtn.enabled = false
    }

    function generateNewUuid() {
        var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0
            var v = c === 'x' ? r : (r & 0x3 | 0x8)
            return v.toString(16)
        })
        uuidField.text = uuid
    }

    onAccepted: {
        var selected = []
        for (var i = 0; i < attachmentListModel.count; i++) {
            if (attachmentListModel.get(i).checked)
                selected.push(i)
        }

        if (mode === "new_instance") {
            abstractionModel.createNewInstance(uuidField.text, selected)
        } else {
            keyModel.addAttachments(targetRow, selected)
        }
    }

    ListModel { id: attachmentListModel }

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        // UUID row
        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Label {
                text: "Instance ID:"
                font.bold: true
                color: DSTheme.secondaryText
            }
            TextField {
                id: uuidField
                Layout.fillWidth: true
                font.family: DSTheme.fontMono
                color: DSTheme.text
                background: Rectangle { color: DSTheme.midlight; radius: 2 }
            }
            Button {
                id: generateBtn
                text: "Generate"
                onClicked: attachmentDialog.generateNewUuid()
            }
        }

        // Attachment checklist
        Rectangle {
            Layout.fillWidth: true
            height: 24
            color: DSTheme.midlight
            Label {
                anchors.verticalCenter: parent.verticalCenter
                text: "  Attachments"
                font.bold: true; color: DSTheme.secondaryText
            }
        }

        ListView {
            id: attachmentListView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: attachmentListModel

            delegate: Rectangle {
                width: attachmentListView.width
                height: 32
                color: index % 2 === 0 ? "transparent" : DSTheme.alternateBase

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    spacing: 8

                    CheckBox {
                        checked: model.checked
                        onToggled: attachmentListModel.setProperty(index, "checked", checked)
                    }
                    Label {
                        text: model.name
                        color: DSTheme.text
                        Layout.fillWidth: true
                    }
                }

                ToolTip.visible: mouseAttachment.containsMouse
                ToolTip.text: model.description
                ToolTip.delay: 500

                MouseArea {
                    id: mouseAttachment
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.NoButton
                }
            }
        }
    }
}
