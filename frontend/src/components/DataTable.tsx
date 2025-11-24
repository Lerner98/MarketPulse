import { useState } from 'react';
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react';
import { GLOBAL_STYLES } from '@/lib/globals';
import { cn } from '@/lib/utils';

interface Column<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  rtl?: boolean;
}

export function DataTable<T extends Record<string, any>>({ data, columns, rtl = true }: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<keyof T | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const handleSort = (key: keyof T) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const sortedData = [...data].sort((a, b) => {
    if (!sortKey) return 0;
    const aValue = a[sortKey];
    const bValue = b[sortKey];
    
    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    }
    
    const aString = String(aValue);
    const bString = String(bValue);
    return sortDirection === 'asc' 
      ? aString.localeCompare(bString, 'he')
      : bString.localeCompare(aString, 'he');
  });

  return (
    <div className={GLOBAL_STYLES.dataTables.container}>
      <div className="overflow-x-auto">
        <table className={GLOBAL_STYLES.dataTables.table} dir={rtl ? 'rtl' : 'ltr'}>
          <thead className={GLOBAL_STYLES.dataTables.header}>
            <tr>
              {columns.map((column) => (
                <th key={String(column.key)} className={GLOBAL_STYLES.dataTables.headerCell}>
                  {column.sortable ? (
                    <button
                      onClick={() => handleSort(column.key)}
                      className={GLOBAL_STYLES.dataTables.sortable}
                    >
                      <span>{column.label}</span>
                      {sortKey === column.key ? (
                        sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronsUpDown className="w-4 h-4 opacity-50" />
                      )}
                    </button>
                  ) : (
                    column.label
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.map((row, rowIndex) => (
              <tr key={rowIndex} className={cn(GLOBAL_STYLES.dataTables.row, GLOBAL_STYLES.dataTables.rowStriped)}>
                {columns.map((column) => (
                  <td key={String(column.key)} className={GLOBAL_STYLES.dataTables.cell}>
                    {column.render ? column.render(row[column.key], row) : row[column.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
