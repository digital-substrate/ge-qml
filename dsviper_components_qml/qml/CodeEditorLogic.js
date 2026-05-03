/**
 * CodeEditorLogic.js — Text manipulation functions for CodeEditor.qml
 *
 * Pure text logic separated from QML UI. All functions take a textEdit
 * object and operate on its text/selection/cursor properties.
 */

// --- Line utilities ---

function lineRange(text, selStart, selEnd) {
    var start = text.lastIndexOf('\n', selStart - 1) + 1
    var end = text.indexOf('\n', selEnd)
    if (end === -1) end = text.length
    return { start: start, end: end }
}

// --- Edit actions ---

function commentSelection(textEdit) {
    var r = lineRange(textEdit.text, textEdit.selectionStart, textEdit.selectionEnd)
    var block = textEdit.text.substring(r.start, r.end)
    var lines = block.split('\n')
    var allCommented = lines.every(function(l) { return l.startsWith('#') })
    var result
    if (allCommented) {
        result = lines.map(function(l) { return l.startsWith('#') ? l.substring(1) : l })
    } else {
        result = lines.map(function(l) { return '#' + l })
    }
    var replacement = result.join('\n')
    textEdit.remove(r.start, r.end)
    textEdit.insert(r.start, replacement)
    textEdit.select(r.start, r.start + replacement.length)
}

function shiftRight(textEdit) {
    var r = lineRange(textEdit.text, textEdit.selectionStart, textEdit.selectionEnd)
    var block = textEdit.text.substring(r.start, r.end)
    var result = block.split('\n').map(function(l) { return '    ' + l }).join('\n')
    textEdit.remove(r.start, r.end)
    textEdit.insert(r.start, result)
    textEdit.select(r.start, r.start + result.length)
}

function shiftLeft(textEdit) {
    var r = lineRange(textEdit.text, textEdit.selectionStart, textEdit.selectionEnd)
    var block = textEdit.text.substring(r.start, r.end)
    var result = block.split('\n').map(function(l) {
        return l.startsWith('    ') ? l.substring(4) : l
    }).join('\n')
    textEdit.remove(r.start, r.end)
    textEdit.insert(r.start, result)
    textEdit.select(r.start, r.start + result.length)
}

function moveLineUp(textEdit) {
    var r = lineRange(textEdit.text, textEdit.selectionStart, textEdit.selectionEnd)
    if (r.start === 0) return
    var prevLineStart = textEdit.text.lastIndexOf('\n', r.start - 2) + 1
    var prevLine = textEdit.text.substring(prevLineStart, r.start - 1)
    var curBlock = textEdit.text.substring(r.start, r.end)
    textEdit.remove(prevLineStart, r.end)
    textEdit.insert(prevLineStart, curBlock + '\n' + prevLine)
    textEdit.select(prevLineStart, prevLineStart + curBlock.length)
}

function moveLineDown(textEdit) {
    var r = lineRange(textEdit.text, textEdit.selectionStart, textEdit.selectionEnd)
    if (r.end >= textEdit.text.length) return
    var nextLineEnd = textEdit.text.indexOf('\n', r.end + 1)
    if (nextLineEnd === -1) nextLineEnd = textEdit.text.length
    var nextLine = textEdit.text.substring(r.end + 1, nextLineEnd)
    var curBlock = textEdit.text.substring(r.start, r.end)
    textEdit.remove(r.start, nextLineEnd)
    textEdit.insert(r.start, nextLine + '\n' + curBlock)
    var newStart = r.start + nextLine.length + 1
    textEdit.select(newStart, newStart + curBlock.length)
}

// --- Text analysis ---

function expressionUnderCursor(textEdit) {
    if (textEdit.selectionStart !== textEdit.selectionEnd)
        return textEdit.selectedText.trim()
    var pos = textEdit.cursorPosition
    var text = textEdit.text
    var start = pos, end = pos
    while (start > 0 && /[\w.]/.test(text[start - 1])) start--
    while (end < text.length && /[\w.]/.test(text[end])) end++
    return text.substring(start, end)
}

function parseDocumentItems(text) {
    var items = []
    var re = /^[ \t]*(def|class)\s+(\w+)/gm
    var match
    while ((match = re.exec(text)) !== null) {
        items.push({
            name: match[2],
            isClass: match[1] === "class",
            position: match.index
        })
    }
    return items
}

// --- Navigation ---

function gotoLine(textEdit, flickable, lineNumber) {
    if (lineNumber < 1) return
    var lines = textEdit.text.split('\n')
    var pos = 0
    for (var i = 0; i < Math.min(lineNumber - 1, lines.length); i++)
        pos += lines[i].length + 1
    textEdit.cursorPosition = pos
    textEdit.forceActiveFocus()
    var lineHeight = textEdit.contentHeight / textEdit.lineCount
    var targetY = (lineNumber - 1) * lineHeight
    var viewportH = flickable.height
    if (targetY < flickable.contentY || targetY > flickable.contentY + viewportH - lineHeight)
        flickable.contentY = Math.max(0, targetY - viewportH / 2)
}

// --- Find ---

function findAll(text, query) {
    if (!query) return []
    var matches = []
    var idx = 0
    while (true) {
        var pos = text.indexOf(query, idx)
        if (pos === -1) break
        matches.push(pos)
        idx = pos + 1
    }
    return matches
}

function selectMatch(textEdit, flickable, matches, index, queryLength) {
    if (index < 0 || index >= matches.length) return
    var pos = matches[index]
    textEdit.select(pos, pos + queryLength)
    var lineNumber = textEdit.text.substring(0, pos).split('\n').length
    var lines = textEdit.text.split('\n')
    var lineY = 0
    for (var i = 0; i < Math.min(lineNumber - 1, lines.length); i++)
        lineY += textEdit.cursorRectangle.height
    var lineHeight = textEdit.cursorRectangle.height
    var viewportH = flickable.height
    if (lineY < flickable.contentY || lineY > flickable.contentY + viewportH - lineHeight)
        flickable.contentY = Math.max(0, lineY - viewportH / 2)
}

// --- Replace ---

function replaceCurrent(textEdit, matches, index, query, replacement) {
    if (index < 0 || index >= matches.length) return
    var pos = matches[index]
    textEdit.remove(pos, pos + query.length)
    textEdit.insert(pos, replacement)
}

function replaceAll(textEdit, matches, query, replacement) {
    if (!query || matches.length === 0) return
    for (var i = matches.length - 1; i >= 0; i--) {
        var pos = matches[i]
        textEdit.remove(pos, pos + query.length)
        textEdit.insert(pos, replacement)
    }
}
