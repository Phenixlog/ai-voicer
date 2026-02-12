import { forwardRef } from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ 
    padding = 'md', 
    hover = false,
    children,
    className = '',
    ...props 
  }, ref) => {
    const paddings = {
      none: '',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    };

    return (
      <div
        ref={ref}
        className={`
          bg-white rounded-xl border border-slate-200
          ${paddings[padding]}
          ${hover ? 'hover:border-slate-300 hover:shadow-lg transition-all duration-300 cursor-pointer' : ''}
          ${className}
        `}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

// Card Header
export const CardHeader = ({ 
  children,
  className = ''
}: { children: React.ReactNode; className?: string }) => (
  <div className={`mb-4 ${className}`}>{children}</div>
);

// Card Title
export const CardTitle = ({ 
  children,
  className = ''
}: { children: React.ReactNode; className?: string }) => (
  <h3 className={`text-lg font-semibold text-slate-900 ${className}`}>{children}</h3>
);

// Card Description
export const CardDescription = ({ 
  children,
  className = ''
}: { children: React.ReactNode; className?: string }) => (
  <p className={`text-sm text-slate-500 mt-1 ${className}`}>{children}</p>
);

// Card Content
export const CardContent = ({ 
  children,
  className = ''
}: { children: React.ReactNode; className?: string }) => (
  <div className={className}>{children}</div>
);

// Card Footer
export const CardFooter = ({ 
  children,
  className = ''
}: { children: React.ReactNode; className?: string }) => (
  <div className={`mt-4 pt-4 border-t border-slate-100 ${className}`}>{children}</div>
);
