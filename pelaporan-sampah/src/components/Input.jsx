export function Input({ label, type = "text", className = "", ...props }) {
  const baseStyle = "w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-slate-50 focus:bg-white";
  
  return (
    <div className="space-y-1.5 flex flex-col items-start w-full">
      {label && <label className="block text-sm font-semibold text-slate-700">{label}</label>}
      {type === 'textarea' ? (
        <textarea className={`${baseStyle} min-h-[120px] resize-y ${className}`} {...props} />
      ) : (
        <input type={type} className={`${baseStyle} ${className}`} {...props} />
      )}
    </div>
  );
}
