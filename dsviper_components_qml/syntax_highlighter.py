"""Python syntax highlighter for QML TextEdit.

same application order (later rules override earlier ones).
Colors from DSSyntaxColor.xcassets dark theme.
"""
from __future__ import annotations

import re
from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextDocument
)
from PySide6.QtQuick import QQuickTextDocument

# --- Dark theme colors from DSSyntaxColor.xcassets ---
_COLORS = {
    "TextPlain":              "#ffffff",
    "TextBackground":         "#292a2f",
    "TextKeyword":            "#f469a0",
    "TextBuiltin":            "#6b8ac3",
    "TextString":             "#a3c2a3",
    "TextQuote":              "#f06860",
    "TextComment":            "#6c7985",
    "TextNumber":             "#cfbe69",
    "TextOperator":           "#41a0c0",
    "TextConstant":           "#c7b18f",
    "TextTypeUser":           "#78b8a9",
    "TextViperType":          "#d0a8ff",
    "TextAttribut":           "#60a898",
    "TextDunder":             "#6f89ff",
    "TextDocStr":             "#a7acbd",
    "TextDefinitionConstant": "#b0bb9a",
    "TextViperFunction":      "#af75f6",
    "TextViperConstant":      "#ad9fc6",
    "TextViperAttribut":      "#8d73be",
    "TextError":              "#e54c4c",
    "TextCursor":             "#ff8900",
    "TextSelection":          "#3f4858",
}

# --- Python keywords (from DSPythonLexicon) ---
_KEYWORDS = [
    'and', 'as', 'assert', 'async', 'await', 'break', 'class',
    'continue', 'def', 'del', 'elif', 'else', 'except', 'finally',
    'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
    'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
    'while', 'with', 'yield',
]

_SPECIAL_CONSTANTS = ['False', 'None', 'True']

_BUILTINS = [
    'print', 'len', 'range', 'int', 'str', 'float', 'list', 'dict',
    'set', 'tuple', 'type', 'isinstance', 'hasattr', 'getattr',
    'setattr', 'open', 'input', 'abs', 'all', 'any', 'bin', 'bool',
    'bytes', 'callable', 'chr', 'dir', 'divmod', 'enumerate',
    'eval', 'exec', 'filter', 'format', 'frozenset', 'globals',
    'hash', 'hex', 'id', 'iter', 'locals', 'map', 'max', 'min',
    'next', 'object', 'oct', 'ord', 'pow', 'repr', 'reversed',
    'round', 'slice', 'sorted', 'sum', 'super', 'vars', 'zip',
    'self', 'cls',
]

