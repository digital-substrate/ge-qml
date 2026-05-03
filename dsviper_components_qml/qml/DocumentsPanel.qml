import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * DSDocumentsPanel — Assembly: abstractions + keys + document tree.
 *
 * Reused by dbe (central widget), cdbe (central widget), graph_editor (Window).
 *
 * Required context properties: abstractionModel, keyModel, documentModel
 */
Item {
    id: root

    // Column visibility — forwarded to document tree panel
    property alias showPath: documentTreePanel.showPath
    property alias showType: documentTreePanel.showType

    // Validation feedback — forwarded from document tree panel
    signal validationFailed(int row, string expectedType)

    SplitView {
        anchors.fill: parent
        orientation: Qt.Vertical

        // ============================================================
        // TOP: Abstractions + Keys (horizontal split)
        // ============================================================
        SplitView {
            SplitView.preferredHeight: 200
            SplitView.minimumHeight: 100
            orientation: Qt.Horizontal

            AbstractionPanel {
                id: abstractionPanel
                SplitView.preferredWidth: 200
                SplitView.minimumWidth: 120

                onNewInstanceRequested: (row) => {
                    attachmentDialog.mode = "new_instance"
                    attachmentDialog.targetRow = row
                    attachmentDialog.loadNewInstance(row)
                    attachmentDialog.open()
                }
            }

            KeyPanel {
                id: keyPanel
                SplitView.fillWidth: true
                SplitView.minimumWidth: 200

                onAddAttachmentsRequested: (row) => {
                    attachmentDialog.mode = "add_attachments"
                    attachmentDialog.targetRow = row
                    attachmentDialog.loadAddAttachments(row)
                    attachmentDialog.open()
                }
            }
        }

        // ============================================================
        // BOTTOM: Document tree (full width)
        // ============================================================
        DocumentTreePanel {
            id: documentTreePanel
            SplitView.fillHeight: true
            SplitView.minimumHeight: 200

            onValidationFailed: (row, expectedType) => root.validationFailed(row, expectedType)
        }
    }

    // Reset key selection when abstraction changes
    Connections {
        target: abstractionModel
        function onAbstractionSelected(row) {
            keyPanel.resetSelection()
        }
    }

    AttachmentDialog {
        id: attachmentDialog
    }
}
