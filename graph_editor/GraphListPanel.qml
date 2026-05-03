import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../dsviper_components_qml/qml" as DS

// List component
// Displays vertices and edges with circle rendering and multi-selection.
// Matches AppKit reference: dashed circles/lines for non-existing vertices.
// Canvas for geometry (circles, lines, dash patterns), Labels for text (pixel-perfect centering).

Rectangle {
    color: DS.DSTheme.window

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 4
        Label {
            text: "Elements"
            font.bold: true
            color: DS.DSTheme.text
        }
        ListView {
            id: listView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: listModel
            // Multi-selection support
            property var selectedIndices: []

            // Animated transitions — triggered by beginInsertRows/beginRemoveRows
            add: Transition { NumberAnimation { properties: "opacity"; from: 0; to: 1; duration: 200 } }
            remove: Transition { NumberAnimation { properties: "opacity"; from: 1; to: 0; duration: 200 } }
            displaced: Transition { NumberAnimation { properties: "y"; duration: 200; easing.type: Easing.OutQuad } }

            delegate: Rectangle {
                id: listDelegate
                width: listView.width
                height: model.isVertex ? Math.max(vertexCircleSize + 8, 28) : Math.max(edgeRowHeight + 8, 28)
                color: model.selected ? DS.DSTheme.highlight
                    : (index % 2 === 0 ? DS.DSTheme.alternateBase : DS.DSTheme.midlight)

                // Vertex circle size — dynamic based on label
                readonly property int vertexCircleSize: {
                    var textLen = (model.label || "").length
                    var s = Math.max(textLen * 8 + 10, 24)
                    return Math.min(s, 40)
                }
                // Edge row height = max of both vertex circles
                readonly property int edgeRowHeight: {
                    var vaLen = (model.vaLabel || "").length
                    var vbLen = (model.vbLabel || "").length
                    var sa = Math.max(vaLen * 8 + 10, 24)
                    var sb = Math.max(vbLen * 8 + 10, 24)
                    return Math.min(Math.max(sa, sb), 40)
                }

                // --- Vertex delegate ---
                Item {
                    visible: model.isVertex
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    anchors.topMargin: 4
                    anchors.bottomMargin: 4

                    Canvas {
                        id: vertexCanvas
                        width: listDelegate.vertexCircleSize
                        height: listDelegate.vertexCircleSize
                        anchors.verticalCenter: parent.verticalCenter
                        renderStrategy: Canvas.Immediate

                        property bool vertexExists: model.exists !== false
                        property color vertexColor: model.elementColor || DS.DSTheme.highlightedText

                        onPaint: {
                            var ctx = getContext("2d")
                            ctx.reset()
                            drawCircle(ctx, 0, 0, width, height, vertexExists, vertexColor)
                        }
                        onVertexExistsChanged: requestPaint()
                        onVertexColorChanged: requestPaint()
                    }

                    Label {
                        anchors.centerIn: vertexCanvas
                        text: model.label || ""
                        font.pixelSize: DS.DSTheme.fontCaption
                        color: model.exists !== false ? DS.DSTheme.validElement : DS.DSTheme.invalidElement
                    }
                }

                // --- Edge delegate ---
                Item {
                    visible: !model.isVertex
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    anchors.rightMargin: 8
                    anchors.topMargin: 4
                    anchors.bottomMargin: 4

                    Canvas {
                        id: edgeCanvas
                        width: parent.width
                        height: listDelegate.edgeRowHeight
                        anchors.verticalCenter: parent.verticalCenter
                        renderStrategy: Canvas.Immediate

                        property bool vaExist: model.vaExists !== false
                        property bool vbExist: model.vbExists !== false
                        property color vaCol: model.vaColor || "transparent"
                        property color vbCol: model.vbColor || "transparent"
                        property int circleSize: listDelegate.edgeRowHeight

                        onPaint: {
                            var ctx = getContext("2d")
                            ctx.reset()
                            var s = circleSize
                            var totalW = width
                            // Draw va circle at left
                            drawCircle(ctx, 0, 0, s, s, vaExist, vaCol)
                            // Draw vb circle at right
                            var vbX = totalW - s
                            drawCircle(ctx, vbX, 0, s, s, vbExist, vbCol)
                            // Draw edge line between circle edges
                            var isValid = vaExist && vbExist
                            var lineY = s / 2
                            var margin = 3
                            ctx.beginPath()
                            ctx.moveTo(s + margin, lineY)
                            ctx.lineTo(vbX - margin, lineY)
                            ctx.lineWidth = 2
                            ctx.strokeStyle = isValid ? DS.DSTheme.text : DS.DSTheme.secondaryText
                            if (!isValid)
                                ctx.setLineDash([4, 4])
                            else
                                ctx.setLineDash([])
                            ctx.stroke()
                        }
                        onVaExistChanged: requestPaint()
                        onVbExistChanged: requestPaint()
                        onVaColChanged: requestPaint()
                        onVbColChanged: requestPaint()
                    }

                    // Va label
                    Label {
                        x: listDelegate.edgeRowHeight / 2 - implicitWidth / 2
                        anchors.verticalCenter: edgeCanvas.verticalCenter
                        text: model.vaLabel || ""
                        font.pixelSize: DS.DSTheme.fontCaption
                        color: model.vaExists !== false ? DS.DSTheme.validElement : DS.DSTheme.invalidElement
                    }

                    // Vb label
                    Label {
                        x: edgeCanvas.width - listDelegate.edgeRowHeight / 2 - implicitWidth / 2
                        anchors.verticalCenter: edgeCanvas.verticalCenter
                        text: model.vbLabel || ""
                        font.pixelSize: DS.DSTheme.fontCaption
                        color: model.vbExists !== false ? DS.DSTheme.validElement : DS.DSTheme.invalidElement
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: (mouse) => {
                        if (mouse.modifiers & Qt.ShiftModifier) {
                            let idx = listView.selectedIndices.indexOf(index)
                            if (idx >= 0) {
                                listView.selectedIndices.splice(idx, 1)
                            } else {
                                listView.selectedIndices.push(index)
                            }
                        } else {
                            listView.selectedIndices = [index]
                        }
                        listModel.setSelection(listView.selectedIndices)
                    }
                }
            }
        }
    }

    // Draw circle only (no text) — Canvas handles geometry, Labels handle text
    function drawCircle(ctx, x, y, w, h, exists, color) {
        var cx = x + w / 2
        var cy = y + h / 2
        var r = (w - 2) / 2

        // Fill circle (only if exists)
        if (exists) {
            ctx.beginPath()
            ctx.arc(cx, cy, r, 0, 2 * Math.PI)
            ctx.fillStyle = color
            ctx.fill()
        }

        // Border — solid if exists, dashed if not
        ctx.beginPath()
        ctx.arc(cx, cy, r, 0, 2 * Math.PI)
        ctx.lineWidth = 2
        ctx.strokeStyle = exists ? DS.DSTheme.text : DS.DSTheme.secondaryText
        if (!exists)
            ctx.setLineDash([4, 4])
        else
            ctx.setLineDash([])
        ctx.stroke()
    }
}
