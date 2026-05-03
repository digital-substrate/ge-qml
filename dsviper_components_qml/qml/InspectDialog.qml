import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * Inspect Dialog
 * Shared between cdbe, graph_editor.
 * Requires context property: inspectModel
 */
Window {
    id: root
    title: "Inspect"
    width: 700; height: 600
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

        // ── Top row: Metadata + Definitions Report ──
        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            // Metadata group
            DSGroupBox {
                title: "Metadata"
                Layout.fillWidth: true
                GridLayout {
                    columns: 2
                    columnSpacing: 8
                    rowSpacing: 4
                    anchors.fill: parent

                    Label { text: "Path:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                    Label { text: inspectModel.path; color: DSTheme.text; Layout.fillWidth: true; elide: Text.ElideMiddle }

                    Label { text: "Documentation:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                    Label { text: inspectModel.documentation; color: DSTheme.text; Layout.fillWidth: true }

                    Label { text: "UUID:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                    Label { text: inspectModel.uuid; color: DSTheme.text; Layout.fillWidth: true }

                    Label { text: "Codec:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                    Label { text: inspectModel.codecName; color: DSTheme.text; Layout.fillWidth: true }

                    Label { text: "Def.HexDigest:"; color: DSTheme.labelText; Layout.alignment: Qt.AlignRight }
                    Label { text: inspectModel.definitionsHexdigest; color: DSTheme.text; Layout.fillWidth: true }
                }
            }

            // Definitions Report group
            DSGroupBox {
                title: "Definitions Report"
                Layout.preferredWidth: 200
                GridLayout {
                    columns: 2
                    columnSpacing: 6
                    rowSpacing: 4
                    anchors.fill: parent

                    Image { source: "../images/concept.png"; width: 16; height: 16; sourceSize: Qt.size(16, 16); fillMode: Image.PreserveAspectFit; Layout.alignment: Qt.AlignVCenter }
                    Label { text: inspectModel.conceptsText; color: DSTheme.text; Layout.alignment: Qt.AlignVCenter }

                    Image { source: "../images/club.png"; width: 16; height: 16; sourceSize: Qt.size(16, 16); fillMode: Image.PreserveAspectFit; Layout.alignment: Qt.AlignVCenter }
                    Label { text: inspectModel.clubsText; color: DSTheme.text; Layout.alignment: Qt.AlignVCenter }

                    Image { source: "../images/enumeration.png"; width: 16; height: 16; sourceSize: Qt.size(16, 16); fillMode: Image.PreserveAspectFit; Layout.alignment: Qt.AlignVCenter }
                    Label { text: inspectModel.enumerationsText; color: DSTheme.text; Layout.alignment: Qt.AlignVCenter }

                    Image { source: "../images/structure.png"; width: 16; height: 16; sourceSize: Qt.size(16, 16); fillMode: Image.PreserveAspectFit; Layout.alignment: Qt.AlignVCenter }
                    Label { text: inspectModel.structuresText; color: DSTheme.text; Layout.alignment: Qt.AlignVCenter }

                    Image { source: "../images/attachment.png"; width: 16; height: 16; sourceSize: Qt.size(16, 16); fillMode: Image.PreserveAspectFit; Layout.alignment: Qt.AlignVCenter }
                    Label { text: inspectModel.attachmentsText; color: DSTheme.text; Layout.alignment: Qt.AlignVCenter }
                }
            }
        }

        // ── DSM Definitions group
        DSGroupBox {
            title: "DSM Definitions"
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 4

                // Controls row
                RowLayout {
                    spacing: 8
                    CheckBox {
                        id: showDocCheck
                        text: "Show Documentation"
                        enabled: inspectModel.enabled
                        onCheckedChanged: inspectModel.setShowDocumentation(checked)
                    }
                    CheckBox {
                        id: showRuntimeIdCheck
                        text: "Show Runtime ID"
                        enabled: inspectModel.enabled
                        onCheckedChanged: inspectModel.setShowRuntimeId(checked)
                    }
                    Label { text: "Attachment:"; color: DSTheme.labelText }
                    ComboBox {
                        id: attachmentCombo
                        Layout.fillWidth: true
                        editable: true
                        enabled: inspectModel.enabled
                        model: inspectModel.attachmentNames()

                        Connections {
                            target: inspectModel
                            function onAttachmentsChanged() {
                                attachmentCombo.model = inspectModel.attachmentNames()
                            }
                        }

                        onAccepted: inspectModel.filterAttachment(editText)
                        onActivated: inspectModel.filterAttachment(currentText)
                    }
                }

                // DSM HTML view
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    TextArea {
                        readOnly: true
                        textFormat: TextEdit.RichText
                        text: inspectModel.dsmHtml
                        font.family: DSTheme.fontMono
                        color: DSTheme.text
                        background: Rectangle { color: DSTheme.window }
                        wrapMode: TextEdit.Wrap
                    }
                }
            }
        }
    }
}
