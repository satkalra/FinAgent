import { useState, useCallback } from 'react';
import { Upload, FileText, X } from 'lucide-react';

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
}

export default function FileUploader({ onFileSelect, disabled = false }: FileUploaderProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, [disabled]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  }, []);

  const handleFile = (file: File) => {
    // Validate file extension
    if (!file.name.endsWith('.csv')) {
      alert('Please upload a CSV file');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB');
      return;
    }

    setSelectedFile(file);
    onFileSelect(file);
  };

  const clearFile = () => {
    setSelectedFile(null);
  };

  return (
    <div className="w-full">
      {!selectedFile ? (
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => !disabled && document.getElementById('file-input')?.click()}
        >
          <input
            id="file-input"
            type="file"
            accept=".csv"
            onChange={handleChange}
            className="hidden"
            disabled={disabled}
          />

          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />

          <p className="text-lg font-medium text-gray-700 mb-2">
            {dragActive ? 'Drop CSV file here' : 'Upload Evaluation Dataset'}
          </p>

          <p className="text-sm text-gray-500">
            Drag and drop your CSV file here, or click to browse
          </p>

          <p className="text-xs text-gray-400 mt-2">
            CSV format required • Max 5MB • Max 100 test cases
          </p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-4">
              <div className="p-3 bg-blue-50 rounded-lg">
                <FileText className="h-8 w-8 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">{selectedFile.name}</h3>
                <p className="text-sm text-gray-500 mt-1">
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  Ready to evaluate
                </p>
              </div>
            </div>
            {!disabled && (
              <button
                onClick={clearFile}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Remove file"
              >
                <X className="h-5 w-5 text-gray-500" />
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