# --- Viper types (subset — most common, from DSPythonSyntaxHighlighter.m) ---
_VIPER_TYPES = [
    # Type hierarchy
    'Type', 'TypeName', 'TypeAny', 'TypeVoid', 'TypeBool',
    'TypeUInt8', 'TypeUInt16', 'TypeUInt32', 'TypeUInt64',
    'TypeInt8', 'TypeInt16', 'TypeInt32', 'TypeInt64',
    'TypeFloat', 'TypeDouble', 'TypeString', 'TypeBlob',
    'TypeBlobId', 'TypeCommitId', 'TypeUUId',
    'TypeVec', 'TypeMat', 'TypeTuple',
    'TypeOptional', 'TypeVector', 'TypeSet', 'TypeMap', 'TypeXArray',
    'TypeAny', 'TypeVariant',
    'TypeEnumerationDescriptor', 'TypeEnumeration', 'TypeEnumerationCase',
    'TypeStructureDescriptor', 'TypeStructure', 'TypeStructureField',
    'TypeKey', 'TypeConcept', 'TypeClub', 'TypeAnyConcept',
    # Value hierarchy
    'Value', 'ValueAny', 'ValueVoid', 'ValueBool',
    'ValueUInt8', 'ValueUInt16', 'ValueUInt32', 'ValueUInt64',
    'ValueInt8', 'ValueInt16', 'ValueInt32', 'ValueInt64',
    'ValueFloat', 'ValueDouble', 'ValueBlobId', 'ValueCommitId', 'ValueUUId',
    'ValueBlob', 'ValueString',
    'ValueVec', 'ValueMat',
    'ValueTuple', 'ValueTupleIter',
    'ValueOptional', 'ValueVector', 'ValueVectorIter',
    'ValueSet', 'ValueSetIter', 'ValueMap', 'ValueVariant', 'ValueXArray',
    'ValueMapValuesIter', 'ValueMapItemsIter', 'ValueMapKeysIter',
    'ValueStructure', 'ValueEnumeration', 'ValueKey',
    'ValueProgram', 'ValueOpcodeKey', 'ValueOpcode',
    'ValueOpcodeDocumentSet', 'ValueOpcodeDocumentUpdate',
    'ValueOpcodeMapSubtract', 'ValueOpcodeMapUnion', 'ValueOpcodeMapUpdate',
    'ValueOpcodeSetSubtract', 'ValueOpcodeSetUnion',
    'ValueOpcodeXArrayInsert', 'ValueOpcodeXArrayRemove', 'ValueOpcodeXArrayUpdate',
    # Attachment
    'Attachment', 'AttachmentGetting', 'AttachmentMutating',
    'AttachmentFunctionPool', 'AttachmentFunctionPoolFunctions',
    'AttachmentGettingFunction', 'AttachmentMutatingFunction',
    # Definitions
    'Definitions', 'DefinitionsConst', 'DefinitionsInspector',
    'DefinitionsExtendInfo', 'DefinitionsCollector', 'DefinitionsMapper',
    # Document
    'DocumentNode', 'Html', 'Key', 'KeyHelper', 'KeyNamer',
    # Path
    'Path', 'PathConst', 'PathComponent', 'PathElementInfo', 'PathEntryKeyInfo',
    # Function
    'FunctionPrototype', 'Function', 'FunctionPool', 'FunctionPoolFunctions',
    # Blob
    'BlobEncoder', 'BlobEncoderLayout', 'BlobView', 'BlobArray', 'BlobStatistics',
    'BlobPackDescriptor', 'BlobPack', 'BlobPackRegion',
    'BlobData', 'BlobInfo', 'BlobLayout', 'BlobStream',
    'BlobIdMapper', 'BlobGetting',
    # Database
    'Databasing', 'Database', 'DatabaseSQLite', 'DatabaseRemote',
    # Commit
    'Commit', 'CommitAction', 'CommitData', 'CommitEvalAction',
    'CommitDatabase', 'CommitDatabaseSQLite', 'CommitDatabaseRemote',
    'CommitDatabasing', 'CommitDatabaseServer',
    'CommitHeader', 'CommitState', 'CommitMutableState',
    'CommitPersistenceSQLite', 'CommitServerLocal', 'CommitServerRemote',
    'CommitStore', 'CommitStoreBaseNotifying',
    'CommitSynchronizer', 'CommitSyncData',
    'CommitSynchronizerInfo', 'CommitSynchronizerInfoTransmit',
    'CommitNode', 'CommitNodeGrid', 'CommitNodeGridBuilder',
    # Stream
    'StreamRawReading', 'StreamRawWriting', 'StreamRawReader', 'StreamRawWriter',
    'StreamWriting', 'StreamReading',
    'StreamBinaryReader', 'StreamBinaryWriter',
    'StreamTokenBinaryReader', 'StreamTokenBinaryWriter',
    'StreamReaderBlob', 'StreamReaderFile', 'StreamWriterBlob', 'StreamWriterFile',
    'StreamReaderSharedMemory', 'StreamWriterSharedMemory',
    'Codec', 'StreamCodecInstancing', 'StreamEncoding', 'StreamDecoding', 'StreamSizing',
    # Service
    'Service', 'ServiceRemote', 'ServiceRemoteFunction', 'ServiceRemoteFunctions',
    'ServiceRemoteFunctionPool', 'ServiceRemoteFunctionPoolFunction',
    'ServiceRemoteFunctionPoolFunctions', 'ServiceRemoteFunctionPools',
    'ServiceRemoteAttachmentFunction', 'ServiceRemoteAttachmentFunctionPool',
    'ServiceRemoteAttachmentFunctionPoolFunction',
    'ServiceRemoteAttachmentFunctionPoolFunctions', 'ServiceRemoteAttachmentFunctionPools',
    # DSM
    'DSMBuilder', 'DSMBuilderPart', 'DSMParseReport', 'DSMParseError',
    'DSMDefinitions', 'DSMDefinitionsInspector',
    'DSMConcept', 'DSMClub', 'DSMEnumeration', 'DSMEnumerationCase',
    'DSMStructure', 'DSMStructureField', 'DSMTypeKey', 'DSMTypeReference',
    'DSMTypeVec', 'DSMTypeMat', 'DSMTypeTuple',
    'DSMTypeOptional', 'DSMTypeVector', 'DSMTypeSet', 'DSMTypeMap', 'DSMTypeXArray',
    'DSMTypeVariant', 'DSMLiteralList', 'DSMLiteralValue',
    'DSMAttachment', 'DSMFunction', 'DSMFunctionPrototype', 'DSMFunctionPool',
    'DSMAttachmentFunction', 'DSMAttachmentFunctionPool',
    # Misc
    'SharedMemory', 'SQLite', 'Hashing', 'Cancelation',
    'Logging', 'LoggerConsole', 'LoggerNull', 'LoggerPrint', 'LoggerReport',
    'Socket', 'RPCPacket', 'Range', 'RangeIter',
    'HashCRC32', 'HashMD5', 'HashSHA1', 'HashSHA256', 'HashSHA3',
    'Float16', 'Fuzzer', 'Error', 'ViperError', 'Optional',
]


