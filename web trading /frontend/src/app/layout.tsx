import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "IDX Quant Terminal",
  description: "Indonesian Stock Market Quantitative Analysis Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
