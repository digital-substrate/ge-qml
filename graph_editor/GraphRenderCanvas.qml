import QtQuick
import QtQuick.Controls
import "../dsviper_components_qml/qml" as DS

// Render canvas
// Graph rendering with Canvas + mouse interaction.

Rectangle {
    id: renderArea

    // Exposed for menu/toolbar actions that need canvas dimensions and mouse position
    readonly property real lastMouseX: renderMouseArea.lastX
    readonly property real lastMouseY: renderMouseArea.lastY
    readonly property real canvasWidth: width
    readonly property real canvasHeight: height

    color: DS.DSTheme.canvasBackground
    focus: true

    Canvas {
        id: renderCanvas
        anchors.fill: parent
        renderStrategy: Canvas.Immediate

        onWidthChanged: if (renderModel) renderModel.setCanvasSize(width, height)
        onHeightChanged: if (renderModel) renderModel.setCanvasSize(width, height)

        Connections {
            target: renderModel
            function onGraphChanged() { renderCanvas.requestPaint() }
        }

        onPaint: {
            var ctx = getContext("2d")
            ctx.reset()

            // Background
            ctx.fillStyle = renderModel ? renderModel.backgroundColor() : DS.DSTheme.canvasBackground
            ctx.fillRect(0, 0, width, height)

            if (!renderModel) return

            // Edges
            var edges = renderModel.getEdges()
            for (var i = 0; i < edges.length; i++) {
                var e = edges[i]
                ctx.beginPath()
                ctx.moveTo(e.x0, e.y0)
                ctx.lineTo(e.x1, e.y1)
                ctx.strokeStyle = e.color
                ctx.lineWidth = e.lineWidth
                if (!e.isValid) {
                    ctx.setLineDash([4, 4])
                } else {
                    ctx.setLineDash([])
                }
                ctx.stroke()
            }

            // Vertices
            ctx.setLineDash([])
            var verts = renderModel.getVertices()
            for (var j = 0; j < verts.length; j++) {
                var v = verts[j]
                var cx = v.x + v.size / 2
                var cy = v.y + v.size / 2
                var radius = v.size / 2

                // Fill circle
                if (v.fillColor) {
                    ctx.beginPath()
                    ctx.arc(cx, cy, radius, 0, 2 * Math.PI)
                    ctx.fillStyle = v.fillColor
                    ctx.fill()
                }

                // Border
                ctx.beginPath()
                ctx.arc(cx, cy, radius, 0, 2 * Math.PI)
                ctx.strokeStyle = v.borderColor
                ctx.lineWidth = 2
                if (!v.isValid) {
                    ctx.setLineDash([3, 3])
                } else {
                    ctx.setLineDash([])
                }
                ctx.stroke()
                ctx.setLineDash([])

                // Label — font size known, center manually
                var fontSize = 13
                ctx.fillStyle = v.isValid ? DS.DSTheme.validElement : DS.DSTheme.invalidElement
                ctx.font = fontSize + "px sans-serif"
                ctx.textAlign = "center"
                ctx.textBaseline = "alphabetic"
                ctx.fillText(v.label, cx, cy + fontSize * 0.4)
            }

            // Connector
            var conn = renderModel.getConnector()
            if (conn) {
                ctx.beginPath()
                ctx.moveTo(conn.x0, conn.y0)
                ctx.lineTo(conn.x1, conn.y1)
                ctx.strokeStyle = DS.DSTheme.canvasHighlight
                ctx.lineWidth = 2.5
                ctx.setLineDash([4, 2])
                ctx.stroke()
                ctx.setLineDash([])

                // Redraw connector vertex on top
                var cv = conn.vertex
                var ccx = cv.x + cv.size / 2
                var ccy = cv.y + cv.size / 2
                var cr = cv.size / 2
                if (cv.fillColor) {
                    ctx.beginPath()
                    ctx.arc(ccx, ccy, cr, 0, 2 * Math.PI)
                    ctx.fillStyle = cv.fillColor
                    ctx.fill()
                }
                ctx.beginPath()
                ctx.arc(ccx, ccy, cr, 0, 2 * Math.PI)
                ctx.strokeStyle = cv.borderColor
                ctx.lineWidth = 2
                ctx.stroke()
                var cvFontSize = 13
                ctx.fillStyle = cv.isValid ? DS.DSTheme.validElement : DS.DSTheme.invalidElement
                ctx.font = cvFontSize + "px sans-serif"
                ctx.textAlign = "center"
                ctx.textBaseline = "alphabetic"
                ctx.fillText(cv.label, ccx, ccy + cvFontSize * 0.4)
            }
        }
    }

    // Mouse interaction
    MouseArea {
        id: renderMouseArea
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton
        hoverEnabled: true

        property real lastX: 0
        property real lastY: 0

        onPressed: (mouse) => {
            renderArea.forceActiveFocus()
            if (renderModel)
                renderModel.mousePress(mouse.x, mouse.y, mouse.modifiers)
        }
        onPositionChanged: (mouse) => {
            lastX = mouse.x; lastY = mouse.y
            if (mouse.buttons & Qt.LeftButton) {
                if (renderModel)
                    renderModel.mouseMove(mouse.x, mouse.y, mouse.modifiers)
            }
        }
        onReleased: (mouse) => {
            if (renderModel)
                renderModel.mouseRelease(mouse.x, mouse.y)
        }
    }
}
