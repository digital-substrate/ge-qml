pragma Singleton
import QtQuick

/**
 * DSTheme — Single source of truth for colors and font sizes.
 *
 * Two usage paths:
 *   1. Fusion controls: bind ApplicationWindow.palette → DSTheme roles
 *      → Button, ComboBox, SpinBox, etc. read palette automatically
 *   2. Custom items: reference DSTheme.xxx or palette.xxx directly
 *      → Rectangle, Text, Canvas delegates
 *
 * Font hierarchy: default inherited from ApplicationWindow (12),
 * only exceptions are declared:
 *   fontHeading (13) — section titles (bold)
 *   fontCaption (10) — status bars, toolbar groups, counters
 *
 * Client apps can override isDark to switch theme.
 */
QtObject {
    readonly property bool isDark: true
    readonly property string iconSuffix: isDark ? "-dark" : ""

    // ── QPalette roles (feed into ApplicationWindow.palette) ──────────

    readonly property color window:          isDark ? "#2d2d2d" : "#f0f0f0"
    readonly property color windowText:      isDark ? "#e0e0e0" : "#1a1a1a"
    readonly property color base:            isDark ? "#1a1a1a" : "#ffffff"
    readonly property color alternateBase:   isDark ? "#353535" : "#f5f5f5"
    readonly property color text:            isDark ? "#e0e0e0" : "#1a1a1a"
    readonly property color button:          isDark ? "#2a2a2a" : "#e0e0e0"
    readonly property color buttonText:      isDark ? "#e0e0e0" : "#1a1a1a"
    readonly property color highlight:       "#3a6ea5"
    readonly property color highlightedText: isDark ? "#ffffff" : "#ffffff"
    readonly property color mid:             isDark ? "#505050" : "#b0b0b0"
    readonly property color midlight:        isDark ? "#3a3a3a" : "#e8e8e8"
    readonly property color light:           isDark ? "#555555" : "#ffffff"
    readonly property color dark:            isDark ? "#1a1a1a" : "#a0a0a0"
    readonly property color placeholderText: isDark ? "#808080" : "#808080"
    readonly property color toolTipBase:    isDark ? "#3a3a3a" : "#f5f5c8"
    readonly property color toolTipText:    isDark ? "#c0c0c0" : "#1a1a1a"

    // ── Text hierarchy (beyond QPalette) ─────────────────────────────

    readonly property color secondaryText:   isDark ? "#c0c0c0" : "#505050"
    readonly property color tertiaryText:    isDark ? "#a0a0a0" : "#707070"
    readonly property color labelText:       isDark ? "#808080" : "#808080"
    readonly property color disabledText:    isDark ? "#606060" : "#a0a0a0"

    // ── Interactive states ──────────────────────────────────────────

    readonly property color hoverBackground: isDark ? "#404040" : "#d8d8d8"

    // ── Borders & separators ─────────────────────────────────────────

    readonly property color separator:       isDark ? "#505050" : "#c0c0c0"
    readonly property color border:          isDark ? "#444444" : "#c8c8c8"
    readonly property color inputBorder:     isDark ? "#4a4a4a" : "#b0b0b0"

    // ── Semantic colors ──────────────────────────────────────────────

    readonly property color error:           isDark ? "#c75050" : "#c04040"
    readonly property color flashError:      isDark ? "#602020" : "#ffd0d0"
    readonly property color success:         isDark ? "#4a8c3f" : "#3a7a30"
    readonly property color warning:         isDark ? "#a07840" : "#907030"

    // ── Selection variants ───────────────────────────────────────────

    readonly property color selectedText:    isDark ? "#c0e0ff" : "#003060"

    // ── Type syntax colors (document tree) ───────────────────────────

    readonly property color typeNumber:      isDark ? "#5a9fd4" : "#2060a0"
    readonly property color typeString:      isDark ? "#5a9a5a" : "#2a7a2a"
    readonly property color typeRef:         isDark ? "#7c6fb0" : "#5a4a90"
    readonly property color typeBool:        isDark ? "#c9a227" : "#a08020"
    readonly property color typeColor:       isDark ? "#c03050" : "#a02040"

    // ── Code editor (always dark — IDE convention) ────────────────────

    readonly property color codeBackground:  "#292a2f"
    readonly property color codeLine:        "#25262b"
    readonly property color codeComment:     "#636d83"
    readonly property color codeSelection:   "#3f4858"

    // ── Graph canvas (always dark — matches AppKit) ─────────────────

    readonly property color canvasBackground: "#292a2f"
    readonly property color canvasHighlight:  "#f8d84a"
    readonly property color validElement:     "#e6e6e6"
    readonly property color invalidElement:   "#b3b3b3"

    // ── Action button palette (CommitsDialog) ────────────────────────

    readonly property color dangerButton:    isDark ? "#cc2020" : "#b81818"
    readonly property color warningButton:   isDark ? "#e07020" : "#d06018"
    readonly property color successButton:   isDark ? "#40a040" : "#309030"

    // ── Font sizes ─────────────────────────────────────────────────

    readonly property int fontHeading: 13
    readonly property int fontCaption: 10
    readonly property string fontMono: Qt.platform.os === "osx" ? "Menlo" : Qt.platform.os === "windows" ? "Consolas" : "DejaVu Sans Mono"
}
