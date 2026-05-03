import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../dsviper_components_qml/qml" as DS

// Tags component
// Displays key/value tags with set/update/unset actions.

Rectangle {
    color: DS.DSTheme.window

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 4
        Label {
            text: "Tags"
            font.bold: true
            color: DS.DSTheme.text
        }
        // Table header — Key / Value
        Rectangle {
            Layout.fillWidth: true
            height: 20
            color: DS.DSTheme.window
            border.color: DS.DSTheme.light
            border.width: 0.5
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 4
                spacing: 0
                Label {
                    Layout.preferredWidth: 80
                    text: "Key"
                    font.bold: true
                    color: DS.DSTheme.tertiaryText
                }
                Rectangle { width: 1; height: parent.height; color: DS.DSTheme.light }
                Label {
                    Layout.fillWidth: true
                    leftPadding: 8
                    text: "Value"
                    font.bold: true
                    color: DS.DSTheme.tertiaryText
                }
            }
        }
        ListView {
            id: tagsView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: tagsModel
            property int selectedRow: -1

            // Animated transitions
            add: Transition { NumberAnimation { properties: "opacity"; from: 0; to: 1; duration: 200 } }
            remove: Transition { NumberAnimation { properties: "opacity"; from: 1; to: 0; duration: 200 } }
            displaced: Transition { NumberAnimation { properties: "y"; duration: 200; easing.type: Easing.OutQuad } }

            delegate: Rectangle {
                width: tagsView.width
                height: 20
                color: index === tagsView.selectedRow ? DS.DSTheme.highlight
                    : (index % 2 === 0 ? DS.DSTheme.window : DS.DSTheme.alternateBase)

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 4
                    spacing: 0
                    Label {
                        Layout.preferredWidth: 80
                        text: model.tagKey || ""
                        color: DS.DSTheme.secondaryText
                        elide: Text.ElideRight
                    }
                    Label {
                        Layout.fillWidth: true
                        leftPadding: 8
                        text: model.tagValue || ""
                        color: DS.DSTheme.text
                        elide: Text.ElideRight
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        tagsView.selectedRow = index
                        tagKeyField.text = model.tagKey
                        tagValueField.text = model.tagValue
                    }
                }
            }
        }
        RowLayout {
            spacing: 4
            TextField {
                id: tagKeyField
                Layout.preferredWidth: 80
                placeholderText: "key"
                color: DS.DSTheme.text
                background: Rectangle { color: DS.DSTheme.button; radius: 2 }
            }
            TextField {
                id: tagValueField
                Layout.fillWidth: true
                placeholderText: "value"
                color: DS.DSTheme.text
                background: Rectangle { color: DS.DSTheme.button; radius: 2 }
            }
        }
        RowLayout {
            Layout.alignment: Qt.AlignRight
            spacing: 8
            RoundButton {
                text: "\u002B"
                font.pixelSize: 14
                implicitWidth: 28; implicitHeight: 28
                enabled: tagsModel.enabled
                onClicked: tagsModel.setTag(tagKeyField.text, tagValueField.text)
                ToolTip.visible: hovered
                ToolTip.text: "Set tag"
                ToolTip.delay: 500
            }
            RoundButton {
                text: "\u003D"
                font.pixelSize: 14
                implicitWidth: 28; implicitHeight: 28
                enabled: tagsModel.enabled
                onClicked: tagsModel.updateTag(tagKeyField.text, tagValueField.text)
                ToolTip.visible: hovered
                ToolTip.text: "Update tag"
                ToolTip.delay: 500
            }
            RoundButton {
                text: "\u2212"
                font.pixelSize: 14
                implicitWidth: 28; implicitHeight: 28
                enabled: tagsModel.enabled && tagsView.selectedRow >= 0
                onClicked: {
                    let keys = []
                    keys.push(tagKeyField.text)
                    tagsModel.unsetTags(keys)
                }
                ToolTip.visible: hovered
                ToolTip.text: "Unset tag"
                ToolTip.delay: 500
            }
        }
    }
}
