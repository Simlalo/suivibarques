import { useCallback, useState } from "react";
import { Upload, FileText, CheckCircle, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface FileUploaderProps {
  label: string;
  accept?: string;
  onFileSelect: (file: File) => void;
  id: string;
}

export function FileUploader({ label, accept, onFileSelect, id }: FileUploaderProps) {
  const [fileName, setFileName] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
      onFileSelect(file);
    }
  };

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files?.[0];
      if (file) {
        setFileName(file.name);
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-slate-700 mb-2">
        {label}
      </label>
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={cn(
          "relative group cursor-pointer flex flex-col items-center justify-center w-full h-32 rounded-lg border-2 border-dashed transition-all duration-200 ease-in-out",
          isDragging
            ? "border-primary bg-primary/5"
            : "border-slate-300 hover:border-primary hover:bg-slate-50",
          fileName ? "bg-emerald-50 border-emerald-200" : "bg-white"
        )}
      >
        <input
          type="file"
          id={id}
          accept={accept}
          onChange={handleFileChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
        />
        
        <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center pointer-events-none">
          {fileName ? (
            <>
              <CheckCircle className="w-8 h-8 text-emerald-500 mb-2" />
              <p className="text-sm font-medium text-emerald-700 truncate max-w-[200px]">
                {fileName}
              </p>
              <p className="text-xs text-emerald-500 mt-1">Prêt à traiter</p>
            </>
          ) : (
            <>
              <div className="p-2 rounded-full bg-slate-100 group-hover:bg-white transition-colors mb-2">
                <Upload className="w-5 h-5 text-slate-400 group-hover:text-primary" />
              </div>
              <p className="text-sm text-slate-500 px-4">
                <span className="font-semibold text-primary">Cliquez pour choisir</span> ou glissez le fichier ici
              </p>
              <p className="text-xs text-slate-400 mt-1">CSV uniquement</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
