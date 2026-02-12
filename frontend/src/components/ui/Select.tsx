import { forwardRef } from 'react';
import { ChevronDown } from 'lucide-react';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helper?: string;
  options: SelectOption[];
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ 
    label,
    error,
    helper,
    options,
    className = '',
    ...props 
  }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            {label}
          </label>
        )}
        <div className="relative">
          <select
            ref={ref}
            className={`
              w-full px-3 py-2.5 pr-10
              bg-white border rounded-lg
              text-slate-900
              appearance-none
              transition-all duration-200
              focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500
              disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed
              ${error ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20' : 'border-slate-300 hover:border-slate-400'}
              ${className}
            `}
            {...props}
          >
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500">
            <ChevronDown className="w-5 h-5" />
          </div>
        </div>
        {error && (
          <p className="mt-1.5 text-sm text-red-600">{error}</p>
        )}
        {helper && !error && (
          <p className="mt-1.5 text-sm text-slate-500">{helper}</p>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';
