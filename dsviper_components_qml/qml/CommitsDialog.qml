import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * Commits Panel
 * Shared between cdbe, graph_editor.
 * Requires context property: commitsModel
 */
Window {
    id: root
    title: "Commits — %1".arg(appPid)
    width: 420; height: 800
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
        anchors.margins: 8
        spacing: 4

        // --- Top buttons
        RowLayout {
            spacing: 8
            Button {
                text: "Delete"; enabled: commitsModel.canDelete
                onClicked: commitsModel.deleteCurrent()
                opacity: enabled ? 1.0 : 0.4
                palette.button: DSTheme.dangerButton; palette.buttonText: DSTheme.highlightedText
            }
            Item { Layout.fillWidth: true }
            Button {
                text: "Reset"; enabled: commitsModel.canReset
                onClicked: commitsModel.resetCommits()
                opacity: enabled ? 1.0 : 0.4
                palette.button: DSTheme.dangerButton; palette.buttonText: DSTheme.highlightedText
            }
        }

        // --- DAG Graph
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: DSTheme.codeBackground
        Flickable {
            id: graphFlickable
            anchors.fill: parent
            clip: true
            contentWidth: Math.max(commitsModel.graphWidth, width)
            contentHeight: Math.max(commitsModel.graphHeight, height)

            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
            ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded }
            boundsBehavior: Flickable.StopAtBounds

            // Tell model our viewport height
            onHeightChanged: commitsModel.setViewportHeight(height)
            Component.onCompleted: commitsModel.setViewportHeight(height)

            Canvas {
                id: dagCanvas
                onWidthChanged: requestPaint()
                onHeightChanged: requestPaint()
                width: graphFlickable.contentWidth
                height: graphFlickable.contentHeight

                property var graphNodes: []
                property var graphEdges: []
                property var graphMerges: []

                property int lastNodeX: 0
                property int lastNodeY: 0

                Connections {
                    target: commitsModel
                    function onGraphChanged() {
                        dagCanvas.graphNodes = commitsModel.graphNodes()
                        dagCanvas.graphEdges = commitsModel.graphEdges()
                        dagCanvas.graphMerges = commitsModel.graphMerges()
                        dagCanvas.requestPaint()
                        // Ensure current node is visible — only scroll when current changed
                        var nx = commitsModel.currentNodeX
                        var ny = commitsModel.currentNodeY
                        if (nx !== dagCanvas.lastNodeX || ny !== dagCanvas.lastNodeY) {
                            dagCanvas.lastNodeX = nx
                            dagCanvas.lastNodeY = ny
                            var margin = 40
                            var vx = graphFlickable.contentX
                            var vy = graphFlickable.contentY
                            var vw = graphFlickable.width
                            var vh = graphFlickable.height
                            if (nx < vx + margin || nx > vx + vw - margin)
                                graphFlickable.contentX = Math.min(
                                    Math.max(0, nx - vw / 2),
                                    Math.max(0, graphFlickable.contentWidth - vw))
                            if (ny < vy + margin || ny > vy + vh - margin)
                                graphFlickable.contentY = Math.min(
                                    Math.max(0, ny - vh / 2),
                                    Math.max(0, graphFlickable.contentHeight - vh))
                        }
                    }
                }

                onPaint: {
                    var ctx = getContext("2d")
                    ctx.reset()
                    ctx.fillStyle = DSTheme.codeBackground
                    ctx.fillRect(0, 0, width, height)

                    var nodes = graphNodes
                    var edges = graphEdges
                    var merges = graphMerges
                    var nodeSize = 17

                    // --- Draw edges (L-shaped) ---
                    for (var ei = 0; ei < edges.length; ei++) {
                        var e = edges[ei]
                        // Horizontal segment (parent color)
                        ctx.beginPath()
                        ctx.strokeStyle = e.parentColor
                        ctx.lineWidth = 1.5
                        ctx.moveTo(e.px, e.py)
                        ctx.lineTo(e.cx, e.py)
                        ctx.stroke()

                        // Vertical segment (child color)
                        ctx.beginPath()
                        ctx.strokeStyle = e.childColor
                        ctx.lineWidth = 1.5
                        ctx.moveTo(e.cx, e.py)
                        ctx.lineTo(e.cx, e.cy)
                        ctx.stroke()

                        // Dot at junction
                        var dotSize = 5
                        ctx.beginPath()
                        ctx.fillStyle = e.parentColor
                        ctx.arc(e.cx, e.py, dotSize / 2, 0, 2 * Math.PI)
                        ctx.fill()
                    }

                    // --- Draw merges (L-shaped path via control points) ---
                    for (var mi = 0; mi < merges.length; mi++) {
                        var m = merges[mi]
                        ctx.beginPath()
                        ctx.strokeStyle = m.color
                        ctx.lineWidth = 1
                        ctx.moveTo(m.ncx, m.ncy)
                        ctx.lineTo(m.c1x, m.c1y)
                        ctx.lineTo(m.c2x, m.c2y)
                        ctx.lineTo(m.tcx, m.tcy)
                        ctx.stroke()
                    }

                    // --- Draw nodes ---
                    var halfNode = nodeSize / 2
                    for (var ni = 0; ni < nodes.length; ni++) {
                        var n = nodes[ni]
                        var cx = n.x + halfNode
                        var cy = n.y + halfNode
                        var innerR = (nodeSize - 2) / 2

                        // Fill background
                        ctx.beginPath()
                        ctx.arc(cx, cy, innerR, 0, 2 * Math.PI)
                        ctx.fillStyle = DSTheme.codeBackground
                        ctx.fill()

                        // Border
                        ctx.beginPath()
                        ctx.arc(cx, cy, innerR, 0, 2 * Math.PI)
                        ctx.strokeStyle = n.color
                        ctx.lineWidth = 1.5
                        ctx.stroke()

                        // Filled inner circle for current commit
                        if (n.isCurrent) {
                            ctx.beginPath()
                            ctx.arc(cx, cy, innerR - 3, 0, 2 * Math.PI)
                            ctx.fillStyle = n.color
                            ctx.fill()
                        }

                        // Dashed border for marked commit — manual dash arcs
                        // (QML Canvas setLineDash is unreliable)
                        if (n.isMarked) {
                            var mr = halfNode + 1.5
                            var circumference = 2 * Math.PI * mr
                            var dashLen = 4, gapLen = 2
                            var segTotal = dashLen + gapLen
                            var segCount = Math.round(circumference / segTotal)
                            var dashAngle = (dashLen / circumference) * 2 * Math.PI
                            var segAngle = (2 * Math.PI) / segCount
                            ctx.strokeStyle = DSTheme.highlightedText
                            ctx.lineWidth = 1.5
                            for (var si = 0; si < segCount; si++) {
                                var startA = si * segAngle
                                ctx.beginPath()
                                ctx.arc(cx, cy, mr, startA, startA + dashAngle)
                                ctx.stroke()
                            }
                        }

                        // Order labels rendered by Repeater below (pixel-perfect centering)
                    }
                }

                // Order labels — QML Labels for pixel-perfect centering
                Repeater {
                    model: dagCanvas.graphNodes
                    Label {
                        visible: modelData.order > 0 && !modelData.isCurrent
                        x: modelData.x + 17 / 2 - implicitWidth / 2
                        y: modelData.y + 17 / 2 - implicitHeight / 2
                        text: String(modelData.order)
                        font.pixelSize: 8
                        color: DSTheme.canvasHighlight
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.LeftButton
                    focus: true
                    onClicked: (mouse) => {
                        forceActiveFocus()
                        commitsModel.pickNode(mouse.x, mouse.y,
                            (mouse.modifiers & Qt.AltModifier) !== 0)
                    }
                    Keys.onUpPressed: commitsModel.moveUp()
                    Keys.onDownPressed: commitsModel.moveDown()
                    Keys.onLeftPressed: commitsModel.moveSibling(-1)
                    Keys.onRightPressed: commitsModel.moveSibling(1)
                }
            }
        }
        }

        // --- Status bar ---
        Rectangle {
            Layout.fillWidth: true
            height: 24
            color: DSTheme.midlight
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 8
                Label { text: "commits: %1".arg(commitsModel.rowCount()); font.pixelSize: DSTheme.fontCaption; color: DSTheme.labelText }
                Item { Layout.fillWidth: true }
                Label { text: "Click = select, Alt+Click = mark"; font.pixelSize: DSTheme.fontCaption; color: DSTheme.disabledText }
                Item { width: 8 }
            }
        }

        // --- Bottom buttons
        RowLayout {
            spacing: 8
            Button {
                text: "Merge"; enabled: commitsModel.canMergeMarked; onClicked: commitsModel.mergeMarked()
                opacity: enabled ? 1.0 : 0.4
                palette.button: DSTheme.successButton; palette.buttonText: DSTheme.highlightedText
            }
            Item { Layout.fillWidth: true }
            Button {
                text: "Enable"; enabled: commitsModel.canEnableDisable; onClicked: commitsModel.enableMarked()
                opacity: enabled ? 1.0 : 0.4
                palette.button: DSTheme.warningButton; palette.buttonText: DSTheme.highlightedText
            }
            Button {
                text: "Disable"; enabled: commitsModel.canEnableDisable; onClicked: commitsModel.disableMarked()
                opacity: enabled ? 1.0 : 0.4
                palette.button: DSTheme.warningButton; palette.buttonText: DSTheme.highlightedText
            }
        }

        // --- Selected Commit
        DSGroupBox {
            title: "Selected Commit"
            Layout.fillWidth: true

            GridLayout {
                columns: 3
                columnSpacing: 8; rowSpacing: 2
                anchors.fill: parent

                Label { text: "Commit:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                Label { text: commitsModel.currentId; font.family: DSTheme.fontMono; font.pixelSize: DSTheme.fontCaption; color: DSTheme.tertiaryText; Layout.fillWidth: true }
                ToolButton { icon.source: "../images/doc.on.doc" + DSTheme.iconSuffix + ".png"; icon.width: 22; icon.height: 22; implicitWidth: 26; implicitHeight: 26; background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                ToolTip.visible: hovered; ToolTip.text: "Copy to Clipboard"; ToolTip.delay: 500; onClicked: commitsModel.copyToClipboard(commitsModel.currentId) }

                Label { text: "Parent:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                Label { text: commitsModel.currentParentId; font.family: DSTheme.fontMono; font.pixelSize: DSTheme.fontCaption; color: DSTheme.tertiaryText; Layout.fillWidth: true }
                ToolButton { icon.source: "../images/doc.on.doc" + DSTheme.iconSuffix + ".png"; icon.width: 22; icon.height: 22; implicitWidth: 26; implicitHeight: 26; background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                ToolTip.visible: hovered; ToolTip.text: "Copy to Clipboard"; ToolTip.delay: 500; onClicked: commitsModel.copyToClipboard(commitsModel.currentParentId) }

                Label { text: "Type:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                Label { text: commitsModel.currentType; color: DSTheme.text; Layout.columnSpan: 2 }

                Label { text: "Target:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                Label { text: commitsModel.currentTargetId; font.family: DSTheme.fontMono; font.pixelSize: DSTheme.fontCaption; color: DSTheme.tertiaryText; Layout.fillWidth: true }
                ToolButton { icon.source: "../images/doc.on.doc" + DSTheme.iconSuffix + ".png"; icon.width: 22; icon.height: 22; implicitWidth: 26; implicitHeight: 26; background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                ToolTip.visible: hovered; ToolTip.text: "Copy to Clipboard"; ToolTip.delay: 500; onClicked: commitsModel.copyToClipboard(commitsModel.currentTargetId) }

                Label { text: "Label:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                Label { text: commitsModel.currentLabel; color: DSTheme.text; Layout.columnSpan: 2 }

                Label { text: "Date:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                Label { text: commitsModel.currentDate; color: DSTheme.text; Layout.columnSpan: 2 }
            }
        }

        // --- Marked Commit
        DSGroupBox {
            title: "Marked Commit"
            Layout.fillWidth: true

            GridLayout {
                columns: 3
                columnSpacing: 8; rowSpacing: 2
                anchors.fill: parent

                Label { text: "Commit:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                Label { text: commitsModel.markedId; font.family: DSTheme.fontMono; font.pixelSize: DSTheme.fontCaption; color: DSTheme.tertiaryText; Layout.fillWidth: true }
                ToolButton { icon.source: "../images/doc.on.doc" + DSTheme.iconSuffix + ".png"; icon.width: 22; icon.height: 22; implicitWidth: 26; implicitHeight: 26; background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                ToolTip.visible: hovered; ToolTip.text: "Copy to Clipboard"; ToolTip.delay: 500; onClicked: commitsModel.copyToClipboard(commitsModel.markedId) }

                Label { text: "Parent:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                Label { text: commitsModel.markedParentId; font.family: DSTheme.fontMono; font.pixelSize: DSTheme.fontCaption; color: DSTheme.tertiaryText; Layout.fillWidth: true }
                ToolButton { icon.source: "../images/doc.on.doc" + DSTheme.iconSuffix + ".png"; icon.width: 22; icon.height: 22; implicitWidth: 26; implicitHeight: 26; background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                ToolTip.visible: hovered; ToolTip.text: "Copy to Clipboard"; ToolTip.delay: 500; onClicked: commitsModel.copyToClipboard(commitsModel.markedParentId) }

                Label { text: "Type:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                Label { text: commitsModel.markedType; color: DSTheme.text; Layout.columnSpan: 2 }

                Label { text: "Target:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                Label { text: commitsModel.markedTargetId; font.family: DSTheme.fontMono; font.pixelSize: DSTheme.fontCaption; color: DSTheme.tertiaryText; Layout.fillWidth: true }
                ToolButton { icon.source: "../images/doc.on.doc" + DSTheme.iconSuffix + ".png"; icon.width: 22; icon.height: 22; implicitWidth: 26; implicitHeight: 26; background: Rectangle { color: parent.hovered ? DSTheme.hoverBackground : "transparent"; radius: 4 }
                ToolTip.visible: hovered; ToolTip.text: "Copy to Clipboard"; ToolTip.delay: 500; onClicked: commitsModel.copyToClipboard(commitsModel.markedTargetId) }

                Label { text: "Label:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                Label { text: commitsModel.markedLabel; color: DSTheme.text; Layout.columnSpan: 2 }

                Label { text: "Date:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                Label { text: commitsModel.markedDate; color: DSTheme.text; Layout.columnSpan: 2 }
            }
        }
    }
}
