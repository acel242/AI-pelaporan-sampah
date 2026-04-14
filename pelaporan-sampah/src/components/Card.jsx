export function Card({ children, className = "", ...props }) {
  return (
    <div {...props} className={`bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden hover:shadow-md transition-shadow duration-300 ${className}`}>
      {children}
    </div>
  );
}
