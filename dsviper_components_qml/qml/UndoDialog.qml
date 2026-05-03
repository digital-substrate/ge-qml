import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * Undo Stack Panel
 * Shared between cdbe, graph_editor.
 * Requires context property: undoModel
 */
Window {
    id: root
    title: "Undo Stack"
    width: 300; height: 400
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

        ListView {
            id: undoView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: undoModel
            currentIndex: undoModel.currentRow

            delegate: Rectangle {
                width: undoView.width
                height: 24
                color: index === undoView.currentIndex ? DSTheme.highlight : (index % 2 === 0 ? DSTheme.window : DSTheme.alternateBase)

                Label {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    text: model.label
                    color: index === undoView.currentIndex ? DSTheme.highlightedText : DSTheme.secondaryText
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 24
            color: DSTheme.midlight
            Label {
                anchors.centerIn: parent
                text: "items: %1".arg(undoModel.rowCount())
                font.pixelSize: DSTheme.fontCaption; color: DSTheme.labelText
            }
        }
    }
}
