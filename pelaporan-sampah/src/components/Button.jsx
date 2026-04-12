export function Button({ children, variant = 'primary', className = '', disabled = false, ...props }) {
  const baseStyle = "px-4 py-2 rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 flex items-center justify-center cursor-pointer";
  const variants = {
    primary: `bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-600 shadow-sm hover:shadow ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`,
    secondary: `bg-slate-100 text-slate-800 hover:bg-slate-200 focus:ring-slate-500 ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`,
    danger: `bg-red-600 text-white hover:bg-red-700 focus:ring-red-600 shadow-sm hover:shadow ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`
  };

  return (
    <button 
      className={`${baseStyle} ${variants[variant]} ${className}`} 
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
