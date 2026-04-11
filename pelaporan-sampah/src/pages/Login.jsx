import { Button } from '../components/Button';
import { Leaf } from 'lucide-react';

export function Login({ onLogin }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <div className="bg-white p-8 rounded-3xl shadow-lg border border-slate-100 w-full max-w-sm text-center transform transition-all">
        <div className="flex justify-center mb-6">
          <div className="p-4 bg-green-100 text-green-600 rounded-2xl shadow-inner">
            <Leaf size={44} strokeWidth={2.5} />
          </div>
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mb-2">EcoLapor</h1>
        <p className="text-slate-500 mb-10 text-sm font-medium">Platform Pelaporan Sampah Warga</p>
        
        <div className="space-y-4">
          <Button 
            className="w-full text-base py-3.5" 
            onClick={() => onLogin('warga')}
          >
            Login sebagai Warga
          </Button>
          <Button 
            variant="secondary" 
            className="w-full text-base py-3.5 bg-slate-100 hover:bg-slate-200" 
            onClick={() => onLogin('admin')}
          >
            Login sebagai Admin
          </Button>
        </div>
      </div>
    </div>
  );
}
