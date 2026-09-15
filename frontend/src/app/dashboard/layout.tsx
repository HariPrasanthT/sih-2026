import Sidebar from "@/components/layout/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-[#f0f7ff] text-slate-900">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col min-h-screen bg-[#f0f7ff]">
        {children}
      </div>
    </div>
  );
}
