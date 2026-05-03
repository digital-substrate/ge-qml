import QtQuick
import QtQuick.Controls

/**
 * DSGroupBox — GroupBox with AppKit-style rounded border.
 *
 * Transparent background with thin rounded border, title above the box.
 * Drop-in replacement for GroupBox.
 */
GroupBox {
    background: Rectangle {
        y: parent.topPadding - parent.bottomPadding
        width: parent.width
        height: parent.height - parent.topPadding + parent.bottomPadding
        color: "transparent"
        border.color: DSTheme.border
        border.width: 1
        radius: 8
    }
}
