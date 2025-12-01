import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Upload, File, X, CheckCircle, ArrowLeft } from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================
interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
}

interface DocumentUploadProps {
  onComplete: () => void;
  onBack: () => void;
}

// ============================================================================
// DOCUMENT UPLOAD COMPONENT
// Drag & Drop Area for Insurance Documents
// ============================================================================
export function DocumentUpload({ onComplete, onBack }: DocumentUploadProps) {
  // ========================================
  // STATE
  // ========================================
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  // ========================================
  // FILE HANDLERS
  // ========================================
  const handleFiles = useCallback((files: FileList | null) => {
    if (!files) return;

    const newFiles: UploadedFile[] = Array.from(files).map(file => ({
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      name: file.name,
      size: file.size,
      type: file.type,
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  }, [handleFiles]);

  const removeFile = useCallback((id: string) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== id));
  }, []);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const handleSubmit = () => {
    setIsProcessing(true);
    // Simulate processing
    setTimeout(() => {
      setIsProcessing(false);
      onComplete();
    }, 2000);
  };

  // ========================================
  // RENDER
  // ========================================
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-6"
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />

      {/* Upload Container */}
      <motion.div
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.1, type: "spring", stiffness: 300, damping: 30 }}
        className="relative w-full max-w-2xl backdrop-blur-xl bg-white/15 border-2 border-white/30 rounded-3xl shadow-[inset_0_4px_8px_rgba(255,255,255,0.15),0_8px_32px_rgba(0,0,0,0.3)] overflow-hidden"
      >
        {/* Header */}
        <div className="p-6 border-b border-white/20">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-white text-2xl mb-1">Upload Your Documents</h2>
              <p className="text-white/60 text-sm">
                Upload your insurance documents to help us find you the best plan
              </p>
            </div>
            <button
              onClick={onBack}
              className="w-10 h-10 backdrop-blur-xl bg-white/10 border border-white/20 rounded-full flex items-center justify-center hover:bg-white/20 transition-all duration-300"
            >
              <ArrowLeft size={20} className="text-white" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          {/* Drag & Drop Zone */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-2xl p-12 transition-all duration-300 ${
              isDragging
                ? 'border-white/60 bg-white/20 scale-[1.02]'
                : 'border-white/30 bg-white/5'
            }`}
          >
            <div className="flex flex-col items-center justify-center text-center">
              <motion.div
                animate={{
                  y: isDragging ? -10 : 0,
                  scale: isDragging ? 1.1 : 1,
                }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
                className="w-20 h-20 backdrop-blur-xl bg-white/15 border border-white/30 rounded-full flex items-center justify-center mb-4 shadow-[inset_0_2px_4px_rgba(255,255,255,0.1)]"
              >
                <Upload size={36} className="text-white" />
              </motion.div>

              <h3 className="text-white text-lg mb-2">
                {isDragging ? 'Drop your files here' : 'Drag & drop your files here'}
              </h3>
              <p className="text-white/50 text-sm mb-6">
                or click to browse from your computer
              </p>

              <label className="cursor-pointer">
                <input
                  type="file"
                  multiple
                  onChange={handleFileInput}
                  className="hidden"
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                />
                <div className="px-6 py-3 backdrop-blur-xl bg-white/20 border border-white/30 rounded-full text-white hover:bg-white/30 transition-all duration-300 shadow-[inset_0_2px_4px_rgba(255,255,255,0.1)]">
                  Browse Files
                </div>
              </label>

              <p className="text-white/40 text-xs mt-4">
                Supported formats: PDF, DOC, DOCX, JPG, PNG
              </p>
            </div>
          </div>

          {/* Uploaded Files List */}
          <AnimatePresence>
            {uploadedFiles.length > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-6"
              >
                <h4 className="text-white text-sm mb-3 flex items-center gap-2">
                  <CheckCircle size={16} className="text-green-400" />
                  Uploaded Files ({uploadedFiles.length})
                </h4>
                <div className="space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <motion.div
                      key={file.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ delay: index * 0.05 }}
                      className="flex items-center justify-between p-3 backdrop-blur-xl bg-white/10 border border-white/20 rounded-xl hover:bg-white/15 transition-all duration-300"
                    >
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <div className="w-10 h-10 backdrop-blur-xl bg-white/15 border border-white/20 rounded-lg flex items-center justify-center flex-shrink-0">
                          <File size={20} className="text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-white text-sm truncate">{file.name}</p>
                          <p className="text-white/50 text-xs">{formatFileSize(file.size)}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => removeFile(file.id)}
                        className="w-8 h-8 backdrop-blur-xl bg-white/10 border border-white/20 rounded-full flex items-center justify-center hover:bg-red-500/30 hover:border-red-400/50 transition-all duration-300 flex-shrink-0 ml-3"
                      >
                        <X size={16} className="text-white" />
                      </button>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-white/20">
          <div className="flex gap-3 justify-end">
            <button
              onClick={onBack}
              className="px-6 py-3 backdrop-blur-xl bg-white/10 border border-white/20 rounded-full text-white hover:bg-white/15 transition-all duration-300"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={uploadedFiles.length === 0 || isProcessing}
              className="px-6 py-3 backdrop-blur-xl bg-white/25 border border-white/30 rounded-full text-white hover:bg-white/35 transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed shadow-[inset_0_2px_4px_rgba(255,255,255,0.1)] flex items-center gap-2"
            >
              {isProcessing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  Continue
                  <CheckCircle size={18} />
                </>
              )}
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
