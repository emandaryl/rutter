import React, { useEffect, useState } from 'react';

import { fetchData } from '../api/client';
import type { Invoice } from '../types';

// Lists invoices with status filter. Marks paid inline; edit goes to the form
// route, never to a modal here.
export default function InvoiceList() {
  const [invoices, setInvoices] = useState<Invoice[] | null>(null);

  useEffect(() => {
    fetchData<Invoice[]>('/invoices').then(setInvoices).catch(() => setInvoices([]));
  }, []);

  if (invoices === null) return <p>Loading invoices…</p>;
  return (
    <table>
      <thead>
        <tr><th>Client</th><th>Total</th><th>Due</th><th>Status</th></tr>
      </thead>
      <tbody>
        {invoices.map((inv) => (
          <tr key={inv.id}>
            <td>{inv.client}</td>
            <td>{inv.total}</td>
            <td>{inv.due_date}</td>
            <td>{inv.status}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
