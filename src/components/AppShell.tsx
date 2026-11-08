import { useEffect } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { Sidebar } from "./Sidebar";

export function AppShell() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return (
    <div className="min-h-screen bg-bg text-ink">
      <Sidebar />
      <main className="lg:pl-72">
        <div className="mx-auto max-w-5xl px-5 py-10 sm:px-8 lg:px-12 lg:py-16">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
