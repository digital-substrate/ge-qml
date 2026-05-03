import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../dsviper_components_qml/qml" as DS

// Comments component
// Displays comments with add/assign/remove actions.

Rectangle {
    color: DS.DSTheme.window

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 4
        Label {
            text: "Comments"
            font.bold: true
            color: DS.DSTheme.text
        }
        ListView {
            id: commentsView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: graphCommentsModel
            property int selectedRow: -1

            // Animated transitions
            add: Transition { NumberAnimation { properties: "opacity"; from: 0; to: 1; duration: 200 } }
            remove: Transition { NumberAnimation { properties: "opacity"; from: 1; to: 0; duration: 200 } }
            displaced: Transition { NumberAnimation { properties: "y"; duration: 200; easing.type: Easing.OutQuad } }

            delegate: Rectangle {
                width: commentsView.width
                height: 20
                color: index === commentsView.selectedRow ? DS.DSTheme.highlight
                    : (index % 2 === 0 ? DS.DSTheme.window : DS.DSTheme.alternateBase)
                border.color: DS.DSTheme.border
                border.width: 0.5
                Label {
                    anchors.fill: parent
                    anchors.leftMargin: 4
                    text: model.commentText || ""
                    color: DS.DSTheme.secondaryText
                    elide: Text.ElideRight
                    verticalAlignment: Text.AlignVCenter
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        commentsView.selectedRow = index
                        commentField.text = model.commentText
                    }
                }
            }
        }
        TextField {
            id: commentField
            Layout.fillWidth: true
            placeholderText: "comment"
            color: DS.DSTheme.text
            background: Rectangle { color: DS.DSTheme.button; radius: 2 }
        }
        RowLayout {
            Layout.alignment: Qt.AlignRight
            spacing: 8
            RoundButton {
                text: "\u002B"
                font.pixelSize: 14
                implicitWidth: 28; implicitHeight: 28
                enabled: graphCommentsModel.enabled
                onClicked: {
                    graphCommentsModel.addComment(commentsView.selectedRow, commentField.text)
                    commentField.text = ""
                }
                ToolTip.visible: hovered
                ToolTip.text: "Add comment"
                ToolTip.delay: 500
            }
            RoundButton {
                text: "\u003D"
                font.pixelSize: 14
                implicitWidth: 28; implicitHeight: 28
                enabled: graphCommentsModel.enabled && commentsView.selectedRow >= 0
                onClicked: {
                    graphCommentsModel.assignComment(commentsView.selectedRow, commentField.text)
                    commentField.text = ""
                }
                ToolTip.visible: hovered
                ToolTip.text: "Assign comment"
                ToolTip.delay: 500
            }
            RoundButton {
                text: "\u2212"
                font.pixelSize: 14
                implicitWidth: 28; implicitHeight: 28
                enabled: graphCommentsModel.enabled && commentsView.selectedRow >= 0
                onClicked: graphCommentsModel.removeComment(commentsView.selectedRow)
                ToolTip.visible: hovered
                ToolTip.text: "Remove comment"
                ToolTip.delay: 500
            }
        }
    }
}
