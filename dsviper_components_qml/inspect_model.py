"""Inspect Model — exposes database info + DSM definitions to QML.

Pure view model — receives data via setters, knows nothing about
Database, CommitStore, or any manager. Callers push data in.
Same pattern as DSInspectViewController (AppKit).
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot

from dsviper import DSMDefinitions, DSMAttachment, Html, ViperError


class InspectModel(QObject):
    """Exposes database info and DSM definition HTML to QML."""

    infoChanged = Signal()
    dsmHtmlChanged = Signal()
    enabledChanged = Signal()
    attachmentsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._enabled = False

        # Database info
        self._path = ""
        self._documentation = ""
        self._uuid = ""
        self._codec_name = ""
        self._definitions_hexdigest = ""

        # Summary
        self._concepts_text = ""
        self._clubs_text = ""
        self._enumerations_text = ""
        self._structures_text = ""
        self._attachments_text = ""

        # DSM
        self._dsm_definitions: DSMDefinitions | None = None
        self._attachments: list[DSMAttachment] = []
        self._selected_attachments: list[DSMAttachment] = []
        self._show_all = False
        self._show_documentation = False
        self._show_runtime_id = False
        self._dsm_html = ""

        # Attachment names for ComboBox
        self._attachment_names: list[str] = []

    # --- Public setters (called by the app) ---

    def set_path(self, value: str):
        self._path = value

    def set_documentation(self, value: str):
        self._documentation = value

    def set_uuid(self, value: str):
        self._uuid = value

    def set_codec_name(self, value: str):
        self._codec_name = value

    def set_definitions_hexdigest(self, value: str):
        self._definitions_hexdigest = value
        self.infoChanged.emit()

    def set_definitions(self, definitions):
        self._configure(definitions)
        self._enabled = True
        self.enabledChanged.emit()

    def clear(self):
        self._clear()
        self._enabled = False
        self.enabledChanged.emit()

    # --- QML Properties: Database Info ---

    def _get_path(self): return self._path
    path = Property(str, _get_path, notify=infoChanged)

    def _get_documentation(self): return self._documentation
    documentation = Property(str, _get_documentation, notify=infoChanged)

    def _get_uuid(self): return self._uuid
    uuid = Property(str, _get_uuid, notify=infoChanged)

    def _get_codec_name(self): return self._codec_name
    codecName = Property(str, _get_codec_name, notify=infoChanged)

    def _get_definitions_hexdigest(self): return self._definitions_hexdigest
    definitionsHexdigest = Property(str, _get_definitions_hexdigest, notify=infoChanged)

    # --- QML Properties: Summary ---

    def _get_concepts_text(self): return self._concepts_text
    conceptsText = Property(str, _get_concepts_text, notify=infoChanged)

    def _get_clubs_text(self): return self._clubs_text
    clubsText = Property(str, _get_clubs_text, notify=infoChanged)

    def _get_enumerations_text(self): return self._enumerations_text
    enumerationsText = Property(str, _get_enumerations_text, notify=infoChanged)

    def _get_structures_text(self): return self._structures_text
    structuresText = Property(str, _get_structures_text, notify=infoChanged)

    def _get_attachments_text(self): return self._attachments_text
    attachmentsText = Property(str, _get_attachments_text, notify=infoChanged)

    # --- QML Properties: DSM ---

    def _get_dsm_html(self): return self._dsm_html
    dsmHtml = Property(str, _get_dsm_html, notify=dsmHtmlChanged)

    def _get_enabled(self): return self._enabled
    enabled = Property(bool, _get_enabled, notify=enabledChanged)

    @Slot(result=list)
    def attachmentNames(self) -> list:
        return self._attachment_names

    # --- DSM Controls ---

    @Slot(bool)
    def setShowDocumentation(self, value: bool):
        self._show_documentation = value
        self._configure_dsm_view()

    @Slot(bool)
    def setShowRuntimeId(self, value: bool):
        self._show_runtime_id = value
        self._configure_dsm_view()

    @Slot(str)
    def filterAttachment(self, text: str):
        self._show_all = False

        if not text:
            self._selected_attachments = self._attachments
            self._show_all = True
        else:
            selected_index = None
            for i, attachment in enumerate(self._attachments):
                if attachment.identifier() == text:
                    selected_index = i
                    break

            if selected_index is not None:
                self._selected_attachments = [self._attachments[selected_index]]
            else:
                candidates = []
                for attachment in self._attachments:
                    if text in attachment.identifier():
                        candidates.append(attachment)
                if candidates:
                    self._selected_attachments = candidates

        self._configure_dsm_view()

    # --- Internal ---

    def _configure(self, definitions):
        try:
            self._configure_summary(definitions)
            self._dsm_definitions = definitions.to_dsm_definitions()
            self._configure_dsm_attachments()

            if self._attachments:
                self._selected_attachments = [self._attachments[0]]

            self._configure_dsm_view()
        except ViperError as e:
            print(f"InspectModel._configure error: {e}")

    @staticmethod
    def _pluralize(word: str, count: int) -> str:
        result = f"{count} {word}"
        if count > 1:
            result += "s"
        return result

    def _configure_summary(self, definitions):
        self._concepts_text = self._pluralize("concept", len(definitions.concepts()))
        self._clubs_text = self._pluralize("club", len(definitions.clubs()))
        self._enumerations_text = self._pluralize("enumeration", len(definitions.enumerations()))
        self._structures_text = self._pluralize("structure", len(definitions.structures()))
        self._attachments_text = self._pluralize("attachment", len(definitions.attachments()))
        self.infoChanged.emit()

    def _configure_dsm_attachments(self):
        self._attachments = self._dsm_definitions.attachments()
        self._attachments.sort(key=lambda a: a.identifier())
        self._attachment_names = [a.identifier() for a in self._attachments]
        self._selected_attachments = self._attachments
        self.attachmentsChanged.emit()

    def _configure_dsm_view(self):
        if not self._dsm_definitions:
            return

        if self._show_all:
            attachments = self._attachments
        else:
            attachments = self._selected_attachments

        content = self._dsm_definitions.to_dsm(
            show_documentation=self._show_documentation,
            show_runtime_id=self._show_runtime_id,
            html=True,
            attachments=attachments)

        style = Html.style()
        body = Html.body(content)
        self._dsm_html = Html.document("DSM Definitions", style, body)
        self.dsmHtmlChanged.emit()

    def _clear(self):
        self._path = ""
        self._documentation = ""
        self._uuid = ""
        self._codec_name = ""
        self._definitions_hexdigest = ""
        self._concepts_text = ""
        self._clubs_text = ""
        self._enumerations_text = ""
        self._structures_text = ""
        self._attachments_text = ""
        self.infoChanged.emit()

        self._dsm_definitions = None
        self._selected_attachments.clear()
        self._attachments.clear()
        self._attachment_names.clear()
        self._show_documentation = False
        self._show_runtime_id = False
        self._dsm_html = ""
        self.dsmHtmlChanged.emit()
        self.attachmentsChanged.emit()
