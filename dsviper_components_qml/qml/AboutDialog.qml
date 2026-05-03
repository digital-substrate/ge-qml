import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * About Dialog
 * Shared between dbe, cdbe, graph_editor.
 * Parent must bind: model property to licenseModel context property.
 */
Dialog {
    id: root
    title: root.model ? "About %1".arg(root.model.appName) : "About"
    width: 450
    height: 280
    anchors.centerIn: parent
    modal: true
    standardButtons: Dialog.Ok

    property var model: null

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        Label {
            text: root.model ? "<b>%1</b> v%2".arg(root.model.appName).arg(root.model.version) : ""
            textFormat: Text.RichText
            font.pixelSize: 16
            color: DSTheme.text
            Layout.alignment: Qt.AlignHCenter
        }

        Label {
            text: root.model ? root.model.appDescription : ""
            color: DSTheme.secondaryText
            Layout.alignment: Qt.AlignHCenter
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: DSTheme.separator }

        Label {
            text: root.model ? root.model.copyright : ""
            color: DSTheme.tertiaryText
            Layout.alignment: Qt.AlignHCenter
        }

        Label {
            text: root.model ? "Licensed under %1".arg(root.model.licenseId) : ""
            font.pixelSize: DSTheme.fontCaption
            color: DSTheme.labelText
            Layout.alignment: Qt.AlignHCenter
        }

        Item { Layout.fillHeight: true }

        Button {
            text: "License..."
            Layout.alignment: Qt.AlignHCenter
            onClicked: licenseDialog.visible = true
        }
    }
}
