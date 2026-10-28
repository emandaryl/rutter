import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { fetchData, postData } from '../api/client';
import type { Invoice } from '../types';

// Create-and-edit form. Submits through postData only; no fetch in here.
export default function InvoiceForm() {
  const navigate = useNavigate();
  const [client, setClient] = useState('');
  const [total, setTotal] = useState('');

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    await postData<Invoice>('/invoices', { client, total: Number(total) });
    navigate('/');
  }

  return (
    <form onSubmit={submit}>
      <label>Client</label>
      <input value={client} onChange={(e) => setClient(e.target.value)} required />
      <label>Total</label>
      <input
        type="number"
        step="0.01"
        value={total}
        onChange={(e) => setTotal(e.target.value)}
        required
      />
      <button type="submit">Save invoice</button>
    </form>
  );
}
