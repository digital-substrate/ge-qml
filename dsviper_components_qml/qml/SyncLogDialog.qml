import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * Sync Log Panel
 * Shared between cdbe, graph_editor.
 * Requires context property: liveModel
 */
Window {
    id: root
    title: "Synchronizer Log"
    width: 500; height: 300
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
        anchors.margins: 4
        spacing: 4

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true

            TextArea {
                id: syncLogText
                readOnly: true
                wrapMode: TextEdit.Wrap
                font.family: DSTheme.fontMono
                color: DSTheme.secondaryText
                background: Rectangle { color: DSTheme.codeBackground }
                text: ""
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }
            Button {
                text: "Clear"
                onClicked: syncLogText.text = ""
            }
        }
    }

    Connections {
        target: liveModel
        function onSyncLogMessage(msg) {
            syncLogText.text = syncLogText.text + msg + "\n"
        }
    }
}
