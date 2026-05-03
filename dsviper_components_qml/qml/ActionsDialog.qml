import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * Actions Panel
 * Shared between cdbe, graph_editor.
 * Requires context property: actionsModel
 */
Window {
    id: root
    title: "Actions"
    width: 350; height: 400
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
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            height: 24
            color: DSTheme.midlight
            Label {
                anchors.fill: parent
                anchors.leftMargin: 8
                text: "Double-click to toggle"
                font.pixelSize: DSTheme.fontCaption; color: DSTheme.labelText
                verticalAlignment: Text.AlignVCenter
            }
        }

        ListView {
            id: actionsView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: actionsModel

            delegate: Rectangle {
                width: actionsView.width
                height: 28
                color: index % 2 === 0 ? DSTheme.window : DSTheme.alternateBase

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    spacing: 8

                    Image {
                        source: model.enabled
                            ? "../images/eye" + DSTheme.iconSuffix + ".png"
                            : "../images/eye.slash" + DSTheme.iconSuffix + ".png"
                        width: 16; height: 16
                        fillMode: Image.PreserveAspectFit
                        opacity: model.enabled ? 1.0 : 0.4
                    }
                    Label {
                        text: model.label
                        color: model.enabled ? DSTheme.secondaryText : DSTheme.disabledText
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                        verticalAlignment: Text.AlignVCenter
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    onDoubleClicked: actionsModel.toggleEnabled(index)
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 24
            color: DSTheme.midlight
            Label {
                anchors.centerIn: parent
                text: "actions: %1".arg(actionsModel.rowCount())
                font.pixelSize: DSTheme.fontCaption; color: DSTheme.labelText
            }
        }
    }
}
