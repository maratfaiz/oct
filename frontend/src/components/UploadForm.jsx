import { useRef, useState } from "react";

export function UploadForm({ onFileSelected, disabled }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef(null);

  function handleFiles(files) {
    const file = files?.[0];
    if (file) onFileSelected(file);
  }

  return (
    <div
      className={`upload-zone${isDragOver ? " upload-zone--active" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragOver(true);
      }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragOver(false);
        handleFiles(e.dataTransfer.files);
      }}
      onClick={() => !disabled && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        hidden
        disabled={disabled}
        onChange={(e) => handleFiles(e.target.files)}
      />
      <p>Перетащите OCT-снимок сюда или нажмите, чтобы выбрать файл</p>
    </div>
  );
}
