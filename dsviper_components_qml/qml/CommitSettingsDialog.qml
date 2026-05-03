import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * Settings Panel
 * Shared between cdbe, graph_editor.
 * Requires context property: settingsMgr
 */
Window {
    id: root
    title: "Commit Settings"
    width: 450; height: 320
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
        spacing: 8

        TabBar {
            id: settingsTabBar
            Layout.fillWidth: true
            TabButton { text: "Secondary Source" }
            TabButton { text: "Live Session" }
        }

        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: settingsTabBar.currentIndex

            // Tab 0: Secondary Source
            GridLayout {
                columns: 3
                columnSpacing: 8
                rowSpacing: 8

                // Source type combo
                Label { text: "Source:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                ComboBox {
                    id: syncSourceCombo
                    Layout.fillWidth: true
                    Layout.columnSpan: 2
                    model: ["None", "File", "Socket", "Host"]
                    currentIndex: settingsMgr.syncSource
                    onActivated: settingsMgr.syncSource = currentIndex
                }

                // File path
                property bool fileEnabled: syncSourceCombo.currentIndex === 1
                Label { text: "File:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight; opacity: parent.fileEnabled ? 1.0 : 0.4 }
                TextField {
                    id: syncFileField
                    Layout.fillWidth: true
                    text: settingsMgr.syncFilePath
                    enabled: parent.fileEnabled
                    opacity: parent.fileEnabled ? 1.0 : 0.4
                    onEditingFinished: settingsMgr.syncFilePath = text
                }
                Button {
                    text: "..."
                    implicitWidth: 32
                    enabled: parent.fileEnabled
                    opacity: parent.fileEnabled ? 1.0 : 0.4
                    onClicked: {
                        var path = settingsMgr.browseFile()
                        if (path) { syncFileField.text = path; settingsMgr.syncFilePath = path }
                    }
                }

                // Socket path
                property bool socketEnabled: syncSourceCombo.currentIndex === 2
                Label { text: "Socket:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight; opacity: parent.socketEnabled ? 1.0 : 0.4 }
                TextField {
                    id: syncSocketField
                    Layout.fillWidth: true
                    text: settingsMgr.syncSocketPath
                    enabled: parent.socketEnabled
                    opacity: parent.socketEnabled ? 1.0 : 0.4
                    onEditingFinished: settingsMgr.syncSocketPath = text
                }
                Button {
                    text: "..."
                    implicitWidth: 32
                    enabled: parent.socketEnabled
                    opacity: parent.socketEnabled ? 1.0 : 0.4
                    onClicked: {
                        var path = settingsMgr.browseSocket()
                        if (path) { syncSocketField.text = path; settingsMgr.syncSocketPath = path }
                    }
                }

                // Hostname
                property bool hostEnabled: syncSourceCombo.currentIndex === 3
                Label { text: "Hostname:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight; opacity: parent.hostEnabled ? 1.0 : 0.4 }
                TextField {
                    Layout.fillWidth: true
                    Layout.columnSpan: 2
                    text: settingsMgr.syncHostname
                    enabled: parent.hostEnabled
                    opacity: parent.hostEnabled ? 1.0 : 0.4
                    onEditingFinished: settingsMgr.syncHostname = text
                }

                // Service
                Label { text: "Service:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight; opacity: parent.hostEnabled ? 1.0 : 0.4 }
                TextField {
                    Layout.fillWidth: true
                    Layout.columnSpan: 2
                    text: settingsMgr.syncService
                    enabled: parent.hostEnabled
                    opacity: parent.hostEnabled ? 1.0 : 0.4
                    onEditingFinished: settingsMgr.syncService = text
                }

                Item { Layout.fillHeight: true; Layout.columnSpan: 3 }
            }

            // Tab 1: Live Session
            GridLayout {
                columns: 2
                columnSpacing: 8
                rowSpacing: 8

                Label { text: "Update interval:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                SpinBox {
                    id: liveIntervalSpin
                    from: 0; to: 100
                    value: settingsMgr.liveUpdateInterval * 10
                    stepSize: 1
                    onValueModified: settingsMgr.liveUpdateInterval = value / 10.0

                    property int decimals: 1
                    textFromValue: function(value, locale) {
                        return (value / 10.0).toFixed(decimals)
                    }
                    valueFromText: function(text, locale) {
                        return Math.round(parseFloat(text) * 10)
                    }
                }

                CheckBox {
                    text: "Sync with source"
                    checked: settingsMgr.liveSyncWithSource
                    onToggled: settingsMgr.liveSyncWithSource = checked
                    Layout.columnSpan: 2
                }

                Item { Layout.fillHeight: true; Layout.columnSpan: 2 }
            }
        }

        // OK / Cancel
        RowLayout {
            Layout.fillWidth: true
            Item { Layout.fillWidth: true }
            Button {
                text: "Cancel"
                onClicked: { settingsMgr.reload(); root.visible = false }
            }
            Button {
                text: "OK"
                onClicked: { settingsMgr.save(); root.visible = false }
            }
        }
    }
}
