import { useRef } from 'react';
import Editor, { type OnMount } from '@monaco-editor/react';
import * as monaco from 'monaco-editor';
import { useCanopyStore } from '../store/useCanopyStore';
import {
  canopyLanguageConfig,
  canopyTokensProvider,
  canopyCompletionItems,
} from '../editor/canopy-language';

export const EditorPanel = () => {
  const { editorContent, setEditorContent, preferences, unsavedChanges, saveStrategy } =
    useCanopyStore();
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;

    // Register Canopy language
    monaco.languages.register({ id: 'canopy' });

    // Set language configuration
    monaco.languages.setLanguageConfiguration('canopy', canopyLanguageConfig);

    // Set tokens provider for syntax highlighting
    monaco.languages.setMonarchTokensProvider('canopy', canopyTokensProvider);

    // Register completion provider for autocomplete
    monaco.languages.registerCompletionItemProvider('canopy', {
      provideCompletionItems: (model, position) => {
        const word = model.getWordUntilPosition(position);
        const range = {
          startLineNumber: position.lineNumber,
          endLineNumber: position.lineNumber,
          startColumn: word.startColumn,
          endColumn: word.endColumn,
        };

        return {
          suggestions: canopyCompletionItems.map((item) => ({
            label: item.label,
            kind: item.kind,
            insertText: item.insertText,
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: item.documentation,
            range: range,
          })),
        };
      },
    });

    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      saveStrategy();
    });

    // Focus the editor
    editor.focus();
  };

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setEditorContent(value);
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Editor Toolbar */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h3 className="text-sm font-semibold text-gray-200">Strategy Editor</h3>
          {unsavedChanges && (
            <span className="text-xs text-amber-400 flex items-center gap-1">
              <span className="w-2 h-2 bg-amber-400 rounded-full"></span>
              Unsaved changes
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={saveStrategy}
            className="px-3 py-1.5 bg-canopy-600 hover:bg-canopy-700 text-white text-sm rounded transition-colors"
          >
            Save (Ctrl+S)
          </button>
        </div>
      </div>

      {/* Monaco Editor */}
      <div className="flex-1">
        <Editor
          height="100%"
          defaultLanguage="canopy"
          language="canopy"
          value={editorContent}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          theme={preferences.editorTheme}
          options={{
            fontSize: preferences.fontSize,
            minimap: { enabled: preferences.showMinimap },
            lineNumbers: preferences.showLineNumbers ? 'on' : 'off',
            wordWrap: preferences.wordWrap ? 'on' : 'off',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            insertSpaces: true,
            formatOnPaste: true,
            formatOnType: true,
            suggestOnTriggerCharacters: true,
            quickSuggestions: true,
            folding: true,
            bracketPairColorization: { enabled: true },
            guides: {
              bracketPairs: true,
              indentation: true,
            },
          }}
        />
      </div>

      {/* Status Bar */}
      <div className="bg-gray-800 border-t border-gray-700 px-4 py-1.5 flex items-center justify-between text-xs text-gray-400">
        <div className="flex items-center gap-4">
          <span>Canopy Language</span>
          <span>UTF-8</span>
        </div>
        <div className="flex items-center gap-4">
          <span>
            Ln {editorRef.current?.getPosition()?.lineNumber || 1}, Col{' '}
            {editorRef.current?.getPosition()?.column || 1}
          </span>
        </div>
      </div>
    </div>
  );
};
