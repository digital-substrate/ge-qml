import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * DSToolbarGroup — NSToolbarItemGroup equivalent.
 * Groups toolbar buttons with a shared bordered background and a single group label.
 * Buttons inside show icon-only; the group label appears below.
 *
 * Usage:
 *   DSToolbarGroup {
 *       label: "Head"
 *       ToolButton { icon.source: "..."; onClicked: ... }
 *       ToolButton { icon.source: "..."; onClicked: ... }
 *   }
 */
ColumnLayout {
    id: root
    spacing: 2

    property string label: ""
    default property alias buttons: buttonRow.data

    // Bordered group background with icon buttons
    Rectangle {
        Layout.alignment: Qt.AlignHCenter
        implicitWidth: buttonRow.implicitWidth + 12
        implicitHeight: buttonRow.implicitHeight + 8
        radius: height / 2
        color: DSTheme.midlight
        border.color: DSTheme.inputBorder
        border.width: 0.5

        Row {
            id: buttonRow
            anchors.centerIn: parent
            spacing: 2

            // Strip Fusion square highlight from all ToolButtons
            Component.onCompleted: {
                for (var i = 0; i < children.length; i++) {
                    var btn = children[i]
                    if (btn instanceof ToolButton) {
                        btn.background = flatBg.createObject(btn)
                    }
                }
            }
        }
    }

    Component {
        id: flatBg
        Rectangle {
            color: "transparent"
            radius: 4
        }
    }

    // Group label below
    Text {
        Layout.alignment: Qt.AlignHCenter
        text: root.label
        color: DSTheme.labelText
        font.pixelSize: DSTheme.fontCaption
        visible: root.label !== ""
    }
}
