/**
 * File Upload Button for Chat
 * 
 * Allows users to upload PDF drawings for validation.
 */

"use client";

import { useState, useRef } from "react";
import { Upload, FileText, X } from "lucide-react";

export interface UploadedFile {
  file: File;
  name: string;
  size: number;
  type: string;
  preview?: string; // For images
}

interface FileUploadProps {
  onFileSelect: (file: UploadedFile) => void;
  onFileRemove?: () => void;
  acceptedTypes?: string;
  maxSizeMB?: number;
  disabled?: boolean;
  currentFile?: UploadedFile | null;
}

export function FileUpload({
  onFileSelect,
  onFileRemove,
  acceptedTypes = ".pdf,.dxf",
  maxSizeMB = 10,
  disabled = false,
  currentFile = null,
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (file: File) => {
    // Validate file size
    const maxBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxBytes) {
      alert(`File too large. Maximum size: ${maxSizeMB}MB`);
      return;
    }

    // Validate file type
    const ext = file.name.toLowerCase().split(".").pop();
    if (acceptedTypes && !acceptedTypes.includes(`.${ext}`)) {
      alert(`Invalid file type. Accepted: ${acceptedTypes}`);
      return;
    }

    // Create uploaded file object
    const uploadedFile: UploadedFile = {
      file,
      name: file.name,
      size: file.size,
      type: file.type,
    };

    onFileSelect(uploadedFile);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleRemove = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    onFileRemove?.();
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (currentFile) {
    // Show selected file
    return (
      <div className="flex items-center gap-2 p-2 rounded-lg glass border border-white/10">
        <FileText className="w-4 h-4 text-blue-400" />
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-white truncate">
            {currentFile.name}
          </div>
          <div className="text-xs text-white/40">
            {formatFileSize(currentFile.size)}
          </div>
        </div>
        <button
          type="button"
          onClick={handleRemove}
          className="p-1 rounded hover:bg-white/10 text-white/50 hover:text-white transition-colors"
          title="Remove file"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedTypes}
        onChange={handleInputChange}
        className="hidden"
        disabled={disabled}
      />

      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        disabled={disabled}
        className={`p-2 rounded-xl transition-all ${
          isDragging
            ? "bg-blue-500/20 border-2 border-blue-400"
            : "hover:bg-white/10 text-white/50 hover:text-white"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
        title="Upload drawing (PDF/DXF)"
      >
        <Upload className="w-5 h-5" />
      </button>
    </div>
  );
}
