import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const html = readFileSync(new URL('../src/static/index.html', import.meta.url), 'utf8');
const script = html
    .match(/<script>([\s\S]*?)<\/script>/)[1]
    .replace('const noteTaker = new NoteTaker();', '');
const { NOTE_LIMITS, shouldShowDeleteButton } = new Function(
    `${script}\nreturn { NOTE_LIMITS, shouldShowDeleteButton };`
)();

test('only saved notes show the Delete control', () => {
    assert.equal(shouldShowDeleteButton(null), false);
    assert.equal(shouldShowDeleteButton({ id: null }), false);
    assert.equal(shouldShowDeleteButton({ id: 42 }), true);
});

test('editor fields have display-safe character limits', () => {
    assert.deepEqual(NOTE_LIMITS, { title: 200, content: 5000 });
    assert.match(html, /id="noteTitle"[^>]*maxlength="200"/);
    assert.match(html, /id="noteContent"[^>]*maxlength="5000"/);
});

test('long note labels truncate visually and retain hover text', () => {
    assert.match(html, /\.editor-title\s*\{[\s\S]*?text-overflow:\s*ellipsis/);
    assert.match(html, /\.note-title\s*\{[\s\S]*?text-overflow:\s*ellipsis/);
    assert.match(html, /class="note-title" title="\$\{this\.escapeHtml\(note\.title/);
});

test('a long unbroken note title cannot widen the single-column workspace', () => {
    assert.match(html, /grid-template-columns:\s*minmax\(0,\s*1fr\);/);
    assert.match(html, /\.sidebar\s*\{[\s\S]*?min-width:\s*0/);
});

test('a note opens in its own editor view with a return-to-list control', () => {
    assert.match(html, /id="backToNotesBtn"/);
    assert.match(html, /backToNotesBtn.*addEventListener\('click', \(\) => this\.returnToNotes\(\)\)/);
    assert.match(html, /showEditor\(\)\s*\{[\s\S]*?sidebar\.style\.display = 'none'/);
    assert.match(html, /returnToNotes\(\)\s*\{[\s\S]*?await this\.saveNote\(true\)/);
    assert.match(html, /hideEditor\(\)\s*\{[\s\S]*?sidebar\.style\.display = 'block'/);
});

test('returning to the list preserves the active search filter', () => {
    assert.match(html, /getFilteredNotes\(\)\s*\{[\s\S]*?searchBox\.value\.trim\(\)/);
    assert.match(html, /renderNotesList\(\)\s*\{[\s\S]*?const filteredNotes = this\.getFilteredNotes\(\)/);
    assert.match(html, /searchNotes\(query\)\s*\{[\s\S]*?this\.renderNotesList\(\)/);
});
