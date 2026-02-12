import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

export const Layout = () => {
  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <Sidebar />
      
      {/* Main content */}
      <main className="pt-16 lg:pl-64 min-h-screen">
        <div className="p-4 lg:p-8">
          <div className="max-w-6xl mx-auto">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
};
