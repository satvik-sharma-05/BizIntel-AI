import Sidebar from './Sidebar';

export default function Layout({ children }) {
    return (
        <div className="flex min-h-screen bg-gray-100">
            <Sidebar />
            <main className="ml-64 flex-1 p-8">
                {children}
            </main>
        </div>
    );
}
