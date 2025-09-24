import SideNavbar from "./components/SideNavbar";
import "./globals.css";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="flex">
          <SideNavbar />
          <div className="flex-1 lg:ml-16 h-screen bg-slate-200 overflow-auto transition-all duration-300">{children}</div>
        </div>
      </body>
    </html>
  );
}