def _word_boundary_pattern(words):
    return r'\b(?:' + '|'.join(re.escape(w) for w in words) + r')\b'


def _make_format(color_name, bold=False, italic=False):
    fmt = QTextCharFormat()
    fmt.setForeground(QColor(_COLORS[color_name]))
    if bold:
        fmt.setFontWeight(QFont.Weight.Bold)
    if italic:
        fmt.setFontItalic(True)
    return fmt


class PythonHighlighter(QSyntaxHighlighter):
    """Application order matches the Obj-C version exactly:
    typeUserRE, viperTypeRE, keywordRE, builtinsRE, viperFunctionRE,
    attributRE, viperAttributRE, dunderRE, then applyCommon
    (operatorRE, decNumberRE, hexNumberRE, stringRE, quoteRE,
     uuidRE, sha1RE, specialConstantRE, constantRE, injectedRE,
     viperConstantRE, docstrRE, commentRE).
    """

    def __init__(self, document):
        super().__init__(document)
        self._mode = "source"  # source, help, dsm, completion
        self._setup_formats()
        self._setup_rules()

    def _setup_formats(self):
        self.f_type_user     = _make_format("TextTypeUser")
        self.f_viper_type    = _make_format("TextViperType")
        self.f_keyword       = _make_format("TextKeyword", bold=True)
        self.f_builtin       = _make_format("TextBuiltin")
        self.f_viper_func    = _make_format("TextViperFunction")
        self.f_attribut      = _make_format("TextAttribut")
        self.f_viper_attr    = _make_format("TextViperAttribut")
        self.f_dunder        = _make_format("TextDunder")
        self.f_operator      = _make_format("TextOperator")
        self.f_number        = _make_format("TextNumber")
        self.f_string        = _make_format("TextString")
        self.f_quote         = _make_format("TextQuote")
        self.f_comment       = _make_format("TextComment", italic=True)
        self.f_constant      = _make_format("TextConstant")
        self.f_def_constant  = _make_format("TextDefinitionConstant")
        self.f_viper_const   = _make_format("TextViperConstant")
        self.f_docstr        = _make_format("TextDocStr")
        self.f_error         = _make_format("TextError")
        self.f_help_section  = _make_format("TextConstant", bold=True)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if self._mode != value:
            self._mode = value
            self.rehighlight()

    def _setup_rules(self):
        """Build rules in exact application order from DSPythonSyntaxHighlighter.m."""
        self.rules = []

        # 1. typeUserRE — \b[A-Z]\w*\b
        self.rules.append((re.compile(r'\b[A-Z]\w*\b'), self.f_type_user))

        # 2. viperTypeRE
        self.rules.append((re.compile(_word_boundary_pattern(_VIPER_TYPES)), self.f_viper_type))

        # 3. keywordRE
        self.rules.append((re.compile(_word_boundary_pattern(_KEYWORDS)), self.f_keyword))

        # 4. builtinsRE
        self.rules.append((re.compile(_word_boundary_pattern(_BUILTINS)), self.f_builtin))

        # 5. viperFunctionRE — just "version" for now
        self.rules.append((re.compile(r'\bversion\b'), self.f_viper_func))

        # 6. attributRE — \.\w+
        self.rules.append((re.compile(r'\.\w+'), self.f_attribut))

        # 7. viperAttributRE — \bvpr_\w+
        self.rules.append((re.compile(r'\bvpr_\w+'), self.f_viper_attr))

        # 8. dunderRE — __\w+__
        self.rules.append((re.compile(r'__\w+__'), self.f_dunder))

        # --- applyCommon ---

        # 9. operatorRE
        self.rules.append((re.compile(r'[+\-*/^%<>()\[\]{}=!|:@.]'), self.f_operator))

        # 10. decNumberRE
        self.rules.append((re.compile(r'\b[-+]?[0-9_]*\.?[0-9_]+([eE][-+]?[0-9_]+)?\b'), self.f_number))

        # 11. hexNumberRE
        self.rules.append((re.compile(r'\b0x[0-9a-fA-F]+\b'), self.f_number))

        # 12. stringRE — f?".*?"
        self.rules.append((re.compile(r'f?".*?"'), self.f_string))

        # 13. quoteRE — f?'.*?'
        self.rules.append((re.compile(r"f?'.*?'"), self.f_quote))

        # 14. uuidRE
        self.rules.append((re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'), self.f_number))

        # 15. sha1RE
        self.rules.append((re.compile(r'\b[0-9a-fA-F]{40}\b'), self.f_number))

        # 16. specialConstantRE — True, False, None
        self.rules.append((re.compile(_word_boundary_pattern(_SPECIAL_CONSTANTS)), self.f_keyword))

        # 17. constantRE — [A-Z]+_[0-9A-Z_]*
        self.rules.append((re.compile(r'\b[A-Z]+_[0-9A-Z_]*\b'), self.f_constant))

        # 18. injectedRE — [0-9A-Z_]+_[T|K|E|S|A|P]_[0-9A-Z_]+
        self.rules.append((re.compile(r'\b[0-9A-Z_]+_[TKESAP]_[0-9A-Z_]+\b'), self.f_def_constant))

        # 19. viperConstantRE — empty in current version

        # 20. docstrRE — single-line """...""" only (multi-line handled in highlightBlock)
        self.rules.append((re.compile(r'""".*?"""'), self.f_docstr))
        self.rules.append((re.compile(r"'''.*?'''"), self.f_docstr))

        # 21. commentRE — #.* or //.*
        self.rules.append((re.compile(r'#.*|//.*'), self.f_comment))

        # Multi-line docstring delimiters
        self._docstr_double = re.compile(r'"""')
        self._docstr_single = re.compile(r"'''")

        # Help mode rules — for help() output
        self.help_rules = [
            (re.compile(_word_boundary_pattern(_VIPER_TYPES)), self.f_viper_type),
            (re.compile(r'\bversion\b'), self.f_viper_func),
            (re.compile(_word_boundary_pattern(_SPECIAL_CONSTANTS)), self.f_keyword),
            (re.compile(r'^\s{4}\w+', re.MULTILINE), self.f_attribut),
            (re.compile(r'^(?:NAME|DESCRIPTION|DATA|FILE|CLASSES|FUNCTIONS|MODULE REFERENCE)\b', re.MULTILINE), self.f_help_section),
        ]

        # DSM mode rules — for to_dsm() output
        _DSM_KEYWORDS = ['struct', 'enum', 'concept', 'club', 'attachment', 'namespace',
                         'function_pool', 'mutable', 'is', 'a']
        self.dsm_rules = [
            (re.compile(r'\b[A-Z]\w*\b'), self.f_type_user),
            (re.compile(_word_boundary_pattern(_VIPER_TYPES)), self.f_viper_type),
            (re.compile(_word_boundary_pattern(_DSM_KEYWORDS)), self.f_keyword),
            (re.compile(r'[+\-*/^%<>()\[\]{}=!|:@.]'), self.f_operator),
            (re.compile(r'\b[-+]?[0-9_]*\.?[0-9_]+([eE][-+]?[0-9_]+)?\b'), self.f_number),
            (re.compile(r'f?".*?"'), self.f_string),
            (re.compile(r"f?'.*?'"), self.f_quote),
            (re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'), self.f_number),
            (re.compile(r'""".*?"""'), self.f_docstr),
            (re.compile(r'#.*|//.*'), self.f_comment),
        ]

    # Block states for multi-line docstrings
    _STATE_NORMAL = -1
    _STATE_IN_DOUBLE_DOCSTR = 1
    _STATE_IN_SINGLE_DOCSTR = 2

    def highlightBlock(self, text: str):
        """Apply syntax highlighting based on current mode."""
        if self._mode == "help":
            rules = self.help_rules
        elif self._mode == "dsm":
            rules = self.dsm_rules
        else:
            rules = self.rules

        # Single-line rules
        for pattern, fmt in rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - match.start()
                self.setFormat(start, length, fmt)

        # Multi-line docstring handling
        self._highlight_multiline(text, self._docstr_double, self._STATE_IN_DOUBLE_DOCSTR)
        self._highlight_multiline(text, self._docstr_single, self._STATE_IN_SINGLE_DOCSTR)

    def _highlight_multiline(self, text: str, delimiter: re.Pattern, state: int):
        """Handle multi-line triple-quoted strings across blocks."""
        if self.previousBlockState() == state:
            # We're inside a docstring from a previous block
            start = 0
            match = delimiter.search(text)
            if match:
                # Found closing delimiter
                length = match.end()
                self.setFormat(start, length, self.f_docstr)
                self.setCurrentBlockState(self._STATE_NORMAL)
            else:
                # Entire line is inside docstring
                self.setFormat(0, len(text), self.f_docstr)
                self.setCurrentBlockState(state)
            return

        # Not inside a docstring — look for opening delimiter
        start = 0
        while start < len(text):
            match = delimiter.search(text, start)
            if not match:
                break
            # Check if it's a single-line docstring (already handled by rules)
            close = delimiter.search(text, match.end())
            if close:
                # Single-line — skip it (already colored by rules)
                start = close.end()
            else:
                # Opening of multi-line docstring
                self.setFormat(match.start(), len(text) - match.start(), self.f_docstr)
                self.setCurrentBlockState(state)
                return


class SyntaxHighlighterHelper(QObject):
    """Helper to attach syntax highlighter to QML TextEdit."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._highlighter: PythonHighlighter | None = None
        self._current_mode = "source"

    @Slot(str)
    def setMode(self, mode: str):
        """Change highlighting mode: source, help, dsm, completion."""
        self._current_mode = mode
        if self._highlighter:
            self._highlighter.mode = mode

    @Slot("QVariant")
    def setDocument(self, quick_doc):
        """Attach highlighter to a QML TextEdit's document."""
        if quick_doc is not None:
            try:
                doc = quick_doc.textDocument()
                if self._highlighter and self._highlighter.document() == doc:
                    return  # already attached
                highlighter = PythonHighlighter(doc)
                highlighter.mode = self._current_mode
                self._highlighter = highlighter
            except Exception as e:
                print(f"Error attaching highlighter: {e}")
