import React from 'react';
import { Routes, Route } from 'react-router-dom';

import InvoiceList from './components/InvoiceList';
import InvoiceForm from './components/InvoiceForm';

// Two routes only: the invoice list and the create/edit form. New routes go
// here, in registration order.
export default function App() {
  return (
    <div style={{ background: 'var(--bg)' }}>
      <Routes>
        <Route path="/" element={<InvoiceList />} />
        <Route path="/invoices/new" element={<InvoiceForm />} />
        <Route path="/invoices/:id" element={<InvoiceForm />} />
      </Routes>
    </div>
  );
}
