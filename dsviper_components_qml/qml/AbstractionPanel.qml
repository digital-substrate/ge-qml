import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Abstraction panel — View+Delegate for abstraction_model.py
// abstractionModel accessed via context property.

Rectangle {
    id: root
    color: DSTheme.window

    // Signals up — parent assembly handles dialog opening
    signal newInstanceRequested(int row)

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Header
        Rectangle {
            Layout.fillWidth: true
            height: 24
            color: DSTheme.midlight

            Label {
                anchors.fill: parent
                text: "  Abstraction"
                font.bold: true; color: DSTheme.secondaryText
                verticalAlignment: Text.AlignVCenter
            }
        }

        ListView {
            id: abstractionView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: abstractionModel
            currentIndex: -1

            delegate: Rectangle {
                width: abstractionView.width
                height: 26
                color: abstractionView.currentIndex === index
                       ? DSTheme.highlight
                       : mouseAbstr.containsMouse
                         ? DSTheme.hoverBackground
                         : "transparent"

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    anchors.rightMargin: 4
                    spacing: 4

                    Label {
                        text: model.name
                        font.bold: true
                        color: abstractionView.currentIndex === index ? DSTheme.highlightedText : DSTheme.text
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }

                    // New Instance button
                    ToolButton {
                        icon.source: "../images/plus.circle" + DSTheme.iconSuffix + ".png"
                        icon.width: 22; icon.height: 22
                        implicitWidth: 26; implicitHeight: 26
                        background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                        visible: model.category === "concept" && (mouseAbstr.containsMouse || abstractionView.currentIndex === index)
                        opacity: abstractionView.currentIndex === index ? 1.0 : 0.6
                        onClicked: root.newInstanceRequested(index)
                        ToolTip.visible: hovered
                        ToolTip.text: "New Instance"
                        ToolTip.delay: 500
                    }
                }

                MouseArea {
                    id: mouseAbstr
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.LeftButton
                    z: -1
                    onClicked: {
                        abstractionView.currentIndex = index
                        abstractionModel.select(index)
                    }
                }
            }
        }
    }

    // Navigation signal — jump-to-key updates ListView selection
    Connections {
        target: abstractionModel
        function onAbstractionIndexChanged(row) {
            abstractionView.currentIndex = row
        }
    }
}
