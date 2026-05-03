# QML Craftsmanship: Decision Criteria

> *Applied to the ge-qml codebase. Derived from the same Boileau/Saint-Exupéry discipline
> that governs Viper Runtime — adapted to declarative UI.*

## Principle Zero, Applied to QML

Boileau: *"Avant donc que d'écrire, apprenez à penser."*

In imperative C++/Qt, you think about **what the code does** (sequence of operations).
In declarative QML, you think about **what the UI is** (structure of bindings).

The mental model shift: a QML file is not a procedure — it is a **description of a state machine**.
Every property binding is a constraint that the runtime maintains. You declare relationships;
the engine maintains them.

When you catch yourself writing imperative JS to synchronize state between components,
**stop** — you are fighting the paradigm. There is almost certainly a binding that makes it
unnecessary.

---

## The Core Pattern: Models, Views and Delegates

QML is **not** MVVM. There is no ViewModel layer.
Qt Quick uses three concepts: **Model, View, Delegate** (
see [Qt documentation](https://doc.qt.io/qt-6/qtquick-modelviewsdata-modelview.html)):

```
┌─────────────────────────────────────────────────────┐
│  Model (Python)                                     │
│  QAbstractListModel / QAbstractItemModel            │
│  → data(), roleNames(), rowCount()                  │
│  → Slots: trySetValue(), executeAction()            │
│  → Signals: dataChanged, modelReset                 │
│                                                     │
│  WHAT to display. Domain logic. You know this.      │
├─────────────────────────────────────────────────────┤
│  View (QML)                                         │
│  ListView, TreeView, TableView, Repeater            │
│  → Scrolling, recycling, layout                     │
│  → You almost never touch this layer                │
├─────────────────────────────────────────────────────┤
│  Delegate (QML)                                     │
│  The Rectangle/Item that represents ONE row/cell    │
│  → Reads data via model.roleName                    │
│  → Calls actions via model.trySetValue()            │
│  → HOW to display. Visual logic lives here.         │
└─────────────────────────────────────────────────────┘
```

The **roles** are the contract between Python and QML — the equivalent of a C++ interface.
The system of roles eliminates the need for a ViewModel: `data(index, role)` already does
the formatting work.

**The decision rule**: "where does this logic go?"

| Question                           | Answer                  |
|------------------------------------|-------------------------|
| WHAT to display?                   | Model (role)            |
| HOW to display it?                 | Delegate                |
| What happens when the user clicks? | Delegate → Model (slot) |

The MVC Controller disappears. Its work is distributed:

| MVC Controller did       | In MDV, done by                       |
|--------------------------|---------------------------------------|
| Format data for the view | Model (`data()` roles)                |
| Handle user events       | Delegate (MouseArea, onClicked)       |
| Update the model         | Delegate → Model (direct slot call)   |
| Create the view          | QML declarative (nothing to "create") |
| Wire signals             | `Connections {}` or bindings          |

---

## File Organization: 1 Model, 1 Panel, 1 Name

### The naming convention

```
Python:   thing_model.py        →  class ThingModel(QAbstractListModel)
QML:      ThingPanel.qml        →  View + Delegate that displays ThingModel
```

The name suffix tells you the role:

| Suffix         | Role                                 | Example                    |
|----------------|--------------------------------------|----------------------------|
| `*_model.py`   | Model — has roles, serves a QML View | `key_model.py`             |
| `*Panel.qml`   | View+Delegate for one Model          | `DSKeyPanel.qml`           |
| `*Dialog.qml`  | Modal View+Delegate (temporary)      | `DSKeySelectionDialog.qml` |
| `*_manager.py` | Service — no roles, no View          | `commit_store_manager.py`  |
| `Main.qml`     | Assembly — menus + toolbar + layout  | `graph_editor/Main.qml`    |

### The map: every Model has its Panel

```
Model (Python)                    View+Delegate (QML)
──────────────                    ─────────────────────
abstraction_model.py          ↔   DSAbstractionPanel.qml
key_model.py                  ↔   DSKeyPanel.qml
document_model.py             ↔   DSDocumentTreePanel.qml
blob_model.py                 ↔   DSBlobsDialog.qml
commits_model.py              ↔   DSCommitsDialog.qml
actions_model.py              ↔   DSActionsDialog.qml
undo_model.py                 ↔   DSUndoDialog.qml
program_model.py              ↔   DSProgramDialog.qml
list_model.py                 ↔   GraphListPanel.qml
tags_model.py                 ↔   GraphTagsPanel.qml
comments_model.py             ↔   GraphCommentsPanel.qml
vertex_model.py               ↔   GraphVertexPanel.qml
render_model.py               ↔   GraphRenderCanvas.qml
```

A newcomer sees `key_model.py` → searches `*Key*Panel*.qml` → finds `DSKeyPanel.qml`. No mystery.

### Python file types

| Type                | Has roles? | Has a QML View? | Example                       |
|---------------------|------------|-----------------|-------------------------------|
| `*_model.py`        | Yes        | Yes             | `key_model.py`                |
| `*_manager.py`      | No         | No              | `commit_store_manager.py`     |
| `*_controller.py`   | No         | No              | `navigation_controller.py`    |
| `*_notifier.py`     | No         | No              | `ds_commit_store_notifier.py` |
| utility (no suffix) | No         | No              | `collection_difference.py`    |

- **Model** = has a Panel/Dialog in front (MDV pair)
- **Manager** = plumbing that `main.py` wires between models (service)
- **Controller** = orchestrates actions across multiple models
- **Notifier** = relays C++ signals to Python

### The Assembly pattern

An Assembly is a layout-only file that composes Panels. It has no delegate logic of its own.

```qml
// DSDocumentsPanel.qml — Assembly (85 lines)
SplitView {
    DSAbstractionPanel { SplitView.preferredWidth: 200 }
    DSKeyPanel { SplitView.fillWidth: true }
    DSDocumentTreePanel { SplitView.fillHeight: true }
}
```

`Main.qml` is also an Assembly: menus + toolbar + SplitView of Panels.

Assemblies own **shared dialogs** and connect **signals up** from panels to those dialogs.

---

## The Seven Decision Criteria

### 1. One File, One Visual Responsibility

**C++ equivalent**: one QWidget subclass per visual responsibility.

**The test**: can you name the file in 2-3 words that describe what it shows?

- `DSKeyPanel` — yes, it shows a key table
- `GraphRenderCanvas` — yes, it shows the graph canvas
- `DSDocumentsPanel` (before refactoring) — ambiguous: abstractions AND keys AND tree AND editors

**The rule**: if you need AND in the description, split.

**Saint-Exupéry corollary**: a component is complete not when it has everything it needs,
but when it has nothing that belongs elsewhere.

**Size guide** (not a hard rule — consequence of the above):

| Lines   | Assessment                                                            |
|---------|-----------------------------------------------------------------------|
| < 150   | Normal — single responsibility likely respected                       |
| 150-300 | Acceptable if genuinely one complex visual element                    |
| 300+    | Suspect — look for hidden responsibilities to extract                 |
| 500+    | Review — justified only by essential complexity (e.g. 5 editor types) |

### 2. Properties Down, Signals Up

**C++ equivalent**: parent configures child via setters; child notifies parent via signals.

**The ideal** (target architecture):

```qml
// Parent injects dependency explicitly
DSDocumentTreePanel {
    required property var documentModel
}
```

**Current reality**: PySide6 context properties are global. Until the app migrates
to explicit property injection, components access context properties directly with
a comment noting the dependency:

```qml
// documentModel accessed via context property
ListView { model: documentModel }
```

**Critical PySide6 trap**: `required property var documentModel` with the same name
as a context property **shadows** it. The right-hand side in `documentModel: documentModel`
resolves to the child's own unset property → `undefined`. Do not use `required property`
with the same name as a context property.

**Signals up** is already in place — panels emit signals for cross-panel interactions:

```qml
// DSAbstractionPanel.qml
signal newInstanceRequested(int row)

// DSDocumentsPanel.qml (assembly) connects signal to dialog
onNewInstanceRequested: (row) => {
    attachmentDialog.loadNewInstance(row)
    attachmentDialog.open()
}
```

### 3. Binding vs Imperative — The Fundamental Choice

**The test**: does this describe a **state** or an **action**?

| State (binding)                               | Action (JavaScript)                 |
|-----------------------------------------------|-------------------------------------|
| `text: model.display`                         | `onClicked: documentModel.save()`   |
| `color: selected ? "#3a6ea5" : "transparent"` | `onAccepted: { var uuid = ... }`    |
| `visible: model.hasChildren`                  | `Component.onCompleted: loadData()` |
| `width: parent.width * 0.3`                   | `onWidthChanged: recalcLayout()`    |

**Red flag**: `onPropertyChanged: otherThing.property = newValue` — this is an imperative
synchronization that should be a binding: `otherThing.property: Qt.binding(() => ...)`.

**Boileau corollary**: if the intent is clear, the binding writes itself.
If you struggle to express a relationship as a binding, the data flow is unclear.
Think first, then bind.

### 4. Composition, Not Inheritance

**C++ equivalent**: there is none. This is QML's biggest departure from C++/Qt.

In C++: `class MyTreeView : public QTreeView { override paintEvent... }`
In QML: you **cannot** override. You compose.

**The three composition tools**:

| Tool             | When to use                           | C++ analogy             |
|------------------|---------------------------------------|-------------------------|
| Nesting          | Always-visible children               | QVBoxLayout + addWidget |
| Loader           | Conditional/variant children (1 of N) | QStackedWidget          |
| Component (file) | Reusable visual unit                  | QWidget subclass        |

**Specialization in QML**: use properties that change behavior, not inheritance.

```qml
// ONE component with a mode property — not two subclasses
DSAttachmentDialog {
    mode: "new_instance"  // or "add_attachments"
}
```

### 5. Model Provides Data, Delegate Displays It

**C++ equivalent**: identical to Qt MVC. But stricter.

**The test**: does the delegate call a method on the model to get display data?
If yes → missing role.

```qml
// WRONG — delegate reaches into model for display
Text { text: documentModel.getPath(model.row) }

// RIGHT — model exposes path via role
Text { text: model.path }
```

**The boundary**: the delegate knows roles (data), not the model object (source).
The only time a delegate should call the model is for **actions** (mutations),
not for **display** (reads).

**Three levels of MDV complexity** (all in this codebase):

| Level | Example             | Roles | Delegate complexity                       |
|-------|---------------------|-------|-------------------------------------------|
| 1     | GraphCommentsPanel  | 1     | Label                                     |
| 2     | GraphListPanel      | 6+    | Conditional layout (vertex vs edge)       |
| 3     | DSDocumentTreePanel | 8+    | Column dispatch + Loader + 5 editor types |

### 6. Complexity vs Complication in QML

Applying the Viper audit distinction:

| Source of difficulty   | Complexity (essential)               | Complication (accidental)                        |
|------------------------|--------------------------------------|--------------------------------------------------|
| **TreeView delegates** | Cell dispatch by column is inherent  | 5 nested parent.parent chains is avoidable       |
| **Editor variants**    | 5 editor types for 5 value types     | All 5 inlined in one file is avoidable           |
| **Context menus**      | Dynamic items depend on node type    | Building MenuItems imperatively is avoidable     |
| **Model duplication**  | dbe vs cdbe mutation patterns differ | 900 lines of identical display code is avoidable |

**Decision rule**: if you can point to the **domain** as the source of difficulty → accept it.
If you can point to the **code structure** → refactor it.

### 7. Principle of Least Surprise

**The Viper audit test**: can a developer fresh from university maintain this?

Applied to QML:

- A new QML file should be understandable without reading other files
- Property names should match Qt conventions (`model`, `delegate`, `currentIndex`)
- Signal names should follow Qt conventions (`clicked`, `accepted`, `selected`)
- File names should predict content: `DSKeyPanel.qml` = panel that displays keys
- File names should match their Model: `key_model.py` ↔ `DSKeyPanel.qml`

**Anti-patterns that surprise**:

| Surprise                                   | Fix                                        |
|--------------------------------------------|--------------------------------------------|
| `parent.parent.parent.parent.modelData`    | `required property` passed from delegate   |
| Dialog defined 800 lines into a panel file | Separate file                              |
| JavaScript function > 20 lines in QML      | Move logic to Python model                 |
| `*_model.py` with no matching `*Panel.qml` | Name mismatch — rename for discoverability |
| Mega `Main.qml` with inline components     | Extract: 1 Model ↔ 1 Panel ↔ 1 name        |

---

## Python Model Principles (QAbstractItemModel)

The Python models serve the QML delegates. Their craftsmanship follows C++/Qt conventions
directly — no paradigm shift needed.

### Base Class Extraction

**The test**: is the code identical between two subclasses?
If yes → extract to base class. No judgment call needed.

| In base class (display)             | In subclass (mutation)                         |
|-------------------------------------|------------------------------------------------|
| `index()`, `parent()`, `data()`     | `trySetValue()` — different commit pattern     |
| `roleNames()`, `headerData()`       | `trySetEnum()` — different commit pattern      |
| `_rebuild()`, `_wrap()`, `_clear()` | `getContextMenu()` — different actions         |
| `_smart_name()`, `_expand_path()`   | `executeContextAction()` — different mutations |

### Slot Signatures

**Rule**: slots callable from QML take `QModelIndex` for tree-aware models.
The QML side creates the index fresh at point of call (`view.index(row, 0)`),
never stores `QModelIndex` as a property (PySide6 GC risk).

### Role Design

**The test**: does the delegate need this data for display?
If yes → it's a role. If it's for an action → it's a slot parameter.

---

## The Refactoring Log

Each step produced working, testable code. Each step improved one axis.

| Step | Target                            | Axis improved        | Result                      |
|------|-----------------------------------|----------------------|-----------------------------|
| 1    | Extract BaseDocumentModel         | Duplication → 0      | ~900 lines eliminated       |
| 2    | Extract DSKeySelectionDialog      | Responsibility split | Self-contained dialog       |
| 3    | Extract DSAttachmentDialog        | Responsibility split | Self-contained dialog       |
| 4    | Split DSDocumentsPanel → 3 panels | 1 Model ↔ 1 Panel    | 825 → 85 lines (assembly)   |
| 5    | Split graph_editor/Main.qml → 7   | 1 Model ↔ 1 Panel    | 1605 → 808 lines (assembly) |

---

## Lessons Learned (Production Polish)

### Store Injection, Not Singletons

`CommitStore.instance()` is an anti-pattern. Components must never find their own
store — it prevents multi-store apps and hides dependencies.

**Pattern**: The store is created by the app, passed to the facade, which passes it
to sub-models via `set_store(store, notifier)`. Models connect to notifier signals
in `set_store()`, not in `__init__`. Before `set_store()`, the model is inert.

**Notifier**: lives with the store. `CommitAdminModel` creates it, installs it on
the store via `store.set_notifier(CommitStoreNotifying.create(notifier))`, and
passes it to sub-models.

### Pure View Components

A view component must know nothing about its context. Like AppKit's
`DSInspectViewController`: setters only (`set_path`, `set_uuid`, `set_definitions`,
`clear`). The caller pushes data on notifier signals. The component never reaches
for a store, manager, or database.

**Test**: can this component work with a completely different data source?
If no → it knows too much.

### ErrorDialog Decomposition

`ErrorDialog` should not reference `StoreMgr` directly — dbe has no store.
Use `property var errorSource` + `property var liveSource`. The parent wires
the source. The component is a pure error display.

(Not yet applied due to `setContextProperty` constraint — see
`AUDIT_TECHNICAL_DEBT.md` section 9.)

### 1:1 Transposition Discipline

When porting from Qt Widgets:

1. **Read the original method completely** before writing anything
2. **Use the same types** — `ValueEnumeration`, not a string; `ValueSet`, not Python `set`
3. **Preserve the same flow** — if ge-py does `ValueKey.keys(key)` to iterate hierarchy
   forms, do the same; don't invent a different mechanism
4. **Guard the same edges** — if ge-py checks `value == item.value` before commit, you must too
5. **Verify after writing** — audit method-by-method starting from the original

**Traps found in practice**:

| Shortcut taken | Correct approach |
|---------------|-----------------|
| `int(text)` for numeric validation | `ValueUInt8.try_parse(text)` — checks range |
| `f".{case_name}"` for enum | `ValueEnumeration(type_enum, case_name)` |
| Python `set()` for key dedup | `ValueSet(TypeSet(type_key))` — typed comparison |
| `to_key(att.type_key())` for all attachments | `try/except` — sibling concepts crash |
| Skip `_update_document` on abstraction change | Must clear document tree |
| Attachments from abstraction type only | `ValueKey.keys(key)` for full hierarchy |

### setContextProperty — Kept Intentionally

`qmlRegisterSingletonInstance` (Qt6 replacement) crashes Fusion MenuBar in
PySide6 6.10.1. Migration blocked until fix. Qt Bridges may supersede the entire
pattern. See `AUDIT_TECHNICAL_DEBT.md` section 9.

### Fusion Style Workarounds

| Problem | Fix |
|---------|-----|
| MenuSeparator invisible in dark mode | `DSMenuSeparator.qml` with explicit `DSTheme.separator` color |
| Disabled fields not visually dimmed | `opacity: enabled ? 1.0 : 0.4` on custom-colored controls |
| Dynamic MenuItem "not placed in scene" | `createObject(null)` instead of `createObject(parent)` |

---

## How to Apply: The Checklist

Before writing or reviewing any QML/Python change:

1. **Name it** — can I name this file/component in 2-3 words?
2. **Map it** — does the `*_model.py` have a matching `*Panel.qml`?
3. **Bind it** — is every state relationship expressed as a binding?
4. **Signal it** — do cross-panel interactions flow up via signals?
5. **Minimize it** — is there anything I can remove without losing function?
6. **Surprise-check it** — would a new developer expect to find this here?

> *"Ce que l'on conçoit bien s'énonce clairement,*
> *Et les mots pour le dire arrivent aisément."*
>
> If the QML is hard to write, the component boundaries are wrong.
> Rethink the decomposition, then the code writes itself.
