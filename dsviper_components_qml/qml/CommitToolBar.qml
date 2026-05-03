import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

/**
 * Commit ToolBar — shared commit operations (Forward, Merge Heads, Fetch/Push/Sync, Manager, Go Live)
 * Shared between cdbe, graph_editor.
 * Requires context properties: storeMgr, settingsMgr, liveModel
 *
 * Uses ToolbarGroup to match NSToolbarItemGroup look from AppKit version.
 */
RowLayout {
    id: root
    spacing: 8

    // Icon base path — caller must set this to resolve dsviper_components_qml/images/
    property string iconBase: "../images/"

    // Head group — Forward, Merge Heads
    ToolbarGroup {
        label: "Head"

        ToolButton {
            enabled: storeMgr.isOpen && !liveModel.liveEnabled
            onClicked: storeMgr.forward()
            display: AbstractButton.IconOnly
            icon.source: root.iconBase + "arrow.up.circle" + DSTheme.iconSuffix + ".png"
            icon.width: 22; icon.height: 22
            ToolTip.visible: hovered
            ToolTip.text: "Move to the most plausible head"
            ToolTip.delay: 500
        }
        ToolButton {
            enabled: storeMgr.isOpen && !liveModel.liveEnabled
            onClicked: storeMgr.reduceHeads()
            display: AbstractButton.IconOnly
            icon.source: root.iconBase + "arrow.triangle.merge" + DSTheme.iconSuffix + ".png"
            icon.width: 22; icon.height: 22
            ToolTip.visible: hovered
            ToolTip.text: "Reduce to a single head by iteratively merging heads"
            ToolTip.delay: 500
        }
    }

    // Sync group — Fetch, Push, Sync
    ToolbarGroup {
        label: "Synchronization"

        ToolButton {
            enabled: storeMgr.isOpen && settingsMgr.hasSourceOfSync && !liveModel.liveEnabled
            onClicked: liveModel.synchronize("fetch")
            display: AbstractButton.IconOnly
            icon.source: root.iconBase + "icloud.and.arrow.down" + DSTheme.iconSuffix + ".png"
            icon.width: 22; icon.height: 22
            ToolTip.visible: hovered
            ToolTip.text: "Fetch from secondary source"
            ToolTip.delay: 500
        }
        ToolButton {
            enabled: storeMgr.isOpen && settingsMgr.hasSourceOfSync && !liveModel.liveEnabled
            onClicked: liveModel.synchronize("push")
            display: AbstractButton.IconOnly
            icon.source: root.iconBase + "icloud.and.arrow.up" + DSTheme.iconSuffix + ".png"
            icon.width: 22; icon.height: 22
            ToolTip.visible: hovered
            ToolTip.text: "Push to secondary source"
            ToolTip.delay: 500
        }
        ToolButton {
            enabled: storeMgr.isOpen && settingsMgr.hasSourceOfSync && !liveModel.liveEnabled
            onClicked: liveModel.synchronize("sync")
            display: AbstractButton.IconOnly
            icon.source: root.iconBase + "link.icloud" + DSTheme.iconSuffix + ".png"
            icon.width: 22; icon.height: 22
            ToolTip.visible: hovered
            ToolTip.text: "Synchronize with secondary source"
            ToolTip.delay: 500
        }
    }

    // Live mode group — Manager, Go Live
    ToolbarGroup {
        label: "Live Mode"

        ToolButton {
            enabled: storeMgr.isOpen
            checkable: true
            checked: liveModel.liveIsManager
            onClicked: liveModel.toggleManager()
            display: AbstractButton.IconOnly
            icon.source: liveModel.liveIsManager
                ? root.iconBase + "person.icloud.fill" + DSTheme.iconSuffix + ".png"
                : root.iconBase + "person.icloud" + DSTheme.iconSuffix + ".png"
            icon.width: 22; icon.height: 22
            ToolTip.visible: hovered
            ToolTip.text: "Toggle automatic merge of heads"
            ToolTip.delay: 500
        }
        ToolButton {
            enabled: storeMgr.isOpen
            checkable: true
            checked: liveModel.liveEnabled
            onClicked: liveModel.toggleLive()
            display: AbstractButton.IconOnly
            icon.source: liveModel.liveEnabled
                ? root.iconBase + "arrow.triangle.2.circlepath.icloud.fill" + DSTheme.iconSuffix + ".png"
                : root.iconBase + "arrow.triangle.2.circlepath.icloud" + DSTheme.iconSuffix + ".png"
            icon.width: 22; icon.height: 22
            ToolTip.visible: hovered
            ToolTip.text: "Toggle Live Mode"
            ToolTip.delay: 500
        }
    }
}
