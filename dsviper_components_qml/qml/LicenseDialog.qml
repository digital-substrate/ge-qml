import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * License Dialog
 * Shared between dbe, cdbe, graph_editor.
 * Parent must bind: model property to licenseModel context property.
 */
Window {
    id: root
    title: "License"
    width: 640; height: 480
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

    property var model: null

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true

            TextArea {
                readOnly: true
                text: root.model ? root.model.licenseText : ""
                font.family: DSTheme.fontMono; font.pixelSize: DSTheme.fontCaption
                color: DSTheme.text
                background: Rectangle { color: DSTheme.codeBackground }
                wrapMode: TextEdit.Wrap
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }
            Button {
                text: "Close"
                onClicked: root.close()
            }
        }
    }
}
