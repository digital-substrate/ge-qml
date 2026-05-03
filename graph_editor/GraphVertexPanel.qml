import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../dsviper_components_qml/qml" as DS

// Vertex component
// SpinBox/Slider controls for value, color, position X/Y.
// Uses illusion pattern: preview while stepper held, commit on release.

Rectangle {
    color: DS.DSTheme.window

    ColorDialog {
        id: colorDialog
        selectedColor: vertexModel.color
        onSelectedColorChanged: if (visible) vertexModel.previewColor(selectedColor)
        onAccepted: vertexModel.setColor(selectedColor)
        onRejected: vertexModel.cancelColor()
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 6
        enabled: vertexModel.enabled && vertexModel.hasVertex

        Label {
            text: "Vertex"
            font.bold: true
            color: DS.DSTheme.text
        }

        GridLayout {
            columns: 3
            columnSpacing: 6
            rowSpacing: 6
            Layout.fillWidth: true

            // Value — illusion pattern: preview while stepper held, commit on release
            Label { text: "Value:"; color: DS.DSTheme.labelText; Layout.alignment: Qt.AlignRight }
            SpinBox {
                id: vertexValueSpinBox
                Layout.preferredWidth: 80
                from: 0; to: 1000
                value: vertexModel.value
                editable: true
                property bool stepping: up.pressed || down.pressed
                onValueModified: {
                    if (stepping)
                        vertexModel.previewValue(value)
                    else
                        vertexModel.setValue(value)
                }
                onSteppingChanged: {
                    if (!stepping)
                        vertexModel.setValue(value)
                }
            }
            Item { Layout.fillWidth: true }

            // Color
            Label { text: "Color:"; color: DS.DSTheme.labelText; Layout.alignment: Qt.AlignRight }
            Rectangle {
                id: colorSwatch
                width: 48; height: 24
                radius: 3
                color: vertexModel.color
                border.color: DS.DSTheme.light
                border.width: 1
                MouseArea {
                    anchors.fill: parent
                    onClicked: colorDialog.open()
                }
            }
            Item { Layout.fillWidth: true }

            // Position X — illusion pattern: preview while stepper held, commit on release
            Label { text: "X:"; color: DS.DSTheme.labelText; Layout.alignment: Qt.AlignRight }
            SpinBox {
                id: xSpinBox
                Layout.preferredWidth: 80
                from: 0; to: 1000
                value: vertexModel.positionX
                editable: true
                property bool stepping: up.pressed || down.pressed
                onValueModified: {
                    if (stepping)
                        vertexModel.previewPositionX(value)
                    else
                        vertexModel.setPositionX(value)
                }
                onSteppingChanged: {
                    if (!stepping)
                        vertexModel.setPositionX(value)
                }
            }
            Slider {
                id: xSlider
                Layout.fillWidth: true
                from: 0; to: 1000
                value: vertexModel.positionX
                onMoved: {
                    xSpinBox.value = Math.round(value)
                    vertexModel.previewPositionX(Math.round(value))
                }
                onPressedChanged: {
                    if (!pressed) {
                        vertexModel.setPositionX(Math.round(value))
                    }
                }
            }

            // Position Y — illusion pattern: preview while stepper held, commit on release
            Label { text: "Y:"; color: DS.DSTheme.labelText; Layout.alignment: Qt.AlignRight }
            SpinBox {
                id: ySpinBox
                Layout.preferredWidth: 80
                from: 0; to: 1000
                value: vertexModel.positionY
                editable: true
                property bool stepping: up.pressed || down.pressed
                onValueModified: {
                    if (stepping)
                        vertexModel.previewPositionY(value)
                    else
                        vertexModel.setPositionY(value)
                }
                onSteppingChanged: {
                    if (!stepping)
                        vertexModel.setPositionY(value)
                }
            }
            Slider {
                id: ySlider
                Layout.fillWidth: true
                from: 0; to: 1000
                value: vertexModel.positionY
                onMoved: {
                    ySpinBox.value = Math.round(value)
                    vertexModel.previewPositionY(Math.round(value))
                }
                onPressedChanged: {
                    if (!pressed) {
                        vertexModel.setPositionY(Math.round(value))
                    }
                }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
