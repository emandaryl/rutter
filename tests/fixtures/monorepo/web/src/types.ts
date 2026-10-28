export type Invoice = {
  id: number;
  client: string;
  total: number;
  due_date: string;
  status: 'draft' | 'sent' | 'paid';
};
