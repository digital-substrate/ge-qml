import QtQuick
import QtQuick.Controls

/**
 * DSDocumentsDialog — Documents panel in a standalone Window.
 *
 * For applications where the documents panel is a secondary window
 * (e.g. graph_editor) rather than the central widget (dbe, cdbe).
 *
 * Requires context properties: abstractionModel, keyModel, documentModel
 */
Window {
    id: root
    title: "Documents"
    width: 900; height: 600
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

    DocumentsPanel {
        anchors.fill: parent
    }
}
