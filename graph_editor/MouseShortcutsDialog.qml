import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../dsviper_components_qml/qml" as DS

// Mouse Shortcuts dialog

Dialog {
    title: "Mouse Shortcuts"
    width: 450; height: 300
    anchors.centerIn: parent
    modal: true
    standardButtons: Dialog.Ok

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        Label {
            text: "<h3>Click</h3>
<table cellpadding='4'>
<tr><td>Select vertex or edge</td><td><b>Click</b></td></tr>
<tr><td>Deselect all</td><td><b>Click</b> on empty space</td></tr>
<tr><td>New vertex</td><td><b>⌘+Click</b> on empty space</td></tr>
<tr><td>Add to selection</td><td><b>Shift+Click</b></td></tr>
<tr><td>Remove from selection</td><td><b>Alt+Click</b></td></tr>
</table>
<h3>Drag</h3>
<table cellpadding='4'>
<tr><td>Move selection</td><td><b>Drag</b></td></tr>
<tr><td>Connect edge</td><td><b>⌘+Drag</b> from vertex</td></tr>
<tr><td>Duplicate selection</td><td><b>Alt+Drag</b></td></tr>
</table>"
            textFormat: Text.RichText
            color: DS.DSTheme.text
        }
    }
}
