import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "../dsviper_components_qml/qml" as DS

/**
 * Graph Editor QML Port
 *
 * Layout:
 *   ┌─────────────────┬─────────────────────────┬──────────────┐
 *   │  Title           │                         │  Vertex      │
 *   │  List            │     Render Canvas       │  Properties  │
 *   │  Tags            │                         │              │
 *   │  Comments        │                         │  Actions     │
 *   │  Statistics      │                         │              │
 *   └─────────────────┴─────────────────────────┴──────────────┘
 *
 * Menus: File, Edit, Graph, Selection, Navigation, Admin, Help
 * Toolbar: Commit ops (shared) + Random ops (graph-specific)
 */
ApplicationWindow {
    id: root
    visible: true
    width: 1200
    height: 800
    title: contextManager.isOpen
           ? "Graph Editor (QML) — %1 — %2".arg(contextManager.fileName).arg(appPid)
           : "Graph Editor (QML) — %1".arg(appPid)
    color: DS.DSTheme.window
    font.pixelSize: 12

    palette {
        window: DS.DSTheme.window
        windowText: DS.DSTheme.windowText
        base: DS.DSTheme.base
        alternateBase: DS.DSTheme.alternateBase
        text: DS.DSTheme.text
        button: DS.DSTheme.button
        buttonText: DS.DSTheme.buttonText
        highlight: DS.DSTheme.highlight
        highlightedText: DS.DSTheme.highlightedText
        mid: DS.DSTheme.mid
        midlight: DS.DSTheme.midlight
        light: DS.DSTheme.light
        dark: DS.DSTheme.dark
        placeholderText: DS.DSTheme.placeholderText
        toolTipBase: DS.DSTheme.toolTipBase
        toolTipText: DS.DSTheme.toolTipText
    }

    // ── Status bar hint ──
    property int currentModifier: modifierHelper.currentModifier
    property string statusHint: {
        var mod = Qt.platform.os === "osx" ? "\u2318" : "Ctrl"
        if (currentModifier === Qt.Key_Control || currentModifier === Qt.Key_Meta)
            return mod + "+Click: New Vertex  |  " + mod + "+Drag: Connect Edge"
        else if (currentModifier === Qt.Key_Shift)
            return "Shift+Click: Add to Selection"
        else if (currentModifier === Qt.Key_Alt)
            return "Alt+Click: Remove from Selection  |  Alt+Drag: Move Copy"
        else
            return "Click: Select / Deselect  |  " + mod + "+Click: New Vertex  |  " + mod + "+Drag: Connect  |  Shift+Click: Add to Selection  |  Alt+Click: Remove from Selection"
    }

    // ── Menu Bar ──
    menuBar: MenuBar {

        // File menu
        Menu {
            title: "&File"
            Action {
                text: "&Open Database..."
                shortcut: "Ctrl+O"
                enabled: !liveModel.liveEnabled
                onTriggered: openDatabaseDialog.open()
            }
            Action {
                text: "&New Database..."
                shortcut: "Ctrl+N"
                enabled: !liveModel.liveEnabled
                onTriggered: newDatabaseDialog.open()
            }
            Action {
                text: "&Close Database"
                shortcut: "Ctrl+W"
                enabled: contextManager.isOpen && !liveModel.liveEnabled
                onTriggered: contextManager.closeDatabase()
            }
            Action {
                text: "&Get Info"
                shortcut: "Ctrl+I"
                enabled: contextManager.isOpen
                onTriggered: inspectDialog.visible = !inspectDialog.visible
            }
            DS.DSMenuSeparator {}
            Action {
                text: "&Forward"
                enabled: contextManager.isOpen && !liveModel.liveEnabled
                onTriggered: contextManager.forward()
            }
            Action {
                text: "&Merge Heads"
                enabled: contextManager.isOpen && !liveModel.liveEnabled
                onTriggered: contextManager.reduceHeads()
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Fetc&h"
                enabled: contextManager.isOpen && settingsMgr.hasSourceOfSync && !liveModel.liveEnabled
                onTriggered: liveModel.synchronize("fetch")
            }
            Action {
                text: "&Push"
                enabled: contextManager.isOpen && settingsMgr.hasSourceOfSync && !liveModel.liveEnabled
                onTriggered: liveModel.synchronize("push")
            }
            Action {
                text: "&Sync"
                enabled: contextManager.isOpen && settingsMgr.hasSourceOfSync && !liveModel.liveEnabled
                onTriggered: liveModel.synchronize("sync")
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Reopen Last Database"
                checkable: true
                checked: settingsMgr.reopenLastFile
                onTriggered: settingsMgr.reopenLastFile = checked
            }
            DS.DSMenuSeparator {}
            Action { text: "&Quit"; shortcut: "Ctrl+Q"; onTriggered: Qt.quit() }
        }

        // Edit menu
        Menu {
            title: "&Edit"
            Action {
                text: "&Undo"
                shortcut: StandardKey.Undo
                enabled: contextManager.canUndo
                onTriggered: contextManager.undo()
            }
            Action {
                text: "&Redo"
                shortcut: StandardKey.Redo
                enabled: contextManager.canRedo
                onTriggered: contextManager.redo()
            }
            Action {
                text: "&Delete"
                shortcut: "Backspace"
                enabled: contextManager.isOpen && contextManager.hasSelection
                onTriggered: contextManager.deleteSelection()
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Delete Bugged"
                shortcut: "Delete"
                enabled: contextManager.isOpen && contextManager.hasSelection
                onTriggered: contextManager.deleteBugged()
            }
        }

        // Graph menu
        Menu {
            title: "&Graph"
            Action {
                text: "&Select"
                enabled: contextManager.isOpen
                onTriggered: { selectGraphModel.configure(); selectGraphDialog.open() }
            }
            Action {
                text: "&New"
                enabled: contextManager.isOpen
                onTriggered: contextManager.newGraph()
            }
            Action {
                text: "&Clear"
                enabled: contextManager.isOpen
                onTriggered: contextManager.clearGraph()
            }
            DS.DSMenuSeparator {}
            Action {
                text: "&Inspect Element"
                shortcut: "Shift+E"
                enabled: contextManager.isOpen
                onTriggered: {
                    if (renderModel.inspectElement(renderCanvas.lastMouseX, renderCanvas.lastMouseY))
                        documentsDialog.visible = true
                }
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Random &Graph"
                enabled: contextManager.isOpen
                onTriggered: contextManager.randomGraph(renderCanvas.canvasWidth, renderCanvas.canvasHeight)
            }
            Action {
                text: "Random &Vertex"
                enabled: contextManager.isOpen
                onTriggered: contextManager.randomVertex(renderCanvas.canvasWidth, renderCanvas.canvasHeight)
            }
            Action {
                text: "Random &Edge"
                enabled: contextManager.isOpen && contextManager.hasRemainingEdges
                onTriggered: contextManager.randomEdge()
            }
            Action {
                text: "Random &Tag"
                enabled: contextManager.isOpen
                onTriggered: contextManager.randomTag()
            }
            Action {
                text: "Random &Comment"
                enabled: contextManager.isOpen
                onTriggered: contextManager.randomComment()
            }
            DS.DSMenuSeparator {}
            Action {
                text: "&Increment Vertex Value"
                enabled: contextManager.isOpen
                onTriggered: contextManager.incrementVertexValue()
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Graph With Missing Vertex"
                enabled: contextManager.isOpen
                onTriggered: contextManager.graphWithMissingVertex()
            }
            Action {
                text: "Graph With Missing Vertex Properties"
                enabled: contextManager.isOpen
                onTriggered: contextManager.graphWithMissingVertexProperties()
            }
            Action {
                text: "Graph With Error"
                enabled: contextManager.isOpen
                onTriggered: contextManager.graphWithError()
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Restore Integrity By Deleting"
                enabled: contextManager.isOpen
                onTriggered: contextManager.restoreIntegrityByDeleting()
            }
            Action {
                text: "Restore Integrity By Restoring"
                enabled: contextManager.isOpen
                onTriggered: contextManager.restoreIntegrityByRestoring()
            }
            Action {
                text: "Restore Integrity By Creating"
                enabled: contextManager.isOpen
                onTriggered: contextManager.restoreIntegrityByCreating()
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Oh My God, They have killed Commit"
                enabled: contextManager.isOpen
                onTriggered: contextManager.killer()
            }
        }

        // Selection menu
        Menu {
            title: "&Selection"
            Action {
                text: "Select &All"
                shortcut: "Ctrl+A"
                enabled: contextManager.isOpen && (contextManager.hasVertices || contextManager.hasEdges)
                onTriggered: contextManager.selectAll()
            }
            Action {
                text: "&Deselect All"
                enabled: contextManager.isOpen && (contextManager.hasSelectedVertices || contextManager.hasSelectedEdges)
                onTriggered: contextManager.deselectAll()
            }
            Action {
                text: "&Invert Selection"
                enabled: contextManager.isOpen && (contextManager.hasVertices || contextManager.hasEdges)
                onTriggered: contextManager.invertSelection()
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Select All &Vertices"
                shortcut: "Shift+A"
                enabled: contextManager.isOpen && contextManager.hasVertices
                onTriggered: contextManager.selectAllVertices()
            }
            Action {
                text: "Deselect All Vertices"
                enabled: contextManager.isOpen && contextManager.hasSelectedVertices
                onTriggered: contextManager.deselectAllVertices()
            }
            Action {
                text: "Invert Vertices Selection"
                enabled: contextManager.isOpen && contextManager.hasVertices
                onTriggered: contextManager.invertVerticesSelection()
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Select All &Edges"
                shortcut: "Alt+A"
                enabled: contextManager.isOpen && contextManager.hasEdges
                onTriggered: contextManager.selectAllEdges()
            }
            Action {
                text: "Deselect All Edges"
                enabled: contextManager.isOpen && contextManager.hasSelectedEdges
                onTriggered: contextManager.deselectAllEdges()
            }
            Action {
                text: "Invert Edges Selection"
                enabled: contextManager.isOpen && contextManager.hasEdges
                onTriggered: contextManager.invertEdgesSelection()
            }
            DS.DSMenuSeparator {}
            Action {
                text: "&Restore Vertex Selection"
                enabled: contextManager.isOpen && contextManager.hasSelectedVertices
                onTriggered: contextManager.restoreVertexSelection()
            }
        }

        // Navigation menu
        Menu {
            title: "&Navigation"
            Action {
                text: "Go &Forward"
                shortcut: "Ctrl+Shift+Right"
                enabled: navController.canGoForward
                onTriggered: navController.goForward()
            }
            Action {
                text: "Go &Back"
                shortcut: "Ctrl+Shift+Left"
                enabled: navController.canGoBack
                onTriggered: navController.goBack()
            }
        }

        // Editor menu
        Menu {
            title: "&Editor"
            Action {
                text: "Open Script"
                shortcut: "Ctrl+Shift+O"
                onTriggered: scriptOpenDialog.open()
            }
            Action {
                text: "Save Script"
                shortcut: "Ctrl+S"
                onTriggered: pythonEditorModel.saveSource(codeEditor.text)
            }
            DS.DSMenuSeparator {}
            Menu {
                title: "Find"
                Action {
                    text: "Find..."
                    shortcut: "Ctrl+F"
                    onTriggered: codeEditor.showFind()
                }
                Action {
                    text: "Find Next"
                    shortcut: "Ctrl+G"
                    onTriggered: codeEditor.findNext()
                }
                Action {
                    text: "Find Previous"
                    shortcut: "Ctrl+Shift+G"
                    onTriggered: codeEditor.findPrevious()
                }
                Action {
                    text: "Use Selection for Find"
                    shortcut: "Ctrl+E"
                    onTriggered: codeEditor.useSelectionForFind()
                }
                Action {
                    text: "Find and Replace..."
                    shortcut: "Ctrl+Alt+F"
                    onTriggered: codeEditor.showReplace()
                }
            }
            Action {
                text: "Jump to Next Error"
                shortcut: "Ctrl+'"
                onTriggered: pythonEditorModel.nextError()
            }
            Action {
                text: "Jump to Previous Error"
                shortcut: "Ctrl+Shift+'"
                onTriggered: pythonEditorModel.previousError()
            }
            Action {
                text: "Jump to Line"
                shortcut: "Ctrl+L"
                onTriggered: codeEditor.jumpToLine()
            }
            Action {
                text: "Jump to Definition"
                shortcut: "Ctrl+Alt+J"
                onTriggered: codeEditor.jumpToDefinition()
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Run Script"
                shortcut: "Ctrl+R"
                onTriggered: pythonEditorModel.evalBuffer(codeEditor.text)
            }
            Action {
                text: "Eval"
                shortcut: "Ctrl+Return"
                onTriggered: pythonEditorModel.evalSelection(codeEditor.text, codeEditor.selectionStart, codeEditor.selectionEnd)
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Show Help"
                shortcut: "Ctrl+Shift+H"
                onTriggered: pythonEditorModel.showHelp(codeEditor.expressionUnderCursor())
            }
            Action {
                text: "Show Type"
                shortcut: "Ctrl+T"
                onTriggered: pythonEditorModel.showType(codeEditor.expressionUnderCursor())
            }
            Action {
                text: "Show Description"
                onTriggered: pythonEditorModel.showDescription(codeEditor.expressionUnderCursor())
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Bigger Font"
                shortcut: "Ctrl+="
                onTriggered: codeEditor.biggerFont()
            }
            Action {
                text: "Smaller Font"
                shortcut: "Ctrl+-"
                onTriggered: codeEditor.smallerFont()
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Comment Selection"
                shortcut: "Ctrl+/"
                onTriggered: codeEditor.commentSelection()
            }
            Action {
                text: "Shift Right"
                shortcut: "Ctrl+]"
                onTriggered: codeEditor.shiftRight()
            }
            Action {
                text: "Shift Left"
                shortcut: "Ctrl+["
                onTriggered: codeEditor.shiftLeft()
            }
            Action {
                text: "Move Line Up"
                shortcut: "Ctrl+Alt+["
                onTriggered: codeEditor.moveLineUp()
            }
            Action {
                text: "Move Line Down"
                shortcut: "Ctrl+Alt+]"
                onTriggered: codeEditor.moveLineDown()
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Refresh Syntax Coloring"
                shortcut: "Ctrl+Alt+Return"
                onTriggered: codeEditor.refreshSyntax()
            }
        }

        // Admin menu — shared with cdbe
        Menu {
            title: "&Admin"
            Action {
                text: "&Commits"
                shortcut: "Ctrl+1"
                onTriggered: commitsDialog.visible = !commitsDialog.visible
            }
            Action {
                text: "&Documents"
                shortcut: "Ctrl+2"
                onTriggered: documentsDialog.visible = !documentsDialog.visible
            }
            Action {
                text: "&Program"
                shortcut: "Ctrl+3"
                onTriggered: programDialog.visible = !programDialog.visible
            }
            Action {
                text: "Commit &Settings Panel"
                shortcut: "Ctrl+4"
                onTriggered: { liveModel.stopLive(); settingsDialog.visible = !settingsDialog.visible }
            }
            Action {
                text: "&Undo Stack"
                shortcut: "Ctrl+5"
                onTriggered: undoDialog.visible = !undoDialog.visible
            }
            Action {
                text: "Sync &Log"
                shortcut: "Ctrl+6"
                onTriggered: syncLogDialog.visible = !syncLogDialog.visible
            }
            Action {
                text: "&Blobs"
                shortcut: "Ctrl+7"
                onTriggered: blobsDialog.visible = !blobsDialog.visible
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Python &Editor"
                shortcut: "Ctrl+0"
                onTriggered: codeEditorWindow.visible = !codeEditorWindow.visible
            }
            DS.DSMenuSeparator {}
            Action {
                text: "Connect To Server"
                shortcut: "Ctrl+K"
                onTriggered: connectDialog.open()
            }
        }

        // Help menu
        Menu {
            title: "&Help"
            Action {
                text: "Mouse Shortcuts"
                onTriggered: mouseShortcutsDialog.open()
            }
            DS.DSMenuSeparator {}
            MenuItem {
                text: "\u200BAbout Graph Editor..."
                onTriggered: aboutDialog.open()
            }
            MenuItem {
                text: "\u200BAbout Qt"
                onTriggered: aboutQtHelper.showAboutQt()
            }
        }
    }

    // ── Toolbar ──
    header: ToolBar {
        background: Rectangle { color: DS.DSTheme.window }
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 8
            spacing: 8

            // Commit operations — shared toolbar (Forward, Merge Heads, Fetch/Push/Sync, Manager, Go Live)
            DS.CommitToolBar {}

            // Random operations — graph_editor-specific
            DS.ToolbarGroup {
                label: "Random"

                ToolButton {
                    enabled: contextManager.isOpen
                    onClicked: contextManager.randomVertex(renderCanvas.canvasWidth, renderCanvas.canvasHeight)
                    display: AbstractButton.IconOnly
                    icon.source: "images/number.circle" + DS.DSTheme.iconSuffix + ".png"
                    icon.width: 22; icon.height: 22
                    ToolTip.visible: hovered
                    ToolTip.text: "Create a new vertex"
                    ToolTip.delay: 500
                }
                ToolButton {
                    enabled: contextManager.isOpen && contextManager.hasRemainingEdges
                    onClicked: contextManager.randomEdge()
                    display: AbstractButton.IconOnly
                    icon.source: "images/line.diagonal" + DS.DSTheme.iconSuffix + ".png"
                    icon.width: 22; icon.height: 22
                    ToolTip.visible: hovered
                    ToolTip.text: "Create a new edge"
                    ToolTip.delay: 500
                }
                ToolButton {
                    enabled: contextManager.isOpen
                    onClicked: contextManager.randomGraph(renderCanvas.canvasWidth, renderCanvas.canvasHeight)
                    display: AbstractButton.IconOnly
                    icon.source: "images/point.3.connected.trianglepath.dotted" + DS.DSTheme.iconSuffix + ".png"
                    icon.width: 22; icon.height: 22
                    ToolTip.visible: hovered
                    ToolTip.text: "Create a random graph"
                    ToolTip.delay: 500
                }
                ToolButton {
                    enabled: contextManager.isOpen
                    onClicked: contextManager.randomTag()
                    display: AbstractButton.IconOnly
                    icon.source: "images/tag" + DS.DSTheme.iconSuffix + ".png"
                    icon.width: 22; icon.height: 22
                    ToolTip.visible: hovered
                    ToolTip.text: "Create a new tag"
                    ToolTip.delay: 500
                }
                ToolButton {
                    enabled: contextManager.isOpen
                    onClicked: contextManager.randomComment()
                    display: AbstractButton.IconOnly
                    icon.source: "images/message" + DS.DSTheme.iconSuffix + ".png"
                    icon.width: 22; icon.height: 22
                    ToolTip.visible: hovered
                    ToolTip.text: "Create a new comment"
                    ToolTip.delay: 500
                }
            }

            Item { Layout.fillWidth: true }
        }
    }

    // ── Status Bar ──
    footer: ToolBar {
        background: Rectangle { color: DS.DSTheme.window }
        Label {
            text: root.statusHint
            color: DS.DSTheme.tertiaryText
            font.pixelSize: DS.DSTheme.fontCaption
            anchors.left: parent.left
            anchors.leftMargin: 8
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    // ── Central Layout
    SplitView {
        anchors.fill: parent
        orientation: Qt.Horizontal

        // Left panel — Title, List, Tags, Comments, Statistics
        SplitView {
            SplitView.preferredWidth: 250
            SplitView.minimumWidth: 200
            orientation: Qt.Vertical

            // Title component — fixed height
            Rectangle {
                SplitView.preferredHeight: 60
                SplitView.minimumHeight: 50
                SplitView.maximumHeight: 70
                color: DS.DSTheme.window
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 4
                    Label {
                        text: "Title"
                        font.bold: true
                        color: DS.DSTheme.text
                    }
                    TextField {
                        id: titleField
                        Layout.fillWidth: true
                        text: titleModel.title
                        enabled: titleModel.enabled
                        color: DS.DSTheme.text
                        background: Rectangle { color: DS.DSTheme.button; radius: 2 }
                        onAccepted: titleModel.setTitle(text)
                    }
                }
            }

            GraphListPanel {
                SplitView.fillHeight: true
                SplitView.minimumHeight: 80
            }

            GraphTagsPanel {
                SplitView.preferredHeight: 200
                SplitView.minimumHeight: 120
            }

            GraphCommentsPanel {
                SplitView.preferredHeight: 150
                SplitView.minimumHeight: 80
            }

            // Statistics component — fixed height, not resizable
            Rectangle {
                SplitView.preferredHeight: 100
                SplitView.minimumHeight: 100
                SplitView.maximumHeight: 100
                color: DS.DSTheme.window
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 2
                    Label {
                        text: "Statistics"
                        font.bold: true
                        color: DS.DSTheme.text
                    }
                    GridLayout {
                        columns: 2
                        columnSpacing: 4
                        rowSpacing: 2
                        Label { text: "Vertices:"; color: DS.DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                        Label { text: statisticsModel.verticesText; font.family: DS.DSTheme.fontMono; color: DS.DSTheme.text }
                        Label { text: "Edges:"; color: DS.DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                        Label { text: statisticsModel.edgesText; font.family: DS.DSTheme.fontMono; color: DS.DSTheme.text }
                        Label { text: "Min/Max:"; color: DS.DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                        Label { text: statisticsModel.minMaxText; font.family: DS.DSTheme.fontMono; color: DS.DSTheme.text }
                    }
                }
            }
        }

        // Center panel — Render Canvas
        GraphRenderCanvas {
            id: renderCanvas
            SplitView.fillWidth: true
            SplitView.minimumWidth: 400
        }

        // Right panel — Vertex, Actions
        SplitView {
            SplitView.preferredWidth: 250
            SplitView.minimumWidth: 200
            orientation: Qt.Vertical

            GraphVertexPanel {
                SplitView.preferredHeight: 180
                SplitView.minimumHeight: 150
            }

            // Actions component
            Rectangle {
                SplitView.fillHeight: true
                color: DS.DSTheme.window
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 4
                    Label {
                        text: "Actions"
                        font.bold: true
                        color: DS.DSTheme.text
                    }
                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: actionsModel
                        delegate: Rectangle {
                            width: parent ? parent.width : 0
                            height: 22
                            color: index % 2 === 0 ? DS.DSTheme.alternateBase : DS.DSTheme.midlight
                            Row {
                                anchors.fill: parent
                                anchors.leftMargin: 4
                                spacing: 6
                                // Eye icon
                                Image {
                                    source: model.enabled
                                        ? "../dsviper_components_qml/images/eye" + DS.DSTheme.iconSuffix + ".png"
                                        : "../dsviper_components_qml/images/eye.slash" + DS.DSTheme.iconSuffix + ".png"
                                    width: 16; height: 16
                                    fillMode: Image.PreserveAspectFit
                                    opacity: model.enabled ? 1.0 : 0.4
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                                Label {
                                    text: model.label || ""
                                    color: model.enabled ? DS.DSTheme.secondaryText : DS.DSTheme.disabledText
                                    elide: Text.ElideRight
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: parent.width - 24
                                }
                            }
                            MouseArea {
                                anchors.fill: parent
                                onDoubleClicked: actionsModel.toggleEnabled(index)
                            }
                        }
                    }
                }
            }
        }
    }

    // ── File Dialogs
    FileDialog {
        id: openDatabaseDialog
        title: "Open Database"
        nameFilters: ["Graph files (*.graph)"]
        onAccepted: contextManager.openDatabase(selectedFile)
    }
    FileDialog {
        id: newDatabaseDialog
        title: "New Database"
        nameFilters: ["Graph files (*.graph)"]
        fileMode: FileDialog.SaveFile
        onAccepted: contextManager.newDatabase(selectedFile)
    }

    // ── Shared Commit Dialogs (from dsviper_components_qml) ──
    DS.UndoDialog { id: undoDialog }
    DS.SyncLogDialog { id: syncLogDialog }
DS.CommitSettingsDialog { id: settingsDialog }
    DS.ProgramDialog { id: programDialog }
    DS.CommitsDialog { id: commitsDialog }
    DS.BlobsDialog { id: blobsDialog }

    // Python Editor
    Window {
        id: codeEditorWindow
        title: "Python Editor"
        width: 900; height: 600
        color: DS.DSTheme.window
        palette {
            window: DS.DSTheme.window
            windowText: DS.DSTheme.windowText
            base: DS.DSTheme.base
            alternateBase: DS.DSTheme.alternateBase
            text: DS.DSTheme.text
            button: DS.DSTheme.button
            buttonText: DS.DSTheme.buttonText
            highlight: DS.DSTheme.highlight
            highlightedText: DS.DSTheme.highlightedText
            mid: DS.DSTheme.mid
            midlight: DS.DSTheme.midlight
            light: DS.DSTheme.light
            dark: DS.DSTheme.dark
            placeholderText: DS.DSTheme.placeholderText
            toolTipBase: DS.DSTheme.toolTipBase
            toolTipText: DS.DSTheme.toolTipText
        }
        flags: Qt.Window

        DS.CodeEditor {
            id: codeEditor
            anchors.fill: parent
            editorModel: pythonEditorModel
        }
    }
    FileDialog {
        id: scriptOpenDialog
        title: "Open Script"
        currentFolder: "file://" + pythonEditorModel.scriptsFolder()
        nameFilters: ["Python files (*.py)", "All files (*)"]
        onAccepted: pythonEditorModel.openScript(selectedFile)
    }
    DS.ConnectDialog { id: connectDialog }
    DS.ErrorDialog { id: errorDialog }
    DS.AboutDialog { id: aboutDialog; model: licenseModel }
    DS.LicenseDialog { id: licenseDialog; model: licenseModel }

    // Inspect dialog
    DS.DocumentsDialog { id: documentsDialog }
    DS.InspectDialog { id: inspectDialog }

    SelectGraphDialog { id: selectGraphDialog }
    MouseShortcutsDialog { id: mouseShortcutsDialog }
}
