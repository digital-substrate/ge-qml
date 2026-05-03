import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * Connect To Server Dialog
 * Shared between cdbe, graph_editor.
 * Requires context properties: settingsMgr, storeMgr
 */
Dialog {
    id: root
    title: "Connect To Server"
    width: 400; height: 220
    anchors.centerIn: parent
    modal: true
    standardButtons: Dialog.Ok | Dialog.Cancel

    onOpened: {
        connectHostField.text = settingsMgr.connectHostname
        connectServiceField.text = settingsMgr.connectService
        connectSocketField.text = settingsMgr.connectSocketPath
        connectUseSocketCheck.checked = settingsMgr.connectUseSocketPath
    }

    onAccepted: {
        settingsMgr.connectHostname = connectHostField.text
        settingsMgr.connectService = connectServiceField.text
        settingsMgr.connectSocketPath = connectSocketField.text
        settingsMgr.connectUseSocketPath = connectUseSocketCheck.checked
        settingsMgr.save()

        if (connectUseSocketCheck.checked) {
            storeMgr.connectToServerLocal(connectSocketField.text)
        } else {
            storeMgr.connectToServer(connectHostField.text, connectServiceField.text)
        }
    }

    GridLayout {
        anchors.fill: parent
        columns: 2
        columnSpacing: 8; rowSpacing: 8

        property bool hostMode: !connectUseSocketCheck.checked
        property bool socketMode: connectUseSocketCheck.checked

        Label { text: "Hostname:"; color: DSTheme.secondaryText; opacity: parent.hostMode ? 1.0 : 0.4 }
        TextField {
            id: connectHostField
            Layout.fillWidth: true
            enabled: !connectUseSocketCheck.checked
            opacity: parent.hostMode ? 1.0 : 0.4
        }

        Label { text: "Service:"; color: DSTheme.secondaryText; opacity: parent.hostMode ? 1.0 : 0.4 }
        TextField {
            id: connectServiceField
            Layout.fillWidth: true
            enabled: !connectUseSocketCheck.checked
            opacity: parent.hostMode ? 1.0 : 0.4
        }

        Label { text: "Socket:"; color: DSTheme.secondaryText; opacity: parent.socketMode ? 1.0 : 0.4 }
        TextField {
            id: connectSocketField
            Layout.fillWidth: true
            enabled: connectUseSocketCheck.checked
            opacity: parent.socketMode ? 1.0 : 0.4
        }

        CheckBox {
            id: connectUseSocketCheck
            text: "Use Socket Path"
            Layout.columnSpan: 2
        }
    }
}
