import './globals.css';
import React from 'react';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main>
          <div className="card">
            <h1>Unlimy Relay Panel</h1>
            <a href="/">Dashboard</a>
            <a href="/nodes">Nodes</a>
            <a href="/alerts">Alerts</a>
            <a href="/audit">Audit</a>
          </div>
          {children}
        </main>
      </body>
    </html>
  );
}
