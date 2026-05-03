import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * Error Dialog — displays dispatch errors, general errors, and connection errors.
 * Shared between cdbe, graph_editor.
 * Requires context property: storeMgr
 * Optional context property: liveModel (for live/sync connection errors)
 *
 * Signal semantics:
 *   dispatchError — exception caught by C++ dispatch (store mutation lambda)
 *   showError     — general application errors (open, connect, close, etc.)
 *   connectionError — live/sync connection failure
 */
Dialog {
    id: root
    title: "Error"
    width: 400; height: 150
    anchors.centerIn: parent
    modal: true
    standardButtons: Dialog.Ok

    property string errorMessage: ""

    Label {
        anchors.fill: parent
        text: root.errorMessage
        wrapMode: Text.Wrap
        color: DSTheme.text
    }

    Connections {
        target: storeMgr
        function onDispatchError(error) {
            root.title = "Dispatch Error"
            root.errorMessage = error
            root.open()
        }
        function onShowError(error) {
            root.title = "Error"
            root.errorMessage = error
            root.open()
        }
    }

    Connections {
        target: typeof liveModel !== "undefined" ? liveModel : null
        function onConnectionError(error) {
            root.title = "Connection Error"
            root.errorMessage = error
            root.open()
        }
    }
}
