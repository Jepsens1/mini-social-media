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
        <SideNavbar/>
        {children}
        </div>
      </body>
    </html>
  );
}
